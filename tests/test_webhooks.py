from app.extensions import db
from app.models import Booking, Payment, WebhookEvent


def _pay(client, auth_headers, booking_id, result="SUCCESS"):
    response = client.post(
        "/api/payments/",
        json={"booking_id": booking_id, "simulate_result": result},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.get_json()["data"]["payment"]


def test_successful_webhook(client, auth_headers, booking, app):
    payment = _pay(client, auth_headers, booking["id"], "FAILED")
    response = client.post(
        "/api/payments/webhook/",
        json={
            "event_id": "evt_success_1",
            "payment_id": payment["external_payment_id"],
            "status": "SUCCESS",
        },
    )
    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["already_processed"] is False
    assert body["booking_status"] == "CONFIRMED"

    with app.app_context():
        stored = db.session.get(Booking, booking["id"])
        assert stored.status == "CONFIRMED"


def test_failed_webhook(client, auth_headers, booking, app):
    payment = _pay(client, auth_headers, booking["id"], "FAILED")
    response = client.post(
        "/api/payments/webhook/",
        json={
            "event_id": "evt_failed_1",
            "payment_id": payment["external_payment_id"],
            "status": "FAILED",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        stored_payment = Payment.query.filter_by(
            external_payment_id=payment["external_payment_id"]
        ).first()
        assert stored_payment.status == "FAILED"
        stored_booking = db.session.get(Booking, booking["id"])
        assert stored_booking.status == "FAILED"


def test_repeated_identical_webhook_is_idempotent(client, auth_headers, booking, app):
    payment = _pay(client, auth_headers, booking["id"], "FAILED")
    payload = {
        "event_id": "evt_repeat",
        "payment_id": payment["external_payment_id"],
        "status": "SUCCESS",
    }
    first = client.post("/api/payments/webhook/", json=payload)
    second = client.post("/api/payments/webhook/", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.get_json()["data"]["already_processed"] is True

    with app.app_context():
        events = WebhookEvent.query.filter_by(event_id="evt_repeat").all()
        assert len(events) == 1
        payments = Payment.query.filter_by(booking_id=booking["id"]).all()
        assert len(payments) == 1
        assert db.session.get(Booking, booking["id"]).status == "CONFIRMED"


def test_duplicate_webhook_does_not_create_payment(client, auth_headers, booking, app):
    payment = _pay(client, auth_headers, booking["id"], "SUCCESS")
    payload = {
        "event_id": "evt_dup_pay",
        "payment_id": payment["external_payment_id"],
        "status": "SUCCESS",
    }
    client.post("/api/payments/webhook/", json=payload)
    client.post("/api/payments/webhook/", json=payload)
    with app.app_context():
        assert Payment.query.filter_by(booking_id=booking["id"]).count() == 1


def test_failed_webhook_does_not_downgrade_success(client, auth_headers, booking, app):
    payment = _pay(client, auth_headers, booking["id"], "SUCCESS")
    response = client.post(
        "/api/payments/webhook/",
        json={
            "event_id": "evt_no_downgrade",
            "payment_id": payment["external_payment_id"],
            "status": "FAILED",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        stored = Payment.query.filter_by(
            external_payment_id=payment["external_payment_id"]
        ).first()
        assert stored.status == "SUCCESS"
        assert db.session.get(Booking, booking["id"]).status == "CONFIRMED"


def test_invalid_webhook_payload(client):
    response = client.post("/api/payments/webhook/", json={"event_id": "evt_x"})
    assert response.status_code == 422


def test_unknown_payment_webhook(client):
    response = client.post(
        "/api/payments/webhook/",
        json={
            "event_id": "evt_unknown",
            "payment_id": "pay_does_not_exist",
            "status": "SUCCESS",
        },
    )
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "PAYMENT_NOT_FOUND"
