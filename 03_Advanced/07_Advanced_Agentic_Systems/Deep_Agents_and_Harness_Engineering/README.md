# Chapter 7: Deep Agents — How Do I Build Multi-Agent Systems?

> Build production multi-agent systems with code execution capabilities.

## What You'll Learn

- Orchestrate **multiple specialized agents** that collaborate on complex tasks
- Define **reusable skills** that control agent behavior
- Configure **code execution backends** (filesystem, local shell, cloud sandbox)

## Prerequisites

- [Chapter 1](../01_Foundations/) through [Chapter 5](../05_Agentic_Design_Patterns/) completed
- Databricks workspace (for Genie-based analytics agents)
- Tavily API key (for research agent)

## Architecture

```
Orchestrator (Claude Opus via Databricks)
│
├── memory-manager         Saves, recalls, and organizes long-term memories
├── senior-developer       Plans, writes, and delivers complete Python projects
├── code-reviewer          Reviews code for bugs, style, and best practices
├── research-agent         Conducts web research via Tavily
│
└── Analytics Agents (Databricks Genie)
    ├── aia-customer-analytics       Customer segmentation, retention, demographics
    ├── aia-distribution-channels    Agent performance, sales channels
    ├── aia-policy-underwriting      Premiums, renewals, product mix
    └── aia-claims-analytics         Claims, fraud scores, processing times
```

## Long-Term Memory

`long_term_memory_agent.py` extends the base agent with persistent long-term memory backed by a JSON file on disk (`long_term_memories.json`).

**How it works:**
- **`save_memory`** — stores facts, preferences, decisions with category labels
- **`recall_memories`** — searches stored memories by keyword or category
- **`forget_memory`** — removes outdated or unwanted memories
- **`memory-manager` subagent** — specializes in deciding what to remember and when

**Persistence:** memories are saved to `long_term_memories.json` on every write, so they survive across script restarts. Type `new` at the prompt to start a fresh thread while keeping all memories.

**Upgrading to PostgresStore:** for production, replace the JSON file with `PostgresStore` for multi-user support and concurrent access (see commented example in the script).

## Backends

| Backend | Code Execution | Isolation | When To Use |
|---|---|---|---|
| `FilesystemBackend` | No | Virtual mode | Safe default — file operations only |
| `LocalShellBackend` | Yes | None (host) | Local dev with trusted agents |
| `LangSmithSandbox` | Yes | Cloud | Production (requires LangSmith plan) |

## Quick Start

```bash
# Default: FilesystemBackend (no code execution)
python examples/simple_coding_agent.py

# With long-term memory (cross-thread persistence)
python examples/long_term_memory_agent.py

# With code execution: add USE_SANDBOX=true to .env
python examples/simple_coding_agent.py
```

## Skills

| Skill | Purpose |
|---|---|
| `skills/senior-developer/` | Project planning, code generation, delivery workflow |
| `skills/code-reviewer/` | Bug detection, style review, best practices |
| `skills/research-agent/` | Web research, fact-checking, source synthesis |
| `skills/aia-customer-analytics/` | Customer data queries via Genie |
| `skills/aia-distribution-channels/` | Agent performance queries via Genie |
| `skills/aia-policy-underwriting/` | Policy metrics queries via Genie |
| `skills/aia-claims-analytics/` | Claims and fraud queries via Genie |
| `skills/memory-manager/` | Long-term memory save, recall, and organization |
