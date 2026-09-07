# Failure Isolation and Evaluation

> **Level** 🟠 Scale, Security, Operations · **Module** 07 · **Doc** 3 of 5 · **Time** ~20 min
> **Prerequisites:** [Reference Architecture and Handoffs](02_Reference_Architecture_Handoffs.md); Module 04 doc 7; Module 06 doc 2
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/09-multi-agent-orchestration.md` §4–5

## Why this matters

The right-hand column of the multi-agent table in doc 1 promised two things: one agent's failure should degrade rather than crash the others, and a wrong final answer should be traceable to the agent that caused it. Neither happens by accident. This document is the short list of what has to be built for those promises to hold — and the reminder that the security bar does not soften because a leak happened *between* agents rather than inside one.

## Failure isolation

**A failure limiter scoped per agent, not shared globally.** One specialist being down must not trip a safeguard that then blocks an unrelated specialist. A circuit breaker on the record system's connector should open for the Record agent and leave the Answer agent untouched. This is Module 06's bulkhead pattern applied at the agent boundary: each specialist has its own pool, its own breaker, its own budget.

**A bounded number of handoffs per case.** Two agents that can hand a case back and forth risk an infinite loop — triage → escalate → triage → … Cap the total hops and force a final outcome — answered, escalated, or failed safely — once the cap is hit. This is Module 01's max-iteration guard, one level up: the same instinct as any hard budget. Halt and report; never let it run forever.

**Partial degradation, not total failure.** If the record system is down, the Answer agent must still be able to answer a pure knowledge question. One specialist's outage must not take down specialists that do not depend on it. Concretely: the triage agent needs to know which specialists are healthy, and a request that needs only healthy ones proceeds.

| Mechanism | Prevents | Analogue elsewhere in the handbook |
|---|---|---|
| Per-agent breaker and budget | One outage becoming a platform outage | Bulkhead (Module 06 doc 2) |
| Hop cap with a forced outcome | Ping-pong loops | Max-iteration guard (Module 01), step budget (Module 05) |
| Health-aware routing | Total failure on partial outage | Graceful degradation (Module 02, Module 04's degrade paths) |

## Evaluating a multi-agent system

**Evaluate each agent, not only the end result.** Did triage route correctly? Did the record agent use the right parameters? Did escalation attach useful context? A wrong final answer could trace back to any one of these. This is the same reason Module 04 separates "was the right information found" from "was the final answer good" — just with more stages to separate. A per-agent golden set: triage cases with expected routes; record cases with expected operations and arguments; escalation cases with expected queue and context fields.

**Handoff correctness as its own measure.** Did the receiving agent get everything it needed, or did it have to guess or re-derive context? An agent that re-asks the user something already in the transcript, or re-runs a retrieval already performed, is a sign the handoff package is under-specified. Measure it directly: fraction of handoffs where the receiver's first action was a lookup the package should have contained.

**The security bar applies the same way everywhere.** A leak caused by one agent forwarding restricted information to the wrong place — an escalation note visible to a broader audience, a drafting agent given a chunk the answer agent should have dropped — is exactly as serious as a leak in the main answer. It does not get a pass because it happened between agents. Module 04's leak gate extends across every handoff: forbidden documents must not appear in *any* agent's context, *any* record it writes, or *any* reply it drafts. Still zero. Still a gate.

## The evaluation shape, extended

```
 Module 04 (single agent)            Module 07 (multi-agent)
 ─────────────────────────           ────────────────────────────────────────────
 retrieval   recall@k, MRR           per agent:   triage route accuracy
 generation  groundedness, refusal                record op + args correctness
 security    leak rate = 0 (gate)                 escalation context completeness
                                                  drafting tone/channel fit
                                     handoff:     completeness (receiver re-derived nothing)
                                     end-to-end:  same three families as before
                                     security:    leak rate = 0 across EVERY agent and handoff (gate)
```

## Interview lens

> *"Three things for failure isolation: a breaker and budget per agent so one specialist's outage stays its own; a cap on handoffs per case with a forced final outcome so two agents can't ping-pong forever; and health-aware triage so a knowledge question still gets answered when the ticketing system is down. For evaluation: score each agent and score the handoff itself, not just the end result — and the leak gate applies across every agent and every handoff, still at zero."*

## Checkpoint

- Name the three failure-isolation mechanisms and the analogue of each elsewhere in the handbook.
- Why does a shared global breaker fail a multi-agent system?
- What does a hop cap force, and why is that better than letting the loop continue?
- Give one per-agent metric for each of the five agents in the reference architecture.
- How would you measure handoff correctness directly?

**Next →** [Case Study — The Research Platform](04_Case_Study_Research_Platform.md)
