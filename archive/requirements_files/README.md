# Archived `requirements.txt` files

These are per-folder dependency files that are **fully superseded by the root
`requirements.txt`** and were not referenced by any README, Dockerfile, or script
next to them. They are kept here only for provenance — nothing installs from them.

Each file sits at its original path under this folder, so
`archive/requirements_files/09_Agent_Protocols/.../requirements.txt` came from
`09_Agent_Protocols/.../requirements.txt`.

## What was moved and why it was safe

| Original location | Packages | Notes |
| --- | --- | --- |
| `01_Theory_and_Foundations/Fine_Tuning_and_RL/01_Foundations/` | 17 | All in root master except `lamini` (single-lab dep) and `packaging` (transitive) |
| `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/` | 29 | All in master except `bs4` (alias of `beautifulsoup4`, which *is* in master) and `pytube` |
| `07_Advanced_Agentic_Systems/Memory_and_State/LangGraph/01_Memory/memory/` | 24 | All in master except `colorlog` |
| `09_Agent_Protocols/MCP/01_Foundations/Anthropic_Rich_Context/` | 6 | All in master except `uv` itself |
| `09_Agent_Protocols/MCP/02_Building_Servers/Databricks_Apps/` | 7 | All in master except `uv` itself |
| `09_Agent_Protocols/MCP/03_Building_Clients/MCP_Essential/01-build-your-own-server-client/clients/mcp-client/` | 78 | A `pip freeze` dump — 46 "extras" are all transitive pins (`certifi`, `anyio`, `attrs`, …) |
| `09_Agent_Protocols/MCP/03_Building_Clients/MCP_Essential/01-build-your-own-server-client/servers/terminal_server/` | 32 | Same — a `pip freeze` dump, 20 transitive pins |
| `09_Agent_Protocols/MCP/03_Building_Clients/MCP_Essential/04-build-streammable-http-mcp-client/` | 13 | All in master except `asyncio-mqtt`, `click`, `flake8` |
| `10_Alternative_Agent_Frameworks/AutoGen/01_Foundations/Some_Simple_Agents/` | 2 | 100% covered by the master's `frameworks` extra |

## What was deliberately NOT archived

**43 per-folder `requirements.txt` files stayed in place** because a Dockerfile,
`render.yaml`, `databricks.yml`, or the README sitting beside them installs from
them by name. Moving those would break documented setup instructions and container
builds. Examples: `13_Projects/LangGraph_Fullstack_Capstone/fullstackapp/backend/`
(Dockerfile), `13_Projects/End_to_End_Medical_Chatbot/` (Dockerfile),
`13_Projects/Automated_Candidate_Interview_Evaluation_System/` (render.yaml),
`14. AI_Engineering_Handbook/07_Multi_Agent_Systems/reference_code/pyrit_dashboard/`
(Dockerfile).

One more stayed put despite having no local reference:

- `10_Alternative_Agent_Frameworks/CrewAI/01_Foundations/Some_Simple_Agents/app/backend/requirements.txt`
  — **CrewAI is deliberately excluded from the root master** (it hard-pins
  `chromadb<1.2`, which cannot coexist with `langchain-chroma` 1.1). That file is
  therefore the only install recipe for that app, not a redundant copy.

## Restoring one

```bash
git mv archive/requirements_files/<original/path>/requirements.txt <original/path>/
```
