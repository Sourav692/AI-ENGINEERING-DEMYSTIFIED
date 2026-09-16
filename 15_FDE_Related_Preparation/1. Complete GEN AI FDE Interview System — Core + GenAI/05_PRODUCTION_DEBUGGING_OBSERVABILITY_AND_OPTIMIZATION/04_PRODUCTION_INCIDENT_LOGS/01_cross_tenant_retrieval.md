# Incident 1: Cross-Tenant Retrieval Leak Through a Missing Metadata Filter

## Scenario

Acme uses an enterprise support copilot to answer questions from internal support agents about customer contracts, escalation policies, and product entitlements. The assistant is multi-tenant: Acme support agents should only retrieve Acme-owned documents, even though the vector database physically stores chunks from several enterprise customers in the same collection.

On 2026-07-08, Acme’s support lead reported that the assistant cited a renewal clause that did not exist in Acme’s contract. The answer looked professional, cited a paragraph, and used the correct support tone, but the cited language belonged to another customer, Globex. This is a high-severity incident because the answer exposed another tenant’s contractual terms and could cause both privacy and commercial harm.

The incident is useful for GenAI FDE interviews because it tests whether the candidate debugs beyond “retrieval quality.” The real issue is the intersection of retrieval, metadata filtering, ACL enforcement, observability, and rollout safety.

## User-Visible Symptom

A support agent asked: “Can Acme customers receive premium onboarding under the 2026 renewal terms?” The assistant answered yes and cited a “Premium Success Addendum.” Acme’s contract did not contain this addendum. The support agent escalated because the cited paragraph referenced “Globex Strategic Renewal 2026.”

## System Context

The system uses an authenticated RAG pipeline: UI → API gateway → tenant resolver → query rewriting → vector retrieval → metadata filter → ACL service → reranker → citation assembler → LLM gateway → response evaluator. The vector database stores chunks from multiple tenants in a shared collection with fields such as `tenant_id`, `doc_tenant_id`, `visibility`, `source_connector`, `acl_hash`, and `metadata_filter_version`.

The intended safety invariant is simple: `tenant_id` on the request must match `doc_tenant_id` on every retrieved chunk, and the ACL service must authorize each chunk before it reaches the prompt context.

## Production Telemetry

```text
2026-07-08T09:12:44.129Z level=warn service=rag-api env=prod region=eu-central-1
  trace_id=trc_7f91c2 request_id=req_acme_88421 query_id=q_20260708_091244_19
  user_id=u_acme_support_044 tenant_id=acme user_role=support_agent
  workflow=contract_entitlement_answer retriever_version=2026-07-07
  metadata_filter_version=v3 filter_expression="visibility in ['public','internal']"
  expected_filter_expression="tenant_id == 'acme' AND visibility in ['public','internal']"

2026-07-08T09:12:44.388Z level=info service=vector-retriever
  trace_id=trc_7f91c2 collection=enterprise_contract_chunks index=contracts_hnsw_v22
  retrieval_k=12 returned_k=12 top_score=0.81
  retrieved_chunk_ids=[chk_globex_9921,chk_acme_1710,chk_acme_1709,chk_globex_9922]
  retrieved_doc_ids=[doc_globex_renewal_2026,doc_acme_msa_2025]
  doc_tenant_ids=[globex,acme,acme,globex]

2026-07-08T09:12:44.421Z level=error service=acl-enforcer
  trace_id=trc_7f91c2 acl_check=skipped reason="pre_authorized_connector_flag=true"
  connector=sharepoint connector_scope=tenant_shared acl_cache_key=acl:v2:sharepoint:contracts
  request_tenant_id=acme doc_tenant_id=globex policy_decision=not_evaluated

2026-07-08T09:12:45.221Z level=error service=response-evaluator
  trace_id=trc_7f91c2 eval=tenant_isolation_violation severity=critical
  response_served=true citation_doc_id=doc_globex_renewal_2026 citation_chunk_id=chk_globex_9921
  tenant_id=acme doc_tenant_id=globex human_review=false
```

## What Changed Recently

A retrieval deploy on 2026-07-07 introduced `metadata_filter_version=v3` to support global product documentation. The new filter builder treated connector-level “pre-authorized” documents as safe and omitted the tenant equality predicate for one SharePoint collection. The rollout was enabled for 15% of Acme traffic on 2026-07-08 at 08:45.

## Root Cause

The metadata filter builder dropped the hard tenant predicate when `pre_authorized_connector_flag=true`. The ACL service then skipped chunk-level checks because it incorrectly trusted the connector-level scope. This allowed Globex chunks to enter Acme’s prompt context and be cited.

## Debugging Path

A strong engineer starts from a known bad answer and opens the full trace. They compare `tenant_id` from the request with `doc_tenant_id` from retrieved chunks, verify the actual filter expression used by the retriever, and inspect whether ACL was evaluated per chunk. They then query all traces using `metadata_filter_version=v3` and look for `tenant_id != doc_tenant_id`. Finally, they compare the canary cohort against the control cohort running `metadata_filter_version=v2`.

The key debugging move is not to re-run the same question in the UI. The UI might not reproduce the exact canary route, cache state, or retrieval ordering. The correct path is trace-first: request → filter → retrieved chunks → ACL decision → prompt context → citation.

## Fix / Mitigation

Immediate mitigation: disable `metadata_filter_version=v3`, purge affected answer cache entries, block all responses where any retrieved chunk has `tenant_id != doc_tenant_id`, and force human review for contract-entitlement answers generated during the incident window.

Longer-term fix: make tenant isolation a non-bypassable server-side predicate, add a hard post-retrieval invariant check, remove connector-level ACL shortcutting, and add an automated eval that fails deployment if cross-tenant chunks appear in retrieved context. Add a dashboard panel for `cross_tenant_retrieval_count` by tenant, connector, retriever version, and filter version.

## Red-Team / Safety Risk

This is a privacy and contractual confidentiality incident. A malicious user could intentionally query for rare phrases that retrieve neighboring tenant documents if tenant filters are weak. Even one leaked contract clause can expose pricing, support commitments, or regulated customer data.

## Interview Explanation

A strong candidate should frame this as a multi-tenant isolation failure, not a hallucination. They should mention blast-radius control, trace reconstruction, filter verification, ACL enforcement, cache purge, customer communication, and regression tests. They should also explain why tenant isolation must be enforced outside the LLM and outside prompt instructions.

## Weak Candidate Answer

“I would improve the prompt and tell the model not to use other customers’ data. I would also increase retrieval accuracy and ask the user to verify the answer.”

## Strong Candidate Answer

“I would treat this as a critical data isolation incident. First I would disable the new filter version and stop serving answers from suspicious traces. Then I would inspect the trace for request tenant, retrieved chunk tenant, filter expression, and ACL decision. The telemetry already shows `tenant_id=acme`, `doc_tenant_id=globex`, and `acl_check=skipped`, so the root cause is likely the filter/ACL path, not the model. The fix is to enforce tenant equality as a hard backend invariant before context assembly, add post-retrieval validation, purge affected cache, and add a deployment gate that fails on cross-tenant retrieval.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies critical multi-tenant isolation failure | Calls it a generic bad answer |
| Telemetry interpretation | Compares request tenant, document tenant, filter version, ACL decision | Looks only at latency or model output |
| Root-cause reasoning | Traces filter builder and ACL shortcut | Blames prompt quality |
| Production debugging | Uses traces, canary cohort, cache audit, invariant checks | Reproduces manually in UI only |
| Security/privacy awareness | Mentions confidentiality, blast radius, customer notification | Ignores data leak impact |
| Mitigation quality | Rollback, block invariant violations, purge cache, add gates | “Improve prompt” |
| Communication clarity | Explains severity and remediation to security/product/customer | Gives vague engineering update |
