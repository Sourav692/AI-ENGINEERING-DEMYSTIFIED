# When Multi-Agent Is Justified

> **Level** 🟠 Scale, Security, Operations · **Module** 07 · **Doc** 1 of 5 · **Time** ~25 min
> **Prerequisites:** Module 01 doc 3, Module 02 doc 4 (the travel-agent fixes), Module 05
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/09-multi-agent-orchestration.md` §1; `Enterprise Agentic Workflow Automation Platform/docs/05-security-tenancy-and-observability-gaps.md` §5; `4. FDE_Related_Preparation/System_Design and Delivery/6. Customer Support AI Assistant Design.md` §5; `4. FDE_Related_Preparation/Star_Stories/AIA_Technical_Implementation_Flow.md` §3

## Why this matters

"Multi-agent" is the most over-reached-for architecture in AI system design. It sounds sophisticated, frameworks make it easy to draw, and it is almost never the right *starting* point. Interviewers notice when the line between "one pipeline with several steps" and "genuinely multiple agents" gets blurred, and they notice when a candidate reaches for specialists before a single agent has been shown to fail. This document gives you the definition, the default, the two triggers that justify escalating past it, and the empirical evidence for those triggers from a real engagement.

## What actually makes something multi-agent

A single pipeline with several steps — rewrite the question, retrieve, check quality, generate — is **not** multi-agent. It is one agent with several *steps*. Module 04's eight-node graph is exactly that, and it is honest to describe it as such rather than overclaim.

**Multi-agent** means multiple **independently scoped** agents, each with its own responsibility, its own tools and its own failure mode — coordinated by something above them, handing off a well-defined package of information rather than a raw transcript.

| | Single agent, multi-step | True multi-agent |
|---|---|---|
| Who decides what happens next | One fixed sequence | A coordinator, or the agents themselves via handoff |
| Tool access | One shared set of tools | Each agent scoped to only what its job needs |
| Failure blast radius | One bad step can fail the whole run | One agent's failure should degrade, not crash, the others |
| What gets passed forward | Everything accumulates | A defined handoff — the next agent gets what it needs, not everything |

The right-hand column is a list of *obligations*. Each one is something you now have to design, test and operate. That is why the default is the left-hand column.

## The default: one agent with good tools

The governing trade-off: **one agent with a tight tool set** — simpler to debug, cheaper to run, one context to reason about. Split into specialists only when one of two triggers fires:

1. **Contexts genuinely conflict.** The same model cannot hold "be a careful finance closer" and "be a chatty support drafter" without one contaminating the other. The system prompt for one job degrades the other.
2. **The tool count becomes unmanageable.** The model starts picking the wrong tool. Past some number of tools — the schemas and descriptions all sitting in context on every turn — selection accuracy falls.

If pushed with "why not many agents?", name one of those two triggers — not "it sounds more sophisticated". Multi-agent is an escalation, not a badge of completeness.

## Not every request needs a planner

The customer-support design in Module 09 makes the same point from the request side. *"Track my order"* is a single tool call — no orchestration. *"My laptop arrived damaged. Refund the order, cancel the warranty, notify shipping, and create a high-priority ticket"* requires planning and coordination across systems. That is when a planner agent earns its cost.

So even inside a multi-agent system, route simple requests straight to a tool or a single agent, and reserve the planner for cross-system tasks. Module 02's travel agent showed the same thing: the supervisor spawns *only the specialists the query needs*, and a cache hit spawns none.

## The evidence: a monolithic agent that failed

The AIA engagement in the fifth document of this module started with the default — one agent — and it broke. Not on paper; in real testing. The single agent carried the full system prompt, **20+ tool schemas**, and the entire conversation history, and it degraded on exactly the two axes above:

- **Context bloat** — every tool's schema and description sat in context on every turn, degrading the model's ability to reason about the actual question.
- **Tool confusion** — with that many tools competing for selection, the agent picked the wrong one often enough that accuracy became unusable for a production advisory engagement.

The fix was not a bigger model or better prompting. It was architectural: split *decide what to do* from *do it*. And later, when the supervisor's own tool list grew back toward the same problem, the same principle was applied again one level up.

That is what the two triggers look like when they actually fire. The default was tried first; it failed measurably; the escalation was justified by the failure. That sequence is the answer to "why multi-agent?"

## The judgement, stated

```
                       start here
                           │
              ┌────────────▼────────────┐
              │  one agent, tight tools  │
              └────────────┬────────────┘
                           │  does it fail?
          ┌────────────────┼────────────────┐
          │ no             │                │ yes — which trigger?
          ▼                │                ▼
      ship it              │     contexts conflict?   tool count unmanageable?
                           │          │                       │
                           │          ▼                       ▼
                           │   split by role             split by domain
                           │   (answer vs draft)         (customer / claims / policy …)
                           │          └───────────┬───────────┘
                           │                      ▼
                           │            multi-agent, with a
                           │            defined handoff contract   → doc 2
                           │            and failure isolation      → doc 3
```

## Interview lens

> *"I'd start with one agent and a tight tool set. I'd split only when contexts conflict or the tool catalogue is too large to route reliably — and I'd want to have seen it fail first. Multi-agent is an escalation, not a badge of completeness. A pipeline with eight steps is still one agent, and I'd describe it that way."*

## Checkpoint

- Give the four-row table distinguishing single-agent multi-step from true multi-agent, from memory.
- Name the two triggers and say what each looks like when it fires.
- Why is Module 04's eight-node graph *not* multi-agent?
- Describe the AIA stage-1 failure and why it justified the escalation.
- What does "not every request needs a planner" imply for routing inside a multi-agent system?

**Next →** [Reference Architecture and Handoffs](02_Reference_Architecture_Handoffs.md)
