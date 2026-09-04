# Module 03 · Robust Agents

> **Level** 🟡 Building Production Systems · **Docs** 5 · **Time** ~2 h + lab
> **Prerequisites:** Module 01 (the loop and the `execute_tool` black box)
> **Lab:** reuses `../01_LLM_Systems_Foundations/project/` — `src/robustness.py`, `src/observability.py`, `tests/test_agent.py`

Module 01 built the loop and used a safe executor as a black box. This module opens the box. The organising idea: **a model deciding to call a tool is a proposal, never an authorisation** — and everything between the proposal and the real world is a check that exists because of a specific way agents fail.

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [Retry, Fallback, Memoization and the Confirmation Gate](01_Retry_Fallback_Memo_Confirm.md) | `execute_tool` line by line; why gate → cache → retry is the order; transient vs permanent failures; fallbacks that go through the same gate | 35 min |
| 2 | [State, Memory and Sessions](02_State_Memory_Sessions.md) | Run / session / user scopes; checkpointers; the three layers of memory and why enterprise knowledge is not memory | 25 min |
| 3 | [Parallel vs Sequential Tool Calls](03_Parallel_vs_Sequential.md) | Latency as max vs sum; the five rules; who decides | 15 min |
| 4 | [Observability for Tool Calls](04_Observability_For_Tool_Calls.md) | The five statuses; the trace as debugging, cost and audit artefact; from in-memory log to spans | 20 min |
| 5 | [The Eight Guard Checks](05_The_Eight_Guard_Checks.md) | All eight checks in one pipeline; argument validation and disambiguation; why none substitutes for another | 30 min |

## The lab

```bash
cd ../01_LLM_Systems_Foundations/project
python -m pytest -q -k "retry or memo or fallback or disambig or confirmation or session"
```

Then read `src/robustness.py` top to bottom with doc 1 open. It is 130 lines; every line is a decision.

## Checkpoint

You are ready for Module 04 when you can:

- Write `execute_tool` from memory and defend the order of its three sections.
- Explain why a fallback must go through the same gate as the primary.
- Name the three scopes of agent state and where each lives in production.
- List the eight guard checks and the failure each prevents.
- Say, in one sentence, why the model's tool call is a proposal.

**Next →** [Module 04 · Enterprise RAG](../04_Enterprise_RAG/README.md)
