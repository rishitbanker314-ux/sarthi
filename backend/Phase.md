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

## Phase 1 — Identity & diagnostic  ✅ COMPLETE (2026-08-29)
### Exit criteria
- [x] Auth works end-to-end; diagnostic produces a real `LearnerProfile`

### Task queue (ordered — take the top unchecked item)
1. [x] Pydantic models for LearnerProfile, DiagnosticSession, NextQuestion
2. [x] Migration 0002: learner_profiles, diagnostic_sessions
3. [x] Diagnostician agent + prompt
4. [x] POST /dev/auth/token (HS256 local token generator)
5. [x] GET /api/v1/me
6. [x] POST /api/v1/diagnostic/sessions
7. [x] GET /api/v1/diagnostic/sessions/{id}
8. [x] POST /api/v1/diagnostic/sessions/{id}/answer
9. [x] POST /api/v1/diagnostic/sessions/{id}/complete
10. [x] GET /api/v1/profile/learner
11. [x] PATCH /api/v1/profile/learner
12. [x] Fixture responses for DEMO_MODE
13. [x] Regenerate openapi.yaml, log contract change, notify FE

### Blocked
- (nothing)

## Phase 2 — Goal → Plan  ✅ COMPLETE (2026-08-29)
### Exit criteria
- [x] POST /goals parses free text into normalized_topic/target_level/deadline
- [x] Planner agent returns schema-valid PlanDraft in ≤90s p95
- [x] Plan/Module/Lesson persisted and versioned
- [x] Rationale references the learner's actual profile fields
- [x] Job polling reports real progress, not a fake bar
- [x] All Phase-2 endpoints marked live in contract/status.md
- [x] Memory.md STATE updated

### Task queue (ordered — take the top unchecked item)
1. [x] Pydantic models: Goal, PlanDraft, ModuleDraft, LessonDraft
2. [x] Migration 0003: goals, plans, modules, lessons
3. [x] Goal parser agent + prompt
4. [x] POST /api/v1/goals (and GET, PATCH)
5. [x] Planner prompt + structured output schema
6. [x] Job dispatch for plan generation
7. [x] GET /api/v1/plans/{id}
8. [x] Fixture responses for DEMO_MODE
9. [x] Regenerate openapi.yaml, log contract change, notify FE

### Blocked
- (nothing)

## Phase 3 — Lesson & checkpoint  ✅ COMPLETE (2026-08-30)
### Exit criteria
- [x] A lesson is generated, streamed, rendered and assessed; mastery moves

### Task queue (ordered)
1. [x] Migration 0004: lesson_contents, checkpoints, checkpoint_attempts, mastery_states, tutor_threads, tutor_messages, signals
2. [x] SSE infrastructure (`sse-streaming` skill)
3. [x] Tutor agent and prompt (`new-agent` skill)
4. [x] Lesson content streaming endpoints (GET metadata, POST start, GET content, POST complete)
5. [x] Reexplain endpoint (POST /reexplain)
6. [x] Tutor chat endpoints (POST /tutor/messages, GET /tutor/threads/{id})
7. [x] Assessor agent (generate checkpoint, score checkpoint) and endpoints
8. [x] Signals and progress endpoints (GET /mastery, GET /summary, POST /signals)
9. [x] Personalisation test + fixtures for DEMO_MODE

## Phase 4 — Adaptation loop  ✅ COMPLETE (2026-08-30)
🔴 This phase is the project. Never cut it. (Project_requirement.md §7)
### Exit criteria
- [x] Failing a checkpoint visibly rewrites the plan with a readable reason

## Phase 5 — Mobile companion  ✅ COMPLETE
### Exit criteria
- [x] Login, continue, lesson, chat, progress on device

## Phase 6 — Polish & demo hardening  ✅ COMPLETE
### Exit criteria
- [x] Demo script rehearsed end-to-end three times without incident
