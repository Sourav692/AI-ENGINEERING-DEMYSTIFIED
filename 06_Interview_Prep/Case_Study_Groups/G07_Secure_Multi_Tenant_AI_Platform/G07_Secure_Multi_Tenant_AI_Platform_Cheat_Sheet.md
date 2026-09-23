# G07 — Secure Multi-Tenant AI Platform: Cheat Sheet

Use the [Main guide](G07_Secure_Multi_Tenant_AI_Platform_Main.md) for the spoken design, the [Deep Dive](G07_Secure_Multi_Tenant_AI_Platform_Deep_Dive.md) for mechanics, and the unchanged [source](G07_Secure_Multi_Tenant_AI_Platform.md) for the full case.

## One sentence

**Derive tenant context from verified identity once; enforce it independently everywhere, and meter before LLM inference.**

## Ask first

Data classes? Residency for data/logs/backups? Shared versus dedicated exceptions? Peak skew and per-tenant SLO? Federated identity and keys? Contractual budgets? Verified export/deletion? Audit evidence?

## Flow

**Verified IdP → tenant directory → immutable context → policy + allowed region → pre-call quota → tenant-scoped stores/retrieval → chunk-tenant post-check → LLM inference → typed output check → audit/usage.**

**Agent role:** this platform hosts assistants or bounded agents; their plans, prompts, tools, caches, and traces inherit tenant context. Model output cannot establish identity or authority.

## Seven layers

**Row · object · cache · queue · log · vector index · key.** The store refuses an unscoped read. Vector scoping happens at ingest, query, and final context assembly. Cache keys include tenant + permission signature + version.

## Numbers and trade-off

**Illustrative sizing:** 500 tenants, 50k active users, 200 QPS peak, 20× skew; mean 0.4 QPS/tenant hides concentration. `C_tenant = C_fixed/N + C_usage + C_isolation`. Shared enforced rows by default → separate namespace → dedicated region/cluster/keys when risk, residency, SLO, or contention justifies it.

## Failures

| Trigger | Default |
|---|---|
| Missing predicate or mismatched retrieved chunk | Fail closed, audit, stop path. |
| Cross-tenant cache hit | Security incident; disable, purge, inspect served window. |
| One tenant over quota | Degrade that tenant; fair queue protects others. |
| Policy/key unavailable | Block protected operation. |
| Regional control outage | Safe local-policy reads only; queue or block sensitive changes. |

## Leak drill

Acme request cited Globex document: v3 filter dropped tenant equality and connector flag skipped ACL. Roll back v3, purge caches, search mismatch traces, notify customer; add non-bypassable predicate, post-check, and negative release gate. **It is an isolation failure, not a model hallucination.**

## Release and close

Internal tenants → adversarial isolation suite → small shared tenants → policy-justified dedicated tier. Any unexplained boundary failure blocks promotion; confirmed cross-tenant incident target is zero. Track p95 and cost **per tenant**.

“The control plane decides tenant policy, region, tier, and budgets; the data plane enforces scope at every store and inference boundary.”
