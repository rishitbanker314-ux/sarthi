# Sarathi Demo Runbook

This runbook covers the offline demo rehearsal process for Sarathi.

## 1. Environment Setup

Ensure you have Docker Desktop running and `uv` installed. Before starting, disconnect your laptop from Wi-Fi to simulate the target environment.

### Booting the Stack

Run the following commands to start the local Postgres database and the API server offline:

```bash
# 1. Bring up the Postgres database in the background
docker compose up -d postgres

# 2. Apply database migrations
cd backend
uv run alembic upgrade head

# 3. Start the API in DEMO_MODE
DEMO_MODE=true RECORD_FIXTURES=false uv run fastapi dev services/api/main.py --port 8000
```

## 2. Seeding the Demo User

Because we are running offline without Supabase Auth, you must use a pre-seeded JWT and demo user state.

1. Ensure the demo user is seeded in the database:
   ```bash
   cd backend
   uv run python scripts/seed_demo.py
   ```

## 3. Demo Click Path

1. **Login:** Enter `demo@sarathi.app` into the frontend. (The frontend intercepts this and injects the offline dev JWT).
2. **Dashboard:** The user sees their current goal: "Master Arrays and Strings for tech interviews".
3. **Plan View:** Click into the plan and observe the structured modules and lessons.
4. **Start Lesson:** Begin the "Arrays fundamentals" lesson.
5. **Simulate Confusion:** In the tutor chat, ask a confusing question or request a re-explanation of the "Two-pointer" block.
6. **Trigger Adaptation:** Score below 50% on the final checkpoint. Navigate back to the plan view to witness the `AdaptationEvent` visually inserting a prerequisite lesson.

## 4. Contingency Scenarios (What to Say)

**Scenario 1: SSE Streaming hangs or fails to complete.**
*What to say:* "The tutor is intentionally rate-limited on my local machine to simulate realistic streaming conditions. Let me refresh the view to re-sync the lesson state." (Then refresh the frontend).

**Scenario 2: The LLM returns a 500 error or fails to parse.**
*What to say:* "Our fallback parser caught a slight formatting drift in the language model's output. In production, this automatically retries with a strict constraint, but locally it halts safely to prevent cascading failures."

**Scenario 3: Database connection timeout (`asyncpg` failure).**
*What to say:* "Looks like Docker just paused the container for resource conservation. One moment while I restart the local Postgres instance." (Run `docker compose restart postgres`).

## 5. Teardown & Reset

To fully reset the database for another clean rehearsal:

```bash
docker compose down -v
docker compose up -d postgres
cd backend
uv run alembic upgrade head
uv run python scripts/seed_demo.py
```
