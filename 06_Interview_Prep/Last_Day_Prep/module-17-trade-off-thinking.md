# Module 17 — Trade-Off Thinking

## CONCISE INTERVIEW MODULE

### 1. What the Interviewer Is Testing

- Can you justify a choice using the customer's requirements?
- Can you explain what improves, what gets worse, and how you would verify it?
- Can you consider a simpler alternative and adapt when priorities change?
- Can you preserve required boundaries while optimizing quality, latency, and cost?

### 2. Core Mental Model

> “I’m choosing X because of requirement Y. The trade-off is Z. I’d verify it using metric W.”

```text
Requirement → Options → Benefits and costs
                              ↓
                 Decision → Evidence → Revisit condition
```

```text
            QUALITY
            /     \
           /       \
        COST ─── LATENCY

Within required security, safety, and correctness boundaries
```

The triangle is a reasoning aid, not a law: some changes improve several dimensions together. State expected effects as hypotheses until measured.

### 3. Essential Concepts

#### 1. Hard Constraints vs Preferences — Know What Cannot Be Traded Away

Separate required permission, policy, residency, and action-correctness boundaries from negotiable latency, cost, or feature preferences.

> “Which conditions must always hold, and where can the customer accept a compromise?”

```text
Unauthorized data exposure → Not an acceptable speed trade
Long research completion  → May be acceptable if agreed
```

Clarify conflicts rather than silently dropping a requirement.

#### 2. Stronger vs Smaller Model — Match Capability to Need

A more capable model may improve difficult-task quality but increase cost or latency. A smaller model may meet simple-task requirements more efficiently.

> “I’d choose the least expensive path that meets the required quality for this task segment.”

```text
Simple task → Evaluate smaller model
Hard task   → Stronger model if measured benefit justifies it
```

Include fallback attempts and manual rework in the comparison, not only per-call price.

#### 3. More Retrieval — Balance Evidence Coverage and Noise

More candidates may improve recall but add reranking work, context noise, and latency. Better selection can sometimes improve quality and efficiency together.

> “I’d tune candidate count and context selection against recall and answer support rather than retrieve everything.”

```text
More candidates → Possible recall gain
                → More processing and irrelevant evidence
```

Permissions remain enforced regardless of retrieval size.

#### 4. More Agents or Critic Calls — Require Measured Value

Specialists or a critic can improve some tasks, but add model calls, handoffs, state, and failure paths.

> “I’d add the critic only if its improvement on important cases justifies the extra latency and cost.”

```text
Candidate with critic → Compare against simpler baseline
                         Task success / errors / latency / cost
```

Independent subtasks may run in parallel. Dependent reasoning hops still extend the critical path.

#### 5. Caching — Exchange Repeated Work for Freshness Management

Caching can reduce latency and cost. It introduces expiry, invalidation, access-scope, and source-version concerns.

> “I’d cache policy results within their freshness and permission boundaries, but confirm live order state when the action needs it.”

```text
Repeated policy lookup → Scoped valid cache may help
Current refund status → Freshness requirement decides reuse
```

Do not present cache hits as a benefit when reused results are incorrect or unauthorized.

#### 6. Autonomy vs Human Review — Balance Workload and Consequences

Automatic execution can reduce human work and waiting, but requires reliable policy, permissions, safe writes, and recovery. Review adds context checking but also delay and reviewer workload.

> “I’d agree on which action classes can execute automatically and which need review.”

```text
Agent recommends → Policy decides → Executor acts
                          ↓
                 Approval when required
```

Human approval is not permission to bypass other controls, and a confident model is not an authorization source.

#### 7. Sync vs Async — Match Interaction to Task Duration

Synchronous execution gives a direct result for short work. Async execution lets long tasks continue with status and results, but adds durable state and a different user interaction.

> “For work that takes minutes, I’d return a task ID and progress rather than hold an interactive request open.”

Async reduces client blocking; it does not necessarily shorten task completion or increase underlying processing capacity.

#### 8. Shared vs Isolated Resources — Balance Efficiency and Isolation

Shared infrastructure can use capacity efficiently but needs tenant scoping, fairness, and blast-radius controls. Dedicated resources may strengthen isolation but increase cost and operational effort.

> “I’d choose the isolation level from the tenant's data, performance, and operational requirements.”

Data isolation and resource fairness remain distinct concerns in either design.

#### 9. Reversibility and Evidence — Explain When You Would Change Your Mind

Prefer a choice you can measure and adjust when uncertainty is high. Define the signal that would justify a more complex alternative.

> “I’d start with one workflow; I’d introduce specialists if evaluation shows a clear task-success benefit.”

```text
Provisional choice → Observe metric → Threshold / requirement changes
                                             ↓
                                      Revisit architecture
```

### 4. Requirement → Component Reasoning

| Customer priority | Possible choice | Why | Trade-off / evidence |
|---|---|---|---|
| Lower simple-task cost | Evaluated model routing | Avoid unnecessary expensive calls | Check segment quality and fallback cost |
| Better evidence coverage | More candidates or hybrid retrieval | Improve retrieval recall | Measure noise, latency, answer support |
| Repeated safe questions | Scoped cache | Avoid repeated work | Verify freshness/access behavior |
| Complex independent subtasks | Specialist agents if justified | Separate or parallelize work | Measure coordination cost and outcome |
| High-impact actions | Policy + approval workflow | Control execution risk | Approval time and reviewer load |
| Long research task | Async job + durable state | Fit interaction to duration | Status/result delivery complexity |
| Strong tenant guarantees | Isolation + fairness controls | Protect data and service | Resource cost and operational effort |

**Support example:** cache eligible policy retrieval, use a sufficient model for simple questions, read live order data for refund decisions, and keep deterministic policy in code. Evaluate any added critic or specialist against resolved cases, latency, and cost—not just nicer wording.

### 5. Important Distinctions and Gotchas

1. **Possible benefit vs guaranteed benefit:** more agents, context, or model capability does not ensure better outcomes.
2. **Optimization vs boundary violation:** do not remove authorization or policy checks for speed.
3. **Cost/call vs cost/success:** retries and rework can erase savings.
4. **Async responsiveness vs faster completion:** acknowledging early changes the interaction, not necessarily the task duration.
5. **Decision vs permanent commitment:** name the evidence or changed requirement that would make you revisit the choice.

### 6. Trigger → Concept Table

| Hear… | Think… | Discuss… |
|---|---|---|
| “Critic adds 3s and 40% cost” | Marginal value | Critical-case gain vs operating targets |
| “Maximum recall, minimal latency” | Retrieval trade-off | Candidate count, search/rerank, quality threshold |
| “Smaller model slightly worse” | Sufficient quality | Task segments and acceptable quality floor |
| “Cache everything” | Freshness/access | Eligible reuse and invalidation |
| “Remove approvals to be faster” | Hard constraint | Customer policy and permitted action classes |
| “Why not a simpler design?” | Baseline comparison | Requirement gap and measured benefit |
| “Priority changed” | Revisit decision | New constraint and evidence |

### 7. Interview Phrases

> “I’m choosing X because of requirement Y; the main trade-off is Z.”

> “I’d compare this against the simpler baseline on successful outcomes, latency, and total task cost.”

> “That benefit is a hypothesis until we evaluate it on the relevant task segments.”

> “If the customer changes this constraint, I’d revisit the choice rather than defend the original design blindly.”

### 8. Practice Questions

1. A critic improves some answers but adds three seconds and 40% cost. What evidence determines whether to keep it?
2. The customer wants maximum retrieval recall and very low latency. What options and measurable compromises would you discuss?
3. A smaller model is slightly less accurate overall. When could you still choose it, and which segments matter?
4. Caching a tool result reduces latency. How do you determine whether the freshness and access risk is acceptable?
5. Explain why your refund architecture needs more than one simple model call, and identify any component you could remove if scope changes.

---

## ONE-PAGE MEMORY CARD — Trade-Off Thinking

**Core question:** Why this choice, what does it cost, and what evidence would change the decision?

### Recall Flow

```text
REQUIREMENT → OPTIONS → BENEFIT / COST
                              ↓
                 CHOICE → VERIFY → REVISIT
```

> “I’m choosing X because of requirement Y. The trade-off is Z. I’d verify it using W.”

### Checklist

| Choice | Potential benefit | Trade-off to check |
|---|---|---|
| Smaller sufficient model | Lower cost, possibly lower latency | Quality by task/risk segment; fallback and rework |
| More retrieval | Better evidence coverage | Noise, processing, context cost |
| Reranking / critic | Better selection or error detection | Extra calls, latency, measured value |
| More agents | Specialization or independent work | Handoffs, coordination, failure paths |
| Cache | Less repeated work | Freshness, access scope, invalidation |
| More autonomy | Less human work and waiting | Policy, safe writes, recovery, impact |
| Human approval | Contextual review | Delay, reviewer workload, durable state |
| Async | Less client blocking for long work | Status/result UX; task duration unchanged |
| Dedicated resources | Stronger isolation in some designs | Cost and operational effort |

### Trigger → Concept

| Hear… | Think… |
|---|---|
| “Extra quality at extra cost” | Marginal task-success gain |
| “Maximum recall, fastest answer” | Evidence vs critical-path budget |
| “Cache live data” | Required freshness and authorization |
| “Many agents” | Justified benefit vs simpler baseline |
| “Remove checks” | Non-negotiable boundaries |
| “Why this design?” | Requirement → choice → trade-off → verification |

### Do Not Confuse

1. **Expected vs measured:** quality/cost/latency effects are hypotheses until tested.
2. **Cheaper call vs cheaper outcome:** include failures, retries, escalation, and rework.
3. **Async vs faster task:** early acknowledgement does not shorten execution automatically.
4. **Preference vs hard constraint:** permission, customer policy, residency, and correct side effects cannot be silently dropped.

### Decision Rules

Start from the customer's priority and minimum acceptable quality. Compare a simple baseline with the proposed alternative on representative tasks and important risk segments. Discuss changes to latency, cost per successful task, evidence quality, failure behavior, and operational complexity.

More context or more agents can hurt performance; better selection or fewer redundant calls can improve several dimensions together. The quality–cost–latency triangle is a reminder to inspect interactions, not proof that every benefit requires a loss.

Keep action authority outside free-form reasoning: agent recommends → policy decides → executor acts. Approval remains where required. Caching must preserve access and freshness. Shared resources need both data isolation and capacity fairness.

State a revisit condition: a changed workload, unacceptable tail latency, insufficient task success, rising review burden, or stronger tenant requirements. Architecture choices should follow the evidence and current requirements.

### 30-Second Answer

> “I’d separate hard constraints from preferences, compare the simplest viable options, and choose based on the customer's priority. I’d explain what improves, what becomes more expensive or complex, and how we would verify the result. I’d measure successful outcomes, latency, and total task cost, preserve required controls, and revisit the choice if evidence or requirements change.”

## Sources (checked 27 Sep 2026)

- [Liu et al. 2023, Lost in the Middle: How Language Models Use Long Contexts (arXiv 2307.03172)](https://arxiv.org/abs/2307.03172) — extra context adds noise
- [Shi et al. 2023, Large Language Models Can Be Easily Distracted by Irrelevant Context (arXiv 2302.00093)](https://arxiv.org/abs/2302.00093) — extra context adds noise
- [Anthropic Engineering, How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — multi-agent overhead
- [Cemri et al. 2025, Why Do Multi-Agent LLM Systems Fail? (MAST, arXiv 2503.13657)](https://arxiv.org/abs/2503.13657) — multi-agent overhead
