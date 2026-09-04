# Module 10 · FDE Delivery and Operating Model

> **Level** 🔴 The FDE Role · **Docs** 7 · **Time** ~3 h + lab
> **Prerequisites:** Module 00 doc 2, Module 02, Module 04 doc 7, Module 05
> **Lab:** `project/` — the Delivery Framework. No API key; 17 deterministic tests.

The forward-deployed engineer's unit of work is the engagement. This module is what that means day to day, how to narrate a delivery end to end, and — as a runnable system — how to take a customer from a scoping document to production in two weeks the same way every time: a reusable accelerator library for speed, and hard, role-gated checkpoints for safety, built as a state machine with the same `Decision` shape as Module 04's access control and Module 05's guardrails.

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [A Day in the Life](01_A_Day_In_The_Life.md) | The three lenses — technical, customer, team — through one day; why they are interdependent; the closing line | 20 min |
| 2 | [End-to-End AI Delivery in Six Stages](02_End_To_End_AI_Delivery_Six_Stages.md) | The six-stage story; do and do not; layered depth; a worked churn answer; the senior bar | 20 min |
| 3 | [Scoping Doc to Production in Two Weeks](03_Scoping_To_Production_In_Two_Weeks.md) | Why two weeks is an asset-reuse problem; the fourteen days; intake refusal; the gate/stage state machine; the accelerator library and reuse rate; Northwind Logistics | 40 min |
| 4 | [Gates, Risks and Metrics](04_Gates_Risks_Metrics.md) | The six gates and who signs; the three deny rules; two pairs of similar gates; risks as checks; the five metrics; when a real gate is still a rubber stamp; the process's own security bar | 35 min |
| 5 | [Cross-Team Collaboration](05_Cross_Team_Collaboration.md) | RACI; a tiered cadence; conflict resolved by data contracts and phasing; the repeatable model as the outcome | 20 min |
| 6 | [Module Reference](06_Module_Reference.md) | Every function in `src/delivery_framework` | reference |
| 7 | [Coverage Map](07_Coverage_Map.md) | What is proven vs described; the scale gap as a tenancy decision | 20 min |

## The lab

```bash
cd project
python scripts/run_engagement_demo.py      # Northwind Logistics — 14 days, every gate in order
python scripts/demo_gate_failure.py        # the negative-control demo — refusals and denials
python -m pytest -q                        # 17 passed
```

Read `src/delivery_framework/gates.py` and `engine.py` with doc 4 open. The whole authority layer is under 200 lines, and it is the same shape as `authz/policy.py` in Module 04.

## The whiteboard script

The full 60-minute script for this prompt is [Module 09 · whiteboard_scripts/04](../09_AI_System_Design_Casebook/whiteboard_scripts/04_Scoping_Doc_To_Deployed_Agent_In_Two_Weeks.md).

## Checkpoint

You are ready for Module 11 when you can:

- Deliver the day-in-the-life closing line and explain the three lenses' interdependence.
- Walk a delivery story through six stages in under five minutes with numbers.
- Draw the gate/stage state machine and say who signs each gate.
- Explain why intake refuses, why seniority is not an override, and why a real gate can still be a rubber stamp.
- Give the RACI and the tiered cadence for a cross-team programme.

**Next →** [Module 11 · Telling the Story](../11_Telling_The_Story/README.md)
