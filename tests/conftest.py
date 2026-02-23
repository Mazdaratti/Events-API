"""
Shared pytest fixtures for integration tests.

These tests:
- Perform real HTTP requests to a running API
- Load configuration from environment variables
- Support local .env file for development

To keep the developer experience smooth, we skip integration tests
if the server is not reachable.
"""

import os
import uuid

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

# Allow overriding locally/CI via env var if needed later.
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


def _is_server_up() -> bool:
    """
    Minimal health probe used to decide if integration tests should run.
    We keep timeouts low to fail fast.
    """
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False


@pytest.fixture(scope="session")
def require_running_server():
    """
    Integration tests require a running API server.

    - In CI we must not "pass" by skipping integration tests.
    - Failing here guarantees that a missing/unhealthy server breaks the build.
    - Unit tests remain independent because they do not use this fixture.
    """
    if not _is_server_up():
        pytest.fail(
            f"Events API not reachable at {BASE_URL}. "
            "Start the server (python app.py) or run the Docker container and re-run pytest."
        )


@pytest.fixture()
def unique_username() -> str:
    """
    Generates a unique username on every test run
    to avoid collisions across repeated runs.
    """
    return f"user_{uuid.uuid4().hex[:12]}"


@pytest.fixture()
def password() -> str:
    """Shared password used for test users."""
    return "securepassword123"


def register_user(username: str, password: str) -> requests.Response:
    """
    Helper that calls the registration endpoint.
    Returns the raw Response so tests can assert status + JSON.
    """
    return requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": password},
        timeout=5,
    )


def login_user(username: str, password: str) -> requests.Response:
    """
    Helper that calls the login endpoint.
    Returns the raw Response so tests can assert status + JSON.
    """
    return requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password},
        timeout=5,
    )


@pytest.fixture()
def auth_token(unique_username, password) -> str:
    """
    Creates a user and logs in, returning a valid JWT access token.
    This keeps tests concise and consistent.
    """
    r = register_user(unique_username, password)
    assert r.status_code == 201, r.text

    r = login_user(unique_username, password)
    assert r.status_code == 200, r.text

    token = r.json().get("access_token")
    assert token, r.text
    return token


@pytest.fixture()
def auth_headers(auth_token) -> dict:
    """
    Standard Authorization header for endpoints protected by JWT.
    """
    return {"Authorization": f"Bearer {auth_token}"}


def create_event(headers: dict | None, payload: dict) -> requests.Response:
    """
    Helper to create events. For authenticated requests, pass headers.
    """
    return requests.post(
        f"{BASE_URL}/api/events",
        json=payload,
        headers=headers,
        timeout=5,
    )
