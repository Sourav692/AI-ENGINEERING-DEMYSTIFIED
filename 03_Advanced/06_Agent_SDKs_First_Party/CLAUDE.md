<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 06 — First-Party Agent SDKs

**Owns:** vendor-native agent SDKs. Stage `03_Advanced/`. Scaffolded — 3 notebooks total.

| Track | State |
|---|---|
| `Google_ADK/` · `Google_AI_SDK/` · `OpenAI_Agents_SDK/` | Mostly scope READMEs |

## Conventions here

- Needs the `protocols` extra for some SDKs (`google-adk`).
- **A new first-party SDK is a track inside this phase, not a new phase.** Anthropic's Agent SDK is the exception — it sits in `04_AI_Coding_Tools/Claude_API_and_Agent_SDK/` because that phase owns the coding-tool vendor material.

## Don't

- Don't put third-party/community frameworks here — CrewAI, AutoGen, DSPy, PydanticAI belong to `03_Advanced/10_Alternative_Agent_Frameworks/`. "First-party" means the model vendor ships it.
