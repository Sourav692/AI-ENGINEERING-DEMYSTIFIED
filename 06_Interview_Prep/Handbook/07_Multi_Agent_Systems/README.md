# Module 07 · Multi-Agent Systems

> **Level** 🟠 Scale, Security, Operations · **Docs** 5 · **Time** ~2.5 h
> **Prerequisites:** Modules 01, 04, 05, 06 (docs 2, 4, 5)
> **Reference:** `reference_code/` — a deployed AWS multi-agent platform (read, not run); `diagrams/` — nine per-layer Mermaid files plus the combined architecture

Multi-agent is the most over-reached-for architecture in AI system design. This module gives you the definition (a pipeline with eight steps is still one agent), the default (one agent with good tools), the two triggers that justify escalating, the handoff contract that makes the escalation safe, the failure-isolation and evaluation obligations it creates — and two real systems: a deployed nine-layer research platform, and a production supervisor-to-deep-agent evolution in a regulated industry.

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [When Multi-Agent Is Justified](01_When_Multi_Agent_Is_Justified.md) | Single-agent multi-step vs true multi-agent; the default; the two triggers; the empirical evidence of a monolith failing | 25 min |
| 2 | [Reference Architecture and Handoffs](02_Reference_Architecture_Handoffs.md) | Triage / answer / record / escalation / drafting; the handoff package; permission scope carried, not re-derived; supervisor vs deep-agent shapes | 25 min |
| 3 | [Failure Isolation and Evaluation](03_Failure_Isolation_And_Evaluation.md) | Per-agent breakers, hop caps, health-aware routing; per-agent and per-handoff evaluation; the leak gate across every agent | 20 min |
| 4 | [Case Study — The Research Platform](04_Case_Study_Research_Platform.md) | Nine layers of a deployed AWS system: entry, cache and memory, the four-agent Critic loop, gateway with fallback, output guardrails, storage, LangSmith, PyRIT, Terraform and CI/CD | 45 min |
| 5 | [Case Study — From Supervisor to Deep Agent](05_Case_Study_Supervisor_To_Deep_Agent.md) | Three stages and two pivots; why LangGraph; the eight-node supervisor; four specialists and their trade-offs; governance underneath; results stated honestly | 30 min |

## The reference material

`reference_code/` is the research platform's application, gateway config, red-team dashboard, Terraform and CI workflow. Its `README.md` explains the AWS setup; it is included for reading alongside doc 4, not for local execution. `diagrams/` holds the nine `.mmd` files doc 4 walks through, the combined `ARCHITECTURE.mmd`, and rendered HTML and PNG.

## Checkpoint

You are ready for Module 08 when you can:

- State the definition of multi-agent and say why Module 04's graph is not one.
- Name the two triggers and describe them firing in the AIA Stage 1 failure.
- Write the handoff package and explain why permission scope is carried.
- List the three failure-isolation mechanisms and their handbook analogues.
- Walk the nine layers of the research platform and say which two enterprise properties it lacks.

**Next →** [Module 08 · AgentOps and Platform](../08_AgentOps_And_Platform/README.md)
