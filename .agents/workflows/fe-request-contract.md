# Request a contract change from the backend

You need something the API does not provide. You must NOT invent it.

1. State exactly what is missing: the endpoint, field or block type, and what
   screen needs it.
2. Show the shape you need, as JSON.
3. Classify it: ADDITIVE (new optional field, new endpoint) or BREAKING
   (rename, removal, type change, new required field).
4. Append to contract/CHANGELOG.md under `## Proposed`, with today's date, the
   classification, the requested shape, and a blank ack line. Remember
   contract/CHANGELOG.md is edited on main — tell the user the exact git
   commands if they are on the frontend branch.
5. Tell the user to message the backend developer in words, not just commit.
6. 🔴 STOP. Do not stub the endpoint, do not mock it locally, do not guess its
   shape. Suggest what else in the current phase can be built meanwhile.
