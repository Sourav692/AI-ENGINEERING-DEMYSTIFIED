# G08 — Document Review Copilot: Cheat Sheet

Use the [Main guide](/modules/15-fde-case-studies/knowledge-retrieval/document-review-copilot#main) for the spoken answer, the [Deep Dive](/modules/15-fde-case-studies/knowledge-retrieval/document-review-copilot#deep-dive) for mechanisms, and the unchanged [source](/modules/15-fde-case-studies/knowledge-retrieval/document-review-copilot#full-pack) for the full case.

## One sentence

**The copilot extracts and drafts; exact evidence and a named human decide what can be trusted or sent.**

## Ask first

Which document and decision? Who approves? Which current rule version? What fields/tables are critical? Patient/matter/tenant scope? What must be refused? False-positive budget and cost per true issue?

## Flow

**Document/rule ingest → OCR and table-coverage gate → authorized rule/evidence retrieval → small-model typed extraction → compare/gaps/risk → strong LLM only on flagged cases → exact-span citation → independent verifier → named human approval → audit.**

**Agent role:** bounded review copilot. Small model extracts; strong LLM drafts flagged work; neither makes a medical, legal, or compliance ruling.

## Six rules

1. One spine covers prior authorization, compliance, and contracts; swap the schema, governing rule, and approver.
2. Missing/low-confidence evidence is a gap, not text to invent.
3. High-risk PDF with missing tables fails ingestion; retrieval cannot recover absent content.
4. A correct answer with a wrong citation is high severity; verify the exact span used.
5. Patient, matter, tenant, PHI, and privilege boundaries apply before prompts and at output.
6. Material drafts and anything external require the named human; version one has no autonomous submission.

## Source examples

Interactive **3–8 s**; packet **10–20 s**; bulk surveillance overnight. Example gates: **≥90% grounded claims, ≥95% span citations, ≥95% high-risk escalation, ≥80% task completion, zero permission/PHI violations**. Agree final bars per customer.

## Two incidents

| Incident | Signal | Fix |
|---|---|---|
| Legal wrong citation | Groundedness **0.91**, citation accuracy **0.38**; true clause ranked 7th | Roll back citation change; require span match and separate citation gate. |
| PDF missing matrix | **17** tables detected, **9** extracted; **52.9%** coverage, pages 31–33 missing | OCR/table reprocess, block affected answers, hard ingestion gate. |

## Cost and rollout

Rules and small models screen every page; strong LLM only on flagged risk. Measure tokens/document, flagged fraction, extraction quality, and cost per **true issue found**. One type + rule → golden historical cases → shadow → read-only pilot → approved draft-only rollout.

“Extraction is cheap; judgment is expensive. The citation and human decision remain release gates.”
