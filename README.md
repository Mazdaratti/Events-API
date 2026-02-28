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

### Local (default)

Locally, the application uses SQLite by default.

A database file (`events.db`) is created automatically on first run.

### Render (production)

On Render, the application uses PostgreSQL via the `DATABASE_URL` environment variable.

This provides persistence across redeploys and container restarts.

**Note:** For demo purposes, the first user registered becomes an admin.

---

## Testing

This project includes both unit and integration tests using `pytest`.

### Test Structure

* `tests/test_models.py`
  Unit tests for model logic (no HTTP calls)

* `tests/test_api.py`
  Integration tests that perform real HTTP requests against a running API server

* `tests/conftest.py`
  Shared fixtures and configuration (e.g. `BASE_URL`, auth helpers, server availability check)

---

### Running Tests (Local)

1. Start the API locally:

```bash
python app.py
```

2. In a separate terminal:

```bash
pytest -v
```

---

### Integration Test Behavior (important)

Integration tests require a running Events API server.

They run against:

* `BASE_URL` environment variable if set
* otherwise default: `http://localhost:5000`

If the server is not reachable at the configured `BASE_URL`,
integration tests **FAIL** (they are not skipped).

This prevents false-positive test runs and ensures CI reliability.

Example failure when API is not running:

```
Failed: Events API not reachable at http://localhost:5000.
```

---

### Environment Configuration (tests)

You can override the test target:

**Windows PowerShell**

```powershell
$env:BASE_URL="http://localhost:5001"; pytest -v
```

**Linux/Mac**

```bash
BASE_URL=http://localhost:5001 pytest -v
```

---

### Test Coverage Overview

Current tests cover:

* Password hashing and validation
* Model serialization logic
* Health endpoint
* User registration and login
* Authenticated event creation
* Public RSVP behavior
* Error cases (duplicate registration, missing auth, protected RSVP)

---

## Docker

The Events API can be run in a container for a reproducible runtime environment.

### Build the Docker image

```bash
docker build -t events-api:local .
```

### Run the container (local port 5000)

The container runs the API using **Gunicorn** (production server), not Flask dev server.

```bash
docker run --rm -p 5000:5000 -e PORT=5000 --name events-api events-api:local
```

API available at:
`http://localhost:5000`

Health check:

```bash
curl http://localhost:5000/api/health
```

Expected:

```json
{"status":"healthy"}
```

---

### Production runtime details (Gunicorn + wsgi.py)

Gunicorn needs an importable WSGI entrypoint in the form `module:app`.

This project provides `wsgi.py` as that entrypoint.

The container command follows the Render pattern:

* bind to `0.0.0.0:$PORT`
* optionally use `WEB_CONCURRENCY` when available

---

### Run tests against the container

1. Start the container
2. Run tests from the host:

```bash
pytest -v
```

Unit tests run locally.

Integration tests send HTTP requests to the containerized API using `BASE_URL`
(default `http://localhost:5000`).

---

## Continuous Integration (GitHub Actions)

CI is designed to validate every change before it reaches `main`.

CI runs on:

* pushes to feature branches (e.g. `feat/*`)
* pull requests targeting `main`

Documentation-only changes (`README.md`, `*.md`) do not trigger CI.

### CI Pipeline Steps

1. Install dependencies
2. Run unit tests (`tests/test_models.py`)
3. Build Docker image
4. Run container
5. Wait for `/api/health`
6. Run integration tests (`tests/test_api.py`) against the container
7. Always stop + remove the container

This guarantees:

* tests pass
* Docker image builds
* container boots
* API is reachable via HTTP

---

### Optional: Two-Job CI Workflow Template

This repository includes an optional two-job CI template:

```
.github/workflows/ci_2_job.yml.template
```

It is stored as `.template` so it does not run automatically.

---

## Docker Hub Publishing

### GitHub secrets required (Docker Hub)

Configure in:

GitHub → Settings → Secrets and variables → Actions

Required:

* `DOCKERHUB_USERNAME`
* `DOCKERHUB_TOKEN` (Docker Hub PAT with write access)

---

## Release Workflow (version tags)

Immutable Docker images are published only when a semantic version tag is pushed:

```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

Release workflow publishes:

* `<user>/events-api:vX.Y.Z`

Important:

* The Release workflow does not publish latest.

* The latest tag is owned by the CD workflow and always represents the current      deployable state of main.

* This avoids collisions and keeps deployments deterministic.

* Use version tags for deterministic runtime.

---

## Continuous Deployment (Render)

Deployment is automated to Render using the Docker Hub `latest` image.

CD flow:

1. merge to `main`
2. CD workflow builds and pushes `<user>/events-api:latest`
3. CD triggers a Render deploy hook
4. Render pulls the new `latest`
5. CD smoke test verifies:

   * `/api/health`
   * `/api/events`

### GitHub secrets required (Render CD)

Add these in GitHub Actions secrets:

* `RENDER_DEPLOY_HOOK` (Render deploy hook URL)
* `RENDER_BASE_URL` (e.g. `https://events-api-latest.onrender.com`)

---

## Render Setup Steps (what was done)

### 1) Create a Render Project

Create a project and place both services inside it:

* Postgres database
* Web service

### 2) Create Render Postgres

* Plan: Free (for development/testing)
* Region: same as the Web service
* Copy the **Internal Database URL**

### 3) Create Render Web Service (Docker)

* Deploy from Docker image:

  * `<dockerhub-username>/events-api:latest`
* Configure environment variables (Render → Environment):

  * `DATABASE_URL` = Render **Internal Database URL**
  * `SECRET_KEY` = random secure value
  * `JWT_SECRET_KEY` = random secure value

Render provides:

* `PORT`
* `WEB_CONCURRENCY`

### 4) Create Deploy Hook

In Render Web Service settings:

* Create a deploy hook
* Store it in GitHub secrets as `RENDER_DEPLOY_HOOK`

---

## Smoke test + DB persistence verification

Smoke test (automated in CD):

* `/api/health` must return 200
* `/api/events` must return 200

Persistence verification (manual proof performed):

* create a user
* login to obtain JWT
* create an event
* redeploy via deploy hook
* confirm the event still exists after redeploy

This confirms PostgreSQL is being used and data persists outside the container.

---

