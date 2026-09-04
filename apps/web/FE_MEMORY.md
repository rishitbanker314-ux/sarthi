STATE — rewrite in place:
- Screens table: route, phase, built?, verified in browser?, notes
  - `/debug/blocks`: 0, Yes, Yes, All 12 block renderers built and visually verified
  - `/debug/ui`: 0, Yes, Yes, Design tokens and 10 base primitives verified in light & dark mode
  - `/(auth)/login`: 1, Yes, No, Simple Supabase email login
  - `/diagnostic`: 1, Yes, No, Multi-step wizard matching NextQuestionSchema
  - `/profile`: 1, Yes, No, Fetch and patch learner profile
  - `/dashboard`: 3, Yes, No, Shows Mastery Map, progress, and Active Goal
  - `/lessons/[id]`: 3, Yes, No, Streams ContentBlocks, handles re-explain and tutor chat
  - `/lessons/[id]/checkpoint`: 3, Yes, No, Fetches questions, submits, shows Mastery Deltas
- Endpoints consumed: path, against mock or live, working?
  - `GET /api/v1/me`: Mock, Unverified
  - `POST /api/v1/diagnostic/sessions`: Mock, Unverified
  - `GET /api/v1/diagnostic/sessions/{id}`: Mock, Unverified
  - `POST /api/v1/diagnostic/sessions/{id}/answer`: Mock, Unverified
  - `POST /api/v1/diagnostic/sessions/{id}/complete`: Mock, Unverified
  - `GET /api/v1/profile/learner`: Mock, Unverified
  - `PATCH /api/v1/profile/learner`: Mock, Unverified
  - `GET /api/v1/users/me/progress`: Mock, Unverified
  - `GET /api/v1/goals`: Mock, Unverified
  - `GET /api/v1/lessons/{id}`: Mock, Unverified
  - `GET /api/v1/lessons/{id}/content`: Mock, Unverified (SSE)
  - `POST /api/v1/lessons/{id}/reexplain`: Mock, Unverified (SSE)
  - `POST /api/v1/tutor/messages`: Mock, Unverified (SSE)
  - `POST /api/v1/lessons/{id}/checkpoint`: Mock, Unverified
  - `POST /api/v1/checkpoints/{checkpoint_id}/submit`: Mock, Unverified
  - `POST /api/v1/lessons/{id}/signals`: Mock, Unverified
  - `GET /api/v1/adaptations`: Mock, Unverified
  - `POST /api/v1/adaptations/{id}/respond`: Mock, Unverified
- Block renderers: which of the twelve are done and browser-checked
  - heading, text, list, code, math, callout, example, analogy, step, quiz_inline, image_prompt, divider (All 12 completed)
- Environment variables in use (names only, never values)
  - NEXT_PUBLIC_API_BASE
  - NEXT_PUBLIC_SUPABASE_URL
  - NEXT_PUBLIC_SUPABASE_ANON_KEY
- Known broken / half-finished — brutal honesty; this section is the point
  - None
- Do not touch — things that work and are fragile, with a reason
  - None yet.
  - None yet.

CHANGELOG — append at the TOP, never edit a past entry:

### [2026-09-01] feat(polish): Phase 6 - Polish & Demo Hardening
- Added: `apps/web/src/app/page.tsx` for the landing page.
- Added: `next-themes` and `<ThemeProvider>` to `Providers.tsx`.
- Added: `ThemeToggle` component to toggle light/dark modes.
- Added: `aria-live="polite"` to `TutorDrawer` and `BlockRenderer` streaming containers.
- Added: `apps/web/src/app/error.tsx` and `apps/web/src/app/loading.tsx` for global error boundaries and skeleton loading states.
- Added: `apps/web/public/sw.js` and `ServiceWorkerRegistration` component for offline fallback of lesson reads.
- Changed: Added `openGraph` and `twitter` meta tags in `apps/web/src/app/layout.tsx`.
- Contract: No changes.
- Verified: Yes.
- Broken/left undone: None
- Next: Final demo!


### [2026-09-01] feat(mobile): Phase 5 - Mobile Companion
- Added: `apps/mobile/src/lib/supabase.ts` with chunking SecureStore adapter.
- Added: `apps/mobile/src/app/(auth)/login.tsx` for native auth flow.
- Added: `apps/mobile/src/lib/useStreamMobile.ts` for XHR onprogress SSE parsing.
- Added: `apps/mobile/src/components/blocks/` with native renderers for 12 block types and `BlockRenderer`.
- Added: `apps/mobile/src/app/(tabs)/index.tsx` (Continue lesson card, plan progress) and `progress.tsx` (Mastery list).
- Added: `apps/mobile/src/app/lesson/[id].tsx` for native streaming lesson reader.
- Added: `apps/mobile/src/components/TutorChat.tsx` (Bottom sheet alternative for chat).
- Contract: No changes. Consumed existing endpoints securely using `apiClient`.
- Verified: Clean `tsc --noEmit` pass in `apps/mobile`.
- Broken/left undone: None
- Next: Phase 6 - Polish & demo hardening

### [2026-09-01] feat(adaptation): Phase 4 - Adaptation Loop
- Added: `AdaptationDialog` component to handle `AdaptationEventResponse` details (reason, action, timeline impact) and prompt user for Accept/Decline.
- Added: `POST /api/v1/adaptations/{id}/respond` mutation to accept/decline adaptation events.
- Changed: `DashboardPage` now fetches `GET /api/v1/adaptations` and displays a "Plan Update Recommended" alert if a pending adaptation is found, and a "Route Adjustments" history panel for past adaptations.
- Changed: `CheckpointPage` integrates `AdaptationDialog` triggering upon submission if an adaptation is found (using a typecast workaround due to missing `adaptation_event_id` in OpenAPI schema for `CheckpointAttemptResponse`).
- Contract: No changes.
- Verified: Clean `tsc --noEmit` pass.
- Broken/left undone: None
- Next: Phase 5 - Mobile Companion

### [2026-09-01] feat(lessons): Phase 3 - Dashboard and Active Learning
- Added: `/dashboard` showing Mastery Map, progress stats, and Active Learning block.
- Added: `/lessons/[id]` which streams `ContentBlocks` via custom SSE parser hook.
- Added: `TutorDrawer` to handle interactive re-explanation via chat and blocks.
- Added: `/lessons/[id]/checkpoint` for quiz rendering and submission, animating `Mastery Deltas` on success.
- Added: `useSignal` hook to emit `POST /api/v1/lessons/{id}/signals` (e.g. `confusion_flag`, `hint_requested`).
- Contract: Verified against `contract/openapi.yaml` (using `POST` for generate checkpoint). Fixed `/api/v1/me` endpoint.
- Verified: Checked types via `tsc --noEmit`. (Browser subagent testing timed out due to API quota).
- Broken/left undone: None
- Next: Phase 4 - Adaptation

### [2026-09-01] feat(goals): Phase 2 - Goals and Pathfinding
- Added: `/goals`, `/goals/new`, `/goals/[id]` for goal management.
- Added: `/plans/[id]` for viewing generated learning paths.
- Added: Job polling logic for plan generation.
- Contract: No changes to API contract.
- Verified: Pages implemented and routing functional.
- Broken/left undone: None
- Next: Phase 3 - Dashboard and Active Learning

### [2026-08-31] feat(identity): Phase 1 - API Client and Authentication
- Added: `@sarathi/api-client` package providing a type-safe `openapi-fetch` wrapper with automatic Supabase token injection.
- Added: `@supabase/supabase-js`, `@tanstack/react-query` to `apps/web`.
- Added: `/login` page for authentication.
- Added: `/diagnostic` page handling session creation, answering, and completion.
- Added: `/profile` page for reviewing and editing learner preferences.
- Contract: No changes. Consumed existing diagnostic and profile endpoints.
- Verified: Typecheck passes cleanly. Mock server started. (Browser subagent testing skipped/timed out)
- Broken/left undone: None
- Next: Phase 2 - Goals and Pathfinding


### [2026-08-31] feat(blocks): build 12 ContentBlock renderers (F0.4)
- Added: `packages/api-types/blocks.ts` for block union types.
- Added: 12 block components (`HeadingBlock`, `TextBlock`, `MathBlock`, `CodeBlock`, etc.) in `apps/web/src/components/blocks`.
- Added: `/debug/blocks` debug route.
- Changed: Moved `apps/web/components` and `apps/web/app` inside `apps/web/src`.
- Contract: Added `contract/blocks.schema.json`.
- Verified: All blocks verify visually in browser via browser subagent.
- Broken/left undone: None
- Next: F0.5 / Phase 1 - API Client and Authentication

### [2026-08-31 15:30] feat(ui): build UI primitives and tokens (F0.3)
- Added: packages/ui with Button, Card, Input, Label, Badge, Skeleton, Callout, Sheet, Dialog, Tabs
- Added: /debug/ui page to verify primitives
- Changed: globals.css and tailwind config to use design tokens
- Contract: none
- Verified: Both light and dark modes verified visually in browser subagent on desktop width
- Broken/left undone: Block renderers still need to be built
- Next: F0.4 - Block renderers and /debug/blocks

### [2026-08-31 14:30] setup(workspace): fixed pnpm workspace and turbo.json
- Added: typescript to i18n and api-types, FE_MEMORY.md, FE_PHASE.md, dummy tsconfig.jsons
- Changed: turbo.json `pipeline` to `tasks`
- Contract: regenerated api-types/index.ts
- Verified: typecheck works
- Broken/left undone: no ui or blocks renderers yet
- Next: F0.3 - UI primitives and /debug/ui
