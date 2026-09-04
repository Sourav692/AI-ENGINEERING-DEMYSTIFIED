# Whiteboard Script — Scoping Doc to Deployed Agent in Under 2 Weeks

**How to present this system in a 60-minute system design round, using the 6-step framework.**

Problem prompt this answers (verbatim from the DevRev prep guide):

> *"Design a delivery framework that takes a customer from scoping doc to deployed AI agent in under
> 2 weeks."*

Everything below has been built and run. Numbers are from real executions — see `README.md`.

---

## Before you start

**The one sentence that frames the whole round.** Say it in the first two minutes:

> *"This isn't really a software architecture question — it's an operating-model question. Anyone
> can draw a pipeline with seven boxes. The signal is whether each box is a real, enforced gate or
> just a status someone reports honestly. I designed it so the gates are code, not trust."*

That sentence does three things: names the real test (repeatability, not cleverness), signals
you've thought about *why* this problem is different from the other two, and sets up the deep dive.

**Time budget** — write it in the corner of the board:

| Minutes | Phase |
|---|---|
| 0–8 | Clarify + scope |
| 8–15 | High-level pipeline |
| 15–35 | Deep dive: gates + the reuse system |
| 35–45 | Cross-cutting: risk mitigation, metrics, CI/CD parallels |
| 45–55 | Failure modes + scale (portfolio, not chunks) |
| 55–60 | Close: trade-offs + what I'd build first |

---

# STEP 1 — Clarify and scope (0–8 min)

### The questions that actually change the design

1. **Is "2 weeks" a hard SLA or a target?** Changes whether gate failures mean "slip the date" or
   "abort and re-scope."
2. **Who owns the go/no-go decision** — the FDA, the account team, or the customer? Changes who the
   `success_metrics_met` gate's allowed role should be.
3. **What's genuinely reusable across customers vs. inherently one-off?** The accelerator library
   only works if most of what's needed already exists — how true is that on day 1 of a *new*
   engagement type, versus the 50th customer of a proven one?
4. **What happens if a hard gate fails outright** — not late, but genuinely fails (security review
   finds a real blocker)? Does the engagement pause, or does it terminate?
5. **Is this framework for one team or an org-wide standard?** Changes whether "the accelerator
   library" is a shared asset with its own ownership and versioning, or informal tribal knowledge.

### Then scope explicitly

> *"I'll design the pipeline as a state machine with named, role-gated checkpoints and a reusable
> asset library behind each stage. I'm explicitly not designing the infrastructure-provisioning
> layer underneath 'configure, do not code' — that's a real system in its own right — I'll name what
> it needs to do and move on."*

### The concrete case study to anchor on

Northwind Logistics — Tier-1 support triage agent over Zendesk, Confluence, and Salesforce. Success
metrics agreed at intake, in writing, before day 1: first-response time under 5 minutes on the top 3
ticket categories, and zero-edit sends on 60% of eligible tickets by week 4.

> *"Notice both metrics are things you can literally measure from ticket timestamps and edit history
> — not 'the agent should be helpful.' If a metric can't be measured this cleanly, intake refuses the
> engagement rather than starting a clock against it."*

**Draw this early.** Immeasurable-metric refusal is the single cheapest, highest-signal thing in
this whole design — say it before you draw a single box.

---

# STEP 2 — Entities and the happy path (8–12 min)

Write the nouns before the boxes:

```
Engagement · Stage · Gate · Principal (role) · Artifact · AcceleratorAsset · Escalation · Metric
```

Then narrate one engagement end to end in words, *before drawing*:

> *"A scoping request comes in. Intake checks it's actually measurable and has an SME assigned, or
> refuses it outright. Accepted, it enters day 1 at the Scoping stage. Each of the next six stages is
> blocked behind a named gate, signed off only by the role authorized for that gate — the FDA cannot
> sign the security gate, no matter how senior. Every stage pulls what it needs from a reusable
> accelerator library before building anything custom. On day 14, if the agreed success metrics were
> actually met, the sponsor signs the go/no-go gate and the engagement deploys with a runbook and
> dashboards handed over."*

---

# STEP 3 — The architecture (12–20 min)

Draw the pipeline. **Label every gate with who signs it.**

```
 SCOPING ──> gate:security_review ──> DATA READY ──> gate:data_access ──> CONFIGURE
  (1-2)         (security reviewer)     (3-4)           (customer SME)      (5-7)
                                            |
                                   day 3, still pending?
                                   AUTO-ESCALATE
                                            v
      gate:golden_set ──> EVALUATE ──> gate:eval_baseline ──> SHADOW
       (customer SME)       (8-9)          (FDA)              (10-11)
                                                                   |
      gate:rollback_tested ──> LIMITED PROD ──> gate:success_metrics ──> GO/NO-GO
             (FDA)                (12-13)            (sponsor)              (14)
                                                                                |
                                                                          DEPLOYED
```

**Two things to call out here:**
- *"This is deliberately the same decision shape as the RAG project's ABAC engine — a named rule, a
  role check, deny overrides, and an explicit reason. A gate sign-off and a document access decision
  are the same kind of problem: 'is the person asking actually authorized to say this is true?'"*
- *"There is no code path that jumps a stage. `advance_stage()` only ever moves to the immediate
  next one — the same way the RAG project has no code path that queries the vector store without the
  ACL filter. The property isn't a rule people follow, it's a rule the code can't violate."*

---

# STEP 4 — Deep dive (20–40 min)

**Announce where the risk is.**

> *"The hardest part of this system isn't the pipeline shape — seven stages in order is not a hard
> problem. The hard part is making 'done' mean something checkable instead of 'time passed,' and
> making the accelerator library real enough that week two doesn't turn into bespoke code. I want to
> spend my time there."*

## 4A. Gates as authority, not checklist items

### Why role-gating, not just existence-checking

```
  Naive version:  "security review complete: [x]"     <- a checkbox anyone can tick
  This version:   sign_off(gate, signer, evidence)
                    signer.role must be in gate.allowed_roles   <- deny overrides
                    evidence must be non-empty                  <- "approved" is not evidence
                    every earlier gate must already be PASSED   <- no signing out of order
```

> **"A checkbox is a status. A gate is a decision with a named authority behind it. The FDA closing
> their own security gate is the delivery-framework version of an LLM enforcing its own access
> control — the person closest to the work is not automatically the person authorized to certify
> it's safe."**

### The automatic risk-mitigation, not a reminder

> *"§5.4 says 'data access delays: start day 1, escalate day 3.' I didn't build that as a note in a
> project tracker — `check_escalation_triggers()` runs a real check: if the data-access gate is still
> pending once day 3 arrives, the system raises the escalation itself, once, and it's in the
> engagement's permanent event log whether anyone was watching or not."*

## 4B. The accelerator library (10 min)

### The governing question, made numeric

```
  Every stage needs an asset (a connector, a prompt template, a guardrail policy...)
  Pull it from the library?  -> reused = true
  Not there yet?             -> build it custom, reused = false, LOGGED

  accelerator_reuse_rate = reused pulls / total pulls
```

> *"'Productised process, not bespoke heroics' is the whole thesis of this problem type. I didn't
> want that to be a slide bullet — I wanted a number. On the Northwind engagement it's 83%: 5 of 6
> assets came straight from the library, one guardrail policy was custom. That ratio, tracked across
> engagements, is the actual measure of whether the framework is working or quietly turning into
> bespoke code again."*

### What the library is honestly *not*

> *"The library entries here are named assets — 'zendesk_connector,' 'golden_set_harness' — not the
> actual connector code or eval harness. The real eval harness this would reuse already exists one
> project over, in the RAG platform. I'd wire the Evaluate stage to actually call it rather than
> assert a score, and I'm explicit that I haven't done that yet — the gate mechanism is real, the
> number behind one piece of evidence currently isn't."*

---

# STEP 5 — Cross-cutting, failure, scale (40–55 min)

**Raise all of this unprompted.**

## Risk mitigation, all four named in §5.4

| Risk | Mitigation | Built? |
|---|---|---|
| Data access delays | Escalate automatically on day 3 | ✅ — a real check, not a reminder |
| Scope creep | Change-control on the signed scope | ❌ — not built; would reuse the gate sign-off pattern for a `request_scope_change()` requiring sponsor role |
| Unmeasurable success criteria | Refuse to start | ✅ — `intake()` |
| No customer SME | Contractual prerequisite | ✅ — `intake()` |

> *"I'd rather show you three of four real and name the honest gap on the fourth than claim all four
> and get caught on it under a follow-up."*

## Failure modes → what a stalled engagement looks like, not what breaks

| Fails | Behaviour |
|---|---|
| A hard gate genuinely fails (not late — actually denied) | Engagement stays at its current stage; the failure is a first-class event in the log, not a silent stall |
| Wrong person attempts a sign-off | Denied, logged, engagement state unchanged — no partial progress from an unauthorized attempt |
| Golden set never gets customer sign-off | Evaluate stage is permanently blocked; this is a customer-side failure, and the framework's job is to surface it clearly, not route around it |
| Success metrics genuinely aren't met by day 14 | The go/no-go gate simply doesn't pass — "no-go" is a legitimate, first-class outcome, not a failure of the framework |

> **"The framework's job isn't to guarantee every engagement deploys in 14 days. It's to guarantee
> that if one doesn't, everyone knows exactly which gate stopped it and why — never a vague 'it's
> taking longer than expected.'"**

## Scale — what breaks first, and it isn't chunks this time

> *"The RAG project's scale question is 'what happens at 10 million chunks.' This system's equivalent
> is 'what happens when one FDA is running six engagements at once.' I haven't built a portfolio
> view — this models exactly one engagement. The honest answer: the state machine itself doesn't
> change with portfolio size, it's the same gates per engagement. What's actually hard is capacity —
> how many engagements one person can carry before gates start queueing behind their calendar, not
> behind the customer. That needs real engagement-duration data before I'd design it, the same way
> I wouldn't guess at embedding-cache hit rates without real query logs."*

---

# STEP 6 — Close deliberately (55–60 min)

### Summarise in three sentences

> *"A seven-stage pipeline where every transition is blocked behind a named, role-gated decision, not
> a status field. Reusable assets are pulled before anything is custom-built, and that ratio is
> tracked as the actual measure of whether the process is repeatable. Two of four named risk
> mitigations are automatic checks in code, not reminders on a tracker — and I can tell you exactly
> which two aren't, yet."*

### Your top three trade-offs — and what would change your mind

| Decision | Chose | Would revisit if |
|---|---|---|
| Role-gated sign-off over self-certification | six named gates, six named authorities | a single-person delivery team where role separation is impossible — then gates would need to compress, not disappear |
| Hard refusal at intake over "start and hope" | refuse unmeasurable/no-SME requests outright | a strategic customer where the business decides to accept the risk anyway — then intake needs an explicit override path with its own sign-off, not a silent bypass |
| Automatic escalation over manual tracking | day-3 auto-escalate on data access | mitigations multiply and a human dashboard becomes clearer than N separate automatic checks — then this becomes a rules engine, not hardcoded checks |

### The forward-deployed close — do not skip this

> *"If I were rolling this out internally, week one isn't building all seven stages. It's: pick the
> two gates most often skipped under deadline pressure today — in my experience that's the golden-set
> sign-off and the rollback test — and make just those two structurally unskippable first. That
> proves the risky part of this idea — that gates as code actually change behaviour, not just
> documentation — before anyone argues about the other five."*

---

## Cheat sheet — the lines that carry the round

1. *"A gate is a decision with a named authority behind it, not a checkbox anyone can tick."*
2. *"There's no code path that skips a stage — the same way the RAG project has no code path that
   skips the ACL filter."*
3. *"Refuse to start an engagement with no measurable success metric — the two-week clock is a
   consequence of readiness, not a target."*
4. *"The reuse-vs-custom ratio is the actual measure of 'productised process,' not a slide bullet."*
5. *"An automatic escalation on day 3 beats a reminder on a tracker — it fires whether anyone was
   watching or not."*
6. *"A 'no-go' at day 14 is a legitimate outcome, not a failure of the framework."*
7. *"Some engagements shouldn't be two weeks — knowing which to reject is part of the design, not a
   gap in it."*

## Questions to ask them

- What does DevRev's actual accelerator library look like today — is it code, templates, or tribal
  knowledge?
- Where has the two-week target actually broken down on real engagements, and which gate was it?
- Who owns the go/no-go call in practice — the FDA, the account team, or the customer?
- How many engagements does a single Forward Deployed Architect typically carry at once?

## If you have a laptop

```bash
python scripts/run_engagement_demo.py     # the happy path, all 14 days, gates signed in order
python scripts/demo_gate_failure.py       # the negative control: wrong role, no evidence,
                                           # out-of-order sign-off, and the day-3 auto-escalation
pytest -q                                 # 17 gate-enforcement tests, all deterministic, no LLM
```

The gate-failure demo is the single most persuasive artefact: the same senior person, in the wrong
role, is denied — not warned, denied — trying to sign off a gate that isn't theirs to sign.
