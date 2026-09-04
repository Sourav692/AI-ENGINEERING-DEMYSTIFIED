# Multi-agent orchestration — search, records, and ticketing together

A common interview ask: architect a system where multiple specialized agents work together across a
knowledge base, a ticketing system, and a records system. None of this needs a codebase — it's
architecture to describe on a whiteboard, including where the line is between "this is multi-agent"
and "this is one pipeline with several steps," because interviewers will notice if that line gets
blurred.

---

## 1. What actually makes something "multi-agent"

A single pipeline with several steps — rewrite the question, retrieve, check quality, generate an
answer — is **not** multi-agent. It's one agent with several *steps*. That's a perfectly good design,
and it's honest to describe it as such rather than overclaim.

**Multi-agent** means multiple **independently-scoped** agents, each with its own responsibility, its
own tools, and its own failure mode — coordinated by something above them, handing off a well-defined
package of information rather than a raw conversation transcript.

| | Single agent, multi-step | True multi-agent |
| --- | --- | --- |
| Who decides what happens next | One fixed sequence | A coordinator, or the agents themselves via handoff |
| Tool access | One shared set of tools | Each agent scoped to only what its job needs |
| Failure blast radius | One bad step can fail the whole run | One agent's failure should degrade, not crash, the others |
| What gets passed forward | Everything accumulates | A defined handoff — the next agent gets what it needs, not everything |

## 2. A reference architecture

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

- **Triage agent** — decides which specialist owns this question at all, generalizing the same idea
  as routing between structured and semantic search, one level up.
- **Answer agent** — its job is exactly retrieve, ground, cite, and refuse cleanly when it can't.
- **Record agent** — owns writes to the ticketing/CRM system through a **fixed, reviewed set of
  operations**, never an open-ended query — same reasoning as keeping the structured-data path
  constrained rather than free-form.
- **Escalation agent** — turns "the answer agent couldn't ground this" into a real workflow action:
  create or update a ticket, route it to the right queue, attach whatever context was gathered so the
  human doesn't start from zero.
- **Drafting agent** — kept separate from the answer agent on purpose: the answer agent's job is
  *being right*; the drafting agent's job is *saying it well for this specific channel* (a chat reply,
  a ticket comment, and a formal email have very different tone and length needs). Splitting these
  means a tone change never risks touching the underlying correctness logic.

## 3. The handoff between agents is the actual hard part

The naive version passes the entire conversation history to every agent. That's expensive, leaks
information one agent doesn't need to see, and makes it hard to reason about what any single agent is
actually allowed to depend on.

The better version: each handoff is a **small, well-defined package**, not a full transcript —
something like: which case this is, what was asked, what was attempted, why it wasn't sufficient, and
what was already gathered so the next agent doesn't repeat work.

Two things worth stating explicitly if asked:

1. **Permission scope has to travel with the handoff, not get re-derived.** If one agent hands a case
   to another, the receiving agent must never end up with broader access than the original request
   had — the same tenant/clearance/region scope carries forward, exactly.
2. **A handoff should be a state transition someone can replay safely.** The same discipline that
   makes a workflow system trustworthy — an action can't accidentally happen twice, a crash midway
   doesn't silently lose the case — applies here too: a retried handoff shouldn't create two tickets,
   and a crash between two agents shouldn't drop the case on the floor.

## 4. Failure isolation

- **A failure limiter scoped per agent**, not shared globally — one specialist being down shouldn't
  trip a safeguard that then blocks a completely unrelated specialist too.
- **A bounded number of handoffs per case.** Two agents that can hand a case back and forth risk an
  infinite loop (triage → escalate → triage → ...). Cap the total number of hops and force a final
  outcome — answered, escalated, or failed safely — once that cap is hit, the same instinct as any
  hard budget: halt and report, don't let it run forever.
- **Partial degradation, not total failure.** If the record system is down, the answer agent should
  still be able to answer a pure knowledge question — one specialist's outage shouldn't take down
  specialists that don't depend on it.

## 5. Evaluating a multi-agent system

- **Evaluate each agent, not only the end result.** Did triage route correctly? Did the record agent
  use the right parameters? Did escalation actually attach useful context? A wrong final answer could
  trace back to any one of these — the same reason it's useful to separate "was the right information
  found" from "was the final answer good," just with more stages to separate here.
- **Handoff correctness as its own thing to measure** — did the receiving agent get everything it
  needed, or did it have to guess/re-derive context (a sign the handoff design is under-specified)?
- **The security bar applies the same way everywhere.** A leak caused by one agent forwarding
  restricted information to the wrong place is exactly as serious as a leak in the main answer — it
  doesn't get a pass just because it happened between two agents instead of inside one.

---

## What to say if asked directly

*"I'd keep the answer-generation agent scoped exactly the way a good single-agent RAG design already
proves — retrieve, ground, cite, refuse. Multi-agent means putting a triage layer in front that routes
to specialists — a record-writing agent, an escalation agent, a drafting agent — each with its own
fixed, narrow toolset, not one shared do-everything toolbox. The part I'd be most careful about is the
handoff: a small, defined package, not the full conversation — and critically, permission scope has to
travel with that handoff rather than get re-derived, so an escalation never accidentally sees more
than the original question was allowed to."*
