STATE — rewrite in place:
- Screens table: route, phase, built?, verified in browser?, notes
  - `/debug/blocks`: 0, No, No, Need to build renderers
  - `/debug/ui`: 0, No, No, Need to build UI primitives
- Endpoints consumed: path, against mock or live, working?
  - None yet
- Block renderers: which of the twelve are done and browser-checked
  - None yet
- Environment variables in use (names only, never values)
  - NEXT_PUBLIC_API_BASE
  - NEXT_PUBLIC_SUPABASE_URL
  - NEXT_PUBLIC_SUPABASE_ANON_KEY
- Known broken / half-finished — brutal honesty; this section is the point
  - No /debug/blocks route.
  - No /debug/ui route.
- Do not touch — things that work and are fragile, with a reason
  - None yet.

CHANGELOG — append at the TOP, never edit a past entry:

### [2026-08-31 14:30] setup(workspace): fixed pnpm workspace and turbo.json
- Added: typescript to i18n and api-types, FE_MEMORY.md, FE_PHASE.md, dummy tsconfig.jsons
- Changed: turbo.json `pipeline` to `tasks`
- Contract: regenerated api-types/index.ts
- Verified: typecheck works
- Broken/left undone: no ui or blocks renderers yet
- Next: F0.3 - UI primitives and /debug/ui
