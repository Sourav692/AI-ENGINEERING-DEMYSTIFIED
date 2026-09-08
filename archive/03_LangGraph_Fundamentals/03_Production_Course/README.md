# Archived: `03_LangGraph_Fundamentals/03_Production_Course/`

This folder held 8 notebooks converted from a "production course" `.py` script set
(`01_langgraph_core.py` … `08_tool_calling_agent.py` — see the original concept map,
`langchain_langgraph_concepts.md`, which was removed separately as it described a
codebase no longer present in this repo).

After reviewing all 8 against the existing, already-formatted Phase 3 content:

## Relocated (kept — covered new ground)

| Notebook | New location | Why kept |
| --- | --- | --- |
| `05_checkpointing.ipynb` | `02_Core_Capabilities/01_Checkpointing/01_Checkpointing.ipynb` | Checkpointing/persistence (`MemorySaver`, thread IDs, resume/replay) had no home anywhere in Phase 3 — filled a real gap (`02_Core_Capabilities/` numbering skipped `01_`). |
| `04_cycles_loops.ipynb` (+ `graph_code.png`) | `02_Core_Capabilities/08_Cycles_and_Loops/01_Cycles_and_Loops.ipynb` | Cyclic graphs / self-correcting agents via conditional edges routing backward — not covered elsewhere in Phase 3. |
| `07_error_handling.ipynb` | `02_Core_Capabilities/07_Retries/02_Manual_Reliability_Patterns.ipynb` | Broader reliability patterns (manual retry+backoff, circuit breaker, fallback models, LangSmith tracing) — distinct from and complementary to `01_Retries.ipynb`, which only covers LangGraph's native `RetryPolicy`. |
| `08_tool_calling_agent.ipynb` | `01_Foundations/12_Tool_Calling_with_Error_Handling.ipynb` | Mostly overlapped with `01_Foundations/05_Augmented_LLM_with_Tools.ipynb` + `06_ReAct_Agent.ipynb`, but its "tool that fails gracefully" section — a tool designed to raise, plus a demo exercising that error path — wasn't covered by either. |

## Archived here (superseded — fully covered elsewhere, in more depth)

| Notebook | Superseded by | Why |
| --- | --- | --- |
| `01_langgraph_core.ipynb` | `01_Foundations/01_State_and_Graph_Basics.ipynb` + `02_MessageState.ipynb` | Foundations' pair is ~2.6x deeper: same state/reducer/multi-node concepts, plus a dedicated "reducer overwrite problem" section and LLM integration that this notebook lacks. |
| `02_first_graph.ipynb` | `01_Foundations/01_State_and_Graph_Basics.ipynb` | A smaller retread of the exact same define-state → nodes → edges → build → run flow. |
| `03_conditional_edges.ipynb` (+ `graph_complex.png`) | `01_Foundations/03_Conditional_Routing.ipynb` | Core routing mechanic already owned by Foundations/03; this notebook's own "conditional loop" demo overlaps with the relocated `08_Cycles_and_Loops/01_Cycles_and_Loops.ipynb`. It also never had a title cell or learning objectives (converted straight from `.py`, unformatted). |
| `06_human_in_loop.ipynb` | `02_Core_Capabilities/03_Human_in_the_Loop/01_HITL_Mechanics.ipynb` + `02_HITL_Patterns.ipynb` | That pair is ~5x deeper (95 cells vs. 18): mechanics (`interrupt`, `interrupt_before`/`after`, resume lifecycle) *and* applied patterns (approve/reject, edit/review, tool-call review, a generic review wrapper) that this notebook doesn't reach. |

## Restoring one

```bash
git mv archive/03_LangGraph_Fundamentals/03_Production_Course/<file> 03_LangGraph_Fundamentals/<wherever>/
```
