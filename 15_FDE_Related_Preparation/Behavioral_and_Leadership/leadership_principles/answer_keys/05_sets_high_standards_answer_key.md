# Sets High Standards - Answer Key

Spoken answers - 4 grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. Holding the team to a higher bar

**GROUNDED — zero-leak release gate (Meridian / AIA)**

*"For the governed RAG work, the expected bar for an AI system is a quality metric — recall, groundedness — plus 'the model refuses nicely.' I set a different bar: a build that produces even one access leak on the governed test set does not ship. Not 'low leak rate.' Zero. And a security decision is never made by the model's judgment — hard rules only.*

*How I communicated it mattered more than the rule. I agreed it with the business sponsor and compliance before the build began, so it wasn't my personal preference — it was the customer's definition of done, and everyone knew it going in. Then I made it mechanical: an evaluation harness that gates the release, plus a standalone check that fails if the security documentation drifts from the running policy code — so what we'd told compliance couldn't silently diverge from what was deployed.*

*And I held myself to it publicly: when the harness flagged a leak on my own work, I reported it — including that it turned out to be a false alarm from stale test data. A bar you only apply to other people isn't a bar."*

## 2. Pushing back on good-enough work

**GROUNDED — the flaky LLM-judged security test (Meridian)**

*"On the enterprise RAG build I had a test that passed most of the time. The temptation was to call it flaky and move on — the numbers were 22 of 22 on the golden set, everything else was green.*

*I dug into why it wasn't deterministic, and the reason was that I'd let the LLM's own judgment sit inside a security-critical pass/fail decision. 'Mostly passes' is fine for 'was the refusal phrased well.' It is not fine for 'did we leak a document.' So I split them: leak/no-leak is decided by hard rules, never the model; tone is a separate, judgment-based check that's allowed to be soft.*

*Same instinct at AIA: the first single-agent design worked in demos. It was 'good enough' until real testing, where it picked the wrong tool because nothing was specialized. I re-architected live mid-engagement rather than ship something that demoed well and failed quietly. The rule I use: good enough is fine for things that fail loud. It's never fine for things that fail silent."*

## 3. Defining done for an AI system

**GROUNDED — Meridian / AIA / Agent Platform**

*"Done is a property you can prove, not a demo that went well. For the governed RAG work, done meant four concrete things. A release gate: the evaluation harness runs the golden set and one leak fails the build. A separation of concerns: leak/no-leak is decided by hard rules, never the model — a security decision can't be probabilistic. Diagnosability: every node traced in MLflow, so a wrong answer can be walked back to the exact tool call that produced it, not just noticed. And documentation that can't drift: a standalone check that fails if the security reference no longer matches the running policy code, so what compliance was told stays true.*

*Plus one honesty requirement: the limits are written down. The 22-document corpus caveat, the in-process locks in the guardrail engine that wouldn't survive a restart — named in the docs, not discovered by the customer. A system that claims to have no edges isn't done; it's untested."*

## 4. Shipping something you knew wasn't perfect

**GROUNDED — Agent Platform in-process state + Bajaj triage**

*"Deliberately, and in writing. On the agent guardrail engine, the entity locks and idempotency-key store are in-process Python dictionaries — correct in shape, but they don't survive a restart or share across workers. I shipped it that way because the point of the build was to prove three properties — no destructive action without approval, no double-apply on retry, no re-run after a crash — and those properties don't depend on where the keys are stored. I documented it directly in the coverage map with the production path: same key shape, moved to Redis or Postgres.*

*At Bajaj, the triage classifier is pattern-based — cheap, interpretable, and brittle to phrasing drift — and the 30 percent of tickets that were clarification round-trips have no path at all yet. I flagged both as the next gaps rather than letting the demo imply they were solved.*

*Imperfect is fine when the imperfection is chosen, bounded, and written down. It's not fine when it's discovered."*
