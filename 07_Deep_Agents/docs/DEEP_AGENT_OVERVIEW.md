# Deep Agent — Synaptic Command

A multi-agent orchestrator with long-term memory, built on LangGraph and deployed as a Databricks App. The system routes user requests to specialized subagents, each with domain-specific skills and tools, while maintaining persistent memory across conversations.

## Architecture

```
                        ┌─────────────────────┐
                        │     React Frontend   │
                        │  (Synaptic Command)  │
                        └──────────┬──────────┘
                                   │ SSE streaming
                        ┌──────────▼──────────┐
                        │   FastAPI Backend    │
                        │  POST /api/chat      │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │    Orchestrator      │
                        │  (Claude Opus 4.6)   │
                        └──────────┬──────────┘
               ┌───────────┬───────┼───────┬───────────┐
               ▼           ▼       ▼       ▼           ▼
         ┌──────────┐ ┌────────┐ ┌───┐ ┌────────┐ ┌────────┐
         │Developer │ │Research│ │...│ │ Claims │ │ Memory │
         │ Agent    │ │ Agent  │ │   │ │ Agent  │ │Manager │
         └──────────┘ └────────┘ └───┘ └────────┘ └────────┘
```

**Model**: `databricks-claude-opus-4-6` via Databricks Model Serving
**Framework**: LangGraph with `deepagents` library, `MemorySaver` checkpointer
**Streaming**: Server-Sent Events with `stream_mode=["updates", "messages"]`
**Recursion Limit**: 100 (supports complex multi-subagent chains)

---

## Agents

### Orchestrator

The central coordinator. Receives every user message, recalls long-term memory, decides which subagent(s) to delegate to, and synthesizes final responses. It has direct access to all 11 tools and delegates to 8 subagents based on intent.

**Mandatory behavior on every turn:**
1. Call `recall_memories()` to load stored context
2. Call `save_memory()` for anything worth remembering
3. Then handle the user's request via subagents or direct tool use

### Senior Developer

Plans, writes, and delivers complete Python projects. Follows a structured workflow: name the project, plan with TODOs, write code, create README, run code review, then deliver.

| Tool | Purpose |
|---|---|
| `name_project` | Create a project folder (local + UC Volume) |
| `write_project_file` | Write files to Databricks Unity Catalog Volume |
| `list_project_files` | List files in a project folder |

**Output**: Project files persisted at `/Volumes/aia_multi_agent_catalog/default/agent_projects/{project-slug}/`

### Code Reviewer

Reviews Python code for bugs, style issues, and best practices. Checks correctness, edge cases, PEP 8 compliance, type hints, and simplicity. Produces structured feedback with severity ratings.

**No tools** — operates on code context provided by the orchestrator.

### Research Agent

Conducts in-depth web research using Tavily search. Searches strategically (broad then narrow), synthesizes findings, and cites sources with URLs.

| Tool | Purpose |
|---|---|
| `internet_search` | Web search via Tavily API (general/news/finance topics) |

### Memory Manager

Manages long-term memory — saving, recalling, and organizing information across conversations. Chooses appropriate categories, strips filler while keeping meaningful detail, and confirms before forgetting.

| Tool | Purpose |
|---|---|
| `save_memory` | Store information with a category label |
| `recall_memories` | Search memories by query and/or category |
| `forget_memory` | Delete a specific memory by content match |

### AIA Customer Analytics

Queries customer segmentation, retention, demographics, and claim frequency data via Databricks Genie.

| Tool | Purpose |
|---|---|
| `ask_customer_analytics` | Natural language query against `customer_360` table |

**Data source**: `aia_multi_agent_catalog.silver.customer_360`

### AIA Distribution Channels

Queries agent performance, sales channels, premium volumes, and top performers via Databricks Genie.

| Tool | Purpose |
|---|---|
| `ask_distribution_channels` | Natural language query against `agent_performance` table |

**Data source**: `aia_multi_agent_catalog.gold.agent_performance`

### AIA Policy & Underwriting

Queries policy volumes, renewal rates, product mix, and underwriting metrics via Databricks Genie.

| Tool | Purpose |
|---|---|
| `ask_policy_underwriting` | Natural language query against policy tables |

**Data sources**: `aia_multi_agent_catalog.gold.policy_performance`, `aia_multi_agent_catalog.silver.enriched_policies`

### AIA Claims Analytics

Queries claim counts, amounts, processing times, fraud scores, and regional breakdowns via Databricks Genie.

| Tool | Purpose |
|---|---|
| `ask_claims_analytics` | Natural language query against claims/fraud tables |

**Data sources**: `aia_multi_agent_catalog.gold.claims_summary`, `aia_multi_agent_catalog.gold.fraud_analysis`, `aia_multi_agent_catalog.silver.enriched_claims`

---

## Memory Layers

The system operates with three distinct memory layers, each serving a different temporal scope:

### 1. Conversation Memory (Short-Term)

**Scope**: Single conversation thread
**Backend**: LangGraph `MemorySaver` checkpointer (in-memory)
**Lifecycle**: Persists for the duration of the app process; lost on restart

The LangGraph checkpointer maintains the full message history for each thread. When a user selects a previous thread, the backend retrieves the state via `agent.get_state(config)` and replays the message history to the frontend.

### 2. Long-Term Memory (Cross-Conversation)

**Scope**: All conversations, all threads, persists indefinitely
**Backend**: Delta table in Unity Catalog — `aia_multi_agent_catalog.default.agent_memories`
**Operations**: Save, recall (search), forget (delete)

| Column | Type | Purpose |
|---|---|---|
| `id` | STRING | UUID primary key |
| `user_id` | STRING | User identifier (defaults to `default-user`) |
| `content` | STRING | The memory content |
| `category` | STRING | Organization label (preference, fact, decision, project, feedback) |
| `saved_at` | TIMESTAMP | When the memory was created |

The orchestrator is instructed to **proactively** use memory on every turn — recalling at the start and saving anything noteworthy before proceeding. Memory categories help organize different types of information:

- **preference** — User likes, dislikes, style choices
- **fact** — Name, role, team, expertise
- **decision** — Architectural choices, tech stack picks
- **project** — Task requests and project context
- **feedback** — Corrections or praise about agent behavior

The Memory Panel in the frontend provides a read-only view of all stored memories with real-time refresh.

### 3. Project Artifact Storage (Persistent Files)

**Scope**: Project files created by the Senior Developer agent
**Backend**: Unity Catalog Volume — `/Volumes/aia_multi_agent_catalog/default/agent_projects/`
**Access**: Databricks SDK `files.upload()` API (not FUSE mount, which is unavailable in Databricks Apps containers)

When the developer agent builds a project, files are written to a UC Volume using the SDK API. This ensures project artifacts survive app redeployments and are accessible from notebooks, jobs, and other Databricks workloads.

```
/Volumes/aia_multi_agent_catalog/default/agent_projects/
  ├── csv-parser-cli/
  │   ├── .project
  │   ├── main.py
  │   ├── README.md
  │   └── tests/
  ├── email-validator/
  │   ├── .project
  │   └── main.py
  └── ...
```

---

## Data Layer — Databricks Genie Spaces

Four Genie spaces provide natural-language SQL interfaces to structured insurance data in Unity Catalog:

| Genie Space | Space ID | Domain |
|---|---|---|
| Customer Analytics | `01f1272d4de1188cac8feeb7e71bdb69` | Segmentation, retention, demographics |
| Distribution Channels | `01f1272d4d271203ad122e9280470248` | Agent performance, sales channels |
| Policy & Underwriting | `01f1272d4c6b1fb49223785ab841befd` | Premiums, renewals, product mix |
| Claims Analytics | `01f1272d4ba6144ba75d868762f1925d` | Claims, fraud, processing times |

Each Genie space wraps curated gold/silver Delta tables and translates natural language questions into SQL, returning structured results with descriptions and suggested follow-up questions.

---

## Frontend — Synaptic Command UI

A React single-page application with a neural-inspired dark theme:

- **Thread Sidebar** — Conversation list with create/rename/delete
- **Agent Topology Bar** — Visual map of all 8 agents with active-state glow and hover tooltips
- **Chat Area** — Markdown rendering, code blocks with syntax highlighting, tables, tool call chips
- **Execution Graph** — Real-time DAG showing agent/tool flow during streaming (left sidebar)
- **Memory Panel** — Collapsible right panel showing all stored long-term memories
- **Animations** — Sonar ripple on orchestrator, energy pulse along spine, idle breathing on input, staggered message entrance

---

## Deployment

Deployed as a Databricks App (`deep-agent-memory`):

```bash
# Build frontend
cd app/frontend && npm run build

# Deploy to Databricks
databricks workspace import-dir app /Workspace/Users/<user>/deep-agent-memory/app --profile DEFAULT --overwrite
databricks apps deploy deep-agent-memory --profile DEFAULT
```

**Runtime**: The FastAPI backend serves both the API and the static React build. The agent initializes lazily on first request to avoid startup crashes if credentials aren't immediately available.
