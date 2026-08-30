# API Endpoints Status

| Method | Path | Status |
|---|---|---|
| GET | /health | live |
| GET | /api/v1/me | live |
| POST | /diagnostic/sessions | mocked |
| GET | /diagnostic/sessions/{id} | mocked |
| POST | /diagnostic/sessions/{id}/answer | mocked |
| POST | /diagnostic/sessions/{id}/complete | mocked |
| GET | /profile/learner | mocked |
| PATCH | /profile/learner | mocked |
| POST | /dev/auth/token | live |
| GET | /api/v1/goals | live |
| GET | /api/v1/goals/{id} | live |
| POST | /api/v1/goals | live |
| GET | /api/v1/plans | live |
| GET | /api/v1/plans/{id} | live |
| POST | /api/v1/plans/{id}/replan | live |
| GET | /api/v1/lessons/{id} | live |
| GET | /api/v1/checkpoints/{id} | live |
| POST | /api/v1/checkpoints/{id}/attempt | live |
| GET | /api/v1/adaptations | live |
| POST | /api/v1/adaptations/{id}/respond | live |
