from app.extensions import db
from app.models import Booking, Payment


def test_successful_simulated_payment(client, auth_headers, booking):
    response = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "SUCCESS"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["payment"]["status"] == "SUCCESS"
    assert body["payment"]["amount"] == "499.00"
    assert body["booking_status"] == "CONFIRMED"


def test_failed_payment(client, auth_headers, booking, app):
    response = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "FAILED"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["payment"]["status"] == "FAILED"
    assert body["booking_status"] == "FAILED"

    with app.app_context():
        stored = db.session.get(Booking, booking["id"])
        assert stored.status == "FAILED"


def test_payment_for_another_users_booking(client, auth_headers_b, booking):
    response = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "SUCCESS"},
        headers=auth_headers_b,
    )
    assert response.status_code == 403


def test_duplicate_successful_payment(client, auth_headers, booking):
    first = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "SUCCESS"},
        headers=auth_headers,
    )
    assert first.status_code == 201
    second = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "SUCCESS"},
        headers=auth_headers,
    )
    assert second.status_code == 409
    assert second.get_json()["error"]["code"] == "PAYMENT_ALREADY_SUCCEEDED"


def test_retry_after_failed_payment(client, auth_headers, booking, app):
    failed = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "FAILED"},
        headers=auth_headers,
    )
    assert failed.status_code == 201
    success = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "SUCCESS"},
        headers=auth_headers,
    )
    assert success.status_code == 201
    assert success.get_json()["data"]["booking_status"] == "CONFIRMED"

    with app.app_context():
        payments = Payment.query.filter_by(booking_id=booking["id"]).all()
        assert len(payments) == 2
        assert sum(1 for payment in payments if payment.status == "SUCCESS") == 1


def test_cannot_pay_cancelled_booking(client, auth_headers, booking):
    client.post(f"/api/bookings/{booking['id']}/cancel", headers=auth_headers)
    response = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "SUCCESS"},
        headers=auth_headers,
    )
    assert response.status_code == 409
