# Incident 8: PDF Parser Drops Critical Tables During Policy Ingestion

## Scenario

A financial compliance reviewer uses a RAG assistant to answer questions about internal trading policy. Many policies are PDFs with tables listing thresholds, exceptions, and approval chains. The ingestion pipeline converts PDFs into markdown, chunks the text, embeds chunks, and stores layout metadata.

On 2026-07-08, reviewers noticed that the assistant gave incomplete answers about restricted-list escalation thresholds. The relevant information existed in the PDF, but it was inside a table that the parser failed to extract.

This incident is valuable because candidates must understand that GenAI quality depends on ingestion fidelity, not just retrieval and prompting.

## User-Visible Symptom

A compliance reviewer asked: “What approval is needed for restricted-list trade exception above €5M?” The assistant answered with the general escalation process but missed the table row requiring “Head of Compliance + Legal sign-off.”

## System Context

Ingestion path: S3 document drop → parser service → table detector → OCR fallback → chunker → embedding worker → vector DB → retrieval. The parser emits `extraction_coverage`, `table_count_detected`, `table_count_extracted`, and `layout_confidence`. High-risk policy PDFs should fail ingestion if table extraction coverage is below 95%.

## Production Telemetry

```text
2026-07-08T07:44:12.002Z level=warn service=pdf-parser
  document_id=doc_trade_policy_2026_v4 source_file=TradingPolicy_2026_v4.pdf
  parser_version=pdf_extract_v3.2 page_count=48
  table_count_detected=17 table_count_extracted=9 table_extraction_coverage=52.9%
  layout_confidence=0.61 ocr_fallback_triggered=false ingestion_status=success

2026-07-08T08:02:31.515Z level=info service=chunker
  document_id=doc_trade_policy_2026_v4 chunks_created=184
  pages_with_no_text=[31,32,33] missing_sections=[restricted_list_threshold_matrix]
  chunking_strategy=heading_aware_v2 embedding_model=text_embed_v5

2026-07-08T10:19:07.724Z level=error service=response-evaluator
  trace_id=trc_parse_8827 request_id=req_fin_55019
  query="approval needed for restricted-list trade exception above €5M"
  expected_source_page=32 retrieved_pages=[12,13,14,21]
  table_required=true table_chunk_present=false answer_completeness_score=0.46
```

## What Changed Recently

The parser was upgraded from `pdf_extract_v2.9` to `pdf_extract_v3.2` to improve speed. The new parser handled text faster but had a regression on rotated landscape tables. The ingestion gate treated low table coverage as a warning instead of failing the job because the document was classified as “policy_text” rather than “policy_with_tables.”

## Root Cause

Critical table pages were dropped during ingestion. The RAG system could not retrieve information that was never indexed. The deeper issue was a weak ingestion quality gate: a high-risk policy document with 52.9% table extraction coverage should not have been marked successful.

## Debugging Path

A strong engineer checks whether the missing answer content exists in the source PDF, then verifies whether it appears in parsed markdown, chunks, embeddings, and retrieval results. They inspect parser coverage metrics and compare parser versions. They also look for page-level gaps and table extraction warnings during ingestion.

The key debugging concept is “absence from index.” If the table was not chunked, increasing top-k or changing the prompt will not fix the answer.

## Fix / Mitigation

Immediate mitigation: reprocess the document with OCR/table extraction fallback, manually validate pages 31–33, and disable autonomous answers for restricted-list threshold questions until the corrected index is live.

Long-term fix: classify table-heavy policies correctly, fail ingestion when table coverage is below threshold, add visual/table regression tests for parser releases, and store page-level extraction coverage in the retrieval metadata. Add a retrieval-time warning when a query targets a section known to have ingestion warnings.

## Red-Team / Safety Risk

Parser failures can silently remove constraints, thresholds, or exceptions, causing the assistant to give overly permissive compliance advice. A malicious actor could upload documents with adversarial formatting to hide policy restrictions from ingestion.

## Interview Explanation

A strong candidate should explain that the LLM cannot reason over missing data. They should trace source PDF → parsed text → chunks → embeddings → retrieval → answer, and propose ingestion gates, parser regression tests, and human validation for high-risk documents.

## Weak Candidate Answer

“I would increase retrieval top-k or ask the model to pay more attention to tables.”

## Strong Candidate Answer

“The telemetry shows the parser detected 17 tables but extracted only 9, with pages 31–33 missing. The relevant threshold matrix was never indexed. I would reprocess with OCR/table fallback, block affected answers, and add ingestion gates so high-risk PDFs fail if table coverage is low. Retrieval tuning cannot recover content that was dropped before indexing.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies ingestion fidelity failure | Calls it retrieval failure only |
| Telemetry interpretation | Uses table coverage, missing pages, chunk presence | Looks only at answer quality |
| Root-cause reasoning | Recognizes missing source content in index | Blames LLM comprehension |
| Production debugging | Traces PDF to parsed chunks to retrieval | Only changes prompt/top-k |
| Security/privacy awareness | Notes compliance and adversarial document risk | Ignores hidden constraints |
| Mitigation quality | Reprocess, gate ingestion, parser tests | Tweak model settings |
| Communication clarity | Explains why absent data cannot be retrieved | Gives generic RAG advice |
