# Story Bank

You don't need 87 stories for 87 behavioural questions. The same handful of real moments answers almost all of them. This page cuts those moments into sixteen stories, one moment each, and lists every question each story can honestly answer.

How to use it: learn every one-liner cold first, then the full version out loud, in about two minutes. In the room, work out what the question is really testing — a failure, a hard no, ownership, influence — and pick the story whose "What it proves" line matches. One story can answer many questions. It just gets told from a different angle each time.

The honesty rule runs through all of it. State limits plainly and never claim a number you can't prove. Where a story is partly grounded, it tells you what you have to supply yourself. Never say a gap out loud as if it were filled.

These are the author's own stories, anonymised, as worked examples: a large Asian life insurer, a large Indian consumer lender, the Meridian Assist reference build. They aren't yours to tell. The last two sections list the questions that need a story of your own, and show you how to build your own bank the same way.

## The insurer: two conversations in discovery

**Engagement:** A large Asian life insurer, a hands-on build of about two months. **Grounding:** PARTLY GROUNDED — the discovery is real; you supply who, if anyone, told you to bring compliance in sooner, and one concrete cross-region friction.

**Say it in one line:** "The brief said natural-language answers over data, but talking to the users and to compliance separately showed me that access control was the real job."

- **Situation:** The brief was one sentence: business users need natural-language answers over governed data. It didn't say which users, which data, or what a wrong answer would cost.
- **Task:** Find the real requirements before designing anything.
- **Action:** I sat with the actuaries, claims managers and analysts, and separately with compliance, legal and security. The users told me the same question needs a different correct answer depending on role and market, and compliance told me which document types carried health disclosures. That became a role-by-document-type-by-market access matrix, a two-layer enforcement path, and a zero-leak release gate agreed with compliance before the build started.
- **Result:** Access control moved from a checkbox to the core of the design, and I narrowed the first build to two business units in one market. The lesson I carry: bring compliance into the first round of discovery, not a second pass. It cost me a cycle.

**What it proves:** discovery before design, listening to the people who do the work and the people who sign it off, turning a vague ask into concrete rules, learning from my own sequencing

**Answers:** [Ambiguity and Discovery · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/ambiguity-and-discovery#section-1), [Ambiguity and Discovery · Q2](/modules/14-behavioural-and-leadership-round/hiring-manager/ambiguity-and-discovery#section-2), [Ambiguity and Discovery · Q3](/modules/14-behavioural-and-leadership-round/hiring-manager/ambiguity-and-discovery#section-3), [Customer Obsession · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/customer-obsession#section-2), [Customer Obsession · Q5](/modules/14-behavioural-and-leadership-round/leadership-principles/customer-obsession#section-5), [Never Stops Learning and Growing · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/never-stops-learning-and-growing#section-2), [Staff-Level and Cross-Cutting · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-3), [Staff-Level and Cross-Cutting · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-4)

## The insurer: starting narrow when the sponsor wanted wide

**Engagement:** A large Asian life insurer. **Grounding:** PARTLY GROUNDED — you supply who pushed for the wider launch, how the sponsor responded, and who was on your team.

**Say it in one line:** "The sponsor wanted every business unit and every market at once; I argued for proving it on two units in one market first, and I framed it as their risk, not my convenience."

- **Situation:** The instinct was to launch wide: every business unit, every market, every document type, plus open-ended enterprise search on top of the BI use case. We had about two months.
- **Task:** Protect the outcome without sounding like I was offering less.
- **Action:** I disagreed early and made it about their exposure: access-control mistakes compound if you scale before you've proven the model, and a leak at launch is the kind of failure that ends an AI programme at an insurer. I agreed the success bar with the sponsor up front — self-serve, governed answers replacing a BI queue that took days, with zero leaks, explainability and acceptable latency — and every new request went on a written expansion path with a precondition: once the zero-leak gate holds on the first slice. Compliance was in the room, and they were the strongest voice for the narrow start.
- **Result:** The MVP shipped on that slice, time-to-insight went from days to minutes on it, and the expansion conversation happened on the back of a result rather than a promise. The customer heard "next", not "no".

**What it proves:** disagreeing with a customer without losing them, framing risk in the customer's terms, scope discipline on a fixed window, focus on the one outcome that matters

**Answers:** [Stakeholder Influence · Q2](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-2), [Pushback and Saying No · Q2](/modules/14-behavioural-and-leadership-round/hiring-manager/pushback-and-saying-no#section-2), [Customer Obsession · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/customer-obsession#section-3), [Ownership · Q6](/modules/14-behavioural-and-leadership-round/leadership-principles/ownership#section-6), [Focuses on Outcomes · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/focuses-on-outcomes#section-1), [Focuses on Outcomes · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/focuses-on-outcomes#section-2), [Engenders Trust · Q5](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-5), [Staff-Level and Cross-Cutting · Q10](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-10)

## The insurer: one agent to a supervisor

**Engagement:** A large Asian life insurer. **Grounding:** GROUNDED.

**Say it in one line:** "Weeks into a two-month build my first architecture broke in testing; I told the sponsor the same day with the mechanism and the fix, re-architected live, and we still shipped on time."

- **Situation:** My first design was one agent, one prompt, twenty-plus tools. It worked in demos. In real testing it kept picking the wrong tool, and accuracy dropped as the context grew.
- **Task:** Fix it inside a shrinking window without losing the sponsor's confidence.
- **Action:** I told the sponsor the same day, in three parts: what's broken, the exact mechanism — twenty tool schemas plus history in one prompt measurably hurts tool selection — and the fix with its cost. Tracing showed it was a structure problem, not a tuning problem, so I moved to a Supervisor with four specialist agents, kept every existing tool and data asset so the change was bounded, added a confidence gate that asks a clarifying question below 60%, and put per-node tracing and a held-out eval set in place so I'd know within days if I was wrong again.
- **Result:** It worked, and we shipped on time. What the sponsor remembered was that they heard it from me first, with a plan.

**What it proves:** calm when my own design fails, bad news delivered early and with the mechanism, deciding fast with incomplete information, changing course when the structure is the problem

**Answers:** [Delivery Under Pressure · Q2](/modules/14-behavioural-and-leadership-round/hiring-manager/delivery-under-pressure#section-2), [Customer Obsession · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/customer-obsession#section-4), [Ownership · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/ownership#section-4), [Sets High Standards · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/sets-high-standards#section-2), [Makes Good Decisions Quickly · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/makes-good-decisions-quickly#section-1), [Makes Good Decisions Quickly · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/makes-good-decisions-quickly#section-3), [Makes Good Decisions Quickly · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/makes-good-decisions-quickly#section-4), [Engenders Trust · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-1), [Embraces Adversity · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/embraces-adversity#section-1), [Embraces Adversity · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/embraces-adversity#section-2), [Embraces Adversity · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/embraces-adversity#section-3), [Never Stops Learning and Growing · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/never-stops-learning-and-growing#section-1), [Never Stops Learning and Growing · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/never-stops-learning-and-growing#section-3), [Staff-Level and Cross-Cutting · Q7](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-7), [Staff-Level and Cross-Cutting · Q12](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-12)

## The insurer: seeing the next ceiling coming

**Engagement:** A large Asian life insurer. **Grounding:** GROUNDED.

**Say it in one line:** "The Supervisor worked, but I could see the same bloat coming back one level up, so I shipped on time, kept the path open, and moved to a Deep Agent before it broke."

- **Situation:** Partway through, the Supervisor was working: four specialists, confidence-gated routing. But as domains grew, its own tool list would drift back towards the context bloat that killed version one.
- **Task:** Hit the deadline without locking in a known ceiling.
- **Action:** I shipped the Supervisor on time and made two choices that kept the long-term path open: prompts lived in a governed table with a five-minute cache, so behaviour could be tuned without a redeploy, and a central Context Index meant the specialists were already loosely coupled. Once domain growth made the ceiling real, I evolved it into a Deep Agent: a central orchestrator handing work to self-contained subagents, each with its own prompt, tools and context window, plus a memory-manager subagent for long-term memory across conversations.
- **Result:** The customer got days-to-minutes time-to-insight on schedule. I moved before the Supervisor broke, not after, because I recognised the mechanism. That removed the ceiling instead of postponing it.

**What it proves:** delivering short-term without closing off the long-term, learning a mechanism from my own failure, refactoring when the pressure is real rather than speculative, innovation as finding the ceiling first

**Answers:** [Ownership · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/ownership#section-3), [Embraces Adversity · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/embraces-adversity#section-3), [Staff-Level and Cross-Cutting · Q8](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-8)

## The insurer: hand-building the supervisor

**Engagement:** A large Asian life insurer. **Grounding:** PARTLY GROUNDED — the build and the result are real; for the product-feedback questions you supply who you shared it with and what came of it.

**Say it in one line:** "The platform's managed multi-agent feature wasn't an option for this customer at the time, so I hand-built the supervisor rather than hand their launch to a roadmap nobody in the room controlled."

- **Situation:** I had about two months to replace a BI queue where an ad-hoc question took days and a dashboard took weeks, with no large delivery team behind me. The managed multi-agent feature was exactly the pattern I needed, and the flattering thing for me to demo, but it wasn't an option for this customer at the time.
- **Task:** Ship a production-grade MVP whose core path didn't depend on a timeline neither of us controlled.
- **Action:** I used managed services wherever they were good enough — a managed text-to-SQL service for the BI specialist, because its SQL is always read-only and the insurer's own analysts could curate it — and built only where there was a gap. The Supervisor became an 8-node LangGraph state machine: classify intent with a confidence score, ask a clarifying question below 60%, resolve governed assets once through a central Context Index, route to one of four specialists, compose the answer. To the sponsor I put it in their terms: "If that feature slips, your launch slips. I'd rather own more code than hand your timeline to a roadmap."
- **Result:** The MVP shipped in the window. Time-to-insight went from days to minutes, and dashboards went from weeks in a queue to self-serve. Adoption grew after rollout, and every time I report that, I say it's a correlated signal, not a controlled experiment.

**What it proves:** build-versus-buy judgement, the company's real interest over my own profile, resourcefulness with a small team, honest attribution, explaining a risk to an executive in their terms

**Answers:** [Stakeholder Influence · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-1), [Stakeholder Influence · Q3](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-3), [Pushback and Saying No · Q3](/modules/14-behavioural-and-leadership-round/hiring-manager/pushback-and-saying-no#section-3), [Scale Beyond Self · Q4](/modules/14-behavioural-and-leadership-round/hiring-manager/scale-beyond-self#section-4), [Ownership · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/ownership#section-1), [Ownership · Q5](/modules/14-behavioural-and-leadership-round/leadership-principles/ownership#section-5), [Communicates with Clarity · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/communicates-with-clarity#section-3), [Focuses on Outcomes · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/focuses-on-outcomes#section-3), [Resourceful · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/resourceful#section-1), [Resourceful · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/resourceful#section-2), [Resourceful · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/resourceful#section-3), [Engenders Trust · Q5](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-5), [Staff-Level and Cross-Cutting · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-4), [Staff-Level and Cross-Cutting · Q11](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-11), [Staff-Level and Cross-Cutting · Q12](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-12)

## The insurer: building the data foundation nobody owned

**Engagement:** A large Asian life insurer. **Grounding:** PARTLY GROUNDED — the build is real; you supply who on the data team was wary and the concrete sign that they came round.

**Say it in one line:** "The data layer was on paper someone else's problem, but agents can't be governed if the data isn't, so I built it myself, with the customer's data team rather than around them."

- **Situation:** The engagement was scoped to the agent layer. The data foundation the agents would query was, on paper, someone else's job, and the BI and data team whose queue I was replacing had every reason to be wary of me.
- **Task:** Make every answer traceable to governed data, inside about two months.
- **Action:** I built the foundation myself, inside their governed catalogue: bronze tables for products, agents, customers, policies, claims and policy documents; silver enrichment joins; and a handful of reviewed, governed metric views on top. The agents query those views, never raw tables, and the assets the data team had reviewed and endorsed were prioritised in the Context Index routing, so their governance decisions were literally what the agents obeyed.
- **Result:** Every number traces back to governed data, which is the property the customer actually needed. The system didn't replace the data team; it made their governed data the thing every business user finally reached. The honest flip side: doing it myself was right here, but it's also the fastest way to become the bottleneck.

**What it proves:** ownership outside my lane, influence without authority, ramping up on a domain by building in it, winning over a sceptical team, knowing the cost of my own habits

**Answers:** [Stakeholder Influence · Q3](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-3), [Stakeholder Influence · Q4](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-4), [Ownership · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/ownership#section-2), [Communicates with Clarity · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/communicates-with-clarity#section-4), [Resourceful · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/resourceful#section-1), [Engenders Trust · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-2), [Staff-Level and Cross-Cutting · Q5](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-5), [Staff-Level and Cross-Cutting · Q13](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-13)

## The insurer: two checkpoints, in plain words

**Engagement:** A large Asian life insurer, later rebuilt as a reference system. **Grounding:** GROUNDED.

**Say it in one line:** "The vector index didn't inherit the source's row-level rules, so I built two checkpoints — a fast one at the door and a careful one right before generation — and explained it to compliance without a word of jargon."

- **Situation:** Compliance, legal, security and a business sponsor, none of them engineers, had to sign off on how the retrieval agent enforced access over policy and claims documents with health disclosures. And the platform's vector index is a derived copy: a revoked grant at the source doesn't reach it.
- **Task:** Build access control that can't go quietly stale, and explain it so non-engineers could reason about it.
- **Action:** The constraint defined the design: a metadata pre-filter compiled into the vector query for speed, then a live re-check against the source grants right before generation for correctness. I explained it as two checkpoints: a fast one at the door that gets you to the right neighbourhood for your role and market, and a careful one right before you're handed anything, because your permissions might have changed in between. Later I rebuilt the pattern as a standalone reference, including a version on a second platform, to document the gap for anyone putting AI on governed data.
- **Result:** Compliance could reason about it and asked the right follow-ups, like "what happens if the second check catches something?" The answer: it's logged as a security event, not swallowed. The technical version came later, for the engineers, and it was the same story with the nouns swapped.

**What it proves:** clear communication to a non-technical audience, turning a platform constraint into a design, naming what the platform isn't good for, learning by building

**Answers:** [Stakeholder Influence · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-1), [Stakeholder Influence · Q4](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-4), [Ownership · Q5](/modules/14-behavioural-and-leadership-round/leadership-principles/ownership#section-5), [Communicates with Clarity · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/communicates-with-clarity#section-1), [Resourceful · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/resourceful#section-2), [Never Stops Learning and Growing · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/never-stops-learning-and-growing#section-1), [Never Stops Learning and Growing · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/never-stops-learning-and-growing#section-4)

## The lender: a couple of hundred tickets, three problems

**Engagement:** A large Indian consumer lender — an agent for the IT-support desk behind their lead-routing pipeline. **Grounding:** GROUNDED.

**Say it in one line:** "The ask was 'automate IT-support tickets'; I read a couple of hundred real tickets before writing any code, found three problems rather than one, and built three routes rather than one bot."

- **Situation:** The lender's lead-routing pipeline sends loan leads into their CRM and dialer. When it misbehaves, an engineer raises a ticket and investigates by hand across logs, control flags and config. I'd never seen their system before.
- **Task:** Work out what the problem really looked like before designing anything.
- **Action:** I went through a couple of hundred historical tickets. More than half were config-table refresh and sync requests, a real slice were log-exclusion investigations, and a small share were bugs in the rules-engine code. So I built a triage layer that narrows the toolset before the agent runs, three investigation routes using retrieval over past tickets rather than a hand-coded rules tree, and a separate code-lookup agent that does a deterministic one-file lookup and hands the model only that file, with four fixed questions.
- **Result:** A working triage-to-root-cause system whose shape came from their data, not my assumption. The same review showed about a third of tickets were clarification round-trips my design didn't handle, and I flagged that as the next gap instead of pretending it was solved. The next step for the code-lookup agent is an AST-based code graph, which I've designed but not shipped.

**What it proves:** letting the customer's data overrule my assumptions, ramping up fast on an unfamiliar system, grounded-by-construction design, being clear about what isn't solved yet

**Answers:** [Ambiguity and Discovery · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/ambiguity-and-discovery#section-1), [Ambiguity and Discovery · Q2](/modules/14-behavioural-and-leadership-round/hiring-manager/ambiguity-and-discovery#section-2), [Ambiguity and Discovery · Q3](/modules/14-behavioural-and-leadership-round/hiring-manager/ambiguity-and-discovery#section-3), [Customer Obsession · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/customer-obsession#section-2), [Customer Obsession · Q5](/modules/14-behavioural-and-leadership-round/leadership-principles/customer-obsession#section-5), [Resourceful · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/resourceful#section-3), [Makes Good Decisions Quickly · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/makes-good-decisions-quickly#section-4), [Engenders Trust · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-3), [Never Stops Learning and Growing · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/never-stops-learning-and-growing#section-4), [Staff-Level and Cross-Cutting · Q5](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-5), [Staff-Level and Cross-Cutting · Q8](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-8)

## The lender: no unreviewed writes to production

**Engagement:** A large Indian consumer lender. **Grounding:** GROUNDED.

**Say it in one line:** "The flashy version let the agent fix config tables on its own; I scoped every tool to one narrow operation, made every action a finding for an engineer to confirm, and told them what that cost."

- **Situation:** The easy version, and honestly the more impressive demo, was full auto-fix: a ticket comes in, the agent diagnoses it, applies the fix to the config table, and the ticket closes. A great headline number.
- **Task:** Decide whether an LLM should write to production config on a live lending pipeline.
- **Action:** A wrong config write misroutes real loan leads at a regulated lender, and you can't un-send those. So I slowed down at the blast radius, not the whole project: every tool was scoped to one narrow, named operation, and every agent action lands in their ticketing system as a finding for an engineer to confirm, never a silent production change. I told them the trade plainly: slower ticket resolution in exchange for zero unreviewed changes, and I recommended the slower path.
- **Result:** They chose it in one conversation, and the triage and retrieval layers still shipped quickly. I'd make the same call again.

**What it proves:** the customer's interest over my own headline metric, judging what can and can't be undone, saying no with a better alternative, explaining risk in the customer's terms

**Answers:** [Stakeholder Influence · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-1), [Pushback and Saying No · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/pushback-and-saying-no#section-1), [Customer Obsession · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/customer-obsession#section-1), [Communicates with Clarity · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/communicates-with-clarity#section-3), [Makes Good Decisions Quickly · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/makes-good-decisions-quickly#section-2), [Staff-Level and Cross-Cutting · Q10](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-10)

## The lender: the metric I couldn't prove

**Engagement:** A large Indian consumer lender. **Grounding:** GROUNDED.

**Say it in one line:** "I shipped a working system, but I can't give you a client-confirmed before-and-after number, because I didn't instrument it from day one, and that's now the first thing I agree on any engagement."

- **Situation:** I committed to compressing ticket resolution time at the lender, and I shipped a working triage-to-root-cause system.
- **Task:** Report the result honestly.
- **Action:** I hadn't instrumented resolution time per ticket type from the start, so there was no clean baseline. I can defend an estimate — roughly half of ticket volume was a strong fit for automation — but I don't quote it as a result. I say plainly that I don't have a client-confirmed number.
- **Result:** The limit stands: there's no proven delta. What changed is how I work. I agree the success metric and instrument it before the first line of code, and the measurement plan is now part of the scoping document.

**What it proves:** honesty about limits, refusing to claim a number I can't prove, owning a shortfall, a lasting change in practice

**Answers:** [Ownership · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/ownership#section-4), [Focuses on Outcomes · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/focuses-on-outcomes#section-3), [Staff-Level and Cross-Cutting · Q11](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-11)

## Meridian: the zero-leak gate

**Engagement:** The Meridian Assist reference build, a 22-document governed RAG system, with the gate first agreed with the insurer's compliance team. **Grounding:** GROUNDED.

**Say it in one line:** "One leak on the governed test set and the build doesn't ship — not a low leak rate, zero — and a security decision is never left to the model's judgement."

- **Situation:** The usual bar for an AI system is a quality score plus "the model refuses nicely". I also had a security test that passed most of the time, and the temptation was to call it flaky and move on.
- **Task:** Set a bar that holds whoever wrote the code, me included.
- **Action:** I agreed the bar with the business sponsor and compliance before the build, so it was the customer's definition of done, not my preference. Then I made it mechanical: an evaluation harness that fails the release on a single leak, and a standalone check that fails if the security documentation drifts from the running policy code. When I dug into the flaky test, I found I'd let the model's judgement sit inside a security pass-or-fail, so I split it: leak or no leak is a hard rule, and tone is a separate check that's allowed to be soft.
- **Result:** The zero-leak property holds and the harness gates every release, and what compliance was told can't silently drift from what's deployed. It also changed a belief of mine: you can't make a system safe by prompting it well. Access control has to be structural.

**What it proves:** setting a high bar and making it mechanical, letting the customer set the standard, refusing "mostly passes" for things that fail silently, earning trust with security and compliance

**Answers:** [Communicates with Clarity · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/communicates-with-clarity#section-4), [Sets High Standards · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/sets-high-standards#section-1), [Sets High Standards · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/sets-high-standards#section-2), [Sets High Standards · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/sets-high-standards#section-3), [Creates a Culture of Accountability · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/creates-a-culture-of-accountability#section-2), [Engenders Trust · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-4), [Never Stops Learning and Growing · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/never-stops-learning-and-growing#section-3), [Staff-Level and Cross-Cutting · Q11](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-11)

## Meridian: the false-alarm leak

**Engagement:** The Meridian Assist reference build. **Grounding:** GROUNDED.

**Say it in one line:** "My own harness flagged a leak; I stopped everything, traced it to stale test data, wrote up the whole thing including my own labelling mistake, and added a check so it can't happen again."

- **Situation:** My evaluation harness flagged a leak: a claims manager was shown a case outside their assignment.
- **Task:** Treat it as real until I'd proven otherwise.
- **Action:** I stopped and traced it before anything else. The manager had just been reassigned that case, so my test data was stale, not the system. I'd also mislabelled my own test data by confusing "not relevant to this question" with "not allowed to see it". I wrote up the alarm, the false alarm and my own mistake, and added a check so those two ideas can't be mixed up again.
- **Result:** The system was fine; the lesson was mine. A false security alarm is worse than none, because people learn to ignore it. I now walk security teams through this story, false alarm included.

**What it proves:** holding myself to my own bar, admitting a mistake in the open, incident discipline — contain, diagnose, communicate, prevent — and trust built through disclosure

**Answers:** [Sets High Standards · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/sets-high-standards#section-1), [Creates a Culture of Accountability · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/creates-a-culture-of-accountability#section-2), [Engenders Trust · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-1), [Engenders Trust · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-4), [Embraces Adversity · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/embraces-adversity#section-2)

## Meridian: 22 out of 22 on 22 documents

**Engagement:** The Meridian Assist reference build. **Grounding:** GROUNDED.

**Say it in one line:** "Every retrieval strategy scored perfectly, including the one I'd bet on, and I wrote down that the table proved the security gate, not which strategy wins at real scale."

- **Situation:** I benchmarked six retrieval strategies, from keyword and dense to hybrid and a decomposition-plus-reranking approach I'd put real effort into and expected to win. Every one scored 22 of 22 on the golden set: recall 1.0, groundedness 1.0, zero leaks.
- **Task:** Decide what to ship, and what the numbers actually proved.
- **Action:** My favourite was simply the slowest and most expensive, so I shipped dense retrieval and said plainly that the sophisticated one hadn't earned its keep. Then I separated the claims. The corpus is 22 documents, so retrieval is easy and the differences are noise. The table proves the zero-leak gate and the testing discipline. It proves nothing about which strategy wins at 200,000 documents.
- **Result:** The limit is written in the docs, along with what would make the bigger claim true: re-run the benchmark at a representative corpus size. Good numbers on the wrong question are the most dangerous kind, because nobody argues with them.

**What it proves:** letting data overrule my own preference, saying no to the impressive option, honest limits on a good-looking result, fast decisions where the call is easy to undo

**Answers:** [Sets High Standards · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/sets-high-standards#section-3), [Focuses on Outcomes · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/focuses-on-outcomes#section-2), [Focuses on Outcomes · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/focuses-on-outcomes#section-4), [Makes Good Decisions Quickly · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/makes-good-decisions-quickly#section-2), [Makes Good Decisions Quickly · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/makes-good-decisions-quickly#section-3), [Engenders Trust · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/engenders-trust#section-3)

## The guardrail engine: shipping the gap in writing

**Engagement:** My agent guardrail-engine reference build, with the same habit at the lender. **Grounding:** GROUNDED.

**Say it in one line:** "I shipped with in-process locks I knew wouldn't survive a restart, because the build proved three properties that didn't depend on them, and I wrote the gap into the coverage map where a reviewer would find it."

- **Situation:** I built a guardrail engine with no LLM in it, on purpose, to prove three properties with exact tests: no destructive action without approval, no double-apply on retry, no re-run after a crash. The entity locks and the idempotency-key store were in-process Python dictionaries.
- **Task:** Decide whether that was good enough to ship.
- **Action:** Those three properties don't depend on where the keys are stored, so I shipped it, and documented in the coverage map that the state doesn't survive a restart or share across workers, with the production path: same key shape, moved to Redis or Postgres. It has 21 deterministic tests, and I can reproduce a $500-refund scenario and show exactly why it paused for a human. Same habit at the lender: the pattern-based triage classifier is brittle to phrasing drift, and I flagged it as the next gap rather than let the demo imply it was solved.
- **Result:** The limit sits where a reviewer will find it, not where a customer will. "We'd add guardrails" became a property I can show, not a slide.

**What it proves:** imperfection that's chosen, bounded and written down, doing right when nobody would notice, proving a claim rather than asserting it, learning by building

**Answers:** [Sets High Standards · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/sets-high-standards#section-3), [Sets High Standards · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/sets-high-standards#section-4), [Never Stops Learning and Growing · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/never-stops-learning-and-growing#section-4), [Staff-Level and Cross-Cutting · Q11](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-11)

## Financial services: red-teaming before saying no

**Engagement:** A financial-services engagement on multi-agent guardrails. **Grounding:** PARTLY GROUNDED — you supply which client, the exact decisioning path they wanted automated, and where the red-team findings went afterwards.

**Say it in one line:** "They wanted agents in a decisioning path with no human in the loop; instead of arguing from principle, I red-teamed it, brought the failures to the table, and offered a version that kept the automation."

- **Situation:** The client wanted agents extended into an automated decisioning path, with no human in the loop.
- **Task:** Decline that scope without losing the account.
- **Action:** I didn't argue from principle. I ran adversarial red-teaming against the deployment with PyRIT and brought the results: concrete cases where the system gave confident, wrong output under adversarial framing. Then I offered the alternative: keep the automation, add a confidence threshold, and escalate to a human above it.
- **Result:** They accepted the constrained design.

**What it proves:** a "no" backed by evidence I generated rather than opinion, always bringing an alternative with the no, keeping the relationship while declining scope

**Answers:** [Pushback and Saying No · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/pushback-and-saying-no#section-1), [Staff-Level and Cross-Cutting · Q10](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-10)

## Beyond one engagement: patterns that travel

**Engagement:** Across my engagements at the platform vendor I worked for. **Grounding:** PARTLY GROUNDED — you supply a reuse count or the effort saved, and who picked the patterns up.

**Say it in one line:** "The same multi-agent scaffolding kept coming back on other accounts, so I turned it into reusable assets and taught the pattern, not the solution."

- **Situation:** The multi-agent patterns from the insurer kept recurring on other accounts, and I was rebuilding the same scaffolding each time.
- **Task:** Stop rebuilding it per engagement, and make myself unnecessary on the accounts.
- **Action:** I generalised the working pieces — the Supervisor–Worker skeleton, tracing conventions, memory tiering, the evaluation harness — into reusable assets, and contributed 40+ scripts to the global codebase. I taught the patterns through partner tech talks to 125+ architects and founded a local practitioner meetup. The specialisation lesson from the insurer became the triage layer I built in at the lender from the start, and an open-source contribution and an internal accelerator both began as gaps between what the product did and what the field needed.
- **Result:** The 40+ scripts and the 125+ architects are real. I don't have a reuse count or an effort-saved number yet, so I don't claim one.

**What it proves:** multiplying other people rather than just executing, teaching the why so others can design the next one, carrying field learning back to the product, impact beyond a single project

**Answers:** [Stakeholder Influence · Q4](/modules/14-behavioural-and-leadership-round/hiring-manager/stakeholder-influence#section-4), [Pushback and Saying No · Q3](/modules/14-behavioural-and-leadership-round/hiring-manager/pushback-and-saying-no#section-3), [Scale Beyond Self · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/scale-beyond-self#section-1), [Scale Beyond Self · Q2](/modules/14-behavioural-and-leadership-round/hiring-manager/scale-beyond-self#section-2), [Scale Beyond Self · Q3](/modules/14-behavioural-and-leadership-round/hiring-manager/scale-beyond-self#section-3), [Scale Beyond Self · Q4](/modules/14-behavioural-and-leadership-round/hiring-manager/scale-beyond-self#section-4), [Staff-Level and Cross-Cutting · Q6](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-6), [Staff-Level and Cross-Cutting · Q7](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-7)

## Questions that need a story of your own

None of the stories above answers these honestly. Most are failure-shaped or about managing people, and a loop that hears only successes scores you as evasive. Find a real moment of your own for each.

- [Ambiguity and Discovery · Q4](/modules/14-behavioural-and-leadership-round/hiring-manager/ambiguity-and-discovery#section-4) — a project you really did mis-scope, told as "I didn't ask X", not "they didn't tell me X". A multi-region migration is a likely home.
- [Delivery Under Pressure · Q1](/modules/14-behavioural-and-leadership-round/hiring-manager/delivery-under-pressure#section-1) — a real incident at a customer site, with the hour, the decision, the recovery time and the lasting fix. A near-miss you name beats a spotless record.
- [Delivery Under Pressure · Q3](/modules/14-behavioural-and-leadership-round/hiring-manager/delivery-under-pressure#section-3) — a deadline that slipped, which you raised early, with options and your own escalation path. Not a weekend rescue.
- [Delivery Under Pressure · Q4](/modules/14-behavioural-and-leadership-round/hiring-manager/delivery-under-pressure#section-4) — a customer who went over your head, where you agreed with part of the complaint and the account recovered.
- [Pushback and Saying No · Q4](/modules/14-behavioural-and-leadership-round/hiring-manager/pushback-and-saying-no#section-4) — an approach you killed after real invested effort, with the evidence and the rebuild cost. The insurer's first-architecture pivot may fit if you can say how much was built and what the rebuild cost.
- [Attracts and Retains Talent · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/attracts-and-retains-talent#section-1) — a hiring loop you changed, ideally towards "prove it, don't assert it".
- [Attracts and Retains Talent · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/attracts-and-retains-talent#section-2) — a strong person at risk of leaving, and what you changed. Usually it's scope or growth, not money.
- [Attracts and Retains Talent · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/attracts-and-retains-talent#section-3) — the real channels you've sourced from, and a debrief where fixed criteria changed the outcome.
- [Communicates with Clarity · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/communicates-with-clarity#section-2) — a handover that carried the task but not the customer's intent, and what you changed in how you write tickets.
- [Develops People · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/develops-people#section-1) — an engineer whose "technical" questions were really unresolved scope, and what changed once you coached the skill.
- [Develops People · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/develops-people#section-2) — someone you gave real blast radius, put in front of a customer, and sponsored, and where they are now.
- [Develops People · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/develops-people#section-3) — a real new joiner you brought up to speed: customer intent first, then the success bar, then design review before code.
- [Develops People · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/develops-people#section-4) — hard feedback to a peer or senior, backed by a trace, a benchmark or ticket data rather than opinion.
- [Creates a Culture of Accountability · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/creates-a-culture-of-accountability#section-1) — a direct conversation about work against an agreed bar. If you've only led as a senior IC, say so, then give the closest real example.
- [Creates a Culture of Accountability · Q3](/modules/14-behavioural-and-leadership-round/leadership-principles/creates-a-culture-of-accountability#section-3) — a commitment you missed and raised before anyone found out. If nothing fits, the lender's unproven metric is the honest adjacent example.
- [Creates a Culture of Accountability · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/creates-a-culture-of-accountability#section-4) — a customer-side dependency that really slipped, and how you showed which work was blocked instead of absorbing it.
- [Embraces Adversity · Q4](/modules/14-behavioural-and-leadership-round/leadership-principles/embraces-adversity#section-4) — harsh criticism you checked for truth before deciding how you felt about it.
- [Staff-Level and Cross-Cutting · Q1](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-1) — a disagreement with a person, not with your own first design, settled with evidence.
- [Staff-Level and Cross-Cutting · Q2](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-2) — work you'd rather have kept and handed over, made safe by a design review before the code existed.
- [Staff-Level and Cross-Cutting · Q9](/modules/14-behavioural-and-leadership-round/leadership-principles/staff-level-and-cross-cutting#section-9) — a real production incident and what you did in the first hour. The false-alarm leak is only an adjacent fallback.

## Build your own story bank

Start with moments, not questions. Here's the method, in the order I'd do it.

1. **Pick 10 to 12 real moments.** A failure, a hard no, a pivot, a number you couldn't prove, something you built that nobody asked you to. Aim for a spread, not your best-ever week.
2. **Cut each one by moment, not by engagement.** One engagement can hold four stories. Each story is one decision, one turn, one result.
3. **Write the one-liner first.** If you can't say it in one sentence, you don't know what the story is yet.
4. **Fill the four beats, short.** Situation and task in two lines. Most of your words go on the action: the mechanism, not the adjectives. Only put proven results in the result, and name the limit.
5. **Tag what it proves.** Three to five plain signals: ownership, calm under a failed launch, deciding with incomplete data.
6. **Map it to questions.** Go through the worksheets and list every question the story honestly answers. Be strict. A story that nearly fits reads worse than a smaller true one.
7. **Check the gaps.** Every principle should have at least one story. Anything with none goes on your "need a story" list, and that list is your homework.
8. **Rehearse out loud.** The one-liner, then the two-minute version, then the same story told for three different questions.

Copy this template for each story:

```
## <Engagement>: <the moment, in a few words>

**Engagement:** <anonymised engagement>. **Grounding:** <GROUNDED, or PARTLY GROUNDED and what you still need to find>

**Say it in one line:** "<the whole story in one spoken sentence>"

- **Situation:** <what was broken, or what was at stake, in one or two sentences>
- **Task:** <what you had to achieve>
- **Action:** <what you did and why it worked: the mechanism, in two or three sentences>
- **Result:** <only what you can prove, and the limit if there is one>

**What it proves:** <three to five signals, in plain words>

**Answers:** <every question this story honestly answers>
```
