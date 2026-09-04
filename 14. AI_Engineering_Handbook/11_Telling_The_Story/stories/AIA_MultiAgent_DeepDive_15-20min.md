> **Level** 🔴 Telling the Story · **Module** 11 · **stories/** · **Format:** 15–20 minute deep-dive
> **Source material:** `4. FDE_Related_Preparation/Star_Stories/AIA_MultiAgent_DeepDive_15-20min.md` — kept as a worked example of the format described in [Deep-Dive and Conversational Formats](../01_Deep_Dive_And_Conversational_Formats.md). It is one engineer's own engagement narrative; use it as a template for the shape, not a script to repeat.

---

# AIA Group — Governed Multi-Agent Data Assistant — 15–20 Minute Deep-Dive
### For: MongoDB Director conversation · The headline AIA engagement itself · Goal: demonstrate end-to-end field-engineer ownership — architecture, two real pivots, governance, delivery

> **How to use this document:** same speakable-script format as the Enterprise RAG deep-dive — read segment headers and bold cues, don't memorize verbatim. This is the **umbrella engagement** that the RAG-governance deep-dive zooms into; use this one when the room wants the whole system story, and the RAG one when they want to go deep on one specialist agent's access-control layer.

> **The one meta-rule:** every technical term gets translated in the same breath it's introduced. This story's natural hook is honesty about failure — the single-agent approach breaking down live is a stronger opening than a system that worked on the first try.

---

## Timing budget

| Segment | Time | Cumulative |
|---|---|---|
| 1. The Hook | 0:30 | 0:30 |
| 2. Situation & Task | 1:30 | 2:00 |
| 3. Action — Pivot 1: single agent → Supervisor | 3:00 | 5:00 |
| 4. Action — The governance foundation underneath | 2:00 | 7:00 |
| 5. Action — Pivot 2: Supervisor → Deep Agent | 2:00 | 9:00 |
| 6. Governance & Security | 2:30 | 11:30 |
| 7. Result | 1:00 | 12:30 |
| 8. Deployment & Platform Reality | 1:00 | 13:30 |
| 9. Honest Limitations | 0:45 | 14:15 |
| 10. Close → FDE Role | 0:45 | 15:00 |
| Q&A buffer | 5:00 | 20:00 |

---

## 1. The Hook (0:30)

> **Coaching note:** lead with the failure, not the success. It's more credible and it's a better story.

*"I want to tell you about a system I built that failed in production testing, on purpose in the sense that I let it — because the failure is what taught me the architecture that actually worked. At AIA, Asia's largest listed life insurer, I built a multi-agent data assistant, and my first version — one agent, one giant prompt, twenty-plus tools — broke down live. What I want to walk you through is the two real pivots that followed, and why 'specialize early, keep context small' became a rule I've carried into every agentic system since."*

---

## 2. Situation & Task (1:30)

*"AIA's business users — actuaries, claims managers, analysts — needed natural-language answers over governed enterprise data spanning multiple business units and markets, and there was no self-serve path. An ad-hoc question took 2 to 10 business days routed through a BI and analyst queue. A new dashboard took roughly 4 weeks end to end — business question, into a queue, SQL or ML coding, dashboard build, review, delivery.*

*I led this engagement end to end as the field engineer on the account — architecture, hands-on build, and delivery — inside an 8-to-9-week advisory-plus-build engagement. The scope was deliberately bounded to governed data domains, not open-ended enterprise search, because 'answer anything about anything' is not a scope you can make provably safe."*

---

## 3. Action — Pivot 1: single agent → Supervisor (3:00)

**The failure, plainly (1:00)**
*"I started with the obvious first design: one agent, one system prompt, twenty-plus tools, full conversation history. In real testing it broke down fast — the model kept picking the wrong tool because nothing was specialized by domain, and stuffing that many tool schemas into context degraded its accuracy generally, not just on tool choice. That's not 'it got confused' — it's a measurable effect of context bloat on a model's decision quality."*

**The pivot (1:30)**
*"So I re-architected, live, mid-engagement, into a Supervisor pattern: an 8-node LangGraph state machine that classifies the user's intent with a confidence score, asks a clarifying question when confidence drops below 60% instead of guessing, and then routes to one of four specialist workers — a Genie agent for text-to-SQL BI questions, a Multi-Tool agent combining generated SQL with retrieval over policy documents, a Data Analysis agent doing anomaly detection and trend statistics, and a Visualization agent that publishes real dashboards via the platform's dashboard API and hands back a clickable link."*

**Why that's the right shape, not just a workaround (0:30)**
*"Each worker has one job and a narrow toolset, so the tool-selection problem that broke the single-agent version mostly disappears — a specialist choosing between 2-3 tools in its own domain is a much easier decision than one generalist choosing between twenty."*

---

## 4. Action — The governance foundation underneath (2:00)

*"Underneath the agents, I built the actual data foundation: bronze tables for the raw domains — products, agents, customers, policies, claims, policy documents — silver enrichment joins, and seven governed gold-layer metric views that the agents queried instead of ever touching raw tables directly. That matters for a business audience: every number an agent surfaces traces back to a governed, reviewed metric definition, not an ad-hoc query someone wrote on the fly.*

*I also built a Context Index — 16 indexed assets covering the governed data sources, metric views, tables, and document indexes — as a single semantic-discovery tool the Supervisor calls once per question, with endorsed assets prioritized in routing. That's what stops two worker agents from silently working off different, inconsistent views of 'the same' data — the resolution happens once, centrally, and every worker sees the same resolved assets through shared state."*

---

## 5. Action — Pivot 2: Supervisor → Deep Agent (2:00)

*"As the number of specialist domains grew, the Supervisor's own tool list started re-approaching the exact bloat problem that broke the original single-agent design — just one level up. So I pivoted again, into a Deep Agent pattern I named Synaptic Command: a central orchestrator that delegates to fully self-contained subagents, each with its own prompt, its own small toolset, and its own context window, instead of one supervisor juggling an ever-growing list.*

*I split the four analytics domains into dedicated subagents — customer analytics, distribution channels, policy and underwriting, claims analytics — each wired to its own dedicated data assets, plus a memory-manager subagent handling long-term, cross-conversation memory in a categorized store — preference, fact, decision, project, feedback — that the orchestrator checks and updates on every single turn. The lesson from pivot one didn't just apply once; the same failure mode reappears at a higher level as a system scales, and the fix is the same instinct applied again: specialize, and keep each unit's context small."*

---

## 6. Governance & Security (2:30)

> **Coaching note:** weight this heavily for an enterprise-buyer audience — this is where the story stops being "cool agent architecture" and becomes "safe to run at a regulated insurer."

*"A few things I built specifically because this is a regulated financial-services environment, not a demo. Every node in the pipeline is instrumented with tracing, so a wrong answer can be traced back to the exact node and tool call that produced it — that's not optional in an environment where a business user might act on a claims or policy number. I put an AI Gateway in front of the serving endpoint for rate limiting, PII filtering, and guardrails, so the raw model endpoint is never exposed directly to agent traffic. Prompts themselves live in a governed table with a base-plus-overlay structure and a short cache, so I could tune agent behavior without a redeploy — which matters when a business stakeholder asks for a small behavior change and you don't want that to be a full release cycle. And accuracy validation runs against a held-out evaluation dataset with per-node tracing, so an incorrect answer is diagnosable, not just something you notice and can't explain."*

---

## 7. Result (1:00)

*"Time-to-insight dropped from 2-to-10 business days to minutes. Dashboard delivery moved from a roughly 4-week queued process to fast, governed self-serve. We saw about 35% year-to-date growth in platform consumption following rollout. And the whole thing — architected, built, and shipped hands-on — landed as a working, production-grade MVP in 8 to 9 weeks, giving every AIA business user a governed, explainable, self-serve AI data agent across business units and markets, with full traceability back to source on every answer."*

---

## 8. Deployment & Platform Reality (1:00)

*"One real platform constraint shaped the design directly: the platform's own Multi-Agent Supervisor feature wasn't GA yet in AIA's Azure region at the time. Rather than depend on a Beta, region-limited feature for the core path of a production system, I built the Supervisor logic myself in LangGraph on generally-available primitives — the agent framework, model serving, the BI/query layer, vector search, the governed metric views, and tracing. That's a deliberate FDE instinct: design around the platform constraints you actually have in front of you, in this customer's specific region and tier, rather than the roadmap you wish you had."*

---

## 9. Honest Limitations (0:45)

*"I'll be direct about one thing I can't fully claim: the 35% year-to-date consumption growth is a strong correlated signal following rollout, not a controlled experiment — I didn't run an A/B test against a counterfactual. I'd say that plainly if pushed rather than overstate causation I can't prove."*

---

## 10. Close — Tying Back to the FDE Role (0:45)

*"What I take from this engagement isn't really the architecture — it's that both real pivots came from the same root cause showing up at two different scales: an agent, or an orchestrator, given too much undifferentiated responsibility degrades. Recognizing that pattern early, and being willing to re-architect live mid-engagement rather than defend a design that was visibly failing in testing, is the actual muscle an FDE needs — the willingness to be wrong fast and fix it in front of the customer, not after."*

---

## Appendix A — Anticipated Follow-Ups (crib sheet, adapted from source material)

| If asked... | Lead with (business) | Then, if pushed (technical) |
|---|---|---|
| "Walk me through why the single-agent approach failed." | "Too much responsibility in one place — it started picking the wrong tool and losing accuracy generally." | The prompt plus 20+ tool schemas in context degraded tool-selection accuracy and blew out the effective context window — a measurable model-quality effect, not vague confusion. |
| "How does the Supervisor decide which agent to call?" | "It classifies intent, and asks for clarification when it's not confident rather than guessing." | Intent classification with a confidence score; below 60% triggers a clarification turn (e.g., "show me the numbers" → "which numbers — claims, policies, agents, or customers?"). |
| "What stopped two worker agents from seeing different data for the same question?" | "One shared lookup, not four separate guesses." | Context Index resolution happens once, centrally, at the Supervisor; results are shared via graph state so every worker sees the same resolved assets. |
| "Why move to the Deep Agent pattern if the Supervisor was already working?" | "The same failure mode reappeared one level up as domains grew." | The Supervisor's own tool list started re-approaching the original bloat problem; splitting into self-contained subagents with their own context windows removed that ceiling. |
| "How did you validate accuracy?" | "Held-out evaluation, plus full traceability back to the exact step that produced an answer." | Agent evaluation against a held-out eval dataset, with per-node tracing so a wrong answer traces to the exact node/tool call. |
| "What was the regional constraint, and how did it change your design?" | "I designed around AIA's actual platform, not the roadmap." | The platform's Multi-Agent Supervisor wasn't GA in AIA's Azure region, so the Supervisor was hand-built on GA primitives rather than a Beta regional feature. |
| "How do you know the 35% growth was caused by this, not something else?" | "It's a strong correlated signal, and I'd say so plainly." | YTD consumption growth correlated with rollout — not a controlled experiment; be upfront about the attribution limit if pressed. |

## Appendix B — Delivery Notes

- **Open with the failure**, not the eventual success — it's a stronger, more credible hook than "I built a system that worked."
- **Watch for a "why not just use [platform feature]" question** — that's your cue for Section 8 (the GA/regional constraint), which shows platform judgment rather than just engineering output.
- **Never soften the 35% growth caveat** — state it as a fact you're proud to know precisely, not a confession.
- **If time is short**, compress Section 4 (governance foundation) to one sentence — Sections 3, 5, 6, and 9 are what a director will remember.
