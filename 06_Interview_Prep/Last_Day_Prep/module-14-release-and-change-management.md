# Module 14 — Release & Change Management

## CONCISE INTERVIEW MODULE

### 1. What the Interviewer Is Testing

- Can you release AI changes using evidence rather than a few attractive examples?
- Can you distinguish shadow evaluation from real user exposure?
- Can you identify which artifacts must be versioned together?
- Can you detect regressions and stop or reverse the change?

### 2. Core Mental Model

```text
Version candidate → Offline evaluation → Release gate
                                              ↓
                   Shadow and/or scoped canary
                                              ↓
                       Observe → Expand / stop / rollback
```

Use a rollout path appropriate to the change. Shadow and canary serve different purposes; both are not mandatory for every release.

### 3. Essential Concepts

#### 1. Version the Behavior — More Than the Model

Track prompts, model/configuration, tools and schemas, routing, retrieval settings, corpus/index versions where feasible, policy, and evaluation artifacts.

> “I’d record the versions that produced each task's behavior so we can reproduce and compare changes.”

```text
Release identity → Prompt + model + tools + retrieval + policy
```

Include workflow/state-schema compatibility for long-running tasks. A model rollback alone may not restore previous behavior.

#### 2. Offline Evaluation — Compare Before Exposure

Evaluate representative held-out normal, edge, failure, and high-risk cases against the baseline. Check task success, constraints, latency, and cost.

> “Improving twenty examples is encouraging, but I’d check coverage and critical regressions before release.”

#### 3. Release Gates — Define Pass/Fail Criteria

Agree on acceptable quality, prohibited failures, operational limits, and required evidence before evaluating the candidate.

```text
Quality + policy + task success + latency/cost criteria
                         ↓
                 Pass / investigate / reject
```

> “A better average should not override a serious permission or action-safety regression.”

#### 4. Shadow Traffic — Evaluate Without User-Facing Actions

Run the candidate alongside the current path for comparison while the current path serves the user. Use sandboxed or read-only operation paths for candidate actions.

```text
Request ─┬→ Current → User / real execution
         └→ Candidate → Evaluation only
```

> “The shadow candidate must not issue a second refund or change production state.”

Shadow calls can still incur cost, load, and data exposure. Control access and resource budgets, and note that shadow results may not capture user reactions to candidate output.

#### 5. Canary — Expose a Limited Real Cohort

Route a small eligible cohort to the candidate, then monitor real quality, task outcomes, errors, latency, and cost against the baseline.

```text
Eligible users / tenants
       ↓
Small candidate cohort → Observe → Expand or revert
```

> “I’d define the cohort, observation window, stop criteria, and owner before enabling it.”

Use consistent assignment where conversation/workflow continuity matters. A tiny cohort may not cover rare failures or all tenant types.

#### 6. Feature Flags — Control Scope

Enable behavior by tenant, cohort, capability, or version. Flags can support limited exposure and fast disabling without a full deployment.

> “For two pilot enterprises, I’d scope the flag to those tenants and track their outcomes separately.”

Flags must cover the actual execution path, not only the UI. Avoid silently changing a pending approval's action semantics.

#### 7. Rollback — Restore a Known Compatible Version

Keep a tested rollback path and know what happens to active workflows, state changes, and already completed business actions.

```text
Regression → Stop expansion → Route new work to baseline
                                      ↓
                         Handle active tasks explicitly
```

> “Rollback restores software behavior; completed refunds need separate business reconciliation.”

#### 8. Kill Switch — Stop Execution Quickly

Disable the affected action, tool, tenant, or agent capability at a trusted boundary. Keep safe unaffected functions where possible.

> “If refund execution is unsafe, I’d disable that capability while preserving safe assistance.”

A kill switch stops permitted new execution according to its scope; it cannot undo a submitted payment.

#### 9. Monitor and Feed Back — Release Continues After Deployment

Track candidate/baseline versions, segment outcomes, errors, escalations, delayed results, and customer feedback. Add discovered failures to regression coverage.

> “I’d expand only after the observed cohort meets the agreed criteria.”

### 4. Requirement → Component Reasoning

| Requirement | Pattern / component | Why | Trade-off |
|---|---|---|---|
| Explain behavior changes | Versioned release artifacts | Reproduce and compare | Artifact coordination |
| Prevent known regressions | Offline evaluation + gate | Check before exposure | Coverage/label effort |
| Compare on real requests safely | Shadow path with isolated writes | Observe candidate behavior | Extra cost and incomplete user feedback |
| Limit real exposure | Canary routing | Control rollout impact | Cohort bias and small samples |
| Pilot selected tenants | Feature flags | Scope behavior explicitly | Configuration complexity |
| Recover from regression | Compatible rollback + kill switch | Restore/stop behavior | In-flight state and actions |

**Support example:** evaluate a new refund prompt and tool schema offline, shadow without payment writes, canary eligible pilot tenants, and monitor confirmed refunds, approval compliance, errors, latency, and cost. Keep the previous version and an execution switch available.

### 5. Important Distinctions and Gotchas

1. **Shadow vs canary:** evaluation-only candidate vs candidate serving real users and actions.
2. **Deploy vs release:** code can be present before a flag exposes behavior.
3. **Rollback vs undo:** reverting software does not reverse external business effects.
4. **Flag vs complete isolation:** ensure tools, workers, and resume paths follow the intended version/scope.
5. **Good small sample vs release evidence:** include important segments and rare/high-impact failure cases.

### 6. Trigger → Concept Table

| Hear… | Think… | Discuss… |
|---|---|---|
| “New prompt better on 20 examples” | Release evidence | Coverage, baseline, held-out failures |
| “Compare without affecting users” | Shadow | No duplicate writes, budget/data scope |
| “Only two enterprises first” | Scoped canary/flag | Cohort, continuity, stop criteria |
| “Quality drops after release” | Rollback | Version comparison, known baseline |
| “Unsafe refunds now” | Kill switch | Stop affected execution |
| “Tasks started yesterday” | Version compatibility | Active state and approval semantics |

### 7. Interview Phrases

> “I’d version the behavior, not just the model name.”

> “Shadow compares without candidate business writes; canary tests limited real exposure.”

> “I’d agree on stop criteria and a rollback path before expanding the cohort.”

> “Completed actions require reconciliation even if we roll the software back.”

### 8. Practice Questions

1. A prompt improves twenty examples. What evidence and gates would you require before exposure?
2. Design shadow evaluation for a refund agent without duplicate payments.
3. Release a new workflow to two tenants while preserving conversation continuity.
4. Which artifacts must be versioned to explain a changed policy answer or refund action?
5. A rollout fails while older approvals remain pending. How do flags, rollback, and active-task handling interact?

---

## ONE-PAGE MEMORY CARD — Release & Change Management

**Core question:** How do we expose a candidate gradually, detect regressions, and retain control over behavior and actions?

### Recall Flow

```text
VERSION → EVALUATE → GATE
                       ↓
          SHADOW and/or CANARY
                       ↓
           MONITOR → EXPAND / STOP / ROLLBACK
```

### Checklist

| Concept | Remember |
|---|---|
| Versioning | Prompt, model/config, tools/schema, routing, retrieval, policy, eval artifacts |
| Compatibility | Active workflow state and pending approval/action semantics |
| Offline gate | Held-out coverage, task success, policy, quality, latency, cost |
| Shadow | Current serves users; candidate evaluated without production writes |
| Canary | Limited real cohort with baseline comparison and defined stop rules |
| Flags | Scope by tenant/cohort/capability; cover workers and execution too |
| Rollback | Known compatible baseline; handle active tasks explicitly |
| Kill switch | Stop affected capability at trusted execution boundary |
| Monitoring | Versions, segments, delayed outcomes, failures, escalations, cost/latency |

### Trigger → Concept

| Hear… | Think… |
|---|---|
| “Twenty better examples” | Broader held-out evidence and gates |
| “Compare invisibly” | Shadow with isolated/sandboxed writes |
| “Two pilot tenants” | Scoped flag/canary |
| “Regression after rollout” | Stop expansion, compare versions, rollback |
| “Unsafe action” | Disable execution with kill switch |
| “Long tasks from old version” | State/behavior compatibility |

### Do Not Confuse

1. **Shadow vs canary:** evaluation-only vs real candidate exposure.
2. **Deployment vs release:** code present vs behavior enabled.
3. **Rollback vs undo:** software routing changes do not reverse payments.
4. **Feature flag vs boundary enforcement:** UI flags alone cannot stop a worker's write.

### Rollout Rules

Define cohort, metrics, observation window, stop/expand criteria, and owner before exposure. Monitor critical segments, not only averages. Candidate shadow execution must not duplicate business actions; it can still add model/tool load and data exposure. Keep budgets and access restrictions in place.

Prefer stable cohort assignment when conversations or workflows need continuity. A small cohort cannot prove all rare cases safe; combine offline coverage with production evidence. Keep versions attached to tasks so pending approvals do not change meaning unexpectedly.

On regression, stop expansion, disable dangerous execution where needed, and restore a compatible baseline for new work. Reconcile already submitted actions and decide how active tasks resume. Feed discovered failures into regression cases.

### 30-Second Answer

> “I’d version all behavior-changing artifacts, evaluate against the baseline, and apply agreed quality, policy, latency, and cost gates. I’d use shadow where comparison must avoid real actions and canary for controlled live exposure. Flags would scope the rollout, versioned telemetry would guide expansion, and tested rollback and execution switches would control regressions and in-flight work.”
