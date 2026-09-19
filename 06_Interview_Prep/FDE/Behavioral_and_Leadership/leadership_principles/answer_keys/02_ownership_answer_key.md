# Ownership - Answer Key

Spoken answers - 4 grounded, 2 partly grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. Company's interests over your own career

**PARTLY GROUNDED — AIA (regional constraint + honest attribution).** Validate the framing: as a Databricks FDE, the "career" move is to showcase the newest product feature.

*"At AIA, Databricks' own Multi-Agent Supervisor in Agent Bricks was the natural thing to showcase — it's the managed version of exactly the pattern I needed, and demoing the newest product feature to Asia's largest life insurer is good for an FDE's profile. But it wasn't GA in AIA's Azure region at the time.*

*I built the Supervisor myself in LangGraph on GA primitives — Agent Framework, Model Serving, Genie, Vector Search, Metric Views, MLflow tracing. That's more code to own, less visible product adoption on my part, and a less flattering story internally than 'customer adopted the new feature.' But the company's real interest is a production system that doesn't depend on a Beta regional timeline nobody controls — and durable consumption. The engagement saw about 35% year-to-date consumption growth after rollout.*

*And when I report that number, I say plainly it's a correlated signal, not a controlled experiment — even though the uncaveated version would look better on my record. `[FILL: if there was an internal conversation about using the Beta feature anyway, name who pushed and what you said.]`"*

## 2. A task outside your job description

**GROUNDED — AIA (data foundation)**

*"The AIA engagement was scoped as advisory-plus-semi-implementation on the agent layer. The data foundation the agents would query was, on paper, someone else's problem.*

*It quickly became clear the agents couldn't be governed if the data wasn't. So I built the Unity Catalog foundation myself: bronze tables for products, agents, customers, policies, claims and policy documents; silver enrichment joins — `enriched_claims`, `enriched_policies`, `customer_360`; and seven reviewed gold-layer metric views for claims, policy performance, agent productivity and fraud analysis. The agents query those metric views instead of touching raw tables, which is what makes every answer traceable to a governed source.*

*It wasn't the glamorous part of an AI engagement, and it wasn't in my lane. But 'every number traces back to governed data' was the property the customer actually needed, and nobody else was going to deliver it inside an 8-to-9-week window. I'd rather own the unglamorous dependency than ship an agent layer sitting on sand."*

## 3. Short-term deliverable versus long-term goal

**GROUNDED — AIA (Supervisor now, Deep Agent later)**

*"At AIA I had an 8-to-9-week commitment to a working MVP, and partway through, the Supervisor architecture was working — four specialist agents, confidence-gated routing, all fine. But I could see the long-term problem: as domains grew, the Supervisor's own tool list was going to re-approach the exact context-bloat failure that killed my first single-agent design, one level up the stack.*

*The tension was: re-architect now into a Deep Agent pattern and risk the deadline, or ship the Supervisor and accept a known ceiling. I did neither purely. I shipped the Supervisor on time — the customer got days-to-minutes time-to-insight — but I made two choices that kept the long-term path open: prompts lived in a governed Delta table with a five-minute cache so behavior could be tuned without a redeploy, and the Context Index was resolved centrally so specialists were already loosely coupled. Then, once domain growth made the ceiling concrete rather than theoretical, I evolved it into the Deep Agent pattern with self-contained subagents and a memory-manager subagent.*

*The principle: ship the deliverable, but don't let it foreclose the strategic direction — and refactor when the pressure is real, not speculative."*

## 4. A project that failed or missed expectations

**GROUNDED — AIA v1 + Bajaj metrics honesty**

*"Two, at different scales. The clean failure was AIA version one — the single do-everything agent. It worked in demos and failed in real testing. What I learned wasn't 'use a Supervisor'; it was the mechanism — undifferentiated responsibility in one context window degrades a model's tool selection — and that mechanism let me predict the same failure one level up the stack later, and pre-empt it at Bajaj with a triage layer before the agent ever runs.*

*The quieter shortfall was Bajaj itself. I shipped a working triage-to-RCA system, but I don't have a client-confirmed before/after resolution-time number, because I didn't instrument per-ticket-type resolution time from day one. I can defend an estimate — 50 to 60 percent of ticket volume was a strong automation fit — but I can't prove it, and I say that plainly. The lesson I've carried since: agree the success metric and instrument it before the first line of code, not as a retrofit. That's now the first thing I do on any engagement."*

## 5. Feeding field learning back into product

**PARTLY GROUNDED — AIA is tagged "Field → Product feedback loop" in your STAR deck.** `[FILL: who you fed it to and what happened]`

*"Two things from AIA went back to the product side. First, the regional gap: the Multi-Agent Supervisor wasn't GA in AIA's Azure region, so I hand-built it on GA primitives — and that hand-built version is a concrete, working spec of what a regulated APAC customer needed from the managed feature: confidence-gated clarification, a central asset index shared across workers, prompts tunable without redeploy. `[FILL: who you shared it with — product/PM, and any outcome].`*

*Second, the governance gap: a Vector Search index is a derived copy and doesn't inherit Unity Catalog's row filters. That's not an AIA-specific finding — every customer putting AI on governed data hits it. I documented the two-layer enforcement pattern and `[FILL: where it went — internal solution pattern, field enablement, product feedback].`*

*The principle: an FDE is the earliest signal the product gets about what a real customer's constraints look like. If that signal stays in the engagement, half the value is wasted."*

## 6. Handling scope creep on an engagement

**GROUNDED — AIA**

*"By deciding what 'done' means with the sponsor before the build, so scope creep has something to be measured against. At AIA the success bar was agreed up front — self-serve, governed answers replacing the 2-to-10-day BI queue, with zero leaks, explainability, and acceptable latency, on two business units in one market.*

*When requests came in — open-ended enterprise search, more markets, more document types — I didn't refuse them; I asked whether they moved that bar within the 8-to-9-week window. Most didn't. They went on a written expansion path with a stated precondition — 'once the zero-leak gate holds on the first slice' — so the customer heard 'next,' not 'no.'*

*Where I did absorb extra scope was the data foundation, because without governed metric views the agreed bar was unreachable. That's the test: scope that serves the agreed outcome, I take on; scope that adds surface without moving the outcome, I sequence. And I have that conversation myself, directly with the sponsor, rather than routing it through a delivery lead."*
