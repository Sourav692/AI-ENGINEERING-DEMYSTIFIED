# Pushback and Saying No - Answer Key

Three drafted, one NEEDS INPUT.

## 1. Telling a customer no

**Anchor:** multi-agent guardrails, financial services.

- **Situation.** The client wanted agents extended into [an automated decisioning path] with no human in the loop.
- **Task.** Decline the scope without losing the account relationship.
- **Action.** I didn't argue from principle. I ran adversarial red-teaming against the deployment using PyRIT and brought the results to the table — concrete cases where the system produced confident wrong output under adversarial framing. Then offered the alternative: keep the automation, add a confidence threshold and human escalation above it.
- **Result.** They accepted the constrained design. The red-team findings became [part of the standing evaluation suite / a reusable pattern across accounts].

**Why it lands.** "No" backed by evidence you generated is the senior version. "No" backed by opinion is the junior version.

## 2. Scope creep on a fixed-timeline engagement

- **Anchor.** Any migration engagement — scope creep is universal there.
- **Action.** You don't refuse additions, you price them in time. Every new request gets logged against the timeline visibly, so the customer makes the tradeoff rather than you absorbing it silently.
- **Result.** [A specific instance where a request got deferred to a phase two, and the customer accepted it.]

**Senior framing.** Absorbing scope quietly feels helpful and is the most common way engagements fail. Say that.

## 3. Pushing back on your own company's roadmap

**Anchor:** your field-to-product feedback loop.

- **Action.** [A specific case where a customer requirement wasn't served by the product as shipped and you either built around it or carried it back to engineering. Overwatch and UNIQ both started as gaps between what the product did and what the field needed.]
- **Result.** [Whether it shipped, or whether the workaround became reusable IP.]

**Why this question exists.** They're checking you'll advocate for the customer internally, not just represent the company externally. FDE roles fail when the engineer becomes a pure sales extension.

## 4. Walking away from an approach mid-project

**NEEDS INPUT — this one is yours to write.**

**What's being tested:** sunk-cost resistance. Can you kill your own work?

**Likely anchor:** the multi-agent or RAG work, where an initial architecture stops holding under real data — a retrieval strategy that didn't survive contact with the corpus, an agent topology that looped, or an orchestration choice you replaced.

To draft this, supply:

1. The engagement and the approach you abandoned.
2. How much had already been built when you concluded it wouldn't work.
3. What the evidence was — evaluation results, a latency ceiling, a cost curve.
4. How you made the case to the client to discard work they'd already paid for.
5. What the replacement did better.
6. How long the rebuild actually cost versus the projection if you'd continued.

**The trap.** Picking a case where you walked away in week one. That's not a hard call. Pick one with real invested effort.
