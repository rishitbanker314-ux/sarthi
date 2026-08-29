# Contract Status

## v0.2 — Phase 1 Complete (2026-08-29)

### New Endpoints (added in Phase 1)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/dev/auth/token` | Dev-only JWT token generator (HS256) |
| GET | `/api/v1/me` | Current user summary + profile metadata |
| POST | `/api/v1/diagnostic/sessions` | Start a new diagnostic session |
| GET | `/api/v1/diagnostic/sessions/{id}` | Get session state |
| POST | `/api/v1/diagnostic/sessions/{id}/answer` | Submit an answer, get next question |
| POST | `/api/v1/diagnostic/sessions/{id}/complete` | Complete session, generate LearnerProfile |
| GET | `/api/v1/profile/learner` | Get current learner profile |
| PATCH | `/api/v1/profile/learner` | Update learner profile (immutable versioning) |

### Existing Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

### Breaking Changes
- None (all endpoints are new)

### Notes
- `openapi.yaml` and `openapi.json` regenerated from live server
- Frontend can update Prism mock from `contract/openapi.json`

---

## v0.1 — Phase 0 Skeleton (2026-08-29)
- Initial contract with `/health` endpoint only
