# Memory.md
> Append-only log. Newest entries at the top of the CHANGELOG section.
> Read STATE first, CHANGELOG for detail.

## STATE — current truth (rewrite this section in place)

### Endpoints
| Method | Path | Status | Tested | Notes |
|---|---|---|---|---|
| GET | /health | live | yes | Basic health and db check. DB not mocked but test isolated. |
| GET | /api/v1/me | mocked | no | contract only |
| POST | /diagnostic/sessions | mocked | no | contract only |
| GET | /diagnostic/sessions/{id} | mocked | no | contract only |
| POST | /diagnostic/sessions/{id}/answer | mocked | no | contract only |
| POST | /diagnostic/sessions/{id}/complete | mocked | no | contract only |
| GET | /profile/learner | mocked | no | contract only |
| PATCH | /profile/learner | mocked | no | contract only |
| POST | /dev/auth/token | mocked | no | contract only |

### Database
Tables that exist: `users`, `alembic_version`.
Latest applied migration ID: 0001.

### Agents
| Agent | Status | Prompt file | Schema class | Tested |
|---|---|---|---|---|
| All | not built yet | | | |

### Environment variables in use
ENV, DEMO_MODE, AUTH_MODE, DATABASE_URL, ALEMBIC_DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWKS_URL, GEMINI_API_KEY, DEV_JWT_SECRET, CORS_ORIGINS, RECORD_FIXTURES

### Known broken / half-finished
- None.

### Do not touch
- None.

## CHANGELOG — append at top, never edit past entries

### [2026-08-29 14:06] chore(ai): pin down Gemini SDK and Models
- Added: `services/agents/models.py` with validated model constants (`gemini-3.1-pro-preview`, `gemini-3.7-flash`, `gemini-3.1-flash-lite`).
- Added: `scripts/smoke_gemini.py` which demonstrates `google-genai` Pydantic response parsing and token usage extraction.
- Validated: `google-genai` version 2.20.0 interfaces verified using the latest available models.
- Broken/left undone: None
- Next: P0.8 - Architecture.md, Memory.md and Phase.md

### [2026-08-29 13:56] feat(core): pagination and sorting contracts
- Added: `services/api/schemas/pagination.py` with generic `PaginatedResponse[T]`, `PaginationParams`, and `SortParams`.
- Contract: All list-returning endpoints must use these schemas for pagination and sorting.
- Tested: `tests/test_pagination.py` validates default params, custom params, and the standard error envelope returning 422 on invalid params (page=0).
- Broken/left undone: None
- Next: Pin down the Gemini SDK before building on it (P0.7)

### [2026-08-29 13:53] chore(db): alembic initialization and initial migration
- Added: `services/api/alembic` directory, `alembic.ini`, and `services/api/models/base.py`.
- Changed: Configured `env.py` for async SQLAlchemy and bound it to `Settings().alembic_database_url`.
- Contract: Alembic points strictly to the `alembic` folder under `services/api`.
- Tested: `alembic upgrade head` ran successfully against Postgres, and `test_health.py` continues to pass.
- Broken/left undone: None
- Next: The contract files (P0.6)

### [2026-08-29 13:48] feat(core): error envelope and exception handling
- Added: `services/api/errors.py` with `AppError` and 8 subclasses.
- Changed: `services/api/main.py` updated with `global_middleware` to catch 500s safely and `exception_handlers` for `AppError`, `RequestValidationError`, and `StarletteHTTPException`.
- Contract: All responses conform to `{"error": {"code": "...", "message": "...", "retryable": bool, "details": {}}}`. `X-Request-ID` is included on every response.
- Tested: `tests/test_errors.py` validates all 4 paths including the catch-all without leaking tracebacks.
- Broken/left undone: None
- Next: Alembic and migration 0001 (P0.5)

### [2026-08-29 13:46] chore(devops): docker compose and offline setup
- Added: Dockerfile, .dockerignore, docker-compose.yml
- Changed: Configured local postgres and API containers.
- Contract: No changes.
- Tested: `docker compose up -d --build` succeeded, and `curl -s localhost:8000/health` returned db ok.
- Broken/left undone: None
- Next: Error envelope and exception handling (P0.4)

### [2026-08-29 13:40] feat(core): project skeleton and health endpoint
- Added: pyproject.toml, .env.example, .gitignore, .agents/mcp_config.example.json, services/api/__init__.py, services/api/main.py, services/api/config.py, services/api/db.py, services/api/routers/__init__.py, services/api/routers/health.py, tests/__init__.py, tests/test_health.py
- Changed: Scaffolded initial project structure.
- Contract: Not yet generated/regenerated (openapi.yaml not setup yet).
- Tested: `uv run pytest tests/test_health.py -v` passed successfully.
- Broken/left undone: None
- Next: Docker compose setup (P0.3)
