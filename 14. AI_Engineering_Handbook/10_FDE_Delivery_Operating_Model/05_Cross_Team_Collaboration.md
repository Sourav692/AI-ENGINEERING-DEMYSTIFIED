# Cross-Team Collaboration

> **Level** 🔴 The FDE Role · **Module** 10 · **Doc** 5 of 7 · **Time** ~20 min
> **Prerequisites:** [A Day in the Life](01_A_Day_In_The_Life.md)
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/10. Cross Team Collaboration.md`

## Why this matters

*"Tell me about a time you led a cross-team data or AI project with multiple stakeholders. How did you ensure alignment, ownership and effective communication?"* The hard part of a cross-team AI platform is rarely the technology — it is aligning teams with different priorities and tightly coupled dependencies. Naming that up front, before any technical detail, is what signals senior thinking. This document is a worked answer with the three mechanisms that make it more than "we had a lot of syncs": a RACI, a tiered communication cadence, and a conflict resolved by an interface rather than by one side losing.

## The example

A global data and AI platform delivered to generate seller and executive insights. Five stakeholder groups, tightly coupled:

```
                Software Teams
              (upstream apps & APIs)
                       │
Business Stakeholders  │  Data Engineering
  (success metrics) ───┼─── (ingestion & lake)
                Global Data & AI
                    Platform
                       │
  Project Manager      │      AI/ML Engineers
(timelines & coord.) ──┴── (forecasting models)
```

Software teams own upstream data and APIs; data engineering builds ingestion and the lake; AI/ML engineers build forecasting and insight models; the PM manages timelines and coordination; business stakeholders define success metrics and consume outputs. Each has a different stake and a different definition of "done". The key challenge: conflicting priorities and dependencies coupled tightly enough that one team's delay cascades.

## Mechanism 1 — Ownership via RACI

To remove ambiguity, a RACI across every major workstream — who is **R**esponsible for doing the work, **A**ccountable for the outcome, **C**onsulted before decisions, **I**nformed after them:

| Workstream | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Data ingestion | DE team | Data platform lead | Software teams | PM, business |
| Data modelling (lake) | DE team | Data platform lead | AI engineers | PM |
| ML forecasting models | AI engineers | ML lead | DE team, business | PM |
| API / data access | Software teams | Engineering manager | DE team | PM, business |
| Dashboards and insights | BI / AI team | Product owner | Business stakeholders | PM |
| Program delivery | Project manager | Program sponsor | All teams | Leadership |

A workstream with an unclear owner is where cross-team projects quietly stall. Exactly one accountable owner per deliverable eliminated ownership confusion, sped up decisions and put accountability at every stage. Module 10 doc 4's gates are the same idea with harder edges: a named role that may sign, and no one else.

## Mechanism 2 — Structured communication, not more meetings

A tiered cadence matching frequency to altitude:

```
📌 Daily async updates — shared tracker: progress, risks, blockers
                │
📌 Weekly cross-team sync — dependencies and decisions only
                │
📌 Bi-weekly executive update — impact, risks, progress

Higher frequency, more detail  →  lower frequency, more altitude
```

Each tier answers a different question: the daily tracker keeps peers unblocked; the weekly sync resolves cross-team dependencies; the bi-weekly update keeps leadership informed without pulling them into detail. Four rules made it work:

- **No status-only meetings.** Every interaction must unblock or decide something. A meeting that only reports status is a written update that got a calendar invite.
- **Single source of truth.** One tracking system — not five spreadsheets and a Slack thread each claiming to be current.
- **Write-first culture.** Decisions documented before discussion, so meetings resolve disagreements instead of generating the first draft of them.
- **Fast escalation.** Blockers raised within 24 hours. A dependency that sits unescalated for a week is how coupled workstreams cascade into delay — the human version of Module 10 doc 3's automatic day-3 escalation.

**Bridging technical and business:** technical issues translated into business impact — *"data delay affects forecast accuracy and seller decisions"*, not *"the ingestion job failed"*. The customer continuously engaged, not briefed at delivery.

## Mechanism 3 — Conflict resolved by an interface

The conflict: software teams prioritised speed of feature delivery; DE and AI teams needed stable, high-quality data. Neither was wrong — they were optimising for different stages of the same pipeline.

```
Software Teams              DE / AI Teams
want: speed          need: stable, high-quality data
        └───────────┬───────────┘
                Data Contracts
                     │
              Phase 1: Reliable core dataset
                     │
              Phase 2: Advanced features
```

**Data contracts** turned an ownership argument into an interface agreement, and **two-phase delivery** balanced speed and reliability instead of forcing one team to lose: phase one shipped a reliable core dataset; phase two layered advanced features once the foundation was stable. Notice the shape — it is the same as narrowing a first build to prove a model before expanding (doc 1), and the same as Module 05's staged rollout: earn trust on the stable core, then extend.

## Execution and outcome

Workstreams aligned to RACI ownership; centralised dependency tracking visible to everyone, not just the PM; regular integration checkpoints before divergence became expensive.

Delivered a scalable global data and AI platform — better demand forecasting, reduced stockouts and wastage — and, arguably more valuable, **a repeatable collaboration model** other cross-team programmes reused without rebuilding the RACI and cadence from scratch. That last clause is doc 2's senior bar: not "I built a platform" but "I built a way of working other teams now reuse".

## Key learnings

- Clear ownership via RACI significantly improves execution speed.
- Communication must be intentional and structured, not frequent — more meetings is not more alignment.
- Early alignment prevents late-stage risks that are far more expensive after integration.

## Why the answer works

It demonstrates cross-team complexity specifically (five named groups with conflicting priorities), shows structured ownership with the actual matrix, highlights communication maturity as a tiered cadence, includes a real conflict resolved with a concrete mechanism and tied to measurable results, and is about *how the work got coordinated*, not just what got built — which is exactly what the question is designed to surface.

## Checkpoint

- Name the five stakeholder groups and what each owns.
- What does each letter of RACI mean, and why does "exactly one A" matter?
- Describe the three-tier cadence and the question each tier answers.
- What was the conflict, and what two mechanisms resolved it without a loser?
- Why is "a repeatable collaboration model" the more senior outcome than the platform itself?

**Next →** [Module Reference](06_Module_Reference.md)
