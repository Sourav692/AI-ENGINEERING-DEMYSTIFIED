# The Three Roles

> **Level** 🟢 Foundations · **Module** 00 · **Doc** 2 of 3 · **Time** ~15 min
> **Prerequisites:** none
> **Source material:** `4. FDE_Related_Preparation/Senior_FDE_Day_to_Day.md` (the three-lens model); synthesis across the three source projects

## Why this matters

The same body of knowledge — retrieval, agents, access control, evaluation, delivery — is examined differently depending on which chair you are sitting in. An AI engineer is asked *does it work and can you prove it*. An agentic systems designer is asked *is it safe when it is wrong*. A forward deployed engineer is asked *did the customer get the outcome, and could your team have done it without you*. If you prepare for one and interview for another, you will answer the wrong question well.

This document names the three roles, says what each is actually judged on, and shows how the handbook's modules serve each. The roles are not tiers — a senior FDE is not "a better AI engineer" — but they build on each other, and the handbook is ordered so that the later roles inherit everything the earlier ones need.

## The three roles

### AI Engineer — *build it, measure it*

You take a capability the business wants — answer questions over our documents, triage our tickets, draft our reports — and turn it into a system with measurable quality. The unit of your work is a pipeline: ingestion, retrieval, generation, evaluation.

What you are judged on:

- **Correctness you can demonstrate.** Not "it answered my question" but recall@k on a golden set, groundedness on every run, a leak rate of exactly zero.
- **Understanding the failure modes of each component.** Why dense retrieval misses exact identifiers; why fixed-size chunking destroys a contract's meaning; why a post-filter after top-k retrieval is a quality *and* security failure.
- **Knowing what the framework does for you and what it does not.** You should be able to write the ReAct loop in a `while` loop before you write it in LangGraph.

Core modules: 01, 03, 04, 06, 08.

### Agentic Systems Designer — *make it safe when it is wrong*

You design systems that *act*: refund a customer, close a ticket, send an email, run a workflow across channels. The unit of your work is not a pipeline but a control boundary: the line between what the model may decide and what the system will permit.

What you are judged on:

- **Splitting deterministic control flow from probabilistic reasoning.** The model chooses *which value* goes in an argument; it never improvises the control flow.
- **Containment.** Step budgets, spend caps, confirmation gates, staged rollout, idempotency keys, kill switches. Each is a specific answer to a specific incident: the double refund, the runaway loop, the autonomous workflow that skipped a human check.
- **Knowing when *not* to reach for multi-agent.** One agent with good tools by default; a second agent only when the handoff has a defined contract and a failure-isolation story.

Core modules: 01, 03, 05, 06, 07, 08.

### Forward Deployed Engineer — *deliver the outcome, through the team, with the customer*

You sit with the customer. You turn a scoping document into a running system in weeks, in *their* environment, with *their* data and *their* security team's sign-off. The unit of your work is an engagement.

The source material describes the role as three lenses, weighted rather than sequential:

| Lens | How it shows up daily | What it is actually for |
|---|---|---|
| **Technical build** | Architecture decisions, hands-on code and review, debugging production issues, evaluating retrieval and agent strategies | Staying credible enough that the team trusts your calls, and catching problems before the customer does |
| **Customer-facing** | Discovery, requirement translation, demos and readouts, escalation handling, expectation-setting on scope and timeline | Making sure what gets built is what the business needs *now* — not what the spec said six weeks ago |
| **Guiding the team** | Unblocking engineers, reviewing designs *before* they are built, calibrating scope with delivery leads, mentoring on customer communication | Making the team's output better and faster than any one person's throughput |

What you are judged on:

- **Asking before architecting.** The next document is entirely about this.
- **Owning the definition of done.** Offering to own evaluation — "how will we know this works?" — is described in the source material as the strongest FDE signal in a room.
- **Interdependence of the three lenses.** The line that distinguishes senior from mid-level: *technical credibility is what lets the team trust your scoping calls; direct customer relationships are what let you make fast trade-off decisions; the team's growth is what lets you stay hands-on where it matters instead of being a bottleneck everywhere.* Pull any one out and the other two get slower.

Core modules: 00, 02, 04, 05, 09, 10, 11.

## How the roles relate

```
                  ┌──────────────────────────────────────────────┐
                  │  FDE: engagement                             │
                  │   scoping → gates → delivery → narrative     │
                  │  ┌─────────────────────────────────────────┐ │
                  │  │  Agentic Systems Designer: control      │ │
                  │  │   what may the model decide?            │ │
                  │  │   what will the system permit?          │ │
                  │  │  ┌────────────────────────────────────┐ │ │
                  │  │  │  AI Engineer: pipeline             │ │ │
                  │  │  │   ingest → retrieve → generate     │ │ │
                  │  │  │   → evaluate                       │ │ │
                  │  │  └────────────────────────────────────┘ │ │
                  │  └─────────────────────────────────────────┘ │
                  └──────────────────────────────────────────────┘
```

Each outer role contains the inner one. An agentic systems designer who cannot build the pipeline designs guardrails around a system they do not understand. An FDE who cannot reason about control boundaries cannot tell a customer's security team why the design is safe. The handbook is ordered inner-to-outer for that reason.

## One problem, three questions

Take the same scenario — *a support agent asks the assistant why a customer lost data in March and whether they get service credits* — and listen to what each role asks:

| Role | The question |
|---|---|
| AI Engineer | Did retrieval find the ticket, the post-mortem *and* the contract? Did the answer cite them? Is the answer grounded? |
| Agentic Systems Designer | The Tier-1 agent is not allowed to read the post-mortem or the contract. Was that enforced *before* the model saw anything, or did we ask the model politely not to mention it? If the assistant can also *issue* the credit, who approved that? |
| FDE | Which of the customer's four personas asked this, what should each see, and did compliance sign off on that matrix before we wrote the first access rule? How do we prove, after the fact, that nobody saw what they should not have? |

All three questions are correct. All three are answered in this handbook — Module 04 for the first, Modules 04 and 05 for the second, Modules 04 and 10 for the third.

## Interview lens

When asked "how do you split your time" or "what makes you senior", the source material's closing line is worth keeping whole:

> *"It's less about doing harder individual work and more about being the person whose judgment the team can borrow — on scope, on what 'done' means for this customer, on when to go deep versus when to ship the simpler thing. That only works if I stay technical enough to be trusted, customer-connected enough to know what actually matters, and available enough that I'm not the bottleneck."*

Module 10 returns to the full day-in-the-life with the lines for each part of the day.

## Checkpoint

- What is the unit of work for each of the three roles?
- Why does the handbook order the roles inner-to-outer rather than teaching FDE skills first?
- Take a system you know. Write the three questions each role would ask about it.

**Next →** [The First Ten Minutes](03_The_First_Ten_Minutes.md)
