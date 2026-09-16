# Never Stops Learning and Growing - Answer Key

Spoken answers - 3 grounded, 1 partly grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. Something you had to learn from scratch

**GROUNDED — multi-agent orchestration, and rebuilding on a second platform to learn its gaps**

*"Multi-agent orchestration — Supervisor and Deep Agent patterns, LangGraph state machines, memory management across conversations. My background is data platforms and large-scale pipelines `[FILL: Barclays, ~700M events/day]`; two years ago none of the agentic patterns I now use daily existed in a form I'd trust in production.*

*I learned it the way I learn anything: by building something that could fail. At AIA that meant learning the hard way that a single agent with 20-plus tools collapses, and then learning why — context bloat degrading tool selection — well enough to predict the same failure one level up and pre-empt it at Bajaj with a triage layer before the agent ever runs.*

*The second piece I deliberately learned was platform-specific governance. I rebuilt the same enterprise RAG system on a second platform specifically to find out where its guarantees didn't travel — and found that a Vector Search index is a derived copy that doesn't inherit Unity Catalog's row filters. I couldn't have led a customer's security review without having found that myself. Next on the list: AST-based code graphs for root-cause analysis, which is where the Bajaj Code Agent needs to go."*

## 2. Feedback that changed how you lead

**PARTLY GROUNDED — "bring compliance into the first round of discovery" is listed in your AIA material as a lesson; frame it as feedback only if it actually came from a stakeholder.** `[FILL: who said it, and how]`

*"At AIA I ran discovery as two separate conversations — users first, then compliance, legal, and security as a follow-up pass. `[FILL: who gave the feedback — e.g., the compliance lead]` told me, fairly bluntly, that being brought in second meant they were reacting to a design rather than shaping it, and that some of the access rules I'd derived from user interviews had to be reworked once they weighed in.*

*They were right. The access matrix was correct in the end, but it cost a cycle I didn't need to spend. The change I made is simple and permanent: governance stakeholders are in the first round of discovery, in the same week as users, not a separate pass afterward. It's slower on day one and faster on every day after — and it's the reason I now treat 'agree the success bar with compliance before the build' as a non-negotiable rather than a nice-to-have.*

*`[FILL: one line on a later engagement where you applied it].`"*

## 3. A belief about building AI you changed

**GROUNDED — prompt-based security → hard rules; one big agent → specialists**

*"Two. I used to think you could make an AI system safe by prompting it well — tell the model what it's allowed to reveal and trust it to refuse. I don't believe that anymore. On the enterprise RAG work I found a test that passed or failed almost at random because the model's judgment was inside a security decision. Now access control is structural: the model never sees a document it isn't allowed to see, and leak/no-leak is a hard rule. The model gets to decide tone, never access.*

*The second: I assumed a capable model with more tools is a more capable agent. AIA proved the opposite — twenty-plus tools in one context made the agent worse at choosing any of them. I now design for specialisation from the start, small context per agent, and I pre-narrow the toolset before the agent runs, as at Bajaj.*

*Both changes came from my own systems failing in testing. That's the only kind of evidence that actually changes my mind."*

## 4. Staying current in a fast-moving field

**GROUNDED — reference builds, rebuilding on a second platform**

*"I build things that can fail. Reading about a pattern tells me it exists; building it tells me where it breaks. I built a full enterprise RAG platform with attribute-based access control and a golden-set harness, then rebuilt it on a second platform specifically to find where the guarantees didn't travel — and found the Vector Search / Unity Catalog governance gap that way. I built a deterministic guardrail engine with no LLM in it, on purpose, to prove idempotency and crash-recovery properties with exact tests rather than model non-determinism.*

*And I keep a 'next' list driven by the limits of what I've shipped: AST-based code graphs for the Bajaj Code Agent, because single-file lookup is its clearest limitation. Learning that's anchored to a real system's edges sticks. Learning from a feed doesn't."*
