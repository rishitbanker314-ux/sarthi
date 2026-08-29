# Phase.md
> Current phase: **1 — Identity & diagnostic**
> 🔴 Do not build anything from a later phase. If a task isn't listed here,
> it is not authorised. See Rules.md §3.

## Phase 0 — Contract & skeleton  ✅ COMPLETE (2026-08-29)
### Exit criteria
- [x] FastAPI boots, /health returns 200
- [x] Docker Compose brings up API + Postgres offline
- [x] Alembic initialised, migration 0001 applied
- [x] contract/openapi.yaml v0.1 generated and committed
- [x] Frontend confirmed Prism mock works against it
- [x] Architecture.md, Memory.md, Phase.md created

## Phase 1 — Identity & diagnostic  ⬅ CURRENT
### Exit criteria
- [ ] Auth works end-to-end; diagnostic produces a real `LearnerProfile`

### Task queue (ordered — take the top unchecked item)
1. [ ] Pydantic models for LearnerProfile, DiagnosticSession, NextQuestion
2. [ ] Migration 0002: learner_profiles, diagnostic_sessions
3. [ ] Diagnostician agent + prompt
4. [ ] POST /dev/auth/token (HS256 local token generator)
5. [ ] GET /api/v1/me
6. [ ] POST /api/v1/diagnostic/sessions
7. [ ] GET /api/v1/diagnostic/sessions/{id}
8. [ ] POST /api/v1/diagnostic/sessions/{id}/answer
9. [ ] POST /api/v1/diagnostic/sessions/{id}/complete
10. [ ] GET /api/v1/profile/learner
11. [ ] PATCH /api/v1/profile/learner
12. [ ] Fixture responses for DEMO_MODE
13. [ ] Regenerate openapi.yaml, log contract change, notify FE

### Blocked
- (nothing)

## Phase 2 — Goal → Plan  ⬜ NOT STARTED
### Exit criteria
- [ ] A typed goal produces a real plan with a real rationale, live on both apps

## Phase 3 — Lesson & checkpoint  ⬜ NOT STARTED
### Exit criteria
- [ ] A lesson is generated, streamed, rendered and assessed; mastery moves

## Phase 4 — Adaptation loop  ⬜ NOT STARTED
🔴 This phase is the project. Never cut it. (Project_requirement.md §7)
### Exit criteria
- [ ] Failing a checkpoint visibly rewrites the plan with a readable reason

## Phase 5 — Mobile companion  ⬜ NOT STARTED
### Exit criteria
- [ ] Login, continue, lesson, chat, progress on device

## Phase 6 — Polish & demo hardening  ⬜ NOT STARTED
### Exit criteria
- [ ] Demo script rehearsed end-to-end three times without incident
