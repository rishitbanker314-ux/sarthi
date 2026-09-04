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
