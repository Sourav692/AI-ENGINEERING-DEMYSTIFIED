# Ambiguity and Discovery - Answer Key

Drafted from documented engagements. Three of the four are ready to deliver; the fourth is marked NEEDS INPUT because it is failure-shaped and cannot be written for you.

## 1. Customer asked for something they didn't need

**Anchor:** multi-agent work for the insurance client.

- **Situation.** The client came in asking for a chatbot over their [claims / policy] knowledge base. The stated ask was a RAG assistant.
- **Task.** Before building, run discovery with the [operations and risk] teams to understand what the assistant was meant to replace.
- **Action.** What surfaced was that a single-turn RAG lookup couldn't cover the actual workflow — the work required retrieval, cross-referencing, and a verification step nobody wanted a model doing unsupervised. I proposed a Supervisor–Worker multi-agent design instead: specialised workers for search, summarisation, and drafting, with a verification agent and a human checkpoint before anything left the system.
- **Result.** We shipped an architecture matching the real workflow rather than the requested one. [Add outcome metric — adoption, cycle-time reduction, or workflows onboarded.]

**Why it lands.** It shows you challenged the framing before writing code, which is the entire FDE job.

**Still open.** The result metric is a placeholder. The answer is structurally sound but lands softer without a number.

## 2. Week one with unclear requirements

**Anchor:** the insurer's Unity Catalog governance rollout.

- **Situation.** "We need governance" is one of the vaguest asks in enterprise data.
- **Action.** Week one wasn't design, it was inventory — mapping what data existed, who was touching it, and where PII actually lived versus where they believed it lived. The gap between those two was the real finding.
- **Result.** That inventory became the scoping document. It enabled a zero-downtime rollout rather than a big-bang cutover, and adoption revenue moved 35% in two months.

**Say out loud.** Week one was spent reducing uncertainty, not producing artifacts.

## 3. Running discovery with a client who can't articulate the ask

Method question, not a story question. Give the process, then one illustration.

- Start from what's painful today rather than what they want to build — pain is concrete, aspiration isn't.
- Get current-state numbers early: runtimes, failure rates, manual hours. They anchor everything downstream and give a baseline to claim credit against later.
- Talk to the people doing the work, not only the people sponsoring it. The sponsor describes the intended workflow; the operator describes the real one.
- Put a strawman architecture in front of them fast. Clients who can't articulate requirements can almost always react to a proposal.

**Illustration.** The multi-agent RCA engine — vague ask, discovery surfaced a repeating manual investigation loop, and that pattern justified building the tooling.

## 4. A project you scoped incorrectly

**NEEDS INPUT — this one is yours to write.**

**What's being tested:** whether your estimates are calibrated, and whether you notice mid-flight or only at the deadline.

**Likely anchor:** the tier-1 bank migration across APAC/EMEA/AMER — multi-region scope is where estimates usually break.

To draft this, supply:

1. Which engagement and roughly when.
2. The commitment you made in specific terms — timeline, workload count, or performance target.
3. What you didn't account for. Common honest candidates: source-system complexity found only after profiling, an undisclosed downstream consumer, regional data-residency constraints, or a client team less available than staffed.
4. How early you caught it and how you re-baselined with the client.
5. What actual delivery looked like versus the original commitment.
6. What you now ask for in discovery that you didn't ask for then.

**The trap.** Blaming discovery quality without owning that discovery was your job. Say "I didn't ask X," not "they didn't tell me X."
