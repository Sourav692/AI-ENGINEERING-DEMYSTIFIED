# Makes Good Decisions Quickly - Answer Key

Spoken answers - 4 grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. A fast decision with incomplete information

**GROUNDED — AIA live pivot from single agent to Supervisor**

*"Mid-engagement at AIA, in real testing, my first architecture — one agent, one prompt, twenty-plus tools — was picking the wrong tool and degrading under context bloat. I was weeks into an 8-to-9-week window. I didn't have time to run a controlled study of alternative architectures.*

*The decision was to re-architect live into a Supervisor pattern with specialist agents. What I knew: the failure mechanism was specific — stuffing 20-plus tool schemas plus history into one context measurably degrades tool selection — so specialization would address the cause, not just the symptom. What I didn't know: whether four specialists was the right number, or whether routing would introduce its own errors.*

*I bounded the risk three ways. I kept every existing tool and data asset and changed only the orchestration on top, so the pivot was reversible. I added a confidence gate — below 60%, the Supervisor asks a clarifying question instead of guessing — so a routing mistake becomes a question to the user rather than a wrong answer. And I put per-node MLflow tracing and a held-out eval set in place so I'd know within days whether it worked, not at the end. It did, and we shipped on time."*

## 2. An irreversible, high-stakes decision

**GROUNDED — Bajaj production writes vs. Meridian retrieval-strategy choice**

*"I treat these two very differently, and I have a clean example of each.*

*Routine, reversible: which retrieval strategy to ship in the RAG platform. I benchmarked six against one golden set, picked the cheapest one that met the bar, and documented when to revisit — at a larger corpus the answer might flip. That's a decision you make with data and can undo in an afternoon.*

*High-stakes, hard to reverse: at Bajaj Finserv, whether the agent could write to production master tables on a live lending pipeline. A bad `update_master_table` call misroutes real loan leads at a regulated NBFC — you don't get to un-send those. So the process changed. I went through 182 historical tickets first to understand the real shape of the problem instead of assuming. I scoped every tool to a single, narrow, named operation rather than open write access. I kept a human in the loop: every action lands in the DevOps ticket as a finding for an engineer to confirm. And I built a separate Code Agent for logic bugs rather than letting the ops agent reason over source code it wasn't shown.*

*The pattern: for reversible calls, decide fast and measure. For irreversible ones, slow down at the blast radius, not the whole project — the triage and RAG layers still shipped quickly."*

## 3. A decision you got wrong

**GROUNDED — AIA single-agent v1 (and the retrieval preference)**

*"The single-agent design at AIA. I chose it because it was fastest to stand up in an 8-to-9-week window — one prompt, twenty-plus tools, full history. It was wrong, and I found out the right way: in real testing, not in front of the customer. The agent picked the wrong tool repeatedly and accuracy degraded as context grew.*

*What I did: diagnosed the mechanism rather than patching symptoms — context bloat degrading tool selection — then re-architected into specialists with a Supervisor, keeping all the tools and data so the change was bounded, and added tracing so I'd know quickly if I was wrong again. Later the same mechanism showed up in the Supervisor as domains grew, and because I understood it, I saw it coming and moved to the Deep Agent pattern before it broke.*

*A smaller one: I expected the sophisticated retrieval strategy to win the RAG benchmark. It didn't, at that corpus size, and I shipped the simpler one. Being wrong is cheap when you've built the thing that tells you. It's expensive when the customer tells you."*

## 4. Deciding when to stop analysing and act

**GROUNDED — AIA pivot vs Bajaj 182-ticket analysis**

*"It depends on whether the decision is reversible, and on whether more analysis would actually change it.*

*At AIA, when version one broke mid-engagement, I pivoted within days. More analysis wouldn't have helped — the mechanism was clear, the fix was bounded because I kept every tool and asset, and tracing would tell me fast if it failed. Waiting had a cost measured in a shrinking delivery window.*

*At Bajaj, before writing any code, I spent time going through 182 historical tickets. That analysis was worth it because it changed the architecture entirely — from one bot to three routes plus a Code Agent — and because the agent would touch production config on a lending pipeline, where being wrong is expensive.*

*The heuristic: if the decision is reversible and instrumented, act and measure. If it's irreversible or the analysis would change the shape of what you build, do the analysis — but time-box it against the delivery window."*
