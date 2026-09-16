# Stakeholder Influence - Answer Key

All four drafted. This is the strongest section in the set — nothing here is marked NEEDS INPUT.

## 1. Explaining a technical tradeoff to a non-technical executive

**Anchor:** multi-agent autonomy debate, insurance client.

- **Situation.** Leadership wanted the agent system to make decisions autonomously. Engineering knew the failure modes.
- **Task.** Get alignment on a constrained rollout without sounding like I was slowing them down.
- **Action.** I reframed from "can the model do this" to "what happens on the day it's wrong, and who answers for it." I walked them through the observability layer — MLflow tracing on every agent step — so the tradeoff became concrete: full autonomy meant no defensible audit trail; supervised autonomy meant every decision was reconstructable.
- **Result.** They chose the supervised path, and traceability became what they cited when [risk / compliance] reviewed the system.

**Why it lands.** You translated a technical constraint into a governance argument — the language executives already speak.

## 2. Disagreeing with a customer executive

**Anchor:** the tier-1 bank migration.

- **Situation.** Multi-region programs almost always contain a sequencing disagreement — [which region first, or big-bang versus phased cutover].
- **Action.** Frame the disagreement as risk, not preference. Argue from the escalation surface: what happens to APAC trading hours if EMEA cutover goes wrong, and who is awake to fix it.
- **Result.** Zero go-live escalations across all three regions — cite this as vindication, briefly, without gloating.

**The trap.** Picking a disagreement you won easily. Choose one where you had to concede something.

## 3. Technical buyer versus economic buyer

**Anchor:** the insurer. Strongest story in this section — it has a commercial number attached, which most engineers can't produce.

- **Situation.** Platform teams wanted capability and control; the budget holder was measuring demonstrable consumption and ROI.
- **Action.** Didn't pick a side — found the overlap. Governance was what the platform team needed to feel safe expanding, and expansion was what the economic buyer was measuring.
- **Result.** 35% adoption revenue growth in two months — proof both sides got what they wanted.

## 4. Building trust with a skeptical chief architect in 30 days

Method question.

- Concede their expertise on their own estate before proposing anything. They know things about their systems you won't learn in a month.
- Ship something small and real in the first two weeks. The 40+ scripts contributed to global codebases is the right kind of evidence — you gave before you asked.
- Be the person who names the risk they were privately worried about. Skeptical architects are usually skeptical because they've watched a vendor gloss over something.
- Don't oversell the platform. Naming what Databricks isn't good for buys more credibility than anything you claim it is good for.
