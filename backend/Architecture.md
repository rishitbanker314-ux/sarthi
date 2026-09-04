# Architecture.md

## A1. Stack
| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.11+ | Type hints everywhere |
| Framework | FastAPI | Auto-generates OpenAPI spec |
| Validation | Pydantic v2 | Every boundary, every agent output |
| Server | Uvicorn | |
| DB | PostgreSQL 16 | Local via Docker for dev and demo; Supabase in the cloud |
| ORM | SQLAlchemy 2.0 (async, asyncpg) | |
| Migrations | Alembic (sync psycopg) | Forward-only. Separate ALEMBIC_DATABASE_URL. |
| Auth | Supabase Auth, verified locally against JWKS (ES256) | We never see or store a password. Dev-only HS256 issuer. |
| Storage | Supabase Storage | Only if S5 is reached |
| LLM | Google Gemini API via google-genai | Structured output mode, always |
| Embeddings | Gemini text-embedding-004 | Only if S5 is reached |
| Vector store | pgvector extension | Same Postgres |
| Cache / jobs | In-process BackgroundTasks (default) | Optional Redis + arq |
| Testing | pytest + httpx | |
| Lint/format | ruff + black | |
| Local run | Docker Compose | Postgres + API. Must run offline |

## A2. Repository layout
services/api/ - Core FastAPI application, routers, schemas, and DB models
services/agents/ - LLM interaction layer and agent logic

## A3. Data model
users(id, email, display_name, locale) - Exists
learner_profiles(...) - Not built yet
diagnostic_sessions(...) - Not built yet
concepts(...) - Not built yet
goals(...) - Not built yet
plans(...) - Not built yet
modules(...) - Not built yet
lessons(...) - Not built yet
lesson_contents(...) - Not built yet
checkpoints(...) - Not built yet
checkpoint_attempts(...) - Not built yet
mastery_states(...) - Not built yet
tutor_threads(...) - Not built yet
tutor_messages(...) - Not built yet
signals(...) - Not built yet
adaptation_events(...) - Not built yet
jobs(...) - Not built yet

## A4. API surface
GET /health - No auth, returns version + db status
(All other endpoints not built yet)

## A5. Agent layer
- **Bounding size**: The prompt enforces a hard maximum on the number of modules and lessons (e.g. max 5 modules, max 5 lessons each). For massive goals, the LLM is instructed to chunk the domain and focus only on the foundational slice to get started, rather than generating the entire curriculum.
- **Vague/Non-educational goals**: The Planner agent contains a strict classification gate. If a goal is deemed non-educational or impossible, it refuses to generate a plan and instead sets the job status to `failed_validation` with a helpful clarification message for the user, preventing junk plans.
- **Generic rationale avoidance**: The rationale must directly cite specific traits from the `LearnerProfile` (e.g. "Because you prefer concrete examples, we start with a hands-on project"). The LLM prompt explicitly forbids generic filler.
- **Deciding prerequisites**: We rely on the LLM's vast parametric knowledge of the domain to implicitly sequence topics from foundational to advanced, using standard pedagogical dependencies, since we don't have a rigid concept graph yet.
- **Partial failure mid-generation**: Plan generation happens within a single atomic database transaction. If the generation or parsing fails midway, the transaction rolls back so we never save a half-baked plan. The async job status is updated to `failed` and can be retried or surfaced.
- **Existing mastery**: The `LearnerProfile` includes the user's prior knowledge. The Planner prompt strictly instructs the LLM to skip basics and start the plan at an advanced level if prior mastery is detected.

### Adaptor Agent & Re-planning
- **Firing on noise**: We use trailing windows of multiple signals (e.g. 3 consecutive failures, multiple confusion flags) to trigger adaptations, rather than single data points.
- **Declined adaptations**: We force adaptation if the user declines but immediately fails again, as the data proves they are stuck.
- **Honest reasoning**: The Adaptor agent outputs a structured before/after diff. The API layer asserts that the generated plain-language reason directly correlates with the structural changes.
- **Completed lessons**: Completed lessons are immutable and retained in the new plan. Re-planning only sequences and structures un-started lessons.
- **Cache invalidation**: The cache key for lesson content includes the `plan_id`. When a plan changes, the `plan_id` changes, cleanly invalidating the cache for un-started lessons.
- **Explainability**: For skeptical judges, we build an admin/demo view showing raw signals, crossed thresholds, the exact before/after JSON of the plan, and the generated reason side by side.

## A6. Async job model
Not built yet.

## A7. Caching strategy
Not built yet.

## A8. Auth & security
- **JWKS Key Rotation & DoS Protection:** Cache the JWKS by `kid`. On unknown `kid`, refetch at most ONCE, and globally rate-limit refetches to 1 per 60 seconds to prevent DDoS via fake kids.
- **Clock Skew:** Strictly allow 60 seconds of clock skew for `exp` and `nbf` claims to handle drifting mobile device clocks.
- **Mode Confusion Prevention:** Explicitly pin verification algorithms (`ES256` for Supabase, `HS256` for Local) at the call site. Never derive the algorithm from the token header. Reject `HS256` outright when `AUTH_MODE=supabase`.
- **Concurrency (Lazy Profile Creation):** `GET /me` handles simultaneous requests gracefully (e.g., via `INSERT ... ON CONFLICT DO NOTHING`) to avoid race conditions when lazily creating user rows.
- **Cross-Tenant Data Leakage:** A central `get_current_user` dependency injects the validated `user_id`. Queries must strictly filter by `user_id == current_user.id` to prevent data leakage between learners.

## A9. Configuration
ENV - Environment (development/production)
DEMO_MODE - Boolean to serve fixtures instead of network calls
AUTH_MODE - supabase or local
DATABASE_URL - Async SQLAlchemy DB connection string
ALEMBIC_DATABASE_URL - Sync psycopg DB connection string
SUPABASE_URL - Supabase project URL
SUPABASE_ANON_KEY - Supabase anon key
SUPABASE_SERVICE_ROLE_KEY - Supabase service role key
SUPABASE_JWKS_URL - Supabase JWKS URL for token verification
GEMINI_API_KEY - Google Gemini API Key
DEV_JWT_SECRET - Secret for signing offline tokens
CORS_ORIGINS - Allowed CORS origins
RECORD_FIXTURES - Boolean to record new responses into fixtures

## A10. Local development
1. Copy `.env.example` to `.env` and fill in secrets.
2. Run `docker compose up -d --build` to start API and Postgres.
3. Apply migrations: `uv run alembic upgrade head`.
4. API is available at `http://localhost:8000`.

## A11. Decision log
| Date | Decision | Alternatives considered | Why |
|---|---|---|---|
| 2026-08-29 | Postgres locally for dev and demo, Supabase in the cloud, same migrations | Separate sqlite for local | The demo must work with no network, and schema parity is essential |
| 2026-08-29 | Supabase Auth with local JWKS verification | Handling passwords manually, Auth0 | It removes password handling from our code entirely |
| 2026-08-29 | Session pooler on port 5432 | Direct connection, Transaction pooler | Direct connection is IPv6-only; transaction pooler breaks asyncpg prepared statements |
