# SSE Contract

Used by endpoints:
- `GET /api/v1/lessons/{id}/content`
- `POST /api/v1/lessons/{id}/reexplain`
- `POST /api/v1/tutor/messages`

All three streaming endpoints are consumed with `fetch` + `ReadableStream`, never `EventSource`.

## Events

```
event: token
data: {"text": "partial text"}

event: block
data: {"id":"blk_9f2c4a1e...","type":"example","concept_id":"c8b1...","title":"...", ...}

event: tool
data: {"name":"retrieve_concept","status":"running"}

event: done
data: {"message_id":"msg_3d7f...","block_count":7,"usage":{"input":1200,"output":800}}

event: error
data: {"code":"MODEL_TIMEOUT","message":"...","retryable":true,"details":{}}
```

## Rules

- **The `error` event's `data` is the INNER error object** — `code`, `message`, `retryable`, `details` at the top level, **without** the `{"error": {...}}` wrapper used by HTTP responses.
- A stream **always** terminates with exactly one `done` **or** one `error`. Never both. Never neither.
- Send a comment heartbeat (`: ping\n\n`) every 15s to defeat proxy timeouts.
- `block` carries a **complete, renderable** block, with real `id` and `concept_id`. Never a partial one.
- `token` is for the tutor chat's prose only. Lesson content uses `block`.
