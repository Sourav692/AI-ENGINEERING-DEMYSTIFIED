# Configurable Platform for Customer-Specific Workflows - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- Which differences recur across customers, and which are genuine one-offs? That separates a platform capability from an exception path.
- Do variations stop at fields, approvals, branding, and integrations, or do they extend into logic and lifecycle states?
- Who authors configuration — internal engineers, customer admins, or a mixed model with vendor approval before production?
- Which integrations are non-negotiable, and does an adapter failure block a transition or degrade gracefully?
- What upgrade guarantee do customers expect: must configs survive core releases untouched?
- Where is the custom-code security boundary — inside the trusted core, in a sandbox, or only through approved integration points?
- What is the time-to-configure target, since hours implies self-service tooling and a week tolerates manual review?
- What happens when a workflow is misconfigured, and is a guaranteed fallback approval path required?

## Strong functional requirements
- Support the core workflow: ten customers vary fields, approvals, branding, and integrations on one shared platform without forking the codebase.
- Run a stable workflow engine executing the same core lifecycle for every customer, on one release train.
- Express variation declaratively through schemas, rules, and UI metadata so most customization never touches code.
- Provide an adapter interface so external systems connect without rewriting the engine.
- Version and validate every configuration so changes can be reviewed, tested, and rolled back.
- Supply migration and rollback tooling so a version change never strands a customer on an incompatible config.

## Strong non-functional requirements
- Latency: partition the budget — saving feels interactive, validation preview tolerates delay, full deployment may be slower if reliable.
- Availability: at roughly 1,000 configuration versions a day with a 3x peak, validation and deployment must not share a synchronous path.
- Security: arbitrary code is off by default; adapters and secrets are scoped per tenant; validation rules are themselves checked for denial-of-service risk.
- Compliance: a durable trail of who published what, what changed, which approval gate was crossed, and which version went live.
- Reliability: configuration isolation, so one tenant's settings or test changes cannot alter another tenant's runtime behavior.
- Cost: measure cost per validated version and activated template, including the support burden a flexible primitive creates.

## Architecture explanation
- The control plane owns configuration truth; the data plane executes workflows. Keeping them apart is what prevents ten forks.
- The workflow runtime executes instances, step transitions, timers, and retries identically for every tenant.
- The configuration registry is the system of record for immutable, published config versions and their release metadata.
- The schema and rule validator runs synchronously on save and publish, checking syntax, semantic constraints, permissions, and compatibility.
- The UI renderer generates tenant-specific forms, labels, and layouts from approved config, holding nothing beyond a cache.
- The integration adapter SDK gives one standard interface for CRM, ERP, ticketing, and webhook connectors, with credentials referenced per tenant.
- A feature flag service gates rollout by tenant, cohort, or percentage, and a sandbox runs the few approved extensions under hard limits.
- A migration service rewrites older configs into new schema versions, and a tenant test harness replays tenant-specific contract tests as a release gate.

## Data model / integration assumptions
- WorkflowTemplate(id, engine_version, schema); TenantConfig(tenant_id, template_id, version, values); AdapterDefinition(name, contract_version, permissions); ConfigDeployment(tenant_id, version, state).
- Assume ConfigDeployment is the deployment ledger and the source of truth for draft, validated, deployed, rolled_back, and failed.
- Assume rollback creates a new deployment state rather than mutating the old record, so history stays reconstructable.
- Assume every write carries an expected version, so two operators cannot race and silently overwrite each other's change.
- Assume every validation, deployment, adapter test, and rollback is tagged with tenant, config version, request ID, and idempotency key.

## Red-team risks
- infinite approval loop, adapter contract drift, upgrade breaking old field mappings, untested flag combinations, sandbox escape
- A cyclic approval graph that loops at runtime, which is deterministic harm rather than a transient fault.
- Adapter contract drift, where a downstream service changes a field or response shape and every tenant using it breaks at once.
- A tenant upgrade breaking old field mappings, stranding integrations that still reference the previous version.
- Untested feature-flag combinations, where two individually safe toggles produce a bad emergent path.
- Sandbox escape from customer-defined logic, which is why arbitrary code is denied by default rather than merely reviewed.

## Rollout plan
- Week 0-1: identify which differences recur, who owns configuration, and where the custom-code boundary sits.
- Week 1-2: prove one recurring pattern can be described in shared primitives rather than a one-off fork.
- Week 2-3: hold the gate until the team agrees the recurring pattern is stable enough to encode as a platform capability.
- Week 3-4: let the first customer admin configure their workflow and complete a pilot run through the real support channel.
- Week 5: confirm the customer accepts the support model and the rollback procedure before widening.
- Week 6-8: instrument baselines for launch speed, defect rate, and validation failures before expanding scope.
- After pilot: expand only if configuration is demonstrably reducing custom work rather than creating hidden rework.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Fork count | The platform stayed one product rather than ten | Zero irremovable customer-specific branches | Architecture review and repo analysis |
| Percentage handled by configuration | Variation lands in config, not code | High and rising per onboarding | Change-request classification tags |
| Time to launch a customer | Onboarding is a platform capability, not a project | Falling across successive tenants | Release tracking timestamps |
| Config validation failure rate | Authoring tools are usable and guardrails work | Stable; spikes signal confusing primitives | Config service logs |
| Upgrade time per tenant | Backward compatibility is real | No bespoke work to move a tenant forward | Release and migration records |
| Tenant incident rate | One bad config does not spread | Isolated per tenant, separate from platform outages | Incident management system |

## Weak answer
I would build a flexible workflow system with configurable forms, approvals, themes, and API hooks. This is weak because flexibility without governance becomes fragmentation — it never says who may author configuration, what survives an upgrade, or where custom code stops.

## Average answer
I would keep a shared engine and move customer differences into versioned configuration, with validation before publish and an adapter layer for integrations. This is better, but still incomplete because it does not decide which differences deserve to become platform primitives, does not bound what validation rules may cost, and has no story for a tenant stranded on an old schema.

## Strong answer
I would separate the requested feature, configuration, from the business result, which is serving customer-specific workflows without fragmenting the product into ten incompatible forks. The outcome has to be testable as safe, versioned, and supportable, and the metric I would hold myself to is how often a new customer variation lands without a fork, a hotfix, or a support escalation. Architecturally that means a stable engine on one release train, declarative schemas for most variation, an adapter interface for integrations, immutable versioned configs with validation before publish, and a narrow sandbox only where declarative configuration genuinely runs out. Arbitrary code is denied by default. I would prove one recurring pattern in shared primitives first, then let a real customer admin configure and pilot it before expanding.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | "Make it flexible" | Names shared core and config | Feature separated from outcome; fork-free variation as the measurable result |
| Requirements | Lists configurable fields | Adds versioning and validation | Recurring versus one-off, authorship model, upgrade promise, custom-code boundary |
| Architecture | One engine plus settings | Registry, validator, adapters | Control/data plane split, sandbox, flags, migration service, tenant test harness |
| Data/integration | Mentions a config table | Names templates and configs | Deployment ledger, rollback as new state, expected-version writes, tagged telemetry |
| Evaluation | "Customers are happy" | Tracks incidents | Fork count, share handled by config, launch time, upgrade time per tenant |
| Safety/security | "Admins are trusted" | Adds tenant separation | Code denied by default, per-tenant secrets, rule DoS validation, publisher audit |
| Rollout | Onboard all ten | Pilot one customer | One recurring pattern first, real admin pilot, baselines before scope expansion |
| Communication | Lists features | Clear but generic | Leads with fragmentation risk, names the non-goals, closes with the go/no-go gate |

## Final 2-minute spoken answer
I would not start with the feature list. Everyone agrees on the headline request and disagrees on everything underneath it, so my first job is to separate the requested feature, configuration, from the business result: serving ten customers without fragmenting the product into ten incompatible forks. I would make that outcome testable in three words. Safe, meaning no change bypasses authorization or creates unreviewed runtime behavior. Versioned, meaning every customer knows which definition is active and what changed. Supportable, meaning someone can diagnose an issue and roll a bad configuration back. The metric I would hold myself to is how often a new customer variation goes live without a fork, a hotfix, or a support escalation — not a vanity count of configurable fields. The first design fork is which differences actually recur, because a recurring approval-chain difference deserves to become a platform capability while one seasonal override belongs in an exception path. Architecturally that means one stable engine on a single release train, declarative schemas carrying most variation, an adapter interface for integrations, immutable versioned configs validated before publish, and a narrow sandbox only where declarative config runs out. Arbitrary code is denied by default, adapters and secrets are scoped per tenant, and validation rules are themselves checked for resource exhaustion. The named failure is an infinite approval loop, which fails closed for that version rather than continuing. I would prove one recurring pattern first, then pilot with a real customer admin.
