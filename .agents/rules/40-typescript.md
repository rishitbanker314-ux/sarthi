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
