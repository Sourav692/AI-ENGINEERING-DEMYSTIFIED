# G08 — Document Review Copilot: Deep Dive

The [Main guide](G08_Document_Review_Copilot_Main.md) is the spoken design; the unchanged [source study](G08_Document_Review_Copilot.md) holds the full cases. This file keeps the mechanisms and the two incidents that are easiest to miss in a short answer.

## 1. One spine, three schemas

| Persona | Typed extraction | Governing rule and version | Evidence-to-rule record | Human |
|---|---|---|---|---|
| Prior authorization | Payer, plan, procedure, diagnosis, date of service, prior therapies, labs, imaging | Payer rule by payer/plan/procedure/diagnosis/date | `EvidenceLink` from clinical fact to requirement, missing-document and denial-risk flags | Clinician approves packet. |
| Financial compliance | Document type, jurisdiction, product, obligation, evidence span | Current regulation and internal policy | `Finding` with rule citation, risk/severity and remediation note | Analyst; supervisor or legal for high risk. |
| Contract review | Clause type, normalized text, counterparty, jurisdiction, confidentiality | Negotiation playbook and preferred clause | `RiskFinding` with deviation and approved fallback language | Counsel for material changes. |

The claims-processing variant adds OCR, anomaly signals, and claim-type rollout, but extraction and missing-information detection precede any adjudication. Do not infer a clinical fact from a “rule out” note. Do not invent step therapy when the EHR has no record. Low-confidence extraction is marked missing because a wrong field corrupts comparison, risk, and citation downstream.

## 2. Ingestion, permission, and version seams

Map EHR/FHIR, payer PDFs, regulatory library, advisor communications, CLM/playbook, and case systems by owner, freshness, ACL, and risk. EHR is patient/role scoped, contracts are matter/privilege scoped, compliance obligations vary by jurisdiction/product. A source without usable ACL metadata stays out of production retrieval. Rule versions are selected by effective/expiry date and case attributes, so a request can be judged against the rule in force on its date of service.

PDF layout is a correctness boundary. Detect tables, extract them in table mode, keep row or row-group chunks together with page anchors, and measure `table_count_detected`, `table_count_extracted`, `extraction_coverage`, and `layout_confidence`. Validate reading order; apply OCR/table fallback where needed. A high-risk policy below the agreed coverage threshold fails ingestion rather than warning. Store page-level coverage in retrieval metadata and rerun offline evaluation on parser or chunker changes.

Minimize PHI and privileged material before prompts, redact logs, retain evidence IDs and policy versions, and audit break-the-glass access where allowed. The retrieval filter checks role plus patient/matter/tenant scope; the output verifier checks it again for each cited span. A retrieved email, clause, or payer PDF is evidence, not instructions to the system.

## 3. Models, verification, and decisions

Run a small extraction/classification model across the page set. Compare typed evidence with criteria and risk rules; use the strong LLM only on flagged or borderline material for drafting and explanation. This is a bounded copilot workflow. The model does not make the clinical necessity, legal position, or compliance ruling. Draft text stays editable. A named professional decides, with material approval bound to the case, evidence, and rule version.

Citation construction and verification are separate. The citation points to the exact source span that supported the drafted claim, not a nearby concise or high-ranked chunk. The verifier checks span-to-claim support and that the user may see the span. Groundedness, citation accuracy, extraction accuracy, escalation, and permission/PHI leakage need separate evaluations. An overall groundedness score cannot compensate for a bad citation. Unsupported or missing claims are blocked or flagged; external submission is disabled in the first release.

## 4. Incident drill: right answer, wrong clause

In [source §14](G08_Document_Review_Copilot.md#14-debug-the-incidents-on-this-design), the assistant answered a termination question correctly but cited a data-processing clause (12.4) instead of the actual termination clause (8.2). The true chunk ranked seventh. `answer_supported=true` and groundedness **0.91** masked `citation_span_match=false` and citation accuracy **0.38**. Citation generator `cite_v5` preferred concise retrieved text; the verifier over-weighted answer groundedness.

Contain by rolling back the citation generator, requiring span match for legal workflows, and sending low-accuracy drafts to human review. Prevent with separate answer/citation/quote-span gates, clause-type features in reranking, and highlighting the actual supporting clause. The interviewer should hear: a correct answer with a false citation launders bad evidence into a professional decision.

## 5. Incident drill: critical PDF table never indexed

The other [source §14 incident](G08_Document_Review_Copilot.md#pdf-parser-drops-critical-tables-92) asks about a restricted-list trade exception above **€5M**. The answer missed the Head of Compliance plus Legal sign-off row. Parser `pdf_extract_v3.2` detected **17** tables but extracted **9**, or **52.9%**; pages **31–33** contained no text and the threshold matrix was absent. Ingestion still said success because the policy was classified as plain text. The regression affected rotated landscape tables.

Reprocess with OCR/table fallback, manually check the missing pages, and block autonomous answers on affected threshold questions until the corrected index is live. Prevent through table-heavy document classification, a hard coverage gate, parser visual/table regression cases, and retrieval metadata marking incomplete pages. Raising top-k cannot retrieve content that never entered the index.

## 6. Release, rollout, and cost detail

Use historical cases with SME-labeled fields and human decisions. Source example goals are **≥90% supported claims**, **≥95% span citations**, **≥95% high-risk escalations**, **≥80% task completion**, and **zero** permission or PHI violations; set field-specific extraction bars and false-positive budgets with the customer. Red-team outdated rules, wrong patient, prompt injection in PDFs/messages, missing diagnosis or step therapy, “rule out” misread as confirmed, and “just submit it anyway.” In compliance, high recall on severe violations must be balanced with the reviewer’s false-positive workload.

Roll out one document type and rule → offline golden set → shadow reviewer decisions → read-only pilot → draft-only low-risk category behind approval. Measure reviewer edits/overrides, packet preparation and review time, first-pass approval or denial, citation accuracy, p95, and cost per true issue. Bulk surveillance runs overnight: deterministic rules and small classifiers screen everything, the strong model handles the flagged fraction, and high-risk cases receive priority. Dedupe repeated templates by hash and batch non-urgent work; never save money by silently dropping citation or approval controls.
