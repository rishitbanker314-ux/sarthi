# Context.md

> **Read this first.** Every human on the team and every AI agent working on this
> repository must read this file before writing a single line of code.
> If something you are about to do contradicts this file, stop and ask the Team Lead.

---

## 0. Document set

| File | Owner | Purpose |
|---|---|---|
| `Context.md` | Team Lead | **This file.** Vision, glossary, how the two devs stay in sync. |
| `Rules.md` | Team Lead | Hard boundaries for AI agents. Non-negotiable. |
| `Project_requirement.md` | Team Lead | What to build, for whom, with what priority. |
| `Frontend_Instructions.md` | Team Lead | Frontend scope, screens, contracts, workflow. |
| `Backend_Instructions.md` | Team Lead | Backend scope, agents, data, contracts, workflow. |
| `contract/openapi.yaml` | Backend Dev (generated) | The single source of truth for the API. Frontend reads, never edits. |
| `contract/status.md`, `CHANGELOG.md`, `blocks.schema.json`, `events.md` | **Joint** | Protocol-gated — see §7.4. |
| `Architecture.md` | Backend Dev | *Created by Backend Dev.* Stack + system design. |
| `Memory.md` | Backend Dev | *Created by Backend Dev.* Running log of what exists. |
| `Phase.md` | Backend Dev | *Created by Backend Dev.* What to build next. **Both** devs read it for the current phase. |
| `apps/web/FE_MEMORY.md` | Frontend Dev | *Created by Frontend Dev.* The frontend's equivalent of `Memory.md`. |

Reading order for a fresh AI agent:
`Context.md` → `Rules.md` → `Project_requirement.md` → your own instruction file
→ your own memory file (`Memory.md` backend / `apps/web/FE_MEMORY.md` frontend)
→ `Phase.md`.

---

## 1. Identity

| Field | Value |
|---|---|
| Working project name | **Sarathi** — *"the one who steers"* |
| Tagline | *The mentor that learns how you learn.* |
| Event | Smart India Hackathon 2026, **Software** edition |
| Problem Statement ID | **SIH26205** |
| Category | Student Innovation (AICTE) |
| Theme | Smart Education |
| Deliverable | Adaptive AI-mentor **web app** (primary) + **mobile companion app** |

> **Renaming:** the project name appears in exactly one place per repo — the
> `APP_NAME` constant. Change it there, nowhere else. Do not hardcode "Sarathi"
> in copy, page titles, or API responses.

> **PS number check:** the public SIH 2026 catalogue lists **SIH26205** as
> AICTE / Student Innovation / *Smart Education* (Software), and SIH26207 as
> AICTE / Student Innovation / *Travel & Tourism*. All docs use **SIH26205**.
> Re-verify on `sih.gov.in` before you submit. If it turns out to be a different
> number, change it here and nowhere else.

---

## 2. The problem, stated honestly

Every student in a classroom of sixty gets the same explanation, at the same
speed, in the same order — but arrives with different prior knowledge, a
different amount of time, and a different reason for being there. Teaching is
one-to-many; learning is stubbornly one-to-one.

The existing digital answer is a video library with a search box. It solves
*access*. It does not solve *fit*. A student who does not understand a lecture
gets the option to watch the same lecture again.

What has never been affordable at scale is the thing that actually works: a
tutor who notices you are lost, works out *why*, and changes approach.

**Sarathi is that tutor, as software.**

### What we are NOT building

State this out loud so no one drifts:

- ❌ Not a course marketplace or content library
- ❌ Not a video platform
- ❌ Not a chatbot with a textbook bolted on
- ❌ Not a quiz app with a leaderboard
- ❌ Not "ChatGPT with a nicer UI"

### What we ARE building

A system that:

1. **Diagnoses** how a specific learner learns, from a short adaptive
   conversation — not a personality quiz.
2. **Plans** a route from where they are to where they want to be, generated
   for their goal and their profile.
3. **Teaches** each lesson in a form chosen for that learner, and reshapes the
   explanation mid-lesson when they struggle.
4. **Checks** understanding continuously and tracks mastery per concept, not
   per lesson.
5. **Re-plans** the route when the evidence says the route is wrong.

That loop — diagnose → plan → teach → check → re-plan — is the product. Every
feature must serve it. Anything that does not serve it is scope creep.

---

## 3. The one-sentence differentiator

> Most "AI learning" products generate content. **Sarathi generates pedagogy** —
> it decides *how* to teach before it decides *what* to say, and it changes that
> decision based on what the learner actually does.

If a judge asks "how is this different from ChatGPT?", the answer is:

- ChatGPT answers the question you asked. Sarathi decides what question you
  should be asked next.
- ChatGPT has no memory of your misconceptions. Sarathi maintains a per-concept
  mastery state and routes around your gaps.
- ChatGPT has no plan. Sarathi has a plan, knows where you are in it, and
  rewrites it when you fall behind.

---

## 4. The agentic architecture (conceptual)

Five specialised agents, one shared learner state. Every agent is a prompt +
tools + a strict output schema — **not** a free-form chat.

| Agent | Trigger | Reads | Writes |
|---|---|---|---|
| **Diagnostician** | New user, or profile refresh | Learner answers | `LearnerProfile` |
| **Planner** | New goal, or re-plan request | `LearnerProfile`, `Goal`, `MasteryState` | `Plan` → `Module[]` → `Lesson[]` |
| **Tutor** | Lesson start / learner message | `Lesson`, `LearnerProfile`, `MasteryState`, thread history | `ContentBlock[]`, `TutorMessage` |
| **Assessor** | Lesson checkpoint / submit | `Lesson`, learner responses | `Checkpoint`, `MasteryState` deltas |
| **Adaptor** | Signal thresholds crossed | `Signal[]`, `MasteryState`, `Plan` | `AdaptationEvent`, new `Plan` version |

```
                    ┌──────────────────┐
   onboarding  ───► │  DIAGNOSTICIAN   │ ──► LearnerProfile
                    └──────────────────┘            │
                                                    ▼
   "teach me X"  ─► ┌──────────────────┐    ┌───────────────┐
                    │     PLANNER      │◄───│ LearnerProfile│
                    └────────┬─────────┘    │ MasteryState  │
                             │              └───────────────┘
                             ▼                      ▲
                    Plan → Modules → Lessons        │
                             │                      │
                             ▼                      │
                    ┌──────────────────┐            │
                    │      TUTOR       │────────────┤
                    └────────┬─────────┘            │
                             │ ContentBlock[]       │
                             ▼                      │
                    ┌──────────────────┐            │
                    │     ASSESSOR     │────────────┤
                    └────────┬─────────┘  mastery Δ │
                             │                      │
                             ▼                      │
                    ┌──────────────────┐            │
                    │     ADAPTOR      │────────────┘
                    └────────┬─────────┘
                             │ re-plan when evidence demands it
                             └──────────► new Plan version
```

**The Adaptor closing the loop is the whole demo.** If you build only one thing
that judges remember, make it a live moment where the learner struggles and the
plan visibly rewrites itself, with a human-readable reason.

---

## 5. How a learner profile is actually built

> ⚠️ **Do not build this on "learning styles" (visual / auditory / kinaesthetic).**
> The VARK model is not supported by evidence, and a technical jury with an
> education background will say so out loud. See `Rules.md` §7.

The `LearnerProfile` is built from **two sources**:

**A. Declared** — from the onboarding diagnostic (adaptive, ~8–12 questions,
mixes self-report with 3–4 actual micro-problems that reveal prior knowledge).

| Dimension | Values | Why it matters |
|---|---|---|
| `prior_knowledge` | per-concept: `none / shaky / solid` | The single strongest predictor of what to teach next. |
| `pace` | `deliberate / standard / fast` | Controls lesson granularity and step size. |
| `representation_pref` | `concrete_first / abstract_first` | Example-then-rule vs rule-then-example. Evidence-backed. |
| `scaffolding_pref` | `worked_examples / guided_discovery` | How much to show before asking. |
| `depth_pref` | `breadth_survey / depth_mastery` | Shapes plan width. |
| `motivation` | `exam / career / curiosity / project` | Changes framing and what gets cut. |
| `session_minutes` | integer | Hard budget per lesson. Respect it. |
| `language` | BCP-47 tag | Explanation language; technical terms stay in English. |
| `accessibility` | object, keys below | Font scale, reduced motion, screen-reader mode, dyslexia-friendly. |

🔴 **`accessibility` keys are fixed.** It is a typed object, not free-form JSON.
The frontend reads exactly these; the backend validates exactly these.

| Key | Type | Default | Effect |
|---|---|---|---|
| `font_scale` | number (1.0–2.0) | `1.0` | Multiplies all `rem` type sizes |
| `reduced_motion` | boolean | `false` | No transitions, autoplay or parallax |
| `screen_reader` | boolean | `false` | Verbose `aria-live` announcements, no purely visual affordances |
| `dyslexia_font` | boolean | `false` | Switches lesson body to a dyslexia-friendly face |

**B. Observed** — from behavioural `Signal`s during real lessons. These
**override** declared preferences over time, because what people do beats what
they say.

| Signal | Emitted when | Interpretation | Wired to a v1 trigger? |
|---|---|---|---|
| `checkpoint_score` | checkpoint submitted | mastery evidence | ✅ `struggling`, `racing` |
| `confusion_flag` | "I'm lost" pressed (**server-side**, see below) | explicit failure signal | ✅ `stuck` |
| `time_on_block` | learner dwells on one block | confusion or deep engagement | ✅ `racing` — lesson elapsed is the **sum** of a lesson's `time_on_block` values, compared against `est_minutes` |
| `hint_requested` | "Show me" pressed on a hidden `step` or `example` step | scaffolding too thin | — collected only |
| `retry` | **checkpoint** item retried | concept not landed | — collected only |
| `inline_check_failed` | wrong answer on a `quiz_inline` block (not scored) | concept wobbly, not yet failed | — collected only |
| `skip` | learner uses the skip-ahead control | material too easy | — collected only |
| `session_abandon` | leaves mid-lesson | lesson too long or too hard | — collected only |
| `revisit` | returns to a completed lesson | retention gap | — collected only |

🔴 **Who emits what.** Every signal is POSTed by the **client** to
`POST /signals`, with **one exception**: `confusion_flag` is written
**server-side** by `POST /lessons/{id}/reexplain` (endpoint 19b), because that
endpoint *is* the "I'm lost" press. The client must **not** also POST it —
double-counting would trip the Adaptor's `stuck` trigger on the first press.

🔴 **The "Wired?" column is authoritative and must match
`Backend_Instructions.md` §9's trigger table exactly.** Collected-only signals
are stored for post-hoc analysis and the pitch metrics — do **not** invent
triggers for them in v1, and do not stop emitting them either. If you wire one
later, update both tables in the same change.

**Rule:** the profile is versioned. Content is generated against a
`profile_version` and cached against it. When the profile changes, cached
content for that learner is invalidated.

---

## 6. Team, roles, ownership

| Role | Person | Owns |
|---|---|---|
| Team Lead / Integrator | **Disha** | `Context.md`, `Rules.md`, `Project_requirement.md`, `contract/` arbitration, demo script, pitch |
| Frontend Dev | *(assign)* | `apps/web/`, `apps/mobile/`, `packages/ui/`, `packages/api-client/`, `packages/i18n/` |
| Backend Dev | *(assign)* | `services/api/`, `services/agents/`, `migrations/`, `fixtures/`, `contract/openapi.yaml`, `Architecture.md`, `Memory.md`, `Phase.md` |

Both instruction files (`Frontend_Instructions.md`, `Backend_Instructions.md`) are
owned by the **Team Lead**. Devs propose changes via `contract/CHANGELOG.md`.

**Ownership is absolute.** Neither dev — and no AI agent acting for them —
edits a file owned by the other. Not "just a quick fix". Not "it was obviously
broken". You open an issue in `contract/CHANGELOG.md` and the owner fixes it.

The single most likely way this project fails is not a hard bug. It is the two
of you drifting apart for six hours and discovering it at hour seven.

---

## 7. The synergy protocol — read this twice

Two developers, both driving AI, working in parallel, cannot stay aligned by
talking. They stay aligned by **coding against a frozen contract**.

### 7.1 The contract is the boundary

```
contract/
├── openapi.yaml       # THE source of truth. Backend generates it. Both obey it.
├── blocks.schema.json # ContentBlock union — what the Tutor emits, what the UI renders
├── events.md          # SSE event names + payloads
├── status.md          # per-endpoint: planned | mocked | live | done
└── CHANGELOG.md       # every contract change, dated, with both devs' initials
```

### 7.2 Nobody hand-writes a type

- Backend defines Pydantic models → FastAPI emits `openapi.yaml`.
- Frontend runs `openapi-typescript contract/openapi.yaml -o packages/api-types/index.ts`.
- **If a type is hand-written on the frontend, it is a bug.** It will silently
  drift and you will find out during the demo.

### 7.3 Frontend never waits for backend

From hour one, the frontend runs against a mock server generated from the same
`openapi.yaml`:

```bash
npx @stoplight/prism-cli mock contract/openapi.yaml --port 4010
```

🔴 **No `--dynamic` flag.** Prism must return the `example` values the backend
commits in `openapi.yaml`, not random junk — otherwise the frontend builds its
renderers against noise.

`NEXT_PUBLIC_API_BASE=http://localhost:4010/api/v1` until `contract/status.md`
marks an endpoint `live`, then `http://localhost:8000/api/v1`. Flipping one env
var moves the whole app to the real backend. There is no "blocked on backend"
in this project.

### 7.4 Changing the contract

A contract change is the only thing that can break the other person. So:

1. Propose it in `contract/CHANGELOG.md` under `## Proposed`.
2. Ping the other dev. **Wait for a written ack** in the same file.
3. Backend implements, regenerates `openapi.yaml`, moves the entry to `## Merged`
   with a date and both initials.
4. Frontend regenerates types and fixes any compile errors immediately.

**Additive changes** (new optional field, new endpoint) may skip the wait — just
log them. **Breaking changes** (rename, remove, type change, required field)
**never** skip the wait.

### 7.5 The 15-minute sync

Twice a day — start and end of each working block — both devs write three lines
in `contract/status.md`:

```
[YYYY-MM-DD HH:MM] FE  done: <what landed>  next: <what's next>  blocked: <or "none">
[YYYY-MM-DD HH:MM] BE  done: <what landed>  next: <what's next>  blocked: <or "none">
```

If "blocked" is not "none" twice in a row, the Team Lead intervenes. That is
the entire escalation policy.

### 7.6 Integration is not a phase

Merge to `main` at least twice a day. A branch that has not touched `main` in a
day is a branch that is diverging. There is no integration day at the end,
because there is never enough time for one.

---

## 8. Glossary — use these exact words

Both devs and both AIs must use these terms. Do not invent synonyms. If a name
appears in the API, the database, the UI and the pitch, it must be **the same
name in all four**.

| Term | Meaning | Never call it |
|---|---|---|
| **Learner** | The end user, a student | user, kid, customer |
| **LearnerProfile** | Versioned model of how this learner learns | persona, style, preferences |
| **Diagnostic** | Onboarding session that produces a LearnerProfile | quiz, test, assessment |
| **Goal** | What the learner said they want to learn | topic, course, subject |
| **Plan** | Versioned route from current state to Goal | curriculum, syllabus, path |
| **Module** | A group of Lessons inside a Plan | chapter, unit, section |
| **Lesson** | One sitting's worth of teaching | class, video, page |
| **ContentBlock** | One renderable unit inside a Lesson | element, component, chunk |
| **Checkpoint** | Understanding check attached to a Lesson | quiz, exam, test |
| **Concept** | Atomic learnable idea; mastery is tracked per Concept | topic, skill, tag |
| **MasteryState** | Learner × Concept → score + confidence | progress, level, XP |
| **Signal** | Behavioural telemetry event | analytics, log, metric |
| **AdaptationEvent** | Record of the Adaptor changing the Plan, with reason | update, change, tweak |
| **Job** | Async agent task the client polls | task, request, run |

Casing: `snake_case` in JSON and Postgres, `camelCase` in TypeScript
(generated automatically — do not convert by hand), `PascalCase` for types.

### 8.1 Sanctioned exceptions

These look like glossary violations and are not. Do not "fix" them.

| Name | Where | Why it stands |
|---|---|---|
| `users`, `user_id` | Auth table + FK columns only | Auth is a separate domain. Every FK stays `user_id`. In product copy, UI, prompts and the pitch, the entity is a **Learner**. |
| `quiz_inline` | `ContentBlock` type | A third thing — an unscored in-lesson check. Neither a Diagnostic nor a Checkpoint. |
| `normalized_topic`, `target_level` | `goals` table | Parsed fields of a Goal, not a separate entity. |
| `/progress/*` | API namespace | A route namespace. The entity returned is still `MasteryState`. |
| `PlanDraft`, `ModuleDraft`, `LessonDraft`, `ProfileDraft`, `NextQuestion`, `ScoreResult`, `AdaptationDecision` | Agent output schemas | Internal agent contracts. `*Draft` = unpersisted agent output; once written to the DB it is a `Plan` / `Module` / `Lesson`. |
| `TutorMessage` | `tutor_messages` rows | One turn in a tutor thread. A real entity, not a synonym for `ContentBlock`. |

---

## 9. Constraints we are working inside

- **Two developers.** Every scope decision is a decision about their hours.
- **Model cost and latency are real.** Plan generation takes 20–90 seconds. The
  UI must be built for that from the start, not retrofitted.
- **Demo network is hostile.** Venue Wi-Fi fails. Cached demo data and a
  recorded fallback are not optional — see `Project_requirement.md` §8.
- **Judges have five minutes.** The demo is a rehearsed path, not an
  exploration. Everything on that path must be flawless; everything off it
  must merely not crash.

---

## 10. Definition of done for the project

We are done when a judge can, unaided, in five minutes:

1. Sign up and complete the diagnostic.
2. Type a real goal in their own words.
3. Watch a plan appear with a visible, readable rationale.
4. Open a lesson and see it explained in the style the profile chose.
5. Deliberately fail a checkpoint.
6. **Watch the plan rewrite itself, and read why.**
7. Open the same account on the mobile app and see the same state.

Every hour spent on something not on that list is an hour borrowed from
something that is.

---

*Last updated: 2026-08-26 · Owner: Disha (Team Lead) · Changes to this file require Team Lead approval.*
