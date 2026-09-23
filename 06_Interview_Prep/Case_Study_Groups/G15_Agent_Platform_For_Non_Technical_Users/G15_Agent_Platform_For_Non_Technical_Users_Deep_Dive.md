# G15 — Agent Platform for Non-Technical Users: Deep Dive

> Read with the unchanged [source](G15_Agent_Platform_For_Non_Technical_Users.md). The [Main guide](G15_Agent_Platform_For_Non_Technical_Users_Main.md) is the interview path; the [Cheat Sheet](G15_Agent_Platform_For_Non_Technical_Users_Cheat_Sheet.md) is the recall card.

## 1. The contract between authoring and runtime

The source's `WorkflowSpec` is a versioned declaration with triggers, fixed steps, max steps and max cost. `Event` carries channel, event type, tenant, target entity, payload and raw reference. `Tool` registration declares typed arguments, scopes and whether it is destructive. A non-technical builder or eventual natural-language compiler produces a reviewable draft spec; the runtime does not execute free text as code. Runs pin a workflow version, so editing a spec cannot alter a run mid-flight.

The runnable project has no LLM. That is intentional for deterministic proof. A future LLM might propose values or produce a draft spec, but schema validation, policy and human promotion must remain deterministic. An open-ended planning loop would be a separate change, bounded by the same step, spend and authorization controls.

## 2. Routing and concurrency

Adapters normalize once at the edge. The router matches tenant, `LIVE` status and `(channel,event_type)` trigger; highest priority wins. It returns `no_trigger_match` when none qualifies. A target-entity lock then refuses a second active run with `entity_locked`, even if priorities are accidentally equal. Priority is a configuration choice; the lock is a safety invariant. In Cascade Robotics, ticket triage priority 10 beats a legacy tagger at priority 1 on the same webhook trigger. A production lock needs a distributed backing or database uniqueness rather than an in-process dict.

## 3. One execution loop and action-level idempotency

`run_workflow()` and `resume()` enter the same loop at `next_step_index`. After each completed step, the run checkpoints the next index. A crash after step 0 resumes at step 1, so step 0 is not deliberately re-run. At-least-once delivery can still replay an action around a crash, so its external side effect needs an idempotency key like `{run_id}:{step_name}` and a durable shared store. The same key must be passed to a provider when the provider supports it.

Check the action's applied key before authorization. The source found that a refund replay skipped the second refund but charged the spend budget again, causing a false cap denial. Idempotency must cover all side effects, including cost accounting and audit semantics, not just the visible API call. A replay of an already-applied action is a free no-op and may advance the checkpoint.

## 4. Guardrail order and the $500 story

`authorize_step()` returns `Decision(allowed, rule, reason)`. In order: deny if the tighter workflow/tenant step budget is exhausted; deny if the step's *real* cost exceeds the tighter spend cap; deny destructive writes in `SHADOW`; deny actions not yet `LIVE`; then require human approval unless the destructive tool is tenant-allow-listed for autonomy. Non-destructive work proceeds after budget checks. Deny overrides allow. The $500 Cascade refund under a $50 cap is refused rather than reduced; its autonomous status does not erase the cap or allow-list.

The first discovered bug used a nominal tool invocation fee to evaluate a $500 refund against a $5 cap, so it checked the wrong number. The fix reads `amount_usd` from the validated financial tool arguments. This distinguishes inference/tool operating cost from money moved on the customer's behalf. A 30-step cheap workflow trips a five-step cap; a single $500 refund trips a $50 spend cap. Neither should retry or silently clamp.

## 5. Promotion and negative evidence

The states are `DRAFT → TESTING → SHADOW → LIVE → AUTONOMOUS`; promotion moves one stage at a time, only by an approver/admin who is not the author. Testing uses historical input; shadow observes live traffic with writes mocked; live can require human approval per action; autonomous can skip approval only for tenant-allow-listed tools. The source demo has 21 deterministic tests covering wrong role, skipped stage, bad typed arguments, not-live action, cap denial, step limit, entity lock, crash resume and no duplicate effect. Those tests prove this engine's rules, not the behavior of an unbuilt planner.

## 6. Product and production gaps

Templates, plain-language run history, natural-language authoring, automatic retry scheduling, real connector secrets, output PII redaction, custom-tool sandboxing and gradual traffic split are incomplete or absent in the source. Production also needs durable run, lock and idempotency stores shared across workers, scoped connector credentials, observability and a tenant-level spending breaker. Keep the run trace understandable to the author: each allow/deny should have a rule name and plain reason. Build week one around a single safe workflow and negative guardrail proof before adding model planning or destructive actions.
