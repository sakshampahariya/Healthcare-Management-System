from app.extensions import db
from app.models import DiagnosticCentre
from app.services.cache_service import cache_get, centres_list_key, invalidate_centre_caches
from app.tasks.payment_tasks import send_booking_confirmation


def test_centres_list_is_cached(app, centre):
    """Cache returns stored data; invalidation causes next call to re-read from DB."""
    from app.services.catalogue_service import list_centres

    with app.app_context():
        # First call: cache miss — should hit DB and populate cache
        data1, _, was_cached1 = list_centres(1, 10)
        assert not was_cached1, "First call should be a cache miss"
        assert data1[0]["name"] == centre.name

        # Second call: same data should come from cache
        data2, _, was_cached2 = list_centres(1, 10)
        assert was_cached2, "Second call should be a cache hit"
        assert data2[0]["name"] == centre.name

        # Update the DB record directly
        centre_row = db.session.get(DiagnosticCentre, centre.id)
        centre_row.name = "Changed In Database"
        db.session.commit()
        db.session.expire_all()

        # Cache still serves the OLD name
        data3, _, was_cached3 = list_centres(1, 10)
        assert was_cached3, "Cache should still be warm before invalidation"
        assert data3[0]["name"] == centre.name  # original cached value

        # Invalidate the cache
        invalidate_centre_caches()

        # Next call after invalidation: cache miss, DB re-read — must see new name
        data4, _, was_cached4 = list_centres(1, 10)
        assert not was_cached4, "Call after invalidation should be a cache miss"
        assert data4[0]["name"] == "Changed In Database"


def test_celery_confirmation_task_logs(app, booking, monkeypatch, caplog):
    """Task should send an email and log a confirmation message."""
    sent = {}

    def fake_send(msg):
        sent["subject"] = msg.subject
        sent["recipients"] = msg.recipients

    monkeypatch.setattr("app.tasks.payment_tasks.mail.send", fake_send)

    with caplog.at_level("INFO"):
        message = send_booking_confirmation.run(booking["id"])

    assert f"Booking confirmation sent for booking #{booking['id']}" in message
    assert f"Booking confirmation sent for booking #{booking['id']}" in caplog.text
    # Ensure email was sent (not suppressed)
    assert "subject" in sent
    assert "Booking Confirmed" in sent["subject"]


def test_celery_confirmation_task_missing_booking(app, caplog):
    """Task should gracefully skip and log a warning for a non-existent booking."""
    with caplog.at_level("WARNING"):
        message = send_booking_confirmation.run(999999)

    assert "not found" in message.lower()


def test_payment_enqueues_confirmation(client, auth_headers, booking, monkeypatch):
    called = {}

    def fake_delay(booking_id):
        called["booking_id"] = booking_id

    monkeypatch.setattr(
        "app.tasks.payment_tasks.send_booking_confirmation.delay",
        fake_delay,
    )
    response = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"], "simulate_result": "SUCCESS"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert called["booking_id"] == booking["id"]
