> **Level** 🔴 Telling the Story · **Module** 11 · **stories/** · **Format:** open-ended conversational guide
> **Source material:** `4. FDE_Related_Preparation/Star_Stories/AIA_MultiAgent_Conversational_Guide.md` — kept as a worked example of the format described in [Deep-Dive and Conversational Formats](../01_Deep_Dive_And_Conversational_Formats.md). It is one engineer's own engagement narrative; use it as a template for the shape, not a script to repeat.

---

# AIA Group — Governed Multi-Agent Data Assistant — Open-Ended Conversational Guide
### For: MongoDB Director · Format: fluid discussion, not a fixed slot · The headline AIA engagement itself

> **How this differs from the deep-dive version:** that one is a script you move through top to bottom. This is a **toolkit** — self-contained "story beats" (30–60 seconds each) deployed in whatever order the conversation goes, plus bridges and a topic-organized "go deeper" menu. Use this one when the conversation wants the whole engagement; switch to the RAG-governance conversational guide if it narrows to the access-control layer inside the Multi-Tool agent specifically.

---

## The one-sentence cold open

If asked "tell me about a project you led end to end":

*"At AIA, Asia's largest listed life insurer, I built a multi-agent system to replace a 2-to-10-day BI queue with natural-language, self-serve answers — and my first design broke down live in testing, which is actually the more interesting part of the story."*

Then wait. Let their next question tell you which beat to go to.

---

## Core story beats (deploy independently, any order)

### Beat A — The business problem (relatability)
*"Actuaries, claims managers, and analysts at AIA had no self-serve path to their own governed data. An ad-hoc question took 2 to 10 business days through a BI queue; a new dashboard took about 4 weeks end to end. I owned building a governed, self-serve alternative, end to end, in an 8-to-9-week engagement."*

**Bridge to technical:** *"I want to tell you how I actually got there, because the path wasn't a straight line — it had two real pivots."*

### Beat B — Pivot 1: the failure that taught the architecture
*"My first version was one agent, one prompt, twenty-plus tools. It broke down fast in real testing — too much in context, and it kept picking the wrong tool because nothing was specialized. So I re-architected live, mid-engagement, into a Supervisor pattern: an 8-node state machine that classifies intent, asks a clarifying question when it's not confident, and routes to four specialist agents — one for SQL-style BI questions, one combining SQL with document retrieval, one for statistical analysis, one for generating dashboards."*

**If they ask "why did it break down, specifically":** stuffing 20+ tool schemas plus full history into one prompt measurably degrades a model's tool-selection accuracy — it's not vague "confusion," it's a context-bloat effect.

### Beat C — The governance foundation (business-first)
*"Underneath the agents, every number traces back to a governed data foundation — raw tables, enrichment joins, and seven reviewed metric views the agents query instead of touching raw data directly. And every worker agent shares one central lookup for 'what data assets exist' so two agents never silently work off inconsistent views of the same question."*

**Bridge to technical:** *"That central lookup is a Context Index — a semantic-discovery tool the Supervisor calls once per question, with results shared through the pipeline's state."*

### Beat D — Pivot 2: the same failure, one level up
*"As the number of domains grew, the Supervisor itself started re-approaching the exact bloat problem that broke my first design — just one level up the stack. So I pivoted again into a Deep Agent pattern, where a central orchestrator delegates to fully self-contained subagents, each with its own prompt, tools, and context window, plus a dedicated subagent just for managing long-term memory across conversations."*

**Why this beat lands well:** it shows the same diagnostic instinct applied twice, at two different scales — that's a stronger signal than one clever fix.

### Beat E — Governance & security (weight heavily for enterprise)
*"Because this runs at a regulated insurer, not a demo: every step is traced end to end so a wrong answer is diagnosable, not just noticeable. There's a gateway in front of the model endpoint doing rate limiting, PII filtering, and guardrails — the raw endpoint is never exposed directly. And prompts live in a governed table I could tune without a redeploy, which matters when a business stakeholder wants a small behavior change and a full release cycle isn't an acceptable answer."*

### Beat F — The platform-reality insight
*"One design decision came directly from a platform constraint: the platform's own Multi-Agent Supervisor feature wasn't GA yet in AIA's Azure region. Rather than depend on a Beta, region-limited feature for a production system's core path, I built the Supervisor myself on generally-available primitives. That's the instinct I'd bring to any customer's stack — design around what's actually available in their region and tier, not the roadmap you wish you had."*

### Beat G — Result & honest attribution
*"Time-to-insight went from days to minutes, dashboard delivery from weeks to self-serve, and we saw about 35% year-to-date growth in platform usage after rollout — though I'll say plainly that's a strong correlated signal, not a controlled experiment, and I wouldn't overstate the causation there."*

---

## Bridges — moving between business and technical mid-sentence

- *"...which, in plain terms, means..."*
- *"...think of it like [analogy] — technically that's called [term], but the idea is..."*
- *"I can go as deep as you'd like on the how — where should I take this?"*
- *"The business reason I did that is X; the engineering reason is Y."*

---

## The "go deeper" menu — organized by what they might ask about

### If they ask about **why the first design failed, specifically**
- 20+ tool schemas plus full conversation history in one prompt degraded tool-selection accuracy and inflated the effective context window.
- Not "the model got confused" — a measurable effect of undifferentiated responsibility on model quality.

### If they ask about **how routing/orchestration actually works**
- 8-node LangGraph state machine: classify intent (with confidence score) → clarify if below 60% confidence → resolve governed assets → route to one of four specialists → compose the answer.
- Context Index (16 governed assets) resolved once, centrally, shared via graph state — prevents inconsistent views across workers.

### If they ask about **why pivot again to the Deep Agent pattern**
- The Supervisor's own tool list started re-approaching the original bloat problem as domains grew.
- Fix: fully self-contained subagents per domain, each with its own context window, plus a dedicated memory-manager subagent for cross-conversation memory (preference/fact/decision/project/feedback categories).

### If they ask about **governance / security / production-readiness**
- Governed gold-layer metric views — agents never touch raw tables directly.
- AI Gateway in front of the serving endpoint: rate limiting, PII filtering, guardrails.
- Per-node tracing plus held-out evaluation dataset for diagnosable, measurable accuracy.
- Prompts in a governed, cacheable table — tunable without a redeploy.

### If they ask about **platform constraints / working within a customer's actual environment**
- Multi-Agent Supervisor feature wasn't GA in AIA's Azure region — built the Supervisor by hand on GA primitives instead of depending on a Beta regional feature for the core path.
- The general instinct: design around what's actually available for this specific customer, region, and tier.

### If they ask about **results / how you know it worked**
- Time-to-insight: 2–10 days → minutes. Dashboard delivery: ~4 weeks → self-serve. ~35% YTD consumption growth post-rollout — stated as a correlated signal, not a controlled experiment, if pressed.
- 8–9 week MVP, architected/built/shipped hands-on.

---

## Reading the room — quick cues

| Signal | What it means | What to do |
|---|---|---|
| Nodding, staying quiet | They're tracking, want the story to keep moving | Continue at current depth |
| "Why did that break down, exactly?" | Green light to go deeper on Beat B's mechanism | Give the context-bloat explanation directly |
| "How do you know it actually worked?" | They want the result held to scrutiny | Give the metrics, then volunteer the attribution caveat unprompted |
| Redirecting to a different angle | They want a different lens | Drop what you're doing, follow their thread |
| Silence after a technical sentence | Went too deep too fast | Re-anchor in plain English immediately |
| Checking the time / wrapping-up language | Time to close | Go straight to a closing line, skip the menu |

---

## Closing lines (pick based on how the conversation actually ended)

**If it ended on the pivots/architecture thread:**
*"The real lesson for me wasn't the specific architecture — it's that the same failure mode showed up twice, at two different scales, and both times the fix was the same instinct: specialize, and keep each unit's context small. I've carried that into every agentic system I've built since."*

**If it ended on the governance/security thread:**
*"That's the part of the job I think matters most at an enterprise like AIA — building something that's not just accurate, but provably safe to hand to a regulated business user."*

**If it ended on the platform-constraint thread:**
*"That's the instinct I'd bring to any customer's stack — design for the platform and region actually in front of you, not the version of the roadmap you'd prefer."*

**If it ended on results/attribution:**
*"I'd rather tell you exactly what I can and can't claim credit for than let a number like that go unquestioned — that's the more useful signal."*

**Generic fallback, any ending:**
*"Happy to go deeper on any piece — the pivots, the governance layer, the platform constraints, or the results — whichever's most useful to you."*
