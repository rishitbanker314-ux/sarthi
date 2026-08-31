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
