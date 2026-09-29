def test_bookings_require_jwt(client, booking_payload):
    response = client.post("/api/bookings", json=booking_payload)
    assert response.status_code == 401


def test_user_cannot_access_another_users_booking(client, auth_headers_b, booking):
    response = client.get(f"/api/bookings/{booking['id']}", headers=auth_headers_b)
    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "BOOKING_FORBIDDEN"


def test_user_cannot_cancel_another_users_booking(client, auth_headers_b, booking):
    response = client.post(
        f"/api/bookings/{booking['id']}/cancel",
        headers=auth_headers_b,
    )
    assert response.status_code == 403


def test_user_cannot_pay_another_users_booking(client, auth_headers_b, booking):
    response = client.post(
        "/api/payments/",
        json={"booking_id": booking["id"]},
        headers=auth_headers_b,
    )
    assert response.status_code == 403


def test_owner_can_access_own_booking(client, auth_headers, booking):
    response = client.get(f"/api/bookings/{booking['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["id"] == booking["id"]
