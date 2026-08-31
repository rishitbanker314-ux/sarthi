# Frontend_Instructions.md

> **For the Frontend Developer and the AI agent building the frontend.**
> Prerequisite reading, in order: `Integration_Guide.md` → `Context.md` →
> `Rules.md` → `Project_requirement.md` → this file → `apps/web/FE_PHASE.md`
> (holds your ⬅ CURRENT marker) → `contract/status.md`.
>
> 🔴 **You work on the `frontend` branch**, cut from `main`. The backend's
> `Phase.md` and `Memory.md` live on its own branch and you cannot see them —
> you keep `apps/web/FE_PHASE.md` and `apps/web/FE_MEMORY.md` instead. Never
> create a root `Phase.md` or `Memory.md`; that is a merge conflict.
> `Integration_Guide.md` §2 is the full path-ownership map.
>
> **Step-by-step build:** `Frontend_Roadmap.md` (what to do and how to verify)
> and `Antigravity_Prompts_Frontend.md` (every prompt, in order).
>
> **You are never blocked on the backend.** From hour one you build against a
> mock server generated from the same contract. If you ever find yourself
> waiting, you have misunderstood the workflow — re-read §4.

---

## 1. Your job in one paragraph

Build a Next.js web app and an Expo mobile companion that make an invisible
adaptive system *visible*. The hardest and most valuable thing you will build is
not a screen — it is the `ContentBlock` renderer and the moments where the
system explains its own reasoning to the learner. Judges cannot see a Planner
agent. They can see a plan rewriting itself with a readable reason. That is
yours.

---

## 2. Ownership 🔴

**You own** (and these are the *only* paths on your branch — see
`Integration_Guide.md` §2.3): `apps/web/`, `apps/mobile/`, `packages/ui/`,
**`packages/api-client/`**, `packages/i18n/`, the root Node config
(`package.json`, `pnpm-workspace.yaml`, `turbo.json`, `.npmrc`, `.nvmrc`), and
your own tracking files `apps/web/FE_MEMORY.md` and `apps/web/FE_PHASE.md`.

🔴 **Never create** a root `Dockerfile`, `docker-compose.yml`, `.env.example`,
`tests/`, `scripts/`, `Phase.md` or `Memory.md`, and never edit `.gitignore` —
every one of those belongs to the backend branch or to `main`, and creating it
guarantees a merge conflict.

**You never edit:** `services/**`, `migrations/**`, `fixtures/**`,
`contract/openapi.yaml`, `packages/api-types/**` (generated), `Context.md`,
`Rules.md`, `Project_requirement.md`, `Backend_Instructions.md`,
**`Frontend_Instructions.md` (this file)**, `Architecture.md`, `Memory.md`,
`Phase.md`.

**You may write to** (protocol-gated, see `Context.md` §7.4):
`contract/status.md`, `contract/CHANGELOG.md`.

If an API is wrong, you report it in `contract/CHANGELOG.md`. You do not work
around it with a client-side patch — a workaround hides the bug until the demo.

---

## 3. Stack — locked, do not substitute

| Layer | Choice | Notes |
|---|---|---|
| Web framework | **Next.js 14+ (App Router)** | TypeScript, `strict: true` |
| Mobile | **Expo (SDK 51+) + React Native** | Managed workflow. 🔴 No custom dev client — a prebuild is hours you do not have |
| Mobile routing | **Expo Router** | Mirrors App Router mental model |
| Styling (web) | **Tailwind CSS** + CSS variables for tokens | |
| Styling (mobile) | **NativeWind** | Same class names as web where possible |
| Components (web) | **shadcn/ui** (Radix under the hood) | Accessible by default. Copy in, do not wrap a second library around it |
| State (server) | **TanStack Query** | Caching, polling, retries — do not hand-roll |
| State (client) | **Zustand** | Only for genuinely global UI state |
| Forms | **react-hook-form** + **zod** | |
| Markdown | **react-markdown** + **remark-gfm** | Sanitised. Never `dangerouslySetInnerHTML` |
| Math | **KaTeX** | |
| Code blocks | **Shiki** (web) / **highlight.js** (mobile) | |
| Charts | **Recharts** | Mastery map only |
| i18n | **next-intl** (web) / **i18n-js** (mobile) | 🔴 From commit one |
| API types | **`openapi-typescript`** | 🔴 Generated. Never hand-written |
| Mock server | **`@stoplight/prism-cli`** | Your lifeline. See §4 |
| Auth | **`@supabase/supabase-js`** | 🔴 Sign-up, sign-in, refresh and password reset happen client-side against Supabase. The backend has **no** `/auth/*` endpoints — see §3.1. |
| Monorepo | **pnpm workspaces** + **Turborepo** | |
| Tests | **Vitest** + **Testing Library** | |

---

## 3.1 🔴 Authentication — you own it now

Changed 2026-08-29 (`contract/CHANGELOG.md`). The backend has **no**
`/auth/register`, `/auth/login` or `/auth/refresh`. Sign-up and sign-in happen
client-side against Supabase.

```ts
// packages/api-client/supabase.ts
import { createClient } from "@supabase/supabase-js"
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
)
```

The flow:

1. `supabase.auth.signUp()` / `signInWithPassword()` on `/register` and `/login`.
2. `supabase-js` stores the session and refreshes the token on its own — 🔴 do
   not write your own refresh logic.
3. `packages/api-client` reads the current session before each request and sets
   `Authorization: Bearer <access_token>`. One place, as always.
4. 🔴 Call `GET /me` once immediately after login — that is what creates the
   learner's row in the backend. Everything else 404s until you do.
5. On a 401 from the API, call `supabase.auth.refreshSession()` once and retry;
   if that fails, sign out and route to `/login`.

🔴 **Only the anon key ever reaches the browser.** If anyone hands you a
`service_role` key, refuse it — it bypasses every access rule in the database.

For mobile: the same `supabase-js` client, with `expo-secure-store` as the
session storage adapter. Never `AsyncStorage`.

⚠️ **SecureStore has a size ceiling** (~2 KB per value on Android) and a full
Supabase session — access token, refresh token and user object — can exceed it.
Write a small chunking adapter that splits the value across numbered keys, or
store only the refresh token securely and keep the rest in memory. Decide this
in Phase 0 when you write the client, not in Phase 5 when logins start failing
on one device and not the other.

---

## 4. 🔴 Mock-first workflow — the most important section

### 4.1 Setup

```bash
# Backend commits contract/openapi.yaml in Phase 0.
npx @stoplight/prism-cli mock contract/openapi.yaml --port 4010
```

🔴 **No `--dynamic`.** It generates random values and ignores the `example`
blocks the backend commits — you would build every renderer against noise.

```bash
# apps/web/.env.local
NEXT_PUBLIC_API_BASE=http://localhost:4010/api/v1   # ← flip to :8000 when live
```

**One env var moves the entire app between mock and real backend.** There is no
other switch, no `if (mock)` in component code, no mock data imported into a
screen. If you find yourself writing `const FAKE_PLAN = {...}` inside a
component, stop — that is exactly the thing that ends up in the demo.

### 4.2 Types are generated, never written

```bash
pnpm gen:types   # openapi-typescript contract/openapi.yaml -o packages/api-types/index.ts
```

Run this every time `contract/CHANGELOG.md` gains a merged entry. 🔴 A
hand-written interface describing an API response is a bug (`Context.md` §7.2;
`Rules.md` §1 forbids editing the generated output). It will drift silently and
you will discover it during the demo.

### 4.3 One API client, one place

`packages/api-client/` wraps `fetch` and handles: base URL, the auth header
(read from the live Supabase session — see §3.1), one refresh-and-retry on 401,
the standard error envelope, and typed responses. 🔴 No component calls `fetch`
directly. Ever.

### 4.4 Reading `contract/status.md`

| Marking | What you do |
|---|---|
| `planned` | Do not build the screen yet |
| `mocked` | Build the full screen against Prism |
| `live` | Point at the real backend, verify, report anything that differs |
| `done` | Tested both sides. Move on. |

### 4.5 When you need something the contract does not have

1. Add a `## Proposed` entry to `contract/CHANGELOG.md` describing the endpoint
   or field and why.
2. Tell the backend dev in words.
3. **Keep building something else.** Do not stub it locally, do not invent the
   shape, do not "assume it'll be `{data: [...]}`".

---

## 5. Repository layout

```
apps/
├── web/
│   ├── app/                      # App Router
│   ├── components/
│   │   ├── blocks/               # ← ContentBlock renderers. The core.
│   │   ├── plan/
│   │   ├── lesson/
│   │   ├── diagnostic/
│   │   └── adaptation/
│   ├── hooks/
│   └── lib/
└── mobile/
    ├── app/                      # Expo Router
    └── components/blocks/        # native renderers, same block types
packages/
├── ui/                           # shared tokens, primitives
├── api-client/                   # the only place fetch lives
├── api-types/                    # 🔴 GENERATED — never edit
└── i18n/                         # shared translation keys
```

---

## 6. Screen inventory — web

Build in phase order. 🔴 = on the demo path; must be flawless.

| # | Route | Phase | What it does |
|---|---|---|---|
| 1 | `/` | **6** | Landing. One sentence, one CTA, one 20-second explainer of the loop. Judges see this first — but it is the *last* thing you build. A stub `<h1>` + login link is enough until Phase 6. |
| 2 | `/login`, `/register` | 1 | 🔴 Email + password **via `supabase-js`, not your API** (§3.1). Inline errors, mapped from Supabase's error codes to friendly copy. Then call `GET /me` once. |
| 3 | `/onboarding/diagnostic` | 1 | 🔴 One question per screen, progress indicator, back button, resume on reload. Must feel like a conversation, not a form. |
| 4 | `/onboarding/profile` | 1 | 🔴 Profile in **plain language** — "You learn best when you see an example first." Every dimension editable. |
| 5 | `/goal` | 2 | 🔴 Large free-text input + voice button. On submit, shows the parsed interpretation; editable via `PATCH /goals/{id}` before planning. |
| 6 | `/plan/generating/[jobId]` | 2 | 🔴 Real progress from `GET /jobs/{id}`. Note the route key is the **job** id — the plan id does not exist until the job succeeds. Show the actual `progress_message`. **This screen is on camera for 60 seconds — make it interesting**, e.g. reveal the reasoning steps as they complete. |
| 7 | `/plan/[id]` | 2 | 🔴 Modules → lessons, status, estimates, mastery pips. Rationale visible, not hidden behind a tooltip. |
| 8 | `/lesson/[id]` | 3 | 🔴 The core screen. Streamed blocks, progress rail, tutor drawer, a **skip-ahead control** (emits `skip` with the `block_id` skipped from), and the "I'm lost" button → `POST /lessons/{id}/reexplain` (endpoint 19b, also SSE). 🔴 Do **not** also POST `confusion_flag` — 19b writes it server-side (`Context.md` §5). Renders the `ai_notice` callout once per lesson (`Rules.md` §6). |
| 9 | Tutor drawer | 3 | 🔴 Side panel on web, sheet on mobile. Streams tokens. Never covers the content it discusses. |
| 10 | `/lesson/[id]/checkpoint` | 3 | 🔴 3–5 items, per-item feedback, mastery delta animation. |
| 11 | `/dashboard` | 3 | 🔴 Continue-lesson card, plan progress, mastery map, activity summary. *(No adaptations panel yet — `GET /adaptations` is Phase 4.)* |
| 11b | `/dashboard` — adaptations panel | 4 | 🔴 Recent `AdaptationEvent`s added to the dashboard once endpoint 29 is live. |
| 12 | `/adaptations` + inline modal | 4 | 🔴 **The money screen.** "Your plan changed" → what changed, why (`reason`), `timeline_impact`, Accept / Keep as is → `POST /adaptations/{id}/respond`. Diff-style before/after. |
| 13 | `/settings` | 4 | UI language (`users.locale`) **and** explanation language (`learner_profiles.language`) — two separate controls. Accessibility toggles, session length, data export, delete account. |
| 14 | `/debug/profile` | 2 | Dev-only. Switch any profile dimension and reload the lesson. This is how you prove `Project_requirement.md` §6 to a judge in ten seconds. Build it early — you will use it constantly. |
| 15 | `/debug/blocks` | 0 | Dev-only. Renders one of every `ContentBlock` type plus one unknown type from a local fixture. 🔴 Required by `Rules.md` §10. Your first real screen. |

---

## 7. 🔴 The ContentBlock renderer — build this first

This is the highest-leverage thing you own. Build it in **Phase 0**, from
`contract/blocks.schema.json`, before any lesson endpoint exists.

```tsx
// components/blocks/BlockRenderer.tsx
export function BlockRenderer({ block }: { block: ContentBlock }) {
  switch (block.type) {
    case "heading":      return <HeadingBlock {...block} />
    case "text":         return <TextBlock {...block} />
    case "list":         return <ListBlock {...block} />
    case "code":         return <CodeBlock {...block} />
    case "math":         return <MathBlock {...block} />
    case "callout":      return <CalloutBlock {...block} />
    case "example":      return <ExampleBlock {...block} />
    case "analogy":      return <AnalogyBlock {...block} />
    case "step":         return <StepBlock {...block} />
    case "quiz_inline":  return <InlineQuizBlock {...block} />
    case "image_prompt": return <ImagePromptBlock {...block} />
    case "divider":      return <Divider />
    default:             return <UnknownBlock type={(block as any).type} />
  }
}
```

🔴 **`UnknownBlock` is mandatory.** A block type the backend adds before you
support it must render as a small visible placeholder — never crash, never
silently vanish. Silent dropping is worse than an ugly box: you will not notice
until content is missing on stage.

**Behaviour per block:**

- `example` — steps collapsed by default for `guided_discovery` learners,
  expanded for `worked_examples`. Reveal one at a time. 🔴 Each reveal emits a
  `hint_requested` signal with the `block_id`, same as `step`.
- `step` — `reveal: true` means show a "Show me" button rather than the text.
  🔴 Pressing it emits a `hint_requested` signal with the `block_id`.
- `quiz_inline` — answer inline, immediate feedback, **not** scored. 🔴 Emits
  `inline_check_failed` **with the `block_id`** on a wrong answer, and **never**
  `retry` — `retry` means a scored checkpoint item was retried. Neither is
  wired to a trigger in v1, but they feed the pre/post mastery metric
  (`Project_requirement.md` §9) and would be wired to different things later.
  Keep them distinct (`Context.md` §5).
- `callout` — five variants, five distinct visual treatments:
  `info`, `tip`, `warning`, `misconception`, `ai_notice`.
  🔴 `misconception` must **not** reuse the `warning` token — they are different
  ideas and must be tellable apart. `misconception` is the most pedagogically
  valuable block in the set; give it real design attention. `ai_notice` is the
  AI-generated disclaimer required by `Rules.md` §6 — quiet, dismissible,
  appears once per lesson.
- `code` — copy button, language label, no execution in v1.
- `math` — KaTeX; `display: true` centres on its own line.

**Storybook-style test page:** `/debug/blocks` renders one of every block type
plus one unknown type, from a local fixture. 🔴 Required by `Rules.md` §10.

---

## 8. 🔴 Consuming SSE

Endpoints 19 (`/lessons/{id}/content`), 19b (`/lessons/{id}/reexplain`) and 21
(`/tutor/messages`) stream. Events are frozen in `contract/events.md`: `token`,
`block`, `tool`, `done`, `error`. Nothing else.

🔴 **Use `fetch` + `ReadableStream` for all three, never `EventSource`.**
`EventSource` is GET-only *and* cannot send an `Authorization` header, and
every one of these endpoints is authenticated (`Backend_Instructions.md` §8.1).
One streaming path, one auth path.

🔴 **The `error` event's `data` is the inner object** — read `data.code` and
`data.message`, **not** `data.error.code`. HTTP responses use the
`{"error": {...}}` wrapper; SSE does not, because the event name already says
it. This exception is recorded in `Rules.md` §2 and `Backend_Instructions.md` §8.

```ts
// hooks/useStream.ts — one hook, used by all three streaming surfaces
// - `block`  → append a complete, renderable ContentBlock
// - `token`  → append text to the in-flight assistant message (chat only)
// - `tool`   → show a subtle "thinking" affordance; do not block the UI
// - `done`   → finalise, stop the spinner
// - `error`  → show a retry affordance with the event's own `message`
//              (data.message — there is no `error` wrapper on SSE)
```

🔴 Non-negotiables:

- **Always** handle `error`, and **always** handle the stream ending without a
  `done` (treat as an error after a 30s idle timeout). A spinner that never
  stops is the worst possible demo failure. 🔴 Reset the idle timer on **any
  bytes received**, including the backend's `: ping` comment heartbeats every
  15s — a timer driven only by parsed events will fire spuriously while the
  model is still thinking about the first block.
- Render blocks as they arrive. Do not buffer until `done` — the whole point is
  perceived speed.
- Auto-scroll only while the learner is already at the bottom. Yanking the
  viewport away from someone who scrolled up is infuriating.
- Abort the stream on unmount. Leaked streams cost tokens and cause ghost
  updates.

---

## 9. Async job UX — Phase 2

Plan generation takes 20–90 seconds. This is not a loading spinner; it is a
screen.

```
POST /goals/{id}/plan  →  202 {job_id}
     ↓
route to /plan/generating/[jobId]
     ↓
poll GET /jobs/{id} every 1.5s (TanStack Query refetchInterval)
     ↓
render progress + progress_message from the response
     ↓
status "succeeded" → route to /plan/{result.plan_id}
                     (result is typed per job kind — Backend_Instructions.md §10)
status "failed"    → error state with a retry that actually re-posts
```

🔴 Show the backend's real `progress_message`, never an invented one. If the
backend says `"Mapping prerequisites"`, show that. It is honest, it is more
interesting than a bar, and it makes the agent's work legible — which is the
entire pitch.

Cap the poll at **180 seconds**, then show a timeout state with a retry. The
backend's own job deadline is 150s (`Backend_Instructions.md` §10), so the cap
sits just above it — a longer cap only makes the learner wait for nothing, and
a shorter one would report a timeout for a job that was about to succeed.

---

## 10. Design direction

The product's claim is *calm, personal, intelligent*. The UI should look like a
tutor's notebook, not a SaaS dashboard.

**Tokens live in `packages/ui/tokens.css`. Every colour and space value comes
from there. No hex codes in components.**

- **Type:** one humanist sans for UI, one serif or high-quality sans for lesson
  body at a comfortable reading measure (60–75 characters). Lesson text is the
  product — treat it like typography, not like UI chrome.
- **Colour:** restrained neutral base, one accent. Reserve semantic colour for
  meaning: mastery (sequential scale), adaptation (accent), and a **distinct
  token per callout variant** — `info`, `tip`, `warning`, `misconception`,
  `ai_notice` are five different things and must not share a colour.
  🔴 Never colour alone — always a label or icon too (`Rules.md` §8).
- **Motion:** meaningful only. Blocks fade in as they stream; mastery pips
  animate on change; adaptation diffs animate. Everything else is instant.
  🔴 All motion respects `prefers-reduced-motion`.
- **Density:** generous. This is a reading surface. Resist the urge to fill it.
- **Dark mode:** from the start via CSS variables. Retrofitting is painful and
  the demo room lighting is unpredictable.

**Anti-patterns:** gradient hero blobs · confetti · streak flames · progress
rings that measure nothing · "AI is thinking ✨" with no substance. Judges have
seen forty of those today.

---

## 11. Accessibility and i18n — non-negotiable

- 🔴 Every string through the i18n layer from the **first** commit. Namespace by
  screen. Hardcoded English is a bug. Vernacular support is a core claim of this
  project; retrofitting i18n at hour 30 is not survivable.
- 🔴 Keyboard: every action reachable, visible focus rings, logical tab order,
  Escape closes overlays.
- 🔴 Screen reader: streamed content in an `aria-live="polite"` region; every
  icon button has an accessible name; landmark regions on every page.
- 🔴 Contrast: WCAG AA. Check the mastery scale specifically — sequential
  palettes fail contrast more often than anything else.
- 🔴 Honour **all four** `accessibility` keys from the profile
  (`Context.md` §5) — the profile is authoritative, the OS media query is only
  an additional input:
  - `font_scale` — multiplies all `rem` type sizes. Use `rem`, never `px`.
  - `reduced_motion` — **ORs** with `prefers-reduced-motion`; either one
    disables motion.
  - `screen_reader` — verbose `aria-live` announcements; no purely visual
    affordances.
  - `dyslexia_font` — swaps the lesson body typeface.

---

## 12. Mobile companion — Phase 5

Scope: **login, continue, lesson, chat, progress.** That is all.

| Screen | Notes |
|---|---|
| Login | Same `supabase-js` client, with `expo-secure-store` as the session storage adapter. Never `AsyncStorage`. |
| Home | "Continue: <lesson>" card + plan progress. One primary action. |
| Lesson | Same block types, native renderers. See the streaming note below. |
| Tutor chat | Bottom sheet. |
| Progress | Mastery list. Simplified — no charts. |

❌ Not on mobile in v1: diagnostic, goal entry, plan generation, settings,
adaptation accept/decline. Those live on web. The mobile app is where you
*continue*, not where you *set up*.

🔴 Share the block **type definitions** and the API client. Do **not** try to
share React components across web and native — the abstraction costs more than
it saves at this scale.

🔴 Managed Expo only. If a library needs a prebuild, find another library.

### 🔴 Streaming on React Native — decide this before Phase 5 starts

React Native's `fetch` does **not** expose a streaming `response.body`, and
managed Expo rules out the usual polyfills. The web `useStream` hook will not
work as-is. Pick one, in this order of preference, and write the choice into
this section:

1. **XHR `onprogress` SSE parser** — `XMLHttpRequest` exposes `responseText`
   incrementally in RN. Parse the delta on each progress event with the same
   event-splitting logic as the web hook. Keeps streaming, works managed.
2. **Non-streaming fallback** — add `?stream=false` to endpoints 19, 19b and 21
   and render the complete block list on arrival. Loses the typing effect but
   is trivially reliable, which on a mobile demo may be the better trade.
   🔴 This is a **contract change**: propose it per `Context.md` §7.4 and get a
   written ack before building against it. Do not assume the parameter exists.

🔴 Share the SSE **parsing** logic (a pure function over a text buffer) between
web and native. Do not share the transport.

---

## 13. Phases — must match `Project_requirement.md` §7

🔴 This table is static. Your **current** phase lives in `apps/web/FE_PHASE.md`
under the `⬅ CURRENT` marker. Read it at the start of every session —
`Rules.md` §3 forbids building outside it. The backend tracks its own phase in
`Phase.md` on its branch; the two can be a phase apart, which is fine as long as
the integration checkpoints in `Integration_Guide.md` §6 are met.

| Phase | Name | Frontend exit criteria |
|---|---|---|
| **0** | Contract & skeleton | Monorepo boots · tokens + UI primitives · `packages/api-client` · **all block renderers built from the schema** · `/debug/blocks` renders every type + unknown · Prism mock wired · types generating · i18n scaffolded |
| **1** | Identity & diagnostic | Register/login via `supabase-js` · `GET /me` on first login · diagnostic flow with resume · profile review + edit |
| **2** | Goal → Plan | Goal entry + `PATCH` correction · job-polling generating screen · plan view with rationale · `/debug/profile` switcher |
| **3** | Lesson & checkpoint | Lesson screen streaming blocks · "I'm lost" → `/reexplain` · tutor drawer · checkpoint + feedback · dashboard (no adaptations panel) · signal emission |
| **4** | Adaptation loop | Adaptation modal + `/adaptations` with before/after diff, reason and timeline impact · dashboard adaptations panel · settings incl. export/delete |
| **5** | Mobile companion | Expo app: login, home, lesson, chat, progress on a real device · RN streaming decision implemented |
| **6** | Polish & demo hardening | Landing page · empty/error/loading states everywhere on the demo path · a11y pass · dark mode · Lighthouse ≥90 · offline fallback for cached lessons |

🔴 Phase 0 is not "setup". The block renderers are the deepest work you do and
they depend on nothing but the schema. Build them while the backend is still
writing migrations.

---

## 14. Working with your AI — the loop

```
0. SYNC    git merge main   (pick up contract and doc updates)
1. READ    apps/web/FE_PHASE.md (the ⬅ CURRENT marker) + apps/web/FE_MEMORY.md
           + contract/status.md + §13 above.
2. PICK    One screen or one component. Not a feature area.
3. STATE   Give the AI:
             - the exact route/component
             - the generated type it must use (paste it)
             - which files it may touch
             - "use only packages/ui tokens; no new dependencies"
4. BUILD   Small diff, one concern.
5. RUN     Open it in a browser. Click it. Tab through it with the keyboard.
6. VERIFY  Loading, empty, error state. Mobile width. Dark mode.
7. SYNC    Post your line in contract/status.md.
```

**Session-opening prompt when your AI has no context:**

```
Read Context.md, Rules.md, Project_requirement.md, Frontend_Instructions.md,
Phase.md and contract/status.md before doing anything.

Then tell me, in under 150 words:
  (a) which phase we're in,
  (b) which screens are unbuilt in that phase,
  (c) which endpoints are mocked vs live,
  (d) which files you'll touch.

Do not write code until I confirm.
```

**Red flags — stop the AI immediately if it:**

- Writes a TypeScript interface for an API response (must be generated)
- Calls `fetch` outside `packages/api-client`
- Hardcodes a colour, a spacing value, or an English string
- Adds a UI library, an animation library, or an icon set you did not approve
- Uses `any`, or `@ts-ignore` without a reason comment
- Creates mock data inside a component
- Touches anything under `services/`
- Says "I also refactored…"

---

## 15. Definition of done — per screen

- [ ] Uses only generated types from `packages/api-types`
- [ ] All data through `packages/api-client`
- [ ] Loading, empty and error states all implemented and seen
- [ ] Keyboard-complete; focus visible; Escape closes overlays
- [ ] All strings via i18n
- [ ] Works at 360px, 768px, 1280px
- [ ] Light and dark
- [ ] `prefers-reduced-motion` respected
- [ ] No console errors or warnings
- [ ] `tsc --noEmit` clean
- [ ] Verified against the **real** backend once the endpoint is `live`
- [ ] Line posted in `contract/status.md`

---

## 16. First 90 minutes — do exactly this

1. `pnpm create next-app apps/web` (TS, App Router, Tailwind)
2. pnpm workspace + Turborepo; create `packages/ui`, `packages/api-client`,
   `packages/api-types`, `packages/i18n`
3. Define tokens in `packages/ui/tokens.css`; wire Tailwind to them
4. Set up next-intl with an `en` and an empty `hi` namespace
5. **The moment `contract/blocks.schema.json` lands, build every block renderer
   plus `UnknownBlock`, and `/debug/blocks` to prove them**
6. Start Prism against `contract/openapi.yaml`; add the `gen:types` script
7. `packages/api-client` with base URL, auth header, error envelope handling
8. Post your first line in `contract/status.md`

🔴 Do not build the landing page first. It is the least important screen and
the most tempting one. Build the block renderers.

---

## 17. Your tracking files: `FE_MEMORY.md` and `FE_PHASE.md`

`Rules.md` §0 requires every agent to record what it changed. The backend agent
writes `Memory.md`; **you write `apps/web/FE_MEMORY.md`.** 🔴 Never write into
`Memory.md` — that file is theirs (`Rules.md` §1).

Use the same structure as `Backend_Instructions.md` §4.2:

- **STATE** (rewritten in place): a table of screens — route, phase, built?,
  tested?, notes; which endpoints you are consuming and whether against mock or
  live; a **Known broken / half-finished** list; a **Do not touch** list.
- **CHANGELOG** (append at top): dated entries with *Added / Changed / Tested /
  Broken-or-left-undone / Next*.

The payoff is identical: a fresh session reads it and knows where you are
without reading every component.

`apps/web/FE_PHASE.md` is your phase tracker — all seven phases with the names
from `Project_requirement.md` §7, exactly one marked `⬅ CURRENT`, and an ordered
task queue for it. 🔴 Do not create a root `Phase.md`; that file is the
backend's, on its own branch.

---

*Last updated: 2026-08-26 · Owner: Disha (Team Lead) · Frontend Dev may propose changes via `contract/CHANGELOG.md`.*
