# Creates a Culture of Accountability - Answer Key

Spoken answers - 1 grounded, 1 partly grounded, 2 needing your input. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. Addressing underperformance directly

**NEEDS YOUR INPUT.** Suggested spine. If the honest answer is "as a senior IC, my version of this was addressing work that drifted from the customer's intent," say that.

*"`[FILL: who, what the gap was — missed commitments, work that didn't match customer intent, quality below the agreed bar].` I had the conversation early and specific: here is the agreed standard `[e.g., the zero-leak gate / the customer's success bar]`, here is where the work is against it, here is what changes by when. I separated the person from the work — the bar wasn't personal, it was the one we'd agreed with the customer. `[FILL: what support you gave — pairing, design review before code, clearer tickets].` Outcome: `[FILL — improved / moved to a better-fit role / exited]`."*

## 2. Inspecting work and giving consequences fairly

**GROUNDED — from the day-to-day doc + the eval-gate discipline**

*"I inspect at two points, and neither is 'end of sprint.'*

*First, before code: I review designs before they're built, because a wrong turn caught at the design stage costs an hour and caught after it ships costs a customer relationship. Second, daily and lightweight: I review what the team produced with two lenses — is it correct, and does it match what the customer actually asked for, which isn't always what the ticket says. Drift between those two is the thing I most want to catch today rather than next week.*

*For fairness, I make the standard mechanical wherever I can, so consequences follow from the bar, not from my mood. On the governed RAG work the release gate is a harness: one leak on the test set and it doesn't ship, whoever wrote it. I hold myself to the same gate — when it flagged my own work, I reported it, including that it turned out to be a false alarm from stale test data. Positive consequences are the same in reverse: the engineer whose design survives review gets the next higher-blast-radius piece and more customer-facing time. That's the reward that actually matters on an engagement team."*

## 3. Missing a commitment

**NEEDS YOUR INPUT.** If nothing fits, the honest adjacent example is the Bajaj measurement gap: you committed to an outcome you then couldn't prove. Suggested spine:

*"`[FILL: what was committed, to whom, and what slipped].` I told them before they found out, with the cause and the new date `[FILL]`. What I changed afterwards: `[FILL]`."*

*Adjacent, grounded version:* *"The commitment I'd most like back is at Bajaj — I committed to compressing ticket resolution time and then couldn't prove the delta, because I hadn't instrumented per-ticket-type resolution time from the start. I said so plainly rather than quoting an estimate as a result, and I now put the measurement plan in the scoping document."*

## 4. Holding a customer accountable for their side

**PARTLY GROUNDED — AIA access matrix / compliance dependency.** `[FILL: a concrete dependency that slipped]`

*"By making their dependencies explicit and visible from the start, so a slip is a shared fact rather than a surprise. At AIA the policy rules came from a role-by-document-type-by-market access matrix that only the customer's compliance and business teams could sign off. That sign-off was on the plan as a named dependency with a date, not an assumption inside my timeline. `[FILL: what slipped and how you raised it — e.g., 'when the compliance review ran late I showed the sponsor exactly which build steps were blocked on it, and we re-sequenced rather than absorbed it'].`*

*Two rules: never absorb a customer slip silently — it teaches them the dates don't matter — and always frame it as their outcome at risk, not my inconvenience."*
