"""
Integration tests for the Events API.

These tests perform HTTP calls against a running server.
They validate the core "happy path" flows plus key error cases.
"""

from datetime import datetime, timedelta, timezone

import requests

import pytest


from tests.conftest import BASE_URL, register_user, login_user, create_event

pytestmark = pytest.mark.usefixtures("require_running_server")

# -------------------------
# Happy path tests
# -------------------------

def test_health_endpoint_returns_healthy():
    """
    Health endpoint should:
    - return 200
    - include JSON payload that indicates service health
    """
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


def test_register_user_creates_new_user(unique_username, password):
    """
    Registering a user should:
    - return 201
    - include created user with matching username
    """
    r = register_user(unique_username, password)
    assert r.status_code == 201, r.text

    data = r.json()
    assert data["user"]["username"] == unique_username


def test_login_returns_jwt_token(unique_username, password):
    """
    Logging in with valid credentials should:
    - return 200
    - include access_token
    """
    r = register_user(unique_username, password)
    assert r.status_code == 201, r.text

    r = login_user(unique_username, password)
    assert r.status_code == 200, r.text

    data = r.json()
    assert "access_token" in data
    assert data["access_token"]


def test_create_public_event_succeeds_with_token(auth_headers):
    """
    Creating an event requires auth and should succeed with a valid token.
    """
    dt = (datetime.now(timezone.utc) + timedelta(days=7)).replace(microsecond=0)
    payload = {
        "title": "Public Test Event",
        "description": "Integration test event",
        "date": dt.isoformat(),
        "location": "Berlin",
        "capacity": 25,
        "is_public": True,
        "requires_admin": False,
    }

    r = create_event(auth_headers, payload)
    assert r.status_code == 201, r.text

    data = r.json()
    assert data["title"] == payload["title"]
    assert data["is_public"] is True


def test_rsvp_to_public_event_succeeds_without_auth(auth_headers):
    """
    RSVP to a public event should not require auth:
    - First create a public event (auth required)
    - Then RSVP without passing Authorization header
    """
    dt = (datetime.now(timezone.utc) + timedelta(days=10)).replace(microsecond=0)
    event_payload = {
        "title": "RSVP Public Event",
        "description": "RSVP integration test",
        "date": dt.isoformat(),
        "location": "Hamburg",
        "capacity": 50,
        "is_public": True,
        "requires_admin": False,
    }

    r = create_event(auth_headers, event_payload)
    assert r.status_code == 201, r.text
    event_id = r.json()["id"]

    r = requests.post(
        f"{BASE_URL}/api/rsvps/event/{event_id}",
        json={"attending": True},
        timeout=5,
    )
    assert r.status_code in (200, 201), r.text

    data = r.json()
    assert data["event_id"] == event_id
    assert data["attending"] is True


# -------------------------
# Edge / error-case tests
# -------------------------

def test_register_duplicate_username_returns_400(unique_username, password):
    """
    Registering the same username twice should return 400 on the second attempt.
    """
    r1 = register_user(unique_username, password)
    assert r1.status_code == 201, r1.text

    r2 = register_user(unique_username, password)
    assert r2.status_code == 400, r2.text


def test_create_event_without_auth_returns_401():
    """
    Creating an event without Authorization header should return 401.
    """
    dt = (datetime.now(timezone.utc) + timedelta(days=5)).replace(microsecond=0)
    payload = {
        "title": "Should Fail",
        "description": "No auth",
        "date": dt.isoformat(),
        "location": "Berlin",
        "capacity": 10,
        "is_public": True,
        "requires_admin": False,
    }

    r = create_event(headers=None, payload=payload)
    assert r.status_code == 401, r.text


def test_rsvp_to_non_public_event_without_auth_returns_401(auth_headers):
    """
    RSVP to a non-public event should require authentication.
    - Create a protected event (is_public=false)
    - Attempt RSVP without auth => 401
    """
    dt = (datetime.now(timezone.utc) + timedelta(days=12)).replace(microsecond=0)
    event_payload = {
        "title": "Protected Event",
        "description": "Non-public event",
        "date": dt.isoformat(),
        "location": "Munich",
        "capacity": 10,
        "is_public": False,
        "requires_admin": False,
    }

    r = create_event(auth_headers, event_payload)
    assert r.status_code == 201, r.text
    event_id = r.json()["id"]

    r = requests.post(
        f"{BASE_URL}/api/rsvps/event/{event_id}",
        json={"attending": True},
        timeout=5,
    )
    assert r.status_code == 401, r.text
