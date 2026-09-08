# Module 05 · Agentic Workflow Platforms

> **Level** 🟡 Building Production Systems · **Docs** 7 · **Time** ~3 h reading + 2 h lab
> **Prerequisites:** Module 01 doc 3, Module 03
> **Lab:** `project/` — the Agent Platform. No API key; 21 deterministic tests in under a second.

This module is the **Agent Platform** project taught as a course. The prompt: *design an AI agent platform for non-technical users to configure workflow automations across multiple channels.* The insight: the hard part is not running an agent, it is letting someone who cannot read code trust that an automation will only do what they meant — even when the model is wrong, the network retries, or the server crashes mid-run. The project contains no LLM at all; every safety property is proven with a deterministic test, including the negative cases.

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [The Problem in Plain English](01_The_Problem_In_Plain_English.md) | The prompt unpacked; "the hard part is trust"; the three layers; the six silent guarantees; why the three source projects share one shape | 30 min |
| 2 | [Canonical Events, Channels and Routing](02_Canonical_Events_And_Channels.md) | Layer 1 — translate once at the edge; priority (design-time) vs the entity lock (run-time); why both | 25 min |
| 3 | [Determinism Over Free Text](03_Determinism_Over_Free_Text.md) | The five determinism controls; the workflow as data the orchestrator walks; typed tools; the five non-technical-user constraints and which are built | 30 min |
| 4 | [Durability and Idempotency](04_Durability_And_Idempotency.md) | Layer 2 — the checkpoint is `next_step_index`; one loop for run and resume; the key is on the action; two bugs about what idempotency must cover | 35 min |
| 5 | [Approvals, Spend Caps and Staged Rollout](05_Approvals_Spend_Caps_Staged_Rollout.md) | Layer 3 — the five-rule guardrail; step budget vs spend cap; autonomous ≠ unlimited; the four gates and why four; separation of duties; the negative-control demo | 40 min |
| 6 | [Module Reference](06_Module_Reference.md) | Every function in `src/agent_platform` | reference |
| 7 | [Coverage Map](07_Coverage_Map.md) | What is proven vs cheat-sheet; what the no-LLM choice bought and cost | 20 min |

## The lab

```bash
cd project
python scripts/run_workflow_demo.py        # happy path: rollout, routing conflict, approval, idempotent retry, crash + resume
python scripts/demo_guardrail_failure.py   # the negative-control demo — seven denials
python -m pytest -q                        # 21 passed
jupyter notebook notebooks/02-hands-on.ipynb
```

Read `src/agent_platform/orchestrator.py` with doc 4 open and `guardrails.py` with doc 5 open. Together they are under 300 lines.

## Checkpoint

You are ready for Level 3 when you can:

- Restate the problem in one breath and name the three layers.
- Draw the orchestrator loop and explain why resume and run share it.
- Say why the idempotency key is on the action and what "every side effect" includes.
- List the five guardrail rules and explain why autonomous does not mean unlimited.
- Name the four rollout gates, the question each answers, and who may promote.

**Next →** [Module 06 · Cross-Cutting Concerns](../06_Cross_Cutting_Concerns/README.md)
