# Gates, Risks and Metrics

> **Level** 🔴 The FDE Role · **Module** 10 · **Doc** 4 of 7 · **Time** ~35 min
> **Prerequisites:** [Scoping Doc to Production in Two Weeks](03_Scoping_To_Production_In_Two_Weeks.md); Module 04 doc 2 (the `Decision` shape); Module 06 doc 1 (secrets)
> **Source material:** `4. FDE_Related_Preparation/Delivery Framework from Scoping to Delivery/docs/01-theory.md` §B.3–B.6; `docs/05-security-gate-depth-and-tenant-scale.md`; `README.md`
> **Lab:** `project/scripts/demo_gate_failure.py` — the negative-control demo

## Why this matters

Gates are the whole point. "Configure, do not code" and "a definition of done that includes observability and a runbook" are the same idea underneath: **a stage is not done because time passed; it is done because a specific, checkable thing is true.** This document is the six gates, who may sign each, the three deny rules, the four named risks and the check that answers each, the five metrics — and then the harder question the source raises about its own design: a gate can be structurally real and still have an evidence bar too weak to trust.

## The six gates

| Gate | Blocks entry to | Who signs it off |
|---|---|---|
| `security_review_passed` | Data readiness | Security reviewer |
| `data_access_granted` | Configure | Customer SME |
| `golden_set_signed_off` | Evaluate | Customer SME |
| `eval_baseline_met` | Shadow mode | Forward Deployed Architect |
| `rollback_tested` | Limited production | Forward Deployed Architect |
| `success_metrics_met` | *(go/no-go — deploy)* | Executive sponsor |

**This is deliberately the same shape as ABAC access decisions.** A gate sign-off and a document-access decision are the same kind of thing: a named rule, deny overrides, an explicit reason — and, critically, **the wrong person cannot sign it off no matter how senior they are.** The Forward Deployed Architect cannot pass the security gate; only a security reviewer can. That is not bureaucracy. It is Module 04's "no LLM is ever the enforcement point" applied to people: the person closest to the work is not automatically the person authorised to certify it is safe.

### The three deny rules

`sign_off(engagement, gate_name, signer, evidence)` returns a `Decision`, deny overriding:

| # | Rule | Denies when |
|---|---|---|
| 1 | `wrong_role` | The signer's role is not in the gate's `allowed_roles` — no exceptions for seniority |
| 2 | `no_evidence` | An approval with no artefact behind it |
| 3 | `prior_gate_incomplete` | An earlier-stage gate has not passed — no signing out of order |

Every attempt, allowed or denied, is logged.

### Two pairs that sound alike but check different things

**`security_review_passed` vs `data_access_granted`.** Both sit early and both sound like "access". The first asks *is it safe to even start touching this customer's systems* — a clearance on the engagement itself, signed by a security reviewer, before any connection is made. The second asks *are the agreed data sources actually connected and live* — an operational fact, signed by the customer's SME, after the clearance already passed. One is a go-ahead; the other confirms the thing you proceeded to do actually worked.

**`golden_set_signed_off` vs `eval_baseline_met`.** Both are about the same test set, one stage apart. The first asks *is this test set actually representative of what this customer needs* — a judgement about the *test*, signed by the customer's SME, who knows their business. The second asks *did the assembled agent clear the bar against that test* — a judgement about the *score*, signed by the FDA, after configuration. One certifies the exam is fair; the other certifies you passed it. A representative set with a failing score, or a rigorous score against a bad set, both correctly fail — the two checks are independent on purpose.

## Risk mitigations are checks, not reminders

Four named risks, and the framework's answer to each is a mechanism, not a to-do item:

| Risk | Mitigation | How it is enforced |
|---|---|---|
| **Data access delays** | *"Start day 1, escalate day 3"* | An automatic check: if `data_access_granted` is still pending on day 3, the system raises the escalation itself — `check_escalation_triggers()` |
| **Scope creep** | Change-control on the signed scope | Any change after intake goes through the same sponsor-level authority that approved the original metrics — not yet built; the coverage map sizes it as low effort using `sign_off()`'s shape |
| **Unmeasurable success criteria** | **Refuse to start** | `intake()` raises `ScopingRefused`. A two-week clock against an unmeasurable goal is worse than no clock |
| **No customer SME** | A contractual prerequisite | Also enforced at intake. Three of the six gates need an SME signature; an engagement with no SME is structurally unable to finish, and it is better to know on day 0 |

**The honest limit, stated out loud:** *some engagements should not be two weeks, and knowing which ones to reject is part of the framework.* Intake refusal is that instinct made literal.

## The five metrics

| Metric | What it actually tells you |
|---|---|
| **Time-to-first-value** | How long until the customer saw *anything* real, not just a status update |
| **Eval score at handover** | The number that was actually true when responsibility transferred |
| **Human-approval override rate** | Falling over time = trust being earned; flat = the agent is not ready for less supervision |
| **Week-4 retention** | Whether the thing deployed is still the thing being used a month later — `None` until recorded, never a fake `0.0` |
| **Accelerator reuse rate** | The direct measure of "productised process" vs "bespoke heroics" — the governing question made numeric |

From the Northwind demo: time-to-first-value 1 day; eval score 0.83; override rate 0.27; reuse rate 0.83; 6 of 6 gates; one escalation, auto-raised on day 3 and resolved when the gate passed. **Read honestly:** one engagement, run once; the eval score is a demo-scripted value, not a measurement. What is proven is that the pipeline enforces its own gates.

## The negative-control demo

`demo_gate_failure.py` is the one to run in front of anyone who asks whether the gates are real. It shows intake refusing an unmeasurable request; the FDA denied `wrong_role` on the security gate; the SME denied `no_evidence`; a sign-off out of order denied `prior_gate_incomplete`; an attempt to skip a stage that has no code path to call; and the day-3 escalation firing by itself. Module 05 taught the same lesson: a demo of things being *stopped* proves more than a demo of things working.

## Where the design is honest about its own weakness

The source material asks a harder question of itself: **a gate can be structurally real and still have a weak evidence bar.** That the right role must sign is a genuine control. But a gate is only as good as *what counts as sufficient evidence*, and that is a separate design question from "does the gate exist".

| What a thorough security review should include | Does a generic "security review passed" checkbox prove it happened? |
|---|---|
| Basic output validation | No — a quality check, not a security check |
| Retrieval and tool-selection accuracy | No |
| Task success on real test cases | No — that is the evaluation gate |
| **Adversarial testing — prompt injection, permission-boundary probes** | **This is what a security review should mean, and free-text evidence cannot prove it happened** |
| Ongoing production monitoring | No — continuous, not a gate |

If the evidence is a sentence — "looks fine", "reviewed" — a reviewer could sign having checked something unrelated and never run a single adversarial test against a system about to touch real customer data. The gate cannot tell a thorough review from a rubber stamp, because the evidence has no required shape.

**The fix:** turn the evidence requirement into a **checklist, not a sentence** — adversarial testing done, permission boundaries tested, data agreements signed — all explicitly present before the gate can pass. The same discipline as intake refusing to start without a measurable metric, applied to *what a signature attests to*, not only whether one exists. Module 08 doc 5 is what that checklist should contain.

Three more things the delivery process itself has to get right, easy to overlook because attention is on what gets deployed rather than the process that deploys it:

- **The delivery process holds live customer credentials** in exactly two windows — when sources first connect, and when the system starts running against the real environment. A gate proving access was granted proves a human attested it is live; it does not prove the credentials were stored in a vault, scoped to this engagement, and revoked at handover. Module 06 doc 1's secrets pattern applies one step earlier.
- **Residency and encryption apply to what the process creates.** The golden set built with the customer's SMEs often contains real customer data. Storing it identically for a regulated customer and a low-sensitivity trial is a residency gap in the delivery process itself. The reusable *tool* is shareable; the *data it produces per engagement* follows that customer's sensitivity tier.
- **Many engagements at once is a tenancy decision.** A framework that models one engagement will need to model many. The instinct is to treat that as scheduling and capacity — but underneath it is the same multi-tenancy decision from Module 06 doc 4, applied to the delivery process's own data: are two customers' engagement records, gate evidence and test sets separated by a tag, or physically? Does "show me all engagements" structurally exclude a competitor's data, or rely on remembering to filter?

## In the code

| Concept | Where |
|---|---|
| Gate definitions, sign-off, ordering | `gates.py` → `GATE_DEFINITIONS`, `sign_off`, `blocking_gates`, `_earlier_unpassed_gates` |
| Roles, including the negative control `u_fda_wrong_hat` | `identity.py` |
| Intake refusal | `pipeline.py` → `intake`, `ScopingRefused` |
| Auto-escalation | `engine.py` → `check_escalation_triggers`, `escalate`, `resolve_escalation` |
| Metrics | `metrics.py` → `time_to_first_value`, `eval_score_at_handover`, `override_rate`, `week4_retention`, `accelerator_reuse_rate`, `summary` |
| Tests | `tests/test_gates.py` — 17, deterministic |

## Interview lens

> *"A gate can be structurally real — the right role has to sign it, the wrong role gets rejected — and still have an evidence bar that's too weak to trust, if the evidence is free text instead of a checklist. Closing that means making the sign-off require specific proof — adversarial testing done, permission boundaries tested — the same way intake refuses to start without a measurable success metric. And credentials the delivery process itself holds to connect a customer's real systems have exactly the same vault, rotation and scoping requirements as anything a deployed system holds — one step earlier, which is why it's easy to overlook."*

## Checkpoint

- List the six gates, what each blocks, and who signs it.
- State the three deny rules and say why seniority is not an override.
- Distinguish the two pairs of similar-sounding gates.
- For each of the four risks, name the mechanism — not the reminder — that mitigates it.
- Why can a real gate still be a rubber stamp, and what is the fix?
- Name the three ways the delivery process itself must meet the same security bar as the deployed system.

**Next →** [Cross-Team Collaboration](05_Cross_Team_Collaboration.md)
