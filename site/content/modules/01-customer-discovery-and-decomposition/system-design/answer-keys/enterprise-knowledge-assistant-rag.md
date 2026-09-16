# Enterprise Knowledge Assistant with RAG - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- Which source is authoritative for each content type, and what should happen when Drive, SharePoint, Slack, the wiki, and tickets disagree?
- Must the assistant inherit source permissions in real time, or is periodic synchronization acceptable? That answer decides where ACL checks live.
- May the assistant synthesize across sources, or answer only from retrieved passages? Must citations point to the exact passage or just the document?
- How fresh must policies, tickets, and project updates be, and how fast must a deletion or revoked permission leave retrieval?
- Who is the primary user, who diagnoses a wrong answer, and who owns the risk if the assistant over-shares?
- What is the p95 latency target, and what residency, retention, and cost limits must we honor?
- Who may view audit logs and answer traces, and what evidence must they contain to reconstruct an answer?
- What is the fallback when retrieval fails or sources conflict: refuse, answer with a staleness label, or escalate to a human?

## Strong functional requirements
- Support the core workflow: employee asks a work question, assistant resolves their groups, retrieves only permitted passages, and answers with passage-level citations.
- Ingest Drive, SharePoint, Slack, wikis, and tickets incrementally; no source change should force a full reindex.
- Preserve document versions and ACL metadata so retrieval can answer "what was visible to this user at this time?"
- Perform hybrid retrieval and reranking; keyword matching carries policy IDs, error codes, and ticket numbers that dense retrieval blurs.
- Show citations and abstain when evidence is weak. A correct refusal beats a confident hallucination.
- Record safe feedback signals for evaluation without indiscriminately storing raw user prompts.

## Strong non-functional requirements
- Latency: state the target as a percentile, never "fast enough"; budget p95 in slices across identity, ACL filtering, retrieval, reranking, and generation.
- Availability: degrade gracefully when a connector, index, or model provider fails — partial coverage, labeled staleness, or refusal, never a silent guess.
- Security: no cross-user disclosure; effective permissions filter candidates before content reaches the model; revocations fan out to every index and cache.
- Compliance: immutable audit of source event IDs, index and ACL version stamps, request IDs, and the exact citation set shown.
- Reliability: fail closed on permission checks, deletion sync, and citation validation; degrade on retrieval quality; queue background reindexing.
- Cost: estimate embedding, index, and token cost independently; at 50 million chunks the refresh pipeline outgrows the initial embedding job.

## Architecture explanation
- Split control plane (policy, config, credentials, connector scheduling, evaluation rules) from data plane (live questions, evidence fetch, permission enforcement, responses).
- Ingestion is asynchronous: connectors feed an event-plus-backfill queue, so events carry near-real-time updates and backfill catches missed items and outages.
- A parser/OCR/chunker normalizes PDFs, slides, tickets, and chat threads; an ACL normalizer maps each source's permissions into one internal model.
- Two indexes are written: keyword for exact names, IDs, and policy phrases; vector for paraphrase, scored as `S_hybrid = α·S_vector + (1−α)·S_keyword`.
- The query path is synchronous and ordered by risk: authenticate, resolve groups, then rewrite the question only where meaning survives.
- The permission-aware retriever applies ACL filters during candidate selection, so unauthorized documents never become evidence; a reranker and context-budget manager trim survivors.
- An LLM gateway centralizes prompts, model selection, and guardrails; a citation builder attaches passage references; an output policy engine abstains or redacts.
- An evaluation and trace store records privacy-safe traces and feedback. Caches are latency optimizations invalidated on permission change, never a permission model.

## Data model / integration assumptions
- Document(id, source, version, owner, acl_policy_id, deleted_at); Chunk(id, document_id, text, embedding_ref, offsets, metadata); QueryTrace(id, actor_hash, retrieval_set, model_version, latency, outcome).
- Assume the indexes own derived search state, never source truth; uncertainty is resolved by re-reading the system of record, not the index.
- Assume a chunk must not outlive its parent's authorization and freshness guarantees; `deleted_at` tombstones a document out of retrieval without erasing its history.
- Assume schedulers, webhooks, and operator retries all double-submit, so sync and delete are idempotent and deleting twice never resurrects derived chunks.
- Assume every version boundary is visible in traces — schema, API, connector checkpoint, embedding model, retrieval policy — because re-chunking is a retrieval-model change.

## Red-team risks
- permission leakage across departments, stale content after a missed deletion, fabricated citations, prompt injection in enterprise content, traces accumulating secrets
- Indirect prompt injection planted in a ticket, wiki page, or pasted note; retrieved content is untrusted evidence, never instructions.
- Permission-boundary tests asking the same question as users with different groups, regions, entitlements, and mid-session membership changes.
- Data exfiltration attempts such as summarizing confidential corpora, coaxing hidden metadata, or extracting system prompts and tool schemas.
- Citation fabrication where the model cites a document absent from the retrieval set; verify every citation post-generation against live authorization.
- Staleness and conflict attacks where a deleted or superseded document still ranks well — the named drill is a connector missing deletion events.

## Rollout plan
- Week 0-1: name the workflow, the dangerous constraint, success metrics, source owners, and explicit non-goals.
- Week 1-2: ingest one low-risk corpus; validate ingestion, ACL normalization, retrieval, and citation formatting with no write-back.
- Week 2-3: build the access-leakage suite across roles, indirect phrasing, stale ACLs, and deleted documents; any exposure blocks release.
- Week 3-4: run silent evaluation on real employee questions while users still receive the legacy workflow.
- Week 5: launch a read-only pilot with citations, abstention, feedback capture, and an escalation path for one segment.
- Week 6-8: expand source by source, each with its own freshness dashboard, reconciliation rules, owner, and rollback trigger.
- After pilot: widen only while leakage stays at zero and groundedness, freshness, latency, and cost hold; rehearse the reconciliation drill.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Permission leakage count | No user saw content or a citation they could not open | Zero; any case triggers rollback review | ACL red-team suite across roles and stale groups |
| Grounded answer rate | Claims are supported by evidence, not model memory | No sustained drop over 5 points from baseline | Silent-mode labeled set plus sampled traffic |
| Citation precision and recall | Cited passages support the answer, and the right sources were used | Above agreed bar; no unexplained 5-point decline | Human/SME review of a sampled set |
| Freshness lag | Updates and deletions reach retrieval inside the agreed window | Within the freshness SLO per content class | Connector telemetry versus index timestamps |
| Retrieval recall | Relevant documents reach the candidate set at all | Measured per query type, used to tune α | Representative query set segmented by type |
| p95 latency and cost per answer | The system meets its interaction budget affordably | p95 within target at 100 QPS peak | Load test plus production telemetry |

## Weak answer
I would connect the enterprise sources to a vector database and have an LLM answer from the top results. This is weak because it ignores the permission boundary, treats retrieval quality as the hard problem, and has no story for deletions, citation verification, evaluation, or diagnosing a bad answer.

## Average answer
I would build a RAG system over the enterprise sources, add hybrid search and reranking so exact policy IDs still match, show citations, and filter results by permission. This is better, but still incomplete because it never says whether permissions are enforced before or after retrieval, does not handle a missed deletion, and does not define what fails open versus closed.

## Strong answer
I would start from the outcome — grounded answers with citations that preserve source permissions and freshness — and name permission fidelity as the load-bearing constraint, because an assistant that leaks is worse than none. Ingestion normalizes each source's ACLs alongside version and tombstone metadata. Retrieval is hybrid and permission-filtered before anything reaches the model, followed by reranking, grounded generation, citation verification, and abstention on weak evidence. I would enforce ACLs at query time and precompute only where permissions are stable, so an optimization never becomes the security policy. I would prove it with a leakage suite, groundedness metrics, and a deletion-reconciliation drill. The key is not just using RAG, but proving the system is permission-safe and auditable.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | Jumps to vector DB and chatbot UI | Names users and a success metric | Reframes feature as outcome, names permission fidelity as the dangerous constraint |
| Requirements | Generic "answer questions accurately" | Lists functional needs and some constraints | MoSCoW split, percentile constraints, explicit non-goals, requirement-to-component traceability |
| Architecture | LLM plus vector index | Reasonable RAG pipeline with reranking | Control/data plane split, ACL normalizer, permission filter before generation, output policy |
| Data/integration | Mentions sources vaguely | Names the three core records | Owners, retention, tombstones, idempotent sync and delete, versioned boundaries |
| Evaluation | "We would test accuracy" | Small golden set and latency checks | Leakage suite, groundedness, citation precision, freshness lag, alert thresholds |
| Safety/security | Mentions privacy generally | Adds RBAC and audit logging | Threat-models injection, stale ACLs, fabricated citations; explicit fail-open/fail-closed per component |
| Rollout | Ships to everyone at once | Pilot group after testing | Low-risk corpus, leakage gate, silent evaluation, source-by-source expansion, rollback drills |
| Communication | Diagram dump or hand-waving | Clear but generic walkthrough | Leads with outcome and risk, spends minutes in proportion to stakes, states assumptions |

## Final 2-minute spoken answer
I would not start with the model. I would start by asking whose workflow changes, what success means, and which constraint is most dangerous if ignored — and here that constraint is permission fidelity, not retrieval quality, because an assistant that answers well but leaks is worse than no assistant at all. So I would restate the ask as a business outcome: employees resolve work questions from approved content across Drive, SharePoint, Slack, wikis, and tickets, with citations, and only from material they could already open. Architecturally, ingestion is asynchronous — connectors into an event and backfill queue, parsing and chunking, then an ACL normalizer that maps every source's permission model into one internal representation, written to both a keyword and a vector index. The query path is synchronous and ordered by risk: authenticate and resolve groups, rewrite only where meaning survives, retrieve with permission filters applied before candidates exist, rerank, trim to a context budget, generate through a gateway, verify every citation, and abstain when evidence is weak. I would enforce ACLs at query time and precompute only where permissions are stable. I would prove it with an access-leakage suite, groundedness and citation precision, freshness lag, and a deletion-reconciliation drill, rolling out from one low-risk corpus through silent evaluation to source-by-source expansion with rollback. The goal is not a demo that answers well; it is a service the enterprise can trust, audit, and operate.
