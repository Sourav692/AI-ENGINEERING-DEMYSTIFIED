# AI Customer-Support Automation - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- Which channels are in scope — chat, email, voice — and what is the monthly volume and peak concurrency?
- Which actions may the system take autonomously, and which require human approval before execution?
- How is the customer authenticated, and which fields such as payment data or PII need extra protection?
- How current must policy articles, order status, and account data be before an answer is unsafe?
- What does a human agent need to see at handoff, and how fast must that handoff happen?
- How many languages at launch, and what happens when language detection fails or returns low confidence?
- Which support categories carry legal, financial, or safety risk and must stay human-reviewed in the first release?
- What is the refund threshold above which approval is mandatory, and who owns that policy?

## Strong functional requirements
- Support the core workflow: classify intent and risk, retrieve grounded policy and account context, draft a response, gate it on policy, then auto-resolve, request approval, or escalate.
- Classify and route every request by intent and risk before any retrieval or drafting begins.
- Retrieve grounded customer and policy context from CRM, order, and policy sources before drafting.
- Execute tools such as refunds, address changes, and subscription actions only through a controlled, authorized layer.
- Hand off to a human with full conversation and action history whenever automation hesitates.
- Record every retrieval, decision, tool call, and human override so any outcome is attributable afterward.

## Strong non-functional requirements
- Latency: tier it by risk — p95 under 3s for routine, under 8s for ambiguous, under 15s for a safe high-risk handoff bundle.
- Availability: at 2M tickets a month and 100 QPS peak, routing, retrieval, and escalation must accept work independently.
- Security: untrusted customer text belongs in a message channel, never a control channel; tools are scoped per workflow.
- Compliance: an immutable trail of actor, model version, tool invoked, fields validated, policy version, and any human override.
- Reliability: degrade into a safe handoff rather than force an answer when a dependency times out or context is incomplete.
- Cost: judge automation by `NetValue = V_time_saved − C_model − C_wrong_resolution − C_recontact`, not by deflection rate alone.

## Architecture explanation
- This is a routed decision pipeline, not a chatbot; every component narrows what the next one is allowed to do.
- The omnichannel gateway normalizes chat, email, web, and voice transcripts into one conversation envelope and owns no business state.
- Identity verification runs synchronously whenever the request could expose account data or trigger an action, and assigns an assurance level.
- The intent and risk router classifies the issue and tags it informational, account-sensitive, money-moving, legal-sensitive, or safety-sensitive.
- Knowledge retrieval pulls approved policy articles, account facts, and prior cases; the response generator drafts a reply or proposed tool call as a recommendation only.
- The tool policy gateway applies deterministic checks — is assurance sufficient, is this action allowed, does the refund exceed threshold — and is the hard authorization boundary.
- The confidence calibrator then decides among auto-resolve, request approval, or escalate to the human-agent queue with reason codes.
- The quality evaluation store records solved, reopened, and corrected outcomes; the customer's CRM and billing systems remain the systems of record, never this layer.

## Data model / integration assumptions
- Case(id, customer_id, channel, intent, risk, state); ProposedAction(id, case_id, tool, args_hash, decision); Handoff(case_id, summary, evidence_refs, attempted_actions).
- Assume the automation layer owns workflow state and decision evidence only; if the source says an account is locked, no cache may contradict it.
- Assume `args_hash` deduplicates logically identical requests without storing raw sensitive arguments, which is where idempotency becomes real.
- Assume every write boundary carries an idempotency key, so a retried message or action returns the original case rather than creating a second one.
- Assume `Case.version` supports optimistic concurrency, so a race between automation and a human agent fails cleanly instead of overwriting.

## Red-team risks
- confidently wrong policy answer, prompt injection in customer text, unverified identity, stale account state, refund executed twice, thin handoff
- Prompt injection or social engineering inside customer text, copied ticket history, or attachments attempting to issue privileged instructions.
- Over-scoped tools, where an assistant that only needs order status is also handed refund, cancellation, and payment-history power.
- Identity spoofing, because "the customer sounds right" is not authentication once the workflow touches billing, PII, or password resets.
- Duplicate side effects when a refund executes but the response times out; retry must reconcile against the ledger, never blindly repeat.
- Thin handoffs that omit intent, tool outputs, policy checks, or uncertainty markers, forcing the agent to repeat work the machine already did.

## Rollout plan
- Week 0-1: fix the scope fence — no open-ended negotiation, no autonomous legal handling, no unsupervised refunds or cancellations.
- Week 1-2: launch as agent-assist only; the model drafts and summarizes, a human sends every final response.
- Week 2-3: prove retrieval quality, escalation logic, and handoff completeness against real traffic before automating anything.
- Week 3-4: automate a narrow set of low-risk, reversible intents such as order status and subscription FAQ.
- Week 5: enable action tools one class at a time, each with its own gate, starting with ticket tagging and order lookup.
- Week 6-8: keep a human review loop sampling automated and assisted cases; maintain a kill switch per intent and per tool.
- After pilot: expand by intent only where safe automation rate holds; roll back a single drifting intent rather than the whole system.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Safe automation rate | Automated cases resolve without correction or harm | Stable per intent; drop triggers rollback | Ticketing system plus QA review labels |
| Incorrect-resolution rate | The system is not confidently closing cases wrongly | At or below the intent-specific baseline | QA review and ticket reopen events |
| Repeat-contact rate | Work was resolved, not just deflected to a second contact | No rise after an automation change | CRM correlation across tickets |
| First-contact resolution | Automation improved resolution, not only typing speed | Holds or improves after each expansion | CRM and ticket timeline |
| CSAT | Throughput gains did not cost customer trust | No decline as automation widens | Post-contact survey platform |
| Cost per resolved case | Savings are real rather than offset by rework | Improves without repeat-contact rising | Finance plus support volume reporting |

## Weak answer
I would send each message to an LLM, draft a reply, and resolve the ticket. This is weak because it treats model output as truth, never verifies identity before touching an account, and puts no policy gate between a fluent answer and a real refund.

## Average answer
I would classify the intent, retrieve policy and account context, draft a grounded reply, and escalate to a human when confidence is low. I would log the interactions. This is better, but still incomplete because it does not name which actions need approval, does not say what happens when a refund executes but the response times out, and treats confidence as sufficient grounds to act.

## Strong answer
I would design this as a routed decision pipeline rather than a chatbot, because the product must decide when to act, when to ask, and when to stop. Identity is verified before any account tool, the router tags risk, retrieval grounds the draft, and a deterministic tool policy gateway — not the model — decides whether an action may execute. Model output is one input to a controlled workflow, never truth. Latency is tiered by risk, and any dependency failure degrades into a safe handoff carrying full context. I would launch agent-assist only, automate low-risk reversible intents next, add one tool class at a time, and keep a kill switch per intent. The key is reducing handling cost without increasing incorrect or harmful resolutions.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | "Build a support chatbot" | Names routing and escalation | Routed decision pipeline, explicit non-goals, constraints separated from preferences |
| Requirements | "Answer tickets accurately" | Lists functional needs | Risk-tiered SLOs, measurable constraints, traceability from requirement to component |
| Architecture | Message in, LLM reply out | Retrieval plus escalation | Identity gate, risk router, deterministic tool policy gateway, calibrator, evaluation store |
| Data/integration | Mentions a ticket table | Names the core records | Case, ProposedAction, Handoff with idempotency, args_hash, optimistic concurrency |
| Evaluation | "Measure accuracy" | Tracks deflection and CSAT | Safe automation rate, incorrect resolutions, repeat contact, cost per resolved case |
| Safety/security | "The model will refuse" | Adds auth and logging | Four seams: untrusted text, least-privilege tools, identity before tools, immutable audit |
| Rollout | Automate everything at once | Pilot on some intents | Agent-assist, low-risk intents, one tool class at a time, per-intent kill switch and rollback |
| Communication | Describes the model | Clear but generic | Leads with the harm case, names the failure policy, closes with the first gate |

## Final 2-minute spoken answer
I would not start with the model. The ask sounds like "automate routine support," but the product is not a chatbot that answers everything — it is a routed service that must decide when to act, when to ask for approval, and when to stop. Take a customer saying they were charged twice and need it fixed today. The naive design sends that to a model and resolves the ticket. The real design starts earlier: verify who the user is, determine whether the request touches money, decide whether it is safe to act on the account, and preserve enough context for a human to take over. So the pipeline is a gateway that normalizes the channel, identity verification that assigns an assurance level, a router that tags intent and risk, retrieval that grounds the draft in approved policy, and then a deterministic tool policy gateway that decides whether any action may execute. That gateway, not the model, is the authorization boundary — model output is one input to a controlled workflow, never truth. Latency is tiered by risk, and if billing times out or the policy check fails, the system degrades into a safe handoff carrying the conversation, the attempted actions, and the reason. I would launch agent-assist only, then automate narrow reversible intents, then add one tool class at a time, each with its own gate and kill switch. Success is lower handling cost with no increase in incorrect or harmful resolutions.
