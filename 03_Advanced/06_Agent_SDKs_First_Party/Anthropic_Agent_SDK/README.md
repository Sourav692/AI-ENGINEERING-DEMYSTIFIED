# Chapter 15 — Anthropic Agent SDK

**Status:** 🚧 Planned — no content yet.

Anthropic's Agent SDK (`claude-agent-sdk`) — the first-party agent framework
that ships with Claude, and the Anthropic counterpart to `OpenAI_Agents_SDK/`
and `Google_ADK/` in this same phase.

| Subfolder | Scope |
|---|---|
| `01_Foundations/` | Agent construction, the built-in tool loop, permissions |
| `02_Core_Capabilities/` | Tools, subagents, hooks, sessions |
| `03_Multi_Agent_Patterns/` | Orchestration and delegation across agents |
| `04_Applications/` | Real-world builds |

## Boundary — read before adding content here

This track owns the **Agent SDK**, not the raw Messages API. Building a coding
agent by hand on `from anthropic import Anthropic` is a *coding-tool* subject
and lives in `04_AI_Coding_Tools/Claude_API_Primitives/`.

The split is the same one that keeps this phase coherent: this phase owns
frameworks *the model vendor ships*; Phase 11 owns AI coding tools as a subject
of study. Added 2026-09-19, when `Claude_API_and_Agent_SDK/` was renamed to
`Claude_API_Primitives/` — its old name claimed this track's territory while
containing only raw-API material.
