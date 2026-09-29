def test_signup_success(client):
    response = client.post(
        "/api/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "Password1"},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["email"] == "alice@example.com"
    assert "password" not in body["data"]
    assert "password_hash" not in body["data"]


def test_duplicate_signup(client, user_a):
    response = client.post(
        "/api/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "Password1"},
    )
    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "DUPLICATE_EMAIL"


def test_signup_weak_password(client):
    response = client.post(
        "/api/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_login_success(client, user_a):
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "Password1"},
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()["data"]


def test_login_incorrect_password(client, user_a):
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "WrongPass1"},
    )
    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_requires_jwt(client, user_a):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_jwt(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["email"] == "alice@example.com"
