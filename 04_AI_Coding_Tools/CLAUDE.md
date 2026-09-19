<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 11 — AI Coding Tools

**Owns:** AI coding tools as a subject of study — Claude Code, Codex, Cursor, Copilot, and the Agent Skills concept. A top-level stage folder because it is tools you *use* rather than a topic in the learning arc.

| Track | Content |
|---|---|
| `AI_Coding_Tool_Landscape/` | Vendor comparison + a from-scratch toy CLI coding agent |
| `Claude_Code/` | Claude Code specifics |
| `Claude_API_Primitives/` | Building a coding agent by hand on the raw Anthropic Messages API |
| `Agent_Skills/` | What skills are and how to author them |

## Conventions here

- Greenfield — 2 notebooks today. **New vendors (Codex, Cursor, Copilot) are sibling tracks inside this phase.**
- Renamed from `11_Claude_Code_and_AI_Coding_Tools` on 2026-09-19 — the old name baked one vendor into the folder name.

## Don't

- Don't confuse `Agent_Skills/` with the repo's own working skills. This track *teaches* the concept; the live skills are in `.claude/skills/` and `plugins/`.
- `01_AI_Agents_on_the_CLI.ipynb` still references the old phase name **and** the old folder name `Claude_API_and_Agent_SDK/` (3 markdown cells) in its text — reorganizations don't edit notebook content, so fix both only when you're editing that notebook for other reasons.
- **Don't let this phase reclaim the Anthropic Agent SDK.** `Claude_API_Primitives/` owns the raw Messages API only; `claude-agent-sdk` is a first-party agent framework and belongs to `03_Advanced/06_Agent_SDKs_First_Party/Anthropic_Agent_SDK/`. Renamed 2026-09-19 for exactly this reason.
