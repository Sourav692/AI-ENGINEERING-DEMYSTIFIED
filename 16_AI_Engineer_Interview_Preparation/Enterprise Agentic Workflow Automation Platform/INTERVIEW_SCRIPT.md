# Whiteboard Script — AI Agent Platform for Non-Technical Users

**How to present this system in a 60-minute system design round, using the 6-step framework.**

Problem prompt this answers (verbatim from the DevRev prep guide):

> *"Design an AI agent platform for non-technical users to configure workflow automations across
> multiple channels."*

Everything below has been built and run. Numbers are from real executions — see `README.md`.

---

## Before you start

**The one sentence that frames the whole round.** Say it in the first two minutes:

> *"Anyone can wire an LLM to a tool call. The hard part is letting someone who has never seen a
> stack trace configure that safely — which means the system has to make the dangerous decisions
> itself, deterministically, and never delegate them to the model's judgement in the moment."*

**Time budget** — write it in the corner of the board:

| Minutes | Phase                                                 |
| ------- | ----------------------------------------------------- |
| 0–8    | Clarify + scope                                       |
| 8–15   | High-level architecture                               |
| 15–35  | Deep dive: determinism, control, and durability       |
| 35–45  | Cross-cutting: multi-tenancy, security, observability |
| 45–55  | Failure modes + scale                                 |
| 55–60  | Close: trade-offs + what I'd build first              |

---

# STEP 1 — Clarify and scope (0–8 min)

### The questions that actually change the design

1. **How non-technical is "non-technical"?** Someone who can read a decision tree is a different
   design than someone who can't read JSON at all — changes whether natural-language authoring is
   a nice-to-have or the whole product.
2. **Which channels, and do we own the integration on each?** Slack and webhook are usually
   straightforward; email threading and web-form dedup are usually where the real work hides.
3. **Read-only, or can it act?** Write actions (refunds, closing tickets) are what turn this into a
   guardrail problem instead of a UI problem.
4. **What's the blast radius of a bad workflow?** A wrong Slack reply is embarrassing. A wrong
   refund is money. This changes how aggressive the default guardrails should be.
5. **Multi-tenant from day one, or single-tenant first?** Changes whether isolation is a retrofit or
   load-bearing from the start.

### Then scope explicitly

> *"I'll design for a multi-tenant platform where non-technical users configure declarative
> workflows — never code — that can take real, destructive actions under a guardrail service. I'm
> explicitly not designing the visual builder UI or a natural-language-to-spec compiler — those are
> their own projects — I'll name what they need to produce and move on."*

### The concrete case study to anchor on

Cascade Robotics — Tier-1 support triage across a Zendesk webhook and a Slack escalation channel. A
high-priority ticket gets a drafted reply and, for billing complaints, an automatic refund up to a
tenant-configured cap; above the cap, a human approves.

> *"Notice the refund cap isn't a nice-to-have — it's the difference between 'the agent can act
> autonomously' and 'the agent can act autonomously up to the point where a mistake actually costs
> real money, and then it stops and asks.'"*

---

# STEP 2 — Entities and the happy path (8–12 min)

Write the nouns before the boxes:

```
Event · Channel · WorkflowSpec (versioned) · Trigger · Step · Tool · Run · Guardrail · Principal
```

Then narrate one event end to end in words, *before drawing*:

> *"A ticket webhook arrives. A channel adapter normalises it into a canonical event. Routing finds
> the highest-priority live workflow that triggers on it, and checks no other run is already active
> on that ticket. The orchestrator executes the workflow's steps one at a time, checkpointing after
> each. A non-destructive step — drafting a reply — just runs. A destructive one — issuing a refund —
> goes through the guardrail: is this workflow live enough to act at all, is this specific tool
> allow-listed for autonomous use, is a human needed, does it fit the spend cap. If it passes, it
> executes with an idempotency key so a retry can never double-refund. Every decision, allowed or
> denied, is logged."*

---

# STEP 3 — The architecture (12–20 min)

Draw the pipeline. **Label the two independent decisions in routing.**

```
  raw payload (any channel) --> ADAPTER --> canonical Event
                                                  |
                                                  v
                                    ┌─────────────────────────┐
                                    │  ROUTING                 │
                                    │  1. priority match        │  <- design-time: which SHOULD run
                                    │  2. entity lock check      │  <- run-time: can TWO ever run
                                    └─────────────────────────┘
                                                  |
                                                  v
                              ┌───────────────────────────────────┐
                              │  ORCHESTRATOR (durable, checkpointed) │
                              │   step -> validate args -> guardrail  │
                              │   -> execute (idempotent) -> checkpoint│
                              └───────────────────────────────────┘
                                                  |
                                    COMPLETED / PAUSED_FOR_APPROVAL / HALTED
```

**Two things to call out here:**

- *"Routing is two independent checks on purpose. Priority answers a configuration question - which
  workflow is supposed to win. The entity lock answers a safety question - can two workflows ever be
  mutating the same ticket at once, and it holds even if priority was misconfigured."*
- *"The checkpoint is the same mechanism whether you call it fresh or you're resuming after a crash -
  there's no separate 'recovery path' with its own bugs. `next_step_index` is the single source of
  truth for where a run is."*

---

# STEP 4 — Deep dive (20–40 min)

**Announce where the risk is.**

> *"The hardest part of this system is making the dangerous decisions deterministic instead of
> delegated to the model. I want to spend my time on the guardrail engine and the orchestrator - the
> channel adapters are comparatively boring."*

## 4A. Determinism over free-text (spend the most time here)

### Constrained schemas, not prompts

```
  Bad:   tool_call("issue a refund of about fifty dollars for this order")
  Good:  issue_refund(order_id: str, amount_usd: float)   <- typed, validated BEFORE execution

  validate_args() checks every required field is present and every value's
  type matches the declared schema. A malformed call never reaches the tool.
```

> **"The model can decide THAT a refund is warranted. It never decides the shape of the call that
> actually moves money - that's a typed function signature, checked before anything executes, the
> same instinct as constrained decoding but at the tool-call boundary instead of the token boundary."**

### The guardrail decision - five ordered rules, deny overrides

```
  1. step budget exceeded?        -> halt, don't loop
  2. spend cap exceeded?          -> halt, don't loop  (uses the REAL dollar amount for a refund,
                                                          not a nominal per-call fee - a bug I actually
                                                          hit building this, worth telling as a story)
  3. non-destructive?             -> just run it
  4. shadow mode?                 -> never executes, regardless of anything else
  5. below LIVE status?           -> destructive steps disabled entirely
  6. autonomous AND allow-listed? -> auto-approved
  7. otherwise                    -> needs a real human with the right role
```

> **"Autonomous status raises the ceiling on which actions can skip approval. It never removes the
> ceiling itself - a destructive tool not explicitly allow-listed still needs a human even on a fully
> autonomous workflow, and the spend cap applies at every single status including autonomous."**

**In plain terms, rules 1 and 2 are not two severities of the same check - they count different
things.** The step budget counts *how many steps* a run has taken, so it catches a run that loops
forever no matter how cheap each step is. The spend cap counts *actual dollars* one step is about to
spend, so it catches one expensive action no matter how few steps came before it. A run can blow past
one without ever touching the other.

### ⭐ A real bug worth telling as a story

> *"While building this, a $500 refund on a workflow with a $5 spend cap passed authorization. I'd
> written the cost function to charge a flat, nominal fee per tool call - the same treatment I gave a
> non-financial tool like drafting a reply - so the cap was checking against $0.00 every time,
> regardless of the refund's actual size. I'd conflated 'the operational cost of running this step'
> with 'the dollars this step spends on the customer's behalf.' Fixed it so a financial tool's cost is
> the real amount in its own arguments. It's the same category of bug as the false-security-alarm one
> in the RAG project - a metric that looks like it's protecting something but is actually measuring
> the wrong quantity."*

**In plain terms:** every tool used one cost function, and for simplicity that function charged a
flat, tiny fee — fine for something like drafting a reply, which doesn't spend real money. But the
refund tool used that same flat fee too, so a $500 refund only ever registered as a few cents, and a
$5 cap approved it every time no matter how big the refund actually was. Two different things got
mixed up: "how much work does this step take to run" vs. "how much money does this step actually hand
out." Fix: for a financial tool, its cost *is* the real dollar amount it's about to spend, not a flat
fee. Same root mistake as the false-alarm bug in the RAG project — a safety check that looks like it's
measuring something, but is quietly measuring the wrong thing.

**A second, subtler one, worth telling if the first lands well:**

> *"After fixing that, a legitimately-approved run whose refund step got retried - simulating a
> redelivered event - started failing with 'spend cap exceeded,' even though nothing extra actually
> happened in the real world. The idempotency guard correctly skipped the second side effect, but I'd
> still run the retry through the budget check and added its cost to the run total a second time. I'd
> made idempotency cover the side effect but not its cost - and cost accounting is itself a side
> effect. The fix moves the idempotency check before authorization entirely: a replay of an
> already-applied action is a free, pre-authorized no-op, full stop, never touching the budget or the
> approval logic again. The general lesson: idempotency has to cover every observable effect of a
> step, not just the most obvious one."*

**In plain terms:** after fixing the first bug, the test was: what happens if the same refund event
gets delivered twice, simulating a network retry. The system correctly refused to issue the refund a
second time — good. But it still ran that retry through the spend-cap check and added its cost to the
running total *again*, even though no real money moved the second time. So a completely safe,
already-blocked retry could still push a run over budget and fail it for no reason. The mistake: it
was made sure the *action* couldn't happen twice, but forgot that *counting its cost* is also
something that shouldn't happen twice. Fix: check "have we already done this exact thing" *before*
even reaching the budget/approval logic — if yes, stop right there and treat it as a free no-op,
never touching the budget at all. Lesson: making something "safe to retry" means protecting *every*
effect of that action, not just the obvious one (the money moving) — cost tracking is an effect too,
and it's easy to forget.

## 4B. Durability and idempotency (10 min)

```
  Run 1: step 0 (draft) -> CHECKPOINT -> step 1 (refund, needs approval) -> PAUSED

  [process restarts / human takes an hour to approve]

  resume(): reads next_step_index=1, re-enters at step 1 - step 0 NEVER re-runs.
  Approval granted -> step 1 executes -> idempotency_key = "run_id:refund" recorded.

  If step 1 is somehow attempted again (a redelivered event, a retry):
  same idempotency_key already exists -> no-op. The refund never fires twice.
```

> **"There's no separate crash-recovery code path. `resume()` and a fresh run call the exact same
> loop - it always starts at `next_step_index`, whether that's 0 or the middle of a long-running
> workflow. One loop, one set of bugs to find, not two."**

---

# STEP 5 — Cross-cutting, failure, scale (40–55 min)

**Raise all of this unprompted.**

## Multi-tenancy

Every event, workflow, and policy carries a `tenant_id`; guardrail caps are per-tenant. Routing only
ever matches a tenant's own workflows against its own events.

## Security

- **Every tool call is typed and scoped.** A tool's `scopes` list is what a real deployment would
  check against the connector credential actually being used - least privilege, not "the agent has
  admin on everything."
- **Destructive vs. non-destructive is a first-class flag on the tool, not inferred.** A guardrail
  can't reason about risk it isn't told about explicitly.
- **What's honestly missing:** a real secrets vault for connector credentials, and PII redaction on
  step outputs before a human sees them for approval - both named gaps in `docs/04`, the second one
  directly reusable from the RAG project's `redact_pii()`.

## Observability

Every guardrail decision - allowed or denied, and why - is on the run's event log as it happens, the
same "replayable record" property as the other two projects in this series.

## Failure modes → what a workflow does, not what breaks

| Fails                                                     | Behaviour                                                                                      |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| A step's arguments don't validate                         | Rejected before execution; run halts with a named reason                                       |
| A destructive step needs approval that never comes        | Run stays`PAUSED_FOR_APPROVAL` indefinitely - it does not silently expire into either action |
| A workflow runs away (misconfigured self-trigger)         | Halts at the step budget, does not loop until someone notices                                  |
| The process crashes mid-run                               | Resumes from the last checkpoint; the step that already ran never re-runs                      |
| An event is redelivered (at-least-once channel semantics) | The idempotency key on any destructive step it retries makes the redelivery a no-op            |

## Scale — what breaks first

> *"Every lock and idempotency key in this demo lives in an in-process dict - correct in shape,
> wrong in storage. At real volume that becomes a distributed lock (Redis, or a unique-constraint row
> in a database) and a durable idempotency store shared across workers. The mechanism doesn't
> change - `acquire_lock`/`release_lock` stay the same two functions - only where they're backed
> changes. I didn't stand up real infrastructure for a local demo, the same honest limit as the RAG
> project's '10 million chunks' story."*

---

# STEP 6 — Close deliberately (55–60 min)

### Summarise in three sentences

> *"A multi-channel platform where every dangerous decision - which workflow runs, whether a
> destructive step executes, whether a retry can double-apply a side effect - is deterministic and
> enforced in code, never delegated to the model in the moment. Workflows are declarative and
> versioned, promoted through a staged rollout the same way a person earns more autonomy over time.
> Durability and idempotency mean a crash or a redelivered event is a non-event, not an incident."*

### Your top three trade-offs — and what would change your mind

| Decision                                                    | Chose                         | Would revisit if                                                                                                                                                         |
| ----------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A fixed step-list "planner" over a real LLM reasoning loop  | deterministic, testable, free | the task space is genuinely open-ended enough that a fixed plan can't cover it - then a real model choosing the next tool, still inside the same guardrail               |
| Priority + entity lock over a single ranking mechanism      | two independent checks        | conflicts became rare enough that the lock's overhead isn't worth it - unlikely, since the lock is what makes a misconfigured priority merely wrong instead of dangerous |
| In-process locks/idempotency store over real infrastructure | simple, fast for a demo       | any real deployment on day one - this was never meant to survive contact with more than one process                                                                      |

### The forward-deployed close — do not skip this

> *"If I were shipping this, week one isn't the full agent runtime. It's: one channel, one
> non-destructive workflow, the guardrail engine, and the staged rollout - prove that a non-technical
> user's workflow genuinely can't take an unapproved destructive action, before anyone argues about
> which LLM plans the steps."*

---

## Cheat sheet — the lines that carry the round

1. *"The model decides THAT something should happen. A typed, validated function signature decides
   HOW - that boundary is where determinism lives."*
2. *"Autonomous status raises the ceiling on what can skip approval. It never removes the ceiling."*
3. *"One execution loop, not two - resume and a fresh run share the exact same code path."*
4. *"An idempotency key is on the action, not the run - because a run can legitimately retry, but one
   specific side effect must never apply twice."*
5. *"Priority answers which workflow SHOULD run. A lock answers whether two ever CAN run at once -
   two different questions, two different checks."*
6. *"A halted run with a named reason beats a workflow that loops until someone notices."*

## Questions to ask them

- How much of DevRev's own agent configuration is already declarative vs. code today?
- Where does the guardrail decision actually live in production - in the platform, or in each
  connector?
- What's the current story for a workflow that needs to act across two channels in one run?
- How do you decide when a workflow has "earned" autonomous status?

## If you have a laptop

```bash
python scripts/run_workflow_demo.py         # staged rollout, routing conflict, approval,
                                              # idempotent retry, crash + resume
python scripts/demo_guardrail_failure.py     # every guardrail actually blocking: wrong role,
                                              # skipped stage, bad args, spend cap, runaway steps,
                                              # entity lock
pytest -q                                    # 21 tests, deterministic, no LLM
```

The durability demo is the single most persuasive artefact: a run is "crashed" mid-flight, resumed,
and the step that already executed is provably never re-run.
