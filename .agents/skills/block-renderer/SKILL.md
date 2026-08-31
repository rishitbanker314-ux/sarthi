---
name: block-renderer
description: How to build and modify ContentBlock renderers — the components that turn the backend's lesson JSON into teaching material. Covers the twelve frozen block types, the discriminated union, unknown-type handling and profile-driven behaviour. Use when working on anything under components/blocks or when a lesson does not render correctly.
---

# ContentBlock renderers

Read contract/blocks.schema.json first. It is the contract. The backend
validates against the same file.

## The twelve types — frozen

heading, text, list, code, math, callout, example, analogy, step,
quiz_inline, image_prompt, divider

callout variants: info, tip, warning, misconception, ai_notice
🔴 Five distinct visual treatments. misconception must NOT reuse the warning
token — they mean different things and must be tellable apart. ai_notice is the
AI-generated disclaimer, quiet and dismissible, once per lesson.

## Rules

- One component per type, in apps/web/components/blocks/.
- A single BlockRenderer switches on block.type.
- 🔴 The default branch renders UnknownBlock — a small visible placeholder
  naming the unknown type. NEVER crash. NEVER silently drop it. A block type the
  backend adds before you support it must degrade, not disappear.
- Types come from packages/api-types. Model the union as a discriminated union
  on `type` so an invalid block cannot type-check.
- Blocks are pure presentational components. No data fetching inside them.

## Profile-driven behaviour

- example: steps collapsed for guided_discovery learners, expanded for
  worked_examples. Reveal one at a time. Each reveal emits a hint_requested
  signal with the block_id.
- step: reveal:true shows a "Show me" button instead of the text. Pressing it
  emits hint_requested with the block_id.
- quiz_inline: answer inline, immediate feedback, NOT scored. Emits
  inline_check_failed WITH the block_id on a wrong answer — never `retry`,
  which means a scored checkpoint item was retried.
- code: copy button, language label, no execution.
- math: KaTeX. display:true centres on its own line.

## Verification

apps/web/app/debug/blocks/page.tsx renders one of every type plus one unknown
type from a local fixture. 🔴 Required by Rules.md section 10. After any change
here, /browser that page and screenshot it in both themes.
