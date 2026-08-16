# Chapter 2: Core Capabilities — What Can LangGraph Do?

> Learn the platform features that make LangGraph production-ready.

## What You'll Learn

These aren't agentic patterns — they're **LangGraph platform capabilities** that you'll use across all your agents:

- **Memory** — Persist conversations across turns and sessions
- **Routing** — Direct requests to the right handler
- **Human-in-the-Loop** — Add human approval and intervention
- **Advanced State** — Manage complex, nested state
- **Subgraphs** — Compose modular, reusable graph components
- **Async & Streaming** — Build responsive, non-blocking agents

## Prerequisites

- [Chapter 1: Foundations](../01_Foundations/) completed

## Sections

### 1. Memory (`01_Memory/`)

| Notebook | What You'll Learn |
|---|---|
| [Memory and Conversational Agent](01_Memory/01_Memory_and_Conversational_Agent.ipynb) | `MemorySaver`, `SqliteSaver`, thread management, short vs long-term memory |

### 2. Routing (`02_Routing/`)

| Notebook | What You'll Learn |
|---|---|
| [Router Agentic RAG System](02_Routing/01_Router_Agentic_RAG_System.ipynb) | Sentiment-aware routing, category-based knowledge base |

### 3. Human-in-the-Loop (`03_Human_in_the_Loop/`)

| Notebook | What You'll Learn |
|---|---|
| [HITL Basics](03_Human_in_the_Loop/01_HITL_Basics.ipynb) | Human approval gates |
| [Interrupt and Resume](03_Human_in_the_Loop/02_HITL_Interrupt_and_Resume.ipynb) | `interrupt()` and resume mechanisms |
| [State Modification](03_Human_in_the_Loop/03_HITL_State_Modification.ipynb) | Modifying agent state at runtime |
| [Dynamic Breakpoints](03_Human_in_the_Loop/04_HITL_Dynamic_Breakpoints.ipynb) | Flexible breakpoints for dynamic control |

### 4. Advanced State (`04_Advanced_State/`)

| Notebook | What You'll Learn |
|---|---|
| [Advanced State](04_Advanced_State/01_Advanced_State.ipynb) | Complex state management patterns |

### 5. Subgraphs (`05_Subgraphs/`)

| Notebook | What You'll Learn |
|---|---|
| [Subgraphs](05_Subgraphs/01_Subgraphs.ipynb) | Graph composition, modular workflows |

### 6. Async and Streaming (`06_Async_and_Streaming/`)

| Notebook | What You'll Learn |
|---|---|
| [Async and Streaming](06_Async_and_Streaming/01_Async_and_Streaming.ipynb) | Async operations, streaming output |

## What's Next?

You now know what LangGraph can do. Move to **[Chapter 3: RAG](../03_RAG/)** to build retrieval-augmented generation systems.
