# What a security gate should actually verify, and what "one engagement at a time" hides

Cross-cutting topics for a **delivery-process** system design round — taking a customer from a
scoping document to a deployed AI system on a fixed timeline. None of this needs a codebase — it's
architecture and process design to defend on a whiteboard.

---

## 1. A gate can be structurally real and still have a weak evidence bar

A gate that blocks progress until the right person signs off is a real, meaningful control — it stops
the wrong person from waving something through. But a gate is only as good as **what counts as
sufficient evidence** to pass it, and that's a separate design question from "does the gate exist."

A generic security review can mean very different things:

| What a thorough security review should include | Is a generic "security review passed" checkbox enough to prove it happened? |
| --- | --- |
| Basic output validation (does the system produce well-formed responses) | No — this is a quality check, not a security check |
| Retrieval and tool-selection accuracy | No |
| Overall task success on real test cases | No — that's a separate evaluation gate |
| **Adversarial testing — prompt injection attempts, permission-boundary probes** | **This is what a security review should mean, and a free-text sign-off can't prove it happened** |
| Ongoing production monitoring | No — that's continuous, not a one-time gate |

**The concrete risk:** if the gate's evidence is just a sentence ("looks fine," "reviewed"), a
reviewer could sign off having only checked something unrelated — a paperwork item, a policy
acknowledgment — and never actually run a single adversarial test against the system that's about to
touch a customer's real data. The gate can't structurally tell the difference between a thorough
review and a rubber stamp, because the evidence has no required shape.

**The fix, conceptually:** turn the evidence requirement into a checklist, not a sentence — a small
set of required items (adversarial testing done, permission boundaries tested, data agreements signed)
that all have to be explicitly present before the gate can be marked passed. This mirrors a pattern
that should already exist elsewhere in the process — refusing to start work at all when a required
input (like a measurable success metric) is missing. The same discipline just needs to apply to *what
a signature actually attests to*, not only to whether a signature exists.

## 2. The delivery process itself handles live customer credentials

Early in any two-week (or similarly fast) delivery timeline, the team connects to a customer's real
systems — a support tool, a CRM, a knowledge base — which means the delivery tooling itself holds live
credentials to those systems during the engagement. This is a distinct problem from the deployed
system's own credential handling: **it's one layer earlier, and it's easy to overlook because
attention is on what gets deployed, not on the process that deploys it.**

This matters most in exactly two windows: when sources first get connected, and again when the system
starts running against the customer's real environment. Both are moments where a credential mishandled
by the *delivery process itself* — not the eventual product — is the actual risk.

**What to say:** *"A gate proving access was granted proves a human attested it's live. It doesn't
prove the credentials enabling that access were ever handled safely during the engagement — stored in
a vault, scoped only to what this engagement needs, revoked cleanly at handover. That's the same
secrets-handling gap that applies to any system holding live customer credentials, and it's easy to
miss because the attention is usually on the deployed product, not the process that builds it."*

## 3. Data residency and encryption apply to what the delivery process creates, not just what gets deployed

Per-tenant encryption and data residency requirements usually get read as a property of the deployed
system. They're equally a property of the **artifacts the delivery process itself produces** — most
notably, a test set built with the customer's own subject-matter experts, which often contains real
customer data (real questions, real account details used as examples).

If that test set is stored identically for a regulated customer and a low-sensitivity trial customer,
that's a residency/encryption gap in the delivery process itself — independent of anything the
deployed system does. A reusable tool for building this kind of test set is fine to share across
engagements; the **data it produces per engagement** still needs to be handled according to that
specific customer's sensitivity tier, not a one-size-fits-all default.

## 4. Running many engagements at once — reframed as a tenancy decision

A framework built to model one engagement at a time will eventually need to model many customers'
engagements running in parallel. The natural instinct is to treat this purely as a scheduling/capacity
problem (how many engagements can one team run at once) — but there's a security dimension underneath
it worth naming explicitly: **it's the same multi-tenancy decision every customer-facing system has to
make, just applied to the delivery process's own operational data.**

- Are two customers' engagement records, gate evidence, and test sets **separated only by a tag on a
  shared record** (the cheap default), or **physically separated** (stronger isolation)?
- If someone can query "show me all engagements," does that query structurally exclude a competitor's
  engagement data, or does it rely on remembering to filter?

Framing this as *the same decision* made everywhere else in a multi-tenant design — rather than a new,
unrelated scaling problem — is the stronger answer: it shows the isolation principle generalizes
across every layer of the stack, including the internal tooling nobody thinks of as customer-facing.

---

## What to say if asked directly

*"A gate can be structurally real — the right role has to sign it, the wrong role gets rejected — and
still have an evidence bar that's too weak to trust, if the evidence is free text instead of a
checklist. Closing that means making the sign-off require specific proof — adversarial testing done,
permission boundaries tested — the same way intake should refuse to start at all without a measurable
success metric. And credentials the delivery process itself holds to connect a customer's real
systems have exactly the same vault/rotation/scoping requirements as anything a deployed system holds
— it's just one step earlier in the process, which is why it's easy to overlook."*
