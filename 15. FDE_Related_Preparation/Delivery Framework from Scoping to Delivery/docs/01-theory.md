# Delivery Framework — Theory

**Problem prompt (verbatim from the DevRev prep guide):**

> *"Design a delivery framework that takes a customer from scoping doc to deployed AI agent in under
> 2 weeks."*

This doc has two parts: **Part A** explains the problem in plain English first — read this if the
prompt itself feels fuzzy. **Part B** is the technical reference, mapped line-by-line to the prep
guide's §5 and to what's actually built in this repo — read this once the problem itself is clear.

---

# Part A — What is this problem actually asking? (plain English)

## A.1 The one-sentence problem

Translated into normal words:

> A new customer signs up wanting an AI agent. Today, day 0, all you have is a rough scoping
> document — a page of "here's roughly what we want it to do." Design the *process* your company
> runs, end to end, so that by day 14 there is a real agent live in production for that customer,
> and it got there the same reliable way every time — not through a different set of heroics for
> each customer.

That's it. You're not being asked to design the agent. You're being asked to design **the assembly
line that produces the agent**, reliably, in two weeks, for any customer.

## A.2 Why this problem feels different from the other two

The other two problems in this series (the agent platform, the RAG system) are software
architecture questions — "design a system that does X." This one is explicitly called out in the
prep guide as a different *kind* of question: a **process / operating-model design problem**. There
is no single running program that "is" the answer the way a search index is the answer to a RAG
question.

That trips people up, because their instinct is "there's nothing to build here, it's just a
process diagram." Wrong instinct. The prep guide is explicit: answer it *as a system* — inputs,
stages, artefacts, gates, and metrics — and a system with stages and gates **is a state machine**.
A state machine is code. So this project builds a real, gate-enforcing pipeline that a customer
engagement actually moves through, the same discipline as the other two projects, just applied to
an operating model instead of a search index.

## A.3 Why is two weeks actually hard? (the part people get wrong)

The naive answer to "how do we go live in 2 weeks" is "work faster" or "hire more people." That's
wrong, and it's the trap the question is testing for.

**Two weeks is only possible if most of the work already existed before the customer showed up.**
If every engagement starts from a blank page — writing connectors from scratch, inventing prompt
templates from scratch, discovering the right guardrail policy from scratch — two weeks is not a
schedule, it's a wish. The only way to hit two weeks *repeatably, for different customers*, is if
most of a stage is **pulled from a reusable library**, and only the small remainder is actually
built or configured for this specific customer.

So the real question the interviewer is testing is:

> **Can you design a process where speed is a *side effect* of reuse and hard gates, rather than a
> target you chase by cutting corners under deadline pressure?**

That reframes the whole problem. It's not a scheduling question. It's an asset-reuse and
risk-containment question wearing a "delivery timeline" costume.

## A.4 The two things every good answer must cover

Think of the problem as two questions stacked on top of each other:

```
 QUESTION 2   "How do we know each stage is actually safe to leave, not just that time passed?"
                 -> gates: a named, checkable condition, signed off by the *right* role — never
                    the person closest to the work rubber-stamping their own progress

 QUESTION 1   "How do we make 2 weeks achievable for a different customer every time?"
                 -> a library of reusable assets (connectors, prompt templates, tool defs,
                    guardrail policies) that most of each stage is assembled from, not written
```

A weak answer draws seven boxes in a row labeled "scoping → data → build → test → launch" and stops
there — that's a checklist, not a framework, and checklists get skipped under deadline pressure. A
strong answer spends most of its time on: what's reusable vs. bespoke at each stage, and what
specific, checkable fact has to be true before the next stage is allowed to start.

## A.5 A concrete mental example (keep this one in your head)

**What actually happens, day by day, if the framework is doing its job:**

1. **Day 1–2:** The customer's scoping doc gets turned into a written, *measurable* success metric
   (not "make support better" — something you can put a number on) and a named customer SME is
   assigned. If nobody can commit to a measurable metric or an SME, the engagement **does not
   start** — a 2-week clock against an unmeasurable goal is worse than no clock at all.
2. **Day 3–4:** Their data sources get connected and access is verified live — not just "access was
   requested."
3. **Day 5–7:** The agent gets *assembled*, not coded — connectors, prompt templates, tool
   definitions, and guardrail policies are pulled from the accelerator library and configured for
   this customer. This is the stage where "reuse vs. bespoke" is decided in practice.
4. **Day 8–9:** A golden set of test cases is built, the customer's own SME signs off that it's
   representative, and the measured baseline against it has to clear a bar before moving on.
5. **Day 10–11:** The agent runs against real traffic in shadow mode — it sees everything, decides
   what it would do, but takes no real action — while humans compare its answers to what they'd
   have done themselves.
6. **Day 12–13:** The agent finally acts for real, but with a human approving actions in the loop,
   and — critically — a rollback path that has actually been *tested*, not just documented.
7. **Day 14:** A go/no-go decision, made against the metric written down on day 1 — and only if it
   passes does a runbook, dashboards, and a named owner get handed over.

Every one of those isn't a date on a calendar — it's a **gate**: a specific, checkable fact, signed
off by a specific role, that has to be true before the next stage is allowed to start. That's the
mechanism that keeps "two weeks" honest instead of becoming "we shipped something in two weeks and
quietly hoped it works."

## A.6 If the interviewer asks you to restate the problem in one breath

Say this:

> "We're designing a repeatable delivery pipeline — not a one-off project plan — where speed comes
> from a reusable accelerator library, and safety comes from hard, role-gated checkpoints between
> stages, so that two weeks is an achievable outcome of the process, not a deadline we hope to hit
> by cutting corners."

---

# Part B — Technical reference

This is the odd one out among the three named problem types. The other two (agent platform, RAG
with access control) are software architecture problems. This one is explicitly named in the prep
guide as different: *"DevRev may hand you a process/operating-model design problem, not only a
software architecture one."* The signal being tested is whether you can design an **operating
model** — inputs, stages, artefacts, gates, metrics — and whether you know the difference between a
repeatable process and a pile of one-off heroics.

That doesn't mean there's nothing to build. §5.1 of the prep guide is explicit: *"Answer it as a
system with inputs, stages, artefacts, gates, and metrics, and draw it as a pipeline on the board."*
A pipeline with gates and metrics is a state machine, and a state machine is code — so
`delivery_framework_platform` builds exactly that: a real, gate-enforcing engagement pipeline, the
same way `enterprise_rag_platform` builds a real, ACL-enforcing retrieval pipeline for Problem
Type B.

---

## B.1 The core insight

**The correct answer is a productised delivery process backed by reusable assets — not heroics and
not bespoke code per customer** (§5.1). Two weeks is only achievable if most of what a stage needs
already exists in a library before the engagement starts. The 2-week clock is a *consequence* of
reuse, not a target you hit by working faster.

This gives the whole design one governing question to keep coming back to: **for any given piece of
work in this pipeline, is it pulled from a library, or built from scratch for this customer?** The
ratio between those two is the actual measure of whether the framework works.

---

## B.2 The seven stages (§5.2)

| Days | Stage | What has to be true to leave it |
|---|---|---|
| 1-2 | Scoping and qualification | Success metrics are written down and measurable; a customer SME is assigned; the security review has started |
| 3-4 | Data readiness | Sources are connected; access is live and verified |
| 5-7 | Configure, do not code | Assembled from the accelerator library — connectors, prompt templates, tool definitions, guardrail policies |
| 8-9 | Evaluate and iterate | A golden set exists, has been reviewed by the customer's SME, and the measured baseline meets the bar |
| 10-11 | Shadow mode | The agent runs against real traffic but takes no action; humans compare its output to what they'd have done |
| 12-13 | Limited production | The agent acts, with human approval on the loop, and a *tested* rollback path exists |
| 14 | Go/no-go and handover | The agreed success metrics were actually met; if so, a runbook, dashboards, and an owner are handed over |

**The order is not optional.** You cannot configure against data you haven't connected; you cannot
evaluate against a golden set nobody signed off; you cannot go to limited production without a
tested way to undo it. This is exactly why the codebase models stage transitions as a state machine
with hard gates rather than a checklist someone might skip under deadline pressure — see §B.3.

**Shadow mode here is the same idea as `agent_platform`'s `SHADOW` status, and Limited production is
the same idea as its `LIVE` status** — worth stating explicitly if the parallel is asked about. Shadow
mode watches real traffic and decides what it *would* do, but takes no real action, exactly like the
agent platform's SHADOW stage. Limited production acts for real but with a human approving each
action, exactly like the agent platform's LIVE stage. Same two-step trust ladder, same reason: don't
let a system's first real action also be the first time nobody's watching it.

---

## B.3 Gates are the whole point

**"Configure, do not code"** and **"a definition of done that includes observability and a
runbook"** are both, underneath, the same idea: a stage isn't done because time passed, it's done
because a *specific, checkable thing* is true. §5.4 names five hard gates plus the terminal decision:

| Gate | Blocks entry to | Who signs it off |
|---|---|---|
| `security_review_passed` | Data readiness | Security reviewer |
| `data_access_granted` | Configure | Customer SME |
| `golden_set_signed_off` | Evaluate | Customer SME |
| `eval_baseline_met` | Shadow mode | Forward Deployed Architect |
| `rollback_tested` | Limited production | Forward Deployed Architect |
| `success_metrics_met` | *(go/no-go — deploy)* | Executive sponsor |

**This is deliberately the same shape as ABAC access decisions in the RAG project.** A gate
sign-off and a document-access decision are the same kind of thing: a named rule, deny overrides,
an explicit reason, and — critically — **the wrong person cannot sign it off no matter how senior
they are.** The Forward Deployed Architect cannot pass the security gate; only a security reviewer
can. That isn't bureaucracy for its own sake — it's the same "no LLM is ever the enforcement point"
instinct applied to people instead of models: the person closest to the work is not automatically
the person authorized to certify it's safe.

**Two pairs of gates that sound similar but check different things — worth being precise about:**

- **`security_review_passed` vs. `data_access_granted`.** Both sit early and both sound like "access"
  checks, but they answer different questions. `security_review_passed` asks *"is it safe to even
  start touching this customer's systems"* — a security clearance on the engagement itself, signed by
  a security reviewer, before any data connection is made. `data_access_granted` asks *"are the agreed
  data sources actually connected and live"* — an operational fact, signed by the customer's own SME,
  after the security clearance already passed. One is a go-ahead to proceed; the other confirms the
  thing you proceeded to do actually worked.
- **`golden_set_signed_off` vs. `eval_baseline_met`.** Both are about the same test set, one stage
  apart, and it's easy to conflate them. `golden_set_signed_off` asks *"is this test set actually
  representative of what this customer needs"* — a judgment call about the *test itself*, signed by
  the customer's SME, who knows their own business. `eval_baseline_met` asks *"did the assembled agent
  actually clear the bar against that test"* — a judgment call about the *score*, signed by the FDA,
  after the agent has been configured. One certifies the exam is fair; the other certifies you passed
  it. A representative test set with a failing score, or a rigorous score against a bad test set, both
  correctly fail to satisfy "ready for shadow mode" — the two checks are independent on purpose.

---

## B.4 Risk mitigations are checks, not reminders (§5.4)

Four named risks, and the framework's answer to each:

1. **Data access delays** — mitigation: *"start day 1, escalate day 3."* Modeled as an automatic
   check, not a task on someone's to-do list — if the `data_access_granted` gate is still pending on
   day 3, the system raises the escalation itself.
2. **Scope creep** — mitigation: change-control on the signed scope. Any change after intake has to
   go through the same sponsor-level authority that approved the original success metrics.
3. **Unmeasurable success criteria** — mitigation: **refuse to start.** This is the delivery
   framework's version of the RAG project's "refuse to index a document with no usable ACL" — a
   2-week clock started against a success metric nobody can actually measure is a worse outcome than
   never starting the clock. `pipeline.py::intake()` enforces this at the very first step.
4. **No customer SME available** — mitigation: make it a contractual prerequisite. Also enforced at
   intake, for the same reason: three of the six gates require an SME signature, so an engagement
   with no SME is structurally unable to ever finish, and it's better to know that on day 0.

---

## B.5 Metrics (§5.4)

| Metric | What it actually tells you |
|---|---|
| Time-to-first-value | How long until the customer saw *anything* real, not just a status update |
| Eval score at handover | The number that was actually true when responsibility transferred |
| Human-approval override rate | Falling over time = trust being earned; flat = the agent isn't ready for less supervision |
| Week-4 retention | Whether the thing that got deployed is still the thing being used a month later |
| *(added here)* Accelerator reuse rate | The direct measure of "productised process" vs. "bespoke heroics" — the governing question from §B.1, made numeric |

**The honest limit, stated out loud (§5.4):** *"Some engagements should not be two weeks, and
knowing which ones to reject is part of the framework."* Intake refusal is that instinct made
literal — not every request should get a clock started against it.

---

## B.6 Why this mirrors the RAG project's shape on purpose

| RAG project (`enterprise_rag_platform`) | Delivery framework (`delivery_framework_platform`) |
|---|---|
| `Principal` / `ResourceAttributes` | `Principal` (role: fda / security_reviewer / customer_sme / sponsor) |
| `authz/policy.py::decide()` — named rules, deny overrides | `gates.py::sign_off()` — named rules, deny overrides |
| Loader refuses a document with no usable ACL | `pipeline.py::intake()` refuses an engagement with no measurable metrics |
| Graph edges encode "authorize first, enforce before generate" | `engine.py::advance_stage()` encodes "no stage without its gates" |
| `observability/trace.py::RunTrace` | `observability.py` — every gate sign-off, escalation, and stage move logged |
| `evaluation/harness.py` — turns a claim into a number | `metrics.py` — turns "the process works" into a number |

The point of building it this way is not novelty — it's that the same interview signal ("I built
this, not just described it") applies to both problem types, using one consistent vocabulary.

---

## See also

- `02-architecture-end-to-end.md` — the pipeline, diagrammed end to end
- `03-src-modules-reference.md` — every function in `src/delivery_framework`
- `04-system-design-coverage-map.md` — checked against the prep doc, gap by gap
- `notebooks/02-hands-on.ipynb` — build and run it
- `../INTERVIEW_SCRIPT.md` — the whiteboard script
