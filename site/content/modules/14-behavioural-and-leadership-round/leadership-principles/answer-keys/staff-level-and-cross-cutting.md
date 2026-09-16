# Staff-Level and Cross-Cutting - Answer Key

Spoken answers - 7 grounded, 4 partly grounded, 2 needing your input. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. Conflict with a colleague or another team

**NEEDS YOUR INPUT.** Suggested spine, using your evidence-first stance:

*"`[FILL: who — a solutions architect, a delivery lead, a product engineer — and what the disagreement was: architecture, scope, timeline, which feature to demo].` I separated the disagreement about facts from the disagreement about priorities. For the facts, I brought `[FILL: the trace, the benchmark, the ticket data]` rather than an opinion. For the priorities, I put it in the customer's terms — whose risk, whose timeline — and proposed a specific alternative rather than just objecting. `[FILL: outcome, and what the relationship looked like afterwards].`"*

*If nothing fits, the honest answer is: "Most of my conflicts have been with my own first designs — but here's how I handle disagreement when it's with a person," then give the spine above as a method.*

## 2. Delegating something you'd rather have done

**PARTLY GROUNDED — day-to-day doc.** `[FILL: the specific piece and who took it]`

*"On an engagement like AIA there's a temptation to keep the interesting work — the orchestration layer, the access-control design — and hand off the rest. I try to invert that: the work I keep is the work only I should be doing, meaning the highest-blast-radius decisions where being wrong fails silently. Everything else, someone on the team should own, or I become the bottleneck.*

*`[FILL: what you delegated — e.g., a specialist agent, the evaluation dataset, the Genie Space curation — and to whom].` The way I make delegation safe isn't checking the code afterwards; it's a design review before the code exists, so the cost of a wrong turn is an hour, and a ticket that carries the customer's intent, not just the task. `[FILL: outcome — and ideally that the person now owns that area].`*

*The line I hold myself to: if I'm the only person who can make a decision, that's a failure of mine, not a sign of my value."*

## 3. Working across cultures, regions and time zones

**PARTLY GROUNDED — AIA (Hong Kong HQ, multi-market APAC), Bajaj (India), Barclays (APAC/EMEA/AMER).** `[FILL: a concrete friction and how you handled it]`

*"Most of my engagements have been cross-regional by nature. AIA is headquartered in Hong Kong with business units across several Asian markets, each with its own regulator — so 'the customer' was never one voice, and the access matrix had to be built market by market. Bajaj was an Indian NBFC with a very different operating rhythm. And `[FILL: Barclays — the ~700M-events/day migration spanned APAC, EMEA, and AMER teams]`.*

*Two practical things I've learned. First, discovery has to be run per region, not centrally: a rule that's fine in one market is a compliance problem in another, and you only find that by asking the people in that market. Second, async by default with explicit decisions in writing — a design review that ends with 'here is what we decided and why' in a shared document survives a time-zone gap; a verbal agreement doesn't. `[FILL: one concrete example].`"*

## 4. Delivering with unclear requirements

**GROUNDED — AIA brief + the confidence-gated clarification pattern**

*"The AIA brief was one sentence: business users need natural-language answers over governed data. No definition of which users, which data, what 'governed' meant per market, or what a wrong answer would cost. That's normal for an FDE engagement — the ambiguity is the job.*

*I resolved it in layers rather than waiting for a spec. First, discovery with users and separately with compliance, which produced the access matrix and the success bar. Second, a deliberately narrow first scope — two business units, one market — so the requirements I did have could be proven before the ones I didn't have mattered. Third, I built the ambiguity into the system itself: the Supervisor classifies intent with a confidence score, and below 60 percent it asks the user a clarifying question instead of guessing. 'Show me the numbers' gets 'Which numbers — claims, policies, agents, or customers?'*

*The instinct: don't try to remove ambiguity up front — you can't. Sequence the work so each unknown gets resolved by the cheapest possible means before it can hurt you."*

## 5. Ramping up on an unfamiliar domain

**GROUNDED — insurance (AIA) and lending ops (Bajaj)**

*"I'm not an actuary and I'm not a lending-operations engineer, and I've had to be credible with both.*

*At AIA the domain was life-insurance analytics — claims, policy performance, underwriting, agent productivity — with health-disclosure sensitivity on top. I ramped by building the data foundation myself: bronze, silver, and seven gold metric views. You can't define `enriched_claims` or a fraud-analysis metric view without understanding how the business thinks about a claim, so the build was the ramp. And I sat with the actuaries and claims managers directly rather than reading about their jobs.*

*At Bajaj the domain was a lead-routing pipeline with control flags, master tables, and a C# rules engine I'd never seen. I ramped by reading 182 real support tickets — the fastest way to learn how a system fails is to read how it's failed — and that reading became the architecture.*

*The pattern: ramp by producing something the domain experts have to correct. It's faster than studying, and it builds the relationship at the same time."*

## 6. Impact beyond a single project or team

**GROUNDED — reusable patterns carried AIA → Bajaj → reference builds**

*"The thing I try to leave behind isn't a system, it's a pattern other people can reuse without me. Three examples.*

*The specialisation lesson from AIA — one agent with twenty-plus tools fails, specialise early, keep each context small — became a design principle I applied proactively at Bajaj with a triage layer before the agent runs, and it's the shape of every agentic system I've built since.*

*The two-layer access-control pattern — fast pre-filter, live re-check before generation — started at AIA, and I rebuilt it as a standalone reference system with a golden-set harness and a second, Databricks-native version specifically to document the Vector Search / Unity Catalog governance gap, so anyone putting AI on governed data can pick it up without rediscovering it.*

*And the guardrail engine — approval gates, idempotency, crash recovery — is a runnable reference with 21 deterministic tests, built so 'we'd add guardrails' can be a demonstrated property rather than a slide claim. `[FILL: where these have actually been reused — a colleague, an enablement session, an internal doc].`*

*A Staff engineer's output isn't the engagements they ship; it's how many engagements ship better because of the patterns they left."*

## 7. Setting technical direction others followed

**PARTLY GROUNDED — same evidence as Q60.** `[FILL: who followed it]`

*"At AIA the direction was 'specialists over a monolith, and governance as structure, not prompt.' I didn't set it by decree — I set it by the first design failing in front of everyone, diagnosing the mechanism publicly, and then every subsequent piece — the Supervisor, the Deep Agent evolution, the Bajaj triage layer — following the same rule. `[FILL: who picked it up — engineers on the team, a later engagement, an internal pattern].` Direction people follow is direction they watched get proven."*

## 8. Something innovative you built

**GROUNDED — Deep Agent / Synaptic Command, Code Agent, graph-based RCA**

*"Three, in increasing ambition. At AIA the obvious fix for a bloated Supervisor was trimming its tool list. Instead I moved to a Deep Agent pattern — a central orchestrator delegating to fully self-contained subagents, each with its own prompt, tools, and context window, plus a dedicated memory-manager subagent maintaining categorised long-term memory across conversations. That removed the ceiling rather than postponing it.*

*At Bajaj the obvious solution to code-level bugs was 'point an LLM at the repo.' I built a Code Agent that does a deterministic one-file lookup first and hands the model only that file with four fixed questions — grounded by construction, not by asking the model nicely.*

*And the next step, which I've designed but not shipped: replace that single-file lookup with an AST-parsed code graph — functions and config keys as nodes, calls and reads as edges — that an agent walks outward from the entry point, then verifies its claimed root cause against a real failing log record before reporting. That closes the biggest trust gap in the current design.*

*Innovation for me isn't novelty — it's finding the ceiling of the obvious approach before the customer does, and building past it."*

## 9. A production incident or customer escalation

**NEEDS YOUR INPUT — Barclays is the natural home for this.** `[FILL: the incident on the ~700M-events/day pipeline, the go-live friction, who escalated, what you did in the first hour]`

*Adjacent, grounded version if nothing else fits:* *"The closest I've had on the AI engagements is a security escalation I raised on myself: my evaluation harness flagged a claims manager seeing a case outside their assignment. I treated it as a live incident — stopped, diagnosed before explaining, traced it to stale test data after a reassignment — and reported the whole sequence to the customer, including that it was a false alarm. The process I'd use for a real one is the same: contain, diagnose the mechanism, communicate with the cause and the next step, then add the check that makes the class of failure impossible."*

## 10. A request that is the wrong thing to build

**GROUNDED — Bajaj autonomy + AIA open-ended search**

*"I don't say no; I show them what the request costs in their own terms and offer the version that gets them the outcome.*

*At Bajaj the intuitive ask is a fully autonomous agent that fixes tickets end to end. The wrong part isn't the ambition — it's letting an LLM write to master tables that route live loan leads at a regulated lender. So I gave them the outcome — automated investigation, root cause in the ticket in minutes — with the write gated behind an engineer's confirmation, and I named the trade: slower resolution, zero unreviewed changes. They chose it once they saw the blast radius.*

*At AIA the ask was open-ended enterprise search. Right outcome, wrong first step — it would have doubled the governance surface before the narrow slice was proven. It went on the roadmap with a precondition, and the customer heard 'next,' not 'no.'*

*The customer is almost always right about the pain and often wrong about the mechanism. My job is to fix the mechanism without dismissing the pain."*

## 11. Doing right when nobody would notice

**GROUNDED — attribution caveats, doc-code sync, in-process state disclosure**

*"Small things, mostly, which is the point. At AIA the platform saw about 35 percent year-to-date consumption growth after rollout; nobody would have questioned that number as a result. I report it every time as a correlated signal, not a controlled experiment. At Bajaj I could quote an estimated resolution-time improvement and nobody would check; I say I don't have a client-confirmed number instead.*

*On the RAG platform I wrote a standalone check that fails the build if the security documentation drifts from the running policy code — nobody asked for it, and its only purpose is to make sure what compliance was told stays true after I've moved on. On the guardrail engine I documented that the locks are in-process and wouldn't survive a restart, in the coverage map, where a reviewer would find it.*

*None of these are dramatic. But the customer's security team is trusting a claim they can't verify themselves. If I'm loose with the small claims, they should assume I'm loose with the big ones."*

## 12. The achievement you're proudest of

**GROUNDED — AIA**

*"Proudest: AIA. Not the metrics — days-to-minutes time-to-insight, dashboards from a four-week queue to self-serve — but that it was hand-built in 8 to 9 weeks at a regulated insurer, survived its own first design failing mid-engagement, and shipped as something compliance could sign off on rather than a demo. The two pivots are the part I'm actually proud of, because each one came from diagnosing a mechanism rather than patching a symptom.*

*Differently, three things, all about sequencing. Bring compliance into the first round of discovery, not a second pass — it cost me a cycle. Instrument the outcome metric from day one so the 35 percent could be more than a correlated signal. And re-run the retrieval benchmark at a representative document count before trusting the MVP's result beyond its boundary. None of those are about the architecture. They're all about what I should have decided in week one instead of week four."*

## 13. Where you need to grow as a leader

**PARTLY GROUNDED — your material implies the honest answer; validate it.**

*"Two things I'd say plainly. First, I've led as a senior IC guiding engagement teams, not as a line manager — hiring, retention, and performance conversations are areas where I have principles but not a track record, and I'd want to be deliberate about learning them rather than assuming engineering judgment transfers. `[FILL: anything you've done toward this].`*

*Second, I default to solving the problem myself when the window is tight — AIA's data foundation is an example where that was the right call, but the habit has a cost: it's the fastest way to become the bottleneck. The day-to-day discipline I hold — unblock others first, review designs before code, protect deep work only for the highest-blast-radius decisions — is the counterweight, and it's something I have to keep choosing, not something I've finished learning."*
