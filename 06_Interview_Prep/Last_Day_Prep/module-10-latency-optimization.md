# Module 10 — Latency Optimization

## CONCISE INTERVIEW MODULE

### 1. What the Interviewer Is Testing

- Can you measure the actual waiting experience before optimizing?
- Can you find the critical path across queues, retrieval, models, and tools?
- Can you distinguish streaming, parallelism, and asynchronous delivery?
- Can you reduce latency while preserving quality and safe actions?

### 2. Core Mental Model

```text
MEASURE → DEFINE SLO → FIND CRITICAL PATH
                              ↓
STREAM / PARALLELIZE / REDUCE HOPS
                              ↓
RETRIEVAL / TOOLS / QUEUE / ASYNC
                              ↓
           Recheck quality + latency + cost
```

A service-level objective (SLO) is an agreed target for a defined workload and measurement window.

```text
End-to-end latency includes:
Queue wait + network + retrieval + model calls
           + orchestration overhead + tools
```

Do not double-count time already included inside another measured span. Parallel branches contribute their critical-path duration, not the sum of all branch durations.

### 3. Essential Concepts

#### 1. P50/P95/P99 — Inspect the Distribution

P50 is the median. P95 and P99 show slower-tail behavior: 95% or 99% of measured requests complete at or below those values.

> “I’d segment latency by workload and inspect the tail, not just the average.”

```text
Average looks acceptable
        ↓
P99 very slow → Some users still wait too long
```

Compare consistent measurement windows and task types. Aggregate improvements can hide a badly affected tenant or workload.

#### 2. Trace the Request — Locate the Critical Path

Measure queue, retrieval, model, tool, and network spans, including repeated calls. Look at the slow requests themselves.

> “If the model takes two seconds and the task takes twelve, I’d inspect the other ten seconds before switching models.”

```text
Queue 4s → Retrieval 1s → Model 2s → Tool 4s → Overhead 1s
```

These times are illustrative. Identify which stages are sequential and which overlap.

#### 3. Time to First Token and Streaming — Improve Perceived Waiting

Time to first token (TTFT) measures when model output begins; user-visible first useful output may occur later. Streaming displays partial output while generation continues.

> “I’d track both first useful output and final completion; streaming improves waiting experience without necessarily reducing total work.”

```text
Non-streamed: Wait ─────────→ Full response
Streamed:     Wait → Partial output → Full response
```

Do not stream an action as successful before execution is confirmed. Partial output must remain safe and not expose unverified sensitive information.

#### 4. Parallelization — Overlap Independent Work

Run independent retrieval or read-tool calls together when permissions, dependency limits, and correctness allow it.

> “I’d parallelize independent order and policy reads, but preserve sequencing where one result is needed for another.”

```text
Sequential: Read A → Read B → Combine
Parallel:   Read A ─┐
            Read B ─┴→ Combine
```

The parallel path is governed by the slowest necessary branch plus overhead. Parallelism can increase load and does not justify unordered business writes.

#### 5. Reduce Sequential Model Hops — Remove Unnecessary Reasoning Calls

Inspect router, planner, agent, critic, and writer calls. Combine or replace steps only when their purpose is preserved.

> “Does this stage need model reasoning, or can a rule, schema check, or simpler call do it?”

```text
Five model hops → Identify required functions
                       ↓
                Fewer justified calls
```

Do not remove policy, authorization, or evaluation controls merely to reduce latency.

#### 6. Retrieval — Optimize the Evidence Path

Measure query embedding, search, filtering, reranking, and context construction. Tune candidate counts, indexing, and caching against quality requirements.

> “I’d reduce retrieval work only while preserving evidence recall, access enforcement, and answer quality.”

```text
Search candidates → Rerank if useful → Select context
```

Permission-safe cache reuse can help; stale or unauthorized evidence is not an acceptable speed improvement.

#### 7. Tools — Control Slow Dependencies

Measure enterprise API latency, set deadlines, reuse results only within freshness limits, and use fallback or async completion where the use case allows it.

> “A slow ERP will not become fast just because I choose a faster model.”

```text
Slow tool → Deadline → Safe fallback / defer / escalate
```

For write timeouts, reconcile the operation's status before retry. Stopping waiting does not cancel a remote side effect automatically.

#### 8. Queue Wait — Protect Tail Latency Under Load

Separate time waiting for capacity from actual processing. Apply admission control, tenant-aware limits, bounded queues, and useful capacity scaling.

> “If model time is stable but queue wait grows at peak, I’d address overload rather than model speed.”

```text
Low load:  Short wait + processing
Peak load: Long wait  + similar processing
```

An unbounded queue can make every request late instead of rejecting excess work clearly.

#### 9. Async Delivery — Change the Interaction for Long Tasks

For work that legitimately takes minutes, return a task identifier and provide status, progress, and result retrieval rather than holding one interactive request open.

> “For a five-minute research task, I’d agree on completion expectations and use asynchronous delivery.”

```text
Submit → Acknowledge task ID → Background execution
                                      ↓
                              Status / result / notification
```

Async reduces blocking for the client, not necessarily task completion time. Persist state and define cancellation or timeout behavior.

### 4. Requirement → Component Reasoning

| Requirement | Pattern / component | Why | Trade-off |
|---|---|---|---|
| Know where time goes | End-to-end traces | Identify critical path | Instrumentation effort |
| Earlier useful output | Streaming | Reduce perceived waiting | Partial-output handling |
| Independent slow reads | Concurrent execution | Overlap waiting | More concurrent dependency load |
| Too many sequential calls | Simpler routing/workflow | Remove redundant hops | Quality must be reevaluated |
| Repeated eligible lookups | Scoped cache | Avoid repeated retrieval/tools | Freshness and permissions |
| Peak queue delay | Admission + bounded queues + capacity | Protect waiting time | Deferral/rejection |
| Long-running task | Async jobs + durable state | Match interaction to duration | Status/result UX |

**Support example:** measure policy retrieval and live order lookup, overlap them if independent, limit unnecessary model hops, and keep refund checks and confirmation intact. Investigate peak queue wait separately from normal processing time.

### 5. Important Distinctions and Gotchas

1. **Average vs tail:** P95/P99 expose slow experiences hidden by averages.
2. **First token vs useful output vs completion:** these are different user and system measurements.
3. **Streaming vs less computation:** showing output earlier does not necessarily reduce generation time.
4. **Parallel vs dependent work:** overlap independent operations; preserve necessary ordering and writes.
5. **Async vs faster task:** releasing the request does not shorten underlying execution.

### 6. Trigger → Concept Table

| Hear… | Think… | Inspect… |
|---|---|---|
| “Average 3s, P99 25s” | Tail latency | Slow traces, tenants, workload classes |
| “Three independent APIs sequentially” | Parallelization | Dependencies and limits |
| “Model fast, task slow” | Critical path | Queue, tools, retrieval, overhead |
| “Long silent wait” | First useful output | TTFT, streaming, progress |
| “Five model calls” | Sequential hops | Necessity of each reasoning step |
| “Slow only at peak” | Queue/capacity | Wait age and saturation |
| “Five-minute research” | Async interaction | Task state and delivery expectations |

### 7. Interview Phrases

> “I’d trace latency end to end before deciding what to optimize.”

> “I’d measure first useful output and final completion separately.”

> “I’d overlap independent work and reduce unnecessary sequential hops.”

> “I’d recheck quality and safety after any latency optimization.”

### 8. Practice Questions

1. Average latency is three seconds but P99 is 25 seconds. What traces and segments do you inspect?
2. CRM, order, and ticket reads are sequential. When can you parallelize them, and when can you not?
3. Model time is two seconds but total time is twelve. How do you locate the bottleneck?
4. Streaming starts quickly but completion remains slow. Which experience improved, and what remains unresolved?
5. A five-minute task has useful progress updates. Design its request, state, status, and result interaction.

---

## ONE-PAGE MEMORY CARD — Latency Optimization

**Core question:** Where does the user wait, and what change improves that experience without breaking quality or safe execution?

### Recall Flow

```text
MEASURE → SLO → CRITICAL PATH
                    ↓
STREAM / PARALLELIZE / REDUCE HOPS
                    ↓
RETRIEVAL / TOOLS / QUEUE / ASYNC
                    ↓
         Recheck quality and cost
```

### Checklist

| Concept | Remember |
|---|---|
| P50/P95/P99 | Median and slower-tail experiences; segment by workload/tenant |
| SLO | Service-level objective: defined metric, target, workload, window |
| TTFT | Time to first token; distinguish first useful output and final completion |
| Tracing | Queue, network, retrieval, models, tool spans, repeated calls |
| Streaming | Earlier partial output; not necessarily less total computation |
| Parallelism | Overlap independent work; slowest necessary branch dominates |
| Hops | Remove/replace unnecessary sequential model calls |
| Retrieval/tools | Tune measured work with quality, freshness, access, deadlines intact |
| Queue | Wait time differs from processing; protect with capacity controls |
| Async | Task ID, durable state, progress/status, result delivery |

### Trigger → Concept

| Hear… | Think… |
|---|---|
| “Bad P99” | Tail traces and workload segments |
| “Independent APIs called one by one” | Parallel reads |
| “Model 2s, total 12s” | Other critical-path stages |
| “Long wait before output” | First useful output / streaming |
| “Many agent hops” | Reasoning-call necessity |
| “Slow at peak” | Queue wait and capacity saturation |
| “Minutes of work” | Async completion expectations |

### Do Not Confuse

1. **Average vs tail:** fast typical requests do not guarantee acceptable slow requests.
2. **TTFT vs completion:** output beginning is not a finished answer or action.
3. **Streaming vs speed:** partial delivery can improve perception without shortening execution.
4. **Async vs less work:** the client stops blocking while the task continues.

### Critical-Path Rules

Sequential stages add. Parallel branches overlap; do not sum all branch times as elapsed latency. Avoid double-counting nested spans. Inspect slow requests, not only aggregate dashboards.

Preserve ordering where results depend on one another. Parallel calls increase concurrent load. Do not reorder business writes merely to save time, remove required policy checks, or stream unconfirmed action success.

Optimize retrieval candidate counts and reranking against evidence quality. Cache only when permissions and freshness hold. For tool write timeouts, reconcile status before retry. For queues, use bounded waiting and clear overload behavior; more workers help only if the bottleneck can scale.

### 30-Second Answer

> “I’d define workload-specific first-output and completion targets, inspect P95/P99 traces, and find the critical path. I’d then stream safe output, parallelize independent work, reduce unnecessary model hops, and optimize measured retrieval, tool, or queue delays. For genuinely long tasks, I’d use asynchronous delivery. I’d verify quality, action safety, and cost after each change.”
