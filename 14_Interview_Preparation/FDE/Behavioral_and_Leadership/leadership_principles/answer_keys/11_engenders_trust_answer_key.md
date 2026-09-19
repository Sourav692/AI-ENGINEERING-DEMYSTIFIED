# Engenders Trust - Answer Key

Spoken answers - 3 grounded, 2 partly grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. Admitting a mistake to your team

**GROUNDED — the false-alarm leak + the failed first architecture**

*"Two, and I'll take the one that's more uncomfortable. On the governed RAG work my own evaluation harness flagged a leak — a claims manager shown a case outside their assignment. I raised it as a potential security incident before I'd fully diagnosed it. It turned out the manager had actually just been reassigned that case: my test data was stale, not the system.*

*I reported the whole thing — the alarm, the false alarm, and the fact that I'd mislabeled my own test data by confusing 'not relevant to this question' with 'not allowed to see it.' Then I added a check so those two ideas can never be conflated again, because a false security alarm is worse than no alarm — people learn to ignore it.*

*The response `[FILL: from the team / the customer — e.g., compliance said it was the first time an AI vendor had shown them a failure]` was more trust, not less. And on the same engagement I'd already told the sponsor mid-build that my first architecture didn't work and why. What I've found is that the failure you volunteer builds more trust than the clean track record you present."*

## 2. Building trust with a skeptical team

**PARTLY GROUNDED — entering AIA as the external FDE.** Validate the dynamic: the BI/analyst team whose queue you were "replacing" had every reason to be wary.

*"At AIA I arrived as an external engineer proposing to replace the BI queue that an existing analyst and data team ran. From their side, I was the person whose project made their work look like a bottleneck. `[FILL: who specifically — the BI lead, the data engineering team].`*

*I didn't build trust by presenting. I built the Unity Catalog foundation with them — bronze, silver, and the seven gold metric views — so the agents queried assets they had reviewed and endorsed, not a parallel copy I'd built around them. Endorsed assets were prioritized in the Context Index routing, which meant their governance decisions were literally what the agents obeyed. I reviewed designs with them before code, and when my first architecture broke in testing, I told them so and showed the tracing rather than hiding it.*

*By the time the MVP shipped, `[FILL: concrete sign of trust — they owned the metric views, they curated Genie Spaces themselves, they demoed it to their own stakeholders].` The system didn't replace them; it made their governed data the thing every business user finally reached."*

## 3. Acting on feedback that disconfirmed your belief

**GROUNDED — the retrieval benchmark + the 182-ticket analysis**

*"I believed the decomposition-plus-reranking retrieval strategy was the right production choice for the enterprise RAG platform — it's the sophisticated approach, and I'd put real effort into it. Rather than trust that, I benchmarked it against five simpler strategies on the same golden set.*

*The data disagreed with me. At that corpus size every strategy scored zero leaks and near-identical quality, and my preferred one was simply the slowest and most expensive. I wrote that down plainly — dense retrieval is the right choice here, the fancy one hasn't earned its keep yet — and documented the condition under which the answer would flip.*

*Same thing at Bajaj, before writing a line: I assumed IT-support tickets were one shape. I went through 182 real tickets and found three — and that 30% were clarification round-trips my design didn't handle at all, which I flagged as the next gap rather than pretending it was solved. The habit I try to keep: build the measurement before the opinion hardens, and when the measurement disagrees, say so in the same sentence you'd have used to claim the win."*

## 4. Building trust with security and compliance

**GROUNDED — AIA / Meridian**

*"Four things, and none of them are a slide. Let them set the bar: I asked AIA's compliance team what zero leaks meant for their regulators and made that the release gate, so it was their standard I was meeting, not mine. Make the guarantee mechanical: the evaluation harness gates the release, and a security decision is a hard rule — the model's judgment is never in that path. Make the documentation unable to lie: a standalone check fails if the security reference drifts from the running policy code, so what they were told stays true. And report failures first: when my own harness flagged a leak — which turned out to be stale test data — they heard about it from me, including the false alarm.*

*Security teams don't trust systems that claim to have no edges. They trust the person who shows them where the edges are."*

## 5. Pushing back on a senior leader

**PARTLY GROUNDED — AIA scope / Beta feature.** Same spine as Q30 and Q3; `[FILL: who, and the moment]`. Use Q30 if the pushback was on scope, Q3 if it was on the Beta feature. Don't use both in one loop.
