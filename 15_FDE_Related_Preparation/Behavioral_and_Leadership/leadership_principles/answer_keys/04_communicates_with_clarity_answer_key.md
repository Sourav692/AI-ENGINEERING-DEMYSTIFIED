# Communicates with Clarity - Answer Key

Spoken answers - 2 grounded, 2 partly grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. Simplifying a technical message for a broad audience

**GROUNDED — AIA / Meridian two-layer access control**

*"At AIA I needed compliance, legal, security, and a business sponsor — none of them engineers — to sign off on how the retrieval agent enforced access over policy and claims documents with health disclosures. The real mechanism is a metadata pre-filter compiled into the Vector Search query plus a live re-check against Unity Catalog grants right before generation.*

*I didn't say any of that first. I said: there are two checkpoints. A fast one at the door that gets you into the right neighborhood of documents for your role and market. And a slower, careful one right before you're handed anything — because your permissions might have changed in between: a case reassignment, a revoked grant, a consent window closing. Most systems only build the first one and hope. I assumed it would go stale and built for that.*

*The outcome was that compliance could reason about it — they asked the right follow-ups, like 'what happens if the second check catches something,' and I could answer: that's logged as a security event, not swallowed. We agreed the success bar — zero leaks, explainability, latency — before the build started. The technical version came later, for the engineers, and it was the same story with the nouns swapped."*

## 2. Communication that was misunderstood

**PARTLY GROUNDED — from the day-to-day doc's "ticket says X, customer meant Y" pattern.** You must supply the specific instance.

*"`[FILL: engagement / engineer].` I handed off work through a ticket that described what to build, and the engineer built exactly what the ticket said — correctly — but not what the customer had actually asked for in the discovery session, because the customer's intent never made it into my handoff. `[FILL: the concrete drift — e.g., built a generic search when the claims manager needed case-scoped results].`*

*I owned that as my miss, not theirs. Two changes: I started reviewing designs before code was written rather than after, so a wrong turn costs an hour instead of a sprint; and I started writing the customer's intent and success bar into the ticket alongside the task — 'the claims manager needs to see only cases assigned to them, because X' — not just the task. `[FILL: outcome].` The general lesson I took: a lot of what looks like a technical question from an engineer is actually an ambiguity I left in the scope."*

## 3. Communicating technical risk to an executive

**GROUNDED — AIA Beta feature + Bajaj blast radius**

*"I translate the risk into what it costs them and who controls it — never into the technology.*

*At AIA, the managed Multi-Agent Supervisor wasn't GA in their region. I didn't say 'Agent Bricks isn't GA in SEA.' I said: 'The core of your production system would depend on a Beta feature whose rollout date in your region neither you nor I control. If it slips, your launch slips. I'd rather own more code than hand your timeline to a roadmap.' The sponsor could weigh that.*

*At Bajaj, the question was whether the agent could change production master tables on its own. I put it as: 'A wrong write here misroutes real loan leads at a regulated lender, and you can't un-send those. The trade is slower ticket resolution for zero unreviewed changes. I recommend the slower path.' They chose it in one conversation.*

*The pattern: name the failure in their terms, name who controls it, name the trade, make a recommendation. Executives don't need the mechanism — they need to know what they're deciding."*

## 4. Influencing people without authority

**PARTLY GROUNDED — AIA data / BI team and compliance.** `[FILL: names/roles]`

*"At AIA I had no authority over the customer's data team or their compliance function — and I needed both. The data team owned the tables my agents would query; compliance owned whether the system could touch documents with health disclosures at all.*

*With the data team, influence came from doing the work with them rather than around them: I built the bronze, silver, and gold metric views inside their Unity Catalog, and endorsed assets — the ones they'd reviewed — were prioritised in the Context Index routing. Their governance decisions were literally what the agents obeyed, so they had a stake in the system working.*

*With compliance, influence came from giving them the decision instead of asking for permission: 'Here's the two-checkpoint model in plain terms; you tell me what zero leaks means for your regulators; that's our release gate.' They set the bar, so they defended it. `[FILL: outcome / a moment where this paid off].`*

*The general rule: people back what they helped decide. Authority is a poor substitute for that."*
