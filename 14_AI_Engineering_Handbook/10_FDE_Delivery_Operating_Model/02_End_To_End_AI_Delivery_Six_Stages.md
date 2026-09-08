# End-to-End AI Delivery in Six Stages

> **Level** 🔴 The FDE Role · **Module** 10 · **Doc** 2 of 7 · **Time** ~20 min
> **Prerequisites:** Module 02
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/9. Proj Delivery.md`

## Why this matters

*"Walk me through an end-to-end AI project you delivered."* A storytelling question in disguise. It probes five things at once: end-to-end ownership (business problem → data → model → production → impact, or does the story stop at "we trained a model"?), systems thinking, practical production experience, trade-off awareness, and whether you can simplify complexity for a stakeholder. Most candidates ramble through a chronology or jump into algorithms without saying why any of it mattered. This document is the structure that prevents both.

## The six stages

Think of it as a story, not a status report:

```
1. Problem &         2. Data Understanding   3. Approach &
   Business Context  →  & Preparation        →  Modeling
                                                     │
6. Impact &          5. Deployment &          4. System Design
   Learnings         ←  Productionization     ←  & Architecture
```

Notice the shape: two stages of context and understanding, one of modelling, two of engineering and production, one of reflection. **Most candidates over-invest in stage 3 and under-invest in the other five.**

| # | Stage | What to cover |
|---|---|---|
| 1 | Problem and business context | What were you solving, and why did it matter — the business impact |
| 2 | Data understanding and preparation | Sources, quality challenges, feature or corpus decisions |
| 3 | Approach and modelling | Why AI was needed versus rules; model or strategy choices and trade-offs |
| 4 | System design and architecture | Pipeline, tools, infrastructure, batch vs real-time |
| 5 | Deployment and productionisation | CI/CD, monitoring, retraining or re-evaluation, scaling |
| 6 | Impact and learnings | Business and model metrics; what you would improve |

For an AI-engineering project, stages 2–5 map directly onto this handbook: Module 04's ingestion for stage 2; retrieval strategy comparison for stage 3; the query graph for stage 4; Module 08 for stage 5.

## Do and do not

**Do:** anchor everything to business value; use specific numbers — accuracy, latency, revenue; show trade-offs — not "we chose X" but *why*; demonstrate cross-functional collaboration; mention failures or iterations — it adds credibility; keep it structured.

**Do not:** jump straight into algorithms without context; list tools like a resume dump ("used Spark, MLflow…"); describe a toy or academic project; ignore production — a red flag; overclaim impact without measurable results.

## Layered depth

Use the framework explicitly. Keep the first pass within **3–5 minutes**, then go deeper only where the interviewer shows interest. Start high-level and expand based on their questions. This signals seniority far more than reciting every detail up front. And highlight **decision points**, not just actions: the interviewer wants to hear *why* you chose gradient boosting over logistic regression — or hybrid retrieval over dense — not just that you did.

## A worked answer: churn prediction

> "Let me walk you through an end-to-end AI project we executed to optimise customer churn prediction for a subscription platform."

1. **Problem** — ~18% monthly churn, significant revenue impact. Goal: predict churn early and enable targeted retention.
2. **Data** — CRM demographics, product usage logs, support tickets. Key challenge: fragmentation and inconsistent IDs. Built a unified customer view; engineered engagement frequency, usage-drop patterns, support sentiment.
3. **Modelling** — baseline logistic regression, then gradient boosting for non-linear capture. Trade-off: slightly less interpretable, in exchange for significantly higher recall for churners (+22%).
4. **Architecture** — a lakehouse pipeline: ingestion → feature engineering → training → serving. Batch daily scoring; a feature store for train/inference consistency.
5. **Deployment** — a REST endpoint for real-time scoring, integrated with the marketing system for automated campaigns; drift monitoring, a monthly retraining pipeline, an A/B framework.
6. **Impact** — recall improved ~25%; targeted campaigns reduced churn ~6% overall; multi-million-dollar annual retention impact.
7. **Learnings** — feature quality mattered more than model complexity; early stakeholder alignment avoided rework; monitoring was critical — the model degraded after three months without retraining.

```
Ingestion → Feature Engineering → Model Training → Serving
                    ▲                                 │
                    │                          ┌───────┴────────┐
                    │                          ▼                 ▼
              (retrain)                REST Endpoint      Marketing System
                    │                (real-time scoring)  (auto campaigns)
                    └──────── Drift Monitoring · Monthly Retraining · A/B Testing
```

The retraining loop is the detail most candidates leave out — and the one senior interviewers listen for. In an LLM system its analogue is Module 06 doc 3's scheduled evaluation and Module 08's production monitoring.

## Why the answer works

Clear structure — the interviewer never has to guess which stage you are in. Business-first — it opens with churn and revenue, not with the algorithm. Real trade-offs — interpretability vs performance, named. Production focus — deployment, monitoring and retraining all get airtime. **Quantified impact** — recall, churn reduction and revenue, all with numbers: the single highest-leverage habit in the whole answer.

## The senior bar

Execution gets you in the room; influence gets you the offer. At senior level the bar shifts from *what did you build* to *what did you change*. Talk about how you influenced decisions, not just implemented them. Mention team coordination and governance — how work was divided, who was accountable (the next documents in this module). Highlight scalability and reusability — platform thinking, not one-off delivery. The difference between "I built a churn model" and "I built a churn platform other teams now reuse."

## Applying it to the projects in this handbook

Module 11's narratives are this framework applied to Meridian Assist and the Agent Platform — with one addition the FDE context demands: a *requirements gathering and scoping* stage before the build, and a *governance and security* stage weighted heaviest for an enterprise audience. Read the six stages as the skeleton; read Module 11 for how the skeleton is dressed for a specific audience.

## Checkpoint

- Name the six stages and the shape of the investment across them.
- What five things does the question probe?
- Give one "do not" and say why interviewers hear it as a red flag.
- What is layered depth and why does it signal seniority?
- Restate the senior bar in one sentence.

**Next →** [Scoping Doc to Production in Two Weeks](03_Scoping_To_Production_In_Two_Weeks.md)
