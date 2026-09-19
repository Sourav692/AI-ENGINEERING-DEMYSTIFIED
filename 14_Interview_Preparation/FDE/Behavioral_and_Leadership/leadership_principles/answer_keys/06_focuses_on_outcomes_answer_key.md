# Focuses on Outcomes - Answer Key

Spoken answers - 3 grounded, 1 partly grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. A team spread too thin

**PARTLY GROUNDED — AIA scope narrowing.** Fill in who was on the team.

*"Early at AIA, the pull was to cover everything at once: multiple business units, multiple markets, every document type, plus open-ended enterprise search on top of the BI use case. With `[FILL: team size / who]` and an 8-to-9-week window, that's a recipe for a wide, shallow system that no one trusts.*

*I refocused around the one outcome that actually mattered to the sponsor — self-serve, governed answers that replace the 2-to-10-day BI queue — and cut everything that didn't serve it. Scope went to governed data domains, not open-ended search. The first governed-retrieval build went to two business units in one market. Four specialist domains, not twelve. And I took the data-foundation work on myself so the rest of the team wasn't split between building agents and building tables.*

*The refocus wasn't 'do less'; it was 'prove the model on a narrow slice so expanding it later is a copy, not a rebuild.' Time-to-insight went from days to minutes on that slice, and that result is what earned the expansion conversation."*

## 2. Saying no to a distracting feature

**GROUNDED — declining the fancy retrieval strategy (Meridian) + open-ended search (AIA)**

*"On the enterprise RAG platform I benchmarked six retrieval strategies — keyword, dense similarity, hybrid, and a decomposition-plus-reranking approach that was the most sophisticated and the most fun to build. On the same golden set, every strategy scored zero leaks and near-identical quality; the sophisticated one was simply the slowest and most expensive. So I said no to shipping it, even though it was the more impressive thing to talk about. Dense retrieval was the right production choice at that corpus size, and I said that plainly instead of defending the clever option.*

*At AIA, the equivalent 'no' was open-ended enterprise search. The outcome that mattered was replacing the BI queue with governed, traceable answers. Open-ended search would have doubled the governance surface and delayed the thing the sponsor actually needed. It's on the roadmap; it wasn't in the MVP.*

*The test I apply: does this feature move the one number the customer is judging us on? If not, it waits — no matter how good it looks in a demo."*

## 3. Measuring success on a customer engagement

**GROUNDED — AIA success bar + honest attribution + Bajaj lesson**

*"Three layers, agreed before the build. The customer's outcome metric — at AIA, time-to-insight, which went from 2-to-10 days to minutes, and dashboard delivery, from a four-week queue to self-serve. The non-negotiable gates — zero leaks, explainability, latency — agreed with the sponsor and compliance before I wrote code. And the platform signal for my own company — about 35 percent year-to-date consumption growth after rollout.*

*And I hold myself to reporting those honestly: the 35 percent is correlated with the rollout, not a controlled experiment, and I say that unprompted. At Bajaj I didn't instrument resolution time per ticket type from day one, so I can't quote a hard number, and I won't invent one. The measurement plan is now part of the scoping conversation, not something I retrofit."*

## 4. Metrics looked good but the outcome wasn't there

**GROUNDED — Meridian 22/22**

*"The enterprise RAG platform scored 22 of 22 on the golden set — recall 1.0, groundedness 1.0, zero leaks, six retrieval strategies all near-perfect. It looks like a finished result. It isn't, and I said so in the write-up.*

*The corpus is 22 documents. At that size retrieval is easy, so every strategy scores well and the differences between them are noise. The table proves nothing about which strategy wins at 200,000 documents — which is the question a real customer would actually have. What it does prove, independent of scale, is the zero-leak gate and the testing discipline.*

*So I separated the claim I could make — 'the security property holds and the harness gates releases' — from the one I couldn't — 'this retrieval strategy is right for production.' And I wrote down what would need to be true to make the second claim: re-run the benchmark at a representative corpus size. Good numbers on the wrong question are the most dangerous kind, because nobody argues with them."*
