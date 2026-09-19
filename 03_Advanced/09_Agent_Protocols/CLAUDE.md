<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 09 — Agent Protocols

**Owns:** inter-agent and tool protocols. Stage `03_Advanced/`.

| Track | State | Content |
|---|---|---|
| `MCP/` | Built | Foundations (Anthropic + Educative), building servers (Educative Mastering + Databricks Apps), building clients (MCP Essential), applications (Udemy MCP Mastery), plus `mcp_a2a_agentic_rag/` |
| `ACP/` · `A2A/` | Planned | scope READMEs only |

## Conventions here

- Needs the `protocols` extra — `fastmcp`, `a2a-sdk`, `google-adk`, `databricks-mcp`.
- **9 dependency manifests in this phase** — most MCP sub-projects are self-contained apps with their own `requirements.txt`/`pyproject.toml` and are meant to run in their own environment, not the root one.
- Track shape here is `01_Foundations / 02_Building_Servers / 03_Building_Clients / 04_Applications` — a capability progression, not a learning arc. Match it.

## Don't

- Don't add protocol-*using* applications that are really about something else. `mcp_a2a_agentic_rag/` also exists under Phase 8 as RAG-first — that duplication was a deliberate decision, not an accident to clean up.
