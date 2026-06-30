# Task Tracker API

A production-style RESTful API built with **Flask** and **MongoDB**, demonstrating CRUD design, input validation, containerized deployment, and automated testing.

## Features
- Full CRUD REST API for a `Task` resource (`title`, `description`, `status`, `priority`)
- MongoDB persistence via PyMongo, with ObjectId-based resource identifiers
- Request validation with clear 400-level error responses (no silent failures)
- Filtering support (`GET /tasks?status=DONE`)
- Application factory pattern for clean, testable Flask structure
- Unit tests (pytest) covering create, read, update, delete, and validation error paths — run with zero external dependencies via `mongomock`
- Dockerized with `docker-compose` (API + MongoDB) for one-command local deployment

## Tech Stack
Python, Flask, PyMongo, MongoDB, pytest, mongomock, Docker, gunicorn

## API Endpoints

| Method | Endpoint          | Description                  |
|--------|-------------------|-------------------------------|
| GET    | `/health`         | Health check                 |
| GET    | `/tasks`          | List all tasks (`?status=`)  |
| POST   | `/tasks`          | Create a task                |
| GET    | `/tasks/<id>`     | Get a single task            |
| PUT    | `/tasks/<id>`     | Full update                  |
| PATCH  | `/tasks/<id>`     | Partial update                |
| DELETE | `/tasks/<id>`     | Delete a task                |

### Example request
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write unit tests", "priority": 1}'
```

## Running locally with Docker (recommended)
```bash
docker-compose up --build
```
API will be available at `http://localhost:5000`.

## Running locally without Docker
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# requires a local MongoDB instance running on 27017
export MONGO_URI="mongodb://localhost:27017/taskdb"
python run.py
```

## Running tests
Tests use `mongomock`, so no live database is required:
```bash
pytest -v
```

## Project Structure
```
flask-task-api/
├── app/
│   ├── __init__.py      # App factory + DB connection
│   ├── routes.py        # REST endpoints (Blueprint)
│   └── validation.py    # Request payload validation
├── tests/
│   └── test_tasks.py    # Pytest suite
├── run.py               # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```
