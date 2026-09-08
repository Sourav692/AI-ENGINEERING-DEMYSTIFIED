# Agent Platform — Theory

**Problem prompt (verbatim from the DevRev prep guide):**

> *"Design an AI agent platform for non-technical users to configure workflow automations across
> multiple channels."*

This doc has two parts: **Part A** explains the problem in plain English first — read this if the
prompt itself feels fuzzy. **Part B** is the technical reference, mapped line-by-line to the prep
guide's §3 and to what's actually built in this repo — read this once the problem itself is clear.

---

# Part A — What is this problem actually asking? (plain English)

## A.1 The one-sentence problem

Translated into normal words:

> Build a system where a support manager (who cannot code) can say **"when a customer emails
> asking for a refund under $50, just refund them automatically"** — and the system does exactly
> that, safely, whether the customer asked by email, Slack, chat, or a web form.

That's it. That's the whole ask. Everything else in the design is just "how do we make that safe
and reliable."

## A.2 Break the sentence into its four parts

| Phrase in the prompt | What it really means |
|---|---|
| "AI agent" | Something that can look at an event and *take an action* (reply, refund, escalate, tag) — not just answer a question. |
| "platform" | Not one workflow — a system where *many different tenants* can each define *many different workflows*. |
| "for non-technical users to configure" | The person building the automation is **not a programmer**. They can't write code, can't debug a stack trace, and shouldn't need to. |
| "across multiple channels" | The same automation has to work whether the trigger came from email, Slack, a chat widget, a web form, or a raw webhook — each of which looks completely different on the wire. |

If you can explain those four phrases back to an interviewer in one breath, you understand the
prompt.

## A.3 Why is this actually hard? (the part people get wrong)

Most people hear "AI agent platform" and think the hard part is: *how do I get an LLM to call the
right tool?* That's not the hard part — LangChain solved the mechanics of "LLM picks a tool" years
ago.

**The hard part is trust.** You are handing a non-programmer a button that can:
- refund real money,
- send a real email to a real customer,
- close a real support ticket.

And they configured it using plain English, not code they can review line-by-line. So the real
question the interviewer is testing is:

> **How do you let someone who cannot read code still trust that the automation will only do what
> they meant — and never something worse — even when the AI part gets it wrong, or the network
> retries a request, or the server crashes mid-run?**

That's a *systems/safety* problem wearing an "AI" costume. The LLM is almost incidental.

## A.4 The three things every good answer must cover

Think of the problem as three layers stacked on top of each other:

```
 LAYER 3   "Is this user allowed to configure/run this, and did we ask a human when we should have?"
              -> guardrails: approvals, spend caps, staged rollout (draft/test/shadow/live)

 LAYER 2   "If this runs twice by accident (retry, crash, redelivery), does it break something?"
              -> idempotency keys, checkpointed/resumable execution

 LAYER 1   "No matter which channel this came from, does it look the same to everything downstream?"
              -> a canonical event schema + one adapter per channel
```

A weak answer only talks about Layer 1 (parsing channels) and maybe waves at an LLM doing
"reasoning." A strong answer spends most of the time on Layers 2 and 3, because that's where real
incidents happen — double refunds, an autonomous workflow that skipped a required human check, a
crash that re-runs an already-completed step.

## A.5 A concrete mental example (keep this one in your head)

**Non-technical user's request, in their own words:**
> "If a customer messages us anywhere asking for a refund and it's under $50, just refund them.
> Don't bother me for small stuff."

**What the platform must silently guarantee, without the user ever knowing these words:**

1. Whether that message arrived by email, Slack DM, or the website chat widget, it gets normalized
   into the same internal shape before any decision is made (**channel adapters**).
2. The workflow only fires for messages that are actually about refunds, and if two workflows could
   both match the same message, only one wins, deterministically (**routing**).
3. Before this workflow can auto-refund anyone, it went through a `draft → test → shadow → live` path
   where someone with authority actually approved it going live (**staged rollout**).
4. "Under $50" is enforced as a real spend cap check at execution time — not just typed into the
   English prompt and trusted (**guardrails**).
5. If the refund tool call gets retried (flaky network, duplicate webhook), the customer is refunded
   once, not twice (**idempotency**).
6. If the server restarts mid-run, the run resumes from where it left off — it doesn't restart the
   whole thing and risk re-sending the refund (**durable/checkpointed execution**).

Every one of those six guarantees is a component in the reference architecture (Part B, §2). None
of them require the user to know what an "idempotency key" is.

## A.6 The five non-technical-user safeguards, in plain language

§B.3 below names five design constraints for the "non-technical user" half of the problem. Here's
what each one actually means, without the jargon:

1. **Templates, not a blank canvas** — Nobody starts from zero. It's like picking a resume template
   instead of designing one in a blank Word doc — you clone something that already works ("Auto-refund
   small orders") and just tweak the numbers, instead of building automation logic from scratch.

2. **Plain English gets turned into something reviewable, not run directly** — When the user types
   "refund anyone under $50," the system doesn't just wire that sentence straight into an execution
   engine and hope for the best. It first converts it into a structured, readable spec — like a form
   with clearly labeled fields (`trigger: refund request`, `condition: amount < $50`,
   `action: issue_refund`) — and shows it back to the user to confirm *before* anything runs. You're
   approving a form, not trusting a black box.

3. **A test mode where nothing actually happens** — Before the automation goes live, it can run in
   "shadow" mode: it watches real customer messages and *decides* what it would do — but it's not
   allowed to actually send the refund, close the ticket, or email anyone. It's like a fire drill —
   everyone practices the real actions, but the building doesn't actually burn. This is
   unconditional: even if the user has admin rights, shadow mode blocks every real action.

4. **Run history in human words** — After the automation runs, the user shouldn't have to read a log
   file full of JSON to know what happened. They should be able to see something like "refunded 12
   customers, escalated 2 to a human, denied 1 for exceeding the spend limit" — a plain-English
   summary instead of raw technical output.

5. **A staged rollout, like a driving test with levels** — An automation can't jump straight from
   "just written" to "fully autonomous." It has to move through stages in order: `draft` (just an
   idea) → `test` (dry-run against sample data) → `shadow` (watches real traffic, takes no action) →
   `live` (acts, but a human approved it going live) → `autonomous` (acts fully on its own). And
   crucially — the person who *wrote* the automation can't be the one who promotes it to the next
   stage. Someone else with actual authority has to sign off, the same way a student driver can't
   grade their own driving test.

---

## A.7 Why four stages, specifically? (not three, not five)

Simple version: **each stage exists to answer exactly one question, and removing any of them
leaves that question unanswered until real customers find out the hard way.**

| Stage | The one question it answers | What breaks if you skipped it |
|---|---|---|
| `DRAFT` | "Is this even wired correctly?" — right trigger, right condition, right tool, no typos. | You'd test your first idea against real customer messages. |
| `TESTING` | "Does it behave correctly on realistic input?" — run it against sample/historical data, off to the side, nothing customer-facing. | You'd find out it's wrong only after it's already watching (or worse, acting on) live traffic. |
| `SHADOW` | "Does it behave correctly on *live, real-time* traffic?" — watches real events as they happen and decides what it *would* do, but every write is mocked, so nothing customer-facing ever fires. | You'd only discover it makes bad *decisions* on live traffic after it had already refunded someone. |
| `LIVE` | "Is a human still willing to vouch for each individual action?" — it acts for real, but every destructive step needs a person to approve it before it fires. | You'd go straight from "looks fine in shadow" to "acts on its own," with no one ever watching a single real action happen before trusting it fully. |
| *(`AUTONOMOUS`)* | "Has this earned the right to act without asking every time?" — same guardrails (spend cap, approval allow-list) still apply; only the *default* changes, from ask-first to act-first. | Not skippable in the same sense — it's the destination, not a gate — but the point is it's a stage in its own right, never the starting point. |

Why not fewer? Collapse `TESTING` into `SHADOW` and you lose the difference between "replaying old
data" (cheap, repeatable, no real-time pressure) and "watching live traffic" (the first time it
sees today's actual weirdness). Collapse `SHADOW` into `LIVE` and you lose the ability to ever
watch a workflow's *decisions* without also exposing customers to its *mistakes* — you'd be
debugging in production. Skip `LIVE`'s human-approval step and jump `SHADOW` straight to
`AUTONOMOUS`, and the very first time a human ever sees this workflow's real-world behavior is
also the first time nobody is watching it.

Why not more? Each extra stage is a stage someone has to remember to promote through — more stages
without a distinct question behind them is just process for its own sake, and the guardrail policy
(spend caps, approval allow-lists) already scales the risk *within* a stage, so there's no need to
carve out extra stages to express "a little more trusted."

The same idea, restated as one line for a whiteboard: **each stage removes exactly one kind of
"we don't actually know yet" — first "is it wired right," then "does it decide right on realistic
data," then "does it decide right on live data," then "will a human still catch a bad individual
action" — and only once all four are answered does it earn the right to act alone.**

### How a non-technical user actually moves through these stages

None of this happens by editing code — it's a status a business user clicks through in a UI, one
stage at a time:

1. They build the workflow (or clone a template) — it starts life in `DRAFT`.
2. They click something like "run against sample data" — that's `TESTING`. Results show up off to
   the side; nothing customer-facing happens yet.
3. Once that looks right, they promote it to `SHADOW` — it now watches real, live traffic and logs
   what it *would* have done, but every write is faked, so no real customer is ever touched. This is
   where a non-technical user builds trust by comparing the workflow's decisions against what a human
   would have done, at zero risk.
4. Once shadow results look good, it's promoted to `LIVE` — it acts for real now, but every
   destructive step pauses and waits for a human to click "approve" before it fires. The business
   user (or their team) is still in the loop for every single action.
5. Only after a track record in `LIVE` does it get promoted to `AUTONOMOUS` — it now acts on its own
   by default, for the specific actions that were pre-approved for that.

**One detail worth stating explicitly if asked:** the person who *built* the workflow can never
promote it themselves — promotion is role-gated to an admin or approver, never the workflow's own
author, and a stage can never be skipped (no jumping `DRAFT` straight to `LIVE`). The person iterating
on the workflow and the person who says "this has earned the next level of trust" are always two
different people — the same separation-of-duties instinct as requiring a second reviewer, just
applied to rollout instead of code review.

---

## A.8 If the interviewer asks you to restate the problem in one breath

Say this:

> "We're building the safety and orchestration layer that sits between a non-technical user's
> plain-English intent and a real, destructive action — so that no matter which channel the trigger
> came from, the action only runs when it's actually supposed to, runs exactly once, and survives
> crashes and retries without ever surprising anyone."

---

# Part B — Technical reference

## B.1 The question behind the question (§3.1)

**The hard part is not running an agent — it's letting a non-technical user define one safely and
predictably.** Anyone can wire an LLM to a tool. The signal being tested is whether you split
*deterministic control flow* from *probabilistic reasoning*, so a user without engineering
background can configure something dependable without writing (or reading) code.

**"Multiple channels" is doing real work in the prompt.** The same logical workflow must fire from
email, chat, Slack, a web form, and a webhook — each with a wildly different payload shape and a
different notion of "what is this about." If channel-specific logic leaks past the first layer of
the system, every subsequent component has to know about every channel, forever. The fix is a
canonical event schema and adapters that translate into it once, at the edge — see §B.2 below.

**Expect follow-ups on testing and containment**, not on the happy path: how does a user try a
workflow before it's live, and how do you stop a bad one mid-flight? Both are answered by the same
mechanism — staged rollout plus a hard step/spend budget — not two separate features.

---

## B.2 Reference architecture (§3.2), and what this project builds of it

| Layer | What it does | Built here? |
|---|---|---|
| Channel adapters | Normalise inbound events into one canonical `Event` schema | ✅ `channels.py` |
| Trigger and routing | Match events to workflows; resolve same-event conflicts | ✅ `routing.py` |
| Workflow definition store | Versioned, declarative specs, never raw code | ✅ `workflows.py` |
| Orchestration engine | Durable, checkpointed, resumable step execution | ✅ `orchestrator.py` |
| Agent runtime | Plan → select tool → call → observe → iterate, with a hard step cap | 🟡 the loop shape is real; the "planner" is a fixed step list, not a real LLM choosing dynamically — see `docs/04` |
| Tool registry | Typed tools, JSON-schema args, scopes, destructive flag | ✅ `tools.py` |
| Connector layer | Authenticated per-tenant integrations, secrets vault | ❌ not built — see `docs/04` |
| Policy and guardrail service | Approval gates, spend caps, PII redaction | 🟡 approval gates + spend caps built; PII redaction not built |
| Run store and trace log | Every step, tool call, output persisted | ✅ `observability.py` |

---

## B.3 The non-technical user problem (§3.3)

Five ideas, stated as design constraints:

1. **Templates, not a blank canvas** — a library of pre-built workflows to clone and edit, not a
   from-scratch authoring surface.
2. **Natural-language authoring compiles to a reviewable declarative spec** — the user never edits
   the thing that actually executes directly; they edit (or generate) the `WorkflowSpec`, and confirm
   intent before it runs. This project's `WorkflowSpec` is exactly that reviewable spec — built here
   directly in code, standing in for what a visual builder or NL-to-spec compiler would emit.
3. **A dry-run mode with all writes mocked** — this project's `SHADOW` status *is* that mode: the
   guardrail engine refuses to apply any destructive tool's side effect while a workflow is in
   `SHADOW`, unconditionally, regardless of role or approval.
4. **Plain-language run history** — not built here (the trace is a structured log, not natural
   language), but the structured log it's built from is exactly what a plain-language summary would
   be generated *from*.
5. **Staged rollout: draft → test → shadow → live (approved) → autonomous** — built exactly as named,
   as an ordered, role-gated promotion (`workflows.py::promote()`), the same shape as
   `delivery_framework_platform`'s stage gates.

---

## B.4 Determinism and control (§3.4)

**This is the section this project is actually about.** Five named controls, all built and tested:

| Control | Where |
|---|---|
| Constrained tool schemas over free-text arguments | `tools.py::validate_args()` — type-checked against a declared schema before execution |
| Idempotency keys on side-effecting calls | `orchestrator.py` — a retried step never applies its side effect twice |
| Max-step and max-cost budgets, halt-and-escalate not loop | `guardrails.py::authorize_step()` — the tighter of the workflow's own budget and the tenant policy's |
| Confirmation gates on destructive actions, configurable per tenant/tool | `guardrails.py` — role-gated approval, an explicit per-tenant allow-list for what autonomous status may skip approval on |
| Split deterministic control flow from probabilistic reasoning | The orchestrator's step sequence is fixed, declarative data; only *which value* goes into an argument is ever templated from the event — the control flow itself is never something an LLM improvises at runtime |

**A subtlety worth stating out loud:** autonomous status does not mean unlimited. A destructive tool
not explicitly allow-listed for autonomous execution still needs a human, even on a fully autonomous
workflow — and a spend cap applies at every status, including autonomous. Autonomy raises the
ceiling on *which* actions can skip approval; it never removes the ceiling itself.

---

## B.5 Likely follow-ups (§3.5) — and where each one is actually answered

| Follow-up | Answer, and where |
|---|---|
| A workflow has been running for two hours when the orchestrator restarts — what happens? | `run.next_step_index` is the checkpoint; `orchestrator.resume()` continues from it, never from step 0. Demoed directly — a simulated crash mid-run, then resumed. |
| Two workflows trigger on the same event and conflict | Two mechanisms: `routing.py`'s priority ordering picks one *by design*, and an exclusivity lock on the event's target entity prevents two runs from ever mutating the same entity concurrently, *even if priority were misconfigured*. |
| How does a tenant safely add a custom tool? | Partially answered: schema validation and scoping exist (`ToolDefinition.schema`/`.scopes`); sandboxed execution and a review-before-publish pipeline do not — see `docs/04`. |
| How do you version a workflow that's already live? | `WorkflowStore` keeps every published version; a `Run` pins to `workflow_version` at start, so editing a workflow mid-flight never changes the behaviour of runs already in progress. |

---

## B.6 Why this mirrors the other two projects on purpose

Third project in the series, same `Decision(allowed, rule, reason)` shape as the RAG project's
`authz.policy.decide()` and the delivery framework's `gates.py::sign_off()`:

| Concept here | Concept in `delivery_framework_platform` | Concept in `enterprise_rag_platform` |
|---|---|---|
| `guardrails.py::authorize_step()` | `gates.py::sign_off()` | `authz/policy.py::decide()` |
| Staged workflow rollout (`workflows.py::promote()`) | Staged engagement pipeline (`engine.py::advance_stage()`) | Layer 1 pre-filter / Layer 2 authoritative re-check |
| Entity lock in `routing.py` | Per-engagement single mutable state | Per-tenant Chroma collection isolation |
| `observability.py` | `observability.py` | `observability/trace.py::RunTrace` |

The point, stated once for all three: **access control, delivery gates, and workflow guardrails are
the same kind of problem wearing three different hats** — a named rule decides, deny overrides, and
the reason is never "because I said so."

---

## See also

- `02-architecture-end-to-end.md` — the pipeline, diagrammed end to end
- `03-src-modules-reference.md` — every function in `src/agent_platform`
- `04-system-design-coverage-map.md` — checked against the prep doc, gap by gap
- `notebooks/02-hands-on.ipynb` — build and run it
- `../INTERVIEW_SCRIPT.md` — the whiteboard script
