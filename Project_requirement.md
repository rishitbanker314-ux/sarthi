# Project_requirement.md

> **What we are building, for whom, and in what order.**
> Prerequisite reading: `Context.md`, `Rules.md`.
>
> This file answers "is this feature in scope?" Nothing else does. If a feature
> is not in this file, it is not in scope.

---

## 1. Product summary

**Sarathi** is an AI-agentic learning mentor. A learner completes a short
adaptive diagnostic, states a learning goal in plain language, and receives a
personalised plan that is taught to them lesson by lesson — and rewritten when
the system sees evidence it is not working.

| | |
|---|---|
| Primary surface | **Web app** (Next.js) — full feature set |
| Secondary surface | **Mobile companion** (Expo / React Native) — continue, learn, track |
| Delivery scope | Web-first. Mobile is a real, installable app that shares the same account and state, with a reduced feature set. |

---

## 2. Target users

### Primary — "the exam-pressed undergraduate"

**Riya, 20, B.Tech 3rd year, tier-3 college, small-town India.**
Placements in five months. Her college covers DSA in one theory paper with no
practice. She has watched thirty hours of YouTube and cannot tell whether she is
ready. She has a mid-range Android phone, a shared laptop, and intermittent Wi-Fi.

*What she needs:* a route, not a library. Something that tells her what to do
today and whether yesterday worked.

### Primary — "the behind-in-class school student"

**Arjun, 15, Class 10, state board, Hindi-medium school.**
Fell behind in trigonometry when he missed two weeks. The class has moved on;
the textbook assumes what he missed. He is embarrassed to ask. He learns on a
shared family phone, 20–30 minutes at a time.

*What he needs:* something that finds the exact gap two chapters back and fixes
it without making him feel stupid, in language he thinks in.

### Secondary — "the switching professional"

**Meera, 27, mechanical engineer moving into data analysis.**
Strong maths, no programming. Every online course starts either too basic or
assumes CS fundamentals. Two hours a week, high discipline, low tolerance for
filler.

*What she needs:* a plan that credits what she already knows and skips it.

### Tertiary — "the teacher"

**Mr. Verma, 44, teaches 62 students across three sections.**
Wants to know which five students are stuck on which concept, before the exam.

*Scope note:* the teacher dashboard is **Should-have (S6), unphased — build only
in Phase 6 slack, after Phase 4 has exited.** It is a strong pitch asset and a
genuine differentiator, but it is not the core loop. 🔴 It must never be started
while any Phase 4 exit criterion is unticked.

### Explicit non-users (v1)

Institutional admins, content authors, parents, corporate L&D buyers. Do not
build screens for them.

---

## 3. Feature list (MoSCoW)

### 3.1 MUST — no demo without these

| # | Feature | Acceptance criteria |
|---|---|---|
| M1 | Email/password auth | Handled by **Supabase Auth** client-side (`contract/CHANGELOG.md`, 2026-08-29). Register, log in, stay logged in across refresh and app restart; `supabase-js` refreshes the token; logout clears both surfaces. The backend verifies the token and has no `/auth/*` endpoints. |
| M2 | Adaptive diagnostic | 8–12 questions, adapts based on previous answers, includes ≥3 micro-problems that measure prior knowledge; produces a `LearnerProfile`; completes in under 4 minutes |
| M3 | Profile review + override | Learner sees their profile in plain language and can change any dimension; edits bump `profile_version` |
| M4 | Free-text goal capture | Learner types a goal in their own words; system parses it into `normalized_topic`, `target_level`, optional `deadline`, and shows its interpretation for confirmation |
| M5 | Plan generation | Planner produces Modules → Lessons with a **visible rationale** explaining why this order for this learner; async with live progress; ≤90s p95 |
| M6 | Plan view | Modules and lessons with status, estimated minutes, and mastery indicators; rationale readable at plan and module level |
| M7 | Adaptive lesson delivery | Tutor generates `ContentBlock[]` shaped by the profile; streams via SSE; respects `session_minutes`; caches per `(lesson_id, profile_version)` |
| M8 | In-lesson tutor chat | Learner asks a question mid-lesson; Tutor answers with full lesson + profile + mastery context; streamed |
| M9 | "I'm lost" control | One button re-explains the current block a different way via `POST /lessons/{id}/reexplain`, which writes the `confusion_flag` signal **server-side** |
| M10 | Checkpoints | Assessor generates 3–5 items per lesson, mixed types, scores them, returns per-item feedback and `MasteryState` deltas |
| M11 | Mastery tracking | Per-`Concept` score + confidence, updated by checkpoints and signals; visible to the learner |
| M12 | **Adaptive re-planning** | When thresholds are crossed, Adaptor produces a new `Plan` version with a human-readable reason; learner is shown what changed and why, and can accept or decline |
| M13 | Progress dashboard | Continue-lesson card, plan progress, mastery map, streak-free activity summary. *(Recent-adaptations panel is added in Phase 4, not Phase 3.)* |
| M14 | Signal collection | Every client-side signal in `Context.md` §5 batched to `POST /signals`; never blocks the UI. `confusion_flag` is the one exception — written server-side by endpoint 19b. |
| M15 | Mobile companion | Login, continue lesson, read lesson content, tutor chat, progress. Same account, same state. **Reducible, not cuttable:** if time runs short, trim to login + continue + read lesson. The app must exist and must show shared state — the problem statement promises a mobile app. |

### 3.2 SHOULD — build if the Must set is stable

| # | Feature | Note |
|---|---|---|
| S1 | Vernacular explanations (Hindi + one regional) | Explanation language switches; technical terms stay English. Strong jury asset for the Indian context. |
| S2 | Voice input for goal + tutor chat | Web Speech API. Cheap, demos brilliantly, matters for low-literacy and low-typing users. |
| S3 | Concept prerequisite graph, visualised | Shows *why* a lesson was inserted. Makes the adaptation legible. |
| S4 | Spaced-repetition review queue | Retrieval practice on concepts whose mastery is decaying. Pedagogically the strongest addition. |
| S5 | Syllabus/notes upload → grounded plan | PDF upload, chunk, embed, ground the plan in the learner's actual syllabus. Big differentiator; also the biggest time sink. |
| S6 | Teacher dashboard | Class-level mastery heatmap, per-concept stuck list. |
| S7 | Offline lesson caching (mobile + PWA) | Downloaded lessons readable without network. Real for Indian users, and hedges the venue Wi-Fi. |

### 3.3 COULD — only with genuine slack

| # | Feature |
|---|---|
| C1 | Peer explanations — learners submit alternative explanations, best get reused |
| C2 | Diagram generation for visual concepts |
| C3 | Code sandbox for programming lessons |
| C4 | Weekly email/push digest |
| C5 | Export plan as PDF |

### 3.4 WON'T — v1, explicitly excluded

Video hosting or generation · live human tutoring · payments · social feed ·
gamified leaderboards · proctored exams · certificate issuance · LMS/SIS
integration · multi-tenant institution accounts · admin panel.

---

## 4. Core user stories with acceptance criteria

**US-01 — Diagnostic**
*As a new learner, I want the system to work out how I learn, so lessons fit me.*
- Given a new account, when I open the app, I am taken into the diagnostic.
- Questions adapt: answering "I've never seen this" changes what comes next.
- At least three questions are actual micro-problems, not self-report.
- I can pause and resume without losing answers.
- On completion I see my profile in plain language, and I can change it.

**US-02 — Goal**
*As a learner, I want to say what I want to learn in my own words.*
- Free text, ≥10 characters, any language in the supported set.
- The system shows its interpretation (`normalized_topic`, `target_level`,
  `deadline`) before planning.
- If it misreads me, I can correct those fields via `PATCH /goals/{id}` without
  retyping the goal.
- Nonsense or non-educational input produces a friendly re-prompt, not a crash.

**US-03 — Plan**
*As a learner, I want a route, and I want to know why it's this route.*
- Plan appears with modules and lessons in a defensible order.
- A rationale is shown at plan level and per module.
- The rationale references *my* profile and *my* mastery — not generic text.
- Generation shows live progress and never looks frozen.
- If generation fails, I get a clear message and a retry that works.

**US-04 — Lesson**
*As a learner, I want the explanation to match how I learn.*
- Content streams in; first block visible in ≤3s.
- `concrete_first` learners see an example before the rule; `abstract_first` the reverse.
- Estimated time is within ±25% of my `session_minutes`.
- I can ask a question at any point without losing my place.
- "I'm lost" produces a genuinely different explanation, not a paraphrase.

**US-05 — Checkpoint**
*As a learner, I want to find out whether I actually understood.*
- 3–5 items, at least two requiring construction rather than recognition.
- Immediate per-item feedback explaining *why*, not just right/wrong.
- Mastery updates visibly after submission.
- I can retry; retries are recorded as signals.

**US-06 — Adaptation** *(the demo moment)*
*As a struggling learner, I want the plan to change instead of me falling behind.*
- Failing a checkpoint below threshold triggers the Adaptor within one lesson.
- I am shown: what changed, why, and what it means for my timeline.
- The reason is specific — names the concept and the evidence.
- I can accept or decline the change.
- Declining is remembered and does not re-prompt immediately.

**US-07 — Continuity**
*As a learner, I want to continue on my phone where I left off on my laptop.*
- Same credentials work on both.
- Lesson progress, mastery and plan version are identical within 5 seconds.
- Mobile shows the same `ContentBlock` types, rendered natively.

---

## 5. Non-functional requirements

| Area | Requirement |
|---|---|
| **Latency** | First content block ≤3s p95 · plan generation ≤90s p95 with live progress · non-LLM API ≤400ms p95 |
| **Reliability** | Every LLM call: timeout, one retry, then a graceful degraded path. No unhandled promise rejections. No 500 on the demo path. |
| **Cost** | Cache aggressively per `(lesson_id, profile_version)`. Rate-limit LLM endpoints per user. Track token spend per agent from day one — you cannot fix a cost problem you cannot see. |
| **Security** | See `Rules.md` §5. Every query scoped to the authenticated learner. |
| **Accessibility** | WCAG 2.1 AA on the demo path. Keyboard-complete. Screen-reader labelled. |
| **i18n** | All strings via the i18n layer from commit one. UI: English + Hindi. Content: English + Hindi + one regional. |
| **Devices** | Web: Chrome/Edge/Firefox/Safari, ≥360px wide. Mobile: Android 10+, iOS 15+. |
| **Data** | Learner data is theirs. Export and delete-account endpoints exist. No third-party analytics carrying learner content. |
| **Observability** | Structured JSON logs with request ID + agent name + latency + token count. Metrics per agent. |

---

## 6. What "personalised" concretely means

This table is the contract between the pitch and the code. If the pitch claims
adaptation, the code must show it here.

| Profile dimension | Observable effect a judge can verify |
|---|---|
| `prior_knowledge` = solid on a concept | Lesson skipped or compressed; plan is visibly shorter |
| `prior_knowledge` = none | Prerequisite lesson auto-inserted before the requested one |
| `pace` = deliberate | More, smaller blocks; more worked examples; smaller step size |
| `pace` = fast | Denser blocks; earlier checkpoints; less repetition |
| `representation_pref` = concrete_first | `example` block precedes `text`/`math` rule block |
| `representation_pref` = abstract_first | Rule stated first, then instances |
| `scaffolding_pref` = worked_examples | Full solutions shown before practice |
| `scaffolding_pref` = guided_discovery | `quiz_inline` prompts before the explanation |
| `depth_pref` = breadth_survey | More modules, fewer lessons each |
| `depth_pref` = depth_mastery | Fewer modules, more lessons and checkpoints each |
| `motivation` = exam | Exam-pattern items; timeline anchored to `deadline` |
| `motivation` = project | Applied lessons; project milestones in the plan |
| `session_minutes` = 20 | Lessons split so none exceeds ~20 min estimate |
| `language` = hi | Explanations in Hindi; technical terms retained in English |
| `accessibility.reduced_motion` | No transitions, no autoplay, no parallax |

**Rule:** every row above must be demonstrable by changing one profile field and
reloading. If it is not, the personalisation is decorative. Build a
`/debug/profile` switcher (dev-only) so you can prove any row in ten seconds.

---

## 7. Phase overview

Detailed exit criteria live in `Phase.md` (backend) and
`Frontend_Instructions.md` §13. 🔴 Both must use these exact phase numbers **and
names**.

| Phase | Name | Ends when |
|---|---|---|
| **0** | Contract & skeleton | `openapi.yaml` v0.1 exists; both apps boot; frontend runs fully against the Prism mock |
| **1** | Identity & diagnostic | Auth works end-to-end; diagnostic produces a real `LearnerProfile` |
| **2** | Goal → Plan | A typed goal produces a real plan with a real rationale, live on both apps |
| **3** | Lesson & checkpoint | A lesson is generated, streamed, rendered and assessed; mastery moves |
| **4** | **Adaptation loop** | Failing a checkpoint visibly rewrites the plan with a readable reason |
| **5** | Mobile companion | Login, continue, lesson, chat, progress on device |
| **6** | Polish & demo hardening | Demo script rehearsed end-to-end three times without incident |

🔴 **Phase 4 is the project.** A polished app with no adaptation loses to a
rough app that adapts.

**Cut order when time runs short** — top of the list goes first:

1. Everything in §3.3 (COULD)
2. Everything in §3.2 (SHOULD), including the teacher dashboard and RAG
3. Phase 6 polish beyond the demo path
4. Phase 5 trimmed to login + continue + read lesson (see M15 — reduce, never remove)
5. 🔴 **Never Phase 4.**

---

## 8. Demo risk plan

Assume the venue network fails. This is not pessimism; it is what happens.

1. **Seeded demo account** — `demo@sarathi.app` with a completed profile, a
   generated plan, and one lesson already cached. Never depends on live
   generation to *show* the product.
2. **Response cache with a `DEMO_MODE` flag** — every LLM call on the demo path
   has a recorded response in `fixtures/demo/`. With `DEMO_MODE=true` the
   backend serves fixtures and never calls the network. Rehearse in this mode.
3. **Local-first deployment** — the full stack runs on one laptop via Docker
   Compose. Cloud deploy is a convenience, not a dependency.
4. **Recorded 3-minute walkthrough** — an MP4 on two USB drives and one phone.
   If everything fails, you still deliver.
5. **Rehearse three times.** Timed, out loud, on the demo laptop, on the demo
   network. The third run is where you find the real bug.

---

## 9. Success metrics for the pitch

Numbers to have ready. Instrument them from Phase 1 — you cannot backfill them
the night before.

| Metric | Target | Why a judge cares |
|---|---|---|
| Diagnostic completion time | < 4 min | Proves the onboarding isn't a wall |
| Plan generation p95 | < 90 s | Proves it's usable, not a batch job |
| Adaptation trigger accuracy | > 80% agree with human judgement on 20 test cases | Proves adaptation is real, not random |
| Mastery gain per lesson | measurable pre/post delta | Proves learning, not engagement |
| Cost per learner-hour | quantified in ₹ | Proves it can scale in an Indian context |
| Lessons per profile variant | ≥3 visibly different renderings of one lesson | Proves personalisation is not cosmetic |

---

*Last updated: 2026-08-26 · Owner: Disha (Team Lead) · Scope changes require Team Lead approval and a `contract/CHANGELOG.md` entry.*
