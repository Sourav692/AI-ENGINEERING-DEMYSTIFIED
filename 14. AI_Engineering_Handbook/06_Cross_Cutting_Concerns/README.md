# Module 06 · Cross-Cutting Concerns

> **Level** 🟠 Scale, Security, Operations · **Docs** 7 · **Time** ~3.5 h
> **Prerequisites:** Modules 03, 04, 05

Levels 1 and 2 built systems that are correct for one customer. This module is what has to be true for those systems to survive many tenants, many documents and many months: identity and secrets in front of the authorisation logic; observability that a customer's stack can read and that drives alerts; caching and streaming without correctness surprises; CI/CD that catches regressions you did not cause; prompt injection and egress for systems that act; structured data alongside documents; and what breaks first at twenty million documents. None of it needs a codebase. All of it needs to be raised unprompted.

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [Identity, Secrets, Per-Tenant Keys and Fair Sharing](01_Identity_Secrets_Tenant_Fairness.md) | SSO/OIDC as a verification problem; secrets by reference with envelope encryption; per-tenant keys and blast radius; rate limits vs fair queues | 25 min |
| 2 | [Observability Standards and Failure Patterns](02_Observability_Standards_Failure_Patterns.md) | OpenTelemetry-style spans; per-tenant dashboards; drift and cost attribution; backup providers; bulkheads; the kill switch | 30 min |
| 3 | [Caching, Streaming, CI/CD Rigor and Build vs Buy](03_Caching_Streaming_CICD_BuildVsBuy.md) | Semantic cache correctness risk; streaming after the refusal decision; nightly runs for provider drift; A/B with power; prompt unit tests; the one build-vs-buy question | 30 min |
| 4 | [Prompt Injection, Egress and Tenancy](04_Prompt_Injection_Egress_Tenancy.md) | Data is not instructions; the schema as firewall; destination allow-lists; three tenancy levels and enforcement in the data layer | 30 min |
| 5 | [Structured Data, Routers and Connectors](05_Structured_Data_Routers_Connectors.md) | Why search fails on counts; the intent router; fixed operations over NL-to-query; permissions on the structured path; connector registries | 25 min |
| 6 | [Scaling to Twenty Million Documents](06_Scaling_To_20M_Documents.md) | Three scaling problems; what breaks first; ingestion arithmetic; filtered ANN; ACL free at scale; p50 vs tail; chunking by format; parent-child | 50 min |
| 7 | [Consolidated Quick Reference](07_Consolidated_Quick_Reference.md) | The nine cross-cutting topics as templates, red flags and answer scripts — the revision artefact | reference |

## How this module is used

Every whiteboard script in Module 09 has a Step 5 — *cross-cutting, failure, scale* — that must be raised unprompted. This module is the content of that step. Each document ends with the sentence that carries it; the quick reference collects them.

## Checkpoint

You are ready for Module 07 when you can:

- Explain why authorisation assumes identity and what three checks sit in front of it.
- Distinguish circuit breaker, bulkhead, backup provider and kill switch by the failure each addresses.
- State the semantic-cache correctness risk and the safest constraint on it.
- Give the three prompt-injection fixes for an acting agent and the egress allow-list.
- Say which scaling mechanisms are free at 20M documents and which need new engineering.

**Next →** [Module 07 · Multi-Agent Systems](../07_Multi_Agent_Systems/README.md)
