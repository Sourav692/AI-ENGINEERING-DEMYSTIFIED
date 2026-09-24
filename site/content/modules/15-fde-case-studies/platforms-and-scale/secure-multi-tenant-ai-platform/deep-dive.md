# G07 — Secure Multi-Tenant AI Platform: Deep Dive

The [Main guide](/modules/15-fde-case-studies/platforms-and-scale/secure-multi-tenant-ai-platform#main) is the spoken answer. This is technical backup for the unchanged [source study](/modules/15-fde-case-studies/platforms-and-scale/secure-multi-tenant-ai-platform#full-pack), especially §§3–14.

## 1. Immutable tenant context and authority

Validate token signature, audience, and expiry with the customer IdP before authorization. The tenant directory maps the verified principal to membership, allowed region, and deployment posture; customer-owned groups may be synced, so renamed groups and mapping drift need alerts. Just-in-time provisioning grants the minimum local role for that tenant. A request-body `tenant_id` is untrusted. Establish context once, make it immutable, and propagate it to services, database sessions, cache helpers, queue messages, vector filters, inference, and audit.

`Tenant(id, region, tier, key_ref, retention_policy)` owns placement and data policy. `Membership(user_id, tenant_id, role, status)` owns authority. `UsageLedger(tenant_id, period, tokens, requests, cost)` owns metering. `AuditEvent(tenant_id, actor, action, resource, decision)` makes the control provable. Writes use idempotency keys and optimistic concurrency. Model output is parsed into a typed schema and policy-checked before persistence.

## 2. Isolation that survives a missed check

The row, object, cache, queue, log, vector, and key layers enforce independently. Bind database row security to verified session context or physically partition; a query with no tenant predicate returns no data, rather than all data. Objects use tenant namespaces. Cache keys include tenant, permission signature, and source/policy version. Queue and dead-letter envelopes carry tenant context. Logs omit raw prompts and secrets. Vector chunks receive tenant metadata at ingest, queries compile a tenant filter, and a final check compares request and chunk tenant before prompt assembly. Tenant-scoped data keys reduce raw-storage compromise blast radius.

Three tenancy tiers trade cost for separation: shared rows with database enforcement (default), separate schema/namespace, and dedicated cluster/region/keys. Escalate on residency, strict latency, unacceptable contention, or a policy demanding harder separation, using documented thresholds rather than customer size alone. G01’s pre-filter plus authoritative post-check applies to tenant retrieval, but tenant isolation must extend to every non-retrieval path too.

## 3. Admission, fairness, and unit economics

The source’s exercise is **500 tenants, 50k active users, 200 QPS peak, 20× skew**. Average QPS per tenant is 0.4, which cannot size peak concurrency, retries, failover, and long-tail inference. At 10× the planning case is **5,000 tenants and 2,000 QPS**; expect cache churn, noisy neighbors, and more regional partitions before merely adding one bigger inference pool.

`C_tenant = C_fixed/N + C_usage + C_isolation`. Attribute tokens, storage, retrieval, egress, and reserved capacity per tenant. Enforce token, concurrency, burst, and monetary budgets before inference; a post-call bill is not a budget gate. Rate limit admission and use weighted fair queuing or tenant token buckets feeding shared workers. Premium reserved lanes protect contractual performance without forcing every tenant into a dedicated cluster. Quotas too tight create artificial failures; quotas too loose shift one tenant’s burst onto its neighbors.

For one high-usage tenant, segment by key, user, feature, time, prompt version, tokens/request, batch jobs, and agent steps. Determine whether this is healthy adoption, a loop, abuse, or missing quota. Support the first with capacity planning; throttle or pause the others, then add contract-aligned budgets and alerts.

## 4. Region, outage, and offboarding contracts

Define policy centrally and enforce regionally when feasible. A tenant’s residency rule includes data, prompts, outputs, traces, logs, backups, and derived indexes. Retention attaches to the tenant record or a versioned policy, not scattered service flags. A regional controller outage may leave safe reads serving from valid local policy and preloaded keys; sensitive changes fail closed, and queued work is reconciled after recovery. Decide RPO/RTO before replication and failover routing.

Export and delete require an inventory of every tenant-owned surface: relational rows, objects, embeddings, caches, queues, logs, and derived artifacts. A verified deletion job records completion and retention exceptions. Backup erasure follows restore and retention semantics; do not claim an immediate surgical delete where the backup design cannot provide one.

## 5. Cross-tenant retrieval incident: trace-first diagnosis

The [source §14](/modules/15-fde-case-studies/platforms-and-scale/secure-multi-tenant-ai-platform#full-pack) records an Acme answer citing a Globex renewal addendum. The request was `tenant_id=acme`; retrieved chunks included `doc_tenant_id=globex`. Filter version `v3` applied only `visibility in ['public','internal']`, omitting `tenant_id == 'acme'`. The ACL enforcer then skipped its check under `pre_authorized_connector_flag=true`. The response evaluator detected a critical violation **after `response_served=true`**. A rollout had reached **15% of Acme traffic**, so the live filter version and canary cohort matter.

Trace request → actual filter → chunk tenants → ACL decision → prompt/citation. Search all traces on `v3` for tenant mismatch; compare with v2 controls rather than relying on a UI reproduction. Contain by disabling v3, blocking any mismatched chunk before context, purging suspect answer caches, holding affected contract answers for human review, and notifying the customer. Root cause is two supposedly independent layers trusting a connector shortcut. Prevent with a non-bypassable server-side tenant predicate, hard post-retrieval invariant, removal of connector-level ACL bypass, negative release tests, and `cross_tenant_retrieval_count` by tenant, connector, and filter version. This is a confidentiality incident, not a hallucination.

## 6. Release evidence and operations

The negative suite tries wrong-tenant IDs, stale-cache hits, replayed tokens, malformed filters, namespace collisions, missing predicates, and cross-tenant vectors. One unexplained boundary failure halts promotion. Retain access logs with identity-derived context, role reviews, namespace checks, key-rotation procedures, and incident runbooks. Track per-tenant p95, quota rejects, cost band, isolation-test pass rate, confirmed incident count, and regional failover time separately.

Internal tenants establish tracing and scope → adversarial suite proves negative cases → a conservative shared-tenant canary tests real load → dedicated tier opens only under policy and economics. Roll back bad config by tenant and region without contaminating caches or data. Platform engineering owns runtime and predicates, security owns isolation gates, SRE owns failover, product owns tiering, and support owns first-response triage.
