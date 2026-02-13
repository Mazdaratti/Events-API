"""
Unit tests for pure model logic.

These tests:
- Do NOT require a running Flask server
- Do NOT require a database session
- Do NOT perform any HTTP requests

They only validate pure Python logic inside the models.
"""

from datetime import datetime, timezone

from models import User, Event, RSVP


# ============================================================
# User Model Tests
# ============================================================

def test_user_password_hashing_behaves_correctly():
    """
    Verifies that:
    - Passwords are hashed (not stored in plain text)
    - Correct password validates successfully
    - Incorrect password fails validation
    """

    user = User(username="alice")

    # Hash and store password
    user.set_password("secret123")

    # Password hash should exist
    assert user.password_hash is not None

    # The hash must NOT equal the raw password
    assert user.password_hash != "secret123"

    # Correct password should validate
    assert user.check_password("secret123") is True

    # Wrong password must fail
    assert user.check_password("wrong") is False


def test_user_to_dict_excludes_password_hash():
    """
    Ensures that sensitive fields (like password_hash)
    are not exposed via the public serialization method.
    """

    user = User(username="bob", is_admin=False)
    user.set_password("pw")

    payload = user.to_dict()

    # Basic field correctness
    assert payload["username"] == "bob"
    assert payload["is_admin"] is False

    # Security check: password hash must never be exposed
    assert "password_hash" not in payload


# ============================================================
# Event Model Tests
# ============================================================

def test_event_to_dict_basic_fields():
    """
    Verifies that Event.to_dict():
    - Returns expected public fields
    - Calculates RSVP count correctly
    - Returns empty attendees list when no RSVPs exist
    """

    event = Event(
        title="Test Event",
        description="Desc",
        date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        location="Berlin",
        capacity=50,
        is_public=True,
        requires_admin=False,
        created_by=None,
    )

    # Simulate no RSVPs without using the database.
    # We directly attach an empty list to the relationship.
    event.rsvps = []

    payload = event.to_dict()

    assert payload["title"] == "Test Event"
    assert payload["capacity"] == 50
    assert payload["rsvp_count"] == 0
    assert payload["attendees"] == []


def test_event_to_dict_counts_only_user_attendees():
    """
    Ensures that:
    - rsvp_count counts ALL RSVP entries
    - attendees only includes user_id values
      where attending == True AND user_id is not None

    Note: Event.rsvps is a SQLAlchemy relationship, so it must contain
    SQLAlchemy-mapped instances (RSVP), not plain Python objects.
    """

    event = Event(
        title="RSVP Test",
        description="Desc",
        date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        location="Berlin",
        capacity=10,
        is_public=True,
        requires_admin=False,
        created_by=None,
    )

    # Pure in-memory objects: no DB session, no commit, no HTTP.
    event.rsvps = [
        RSVP(user_id=1, attending=True, event_id=1),
        RSVP(user_id=2, attending=False, event_id=1),
        RSVP(user_id=None, attending=True, event_id=1),  # anonymous attendee
        RSVP(user_id=3, attending=True, event_id=1),
    ]

    payload = event.to_dict()

    assert payload["rsvp_count"] == 4
    assert set(payload["attendees"]) == {1, 3}
