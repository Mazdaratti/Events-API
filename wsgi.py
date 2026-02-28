"""
WSGI entrypoint for production servers (e.g., Gunicorn).

This module exposes a top-level `app` object so that
Gunicorn can import it using: wsgi:app
"""

from app import create_app

app = create_app()