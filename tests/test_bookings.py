from tests.conftest import future_appointment


def test_create_valid_booking(client, auth_headers, booking_payload, diagnostic_test):
    response = client.post("/api/bookings", json=booking_payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["status"] == "PENDING"
    assert data["amount"] == "499.00"
    assert data["test_id"] == diagnostic_test.id


def test_invalid_test_id(client, auth_headers, centre):
    response = client.post(
        "/api/bookings",
        json={
            "test_id": 9999,
            "centre_id": centre.id,
            "appointment_datetime": future_appointment(),
        },
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "TEST_NOT_FOUND"


def test_invalid_centre_id(client, auth_headers, diagnostic_test):
    response = client.post(
        "/api/bookings",
        json={
            "test_id": diagnostic_test.id,
            "centre_id": 9999,
            "appointment_datetime": future_appointment(),
        },
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "CENTRE_NOT_FOUND"


def test_test_does_not_belong_to_centre(
    client, auth_headers, centre, other_test
):
    response = client.post(
        "/api/bookings",
        json={
            "test_id": other_test.id,
            "centre_id": centre.id,
            "appointment_datetime": future_appointment(),
        },
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "TEST_CENTRE_MISMATCH"


def test_list_bookings_only_own(client, auth_headers, booking):
    response = client.get("/api/bookings", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["meta"]["total"] == 1


def test_booking_cancellation(client, auth_headers, booking):
    response = client.post(
        f"/api/bookings/{booking['id']}/cancel",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["status"] == "CANCELLED"


def test_invalid_booking_id(client, auth_headers):
    response = client.get("/api/bookings/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "BOOKING_NOT_FOUND"


def test_cannot_set_status_in_create(client, auth_headers, booking_payload):
    booking_payload["status"] = "CONFIRMED"
    booking_payload["amount"] = "1.00"
    response = client.post("/api/bookings", json=booking_payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["status"] == "PENDING"
    assert data["amount"] == "499.00"
