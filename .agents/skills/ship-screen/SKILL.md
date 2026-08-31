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
