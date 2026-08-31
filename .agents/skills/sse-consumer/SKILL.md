---
name: sse-consumer
description: How to consume the backend's Server-Sent Event streams for lesson content, reexplain and tutor chat — event names, parsing, termination, heartbeats, idle timeouts and cancellation. Use when building or debugging any streaming UI, or when a stream hangs, arrives all at once, or never finishes.
---

# Consuming SSE

Read contract/events.md. Three endpoints stream:
  GET  /lessons/{id}/content     block events
  POST /lessons/{id}/reexplain   block events
  POST /tutor/messages           token events, plus block for code and maths

## 🔴 Use fetch + ReadableStream, never EventSource

EventSource is GET-only AND cannot send an Authorization header. All three
endpoints are authenticated. One transport, one auth path.

## The five events — nothing else exists

token  {"text": "..."}                     append to the in-flight chat message
block  {id, type, concept_id, ...}         a COMPLETE renderable ContentBlock
tool   {"name": "...", "status": "..."}    subtle thinking affordance, non-blocking
done   {message_id, block_count, usage}    finalise, stop the spinner
error  {code, message, retryable, details} 🔴 INNER object, no wrapper

## Hard rules

- Render blocks as they arrive. Never buffer until `done` — perceived speed is
  the point.
- 🔴 Always handle a stream that ends WITHOUT a terminal event. Treat 30s of
  silence as an error. A spinner that never stops is the worst demo failure
  there is.
- 🔴 Reset the idle timer on ANY bytes received, including the backend's
  `: ping` comment heartbeats every 15s. A timer driven only by parsed events
  fires spuriously while the model is still thinking about the first block.
- Auto-scroll ONLY when the user is already at the bottom. Yanking the viewport
  away from someone who scrolled up is infuriating.
- Abort the stream on unmount with an AbortController. A leaked stream costs
  real tokens and causes ghost updates.
- Parse incrementally: keep a text buffer, split on "\n\n", handle partial
  events left at the end of a chunk. Do not assume one chunk is one event.

## Sharing with mobile

Put the PARSING in a pure function over a text buffer, in packages/api-client,
so React Native can reuse it. Do NOT share the transport — React Native's fetch
does not expose a streaming body. See mobile-parity.
