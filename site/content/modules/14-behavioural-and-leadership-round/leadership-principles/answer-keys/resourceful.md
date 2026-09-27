# Resourceful - Answer Key

Spoken answers - 3 grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. A significant result with limited headcount

**GROUNDED — a large Asian life insurer, about two months, hands-on**

*"At the insurer, I had about two months to replace a BI queue where an ad-hoc question took days and a dashboard took weeks. There wasn't a large delivery team behind it — I architected, built, and shipped the MVP hands-on, including the Unity Catalog data foundation underneath the agents.*

*Two things made that possible. First, I leaned on managed platform primitives wherever they were good enough — Genie Spaces (now called Genie Agents) for text-to-SQL rather than a hand-rolled chain, Vector Search with managed embeddings, Model Serving with an AI Gateway in front — and spent the hand-built effort only where the platform had a gap: the Supervisor logic, because the managed multi-agent feature wasn't an option for this customer at the time. Second, I designed for iteration without redeploys — prompts in a governed table, per-node MLflow tracing — so tuning was cheap and a wrong answer was diagnosable in minutes.*

*Result: a production-grade MVP in the window, days-to-minutes time-to-insight, dashboards moved from weeks in a queue to self-serve via the Visualization agent, and adoption grew afterward — a correlated signal, not a controlled experiment."*

## 2. A constraint that forced a creative solution

**GROUNDED — hand-built supervisor (insurer), with the Vector Search / Unity Catalog gap as a second**

*"At the insurer, the managed multi-agent feature — exactly the pattern I needed — wasn't an option for this customer at the time. And I couldn't leave a production system's core path waiting on it.*

*So I built the Supervisor myself as an 8-node LangGraph state machine on standard platform pieces: classify intent with a confidence score, ask a clarifying question below 60% confidence, resolve governed assets once through a central Context Index, route to one of four specialists, compose the answer. More code to own — but a production path that didn't depend on a roadmap I didn't control. And it turned out to be an advantage: because I owned the orchestration, I could evolve it into the Deep Agent pattern when the Supervisor hit its own ceiling.*

*A second constraint on the same engagement: the platform's Vector Search index — it's called AI Search now — is a derived copy of the governed data — it doesn't inherit Unity Catalog's row-level rules. A revoked grant at the source doesn't reach the index. That constraint is what produced the two-layer design: fast pre-filter for speed, live grant re-check right before generation for correctness. The constraint didn't limit the design; it defined it."*

## 3. Reuse or buy versus build

**GROUNDED — Genie managed text-to-SQL vs hand-built Supervisor; RAG vs rules engine at a large Indian consumer lender**

*"I made both calls on the same engagement, and the reasoning was the same each time: build only where the platform has a gap that matters.*

*At the insurer, for the BI specialist I used Genie Spaces — a managed text-to-SQL service — rather than hand-rolling a chain. It's less flexible, but its generated SQL is always read-only, so a prompt or SQL injection can't change the data — a much smaller blast radius — and the insurer's own analysts could curate it without an engineer. For the orchestration layer I built, because the managed multi-agent feature wasn't an option for this customer at the time.*

*At the lender, the alternative to RAG over historical tickets was a hand-coded decision tree — 'if the ticket mentions X, do Y.' I chose retrieval because a rules engine needs constant manual maintenance as phrasing drifts; retrieval generalises across phrasing at the cost of being only as good as the seed examples.*

*The test I use: does building it give the customer something the managed option can't — control over a constraint, a smaller attack surface, independence from a timeline? If not, buy it and spend the engineering where it counts."*
