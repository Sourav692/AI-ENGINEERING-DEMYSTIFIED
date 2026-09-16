# 11. Multi-Tenant SaaS Assistant
## What the diagram shows

This diagram shows a multi-tenant SaaS assistant where users from different tenants enter through a tenant gateway. Tenant context drives the policy layer, isolated indexes, admin console, shared LLM gateway, and audit store.

The main interview point is tenant isolation. A SaaS assistant must prevent data leakage between customers while still sharing infrastructure efficiently.

## How to explain it in an interview

A strong spoken explanation could be:

> I would design tenant isolation as a first-class requirement. Every request is resolved to a tenant context before retrieval, tool use, caching, logging, or generation. Depending on risk, we can use physically isolated indexes per tenant or logically isolated indexes with strong metadata filters. The shared LLM gateway must not mix tenant prompts, cache entries, or logs. Admin controls allow tenant-specific policies, connectors, retention settings, and audit exports.

## Key trade-offs

- **Isolated indexes vs shared index:** Isolated indexes improve separation but cost more. Shared indexes are efficient but require strict metadata filtering.
- **Shared LLM gateway vs tenant-specific deployment:** Shared gateway reduces cost; tenant-specific deployment may be required for regulated customers.
- **Central admin console vs tenant autonomy:** Central management is simpler; tenant-specific controls improve enterprise fit.
- **Caching efficiency vs leakage risk:** Shared caches are risky unless tenant and permission context are part of cache keys.

## Failure modes

- Tenant resolver maps a user to the wrong tenant.
- Shared vector index leaks chunks through missing metadata filters.
- Cache returns an answer generated for another tenant.
- Admin console policy change does not propagate to runtime.
- Audit store mixes tenant records without proper access control.
- LLM gateway logs tenant-sensitive prompts in a shared location.
- Tool calls execute against the wrong tenant workspace.

## Security concerns

- Enforce tenant ID at gateway, retrieval, cache, tool, and audit layers.
- Include tenant context in every trace and log entry.
- Support tenant-specific data retention and deletion policies.
- Isolate admin privileges by tenant.
- Add cross-tenant leakage tests to the regression suite.
- Avoid shared prompt or response caches unless safely scoped.

## What a weak candidate misses

A weak candidate says: “Add tenant ID to the database.” That is not enough. Multi-tenant safety must be enforced across indexes, caches, prompts, tools, logs, admin settings, and audit exports.

## What a strong candidate says

A strong candidate discusses tenant resolution, isolated or filtered indexes, tenant-scoped cache keys, policy enforcement, admin configuration, audit isolation, and cross-tenant red-team tests.

## Visual improvement suggestion

Show separate tenant lanes:

- **Tenant A Lane:** User, Tenant Context, Index A, Policies
- **Tenant B Lane:** User, Tenant Context, Index B, Policies
- **Shared Services:** LLM Gateway, Observability, Admin Console
- **Isolation Boundary:** Clear line showing where tenant data must not cross

Add warning labels for cache, logs, and tool calls as common leakage points.
