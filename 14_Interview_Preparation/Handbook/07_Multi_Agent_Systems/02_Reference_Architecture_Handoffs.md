# Reference Architecture and Handoffs

> **Level** 🟠 Scale, Security, Operations · **Module** 07 · **Doc** 2 of 5 · **Time** ~25 min
> **Prerequisites:** [When Multi-Agent Is Justified](01_When_Multi_Agent_Is_Justified.md); Module 04, Module 05
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/09-multi-agent-orchestration.md` §2–3

## Why this matters

Once a split is justified, the question is what the specialists are and — far more important — what passes between them. The naive design hands the entire conversation to every agent. That is expensive, leaks information an agent has no need to see, and makes it impossible to reason about what any agent may depend on. The handoff is the actual hard part of multi-agent design, and it is where the security discipline of Modules 04 and 05 has to be re-applied rather than assumed.

## A reference architecture

A common ask: a system where specialised agents work together across a knowledge base, a ticketing system and a records system.

```
                     customer / support message
                                   |
                                   v
                        ┌────────────────────┐
                        │   TRIAGE AGENT      │   classify: bug report? billing question?
                        │                     │   feature request? "why did X happen"?
                        └──────────┬──────────┘
                                   |
        ┌──────────────────────────┼──────────────────────────┐
        v                          v                          v
┌───────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ ANSWER AGENT    │        │ RECORD AGENT      │        │ ESCALATION AGENT  │
│ retrieves,      │        │ creates/updates   │        │ hands off to a    │
│ grounds, cites,  │        │ a ticket/record   │        │ human queue with  │
│ or refuses       │        │ via a fixed set   │        │ full context      │
│                 │        │ of operations     │        │                    │
└───────┬─────────┘        └──────────┬────────┘        └──────────┬────────┘
        |                             |                             |
        └──────────────────────────────┴──────────────────────────────┘
                                   v
                        ┌────────────────────┐
                        │   DRAFTING AGENT    │   turns the answer + ticket state into
                        │                     │   a channel-appropriate reply
                        └────────────────────┘
```

| Agent | Job | Why it is separate |
|---|---|---|
| **Triage** | Decides which specialist owns this question at all | Module 06's structured-vs-semantic router, one level up |
| **Answer** | Retrieve, ground, cite — or refuse cleanly | Exactly Module 04's single-agent RAG. Its job is *being right* |
| **Record** | Writes to ticketing/CRM through a **fixed, reviewed set of operations**, never an open query | Same reasoning as the constrained structured path: the surface of what can happen is a reviewed list |
| **Escalation** | Turns "the answer agent couldn't ground this" into a real workflow action — create or update a ticket, route to the right queue, attach gathered context | Module 08 covers what escalation must actually do |
| **Drafting** | Turns answer + ticket state into a channel-appropriate reply | Kept apart from Answer on purpose: Answer's job is *being right*; Drafting's is *saying it well for this channel*. A chat reply, a ticket comment and a formal email differ in tone and length. Splitting them means a tone change never touches correctness logic |

Notice that the Answer agent is *unchanged* from the single-agent design. Multi-agent did not replace it; it put a triage layer in front and specialists beside it. The thing that was already proven stays proven.

## The handoff is the hard part

The naive version passes the entire conversation history to every agent. The better version: each handoff is a **small, well-defined package**:

```
  handoff = {
    case_id,
    what_was_asked,
    what_was_attempted,
    why_it_was_insufficient,      # or: why access was denied
    what_was_already_gathered,    # so the next agent does not repeat work
    permission_scope,             # tenant · clearance · region · compartments — carried, not re-derived
  }
```

Two properties to state explicitly:

**1 · Permission scope travels with the handoff; it is never re-derived.** If one agent hands a case to another, the receiving agent must never end up with broader access than the original request had. The same tenant, clearance, region and compartment scope carries forward, exactly. An escalation agent that re-resolves identity — or worse, runs as a service principal — is a privilege-escalation path. Module 04's `Principal` is the thing in the package.

**2 · A handoff is a state transition someone can replay safely.** The same discipline that makes Module 05's orchestrator trustworthy applies here: a retried handoff must not create two tickets; a crash between two agents must not drop the case on the floor. That means an idempotency key on the handoff and a checkpoint after it — the handoff *is* a step in a durable run.

## Two coordination shapes

The reference architecture above is a **supervisor** shape: triage decides, specialists execute, results converge. The fifth document of this module shows the same shape and then its evolution into a **deep agent** shape — an orchestrator delegating to fully self-contained sub-agents, each with its own prompt, small toolset and context window. The difference:

| | Supervisor | Deep agent / orchestrator + sub-agents |
|---|---|---|
| Who holds the tools | The supervisor holds routing; specialists hold their own | Each sub-agent is self-contained: own prompt, own tools, own context |
| Where context lives | Shared graph state, resolved centrally | Per sub-agent; the orchestrator holds only what it needs to delegate |
| When it fits | A bounded set of specialists; consistency of shared lookups matters | The supervisor's own tool list has started to bloat; domains keep growing |
| The cost | One extra hop for centralised resolution | More infrastructure surface: more endpoints, more moving parts |

Neither is "better". The second is what you evolve *to* when the first re-encounters the tool-bloat trigger one level up.

## Interview lens

> *"I'd keep the answer-generation agent scoped exactly the way a good single-agent RAG design already proves — retrieve, ground, cite, refuse. Multi-agent means putting a triage layer in front that routes to specialists — a record-writing agent, an escalation agent, a drafting agent — each with its own fixed, narrow toolset, not one shared do-everything toolbox. The part I'd be most careful about is the handoff: a small, defined package, not the full conversation — and critically, permission scope travels with that handoff rather than getting re-derived, so an escalation never accidentally sees more than the original question was allowed to."*

## Checkpoint

- Name the five agents in the reference architecture and say why Answer and Drafting are separate.
- List the fields of a good handoff package.
- Why must permission scope be carried rather than re-derived? What goes wrong otherwise?
- What two properties from Module 05 apply to a handoff, and how?
- When would you evolve from a supervisor to an orchestrator-plus-sub-agents shape?

**Next →** [Failure Isolation and Evaluation](03_Failure_Isolation_And_Evaluation.md)
