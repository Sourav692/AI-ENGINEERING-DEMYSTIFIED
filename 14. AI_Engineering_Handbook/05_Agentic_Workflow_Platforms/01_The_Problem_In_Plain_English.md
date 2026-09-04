# The Problem in Plain English

> **Level** 🟡 Building Production Systems · **Module** 05 · **Doc** 1 of 7 · **Time** ~30 min
> **Prerequisites:** Module 01 doc 3, Module 03
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise Agentic Workflow Automation Platform/docs/01-theory.md` Part A, §B.1, §B.6; `README.md` (business case)
> **Lab:** `project/scripts/run_workflow_demo.py`

## Why this matters

The prompt this module answers reads: *"Design an AI agent platform for non-technical users to configure workflow automations across multiple channels."* Most people hear "AI agent platform" and start drawing an LLM choosing tools. That is not the problem, and a design that starts there will spend forty minutes on the wrong thing. This document translates the prompt into what it actually asks, names the hard part, and gives you the three-layer structure that every later document fills in.

## The one-sentence problem

Translated into normal words:

> Build a system where a support manager (who cannot code) can say **"when a customer emails asking for a refund under $50, just refund them automatically"** — and the system does exactly that, safely, whether the customer asked by email, Slack, chat or a web form.

That is the whole ask. Everything else in the design is "how do we make that safe and reliable".

## The four phrases, unpacked

| Phrase in the prompt | What it really means |
|---|---|
| "AI agent" | Something that looks at an event and *takes an action* — reply, refund, escalate, tag — not just answers a question |
| "platform" | Not one workflow: many tenants, each defining many workflows |
| "for non-technical users to configure" | The person building the automation is **not a programmer**. They cannot write code, cannot read a stack trace, and should not need to |
| "across multiple channels" | The same automation must work whether the trigger came from email, Slack, a chat widget, a web form or a raw webhook — each of which looks completely different on the wire |

If you can say those four back to an interviewer in one breath, you understand the prompt.

## Why it is actually hard

The mechanics of "LLM picks a tool" were solved years ago. **The hard part is trust.** You are handing a non-programmer a button that can refund real money, send a real email to a real customer, close a real support ticket — and they configured it in plain English, not code they can review line by line. The question actually being tested:

> How do you let someone who cannot read code still trust that the automation will only do what they meant — and never something worse — even when the AI gets it wrong, or the network retries a request, or the server crashes mid-run?

That is a *systems and safety* problem wearing an AI costume. The LLM is almost incidental — and the source project makes the point brutally: it contains **no LLM at all**. The "agent reasoning loop" is a fixed, deterministic step sequence, so every property can be proven with fast, reproducible tests. What that trades away is named honestly in the coverage map.

## The three layers every good answer covers

```
 LAYER 3   "Is this user allowed to configure/run this, and did we ask a human when we should have?"
              -> guardrails: approvals, spend caps, staged rollout (draft/test/shadow/live)

 LAYER 2   "If this runs twice by accident (retry, crash, redelivery), does it break something?"
              -> idempotency keys, checkpointed/resumable execution

 LAYER 1   "No matter which channel this came from, does it look the same to everything downstream?"
              -> a canonical event schema + one adapter per channel
```

A weak answer talks about Layer 1 (parsing channels) and waves at an LLM doing "reasoning". A strong answer spends most of its time on Layers 2 and 3, because that is where real incidents happen: double refunds, an autonomous workflow that skipped a required human check, a crash that re-runs an already-completed step. Docs 2, 4 and 5 of this module are those three layers.

## A concrete example to keep in your head

The non-technical user's request, in their own words:

> "If a customer messages us anywhere asking for a refund and it's under $50, just refund them. Don't bother me for small stuff."

What the platform must silently guarantee, without the user ever knowing these words:

1. Whether the message arrived by email, Slack DM or the website widget, it is normalised into the same internal shape before any decision is made — **channel adapters**.
2. The workflow fires only for messages actually about refunds, and if two workflows could match, exactly one wins, deterministically — **routing**.
3. Before this workflow could auto-refund anyone, it went through `draft → test → shadow → live`, and someone with authority approved it going live — **staged rollout**.
4. "Under $50" is enforced as a real spend-cap check at execution time — not typed into an English prompt and trusted — **guardrails**.
5. If the refund call is retried (flaky network, duplicate webhook), the customer is refunded once, not twice — **idempotency**.
6. If the server restarts mid-run, the run resumes where it left off rather than restarting and risking a second refund — **durable, checkpointed execution**.

Every one of those six guarantees is a component in the architecture. None requires the user to know what an idempotency key is.

## The case study: Cascade Robotics

The project's scenario is a support tenant with a ticket-triage workflow: draft a reply, then issue a refund. The question that drives the demo:

> *"Why didn't Cascade Robotics' $500 refund fire automatically?"*

| Question | What actually happened |
|---|---|
| Wasn't the workflow autonomous? | Yes — but `issue_refund` was not allow-listed for autonomous use on this tenant, so it still needed a human |
| Wasn't there budget? | The tenant's spend cap is $50. A $500 refund is refused outright — `spend_cap_exceeded` — never silently clamped down to the cap |
| What if it retries and refunds twice? | It cannot — the idempotency key on that action exists after the first apply; a retry is a no-op |

Those three answers are Layers 3, 3 and 2 respectively, and each is a test in the project.

## Why this mirrors the other two projects on purpose

Module 04's RAG platform, this module's agent platform, and Module 10's delivery framework share one shape: a `Decision(allowed, rule, reason)` returned by a named policy where deny overrides allow.

| Concept here | In the delivery framework | In enterprise RAG |
|---|---|---|
| `guardrails.py::authorize_step()` | `gates.py::sign_off()` | `authz/policy.py::decide()` |
| Staged workflow rollout (`promote()`) | Staged engagement pipeline (`advance_stage()`) | Layer 1 pre-filter / Layer 2 authoritative re-check |
| Entity lock in `routing.py` | Per-engagement single mutable state | Per-tenant collection isolation |
| `observability.py` | `observability.py` | `observability/trace.py::RunTrace` |

The point, stated once for all three: **access control, delivery gates and workflow guardrails are the same kind of problem wearing three different hats.** A named rule decides, deny overrides, and the reason is never "because I said so".

## Interview lens

If asked to restate the problem in one breath:

> *"We're building the safety and orchestration layer that sits between a non-technical user's plain-English intent and a real, destructive action — so that no matter which channel the trigger came from, the action only runs when it's actually supposed to, runs exactly once, and survives crashes and retries without ever surprising anyone."*

And expect follow-ups on **testing and containment**, not the happy path: how does a user try a workflow before it is live, and how do you stop a bad one mid-flight? Both are answered by the same mechanism — staged rollout plus a hard step/spend budget — not two separate features.

## Checkpoint

- Unpack the four phrases of the prompt from memory.
- Why is "the hard part is trust" a stronger framing than "the hard part is tool selection"?
- Name the three layers and the incident each prevents.
- For the $50 refund example, list the six silent guarantees and the component behind each.
- What single shape do the three source projects share, and why does it matter?

**Next →** [Canonical Events, Channels and Routing](02_Canonical_Events_And_Channels.md)
