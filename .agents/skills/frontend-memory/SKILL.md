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
