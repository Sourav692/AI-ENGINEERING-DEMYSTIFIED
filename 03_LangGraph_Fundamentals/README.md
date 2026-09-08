# Phase 3 — LangGraph Fundamentals

**Status:** ✅ Built.

Core LangGraph mechanics only — state, graphs, routing, tools, platform capabilities. RAG, agent builds, and design patterns each have their own dedicated phase elsewhere in the roadmap.

| # | Section | Topic |
|---|---|---|
| 1 | `01_Foundations/` | State/graph basics, MessagesState, conditional routing, tools, ReAct, Pydantic validation, node patterns, runtime context, Command objects, tool-calling error handling (12 notebooks) |
| 2 | `02_Core_Capabilities/` | Checkpointing, routing (incl. an agentic-RAG-router example — kept here since it's also a routing-mechanics demo), human-in-the-loop, advanced state, subgraphs, async/streaming, retries, cycles & loops |

## Prerequisites

- Basic Python (functions, classes, dictionaries)
- An API key for OpenAI, Groq, or Databricks

---

## Chapter 1: Foundations — How Does LangGraph Work?

> Master the building blocks before writing agents.

| # | Notebook | Location | Topics & Functionality Covered |
|---|---|---|---|
| 1 | State and Graph Basics | [01_Foundations/01_State_and_Graph_Basics.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/01_State_and_Graph_Basics.ipynb) | Core building blocks — `StateGraph`, `TypedDict` state schemas, nodes, edges, reducers (including the "reducer overwrite problem" and further reducer examples), and basic LLM integration |
| 2 | MessagesState | [01_Foundations/02_MessageState.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/02_MessageState.ipynb) | The pre-built `MessagesState` base class and its `add_messages` reducer, and extending it with custom state fields alongside `messages` |
| 3 | Conditional Routing | [01_Foundations/03_Conditional_Routing.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/03_Conditional_Routing.ipynb) | `add_conditional_edges`, writing routing functions, and building dynamic, state-based execution paths |
| 4 | LLM-Powered Chatbot | [01_Foundations/04_LLM_Powered_Chatbot.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/04_LLM_Powered_Chatbot.ipynb) | Integrating a chat model into a graph node, `invoke` vs. streaming, and managing conversation history end-to-end |
| 5 | Augmented LLM with Tools | [01_Foundations/05_Augmented_LLM_with_Tools.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/05_Augmented_LLM_with_Tools.ipynb) | Giving an LLM tool access: the `@tool` decorator, `bind_tools()`, and wiring a `ToolNode` into the graph |
| 6 | ReAct Agent | [01_Foundations/06_ReAct_Agent.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/06_ReAct_Agent.ipynb) | The ReAct loop (Reason → Act → Observe): the difference between an augmented LLM and an agent, and feeding tool outputs back to the LLM |
| 7 | Different Graph States | [01_Foundations/07_Different_Graph_States.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/07_Different_Graph_States.ipynb) | Four ways to define graph state: schema-free dictionary state, `TypedDict` with custom reducers, `dataclass` state with defaults, and Pydantic state |
| 8 | Pydantic State Validation | [01_Foundations/08_Pydantic_State_Validation.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/08_Pydantic_State_Validation.ipynb) | `TypedDict` (no runtime enforcement) vs. Pydantic `BaseModel` state (automatic runtime type validation) as a drop-in replacement |
| 9 | Node Patterns | [01_Foundations/09_Node_Patterns.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/09_Node_Patterns.ipynb) | Plain nodes (state-only), config-aware nodes (`RunnableConfig` for thread IDs/metadata), and runtime-context nodes for injecting external dependencies |
| 10 | Runtime Context | [01_Foundations/10_Runtime_Context.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/10_Runtime_Context.ipynb) | Passing external dependencies (DB connections, API keys) into nodes without storing them in state, via a typed `context_schema` |
| 11 | Command Objects | [01_Foundations/11_Command_Objects.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/11_Command_Objects.ipynb) | The `Command` object for updating state and routing in a single return value, `Command[Literal[...]]` type annotations, and graphs that need no explicit edges |
| 12 | Tool-Calling Agents with Graceful Error Handling | [01_Foundations/12_Tool_Calling_with_Error_Handling.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/01_Foundations/12_Tool_Calling_with_Error_Handling.ipynb) | A full tool-calling agent loop (`agent` node + `ToolNode` + conditional edges), execution-trace inspection, and a tool designed to fail gracefully (division by zero) so errors surface to the LLM instead of crashing the graph |

---

## Chapter 2: Core Capabilities — What Can LangGraph Do?

> Learn the platform features that make LangGraph production-ready — not agentic patterns, but capabilities you'll use across all your agents.

> **Note:** Long-term, cross-session memory (Postgres-backed persistence beyond a single
> thread) is covered in
> [Phase 7 — Memory_and_State](../07_Advanced_Agentic_Systems/Memory_and_State/) rather
> than here. This chapter's `01_Checkpointing/` covers the underlying thread-level
> checkpointing mechanism (`MemorySaver`, `SqliteSaver`) that both short-term resume and
> Phase 7's long-term memory are built on.

| Notebook | Location | Topics & Functionality Covered |
|---|---|---|
| Checkpointing | [02_Core_Capabilities/01_Checkpointing/01_Checkpointing.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/01_Checkpointing/01_Checkpointing.ipynb) | How LangGraph snapshots state after every node runs via a checkpointer: in-memory (`MemorySaver`) vs. `SqliteSaver` persistence, thread IDs, and resuming/replaying prior state |
| Router Agentic RAG System | [02_Core_Capabilities/02_Routing/01_Router_Agentic_RAG_System.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/01_Router_Agentic_RAG_System.ipynb) | Customer-support router agent: GPT-4o query categorization (billing/technical/general) and sentiment analysis, dynamic routing to specialized response nodes, RAG over a custom knowledge base |
| Router Agentic RAG System (Modular) | [02_Core_Capabilities/02_Routing/02_Router_Agentic_RAG_System_Modular.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/02_Router_Agentic_RAG_System_Modular.ipynb) | Modularized rebuild of the router above: prompts externalized to `prompts.yaml`, shared `retrieve_knowledge_base_content()` / `generate_support_response()` helpers bound via `functools.partial`, `ChatPromptTemplate` + LCEL categorization |
| HITL Mechanics | [02_Core_Capabilities/03_Human_in_the_Loop/01_HITL_Mechanics.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/03_Human_in_the_Loop/01_HITL_Mechanics.ipynb) | Core interrupt/resume mechanics: the `interrupt()` function, compile-time `interrupt_before`/`interrupt_after`, the resume lifecycle (what re-runs vs. what doesn't), validating human input via repeated `interrupt()` calls in one node |
| HITL Patterns | [02_Core_Capabilities/03_Human_in_the_Loop/02_HITL_Patterns.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/03_Human_in_the_Loop/02_HITL_Patterns.ipynb) | Applied, LLM-backed HITL workflows built on the mechanics above: tool-calling agent with `interrupt_before`, Approve/Reject via `interrupt()` + `Command(goto=...)`, Edit/Review of LLM output, reviewing tool calls before execution |
| Advanced State | [02_Core_Capabilities/04_Advanced_State/01_Advanced_State.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/04_Advanced_State/01_Advanced_State.ipynb) | Separate `input_schema`/`output_schema` vs. internal state on `StateGraph`, and injecting runtime configuration (`RunnableConfig`, `configurable`) into node behavior (e.g. per-request response language) |
| Subgraphs | [02_Core_Capabilities/05_Subgraphs/01_Subgraphs.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/05_Subgraphs/01_Subgraphs.ipynb) | Composing modular graphs: invoking a subgraph directly, embedding a subgraph as a node in a parent graph, and transforming state between a parent's schema and a subgraph's own schema |
| Async and Streaming | [02_Core_Capabilities/06_Async_and_Streaming/01_Async_and_Streaming.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/06_Async_and_Streaming/01_Async_and_Streaming.ipynb) | LangGraph-specific async: a synchronous tool-calling agent baseline, converting to an async node with `ainvoke`, streaming per-node output with `stream_mode="updates"`, token-level streaming with `stream_mode="messages"` and `AIMessageChunk` assembly |
| Async Patterns for Agentic Systems | [02_Core_Capabilities/06_Async_and_Streaming/02_Async_Patterns_for_Agentic_Systems.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/06_Async_and_Streaming/02_Async_Patterns_for_Agentic_Systems.ipynb) | Framework-agnostic `asyncio` deep dive with a fake LLM/tools: coroutines & `gather` vs. `TaskGroup`, streaming with mid-stream tool calls, `Semaphore`/`asyncio.timeout`/`tenacity` retry/cancellation, a multi-agent supervisor, fire-and-forget background logging, `asyncio.to_thread` for blocking SDKs, and a concurrent-user load-testing harness |
| Retries | [02_Core_Capabilities/07_Retries/01_Retries.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/07_Retries/01_Retries.ipynb) | Fault-tolerant nodes with `RetryPolicy`: attaching a retry policy per-node via `add_node(..., retry_policy=...)`, backoff strategy configuration (`max_attempts`, backoff factor), simulating a flaky node and handling exhausted retries |
| Manual Reliability Patterns | [02_Core_Capabilities/07_Retries/02_Manual_Reliability_Patterns.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/07_Retries/02_Manual_Reliability_Patterns.ipynb) | Reliability patterns beyond `RetryPolicy`: manual retry with exponential backoff + jitter, a circuit breaker to stop hammering a failing dependency, fallback models, and LangSmith `@traceable` tracing for observability |
| Cycles and Loops | [02_Core_Capabilities/08_Cycles_and_Loops/01_Cycles_and_Loops.ipynb](https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/03_LangGraph_Fundamentals/02_Core_Capabilities/08_Cycles_and_Loops/01_Cycles_and_Loops.ipynb) | Building cyclic graphs with conditional edges that route back to already-visited nodes: self-correcting code generation that writes, validates, and iteratively fixes its own output |

## What's Next?

You now know how LangGraph works and what it can do. Move to **[Phase 4: Retrieval and RAG](../04_Retrieval_and_RAG/)** to build retrieval-augmented generation systems.
