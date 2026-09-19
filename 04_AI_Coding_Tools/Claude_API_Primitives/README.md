# Claude API Primitives

**Status:** ✅ Built — 1 notebook.

Building a coding agent directly on the Anthropic Messages API, with no agent
framework in between. The point is to see the loop that every coding tool —
Claude Code included — is ultimately running: send messages, get back a
`tool_use` block, execute it yourself, feed the result back as `tool_result`,
repeat until the model stops asking for tools.

| Notebook | Topic |
|---|---|
| `01_Building_a_Coding_Agent_with_Claude_API.ipynb` | The core tool-use loop, a hand-written agentic loop, and multi-turn agentic behaviour — all executed inside a throwaway sandbox |

## Scope

**In scope:** the raw `anthropic` client (`from anthropic import Anthropic`),
tool definitions, the manual agentic loop, sandboxed tool execution.

**Not in scope — and deliberately so:** Anthropic's **Agent SDK**
(`claude-agent-sdk`). That is a first-party *agent framework*, the Anthropic
counterpart to OpenAI's Agents SDK and Google's ADK, so it belongs beside them
in `03_Advanced/06_Agent_SDKs_First_Party/Anthropic_Agent_SDK/` — not here.
This track was renamed from `Claude_API_and_Agent_SDK/` on 2026-09-19 precisely
because the old name claimed both and delivered only the first.

## Notes

- This notebook is a **deliberate exception** to the repo's `helpers.get_llm()`
  convention — the whole subject is the raw provider API, so routing through the
  factory would hide the thing being taught. It reads `ANTHROPIC_API_KEY` from
  the project-root `.env`.
- For the toy from-scratch CLI agent and the vendor comparison, see the sibling
  track `AI_Coding_Tool_Landscape/`. The notebook here contains a section
  explaining exactly how the two differ.
