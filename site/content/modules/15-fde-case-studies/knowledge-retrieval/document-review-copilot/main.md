# G08 — Document Review Copilot: Main Interview Guide

**Document review** is: a packet arrives, a human decides yes/no against a rule (payer, law, playbook). Reading is cheap. **Signing** is expensive.

**G08 covers one slice:** extract evidence, compare to the right rule version, cite the exact span, draft. A named human still decides.

End to end, as prior auth for a procedure:

1. **Packet and payer rule ingest.** If page 7’s table is unreadable, we stop ingest.
2. **Clinician opens the case** with patient scope.
3. **We pull the rule that was in force on the procedure date.**
4. **We extract fields and the supporting sentences.**
5. **We draft “meets criteria” only where the span actually says that.** Bad citation → no green draft.
6. **Clinician approves or rejects.** We never send to the payer alone.

That’s it: **evidence → rule → cited draft → human.** Autonomous clinical or legal yes is out.

**Extraction is cheap; judgment is expensive.** The copilot extracts evidence, compares it with the governing rule, cites the exact supporting span, and drafts. A named clinician, compliance reviewer, or lawyer makes the material decision. Missing evidence, a broken citation, or uncertain access stops the path.

The [source study](/modules/15-fde-case-studies/knowledge-retrieval/document-review-copilot#full-pack) treats three cases as variations of one spine:

| Case | Shared foundation | What changes |
|---|---|---|
| Healthcare prior authorization, the anchor | Document → typed evidence → versioned rule → gap/risk → cited draft → human approval | Patient/PHI boundary, payer/plan/procedure/date rule, clinician decision |
| Financial compliance reviewer | Same extraction, rule mapping, exact citation, review | Jurisdiction/product obligations, severity, high-recall surveillance, false-positive burden |
| Legal contract copilot | Same clause-to-rule comparison and review | Playbook position, fallback language, privilege, material deviation to counsel |
| Claims-processing assistant | Same triage and evidence controls | Claim-type rollout, anomaly signals, adjudication held for later governance |

## 1. Questions to ask the interviewer

| Question to ask | What it's really asking | What you then decide |
| --- | --- | --- |
| Which document and decision are slow or risky today? Who owns the final call? | Is this a prior-auth packet a clinician must sign, or a contract a lawyer must sign? | First slice, named reviewer, and approval route. |
| What is read-only, draft-only, or externally submitted? | Can it only highlight a clause, draft a letter, or actually send it to the payer? | Tool allowlist and whether write-back exists at launch. |
| What is the governing source: payer rule, regulation, or playbook? How is its effective version selected? | Which year’s payer rule applies to this procedure date? | Rule ingestion, versioning, and retrieval. |
| Which fields or tables are crucial, and what extraction coverage is acceptable? | If the table on page 7 is unreadable, do we still draft an approval? | Typed schema, parser mode, and the ingest gate. |
| Which PHI, privileged, or financial fields may enter prompts, logs, and the model provider? | Can diagnosis codes go to a US cloud model, or only a redacted summary? | Minimization, redaction, and where the model runs. |
| What must the assistant refuse or escalate? What evidence must the reviewer see? | If the cited span does not support “meets medical necessity,” does the reviewer still see a green draft? | Risk tiers, span verifier, and review UI. |
| How much false-positive burden can the reviewer absorb, and what cost per true issue is acceptable? | If we flag 50 harmless files to catch one real issue, will reviewers ignore the tool? | Screening tiers and eval thresholds. |

## 2. Requirements: Functional + Non-Functional

The easiest way to frame requirements in an interview is:

> **Functional = what the system does. Non-functional = how well it does it and what constraints it must satisfy.**

### Functional requirements — what the system must do

1. **Retrieve the governing rule** effective for the case.
2. **Extract fields and exact source spans.**
3. **Compare evidence with criteria** — flag missing, stale, or conflicting facts.
4. **Classify risk.**
5. **Draft with a span citation for every claim** — editable.
6. **Verify each span** supports the claim and the user may view it.
7. **Route material or uncertain cases** to a named human.
8. **Audit** evidence IDs, rule/prompt/model versions, edits, and approval.

### Non-functional requirements — how well / under what constraints

| Requirement | Example target / constraint |
|---|---|
| **Security** | Source ACL and patient/matter scope before generation; PHI/privilege minimized in prompts and redacted from logs; no customer-data training without agreement. |
| **Latency** | **3–8 s** interactive; **10–20 s** packet generation; overnight batch for bulk surveillance; analyst drill-down <**10 s**. |
| **Fail-closed** | Access fail, stale governing rule, missing citation, or missing material approval. |
| **Degradation** | Non-authoritative formatting and source outages degrade visibly. |
| **Cost** | Per document **and** per true issue found. |

### First release

One document type, one rule source, internal drafts, every material case approved. No autonomous clinical, legal, or regulatory decision and no external submission. Unmapped ACL or critical parser coverage failure excludes the source until repaired.

### Interview shortcut

If asked **“What are the requirements?”**, say:

> **“Functionally, extract evidence, match the right rule version, cite the span, and send material cases to a named human. Non-functionally, fail closed on access or broken citations, and measure cost per true issue, not just per document.”**

## 3. Architecture

This diagram condenses the [source architecture, §4](/modules/15-fde-case-studies/knowledge-retrieval/document-review-copilot#full-pack) into the ingest and review lanes. It names where the cheap model and strong LLM run and where they lose authority.

```mermaid
flowchart LR
    subgraph ING[Versioned source ingestion]
        DOC[Case documents and records] --> PARSE[OCR, layout and table extraction]
        RULE[Policies, regulations, playbooks] --> PARSE
        PARSE --> QA{Critical pages and tables covered?}
        QA -->|No| HOLD[Fail ingestion and reprocess]
        QA -->|Yes| IDX[(Permission-scoped evidence and rule index)]
    end
    subgraph REV[One review case]
        USER[Reviewer request] --> AUTH[Identity, role, patient or matter scope]
        AUTH --> RR[Retrieve permitted rule effective for case]
        AUTH --> EVID[Retrieve permitted case evidence]
        IDX --> RR
        IDX --> EVID
        RR --> EX[Small model: typed field and span extraction]
        EVID --> EX
        EX --> CMP[Deterministic compare and gap check]
        CMP --> RISK{Risk and completeness}
        RISK -->|Routine| STRUCT[Structured evidence draft]
        RISK -->|Flagged| LLM[Strong LLM: evidence-backed draft]
        RISK -->|Missing or conflicting| ESC[Refuse claim and escalate]
        STRUCT --> CITE[Cite exact supporting spans]
        LLM --> CITE
        CITE --> VERIFY{Span supports claim and is permitted?}
        VERIFY -->|No| ESC
        VERIFY -->|Yes| HUMAN[Reviewer edits; named approver decides]
        HUMAN --> AUDIT[(Evidence, versions, decision audit)]
        ESC --> AUDIT
    end
```

### Step-by-step architecture

- **Step 1.** Ingest case records and governing rules with version, effective date, ACL, and page/span metadata.
- **Step 2.** Parse text and tables. For a high-risk policy, low table or page coverage fails ingestion and triggers OCR/table reprocessing; missing content cannot be retrieved later.
- **Step 3.** Authenticate the reviewer and apply role plus patient, matter, or tenant scope before retrieving both the rule in force and the case evidence.
- **Step 4.** A small model extracts typed fields and exact evidence spans. Low-confidence fields become gaps, never invented facts.
- **Step 5.** Compare fields with the governing criteria, detect missing or conflicting evidence, and assign a risk tier.
- **Step 6.** Use a structured routine draft or send flagged risk to a strong LLM for an evidence-backed draft. Missing or conflicting support takes the refusal/escalation branch.
- **Step 7.** Cite the span actually used, then verify both claim-to-span support and permission. A wrong citation blocks the output even if the answer sounds correct.
- **Step 8.** The human reviewer edits, approves, or rejects. Record evidence, rule version, model/prompt version, edits, and final decision; nothing external is submitted in version one.

**Model and agent role:** this is a bounded document-review copilot, not an autonomous clinical, legal, or compliance decider. A small extraction model processes the broad page set, and the strong LLM drafts only flagged work. Deterministic rules, the citation verifier, and the named professional control what can be relied on and what leaves the workflow.

## 4. Controls worth defending

| Boundary | Why it exists |
|---|---|
| Typed extraction schema | Payer, plan, procedure, diagnosis, date, therapy, lab, imaging; or jurisdiction/obligation/evidence; or clause type/playbook/deviation. Comparison needs named facts. |
| Parser coverage gate | A table-heavy PDF flattened into prose may silently lose an approval matrix. Check detected versus extracted tables and page coverage before indexing. |
| Rule version | Payer rule by plan/procedure/date of service; regulation by jurisdiction/product; playbook by clause type and effective date. |
| Span-level citation | A correct answer with a misleading citation can be more dangerous than refusal. The verifier checks the actual supporting span, not the nearest ranked chunk. |
| Sensitive-data boundary | Restrict what enters prompt, index, logs, provider, and reviewer view; no permission granted by a prompt instruction. |
| Human decision | Drafts and suggestions never become clinical, compliance, or legal rulings automatically. |

## 5. Failure and cost playbook

| Failure | Response |
|---|---|
| PDF parser misses tables on high-risk policy | Fail ingestion, use OCR/table fallback, block affected answers until corrected index is live. |
| Governing rule stale or missing | Refuse draft; show required rule version and route to reviewer. |
| Step therapy or other clinical evidence absent | Flag the gap; do not invent a treatment history. |
| Citation does not support claim | Reject output and send to review, regardless of overall groundedness score. |
| Wrong patient or privileged matter | Access check fails closed before retrieval. |
| LLM or retrieval unavailable | Partial packet with labeled gaps or refusal; bulk work may queue. |
| Approval unavailable | Nothing external leaves. |

Bulk surveillance is a screening funnel: rules and small classifiers process all documents; the strong model sees only borderline or flagged risk. Dedupe templated packets by content hash, batch non-urgent work off-peak, cap context and top-k, and watch the **flagged fraction** because it drives strong-model spend. Keep the citation verifier on the path that a material draft takes.

## 6. Evaluation and rollout

Use separate datasets and gates for extraction fields, answer groundedness, **citation span accuracy**, high-risk escalation, and PHI/permission safety. The source examples offer **≥90% grounded claims**, **≥95% correct span citations**, **≥95% high-risk escalation**, **≥80% task completion**, and **zero** permission/PHI violations; agree final thresholds per workflow. Track reviewer overrides, false-positive burden, preparation time, first-pass approval/denial, p95, and cost per true issue found.

The two source incidents show why gates are separate. In the legal citation incident, the answer was supported but cited the wrong clause; grounding scored **0.91** while citation accuracy was **0.38**. In the parser incident, **17** tables were detected but only **9** extracted (**52.9%** coverage), leaving pages 31–33 and the approval matrix out of the index. Retrieval tuning cannot repair either missing input or a verifier that ignores span mismatch.

Roll out one document type and rule source → offline golden cases → red-team and shadow mode → read-only reviewer pilot → one low-risk category with approved drafting. Expand only while extraction, citation, escalation, and privacy gates hold. Reviewer corrections feed a governed evaluation set, not silent training.

## 7. Interview answer to rehearse

> “I would first clarify which decision the reviewer makes and what the assistant must never decide. I would ingest the right rule version and case evidence under patient or matter permissions, with a parser gate for critical tables. A small model extracts typed fields and spans, deterministic checks compare them to criteria and flag gaps, and a strong LLM drafts only flagged cases. Every claim cites the exact span used; a separate verifier blocks a mismatched or forbidden citation. A named human approves material cases, and versioned evidence and edits go into the audit. I would launch on one document type, shadow real reviewers, and gate on extraction, citation, escalation, and zero privacy violations. Cost is controlled by cheap screening and strong-model routing, not by skipping review.”

Use the [Deep Dive](/modules/15-fde-case-studies/knowledge-retrieval/document-review-copilot#deep-dive) for incident and schema details and the [Cheat Sheet](/modules/15-fde-case-studies/knowledge-retrieval/document-review-copilot#cheat-sheet) for recall.
