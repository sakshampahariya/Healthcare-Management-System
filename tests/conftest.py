from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app import create_app
from app.extensions import db
from app.models import DiagnosticCentre, DiagnosticTest, User


@pytest.fixture
def app():
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user_a(app):
    user = User(name="Alice Patient", email="alice@example.com")
    user.set_password("Password1")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def user_b(app):
    user = User(name="Bob Patient", email="bob@example.com")
    user.set_password("Password1")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def centre(app):
    centre = DiagnosticCentre(name="EVE Koramangala", location="Bengaluru")
    db.session.add(centre)
    db.session.commit()
    return centre


@pytest.fixture
def other_centre(app):
    centre = DiagnosticCentre(name="EVE Whitefield", location="Bengaluru")
    db.session.add(centre)
    db.session.commit()
    return centre


@pytest.fixture
def diagnostic_test(app, centre):
    test = DiagnosticTest(
        centre_id=centre.id,
        name="CBC",
        description="Complete blood count",
        price=Decimal("499.00"),
    )
    db.session.add(test)
    db.session.commit()
    return test


@pytest.fixture
def other_test(app, other_centre):
    test = DiagnosticTest(
        centre_id=other_centre.id,
        name="LFT",
        description="Liver function",
        price=Decimal("950.00"),
    )
    db.session.add(test)
    db.session.commit()
    return test


def login(client, email="alice@example.com", password="Password1"):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client, user_a):
    return login(client, user_a.email)


@pytest.fixture
def auth_headers_b(client, user_b):
    return login(client, user_b.email)


def future_appointment() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=7)).replace(microsecond=0).isoformat()


@pytest.fixture
def booking_payload(centre, diagnostic_test):
    return {
        "test_id": diagnostic_test.id,
        "centre_id": centre.id,
        "appointment_datetime": future_appointment(),
    }


@pytest.fixture
def booking(client, auth_headers, booking_payload):
    response = client.post("/api/bookings", json=booking_payload, headers=auth_headers)
    assert response.status_code == 201
    return response.get_json()["data"]
