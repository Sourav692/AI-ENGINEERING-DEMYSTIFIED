# Multi-Channel Delivery and Human Escalation

> **Level** 🟠 Scale, Security, Operations · **Module** 08 · **Doc** 4 of 6 · **Time** ~20 min
> **Prerequisites:** Module 04 doc 6 (refusal), Module 05 doc 2 (channel adapters), Module 06 doc 3 (streaming), Module 07 doc 2 (the escalation agent)
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/10-agent-ops-and-channels.md` §2–3

## Why this matters

Two more "after it works once" questions. First: the same core system has to serve a chat widget, a messaging platform, email and a raw API — and those are not the same problem in different clothes. Second: "refuse cleanly and escalate to a human" is the right policy, but it says nothing about the *mechanism* — and in a support or ticketing context, "escalate" has to become something concrete, or it is just a message shown to the user before they give up.

## Multi-channel delivery

| Channel | Latency expectation | Output shape | What it means for the design |
|---|---|---|---|
| **Live chat** | Sub-second first response | Short, conversational, streamed | Needs token streaming; cannot wait for the full answer before showing anything |
| **Team messaging (Slack)** | A few seconds is fine | Slightly more structured | Can afford one extra retrieval pass a live-typing interface cannot |
| **Email / async** | Minutes is fine | Longer, more formal | Where a separate drafting step earns its keep — same answer, very different prose |
| **Raw API** | Caller-defined | Structured data, not prose | No drafting step at all — the grounded answer plus sources, machine-readable |

**The architecture implication: do not build a separate agent per channel.** One core pipeline — retrieve → ground → cite → refuse — behind a **thin channel-adapter layer** that changes exactly two things:

1. **How much latency budget is available**, which decides how much extra retrieval work is affordable (multi-query and HyDE for email; dense-only for chat).
2. **How the same grounded answer is formatted** for that channel's expectations — which is Module 07's Drafting agent, and Module 06's "streaming is a channel decision".

**The permission and security layer is identical across every channel, on purpose.** Which channel someone used is a presentation decision, never a permissions decision. Module 05 built the inbound half of this — channel adapters normalising into one canonical event; this is the outbound half. Same principle: translate once at the edge, keep the core channel-blind.

## Human-in-the-loop escalation as a real workflow

What escalation has to actually do:

**1 · Create or update a real record somewhere a human will see it.** Not just return a message and move on. The case lands in whichever queue owns this kind of question. Module 07's Escalation agent exists to do exactly this through a fixed set of record operations.

**2 · Attach the working context.** The original question, whatever was found (even if insufficient), why it was judged insufficient or why access was denied. The human should not start from zero, and the person asking should not have to repeat themselves. This is the handoff package from Module 07, handed to a person instead of an agent.

**3 · Route to the right owner.** A question denied for permission reasons and a question with no available information are different problems and belong in different queues. Mixing them either floods a security queue with routine content gaps, or buries real access-denial cases among unrelated ones.

**4 · Never leak the reason for a permission-based refusal into a record visible to a broader audience than the original request.** An internal note explaining *why* something was denied can itself be a disclosure if the wrong audience can see it. The escalation record is subject to the same permission rules as the original question. Module 04's refusal hygiene, extended to the ticket.

**5 · Feed the outcome back into evaluation.** Every escalation is a free, labelled example: either "the system should have been able to answer this" — a genuine content or capability gap, worth fixing — or "the system correctly refused" — evidence the safety behaviour works. This closes the gap Module 04's coverage map named as unbuilt: there is usually no loop from live usage back into evaluation, and escalation outcomes are exactly the signal that closes it, using a mechanism the product already needs.

```
   grade → insufficient ──▶ refuse ──▶ ESCALATE
                                          │
                   ┌──────────────────────┼──────────────────────┐
                   ▼                      ▼                      ▼
            create/update          attach context          route by cause
            a real record          (q, found, why)         ├─ permission-denied → security/owner queue
                   │                      │                └─ no information    → content-owner queue
                   └──────────┬───────────┘
                              ▼
                  record inherits the original request's permission scope
                              │
                              ▼
                  outcome → evaluation set   (gap to fix  |  correct refusal)
```

## Interview lens

> *"For channels, I'd keep one core pipeline and put a thin adapter in front that only changes latency budget and output formatting — never the security layer, because which channel someone used is a presentation decision, not a permissions decision. And 'refuse and escalate' has to mean something concrete: create a record, attach the context, route it to the right queue by cause, keep the record under the same permission scope as the question, and feed the outcome back into evaluation — every escalation is a free labelled example of either a real gap or a correctly working refusal."*

## Checkpoint

- What are the *only* two things a channel adapter may change, and what must it never change?
- Why does email get a drafting step and the raw API none?
- List the five things escalation must do.
- Why do permission-denied and no-information cases need different queues?
- How does an escalation record become a leak, and what prevents it?
- Which unbuilt item from Module 04's coverage map does step 5 close?

**Next →** [Red Teaming](05_Red_Teaming.md)
