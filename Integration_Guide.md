# Integration_Guide.md
### One repo, two branches, one clean merge · Sarathi · SIH26205

> **Read this before either of you writes another line.** It is the only
> document that exists to make the final merge boring.
>
> Owner: Disha (Team Lead). Both devs follow it exactly.

---

## 0. The one thing that matters

> **A merge is painful in exact proportion to how long you delayed it.**

The plan is *not* "build the backend, build the frontend, merge at the end." That
plan fails, every time, at the worst possible moment. The plan is:

1. Make the two branches **touch different files**, so git has nothing to argue about.
2. Merge `main` into both branches **daily**, so drift is measured in hours.
3. Do a **trial full merge at the end of every phase**, so you find integration
   bugs six at a time instead of sixty.

Do those three things and the final merge is a `git merge` that prints
"Fast-forward" and you go back to rehearsing your pitch. Skip them and you will
spend the last 48 hours resolving conflicts instead of building.

---

## 1. The branch model

```
                    main  ← the shared trunk
                     │      docs + contract/ + shared config ONLY
                     │      No application code ever lives here.
        ┌────────────┴────────────┐
        │                         │
    backend                   frontend
    Python / FastAPI          TypeScript / Next.js / Expo
    owns services/,           owns apps/, packages/
    migrations/, tests/
```

**Rules of the model:**

| Rule | Why |
|---|---|
| `main` holds only documents, `contract/`, and shared config | Nothing to conflict over |
| Neither branch is ever merged *into the other* directly | That is how you get a 200-file conflict |
| Both branches merge **from** `main`, daily | Keeps the contract in sync |
| `contract/openapi.yaml` is **published to `main`** by the backend | One source of truth, reachable by both |
| Every file has exactly **one owning branch** | §2 is the map. Follow it literally. |
| The final merge is `main ← backend`, then `main ← frontend` | Disjoint paths, so the second merge is trivial |

---

## 2. 🔴 The path-ownership map

This table is the whole trick. If both branches obey it, the two file sets are
**disjoint** and git cannot produce a content conflict.

### 2.1 `main` — shared, changed rarely and deliberately

```
Context.md                       Rules.md
Project_requirement.md           Integration_Guide.md
Backend_Instructions.md          Frontend_Instructions.md
Backend_Roadmap.md               Frontend_Roadmap.md
Antigravity_Prompts.md           Antigravity_Prompts_Frontend.md
README.md
.gitignore                       ← ONE file, created once, then frozen
.agents/rules/00-project.md      ← shared rules both agents need
contract/
├── openapi.yaml                 ← backend generates → publishes here
├── blocks.schema.json
├── events.md
├── status.md                    ← both devs append their sync lines
└── CHANGELOG.md                 ← both devs append entries
tools/
└── sync-contract.sh
```

### 2.2 `backend` branch only — the frontend never creates these

```
pyproject.toml                   uv.lock
alembic.ini                      Dockerfile
docker-compose.yml               .dockerignore
.env.example                     ← backend's; frontend uses per-app files
services/**                      migrations/**
tests/**                         ← Python tests, root-level
scripts/**                       ← Python scripts
/fixtures/**                     ← root-anchored. apps/web/lib/fixtures/ is the
                                   frontend's own and is NOT this path.
Architecture.md   Memory.md   Phase.md
.agents/rules/10-python.md
.agents/rules/20-migrations.md
.agents/rules/30-agents.md
.agents/skills/ship-endpoint/          .agents/skills/new-agent/
.agents/skills/supabase-postgres/      .agents/skills/demo-mode/
.agents/skills/sse-streaming/          .agents/skills/project-memory/
.agents/workflows/phase-check.md
.agents/workflows/verify-me.md
.agents/workflows/contract-change.md
.agents/mcp_config.json (gitignored)   .agents/mcp_config.example.json
```

### 2.3 `frontend` branch only — the backend never creates these

```
package.json                     pnpm-lock.yaml
pnpm-workspace.yaml              turbo.json
.npmrc                           .nvmrc
apps/web/**                      ← includes apps/web/.env.example
apps/mobile/**                   ← includes apps/mobile/.env.example
packages/ui/**                   packages/api-client/**
packages/api-types/**            packages/i18n/**
apps/web/FE_MEMORY.md            apps/web/FE_PHASE.md
.agents/rules/40-typescript.md
.agents/rules/50-ui.md
.agents/rules/60-integration.md
.agents/skills/ship-screen/            .agents/skills/block-renderer/
.agents/skills/api-integration/        .agents/skills/sse-consumer/
.agents/skills/mobile-parity/          .agents/skills/frontend-memory/
.agents/workflows/fe-phase-check.md
.agents/workflows/fe-verify-me.md
.agents/workflows/fe-request-contract.md
```

🔴 **Notice what is NOT in the frontend list:** no root `Dockerfile`, no root
`docker-compose.yml`, no root `.env.example`, no root `tests/`, no root
`scripts/`, no root `.gitignore` edits. Every one of those is a guaranteed
conflict. The frontend uses `apps/web/.env.example`, colocated tests, npm
scripts, and `tools/` on `main`.

### 2.4 The four files that could still bite, and how each is handled

| File | Risk | Handling |
|---|---|---|
| `.gitignore` | Both need entries | 🔴 **Created once on `main` in §3 with BOTH sides' entries, then never edited again.** If you must add a line, add it on `main` and pull. |
| `.agents/rules/00-project.md` | Both agents need shared rules | Lives on `main`. Branch-specific rules use non-colliding numbers (10/20/30 backend, 40/50/60 frontend). |
| `contract/status.md`, `CHANGELOG.md` | Both append | Both edit them **on `main`**, never on a branch. Append at the **end** for status, at the **top** for CHANGELOG. Two people appending to different ends of a file merges cleanly nine times out of ten; when it does not, the conflict is two lines and takes ten seconds. |
| `README.md` | Both want to write it | Disha owns it, on `main`. Neither dev touches it. |

---

## 3. Day 0 — set the trunk up correctly (Disha, ~20 minutes)

The backend branch is already at Phase 1+, so this is a small fixup, not a
rebuild. Run it once, today, before the frontend branch is created.

```bash
git checkout main
git pull

# 1. Bring the shared documents onto main.
git checkout backend -- Context.md Rules.md Project_requirement.md \
    Backend_Instructions.md Frontend_Instructions.md \
    Backend_Roadmap.md Antigravity_Prompts.md
# then add the four new files from this session:
#   Frontend_Roadmap.md  Antigravity_Prompts_Frontend.md  Integration_Guide.md

# 2. Bring the contract onto main.
git checkout backend -- contract/

# 3. Bring .gitignore onto main and complete it (content in §3.1).
git checkout backend -- .gitignore
$EDITOR .gitignore

# 4. Split the shared rules out of the backend's 00-project.md (see §3.2).
mkdir -p .agents/rules
git checkout backend -- .agents/rules/00-project.md
$EDITOR .agents/rules/00-project.md      # strip backend-only lines

mkdir -p tools                            # paste sync-contract.sh from §5.2 here
chmod +x tools/sync-contract.sh           # and e2e_check.md from §9.1

git add -A && git commit -m "chore: establish main as the shared trunk"
git push origin main
```

Then, on the backend branch, take `main`'s versions and stop editing them:

```bash
git checkout backend
git merge main

# Move the backend-only lines you stripped out of 00-project.md into 10-python.md.
$EDITOR .agents/rules/10-python.md
# main's 00-project.md now arrives by merge and overwrites the old one.

git add -A && git commit -m "chore: adopt main's shared config"
git push origin backend
```

> 🔴 **Do NOT `git rm --cached` `.gitignore` or `contract/` on the backend
> branch.** It is tempting — "only `main` should track them" — and it is a trap
> with two separate failure modes:
>
> 1. Git records those paths as *deleted in `backend`*. At the final merge
>    (§8), git sees `main` modified `contract/` and `backend` deleted it, and
>    resolves that as a delete-vs-modify conflict on every contract file — or
>    silently deletes `.gitignore` outright.
> 2. The files stay on disk **untracked**, so the very next `git merge main`
>    (§4, every session) aborts with *"untracked working tree files would be
>    overwritten by merge."*
>
> These files stay **tracked on every branch**. Disjointness comes from nobody
> *editing* them on a branch, not from removing them.

**The rule, stated plainly:** `.gitignore`, `contract/**` and
`.agents/rules/00-project.md` are edited **only on `main`**. Both branches
receive them by merging. That is the whole mechanism.

Finally, create the frontend branch **from `main`, not from `backend`**:

```bash
git checkout main
git checkout -b frontend
git push -u origin frontend
```

🔴 Branching the frontend from `backend` would drag every Python file onto it
and guarantee conflicts later. From `main`, it starts with docs and contract
only — exactly what it needs.

### 3.1 The complete `.gitignore` for `main`

Create this once. Then leave it alone.

```gitignore
# ── Shared ────────────────────────────────────────────────
.env
.env.local
.env.*.local
.DS_Store
*.log
.idea/
.vscode/
.agents/mcp_config.json

# ── Backend (Python) ──────────────────────────────────────
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.ruff_cache/
.mypy_cache/
*.egg-info/
htmlcov/
.coverage

# ── Frontend (Node) ───────────────────────────────────────
node_modules/
.next/
out/
build/
dist/
.turbo/
.expo/
.expo-shared/
*.tsbuildinfo
coverage/
.pnpm-store/

# ── Generated, but COMMITTED on purpose ───────────────────
# packages/api-types/  is generated from contract/openapi.yaml but IS committed,
# so a fresh clone type-checks before anyone runs a generator. Do not ignore it.
```

### 3.2 `main`'s `.agents/rules/00-project.md` — the shared rules

Both agents read this. Strip everything language-specific out of it; that goes
in `10-python.md` (backend) or `40-typescript.md` (frontend).

Keep in `00-project.md`: the project summary, the glossary, the error envelope,
contract discipline, the secrets rules, the honesty rules, the file-ownership
rules, and a pointer to `Integration_Guide.md` §2.

Add these lines to it — they are new and they matter:

```markdown
## Branch discipline

This repository has three branches. `main` holds documents, `contract/` and
shared config. `backend` holds Python. `frontend` holds TypeScript.

- Never create a file that Integration_Guide.md section 2 assigns to the other
  branch. If a task seems to require it, STOP and tell the user.
- Never edit contract/openapi.yaml. The backend generates it; both branches
  receive it by merging main.
- If you need something from the other side that does not exist yet, say so and
  stop. Do not stub it, do not invent its shape, do not work around it.
```

---

## 4. The daily rhythm

**Both devs, every working session, first thing:**

```bash
git checkout <your-branch>
git merge main          # pick up contract changes and doc updates
```

**Both devs, end of session:**

```bash
git push origin <your-branch>
```

Then append one line to `contract/status.md` **on `main`**:

```
[2026-09-03 21:40] BE  done: planner agent + POST /goals/{id}/plan  next: GET /plans/{id}  blocked: none
[2026-09-03 21:55] FE  done: block renderers + /debug/blocks        next: login screens   blocked: none
```

If either line says anything but `blocked: none` twice running, Disha
intervenes. That is the entire escalation policy.

---

## 5. The contract sync ritual

### 5.1 Who may change what

| File | Written by | Read by |
|---|---|---|
| `contract/openapi.yaml` | Backend only (generated) | Frontend, to generate types |
| `contract/blocks.schema.json` | Backend proposes, both agree | Frontend, to build renderers |
| `contract/events.md` | Backend proposes, both agree | Frontend, to consume SSE |
| `contract/status.md` | Both, append-only | Both |
| `contract/CHANGELOG.md` | Both, append at top | Both |

### 5.2 Backend publishes a contract change

After any endpoint ships:

```bash
# on the backend branch, after regenerating contract/openapi.yaml
git add contract/openapi.yaml && git commit -m "contract: add POST /goals/{id}/plan"

git checkout main
git checkout backend -- contract/openapi.yaml
git commit -m "contract: publish openapi.yaml @ $(date +%F)"
git push origin main

git checkout backend
```

Then **message the frontend dev in words**. Not just a commit — an actual
message. A silent contract change is the single most expensive mistake
available on this project.

**`tools/sync-contract.sh`** — create this on `main` in §3, and run it from the
backend branch after every endpoint ships. `Backend_Roadmap.md` §6.3 also
defines a `/sync-contract` Antigravity workflow that calls it.

```bash
#!/usr/bin/env bash
# tools/sync-contract.sh — publish contract/openapi.yaml from `backend` to `main`.
# Run from the repo root, on the backend branch, with a clean working tree.
set -euo pipefail

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[ "$BRANCH" = "backend" ] || { echo "Run this on the backend branch (you are on $BRANCH)."; exit 1; }
git diff --quiet && git diff --cached --quiet || { echo "Commit or stash your changes first."; exit 1; }

git add contract/openapi.yaml
git diff --cached --quiet && echo "openapi.yaml unchanged — nothing to publish." && exit 0
git commit -m "contract: regenerate openapi.yaml"

git checkout main
git pull --ff-only
git checkout backend -- contract/openapi.yaml
git commit -m "contract: publish openapi.yaml @ $(date +%F)" || echo "main already up to date."
git push origin main
git checkout backend

echo
echo "Published. NOW MESSAGE THE FRONTEND DEV IN WORDS."
echo "A silent contract change is the most expensive mistake on this project."
```

`chmod +x tools/sync-contract.sh` after creating it.

### 5.3 Frontend consumes it

```bash
git checkout frontend
git merge main
pnpm gen:types          # openapi-typescript contract/openapi.yaml -> packages/api-types
pnpm typecheck          # compile errors here are the contract change, surfacing
```

🔴 Compile errors after a contract sync are **good news** — that is the whole
point of generated types. Fix them immediately, do not `// @ts-ignore` them.

### 5.4 Frontend needs something that does not exist

Never invent it. Append to `contract/CHANGELOG.md` on `main` under
`## Proposed`, message the backend dev, and keep building something else. The
`/fe-request-contract` workflow does this for you.

---

## 6. 🔴 Integration checkpoints — do not skip these

Four of them. Each is a **trial merge into a throwaway branch**, so nothing is
at risk and you learn what would break.

```bash
git checkout main && git pull
git checkout -b trial-merge-phaseN
git merge backend    # expect: clean
git merge frontend   # expect: clean
# ... run the checks below ...
git checkout main && git branch -D trial-merge-phaseN
```

| Checkpoint | When | What must pass |
|---|---|---|
| **IC-1** | End of Phase 1, both sides | Trial merge is clean. Frontend logs in with Supabase, calls the **real** `GET /me` on `localhost:8000`, and completes a real diagnostic. |
| **IC-2** | End of Phase 2 | Real goal → real plan generation → the generating screen shows the backend's actual `progress_message` → the plan renders with its real rationale. |
| **IC-3** | End of Phase 3 | 🔴 **The hard one.** Real SSE from FastAPI renders in the browser: blocks arrive progressively, exactly one `done`, heartbeats do not break the parser, an error mid-stream shows a retry. Checkpoint scores and mastery moves. |
| **IC-4** | End of Phase 4 | The full demo path end to end on real services: diagnostic → goal → plan → lesson → failed checkpoint → **adaptation modal with a real reason** → accept → new plan version. |

🔴 **IC-3 is where projects like this die.** SSE is the only place where a
subtle contract mismatch produces a hang rather than an error. Do it on
schedule, not "when we get to it."

**If a checkpoint fails**, fix it *then*. A known integration bug carried into
the next phase gets built on top of and costs five times as much to remove.

---

## 7. How the frontend dev runs the real backend

The frontend dev does not need to understand Python. Four commands.

```bash
# once, in a SEPARATE folder so it does not disturb your frontend checkout
git clone <repo-url> sarathi-backend-checkout
cd sarathi-backend-checkout
git checkout backend

# get the env file from Disha (it contains keys — never commit it)
cp .env.example .env && $EDITOR .env

docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.seed_demo

curl -s localhost:8000/health          # {"status":"ok","db":"ok",...}
```

Then in `apps/web/.env.local`:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

To get a token without a Supabase account, use the backend's dev issuer:

```bash
curl -s -XPOST localhost:8000/dev/auth/token \
  -H 'content-type: application/json' \
  -d '{"email":"demo@sarathi.app"}' | jq -r .access_token
```

🔴 That endpoint exists **only** when the backend runs with
`ENV=development`. It is a development convenience, never a production path.

**Alternatively**, use `git worktree` to keep both branches checked out at once
without a second clone:

```bash
git worktree add ../sarathi-backend backend
```

---

## 8. The final merge

Do this when both branches have finished Phase 6 — and after IC-4 has already
passed, so you are confirming, not discovering.

```bash
# 0. Both devs push everything. Both branches are green.
#    Backend: pytest passes.  Frontend: pnpm build && pnpm typecheck pass.

git checkout main && git pull

# 1. Backend first — it owns the contract.
git merge backend --no-ff -m "merge: backend"
#    Expect zero conflicts. If you get one, STOP and read §10.

# 2. Frontend second.
git merge frontend --no-ff -m "merge: frontend"
#    Expect zero conflicts.

# 3. Verify BEFORE pushing.
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api pytest -q
pnpm install && pnpm typecheck && pnpm build

# 4. Run the end-to-end check in §9.

# 5. Only then:
git push origin main
git tag -a v1.0-demo -m "SIH demo build" && git push --tags
```

🔴 **Tag it.** When something breaks during rehearsal at 2 a.m., `git checkout
v1.0-demo` is the difference between a five-minute recovery and a disaster.

---

## 9. Post-merge verification — the checklist

Run every line. Tick every box. Do not assume.

**Structure**

- [ ] `git status` is clean, no leftover `.orig` or `.rej` files
- [ ] One `.gitignore`, one `contract/`, one `.agents/` with all rule files present
- [ ] No duplicated config (`Dockerfile`, `package.json`, `pyproject.toml` all appear exactly once)
- [ ] `grep -r "<<<<<<<" .` returns nothing

**Backend**

- [ ] `docker compose up -d --build` succeeds
- [ ] `alembic upgrade head` runs clean on a fresh database
- [ ] `pytest -q` is green
- [ ] `curl localhost:8000/health` → `"db":"ok"`

**Frontend**

- [ ] `pnpm install` succeeds from a clean `node_modules`
- [ ] `pnpm typecheck` is clean
- [ ] `pnpm build` succeeds
- [ ] `pnpm gen:types` produces **no diff** — proof the committed types match the committed contract

**Integration**

- [ ] Web app at `localhost:3000` talks to the API at `localhost:8000`
- [ ] Login works, `GET /me` creates the profile
- [ ] The whole demo path runs (see §9.1)
- [ ] SSE streams progressively — check the Network tab, not just the rendered page
- [ ] Mobile app on a real device reaches the same API and shows the same state
- [ ] `DEMO_MODE=true` + Wi-Fi **physically off** still runs the whole path

### 9.1 The end-to-end integration test

🔴 **Disha writes `tools/e2e_check.md` on `main`** — `tools/` is `main`-owned,
so neither dev creates it on a branch. It is a human runbook, not a test suite.
Walk it after every trial merge:

```
 1. Fresh browser profile, go to localhost:3000
 2. Register a new account                     → lands on the diagnostic
 3. Complete the diagnostic                    → profile page shows plain-language summary
 4. Change one profile dimension               → profile_version increments
 5. Enter a goal in your own words             → interpretation shown, editable
 6. Generate the plan                          → progress messages are the backend's real ones
 7. Plan renders                               → rationale names YOUR profile values
 8. Open lesson 1                              → blocks stream in, first one within 3s
 9. Press "I'm lost"                           → a DIFFERENT kind of explanation appears
10. Ask the tutor a question                   → tokens stream
11. Take the checkpoint, fail it deliberately  → per-item feedback explains why
12. Wait                                       → adaptation modal appears with a real reason
13. Accept it                                  → plan visibly changes, new version
14. Open the mobile app, same account          → same lesson, same progress
15. Turn Wi-Fi off, DEMO_MODE=true, repeat 8–13
```

Any step that needs an explanation or a retry is a bug, not a quirk.

---

## 10. When it conflicts anyway

It will, once or twice. Here is the triage.

| Conflict in | Cause | Fix |
|---|---|---|
| `contract/status.md` or `CHANGELOG.md` | Both appended | Keep **both** sides. Delete the markers. Ten seconds. |
| `.gitignore` | Someone edited it on a branch | Take `main`'s version, then add the missing line **on `main`** |
| `package.json` or `pyproject.toml` | The other branch created one | Someone violated §2. Delete the file from the branch that should not have it. |
| `.agents/rules/*` | Filename collision | Rename the newer one to an unused number |
| Anything under `services/` or `apps/` | The other branch edited it | 🔴 Someone edited a file they do not own. `git checkout --ours` / `--theirs` for the owning branch, then talk about why it happened. |

**The universal escape hatch.** If a merge goes badly wrong:

```bash
git merge --abort          # nothing has been lost; you are back where you started
```

Then merge one directory at a time to find the culprit:

```bash
git checkout main
git checkout frontend -- apps/
git checkout frontend -- packages/
git checkout frontend -- package.json pnpm-workspace.yaml turbo.json
git commit -m "merge: frontend, path by path"

# 🔴 That copied CONTENT but recorded no merge parentage, so git still thinks
# `frontend` is unmerged and the next `git merge frontend` would redo it all.
# Record the parentage without changing any file:
git merge -s ours frontend -m "merge: frontend (content already applied)"
```

That is slower but it always works, and you can see exactly what came across.

---

## 11. What each person does with this file

**Disha (backend + lead)**

- Run §3 today, before the frontend branch exists
- Publish the contract with §5.2 after every endpoint
- Call the integration checkpoints in §6 and refuse to let them slip
- Own `main`, `README.md` and the final merge

**Frontend dev**

- Branch from `main`, never from `backend`
- Never create a file listed in §2.2
- Merge `main` daily; regenerate types after every contract sync
- Run the real backend with §7 from Phase 1 onward — do not live on the mock
  for six weeks and discover reality at IC-3

---

*Companions: `Frontend_Roadmap.md`, `Antigravity_Prompts_Frontend.md`, `Backend_Roadmap.md`, `Antigravity_Prompts.md`.*
*Last updated: 2026-08-29 · Owner: Disha (Team Lead)*
