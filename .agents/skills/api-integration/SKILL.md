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
