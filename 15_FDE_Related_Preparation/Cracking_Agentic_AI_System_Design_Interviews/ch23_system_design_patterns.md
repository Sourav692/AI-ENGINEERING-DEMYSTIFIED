# Chapter 23 — System Design Patterns for Agents

By now the ops agent has touched almost every idea in this book — a tool
gateway, typed results, a context assembler, a skill library, an evaluation
harness. This chapter's job is to give all of that a shared vocabulary: named
patterns across six families, each with the forces that produce it, what it
costs you, and the one metric that tells you whether it's actually earning
its place.

## Why Names Matter

**A pattern you can't name is a pattern you'll rediscover slowly, under time
pressure, on a whiteboard.**

Naming a pattern buys you three things: it compresses a paragraph of
explanation into two words, it signals you've seen this problem before, and
it gives your interviewer a hook to probe with — turning a monologue into an
actual design conversation.

> **🎯 OpenAI Interview Pointer**
> The book's own framing: naming a pattern is a mid-level signal. **Naming the pattern plus the measurement that justifies it** is a senior signal — it shows you treat architecture as falsifiable claims, not taste. Every pattern below has that measurement attached for exactly this reason.

## Family One: Orchestration Patterns

**Govern the topology of decision-making — the foundational choice that sets your latency ceiling, token profile, and failure containment boundary.**

| Pattern | Forces & structure | Consequence | Measurement |
|---|---|---|---|
| Router | Enumerable, disjoint intents; small model picks one of n branches | Cheap, predictable, misroutes silently | Route distribution, shadow disagreement rate |
| Bounded Loop | Next step depends on last observation; 4 independent bounds | Adaptive, variable cost | Budget termination rate, step p95 |
| Plan then Execute | Independent subtasks known upfront; plan once, fan out | Parallel, commits before evidence | Replan rate, plan validity |
| Reflection | A critic with an information advantage revises a draft | Better output, ~2x tokens | Revision acceptance rate, critic agreement |
| Supervisor | Distinct specialities; one coordinator delegates + synthesizes | Tree-shaped trace, terminates by construction | Coverage, per-worker spend |
| Pipeline | Process has named stages; fixed sequence, bounded reject-back | Predictable latency, testable stages | Stage pass rate, reject-back rate |
| Blackboard | Contribution order unknown; agents read/write shared state | Decoupled, needs strict concurrency discipline | Write conflict rate |
| Event Driven | Work arrives async, over long horizons | Decoupled from request lifetime | Queue lag, duplicate rate |

## Family Two: Context and Memory Patterns

**Govern how information is budgeted, organized, and retrieved across time — because the context window is a scarce, expensive resource that degrades non-linearly when overloaded.**

| Pattern | Forces & structure | Consequence | Measurement |
|---|---|---|---|
| Context Assembler | Window is finite; fixed section order + per-section budgets | Deterministic, cacheable, reconstructable | Section token shares, eviction counts |
| Sub-agent Isolation | Subtask consumes a window the parent needs; isolate, return a summary | Parent grows by hundreds, not thousands | Parent context growth per subtask |
| Structured Compaction | History must shrink; extract into typed records, not prose | Stable across re-compaction | Fact retention across compactions |
| Memory Tiering | Different query patterns need different stores | Right store per tier | Retrieval precision per tier |
| Evidence Ledger | Parallel workers re-retrieve the same sources | Removes duplicate retrieval cost | Duplicate source rate |
| Predicate Normalization | Contradictions can't be resolved by similarity | Newer fact supersedes by construction | Contradiction rate in the store |

## Family Three: Tool and Action Patterns

**Manage the interface between probabilistic reasoning and deterministic external systems — the primary failure mode without them is unconstrained environment access.**

| Pattern | Forces & structure | Consequence | Measurement |
|---|---|---|---|
| Tool Gateway | Model must not touch the environment directly; authorize→validate→bound→execute→classify→project→observe | Single security and cost boundary | Denial rate, argument validity |
| Typed Result | "Empty" and "unavailable" are different facts | Removes retry storms | Status mix per tool |
| Projection | Upstream schema growth inflates context | Cost decoupled from other teams' changes | Payload bytes per tool |
| Idempotency Key | Retries and checkpoint restores repeat effects | Safe retry of writes | Duplicate effect rate |
| Tool Retrieval | Selection degrades past ~40 tools | Short advertised list | Selection accuracy, retrieval recall |
| Action Selector | Free-form calls can be invented by injected text | Injection can't fabricate actions | Invalid action attempt rate |

## Family Four: Reliability Patterns

**Convert the compounding failure probability of a multi-step run into recoverable, bounded operations — partial dependency degradation is the normal operating condition, not an edge case.**

| Pattern | Forces & structure | Consequence | Measurement |
|---|---|---|---|
| Degradation Ladder | Partial failure is normal; rungs from full capability to honest refusal | Partial answers instead of exceptions | Rung distribution |
| Circuit Breaker | A failing dependency must not be retried into the ground | Fast failure, faster recovery | Open duration, half-open success |
| Typed Bounded Retry | Some failures are retryable, some aren't | No retry on denials/invalid args | Retry success rate by status |
| Checkpoint and Resume | Long runs meet deploys and preemptions | Runs survive process death | Resume rate, duplicate effect rate |
| Human Interrupt | Irreversible actions need a decision | Pause without holding a process | Approval queue age, expiry rate |
| Compensating Action | Some effects can't be undone, only offset | Recovery path exists | Compensation success rate |

> **🔍 Deep Dive: two of these, worked through properly**
> **Degradation Ladder** — an ordered set of rungs from full capability to honest refusal, selected by a pure function of a health snapshot, with the selected rung *disclosed to the user* and emitted as a span attribute. The common finding when teams first instrument this: a meaningful share of traffic has been running above rung zero, unnoticed, for a while.
> **Circuit Breaker** — closed / open / half-open state machine per dependency. Trip on a **windowed failure rate with a minimum sample size**, never on consecutive failures — agent traffic is bursty, so a consecutive-failure trigger either trips constantly or never trips at all. In the open state, return a typed `UNAVAILABLE` immediately so the degradation ladder can select a lower rung. In half-open, admit only a small number of probes — otherwise recovery is indistinguishable from a second outage.

> **🎯 OpenAI Interview Pointer**
> "Trip circuit breakers on a windowed failure rate with a minimum sample, not on consecutive failures, because agent traffic is bursty" is a direct quote-worthy line from the book's own chapter summary. It's specific, mechanism-level, and cheap to have ready.

## Family Five: Safety Patterns

**Enforce architectural security boundaries rather than relying on probabilistic prompt-level compliance — injection and exfiltration can't be mitigated by asking the model to behave.**

| Pattern | Forces & structure | Consequence | Measurement |
|---|---|---|---|
| Privilege Separation | Untrusted content must not reach a component with capability | Injection can't act | Residual attack success rate |
| Provenance Tagging | Policy must refer to where content came from | Makes the trifecta rule enforceable | Untrusted content share per run |
| Trifecta Guard | Three capabilities are jointly dangerous together | Composition refused, not filtered | Guard trigger rate |
| Egress Firewall | Data leaves through arguments AND rendered output | Exfiltration blocked on both paths | Egress denials by principal |
| Approval Gate | Irreversible actions need a person | Bounded catastrophic risk | Decision time, later reversal rate |
| Grounded Refusal | An uncited claim in grounded mode is not a fact | Confident errors become refusals | Citation-free answer rate |

## Family Six: Cost and Evaluation Patterns

**Provide economic governance and continuous quality verification — agent workloads compound token usage quadratically over long trajectories, so uncontrolled execution creates real billing surprises.**

| Pattern | Forces & structure | Consequence | Measurement |
|---|---|---|---|
| Prefix Cache Boundary | Input tokens dominate; keep the prefix byte-stable | Large input cost reduction | Cache hit rate |
| Tier Router | Quality difference on easy traffic is small | Spend follows difficulty | Shadow disagreement rate |
| Semantic Answer Cache | Traffic repeats; key on corpus versions | Whole runs removed | Hit rate, stale answer rate |
| Early Termination | Enough evidence should stop the loop | Removes the *most expensive* steps | Steps saved per run |
| Cost Governor | Worst case must be bounded, not just average | Graduated degradation, no surprise invoice | Ceiling trigger rate |
| Trajectory Assertion | Several paths are valid; assert properties, not paths | Unsafe paths fail, valid ones pass | Assertion coverage |
| Shadow Evaluation | Small differences need production volume to detect | Router/model quality becomes observable | Disagreement rate |
| Canary with Guardrails | Offline can't detect small regressions | The rollout itself becomes the detector | Rollback rate, breach lead time |

## Composition Rules and the Pattern Audit

**Patterns compose — real production systems layer several from each family — but every pattern you add without a reason is cost someone pays at 3am with nothing to show for it.**

**Key points**
- A representative composed system: an event-driven or router entry point, wrapping a bounded loop or supervisor, wrapped by a tool gateway with typed results, wrapped by a circuit breaker and a degradation ladder — with a cost governor and trajectory assertions cutting across the whole thing.
- The audit question for every pattern in your system: **what metric motivated this, and what incident has it actually prevented?** No answer to either is a strong signal to remove it.

> **🔍 Deep Dive: the system with nine patterns nobody could justify**
> A real case from the book. A production system accumulated five layers of indirection between a request and a model call, three separate caches with different invalidation rules, two overlapping retry mechanisms that occasionally interacted to produce duplicate effects, and an 11-rung degradation ladder — four of whose rungs had never once been observed in production. **Resolution:** the team ran an inventory — for every pattern, produce the metric that motivated it and the incidents it prevented. Nine patterns had neither, and were removed. The two overlapping retries were consolidated into one typed bounded retry. The ladder shrank to 5 rungs matching actually-observed failure modes. Mean time to resolution fell substantially, and *no capability was lost*.

> **🎯 OpenAI Interview Pointer**
> The transferable lesson, in the book's own words: "patterns are answers to questions. A system that contains answers to questions nobody asked is carrying cost with no corresponding benefit, and the cost is paid by whoever is on call at three in the morning." A strong closing line for any system-design answer where you're asked to justify architectural complexity — showing restraint reads as more senior than showing breadth.

---

## Cheat Sheet

| Family | The one thing to remember |
|---|---|
| Orchestration | Real systems compose these 8; the composition itself is the strongest answer |
| Context & Memory | Fixed assembly + isolation + typed extraction — the three things that keep context sane |
| Tool & Action | The gateway's 7-step order + typed results is the single biggest reliability lever |
| Reliability | Circuit breakers trip on windowed rate, never consecutive failures — agent traffic is bursty |
| Safety | Architectural boundaries, not prompt compliance — privilege separation + provenance make the trifecta guard enforceable |
| Cost & Evaluation | Prefix cache boundary is usually the single largest cost lever; canaries catch what offline evaluation can't |
| Composition | Every pattern needs a metric AND an incident it prevented — audit and remove what has neither |
