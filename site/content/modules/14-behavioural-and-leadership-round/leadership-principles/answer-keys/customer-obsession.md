# Customer Obsession - Answer Key

Spoken answers - 4 grounded, 1 partly grounded. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. Easy for your team versus best for the customer

**GROUNDED — Bajaj Finserv**

*"At Bajaj Finserv, RapidLR is the existing pipeline that routes loan leads into Salesforce and their dialer — I didn't touch that. What I built was an agent for the IT-support desk behind it: when RapidLR misbehaves and an engineer raises a ticket — a lead silently excluded, a feed that stopped, a master table out of sync — the agent runs the investigation an engineer would otherwise do by hand across logs, control flags, and config, and writes up the root cause. The easy version — and honestly the more impressive demo — was to let that agent close the loop itself: ticket comes in, agent diagnoses it, agent applies the fix to the master table, ticket closes. Fast time-to-resolution, great headline number.*

*I didn't build that. Fifty-eight percent of their 182 historical tickets were master-table refresh and sync requests, and a wrong `update_master_table` call on a live lending pipeline misroutes real loan leads at a regulated NBFC. So I scoped every tool to one narrow, named operation, and every agent action lands in the Azure DevOps ticket as a finding for an engineer to confirm — never a silent production change. The cost was real: slower resolution than a full auto-fix, and a less flashy demo. But the customer's actual interest was 'never let an LLM make an unreviewed change to lead-routing config,' not 'close tickets fastest.'*

*I told them that trade-off explicitly rather than hiding it — the slower path was a deliberate choice, and I'd make it again."*

**Why it lands:** you chose the customer's blast radius over your own headline metric, and you named the cost.

## 2. Customer feedback that changed project direction

**GROUNDED — AIA Group (discovery) with Bajaj as a second example**

*"At AIA, the engagement was framed as 'give business users natural-language answers over governed data.' If I'd built to that brief, I'd have built a retrieval and text-to-SQL system and called it done.*

*Before designing anything, I sat with the actual users — actuaries, claims managers, analysts — and separately with compliance, legal, and security. Those two conversations surfaced different things. The users told me the same question needed a different correct answer depending on who was asking: a claims manager handling a case needs something an actuary must never see, and each market had its own regulator and residency rules. Compliance told me which document types carried health disclosures.*

*That feedback moved access control from a checkbox to the core of the design — a role-by-document-type-by-market matrix that became the policy engine's rules, a two-layer enforcement path, and a zero-leak release gate agreed with compliance before the build started. It also changed the scope: I deliberately narrowed the first build to two business units in one market, because access-control mistakes compound if you scale before you've proven the model.*

*The same thing happened at Bajaj: I assumed one problem shape, and 182 real tickets showed three — which is why the system has three investigation routes instead of one agent."*

## 3. Disagreeing with a customer

**PARTLY GROUNDED — AIA scope.** `[FILL: who on the AIA side wanted the wider scope]`

*"At AIA the sponsor's instinct was to launch wide — every business unit, every market, open-ended enterprise search on top of the BI use case. I disagreed, and I said so early rather than quietly under-delivering.*

*My argument wasn't 'that's too hard.' It was about their risk: the retrieval agent would be answering over policy and claims documents with health disclosures, across markets with different regulators. Access-control mistakes compound if you scale before you've proven the model — and a leak at launch is the kind of failure that ends an AI programme at an insurer. So I proposed proving it on two business units in one market first, with a zero-leak gate agreed with compliance, and expanding from a validated base.*

*How I handled it mattered as much as the argument: I framed it as their exposure, not my convenience, offered a concrete expansion path so 'narrow' didn't sound like 'less,' and let compliance be in the room — they were the strongest voice for the narrow start. `[FILL: how the sponsor responded].` The MVP shipped on that slice, and the expansion conversation happened on the back of a result rather than a promise."*

## 4. Delivering bad news to a customer

**GROUNDED — AIA v1 failure**

*"Mid-engagement at AIA, my first architecture — one agent with twenty-plus tools — broke down in real testing. I was weeks into an 8-to-9-week window and the sponsor was expecting a working MVP.*

*I told them the same day, in three parts: what's broken — the agent is picking the wrong tool and degrading under context bloat; why, specifically — stuffing twenty tool schemas plus history into one prompt measurably hurts tool selection, it's not vague 'confusion'; and what I'm doing about it — a Supervisor pattern with specialist agents, keeping every existing tool and data asset so the change is bounded, with tracing so we'll know within days if it works.*

*Two rules I follow for bad news: never deliver a problem without the mechanism, because 'it doesn't work' invites panic and 'here's exactly why' invites trust; and never deliver it without the next step and its cost. The pivot worked and we shipped on time — but the thing the sponsor remembered was that they heard it from me first, with a plan."*

## 5. What they need versus what they ask for

**GROUNDED — AIA two-track discovery + Bajaj 182 tickets**

*"Two habits. First, I don't start from the brief; I start from the people who'll use the thing and the people who'll have to sign off on it, and I talk to them separately — because they surface different requirements. At AIA the brief said 'natural-language answers over data.' The actuaries, claims managers, and analysts told me the same question needed different correct answers per role and market. Compliance told me which documents carried health disclosures. Neither was in the brief, and together they became the core of the design.*

*Second, I look at the customer's own data before I believe the framing. At Bajaj the ask was 'automate IT-support tickets.' I went through 182 real tickets and found it wasn't one problem — 58% were master-table maintenance, a real slice were log-exclusion investigations, and 12% were bugs in the pipeline's C# code. That's three investigation routes and a separate Code Agent, not one bot.*

*The framing is usually right about the pain and wrong about the shape. Discovery is how you find the shape."*
