# Evently API

A Flask-based REST API for managing events and RSVPs with different access levels. This API is designed to teach web security best practices through incremental improvements.

## Features

- **Public Events**: Anyone can RSVP without authentication
- **Protected Events**: Requires user authentication to RSVP
- **Admin Events**: Requires admin role to RSVP

## Tech Stack

- Flask 3.0.0
- Flask-SQLAlchemy (SQLite database)
- Flask-CORS
- Flask-JWT-Extended (JWT authentication)

## Setup

1. Create and activate a virtual environment:

   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **Linux/Mac:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Swagger UI Documentation

The API includes interactive Swagger UI documentation. After starting the server:

1. Open your browser and navigate to: `http://localhost:5000/apidocs`

2. You'll see an interactive API documentation interface where you can:
   - Browse all available endpoints
   - See request/response schemas
   - Test endpoints directly from the browser
   - Authenticate using the "Authorize" button (enter your JWT token)

3. To use the "Authorize" button:
   - First, login via `/api/auth/login` to get your JWT token
   - Click the "Authorize" button at the top of the Swagger UI
   - Enter: `Bearer <your_jwt_token>` (replace `<your_jwt_token>` with your actual token)
   - Now you can test protected endpoints directly from Swagger UI

**Alternative**: You can also view the OpenAPI specification directly at `http://localhost:5000/apispec_1.json`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```

- `POST /api/auth/login` - Login and get JWT token
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```

### Events

- `GET /api/events` - Get all events
- `GET /api/events/<id>` - Get a specific event
- `POST /api/events` - Create a new event (requires authentication)
  ```json
  {
    "title": "Python Meetup",
    "description": "Monthly Python developer meetup",
    "date": "2026-01-15T18:00:00",
    "location": "Tech Hub, Room 101",
    "capacity": 50,
    "is_public": true,
    "requires_admin": false
  }
  ```

### RSVPs

- `POST /api/rsvps/event/<event_id>` - RSVP to an event
  ```json
  {
    "attending": true
  }
  ```

- `GET /api/rsvps/event/<event_id>` - Get all RSVPs for an event

## Authentication

For protected endpoints, include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Security Notes

This is a basic implementation designed for educational purposes. The following security considerations are intentionally simplified and can be improved in subsequent lessons:

- Password storage (currently using werkzeug, but can be improved)
- JWT token handling
- Input validation
- SQL injection prevention (SQLAlchemy helps, but can be improved)
- Rate limiting
- CORS configuration
- Error handling and information disclosure

## Database

The application uses SQLite by default. The database file (`events.db`) will be created automatically on first run.

**Note**: The first user registered automatically becomes an admin for demo purposes.

---

## Testing

This project includes both unit and integration tests implemented with `pytest`.

### Test Structure

- `tests/test_models.py`  
  Pure unit tests for model logic.  
  These tests do **not** require a running server or a database connection.

- `tests/test_api.py`  
  Integration tests that perform real HTTP requests against a running API server.

- `tests/conftest.py`  
  Shared fixtures and configuration (e.g. `BASE_URL`, auth helpers, server availability check).

---

### Running Tests

1. Start the API locally:

```bash
python app.py
````

2. In a separate terminal, run:

```bash
pytest
```

---

### Integration Test Behavior

Integration tests require a running Events API server.

If the server is not reachable at:

```
http://localhost:5000
```

(or the configured `BASE_URL`), integration tests **FAIL**.
This prevents false-positive test passes and ensures CI reliability.

Unit tests still execute independently, but the overall test run will fail.

Example output when the server is **not** running:

```
Failed: Events API not reachable at http://localhost:5000.
```

---

### Environment Configuration

Integration tests read `BASE_URL` from environment variables.

By default, configuration is loaded from a local `.env` file:

```bash
BASE_URL=http://localhost:5000
```

The `.env` file is loaded automatically via `python-dotenv`.

If no `BASE_URL` is provided, it defaults to:

```
http://localhost:5000
```

You can temporarily override the value via environment variable:

```bash
BASE_URL=http://localhost:5001 pytest
```

Environment variables take precedence over values defined in `.env`.

---

### Test Coverage Overview

The current test suite covers:

* Password hashing and validation behavior
* Model serialization logic
* Health endpoint
* User registration and login
* Authenticated event creation
* Public RSVP behavior
* Error cases (duplicate registration, missing auth, protected RSVP)

> **Note:** Integration tests currently write into the configured database.
> Database isolation can be introduced in a future iteration (e.g. during the Docker/CI phase).

---

## Docker

The Events API can be run inside a Docker container for a fully reproducible runtime environment.

### Build the Docker Image

From the project root:

```bash
docker build -t my_events_api .
```

This builds a container image using:

* `python:3.11-slim` as base image
* Layer caching for dependency installation
* Optimized image size via `.dockerignore`

---

### Run the Container

```bash
docker run -p 5000:5000 --name events-api-container my_events_api
```

The API will be available at:

```
http://localhost:5000
```

Health check:

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{"status":"healthy"}
```

---

### Stopping and Removing the Container

```bash
docker stop events-api-container
docker rm events-api-container
```

---

### Running Tests Against the Container

1. Start the container.
2. In a separate terminal, run:

```bash
pytest -v
```

Unit tests run locally.
Integration tests perform real HTTP requests against the containerized API.

All tests must pass while the API is running inside Docker.

---

# Continuous Integration (GitHub Actions)

CI runs automatically on:

- Push
- Pull Request

Markdown-only changes do NOT trigger CI.

## CI Pipeline Steps

1. Install dependencies
2. Run unit tests
3. Build Docker image
4. Start container
5. Wait for health endpoint
6. Run integration tests
7. Clean up container

This guarantees:

- Tests pass
- Docker image builds correctly
- Container starts successfully
- API responds correctly

CI must pass before merging to `main`.

---

# Docker Hub Release Policy

Docker images are published **only when a version tag is pushed**.

Example version tag:

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## What Happens on Tag Push

Release workflow:

1. Checks out tagged commit
2. Builds Docker image
3. Pushes image to Docker Hub

Published tags:

- `vX.Y.Z` (deterministic release tag)
- `latest` (points to latest released version)

This ensures:

- Reproducible deployments
- Clear release history
- Explicit version control

---

# Docker Hub Image

Repository:

```
https://hub.docker.com/r/<your-dockerhub-username>/events-api
```

Pull specific version:

```bash
docker pull <your-dockerhub-username>/events-api:v1.0.0
```

Pull latest release:

```bash
docker pull <your-dockerhub-username>/events-api:latest
```

---

# GitHub Secrets Required

To enable Docker publishing, configure in:

GitHub → Repository → Settings → Secrets and variables → Actions

Required secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN` (Docker Hub Personal Access Token with write permissions)

---

# Deployment

This project is designed to:

- Build via GitHub Actions
- Publish Docker images to Docker Hub
- Deploy container to Render

Deployment pulls a specific version tag (`vX.Y.Z`) for deterministic runtime.