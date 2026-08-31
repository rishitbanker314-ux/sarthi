# Frontend_Roadmap.md
### Sarathi — SIH26205 · Building the whole frontend with Antigravity IDE

> **Who this is for:** the frontend developer, building the web app and the
> mobile companion alone, using Antigravity for code generation. It assumes you
> have not built a Next.js + Expo + Server-Sent-Events app before. Every step
> says what to do, what to paste, what "working" looks like, and how to tell
> when it has gone wrong.
>
> **Its companion is `Antigravity_Prompts_Frontend.md`** — every prompt, in
> order, ready to paste. This file explains *why* and *how to check*; that file
> is *what to type*.
>
> 🔴 **Read `Integration_Guide.md` before your first prompt.** You are working
> on a branch that must merge cleanly with someone else's. That document tells
> you which files you may never create.

---

## 0. How to use these files

Keep four things open:

1. **`apps/web/FE_PHASE.md`** — where you are. One phase is `⬅ CURRENT`.
2. **`apps/web/FE_MEMORY.md`** — what already exists.
3. **`Antigravity_Prompts_Frontend.md`** — the next prompt.
4. **This file** — the verification steps for that prompt.

The loop never changes:

```
merge main  →  read FE_PHASE.md  →  copy the next prompt
   →  review Antigravity's plan  →  let it build
   →  LOOK AT IT IN A BROWSER  →  update FE_MEMORY.md + FE_PHASE.md  →  next
```

🔴 **"Look at it in a browser" is not optional.** Backend bugs show up as failing
tests. Frontend bugs show up as a button that is three pixels off the screen on
a phone, or a spinner that never stops. Tests will not catch those. Your eyes
will.

**Rough time budget** (honest, assuming you verify properly):

| Phase | Name | Realistic hours |
|---|---|---|
| 0 | Contract & skeleton | 5–6 |
| 1 | Identity & diagnostic | 7–9 |
| 2 | Goal → Plan | 7–9 |
| 3 | Lesson & checkpoint | 11–13 |
| 4 | **Adaptation loop** | 6–8 |
| 5 | Mobile companion | 7–9 |
| 6 | Polish & demo hardening | 7–9 |
| | **Total** | **~50–63 hours** |

Phase 3 is the biggest block. Phase 0 is bigger than it looks — the block
renderers live there, and they are the deepest work you do.

---

## 1. What you will have at the end

- A **Next.js web app** where a learner signs up, is diagnosed, states a goal in
  their own words, watches a plan being generated, and is taught lesson by lesson
- A **ContentBlock renderer** that turns the backend's JSON into twelve kinds of
  teaching material — worked examples, misconception callouts, inline checks, maths
- **Live streaming lessons** over SSE, arriving block by block
- The **adaptation modal** — the screen the whole project is judged on
- An **Expo mobile app** sharing the same account and state
- Full **keyboard, screen-reader, dark-mode and Hindi** support
- All of it built against generated types, so a backend change breaks your build
  instead of your demo

---

## 2. Antigravity 101 — only the parts you will actually use

Antigravity is an agent-first IDE. You delegate tasks and review artifacts.

### 2.1 Editor vs Agent Manager

- **Editor** — a code window with an agent side-panel. Use it for everything
  through Phase 2, and whenever you want to watch what is happening.
- **Agent Manager** — several agents in parallel, optionally in isolated git
  worktrees. Genuinely useful from Phase 3: one agent building the checkpoint
  screen while another builds the tutor drawer, since they barely touch.

**Start in the Editor.**

### 2.2 Artifacts — the review surface

| Artifact | What it is | What you do with it |
|---|---|---|
| **Implementation Plan** | The proposed approach, before any code | 🔴 Read every line. Comment on it. |
| **Walkthrough** | A narrated summary of what changed | Skim to confirm |
| **Screenshots** | 🔴 **Browser captures — your best friend.** | The agent can open your app, screenshot it, and *see* what it built |

🔴 Settings → Artifact Review must **not** be "Always Proceed."

### 2.3 🔴 `/browser` — the frontend superpower

Antigravity has a sandboxed browser subagent. For frontend work this changes
everything: the agent can render the page it just wrote, take a screenshot, read
the console, and fix its own mistake before you ever see it.

Use it constantly:

```
/browser open http://localhost:3000/debug/blocks, screenshot it, and tell me
which block types look visually broken or unreadable
```

```
/browser open http://localhost:3000/lesson/demo, resize to 360px wide,
screenshot, and report anything that overflows horizontally
```

```
/browser open http://localhost:3000/plan/demo, read the console, and report
any errors or React warnings
```

This is the closest thing to a second pair of eyes you will get. Backend devs
do not have this. Use it after every screen.

### 2.4 Slash commands

| Command | Use it for |
|---|---|
| `/plan` | 🔴 **Your default** for anything non-trivial |
| `/grill-me` | Interviews *you* about edge cases. Use once per phase. |
| `/goal` | Runs to completion. Only for mechanical work — writing the remaining eight block renderers once you have approved four. |
| `/learn` | Turns this session's corrections into a rule or skill. Use at the end of every phase. |
| `/browser` | See §2.3. Use it more than you think you should. |
| `/btw` | A quick side question without interrupting a running task |
| `/schedule` | Recurring tasks |

### 2.5 Rules — always-on constraints

- **Workspace:** `.agents/rules/` — markdown files
- **Global:** `~/.gemini/GEMINI.md`
- **Limit:** 12,000 characters per file
- **Activation:** `Always On`, `Glob` (e.g. `apps/web/**/*.tsx`), `Model Decision`, `Manual`
- `@filename` pulls in another file

🔴 **Your rule files are numbered 40, 50, 60.** `main` owns `00-project.md`
(the shared rules you and the backend both follow); the backend owns 10, 20, 30.
Do not create a file with any of those numbers — see `Integration_Guide.md` §2.
Full contents in §6.1.

### 2.6 Skills — reusable procedures

- **Workspace:** `.agents/skills/<skill-name>/SKILL.md`
- **Global:** `~/.gemini/config/skills/<skill-name>/SKILL.md`
- Frontmatter: `description` is **required** and is what makes the skill fire;
  `name` is optional
- Optional subfolders: `scripts/`, `examples/`, `resources/`

The agent sees every skill's *description* at the start of a conversation and
loads the body only when one looks relevant. Write descriptions as "what it does
AND when to use it." Six skills in §6.2.

### 2.7 Workflows — your own slash commands

Markdown, invoked as `/workflow-name`, same 12,000-character limit. Three in
§6.3, all prefixed `fe-` so they cannot collide with the backend's.

### 2.8 Models

| Task | Model |
|---|---|
| Implementation plans, architecture, a subtle layout or streaming bug | **Gemini 3.1 Pro** |
| A specified component, a screen from a described layout, tests, translations | **Gemini 3.7 Flash** |
| A bug two Gemini attempts failed on | **Claude Sonnet 4.6 (thinking)** — a different model family breaks deadlocks |
| A UI mockup or placeholder image | **Nano Banana 2** (image generation, non-selectable — just ask) |

Plan with Pro, build with Flash. Watch the Weekly and Five Hour limits in the
model dropdown.

---

## 3. Accounts, keys and costs

### 3.1 What you need

| # | Thing | From | Cost |
|---|---|---|---|
| 1 | GitHub access to the repo | Disha | Free |
| 2 | `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 🔴 **Ask Disha** | Free |
| 3 | Node 20 LTS + pnpm | `nvm install 20 && corepack enable` | Free |
| 4 | Docker Desktop | For running the real backend locally (§7) | Free |
| 5 | Expo Go on your phone | App store, Phase 5 | Free |
| 6 | Vercel account | Phase 6 deploy | Free |

🔴 **The anon key is the only Supabase key that may touch your code.** If anyone
sends you a `service_role` key, refuse it and tell them — it bypasses every
access rule in the database and would be catastrophic in a public bundle.

### 3.2 Free vs paid — every choice

| Need | Choice | Cost | Why |
|---|---|---|---|
| Web hosting | **Vercel** | Free hobby tier | Made by the Next.js team; zero-config; preview URL per push |
| Alternative | Cloudflare Pages / Netlify | Free | Fine, marginally more setup for App Router |
| Mobile dev | **Expo Go** | Free | Scan a QR, app runs on your phone. No build needed. |
| Mobile builds | EAS Build | Free tier, queued | Only needed if you want an installable APK. Expo Go is enough for the demo. |
| UI components | **shadcn/ui** | Free, MIT | Copied into your repo, not a dependency. Accessible by default via Radix. |
| Icons | **lucide-react** | Free, MIT | Matches shadcn |
| Fonts | **Google Fonts** via `next/font` | Free | Self-hosted at build time, no layout shift |
| Maths | **KaTeX** | Free | Faster than MathJax, enough for us |
| Code highlighting | **Shiki** | Free | Build-time, no runtime cost on web |
| Charts | **Recharts** | Free | Mastery map only |
| Voice input | **Web Speech API** | Free, built into the browser | Costs nothing, demos brilliantly |
| Mock API | **Prism** | Free | `npx`, no install |
| Error tracking | Sentry free tier | Free | Optional; skip unless you have slack |
| Analytics | **None** | — | 🔴 We handle student learning data. No third-party analytics. |

🔴 **You need no paid service.** If a prompt suggests adding one, say no.

---

## 4. The two constraints you cannot negotiate

### 4.1 The contract

`contract/openapi.yaml` is generated by the backend and published to `main`. You
**generate your TypeScript types from it** and never hand-write an API type.

```bash
pnpm gen:types    # openapi-typescript contract/openapi.yaml -o packages/api-types/index.ts
```

If you need an endpoint that is not in the contract, you do **not** invent it.
Run `/fe-request-contract`, message the backend dev, and build something else.

### 4.2 Auth is not yours to build

The backend has **no** `/auth/register`, `/auth/login` or `/auth/refresh`. You
authenticate directly with Supabase using `supabase-js`, and send the resulting
token to the API.

```
you ──signUp/signIn──► Supabase ──access token──► you
you ──Bearer token──► FastAPI ──verifies it──► your data
```

🔴 Immediately after a successful login, call `GET /me` **once**. That call is
what creates the learner's row in the backend database. Everything else 404s
until you do.

---

## 5. Day 0 — the literal setup

**5.1 Install Antigravity** from `antigravity.google`. Sign in. Settings →
Artifact Review → not "Always Proceed."

**5.2 Get the repo and the right branch.**

```bash
git clone <repo-url> sarathi
cd sarathi
git checkout frontend        # Disha creates it FROM main — see Integration_Guide.md §3
```

🔴 If `git checkout frontend` fails, the branch does not exist yet. Ask Disha to
create it **from `main`**. Do not create it yourself from `backend` — that drags
every Python file onto your branch and guarantees merge conflicts later.

**5.3 Check what you inherited.** You should see the ten `.md` docs and
`contract/`. You should see **no** `services/`, `migrations/` or
`pyproject.toml`. If you do, the branch was cut from the wrong place — stop and
tell Disha.

**5.4 Install toolchain.**

```bash
nvm install 20 && nvm use 20
corepack enable && corepack prepare pnpm@latest --activate
node -v && pnpm -v
```

**5.5 Write your Antigravity config** — §6 below. 🔴 Before your first code
prompt. Configuration added later does not retroactively fix code generated
without it.

**5.6 Read these, in this order**, before prompt F0.1:
`Integration_Guide.md` → `Context.md` → `Rules.md` → `Project_requirement.md` →
`Frontend_Instructions.md`.

That is about forty minutes. It will save you a week.

---

## 6. Your Antigravity configuration

### 6.1 Rules — `.agents/rules/`

🔴 Numbers 40, 50, 60 only. `main` owns `00-project.md` — the rules you and the
backend both follow; you read it, you never edit it. The backend owns 10, 20, 30
on its own branch.

**`.agents/rules/40-typescript.md`** · activation: **Glob** `**/*.{ts,tsx}`

```markdown
# TypeScript and React conventions

- TypeScript strict mode. `any` is BANNED — use `unknown` and narrow it.
  No `@ts-ignore` without a comment on the line above saying why.
- 🔴 Never hand-write a type that describes an API response. Every one of them
  comes from packages/api-types, which is generated from contract/openapi.yaml.
  If the type you need is not there, the contract is missing it — say so and
  stop.
- 🔴 Never call fetch outside packages/api-client. Every request goes through it.
- Server Components by default. Add "use client" only when the component needs
  state, an effect, or a browser API — and say in one comment why.
- Data fetching uses TanStack Query. Do not hand-roll caching, retries or
  polling.
- Forms use react-hook-form + zod. Never uncontrolled inputs with manual state.
- 🔴 No colour, spacing, radius or font-size literal in a component. Everything
  comes from the tokens in packages/ui. If a token is missing, add it there.
- 🔴 No user-visible string literal in a component. Every string goes through
  the i18n layer. Hardcoded English is a bug, not a shortcut.
- Never use localStorage or sessionStorage for anything that matters. Session
  storage is supabase-js's job; server state is TanStack Query's job.
- Components are small. If a file passes ~200 lines, it is doing two things.
- Every list has a stable key that is not the array index.
- Every async operation has a loading state, an empty state and an error state.
  A component with only a success state is unfinished.
```

**`.agents/rules/50-ui.md`** · activation: **Glob** `apps/web/**/*.tsx`, `packages/ui/**`

```markdown
# UI, accessibility and design

- 🔴 Every interactive element is reachable by keyboard, has a visible focus
  ring, and has an accessible name. Escape closes every overlay.
- 🔴 Contrast meets WCAG AA: 4.5:1 body text, 3:1 large text and UI borders.
- 🔴 Never convey meaning by colour alone. Always a label, an icon or a shape too.
- 🔴 Honour prefers-reduced-motion AND the learner's accessibility.reduced_motion
  profile field. Either one disables motion.
- 🔴 Type sizes in rem, never px, so accessibility.font_scale works.
- Streamed content lives in an aria-live="polite" region.
- Landmarks on every page: header, nav, main, footer.
- Responsive at 360px, 768px and 1280px. Wide content (code, tables, diagrams)
  scrolls inside its own overflow-x container — the page body NEVER scrolls
  horizontally.
- Dark mode from the start, via CSS variables. Never a second stylesheet.
- Lesson body text sits at a 60–75 character measure. It is the product; treat
  it as typography, not as UI chrome.

## Banned, because every hackathon judge has seen forty of them today

Gradient hero blobs. Confetti. Streak flames. Progress rings that measure
nothing. "AI is thinking ✨" with no substance behind it. Purple-to-pink
gradients on everything.

## Wanted

Calm, personal, intelligent. A tutor's notebook, not a SaaS dashboard.
Generous spacing. One accent colour. Semantic colour reserved for meaning:
mastery uses a sequential scale; adaptation uses the accent; each callout
variant gets its own distinct token.
```

**`.agents/rules/60-integration.md`** · activation: **Always On**

```markdown
# Integration discipline — the frontend must merge cleanly with the backend

Read @Integration_Guide.md section 2 before creating any file at the repository
root.

## Never create these — they belong to the backend branch

pyproject.toml, uv.lock, alembic.ini, Dockerfile, docker-compose.yml,
.dockerignore, a root .env.example, a root tests/ directory, a root scripts/
directory, services/, migrations/, fixtures/, Architecture.md, Memory.md,
Phase.md, and any .agents/rules file numbered 00, 10, 20 or 30.

## Never edit these

.gitignore (it lives on main and is frozen), contract/openapi.yaml,
contract/blocks.schema.json, contract/events.md, packages/api-types/** (it is
generated), and any document on main other than contract/status.md and
contract/CHANGELOG.md.

## The contract

- Only call endpoints that exist in contract/openapi.yaml. If one is missing,
  STOP and tell the user to run /fe-request-contract. Do not stub it, do not
  guess its shape, do not work around it.
- Only render ContentBlock types listed in contract/blocks.schema.json. An
  unknown type renders as a visible placeholder — never a crash, never silently
  dropped.
- SSE event names are exactly: token, block, tool, done, error.
- The SSE `error` event carries the INNER error object: read data.code and
  data.message, NOT data.error.code. HTTP responses use the {"error": {...}}
  wrapper; SSE does not.
- HTTP errors always look like:
  {"error": {"code": "...", "message": "...", "retryable": bool, "details": {}}}

## Every session

Start by merging main. After any code change, append to apps/web/FE_MEMORY.md
and update its STATE section, in the same turn.
```

### 6.2 Skills — `.agents/skills/`

Six skills, all with names the backend does not use.

**`.agents/skills/ship-screen/SKILL.md`**

```markdown
---
name: ship-screen
description: The complete procedure for building or finishing a screen or route in this Next.js app — data fetching, generated types, loading/empty/error states, accessibility, i18n, responsive checks and browser verification. Use whenever the task involves creating or changing any page, route or major UI component.
---

# Shipping a screen

1. Confirm every endpoint the screen needs exists in contract/openapi.yaml and
   is marked `mocked`, `live` or `done` in contract/status.md. If one is
   `planned`, tell the user and stop.
2. Import the response types from packages/api-types. Never write your own.
3. Fetch through packages/api-client, inside a TanStack Query hook in
   apps/web/hooks/. Never fetch in a component body.
4. Build the screen with primitives from packages/ui. No colour, spacing or
   font-size literals.
5. 🔴 Implement all four states, not just the happy one:
   loading (skeleton, not a spinner where content will appear),
   empty (says what to do next, not "no data"),
   error (says what went wrong and offers a real retry),
   success.
6. Every string through the i18n layer. Add keys to packages/i18n/en.json and a
   placeholder in hi.json.
7. Accessibility: keyboard reachable, visible focus, accessible names, Escape
   closes overlays, aria-live on anything that streams.
8. Run `pnpm typecheck`. Show me the output.
9. 🔴 Use /browser to open the route, screenshot it at 360px and at 1280px, in
   light and dark mode, and report anything that overflows, overlaps or is
   unreadable. Fix what you find, then screenshot again.
10. Update contract/status.md if you moved an endpoint from mocked to live, and
    append to apps/web/FE_MEMORY.md.
11. Tell me the URL to open so I can look at it myself.
```

**`.agents/skills/block-renderer/SKILL.md`**

```markdown
---
name: block-renderer
description: How to build and modify ContentBlock renderers — the components that turn the backend's lesson JSON into teaching material. Covers the twelve frozen block types, the discriminated union, unknown-type handling and profile-driven behaviour. Use when working on anything under components/blocks or when a lesson does not render correctly.
---

# ContentBlock renderers

Read contract/blocks.schema.json first. It is the contract. The backend
validates against the same file.

## The twelve types — frozen

heading, text, list, code, math, callout, example, analogy, step,
quiz_inline, image_prompt, divider

callout variants: info, tip, warning, misconception, ai_notice
🔴 Five distinct visual treatments. misconception must NOT reuse the warning
token — they mean different things and must be tellable apart. ai_notice is the
AI-generated disclaimer, quiet and dismissible, once per lesson.

## Rules

- One component per type, in apps/web/components/blocks/.
- A single BlockRenderer switches on block.type.
- 🔴 The default branch renders UnknownBlock — a small visible placeholder
  naming the unknown type. NEVER crash. NEVER silently drop it. A block type the
  backend adds before you support it must degrade, not disappear.
- Types come from packages/api-types. Model the union as a discriminated union
  on `type` so an invalid block cannot type-check.
- Blocks are pure presentational components. No data fetching inside them.

## Profile-driven behaviour

- example: steps collapsed for guided_discovery learners, expanded for
  worked_examples. Reveal one at a time. Each reveal emits a hint_requested
  signal with the block_id.
- step: reveal:true shows a "Show me" button instead of the text. Pressing it
  emits hint_requested with the block_id.
- quiz_inline: answer inline, immediate feedback, NOT scored. Emits
  inline_check_failed WITH the block_id on a wrong answer — never `retry`,
  which means a scored checkpoint item was retried.
- code: copy button, language label, no execution.
- math: KaTeX. display:true centres on its own line.

## Verification

apps/web/app/debug/blocks/page.tsx renders one of every type plus one unknown
type from a local fixture. 🔴 Required by Rules.md section 10. After any change
here, /browser that page and screenshot it in both themes.
```

**`.agents/skills/api-integration/SKILL.md`**

```markdown
---
name: api-integration
description: How this app talks to the FastAPI backend — generated types, the api-client wrapper, Supabase auth headers, the error envelope, TanStack Query patterns, async job polling and the Prism mock server. Use whenever adding a data-fetching hook, handling an API error, or switching between mock and live backend.
---

# Talking to the backend

## Types are generated, never written

pnpm gen:types  →  openapi-typescript contract/openapi.yaml -o packages/api-types/index.ts

Run it after every `git merge main` that touched contract/. Compile errors
afterwards are the contract change surfacing — fix them, never suppress them.
🔴 A hand-written interface for an API response is a bug.

## One client

packages/api-client owns: the base URL from NEXT_PUBLIC_API_BASE, the
Authorization header read from the live Supabase session, ONE
refresh-and-retry on 401, error-envelope parsing, and typed responses.
🔴 No component calls fetch directly. Ever.

## Errors

HTTP errors are always {"error": {code, message, retryable, details}}.
The client throws a typed ApiError carrying those fields. Screens show
error.message — it is written to be safe to show a learner — plus a retry when
retryable is true.
🔴 SSE is different: the `error` EVENT carries the inner object directly. Read
data.code and data.message, not data.error.code.

## Auth

supabase-js owns the session. Read the access token from it before each
request. Never store or refresh tokens yourself.
🔴 Call GET /me once immediately after login — it creates the learner row.

## Async jobs

Plan generation returns 202 {job_id}. Poll GET /jobs/{id} with TanStack Query's
refetchInterval at 1.5s. Render the backend's real progress and
progress_message — never invent your own. Cap the poll at 180 seconds, then
show a timeout with a working retry.

## Mock vs live

NEXT_PUBLIC_API_BASE is the only switch.
  mock:  http://localhost:4010/api/v1   (npx @stoplight/prism-cli mock contract/openapi.yaml --port 4010)
  live:  http://localhost:8000/api/v1
🔴 No --dynamic flag on Prism — it ignores the committed examples and serves
random junk.
🔴 No `if (mock)` branches in component code. No fixture data imported into a
screen. The env var is the entire mechanism.
```

**`.agents/skills/sse-consumer/SKILL.md`**

```markdown
---
name: sse-consumer
description: How to consume the backend's Server-Sent Event streams for lesson content, reexplain and tutor chat — event names, parsing, termination, heartbeats, idle timeouts and cancellation. Use when building or debugging any streaming UI, or when a stream hangs, arrives all at once, or never finishes.
---

# Consuming SSE

Read contract/events.md. Three endpoints stream:
  GET  /lessons/{id}/content     block events
  POST /lessons/{id}/reexplain   block events
  POST /tutor/messages           token events, plus block for code and maths

## 🔴 Use fetch + ReadableStream, never EventSource

EventSource is GET-only AND cannot send an Authorization header. All three
endpoints are authenticated. One transport, one auth path.

## The five events — nothing else exists

token  {"text": "..."}                     append to the in-flight chat message
block  {id, type, concept_id, ...}         a COMPLETE renderable ContentBlock
tool   {"name": "...", "status": "..."}    subtle thinking affordance, non-blocking
done   {message_id, block_count, usage}    finalise, stop the spinner
error  {code, message, retryable, details} 🔴 INNER object, no wrapper

## Hard rules

- Render blocks as they arrive. Never buffer until `done` — perceived speed is
  the point.
- 🔴 Always handle a stream that ends WITHOUT a terminal event. Treat 30s of
  silence as an error. A spinner that never stops is the worst demo failure
  there is.
- 🔴 Reset the idle timer on ANY bytes received, including the backend's
  `: ping` comment heartbeats every 15s. A timer driven only by parsed events
  fires spuriously while the model is still thinking about the first block.
- Auto-scroll ONLY when the user is already at the bottom. Yanking the viewport
  away from someone who scrolled up is infuriating.
- Abort the stream on unmount with an AbortController. A leaked stream costs
  real tokens and causes ghost updates.
- Parse incrementally: keep a text buffer, split on "\n\n", handle partial
  events left at the end of a chunk. Do not assume one chunk is one event.

## Sharing with mobile

Put the PARSING in a pure function over a text buffer, in packages/api-client,
so React Native can reuse it. Do NOT share the transport — React Native's fetch
does not expose a streaming body. See mobile-parity.
```

**`.agents/skills/mobile-parity/SKILL.md`**

```markdown
---
name: mobile-parity
description: What the Expo mobile app must share with the web app and what it must not, including the streaming transport problem, secure session storage and native block renderers. Use when building anything under apps/mobile or deciding whether code can be shared between web and native.
---

# Web and mobile

## Scope — Phase 5 only, and deliberately small

Login, home ("continue this lesson"), lesson reading, tutor chat, progress.
NOT on mobile in v1: the diagnostic, goal entry, plan generation, settings,
accepting or declining an adaptation. Those live on web. Mobile is where you
CONTINUE, not where you SET UP.

## Share

- packages/api-types (generated types)
- packages/api-client (the fetch wrapper and the SSE PARSER)
- packages/i18n (translation keys)
- The ContentBlock type union and the decision logic about how to render it

## Do NOT share

React components. Web and native primitives are different enough that the
abstraction costs more than it saves at this scale. Write native block
renderers in apps/mobile/components/blocks/ mirroring the web ones one-for-one.

## 🔴 The streaming problem — decide before Phase 5 starts

React Native's fetch does not expose a streaming response.body, and managed
Expo rules out the usual polyfills. Two options, in order of preference:

1. XHR onprogress SSE parser — XMLHttpRequest exposes responseText
   incrementally in RN. Parse the delta on each progress event with the SAME
   pure parser the web uses. Keeps streaming, works in managed Expo.
2. Non-streaming fallback — ?stream=false on endpoints 19, 19b and 21.
   🔴 That is a CONTRACT CHANGE: run /fe-request-contract and get a written ack
   before building against it.

## Session storage

supabase-js with expo-secure-store as the storage adapter. Never AsyncStorage.
⚠️ SecureStore caps values at roughly 2KB on Android and a full Supabase
session can exceed it. Write a chunking adapter that splits across numbered
keys. Decide this when you write the client, not when logins start failing on
one device.

## Managed Expo only

If a library requires a prebuild or a custom dev client, find another library.
You do not have time for a native build pipeline.
```

**`.agents/skills/frontend-memory/SKILL.md`**

```markdown
---
name: frontend-memory
description: How to update apps/web/FE_MEMORY.md and apps/web/FE_PHASE.md after any change so the next session has accurate context. Use at the end of every task that changed code, and whenever asked what has been built or what is next.
---

# Keeping FE_MEMORY.md and FE_PHASE.md true

Do this in the SAME turn as the code change. Never "later". A stale memory file
is worse than none, because the next session trusts it.

## apps/web/FE_MEMORY.md

STATE — rewrite in place:
- Screens table: route, phase, built?, verified in browser?, notes
- Endpoints consumed: path, against mock or live, working?
- Block renderers: which of the twelve are done and browser-checked
- Environment variables in use (names only, never values)
- Known broken / half-finished — brutal honesty; this section is the point
- Do not touch — things that work and are fragile, with a reason

CHANGELOG — append at the TOP, never edit a past entry:

### [YYYY-MM-DD HH:MM] type(scope): summary
- Added: <files, routes, components>
- Changed: <what and why>
- Contract: <did you regenerate types? which CHANGELOG entry?>
- Verified: <what you actually opened in a browser, at what widths, which themes>
- Broken/left undone: <always present, even if "nothing">
- Next: <the next session starts here>

## apps/web/FE_PHASE.md

Your own phase tracker. The backend has its own Phase.md on its branch; you
cannot see it and must not create one. Phase NAMES and NUMBERS come from
Project_requirement.md section 7 and must match exactly.

- Exactly one phase marked ⬅ CURRENT
- Tick the task you just finished
- A phase is complete only when every exit criterion in
  Frontend_Instructions.md section 13 is ticked AND FE_MEMORY.md reflects it
- Work you discover that belongs to a later phase goes in that phase's queue,
  not into today

## The test

Hand FE_MEMORY.md to someone who has never seen this repo. If they cannot say
what works and what does not in two minutes, it has failed.
```

### 6.3 Workflows — `.agents/workflows/`

**`.agents/workflows/fe-phase-check.md`** → `/fe-phase-check`

```markdown
# Frontend phase check

Verify the current phase honestly and report. Fix nothing.

1. Read apps/web/FE_PHASE.md for the CURRENT phase, and
   Frontend_Instructions.md section 13 for its exit criteria.
2. Verify each criterion by actually doing something — running a build, opening
   a route with /browser, screenshotting it — not by reading code and assuming.
3. Run `pnpm typecheck` and `pnpm build`. Paste the real output.
4. Run `pnpm gen:types` and report whether packages/api-types changed. If it
   did, the committed types were stale.
5. For every screen in this phase, /browser it at 360px and 1280px, light and
   dark, and report anything broken.
6. Produce a table: criterion | verified how | PASS or FAIL.
7. If all pass, mark the phase complete in FE_PHASE.md and move ⬅ CURRENT.
8. Update FE_MEMORY.md STATE.
```

**`.agents/workflows/fe-verify-me.md`** → `/fe-verify-me`

```markdown
# Verify the last change

You just made a change. Prove it works.

1. State what you changed, in one sentence.
2. Run `pnpm typecheck`. Paste the real output.
3. /browser the affected route. Screenshot it at 360px and 1280px, light and
   dark. Show me the screenshots.
4. Read the browser console and report every error and React warning.
5. Tab through the screen with the keyboard and report anything unreachable or
   without a visible focus ring.
6. List what you did NOT verify, and why.
7. List anything you touched that the task did not require.
8. If any step failed, say so plainly and stop. Do not fix it in this workflow.
```

**`.agents/workflows/fe-request-contract.md`** → `/fe-request-contract`

```markdown
# Request a contract change from the backend

You need something the API does not provide. You must NOT invent it.

1. State exactly what is missing: the endpoint, field or block type, and what
   screen needs it.
2. Show the shape you need, as JSON.
3. Classify it: ADDITIVE (new optional field, new endpoint) or BREAKING
   (rename, removal, type change, new required field).
4. Append to contract/CHANGELOG.md under `## Proposed`, with today's date, the
   classification, the requested shape, and a blank ack line. Remember
   contract/CHANGELOG.md is edited on main — tell the user the exact git
   commands if they are on the frontend branch.
5. Tell the user to message the backend developer in words, not just commit.
6. 🔴 STOP. Do not stub the endpoint, do not mock it locally, do not guess its
   shape. Suggest what else in the current phase can be built meanwhile.
```

### 6.4 MCP — `.agents/mcp_config.json`

You mostly do not need MCP. If you want the agent to read live docs, the browser
subagent (`/browser`) already covers it. Skip MCP unless something specific
demands it — the file is gitignored either way, so it never affects the merge.

---

## 7. Running the real backend on your machine

Do this from Phase 1 onward. 🔴 **Do not live on the mock for six weeks.** The
mock tells you your code compiles; only the real backend tells you it works.

```bash
# in a SEPARATE folder, so your frontend checkout is undisturbed
git clone <repo-url> sarathi-backend
cd sarathi-backend && git checkout backend
cp .env.example .env && $EDITOR .env      # Disha gives you the values
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.seed_demo
curl -s localhost:8000/health             # {"status":"ok","db":"ok",...}
```

Then `apps/web/.env.local`:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://<ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key>
```

Interactive API docs: **`http://localhost:8000/docs`**. That page is the fastest
way to see the real shape of any response. Use it constantly.

Need a token without a Supabase account:

```bash
curl -s -XPOST localhost:8000/dev/auth/token \
  -H 'content-type: application/json' -d '{"email":"demo@sarathi.app"}' | jq -r .access_token
```

---

## 8. How to write a prompt that works

Six parts. `Antigravity_Prompts_Frontend.md` is written this way.

```
1. ANCHOR    "Read FE_PHASE.md, FE_MEMORY.md and contract/status.md first."
2. TASK      One deliverable. Not "build the lesson page" — "build the block
             renderer for `example`".
3. BOUNDS    "You may only create or edit these files: ..."
4. CONTRACT  Paste the exact type, endpoint row or block schema.
5. VERIFY    "Then /browser it at 360px and 1280px and show me screenshots."
6. GATE      "Produce an implementation plan first. Do not write code yet."
```

**Do**

- One screen or one component per prompt.
- Paste the generated type rather than describing it.
- Always ask for a browser screenshot. It is the frontend equivalent of running
  the tests, and it is the single biggest advantage you have.
- Ask for all four states — loading, empty, error, success — explicitly, every
  time. Agents default to success-only.
- Say "if anything is ambiguous, ask me before writing code."

**Do not**

- Do not say "build the dashboard." You will get 600 lines you cannot review.
- Do not accept a plan you have not read.
- Do not say "also make it look nicer." Unbounded aesthetic instructions produce
  gradient blobs.
- Do not let it hand-write an API type. Ever.
- Do not accept "it should work" — open it.

**When it goes wrong.** After two failed attempts: switch model (Pro, then
Claude Sonnet 4.6), or `git stash` and re-prompt with a narrower task, or run
`/grill-me` to find the assumption you never stated. A third louder attempt
never works.

**End every phase with `/learn`.** It converts this phase's corrections into a
permanent rule, so the next phase does not repeat them.

---

## 9. The phases

Full prompts in `Antigravity_Prompts_Frontend.md`. Exit criteria in
`Frontend_Instructions.md` §13. Phase numbers and names match
`Project_requirement.md` §7 exactly — the backend uses the same ones.

### Phase 0 — Contract & skeleton · 5–6 h · F0.1–F0.9

**Building:** the monorepo, design tokens, i18n, the api-client, the Supabase
client, the Prism mock — and **all twelve block renderers**.

🔴 Phase 0 is not "setup". The block renderers are the deepest work in the whole
project and they depend on nothing but `contract/blocks.schema.json`. Build them
while the backend is still writing migrations.

**Verify:**

```bash
pnpm install && pnpm typecheck && pnpm build
pnpm dev                       # localhost:3000
npx @stoplight/prism-cli mock contract/openapi.yaml --port 4010
```

Then open `/debug/blocks`. You should see one of every block type plus a visible
"unknown block type" placeholder. Screenshot it in light and dark.

**Exit criteria** — `Frontend_Instructions.md` §13, Phase 0.

**Usually goes wrong:** `UnknownBlock` gets skipped because "the backend won't
send unknown types." It will, the first time it adds one, and a silent drop is
almost impossible to notice. Also: tokens defined but components still using
`text-gray-500` — grep for colour literals before you call Phase 0 done.

---

### Phase 1 — Identity & diagnostic · 7–9 h · F1.1–F1.8

**Building:** Supabase auth, session provider, route protection, login and
register, the diagnostic flow, the profile screen.

**Verify with the REAL backend** (§7), not the mock:

- Register a new account → you land on the diagnostic
- Reload mid-diagnostic → you resume on the same question, answers intact
- Complete it → the profile page shows plain-language sentences, not raw enum values
- Change a dimension → `profile_version` increments
- Delete your cookies → you are bounced to `/login`, not shown a broken page

🔴 **IC-1 happens at the end of this phase** — `Integration_Guide.md` §6.

**Usually goes wrong:** calling `GET /me` too late, so every subsequent request
404s. Call it once, immediately after login, before routing anywhere. And
mapping Supabase's raw error strings straight into the UI — "AuthApiError:
Invalid login credentials" is not something you show a student.

---

### Phase 2 — Goal → Plan · 7–9 h · F2.1–F2.7

**Building:** the goal screen with voice input, the interpretation confirmation,
the job-polling generating screen, the plan view, and `/debug/profile`.

**Verify:** type a real goal, watch the generating screen show the backend's
actual `progress_message` strings, and read the plan's rationale.

🔴 **If the rationale reads like "this plan is tailored to your learning style",
tell the backend dev immediately.** That is a backend prompt problem, but you
will see it first, and it is the single most important string in the demo.

**Usually goes wrong:** a fake progress bar. If the backend says
"Mapping prerequisites", show that. It is more honest, more interesting, and it
makes the agent's work legible — which is the entire pitch.

Also: routing to `/plan/[id]` before the job finishes. The plan id does not
exist until `status === "succeeded"`. That is why the route is
`/plan/generating/[jobId]`.

---

### Phase 3 — Lesson & checkpoint · 11–13 h · F3.1–F3.9

The biggest phase, and the one with the hardest bug class. Do not start it with
three hours free.

**Building:** the `useStream` hook, the lesson screen, "I'm lost", the tutor
drawer, checkpoints, the dashboard, signal batching.

**Verify — with `curl` first, then the browser:**

```bash
curl -N -H "Authorization: Bearer $TOKEN" \
  localhost:8000/api/v1/lessons/<id>/content
```

See `event: block` lines arriving progressively and exactly one `event: done`.
**Only then** open it in the app. If curl streams and your UI does not, the bug
is yours. If curl does not stream, it is the backend's.

Then, in the browser:

- Blocks appear one by one, not all at the end
- Scroll up mid-stream — the view must not yank you back down
- Kill the backend mid-stream → you see an error and a retry, not a spinner
- Open the Network tab and confirm the response is streaming, not buffered
- Press "I'm lost" → a genuinely different explanation
- 🔴 Flip `representation_pref` in `/debug/profile` and reload → the first block
  should be a different **type**. If it is not, tell the backend dev — the
  personalisation is not real yet.

🔴 **IC-3 happens at the end of this phase.** It is where projects like this
die. Do it on schedule.

**Usually goes wrong:** assuming one network chunk equals one SSE event. It does
not. Buffer the text, split on `\n\n`, and keep the partial remainder. Also:
the idle timeout firing during a long first-block wait because the timer ignores
`: ping` heartbeats.

---

### Phase 4 — Adaptation loop · 6–8 h · F4.1–F4.5

🔴 **This phase is the project.** Everything before it is table stakes.

**Building:** the adaptation modal — the money screen — the `/adaptations` page,
the dashboard panel, and settings.

**Verify:** deliberately fail a checkpoint, and watch. The modal must show what
changed, the `reason`, the `timeline_impact`, and a real before/after diff of the
plan. Accept it and watch the plan visibly change.

🔴 **Spend your design effort here, not on the landing page.** This one screen
is what the judges remember. Give the before/after diff real thought: a plain
list of changes is fine, a visual diff that makes the inserted lesson obvious is
much better.

**Usually goes wrong:** the modal appearing over the thing it is describing.
Show the plan and the change together. And treating decline as a no-op — record
it, and do not re-prompt immediately. A tutor that nags is a tutor people close.

---

### Phase 5 — Mobile companion · 7–9 h · F5.1–F5.5

**Building:** the Expo app — login, home, lesson, chat, progress.

**Verify on a real phone over mobile data**, not your Wi-Fi. Same account, same
lesson, same progress as the web app within five seconds.

**Usually goes wrong:** the streaming transport (see `mobile-parity`). Decide it
in F5.1, not F5.4. And SecureStore silently failing to store an oversized
session — test login, force-quit the app, reopen, and confirm you are still
logged in.

---

### Phase 6 — Polish & demo hardening · 7–9 h · F6.1–F6.6

**Building:** the states sweep, accessibility, dark mode, the landing page,
offline fallback, and the adversarial review.

**Exit criteria**

- [ ] Every screen on the demo path has loading, empty and error states you have
      actually seen — force each one
- [ ] Keyboard-complete: tab through the whole demo path without a mouse
- [ ] Screen reader announces streamed content
- [ ] Light and dark, 360px and 1280px, all clean
- [ ] Lighthouse ≥90 on performance and accessibility
- [ ] 🔴 The full demo path works against the backend in `DEMO_MODE` with the
      **Wi-Fi physically off**
- [ ] Three timed rehearsals on the demo laptop

---

## 10. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `pnpm gen:types` produces an empty file | `contract/openapi.yaml` missing or stale | `git merge main`, check the file exists |
| Types do not match the real API | You did not regenerate after a contract sync | `pnpm gen:types`, fix the compile errors |
| Every API call is 401 | No token, or you did not call `GET /me` after login | Check the Authorization header in the Network tab |
| Every API call is 404 after login | The learner row was never created | Call `GET /me` once, immediately after login |
| CORS error | The backend's `CORS_ORIGINS` does not list your origin | Ask Disha to add `http://localhost:3000` |
| SSE arrives all at once at the end | You are reading `response.text()` instead of streaming, or a proxy is buffering | Use `getReader()`; confirm with `curl -N` |
| Stream hangs forever | No terminal event handling, or the idle timer ignores heartbeats | Handle a missing `done`; reset the timer on any bytes |
| `data.error.code` is undefined on an SSE error | SSE carries the inner object | Read `data.code` |
| Hydration mismatch in Next.js | A client-only value (date, random, `window`) rendered on the server | Move it into `useEffect` or a client component |
| Expo app cannot reach `localhost:8000` | The phone has its own localhost | Use your machine's LAN IP, e.g. `http://192.168.1.5:8000` |
| Login lost on app restart | SecureStore value too large | Chunking adapter — see `mobile-parity` |
| Antigravity rewrote a working component | The prompt did not bound the files | `git checkout` that file; re-prompt with an explicit list |
| Merge conflict with the backend branch | You created a file you do not own | `Integration_Guide.md` §2 and §10 |

---

## 11. The five things that will actually decide this

1. **Open it in a browser after every change.** Use `/browser`. A frontend you
   have not looked at is a frontend that does not work.
2. **Never hand-write an API type.** Generated types turn a backend change into
   a compile error instead of a demo failure.
3. **Run against the real backend from Phase 1.** The mock proves your code
   compiles; only the real API proves it works.
4. **Phase 4 is the project.** The adaptation modal is what judges remember.
   A polished landing page with no adaptation loses to a plain one that adapts.
5. **Merge `main` every day.** Integration pain compounds; six weeks of drift
   cannot be resolved in one night.

---

*Companions: `Antigravity_Prompts_Frontend.md`, `Integration_Guide.md`, `Frontend_Instructions.md`.*
*Last updated: 2026-08-29 · Owner: Disha (Team Lead)*
