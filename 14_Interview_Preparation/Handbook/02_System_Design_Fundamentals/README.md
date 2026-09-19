# Module 02 · System Design Fundamentals

> **Level** 🟢 Foundations · **Docs** 5 · **Time** ~3 h
> **Prerequisites:** Module 00, Module 01

Before you can design an AI system you need the vocabulary and discipline of system design in general — and the specific additions AI makes to it. This module gives you the 12-part framework every design conversation follows, the 15 principles that decide inside each part, the most common architectural trade-off, a worked example that shows the framework correcting a real diagram, and the timed method the whiteboard scripts in Module 09 all use.

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [The 12-Part Framework](01_The_12_Part_Framework.md) | The silent questions behind a design round, the AI-specific components, and the deep callouts: SQL vs NoSQL, statelessness, circuit breakers, reliability vs availability, active-active, short-circuiting | 60 min |
| 2 | [The 15 Principles](02_The_15_Principles.md) | Each principle with its AI-system application; the SCALED mnemonic; how principles sound when narrated rather than recited | 25 min |
| 3 | [Monolith vs Microservices](03_Monolith_vs_Microservices.md) | The trade-off as a sequencing question; the same trade-off in an AI platform; the evolution model | 25 min |
| 4 | [Worked Example — The Travel Agent](04_Worked_Example_Travel_Agent.md) | Five structural mistakes in a published multi-agent diagram and how to fix them; five questions to ask of any agent architecture | 30 min |
| 5 | [The 60-Minute Whiteboard Method](05_The_60_Minute_Whiteboard_Method.md) | The six-step timed method behind every script in this handbook; what each step must produce; the three artefacts to prepare | 30 min |

## How this module connects

- Doc 1's AI additions (model gateway, semantic cache, orchestrator, tool layer, guardrails) each get a full treatment in Levels 2 and 3.
- Doc 4's five fixes are the first pass at the multi-agent judgement Module 07 develops.
- Doc 5 is the skeleton of the four full scripts in [Module 09 · whiteboard_scripts/](../09_AI_System_Design_Casebook/whiteboard_scripts/). Read it now; return to it before reading them.

## Checkpoint

You are ready for Level 2 when you can:

- Walk the 12 parts for a system you know, naming the cost of every component you introduce.
- Explain a circuit breaker's three states and the cascade it prevents.
- Say why a modular monolith is the right starting shape and what pressure justifies extracting a service.
- Spot the five structural mistakes in the original travel-agent diagram.
- Write the six-step time budget from memory and state what Step 1 and Step 4 must each produce.

**Next →** [Module 03 · Robust Agents](../03_Robust_Agents/README.md)
