# Chapter 6: Production — How Do I Ship It?

> Deploy your agents as full-stack apps, test them, and build interactive UIs.

## What You'll Learn

- Build a **full-stack agent app** with FastAPI, Angular, and PostgreSQL
- Write **unit tests** for LangGraph nodes with pytest
- Ship **interactive Streamlit apps** for document analysis and knowledge graphs

## Prerequisites

- [Chapter 1](../01_Foundations/) through [Chapter 4](../04_Agents/) completed
- Docker (for full-stack app)
- Google API key (for Streamlit apps)

## Content

### Full-Stack App (`fullstackapp/`)

A production application demonstrating human-in-the-loop agent workflows:

```
fullstackapp/
├── backend/            # FastAPI (async) + LangGraph workflows
│   └── workflows/      # Football stats, news, text generation, human approval
├── frontend/           # Angular UI
└── docker-compose.yml  # One-command deployment with PostgreSQL
```

```bash
cd fullstackapp
docker compose up
# Backend: http://localhost:8000 | Frontend: http://localhost:5555
```

### Unit Testing (`unit_tests/`)

Test LangGraph agents with pytest:

```bash
cd unit_tests
pytest
```

Covers: pytest fixtures, mocked LLMs, node-level testing, structured assertions.

### Streamlit Apps (`streamlit_apps/`)

| App | What It Does | Run With |
|---|---|---|
| `doc-entity-extractor/` | Extract entities from documents | `cd doc-entity-extractor && streamlit run app.py` |
| `knowledge-graphs-with-langextract/` | Build knowledge graphs from text | `cd knowledge-graphs-with-langextract && streamlit run app.py` |

## What's Next?

Move to **[Chapter 7: Deep Agents](../07_Deep_Agents/)** to build multi-agent systems with code execution.
