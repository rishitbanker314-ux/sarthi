---
name: mobile-parity
description: What the Expo mobile app must share with the web app and what it must not, including the streaming transport problem, secure session storage and native block renderers. Use when building anything under apps/mobile or deciding whether code can be shared between web and native.
---

# Web and mobile

## Scope — Phase 5 only, and deliberately small

Login, home ("continue this lesson"), lesson reading, tutor chat, progress.
NOT on mobile in v1: the diagnostic, goal entry, plan generation, settings,
accepting or declining an adaptation. Those live on web. Mobile is where you
CONTINUE, not where you SET UP.

## Share

- packages/api-types (generated types)
- packages/api-client (the fetch wrapper and the SSE PARSER)
- packages/i18n (translation keys)
- The ContentBlock type union and the decision logic about how to render it

## Do NOT share

React components. Web and native primitives are different enough that the
abstraction costs more than it saves at this scale. Write native block
renderers in apps/mobile/components/blocks/ mirroring the web ones one-for-one.

## 🔴 The streaming problem — decide before Phase 5 starts

React Native's fetch does not expose a streaming response.body, and managed
Expo rules out the usual polyfills. Two options, in order of preference:

1. XHR onprogress SSE parser — XMLHttpRequest exposes responseText
   incrementally in RN. Parse the delta on each progress event with the SAME
   pure parser the web uses. Keeps streaming, works in managed Expo.
2. Non-streaming fallback — ?stream=false on endpoints 19, 19b and 21.
   🔴 That is a CONTRACT CHANGE: run /fe-request-contract and get a written ack
   before building against it.

## Session storage

supabase-js with expo-secure-store as the storage adapter. Never AsyncStorage.
⚠️ SecureStore caps values at roughly 2KB on Android and a full Supabase
session can exceed it. Write a chunking adapter that splits across numbered
keys. Decide this when you write the client, not when logins start failing on
one device.

## Managed Expo only

If a library requires a prebuild or a custom dev client, find another library.
You do not have time for a native build pipeline.
