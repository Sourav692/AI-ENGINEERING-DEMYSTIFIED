<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 06 — First-Party Agent SDKs

**Owns:** vendor-native agent SDKs. Stage `03_Advanced/`. Scaffolded — 3 notebooks total.

| Track | State |
|---|---|
| `Google_ADK/` · `Google_AI_SDK/` · `OpenAI_Agents_SDK/` · `Anthropic_Agent_SDK/` | Mostly scope READMEs |

## Conventions here

- Needs the `protocols` extra for some SDKs (`google-adk`).
- **A new first-party SDK is a track inside this phase, not a new phase.** That includes Anthropic's — `Anthropic_Agent_SDK/` is reserved here beside `OpenAI_Agents_SDK/` and `Google_ADK/`.
- **The Anthropic boundary is API-vs-SDK, not vendor.** This phase owns the Agent SDK (`claude-agent-sdk`). Building an agent by hand on the raw Messages API (`from anthropic import Anthropic`) is a coding-tool subject and stays in `04_AI_Coding_Tools/Claude_API_Primitives/`. Corrected 2026-09-19: that folder was called `Claude_API_and_Agent_SDK/` and this note used to hand it the whole Anthropic SDK topic, though it only ever contained raw-API material.

## Don't

- Don't put third-party/community frameworks here — CrewAI, AutoGen, DSPy, PydanticAI belong to `03_Advanced/10_Alternative_Agent_Frameworks/`. "First-party" means the model vendor ships it.
