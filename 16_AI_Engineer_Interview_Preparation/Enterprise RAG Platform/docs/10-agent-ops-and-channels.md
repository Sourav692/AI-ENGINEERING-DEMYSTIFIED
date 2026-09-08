# Operating an AI system in production — versioning, channels, and real escalation

The "after it works once" questions: how do you change a prompt safely, how does the same system
serve multiple channels, and what does "escalate to a human" actually mean as a mechanism. None of
this needs a codebase — it's architecture to describe on a whiteboard.

---

## 1. Treating prompt/config changes like real deployments

The failure mode to name explicitly: most teams ship a prompt change the way they'd ship a quick
config tweak — edit it, deploy it, hope. The fix is to treat every prompt (and the surrounding
configuration — tool definitions, safety rules) as a **versioned, deployable artifact**, not a mutable
string that gets silently overwritten.

### The gate before promoting a new version

Reuse the same evaluation bar a full release would have to pass:

- **A safety/security gate that must hit zero** — no acceptable rate of leaked information, no
  acceptable rate of unsafe output. This is a hard block, not a review comment, for the same reason a
  security incident is never "averaged into" an overall quality score.
- **A quality gate** — accuracy/groundedness must not regress past a set threshold versus the current
  live version, measured on the same fixed test set.
- **A version that fails either gate never reaches even a small slice of real traffic**, let alone
  full rollout.

### Staged rollout

- **Shadow first** — run the new version alongside the live one on real traffic, log both outputs,
  compare them offline. Zero risk to any real user.
- **Small-scale release next** — a small percentage of traffic (or a small set of low-risk customers)
  actually sees the new version; watch the same metrics live, not only at the initial gate.
- **Promote or roll back** based on that — and rollback has to be **instant and cheap**: switch which
  version handles new requests, not a full redeploy. The version that was live five minutes ago should
  still be sitting there, ready to take traffic again immediately.

### A/B testing

Two versions serve concurrently, split by something stable per user (not randomly on every single
request) so one person's experience doesn't flicker between versions mid-conversation. What to compare
on: real outcome metrics (did the answer resolve the issue, did it need escalation), not only an
internal quality score — and the safety gate has to be identical (zero) across both versions, never
something you're "testing" a difference on.

## 2. Multi-channel delivery

The same core system — retrieve, ground, answer — has to serve a live chat widget, a messaging
platform, email, and a raw API, and those are not the same problem wearing different clothes.

| Channel | Latency expectation | Output shape | What this means for the design |
| --- | --- | --- | --- |
| **Live chat** | Sub-second first response | Short, conversational, streamed | Needs token streaming; can't wait for the full answer before showing anything |
| **Team messaging (e.g. Slack)** | A few seconds is fine | Slightly more structured | Can afford one extra retrieval pass that a live-typing interface can't |
| **Email / async reply** | Minutes is fine | Longer, more formal | This is where a separate drafting step earns its keep — same underlying answer, very different prose |
| **Raw API** | Caller-defined | Structured data, not prose | No "drafting" step at all — the raw grounded answer plus its sources, in a machine-readable shape |

**The architecture implication:** don't build a separate agent per channel. Keep one core pipeline
(retrieve → ground → cite → refuse) behind a **thin channel-adapter layer** that only changes two
things: how much latency budget is available (which affects how much extra retrieval work is
affordable), and how the same grounded answer gets formatted for that channel's expectations. The
permission/security layer stays identical across every channel, on purpose — which channel someone
used is a presentation decision, never a permissions decision.

## 3. Human-in-the-loop escalation as a real workflow, not a phrase

"Refuse cleanly and escalate to a human" is the right policy. It says nothing yet about the
*mechanism* — and in a support/ticketing context, "escalate" has to become something concrete, not
just a message shown to the user.

**What escalation has to actually do:**

1. **Create or update a real record somewhere a human will see it** — not just return a message and
   move on. The case needs to land in whichever queue actually owns this kind of question.
2. **Attach the working context** — the original question, whatever was found (even if it wasn't
   enough), why it was judged insufficient or why access was denied. The human shouldn't have to start
   from zero, and the person asking shouldn't have to repeat themselves.
3. **Route to the right owner.** A question denied for permission reasons and a question with no
   available information at all are different problems — they belong in different queues. Mixing them
   either floods a security queue with routine content gaps, or buries real access-denial cases that
   need review among unrelated ones.
4. **Never leak the reason for a permission-based refusal into a record visible to a broader
   audience** than the original request was. An internal note explaining *why* something was denied can
   itself be a disclosure if the wrong audience can see it — the escalation record is subject to the
   same permission rules as the original question.
5. **Feed the outcome back into evaluation.** Every escalation is a free, labeled example: either "the
   system should have been able to answer this" (a genuine content or capability gap, worth fixing) or
   "the system correctly refused" (evidence the safety behavior is working as intended, not something
   to fix). This closes a common gap in most systems — there's usually no loop from live usage back
   into the evaluation process, and escalation outcomes are exactly the signal that closes it, using a
   mechanism the product already needs anyway.

---

## What to say if asked directly

*"Versioning and channels aren't built in a first pass, but the mechanisms generalize cleanly: the same
evaluation gate that would block a full release also has to gate a new prompt version before it can
even reach a small slice of traffic — the safety bar doesn't get softer just because it's framed as an
A/B test. For channels, I'd keep one core pipeline and put a thin adapter in front that only changes
latency budget and output formatting — never the security layer, because which channel someone used is
a presentation decision, not a permissions decision. And for escalation: 'refuse and escalate' has to
mean something concrete — create a record, attach the context, route it to the right queue, and feed
the outcome back into evaluation, because every escalation is a free labeled example of either a real
gap or a correctly-working refusal."*
