# Chapter 1: Foundations — How Does LangGraph Work?

> Master the building blocks before writing agents.

## What You'll Learn

- How **state** flows through a LangGraph graph
- How to create **nodes** and connect them with **edges**
- How to add **conditional routing** for dynamic workflows
- How to integrate **LLMs** and manage conversation history
- How to give LLMs **tool-calling** capabilities
- How to build a **ReAct agent** — the foundational pattern for AI agents
- How to validate state with **Pydantic**

## Prerequisites

- Basic Python (functions, classes, dictionaries)
- An API key for OpenAI, Groq, or Databricks

## Notebooks

| # | Notebook | What You'll Learn | Key Concepts |
|---|---|---|---|
| 1 | [State and Graph Basics](01_State_and_Graph_Basics.ipynb) | Define state, create nodes, wire them into a graph | `StateGraph`, `TypedDict`, nodes, edges, reducers |
| 2 | [Conditional Routing](02_Conditional_Routing.ipynb) | Make graphs take different paths based on conditions | `add_conditional_edges`, routing functions |
| 3 | [LLM-Powered Chatbot](03_LLM_Powered_Chatbot.ipynb) | Integrate LLMs and manage conversation history | Chat models, message history, streaming |
| 4 | [Augmented LLM with Tools](04_Augmented_LLM_with_Tools.ipynb) | Give LLMs the ability to call external tools | `@tool`, `bind_tools()`, `ToolNode` |
| 5 | [ReAct Agent](05_ReAct_Agent.ipynb) | Build a reasoning agent that thinks, acts, and observes | ReAct loop: Reason → Act → Observe |
| 6 | [Pydantic State Validation](06_Pydantic_State_Validation.ipynb) | Validate state with Pydantic for robust agents | `BaseModel` vs `TypedDict`, runtime validation |

## What's Next?

You can now build a basic agent. Move to **[Chapter 2: Core Capabilities](../02_Core_Capabilities/)** to learn memory, human-in-the-loop, subgraphs, and more.
