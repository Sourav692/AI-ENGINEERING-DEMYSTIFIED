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
- Six A2A notebooks under `A2A/02_Building_Agents_with_A2A/` and `A2A/03_Applications/` cite the app by its old path `09_Agent_Protocols/MCP/mcp_a2a_agentic_rag/` in markdown cells. It moved under `04_Applications/` on 2026-09-19; reorganizations don't edit notebook content, so fix those only when editing those notebooks for other reasons.


- Don't add protocol-*using* applications that are really about something else. `04_Applications/mcp_a2a_agentic_rag/` is the exception and lives here as the single canonical copy: A2A + MCP servers are its substance, RAG is the payload. Confirmed 2026-09-19 — earlier docs claimed a second copy under Phase 8, but none exists.
