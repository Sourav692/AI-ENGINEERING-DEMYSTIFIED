# CLAUDE.md — 07_Deep_Agents

Chapter-specific guidance for this directory. See the project-root `CLAUDE.md` for repo-wide conventions (package manager, env vars, notebook conventions) — those still apply here.

## What this chapter is

Multi-agent orchestration built on the `deepagents` library (not plain LangGraph notebooks like Chapters 1–6). Vendored in from the standalone `Deep_Agent_Demystified` repo — no separate environment: it runs off the project-root `pyproject.toml`, which already includes `deepagents`, `databricks-langchain`, `databricks-sdk`, `langgraph`, and `tavily-python`.

## Running

```bash
# From the project root, with the root env active (uv pip install -e ".[dev]")
cd 07_Deep_Agents

# Default: FilesystemBackend (no code execution)
python examples/simple_coding_agent.py

# With long-term memory (cross-thread persistence via JSON, upgradeable to PostgresStore)
python examples/long_term_memory_agent.py

# With code execution enabled: add USE_SANDBOX=true to .env first
```

The standalone deployable version (FastAPI backend + frontend, Docker) lives in `app/` — see `app/README.md`. Its `app/requirements.txt` is separate from the root project (fastapi/uvicorn/psycopg, mirroring the `fullstack` extra), consistent with how `06_Production/fullstackapp/` is structured. `app/docker-compose.yaml` binds backend port **8000**, same as `06_Production/fullstackapp` — don't run both stacks at once.

## Architecture

```
Orchestrator (Claude Opus via Databricks)
├── memory-manager         Saves, recalls, and organizes long-term memories
├── senior-developer       Plans, writes, and delivers complete Python projects
├── code-reviewer          Reviews code for bugs, style, and best practices
├── research-agent         Web research via Tavily
└── Analytics agents (Databricks Genie): aia-customer-analytics, aia-distribution-channels,
    aia-policy-underwriting, aia-claims-analytics
```

Each agent's behavior is defined by a `SKILL.md` under `skills/<agent-name>/`.

Three code-execution backends (`deepagents.backends`): `FilesystemBackend` (virtual, no execution — safe default), `LocalShellBackend` (executes on host — local dev only), `LangSmithSandbox` (cloud isolation — requires a LangSmith plan).

## Prerequisites

Chapters 1–5 (LangGraph fundamentals through design patterns). Also needs a Databricks workspace (Genie-based analytics agents) and a Tavily API key (research agent) — both already covered by the root `CLAUDE.md`'s env var list.
