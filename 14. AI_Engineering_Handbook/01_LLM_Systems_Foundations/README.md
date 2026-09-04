# Module 01 · LLM Systems Foundations

> **Level** 🟢 Foundations · **Docs** 5 · **Time** ~2.5 h reading + 2 h lab
> **Prerequisites:** Module 00; Python; having called an LLM API once

Two ideas underlie every system in this handbook: **retrieve** (find the right text before you generate) and **act** (let the model choose an action, execute it, feed the result back). This module builds both from first principles, ending with a working agent loop you can write on a whiteboard and then express in LangGraph.

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [What RAG Actually Is](01_What_RAG_Actually_Is.md) | The two-box idea; why enterprise changes it; the ingestion and query pipelines and the two security positions in them | 20 min |
| 2 | [Chunking, Retrieval and Fusion](02_Chunking_Retrieval_Fusion.md) | Structure-aware chunking; dense vs BM25 and why you need both; RRF, Multi-Query, HyDE, decomposition, reranking | 30 min |
| 3 | [What an Agent Actually Is](03_What_An_Agent_Actually_Is.md) | Tools, brain, loop; the `destructive` flag; why the hard part is trust, not mechanics | 25 min |
| 4 | [The Tool-Calling Loop From Scratch](04_Tool_Calling_Loop_From_Scratch.md) | `Agent.run` line by line; `Session`; the three exits; swapping a rule-based brain for an LLM | 35 min + lab |
| 5 | [The Same Loop in LangGraph](05_Same_Loop_In_LangGraph.md) | `StateGraph`, reducers, the two nodes and conditional edge; what the framework gives you and what it does not | 30 min + lab |

## The lab

`project/` is the agent tool-calling demo — pure Python, no API key, twelve passing tests.

```bash
cd project
pip install -r requirements.txt     # only needed for the LangGraph half
python -m pytest -q                 # 12 passed
```

Then work through the notebooks in this order:

1. `notebooks/agent_tool_calling_demo.ipynb` — the from-scratch loop, every concept, runnable.
2. `notebooks/langgraph_react_agent.ipynb` — the same loop as a graph.
3. `notebooks/robust_langgraph_tool_calling_agent.ipynb` — checkpointing and interrupts (previews Module 03 and Module 05).
4. `notebooks/agent_tool_calling_demo_openai.ipynb` — the real-LLM brain, if you have a key.

The RAG techniques in docs 1–2 are implemented in Module 04's project; this module teaches the concepts, Module 04 has you build them.

## What each concept maps to in the code

| Concept | `project/src/` |
|---|---|
| Tool, registry, `destructive` flag | `tools.py` |
| Brain contract, rule-based and LLM brains | `brain.py` |
| The loop, `Session`, `RunResult` | `scratch_agent.py` |
| The same loop as a `StateGraph` | `langgraph_agent.py` |
| Confirmation gate, memo, retry, fallback, disambiguation | `robustness.py` → Module 03 |
| Per-call trace | `observability.py` → Module 03 |

## Checkpoint

You are ready for Module 02 when you can:

- Draw the RAG query pipeline and name the two positions that make it secure.
- Explain why hybrid search exists and how RRF merges its results.
- Write the ReAct loop from memory with its guard and its pause-for-confirmation exit.
- Say what LangGraph's `add_messages` reducer does and where the step budget lives in the graph version.
- State, in one sentence, why "the hard part of agents is trust".

**Next →** [Module 02 · System Design Fundamentals](../02_System_Design_Fundamentals/README.md)
