# Memory.md
> Append-only log. Newest entries at the top of the CHANGELOG section.
> Read STATE first, CHANGELOG for detail.

## STATE — current truth (rewrite this section in place)

### Endpoints
| Method | Path | Status | Tested | Notes |
|---|---|---|---|---|
| GET | /health | live | yes | Basic health and db check. DB not mocked but test isolated. |
| GET | /api/v1/me | live | yes | P1.3 implemented |
| POST | /diagnostic/sessions | mocked | no | contract only |
| GET | /diagnostic/sessions/{id} | mocked | no | contract only |
| POST | /diagnostic/sessions/{id}/answer | mocked | no | contract only |
| POST | /diagnostic/sessions/{id}/complete | mocked | no | contract only |
| GET | /profile/learner | mocked | no | contract only |
| PATCH | /profile/learner | mocked | no | contract only |
| POST | /dev/auth/token | live | yes | Local dev authentication |

### Database
Tables that exist: `users`, `alembic_version`, `learner_profiles`, `diagnostic_sessions`, `concepts`.
Latest applied migration ID: cbe458a6eb04.

### Agents
| Agent | Status | Prompt file | Schema class | Tested |
|---|---|---|---|---|
| All | not built yet | | | |

### Environment variables in use
ENV, DEMO_MODE, AUTH_MODE, DATABASE_URL, ALEMBIC_DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWKS_URL, GEMINI_API_KEY, DEV_JWT_SECRET, CORS_ORIGINS, RECORD_FIXTURES

### Known broken / half-finished
- None.

### Agents
| Runtime | live | _test_prompt.md (mocked) | SmokeAnswer | yes |
| Diagnostician | live | diagnostician.md | DiagnosticResponse | yes |

### Environment variables in use
ENV, DEMO_MODE, AUTH_MODE, DATABASE_URL, ALEMBIC_DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWKS_URL, GEMINI_API_KEY, DEV_JWT_SECRET, CORS_ORIGINS, RECORD_FIXTURES

### Known broken / half-finished
- None.

### Do not touch
- None.

## CHANGELOG — append at top, never edit past entries

### [2026-08-29 15:56] feat(api): Learner Profile endpoints (P1.8)
- Added: `services/api/routers/profile.py`.
- Added: `services/api/services/profile.py` for DB logic.
- Updated: `GET /api/v1/me` now correctly flags `has_learner_profile` by checking for rows in `learner_profiles`.
- Tested: `tests/test_profile.py` validates GET/PATCH and checks that PATCH correctly bumps the `profile_version`.

### [2026-08-29 15:45] feat(api): Diagnostic session endpoints (P1.7)
- Added: `services/api/routers/diagnostic.py`.
- Added: Database logic for creating sessions, recording answers, and finalizing profiles.
- Tested: `tests/test_diagnostic.py` verifies the full lifecycle from session creation to completion.
- Contract: Endpoints return `DiagnosticSession` and `DiagnosticResponse` objects as defined in P1.6.

### [2026-08-29 15:39] feat(agents): The Diagnostician Agent (P1.6)
- Added: `services/agents/diagnostician.py`, `services/agents/prompts/diagnostician.md`.
- Added: `DiagnosticResponse`, `NextQuestion`, `ProfileDraft`, and `AccessibilityOptions` schemas in `schemas.py`.
- Added: `fixtures/demo/diagnostician_default.json` for deterministic offline testing and fallback execution.
- Tested: `tests/test_diagnostician.py` correctly covers the adaptive question logic divergence and tests the offline fallback rule-set behavior (providing 8 distinct questions followed by a drafted ProfileDraft).
- Contract: The prompt has strict anti-VARK instructions and guarantees that at least 3 questions in the diagnostic sequence are measurable micro-problems.
- Next: P1.7 - Diagnostic endpoints.

### [2026-08-29 15:33] feat(agents): The agent runtime (P1.5)
- Added: `services/agents/__init__.py`, `services/agents/schemas.py`, `services/agents/usage.py`, `services/agents/client.py`, `services/agents/base.py`, `services/agents/prompts/.gitkeep`.
- Added: `fixtures/demo/_smoke_default.json` for `DEMO_MODE=true` testing.
- Added: `tests/test_agent_base.py`.
- Changed: Implemented a robust agent execution pipeline (`base.run`) featuring timeout handling (20s flash, 110s pro), simple `{{key}}` string replacement templating, usage statistics tracking, exact 1-retry on validation failure, and a safe fallback factory.
- Changed: Built `client.py` capable of seamlessly routing to `fixtures/demo` when `DEMO_MODE=true` using a deterministic MD5 hash of inputs.
- Contract: Agents run through `base.run()`, schemas live in `schemas.py`.
- Tested: Mocked Gemini SDK responses and simulated validation failures for retries and fallbacks. Verified `DEMO_MODE=true` loads without network requests.
- Broken/left undone: None.
- Next: Phase 1 Task 6 (Generating the diagnostic session via prompt).

### [2026-08-29 15:19] feat(api): GET /me and lazy profile creation
- Added: `services/api/models/user.py` missing from P0.4 and generated Alembic migration `0002_add_users_table`.
- Added: `MeResponse` schema, `get_or_create_user` logic with `ON CONFLICT DO NOTHING`, and `GET /api/v1/me` route.
- Contract: Re-generated OpenAPI schema. Updated `contract/status.md`.
- Tested: Verified DB insertion, idempotency, and 401 unauth scenarios.
- Broken/left undone: `has_learner_profile` hardcoded to `False` as required (Phase 1 Task 4 will wire this).
- Next: P1.4 - Learner Profile schema.

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
