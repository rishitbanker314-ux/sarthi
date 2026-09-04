# Backend_Instructions.md

> **For the Backend Developer and the AI agent building the backend.**
> Prerequisite reading, in order: `Context.md` → `Rules.md` →
> `Project_requirement.md` → this file → `Memory.md` → `Phase.md`.
>
> You own the contract. The frontend cannot move faster than your
> `openapi.yaml`. Ship the contract before you ship the implementation.

---

## 1. Your job in one paragraph

Build a FastAPI service that exposes a small, strictly-typed HTTP API, and
behind it an agent layer that turns a learner's profile, goal and mastery state
into teaching. Every model call returns schema-validated structured output.
Every endpoint is declared in `contract/openapi.yaml` before the frontend
touches it. You are not building a chatbot; you are building five agents with
narrow jobs and one shared state.

---

## 2. Ownership 🔴

**You own:** `services/api/`, `services/agents/`, `migrations/`, `fixtures/`,
`contract/openapi.yaml` (you generate it), `Architecture.md`, `Memory.md`,
`Phase.md`.

**You never edit:** `apps/web/`, `apps/mobile/`, `packages/ui/`,
`packages/api-client/`, `packages/i18n/`, `packages/api-types/`,
`apps/web/FE_MEMORY.md`, `Context.md`, `Rules.md`, `Project_requirement.md`,
**`Backend_Instructions.md` (this file)**, `Frontend_Instructions.md`.

**You may write to** (protocol-gated, see `Context.md` §7.4):
`contract/status.md`, `contract/CHANGELOG.md`.

If the frontend is broken, you report it in `contract/CHANGELOG.md`. You do not
fix it. See `Rules.md` §1.

---

## 3. Stack — locked, do not substitute

| Layer | Choice | Notes |
|---|---|---|
| Language | **Python 3.11+** | Type hints everywhere |
| Framework | **FastAPI** | Auto-generates our OpenAPI spec — this is why we chose it |
| Validation | **Pydantic v2** | Every boundary, every agent output |
| Server | **Uvicorn** | |
| DB | **PostgreSQL 16** | Local via Docker for dev **and the demo**; **Supabase** in the cloud. Same Alembic migrations against both. One engine only (`Rules.md` §3). |
| ORM | **SQLAlchemy 2.0** (async, `asyncpg`) | |
| Migrations | **Alembic** (sync `psycopg`) | Forward-only. Separate `ALEMBIC_DATABASE_URL`. |
| Auth | **Supabase Auth**, verified locally against JWKS (ES256) | 🔴 We never see or store a password. A dev-only HS256 issuer covers offline work — see §3.2. |
| Storage | **Supabase Storage** | Only if S5 (syllabus upload) is reached. ⚠️ Network-dependent — keep it off the offline demo path. |
| LLM | **Google Gemini API** via `google-genai` | Structured output mode, always |
| Embeddings | **Gemini `text-embedding-004`** | Only if **S5** (syllabus upload / RAG) is reached — unphased, Phase-6 slack only |
| Vector store | **`pgvector` extension** | Same Postgres. No Pinecone, no Chroma. |
| Cache / jobs | **Redis** + **`arq`** | **Optional.** In-process `BackgroundTasks` is the default through Phase 4. Add Redis only if jobs must survive a restart. Pre-approved in `Rules.md` §3 either way. |
| Testing | **pytest** + **httpx** | |
| Lint/format | **ruff** + **black** | |
| Local run | **Docker Compose** | Postgres + API (+ Redis only if adopted). Must run offline. |

**Gemini model routing** — different agents need different tiers:

| Agent | Model | Why |
|---|---|---|
| Diagnostician | Flash | Short, cheap, high volume |
| Planner | Pro | Hardest reasoning in the system; runs rarely |
| Tutor | Flash | Latency-critical, streams to the learner |
| Assessor | Flash | Structured, bounded |
| Adaptor | Pro | Decision quality matters more than speed |

Put the model IDs in **one** config module. Never hardcode a model name at a
call site. When a model is deprecated you change one file.

---

## 3.1 Companion documents

Two files expand this one into a step-by-step build:

- **`Backend_Roadmap.md`** — Antigravity setup, accounts and keys, free-vs-paid
  platform choices, the `.agents/` rules and skills to install, per-phase
  verification, Supabase and Gemini references, deployment, troubleshooting.
- **`Antigravity_Prompts.md`** — every prompt, in order, ready to paste.

This file stays the specification. Those two are the procedure.

---

## 3.2 🔴 Authentication — how it actually works

The frontend authenticates directly with Supabase (`supabase-js`) and sends the
resulting access token as `Authorization: Bearer <token>`. This backend
**verifies** that token; it never issues one and never sees a password.

```
frontend ──signUp/signIn──► Supabase Auth ──access token (ES256)──► frontend
frontend ──Bearer token──► FastAPI ──verify against cached JWKS──► sub = user_id
```

- JWKS: `https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json`
- Cache the JWKS in memory. Refresh only on an unknown `kid`, at most once a
  minute. 🔴 Never fetch it per request.
- Require `aud == "authenticated"`, validate `exp`, allow ≤60s clock skew.
- 🔴 `verify_signature=False` must not appear anywhere, ever.

**Two modes, one dependency.** `get_current_user` picks a verifier from
`AUTH_MODE`:

| `AUTH_MODE` | Verifier | Used for |
|---|---|---|
| `supabase` | ES256 against cached JWKS | Cloud deploy and normal dev |
| `local` | HS256 signed with `DEV_JWT_SECRET`, issued by `POST /dev/auth/token` | Offline dev and the offline demo |

🔴 The `local` mode router must be **physically absent** when
`ENV=production` — registered inside `if settings.env != "production":`, not
gated by a flag inside the handler.

---

## 4. 🔴 The three files you must create

These are yours to write and maintain. Create all three **in Phase 0, before
writing feature code.** The AI you are working with reads them at the start of
every session; if they are stale, it will build the wrong thing.

---

### 4.1 `Architecture.md` — the stable picture

Write once at the start of Phase 0. Update only when a structural decision
changes. This is *how the system is built*, not *what has been built*.

**Required sections:**

> Heading numbers below are prefixed `A` so that a "§4" reference in *this*
> document is never confused with a section of `Architecture.md`. Keep the
> prefix.

```markdown
# Architecture.md

## A1. Stack
Table of every technology + pinned version + one line on why.

## A2. Repository layout
Tree of services/api/ and services/agents/ with one line per directory.

## A3. Data model
Every table: columns, types, nullability, foreign keys, indexes.
An ER description in text. Keep this in sync with migrations/ — it is the
only human-readable view of the schema.

## A4. API surface
Every endpoint: method, path, auth required, request model, response model,
error codes, whether it streams. Must match contract/openapi.yaml exactly.

## A5. Agent layer
For each of the five agents:
  - Trigger
  - Inputs (which DB reads)
  - Output Pydantic schema (the actual class)
  - Model tier and why
  - Prompt file path
  - Timeout, retry policy, fallback behaviour
  - Estimated tokens per call

## A6. Async job model
How long-running agent work is dispatched, tracked and polled.
Job kinds, statuses, progress semantics, and the `result` shape per kind.

## A7. Caching strategy
What is cached, keyed by what, invalidated when.

## A8. Auth & security
Token lifetimes, hashing, where the row-level user scoping is enforced,
and how the SSE endpoints authenticate.

## A9. Configuration
Every environment variable, its purpose, and its default.
Never the values themselves.

## A10. Local development
Exact commands to go from clone to running, on a machine with no network.

## A11. Decision log
| Date | Decision | Alternatives considered | Why |
Append-only. This is what you read from when a judge asks "why Postgres?"
```

---

### 4.2 `Memory.md` — what actually exists right now

🔴 **This is the most important file you maintain.** Its job: an AI agent
starting a fresh session with zero context reads `Memory.md` and knows exactly
what exists, what works, and what is half-finished — without reading the code.

**🔴 Update it in the same change as the code. Not at the end of the day.
Not "later". An un-updated `Memory.md` is worse than no `Memory.md`, because
the next session will trust it and build on a lie.**

**Structure:**

```markdown
# Memory.md
> Append-only log. Newest entries at the top of the CHANGELOG section.
> Read STATE first, CHANGELOG for detail.

## STATE — current truth (rewrite this section in place)

### Endpoints
| Method | Path | Status | Tested | Notes |
|---|---|---|---|---|
| GET | /api/v1/me | live | yes | creates the profile row on first call |
| POST | /api/v1/goals | mocked | no | contract only, Prism serves it |
🔴 Status vocabulary is **exactly** `planned | mocked | live | done` — the same
four words used in `contract/status.md` and read by the frontend
(`Frontend_Instructions.md` §4.4). Never invent a fifth (no "stub", no "wip").
`mocked` = declared in the contract, not implemented.
`live` = implemented and reachable.
`done` = live AND tested AND the frontend has verified against the real endpoint.

### Database
Tables that exist, latest applied migration ID.

### Agents
| Agent | Status | Prompt file | Schema class | Tested |

### Environment variables in use
Names only.

### Known broken / half-finished
Bullet list. Be brutally honest. This section existing is the point of the file.

### Do not touch
Things that work and are fragile, with a one-line reason.

## CHANGELOG — append at top, never edit past entries

### [2026-09-01 14:20] feat(planner): plan generation endpoint
- Added: services/agents/planner.py, PlanDraft schema, POST /goals/{id}/plan
- Changed: jobs table gained progress_message column (migration 0007)
- Contract: openapi.yaml regenerated, CHANGELOG entry #12, acked by FE
- Tested: unit schema test passes; not yet load-tested
- Broken/left undone: rationale is generic, doesn't cite mastery yet
- Next: wire mastery_states into planner context
```

**Entry rules:**

- One entry per meaningful change. Not per file, not per day.
- Always include **Broken/left undone** — even if it says "nothing".
- Always include **Next** — the next session starts there.
- Never edit or delete a past entry. Add a new one that corrects it.
- If you touched the contract, say so, with the `CHANGELOG.md` entry number.

**The test:** hand `Memory.md` to someone who has never seen the repo. If they
cannot say what works and what does not in two minutes, it has failed.

---

### 4.3 `Phase.md` — what to build next

Turns the roadmap into an ordered queue with hard exit criteria. Phase numbers
**and names must** match `Project_requirement.md` §7 and
`Frontend_Instructions.md` §13 exactly. 🔴 All seven phases (0–6) must appear in
`Phase.md` from the day you create it, even if later ones are one-line stubs —
otherwise a fresh agent cannot see where the project is going.

```markdown
# Phase.md
> Current phase: **2 — Goal → Plan**
> 🔴 Do not build anything from a later phase. If a task isn't listed here,
> it is not authorised. See Rules.md §3.

## Phase 0 — Contract & skeleton  ✅ COMPLETE (2026-08-30)
### Exit criteria
- [x] FastAPI boots, /health returns 200
- [x] Docker Compose brings up API + Postgres offline
- [x] Alembic initialised, migration 0001 applied
- [x] contract/openapi.yaml v0.1 generated and committed
- [x] Frontend confirmed Prism mock works against it
- [x] Architecture.md, Memory.md, Phase.md created

## Phase 1 — Identity & diagnostic  ✅ COMPLETE
...

## Phase 2 — Goal → Plan  ⬅ CURRENT
### Exit criteria
- [ ] POST /goals parses free text into normalized_topic/target_level/deadline
- [ ] Planner agent returns schema-valid PlanDraft in ≤90s p95
- [ ] Plan/Module/Lesson persisted and versioned
- [ ] Rationale references the learner's actual profile fields
- [ ] Job polling reports real progress, not a fake bar
- [ ] All Phase-2 endpoints marked live in contract/status.md
- [ ] Memory.md STATE updated

### Task queue (ordered — take the top unchecked item)
1. [ ] Pydantic models: Goal, PlanDraft, ModuleDraft, LessonDraft
2. [ ] Migration 0005: goals, plans, modules, lessons
3. [ ] Goal parser agent + prompt
4. [ ] POST /api/v1/goals
5. [ ] Planner prompt + structured output schema
6. [ ] Job dispatch for plan generation
7. [ ] GET /api/v1/plans/{id}
8. [ ] Fixture responses for DEMO_MODE
9. [ ] Regenerate openapi.yaml, log contract change, notify FE

### Blocked
- (nothing) — or: item, who/what unblocks it, since when

## Phase 3 — Lesson & checkpoint  ⬜ NOT STARTED
### Exit criteria
...

## Phase 4 — Adaptation loop  ⬜ NOT STARTED
🔴 This phase is the project. Never cut it. (Project_requirement.md §7)

## Phase 5 — Mobile companion  ⬜ NOT STARTED

## Phase 6 — Polish & demo hardening  ⬜ NOT STARTED
```

**Rules:**

- Exactly one phase is `CURRENT`.
- Tasks are ordered. Take the top unchecked one.
- 🔴 A phase is not complete until **every** exit criterion is ticked and
  `Memory.md` STATE reflects it. No partial phase completion.
- If you discover work that belongs to a later phase, add it to that phase's
  queue. Do not do it now.

---

## 5. Data model

Create these across migrations as phases require. `snake_case` everywhere.
Every table has `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`,
`created_at TIMESTAMPTZ NOT NULL DEFAULT now()`.

```sql
users(id, email, display_name, locale)
      -- 🔴 NO password_hash. Supabase Auth owns credentials; we never see one.
      -- id is the Supabase auth user id (the JWT's `sub` claim).
      -- On Supabase: id REFERENCES auth.users(id) ON DELETE CASCADE.
      --   On local Postgres there is no `auth` schema, so migration 0001 must
      --   add that FK conditionally and run cleanly on BOTH databases.
      -- The row is created lazily by GET /me on first authenticated request.
      -- locale = UI chrome language. Distinct from learner_profiles.language,
      --          which is the EXPLANATION language. Both are user-settable.

learner_profiles(user_id FK, profile_version INT,
                 prior_knowledge JSONB,      -- {concept_id: none|shaky|solid}
                 pace, representation_pref, scaffolding_pref, depth_pref,
                 motivation, session_minutes INT, language,
                 accessibility JSONB,        -- validated by an Accessibility
                                             -- Pydantic model, NOT free JSON.
                                             -- Keys fixed in Context.md §5.
                 updated_at)
                 -- UNIQUE(user_id, profile_version); latest is authoritative
                 -- 🔴 The column is `profile_version` and the API field is
                 --    `profile_version`. Never just `version` — it is the
                 --    lesson-content cache key and must be unambiguous.

diagnostic_sessions(user_id FK, status, transcript JSONB,
                    derived_profile JSONB, completed_at)

concepts(name, description, domain, prerequisite_ids UUID[])

goals(user_id FK, raw_input TEXT, normalized_topic, target_level,
      deadline DATE NULL, status)

plans(goal_id FK, version INT, title, rationale TEXT,
      profile_version INT, status)          -- UNIQUE(goal_id, version)

modules(plan_id FK, order_index INT, title, objective, rationale,
        est_minutes INT, status)

lessons(module_id FK, order_index INT, title, objective,
        concept_ids UUID[], est_minutes INT, status)

lesson_contents(lesson_id FK, profile_version INT, blocks JSONB,
                token_cost INT, generated_at)
                -- UNIQUE(lesson_id, profile_version)  ← the cache key

checkpoints(lesson_id FK, user_id FK, items JSONB)

checkpoint_attempts(checkpoint_id FK, responses JSONB, score NUMERIC,
                    mastery_deltas JSONB, feedback JSONB, submitted_at)

mastery_states(user_id FK, concept_id FK, score NUMERIC, confidence NUMERIC,
               attempts INT, last_seen_at)  -- UNIQUE(user_id, concept_id)

tutor_threads(user_id FK, lesson_id FK)
tutor_messages(thread_id FK, role, content TEXT, blocks JSONB)

signals(user_id FK, lesson_id FK NULL, block_id UUID NULL, type, value JSONB)
        -- block_id is REQUIRED for time_on_block, hint_requested,
        -- inline_check_failed and skip (the block skipped FROM).
        -- NULL for lesson-level signals: checkpoint_score, confusion_flag,
        -- retry, session_abandon, revisit.
        -- Types enumerated in Context.md §5.

adaptation_events(user_id FK, plan_id FK, trigger, action,
                  reason TEXT, timeline_impact TEXT,
                  before JSONB, after JSONB, accepted BOOL NULL)
        -- 🔴 field is `action`, matching AdaptationDecision.action in §9.
        -- 🔴 timeline_impact is REQUIRED and shown to the learner
        --    (Project_requirement.md §4 US-06). e.g. "adds ~25 min;
        --    still on track for your 12 Oct deadline".
        -- changes[] from AdaptationDecision serialises into before/after.

jobs(user_id FK, kind, status, progress INT, progress_message,
     result JSONB, error JSONB, updated_at)
```

🔴 **Every query filters by the authenticated `user_id`.** Write a dependency
that injects the current user and make it impossible to query without one.

---

## 6. API surface — build in this order

All paths prefixed `/api/v1` **except rows 1, 4b and 33**, which sit outside the
versioned router at the bare root (`/health`, `/dev/auth/token`,
`/health/usage`) — the frontend's `NEXT_PUBLIC_API_BASE` includes the `/api/v1`
prefix, so health checks and dev-only routes must not be inside it.
🔴 = on the demo path, must never 500.

| # | Method | Path | Phase | Notes |
|---|---|---|---|---|
| 1 | GET | `/health` | 0 | Unprefixed. No auth. Returns version + db status. |
| ~~2~~ | ~~POST~~ | ~~`/auth/register`~~ | — | ❌ **Removed 2026-08-29.** Supabase Auth owns it. See §3.2. |
| ~~3~~ | ~~POST~~ | ~~`/auth/login`~~ | — | ❌ **Removed.** `supabase.auth.signInWithPassword()` on the client. |
| ~~4~~ | ~~POST~~ | ~~`/auth/refresh`~~ | — | ❌ **Removed.** `supabase-js` refreshes automatically. |
| 4b | POST | `/dev/auth/token` | 1 | 🔴 **Development only.** Issues an HS256 token so the stack works offline. Must be *absent* — not merely disabled — when `ENV=production`. |
| 5 | GET | `/me` | 1 | 🔴 Creates the learner's profile row on first call (`INSERT … ON CONFLICT DO NOTHING`) |
| 6 | POST | `/diagnostic/sessions` | 1 | 🔴 Starts, returns first question |
| 7 | GET | `/diagnostic/sessions/{id}` | 1 | Resume |
| 8 | POST | `/diagnostic/sessions/{id}/answer` | 1 | 🔴 Returns next question or `complete: true` |
| 9 | POST | `/diagnostic/sessions/{id}/complete` | 1 | 🔴 Returns `LearnerProfile` |
| 10 | GET | `/profile/learner` | 1 | 🔴 |
| 11 | PATCH | `/profile/learner` | 1 | Bumps `profile_version` |
| 12 | POST | `/goals` | 2 | 🔴 Body `{raw_input}`; returns parsed interpretation |
| 13 | GET | `/goals` | 2 | |
| 13b | PATCH | `/goals/{id}` | 2 | 🔴 Learner corrects `normalized_topic` / `target_level` / `deadline` without retyping (US-02) |
| 14 | POST | `/goals/{id}/plan` | 2 | 🔴 Returns `202` + `{job_id}` |
| 15 | GET | `/jobs/{id}` | 2 | 🔴 Poll. `queued\|running\|succeeded\|failed` |
| 16 | GET | `/plans/{id}` | 2 | 🔴 Plan + modules + lessons + rationale |
| 17 | GET | `/lessons/{id}` | 3 | Metadata only |
| 18 | POST | `/lessons/{id}/start` | 3 | 🔴 Marks in-progress, returns thread id |
| 19 | GET | `/lessons/{id}/content` | 3 | 🔴 **SSE stream** of `ContentBlock`s |
| 19b | POST | `/lessons/{id}/reexplain` | 3 | 🔴 **SSE stream.** Powers the "I'm lost" button (M9). Body `{block_id, reason?}`. Re-teaches that block a *different* way — different representation, not a paraphrase. 🔴 Writes the `confusion_flag` signal **server-side**; the client must not also POST it (`Context.md` §5). |
| 20 | POST | `/lessons/{id}/complete` | 3 | |
| 21 | POST | `/tutor/messages` | 3 | 🔴 **SSE stream** |
| 22 | GET | `/tutor/threads/{lesson_id}` | 3 | History |
| 23 | POST | `/lessons/{id}/checkpoint` | 3 | 🔴 Generates items |
| 24 | POST | `/checkpoints/{id}/submit` | 3 | 🔴 Score + feedback + mastery deltas |
| 25 | GET | `/progress/mastery` | 3 | 🔴 |
| 26 | GET | `/progress/summary` | 3 | 🔴 Dashboard payload |
| 27 | POST | `/signals` | 3 | Batch. Returns `202`, fire-and-forget |
| 28 | POST | `/plans/{id}/replan` | 4 | 🔴 Returns `202` + `{job_id}` |
| 29 | GET | `/adaptations` | 4 | 🔴 Recent `AdaptationEvent`s with reasons |
| 30 | POST | `/adaptations/{id}/respond` | 4 | 🔴 `{accepted: bool}` |
| 31 | GET | `/me/export` | 4 | Data export. Phase 4 so the settings screen can ship whole. |
| 32 | DELETE | `/me` | 4 | Account deletion. Same reason. |
| 33 | GET | `/health/usage` | 2 | Unprefixed. **Dev only** — disabled when `ENV=production`. Token spend per agent. You need this for the pitch numbers. *(Listed last for readability; build it in Phase 2 — it is the only row out of phase order.)* |

**Every** HTTP response uses the error envelope from `Rules.md` §2. The SSE
`error` event is the documented exception — see §8.

---

## 7. 🔴 The ContentBlock contract

This is the single most important shared type in the project. The Tutor emits
it; the web and mobile renderers consume it. Publish it as
`contract/blocks.schema.json` in **Phase 0**, before the Tutor exists, so the
frontend can build renderers in parallel.

```jsonc
// Every block has these:
{ "id": "blk_<uuid>", "type": "<one of below>", "concept_id": "<uuid|null>" }
```

| `type` | Extra fields | Rendered as |
|---|---|---|
| `heading` | `text`, `level` (1–3) | Section heading |
| `text` | `text` (markdown subset: bold, italic, inline code, links) | Paragraph |
| `list` | `ordered` (bool), `items` (string[]) | List |
| `code` | `language`, `code`, `caption?` | Syntax-highlighted block |
| `math` | `latex`, `display` (bool) | KaTeX |
| `callout` | `variant` (`info\|tip\|warning\|misconception\|ai_notice`), `title`, `text` | Coloured box. `ai_notice` carries the AI-generated disclaimer required by `Rules.md` §6 — emit exactly one per lesson. |
| `example` | `title`, `setup`, `steps` (string[]), `result` | Worked example, steps revealable |
| `analogy` | `text`, `maps_to` | Styled analogy card |
| `step` | `index`, `text`, `reveal` (bool) | Faded-scaffolding step |
| `quiz_inline` | `question`, `options` (string[]), `answer_index`, `explanation` | Inline check, no scoring |
| `image_prompt` | `alt`, `description` | Placeholder card (v1 does not generate images) |
| `divider` | — | Rule |

🔴 **Adding a type or a `callout` variant requires the contract-change
protocol** — stated in `Rules.md` §2, defined step-by-step in `Context.md` §7.4.
🔴 **The frontend renders unknown types as a visible placeholder.** Design for
that — it means a new type degrades instead of crashing.

---

## 8. 🔴 SSE contract

Frozen. Defined in `contract/events.md`. Used by endpoints 19, 19b and 21.

```
event: token
data: {"text": "partial text"}

event: block
data: {"id":"blk_9f2c4a1e...","type":"example","concept_id":"c8b1...","title":"...", ...}

event: tool
data: {"name":"retrieve_concept","status":"running"}

event: done
data: {"message_id":"msg_3d7f...","block_count":7,"usage":{"input":1200,"output":800}}

event: error
data: {"code":"MODEL_TIMEOUT","message":"...","retryable":true,"details":{}}
```

Rules:

- 🔴 **The `error` event's `data` is the INNER error object** — `code`,
  `message`, `retryable`, `details` at the top level, **without** the
  `{"error": {...}}` wrapper used by HTTP responses. The event name already
  says it is an error. This exception is recorded in `Rules.md` §2 and mirrored
  in `Frontend_Instructions.md` §8. Do not "fix" it in either direction.
- A stream **always** terminates with exactly one `done` **or** one `error`.
  Never both. Never neither. A stream that just stops is a hung UI.
- Send a comment heartbeat (`: ping\n\n`) every 15s to defeat proxy timeouts.
- `block` carries a **complete, renderable** block, with real `id` and
  `concept_id`. Never a partial one.
- `token` is for the tutor chat's prose only. Lesson content uses `block`.

### 8.1 🔴 SSE authentication

`EventSource` cannot send an `Authorization` header, so **all three streaming
endpoints are consumed with `fetch` + `ReadableStream`, never `EventSource`.**
That keeps the bearer token in the normal header, inside
`packages/api-client`, with no token in a query string and no second auth path
to secure. Endpoint 19 is therefore an ordinary authenticated `GET` that
returns `text/event-stream`; the frontend reads it with a streaming fetch
rather than `EventSource`. Endpoints 19b and 21 are authenticated `POST`s that
return `text/event-stream` the same way. Mirrored in
`Frontend_Instructions.md` §8 and §12.

---

## 9. Agent layer

```
services/agents/
├── base.py          # run(), timeout, retry, schema validation, token accounting
├── client.py        # Gemini client, model routing, DEMO_MODE fixture switch
├── schemas.py       # every agent's Pydantic output model
├── diagnostician.py
├── planner.py
├── tutor.py
├── assessor.py
├── adaptor.py
└── prompts/
    ├── diagnostician.md
    ├── planner.md
    ├── tutor.md
    ├── assessor.md
    └── adaptor.md
```

🔴 **Prompts live in `.md` files, never inline in Python.** They get iterated on
constantly; they must be diffable and reviewable on their own.

🔴 **Every agent call goes through `base.run()`**, which:
1. Renders the prompt with a validated context object
2. Calls Gemini with `response_schema` set (structured output mode)
3. Validates into the Pydantic model
4. On failure: retry once with the validation error appended
5. On second failure: return the declared fallback and log at `ERROR`
6. Records input/output tokens against the agent name
7. Enforces a timeout: **Flash 20s, Pro 110s** — the Pro timeout must sit above
   the 90s p95 target, and below the 150s job deadline in §10, so that a slow
   model call fails as a model error rather than as a job timeout

### Agent contracts

| Agent | In | Out (Pydantic) | Fallback |
|---|---|---|---|
| **Diagnostician** | prior answers, question bank | `NextQuestion` or `ProfileDraft` | Fixed question bank, rule-based profile |
| **Planner** | profile, goal, mastery, concept graph | `PlanDraft{title, rationale, modules[{title, objective, rationale, lessons[...]}]}` | Template plan for the normalized topic |
| **Tutor** | lesson, profile, mastery, thread | `ContentBlock[]` streamed | Cached content for a neighbouring profile version |
| **Assessor** | lesson, concepts, profile | `Checkpoint{items[]}` / `ScoreResult{per_item_feedback, mastery_deltas}` | Fixture checkpoint for that lesson |
| **Adaptor** | signals, mastery, plan | `AdaptationDecision{trigger, action, reason, timeline_impact, changes[]}` | No-op with logged reason |

🔴 **`reason` and `timeline_impact` are both required, non-empty,
human-readable strings on every `AdaptationDecision`.** They are shown directly
to the learner and to the judges (`Project_requirement.md` §4 US-06,
`Frontend_Instructions.md` §6 screen 12). Reject any model output where either
is generic. Test for this.

`AdaptationDecision` maps onto `adaptation_events` (§5) one-to-one:
`trigger→trigger`, `action→action`, `reason→reason`,
`timeline_impact→timeline_impact`, `changes[]→before`/`after` JSONB.

### Adaptor trigger thresholds

Put these in config, not in the prompt — they must be tunable during rehearsal.
🔴 These five are the **only** triggers in v1. Every signal not named in a
condition below is collected but unwired — see `Context.md` §5, whose "Wired?"
column must match this table exactly.

| Trigger | Condition | Action |
|---|---|---|
| `struggling` | checkpoint score < 0.5, or 2 consecutive < 0.7 | Insert prerequisite lesson, slow pace |
| `stuck` | ≥2 `confusion_flag` in one lesson | Re-explain differently; flag concept |
| `racing` | 2 consecutive `checkpoint_score` > 0.9 **and** lesson elapsed < 60% of `est_minutes` (elapsed = sum of that lesson's `time_on_block` signals) | Compress or skip forward |
| `stalled` | no `signals` row for this learner in ≥3 days | Shorten next lesson, re-anchor to goal. ⚠️ Needs a scheduler — **evaluate lazily on next login**, not on a cron, unless Redis + `arq` is adopted. |
| `decaying` | mastery on a completed concept ages past its interval | Queue spaced review. ⚠️ **Depends on S4 (spaced repetition), which is unphased.** Not wired in v1 — implement only if S4 ships. |

---

## 10. Async jobs — get this right in Phase 2

Plan generation takes 20–90 seconds. Never block an HTTP request on it.

1. `POST /goals/{id}/plan` creates a `jobs` row, dispatches the work, returns
   `202 {"job_id": "..."}` immediately.
2. The worker updates `progress` (0–100) and `progress_message` at real
   milestones: `"Reading your profile" → "Mapping prerequisites" →
   "Sequencing modules" → "Writing lesson objectives"`.
3. `GET /jobs/{id}` returns status, progress, message, and `result` when done.
4. 🔴 **Progress must be real.** A fake animated bar is a lie the frontend will
   have to keep, and judges notice when it hits 90% and sits there.
5. 🔴 **Every job has a hard deadline of 150s.** On exceeding it: `failed` with
   `code: "JOB_DEADLINE_EXCEEDED"`, `retryable: true`. Never leave a job
   `running` forever.

   The ladder, and it must stay in this order:
   **90s p95 target < 110s Pro model timeout < 150s job deadline < 180s frontend poll cap.**
   Each layer must outlive the one inside it, or a slow-but-successful call
   gets killed by the layer above and reported as the wrong kind of failure.
6. 🔴 **`result` is typed per job `kind` and declared in `openapi.yaml`** — not
   an opaque blob. The frontend routes on it.

   | `kind` | `result` shape |
   |---|---|
   | `plan_generation` | `{"plan_id": "<uuid>"}` |
   | `replan` | `{"plan_id": "<uuid>", "adaptation_event_id": "<uuid>"}` |

---

## 11. Caching and cost

- 🔴 Lesson content caches on `(lesson_id, profile_version)`. Same learner, same
  lesson, same profile → zero model calls. This is the difference between a
  demo that costs ₹40 and one that costs ₹4000.
- Cache the concept graph per `normalized_topic`.
- 🔴 Rate-limit every LLM endpoint per user (suggested: 30 model calls/hour).
- Log token usage per agent per request. Expose it via `GET /health/usage`
  (row 33 in §6, dev only). You will need cost-per-learner-hour for the pitch
  (`Project_requirement.md` §9) and you cannot reconstruct it later.
- 🔴 `DEMO_MODE=true` serves everything from `fixtures/demo/` and makes **zero**
  network calls. Build this in Phase 2, not Phase 6 — it is also how you write
  fast tests.

---

## 12. Working with your AI — the loop

Run this loop for every task. It is what keeps a long AI-built codebase coherent.

```
1. READ    Memory.md STATE + Phase.md current phase.
2. PICK    The top unchecked task in the Phase.md queue. Only that one.
3. STATE   Tell the AI, explicitly:
             - the task, verbatim from Phase.md
             - the files it may touch
             - the schema/contract it must honour
             - "do not modify anything else"
4. BUILD   Small diff. One concern.
5. RUN     Actually execute it. pytest + a real curl against the endpoint.
           Never accept "this should work".
6. RECORD  Append a Memory.md CHANGELOG entry AND update the STATE section.
7. SYNC    If the contract changed: regenerate openapi.yaml, log it in
           contract/CHANGELOG.md, tell the frontend dev in words.
8. TICK    Check the box in Phase.md.
```

**Session-opening prompt to paste when your AI has no context:**

```
Read Context.md, Rules.md, Project_requirement.md, Backend_Instructions.md,
Architecture.md, Memory.md and Phase.md before doing anything.

Then tell me, in under 150 words:
  (a) which phase we're in,
  (b) the top unchecked task,
  (c) which files you'll touch,
  (d) anything in Memory.md marked broken that affects this task.

Do not write code until I confirm.
```

**Red flags — stop the AI immediately if it:**

- Touches a file outside `services/`, `migrations/`, `fixtures/`, `contract/`,
  or the three markdown files it owns (`Architecture.md`, `Memory.md`, `Phase.md`)
- Invents an endpoint not in the table in §6
- Adds a dependency you did not approve
- Rewrites something that already worked
- Says "I've also improved..." — that is scope creep with a smile
- Produces a diff you cannot read in one screen
- Reports success without having run anything

---

## 13. Definition of done — per endpoint

An endpoint is `done` (not `live`, not `mocked`) only when **all** of these hold:

- [ ] Request and response are Pydantic models — no raw dicts
- [ ] Declared in the regenerated `contract/openapi.yaml`
- [ ] Auth enforced; query scoped to the authenticated user
- [ ] Errors use the standard envelope with a specific `code`
- [ ] One happy-path test and one auth-failure test pass
- [ ] Manually hit with `curl` or `/docs` and the output eyeballed
- [ ] `DEMO_MODE` fixture exists if it is on the demo path
- [ ] `contract/status.md` updated to `live`
- [ ] `Memory.md` STATE table updated
- [ ] Frontend dev told, in words, that it is ready
- [ ] **After** the frontend verifies against the real endpoint, either dev
      flips `contract/status.md` to `done`. Only then is it `done`.

---

## 14. First 90 minutes — do exactly this

> Follow `Antigravity_Prompts.md` P0.1–P0.9 for the actual prompts. The list
> below is the same sequence, as a checklist.

1. `mkdir -p services/api services/agents contract fixtures/demo migrations .agents`
2. FastAPI app with an unprefixed `/health`. Run it. See 200.
3. Docker Compose: `api` + `postgres`. `docker compose up` works offline.
4. Alembic init, migration 0001: `users` (with the conditional `auth.users` FK).
5. Generate `contract/openapi.yaml` from the running app. Commit it.
6. Create `contract/blocks.schema.json` from §7 above. Commit it.
7. Create `contract/events.md` from §8 above. Commit it.
8. Create `contract/status.md` and `contract/CHANGELOG.md`.
9. **Tell the frontend dev the contract is live.** They start immediately.
10. Write `Architecture.md`, `Memory.md`, `Phase.md`.
11. Only now start Phase 1.

🔴 Steps 5–9 come before any feature code. Every hour the contract does not
exist is an hour the frontend developer cannot work.

---

*Last updated: 2026-08-26 · Owner: Disha (Team Lead) · Backend Dev may propose changes via `contract/CHANGELOG.md`.*
