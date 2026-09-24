# G15 — Agent Platform for Non-Technical Users: Cheat Sheet

[Main](/modules/15-fde-case-studies/platforms-and-scale/agent-platform-for-non-technical-users#main) · [Deep Dive](/modules/15-fde-case-studies/platforms-and-scale/agent-platform-for-non-technical-users#deep-dive) · [Unchanged source](/modules/15-fde-case-studies/platforms-and-scale/agent-platform-for-non-technical-users#full-pack)

## Ask first

How non-technical is authoring? Which channels? Read-only or destructive actions? Blast radius? Multi-tenant from day one?

## Whiteboard path

`Channel adapter → canonical tenant Event → live-trigger priority → entity lock → pinned-spec orchestrator → typed args → action idempotency → guardrail / approval → scoped tool → checkpoint / trace`

The demonstrated engine has **no LLM**. A future model proposes values or a draft spec; code and humans authorize actions.

## Five rules

- Priority chooses which workflow **should** run; a lock stops two that **can** collide.
- Resume and fresh execution share one loop at `next_step_index`.
- Key idempotency on `{run_id}:{step_name}` and check it before authorization or billing.
- Guardrail denies in order: step cap, real-dollar spend cap, shadow, not-live, missing destructive-action authority.
- Promote `DRAFT → TESTING → SHADOW → LIVE → AUTONOMOUS`, one step at a time, never self-approved.

## Failure story

$500 refund, $50 tenant cap: refuse, never clamp. Wrong-cost bug checked a nominal API fee; replay bug charged the cap again despite no second refund. Correct the amount and place idempotency before authorization. The source demo has 21 deterministic tests; in-process stores still need durable shared replacements for production.

**60-second close:** “Non-technical intent becomes a reviewable spec. Deterministic routing, guardrails, idempotency and checkpointing decide whether a real action can run once and recover safely; the model never grants itself authority.”
