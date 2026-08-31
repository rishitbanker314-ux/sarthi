# Sarathi Backend Handover

## Overview
This folder contains the backend `.env` file needed to run the API locally. The `contract/` directory in the repository contains the OpenAPI schema (`openapi.yaml`) which you can use to generate your frontend client.

## Getting Started

1. Clone the repository into a separate folder (if you haven't already).
2. Checkout the backend branch: `git checkout backend`
3. Copy the attached `.env` file directly into the **`backend/`** folder. (Do not put one in the root of the repo).

## Running the Backend

You can run the backend via Docker or directly using `uv`. **All commands must be run from inside the `backend/` folder.**

### Option A: Docker Compose (Preferred)
Run this from inside the `backend/` folder:
```bash
docker compose up -d --build
```
*(Note: If port 5432 is already allocated by a local Postgres instance, use Option B instead.)*

### Option B: Local Development Server with uv
Run this from inside the `backend/` folder:
```bash
uv run fastapi dev services/api/main.py --port 8000
```
*(Note: Do not override `DEMO_MODE` or `AUTH_MODE` here—the `.env` already configures them correctly!)*

## Applying Migrations and Seeding Data
Once the server is running, you need to apply the database migrations and seed the initial data.
Since these commands are run on your host machine, the `.env` uses `localhost` to connect to Postgres.
(When running inside Docker, `docker-compose.yml` automatically overrides the host to `postgres`.)

Run these from the `backend/` folder:
```bash
uv run alembic upgrade head
uv run python -m scripts.seed_demo
```

## Verification
Confirm the API is healthy by running:
```bash
curl http://localhost:8000/health
```

## Local Offline Mode
The `.env` ships with `AUTH_MODE=supabase` so your real login screen works. If you ever need to work fully offline, you can flip `AUTH_MODE=local` in the `.env`. In local mode, there is no login screen; you retrieve a valid JWT token by sending a POST request:
```bash
curl -X POST http://localhost:8000/dev/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@sarathi.app"}'
```

## API Documentation
Interactive API documentation (Swagger UI) is available at:
http://localhost:8000/docs
