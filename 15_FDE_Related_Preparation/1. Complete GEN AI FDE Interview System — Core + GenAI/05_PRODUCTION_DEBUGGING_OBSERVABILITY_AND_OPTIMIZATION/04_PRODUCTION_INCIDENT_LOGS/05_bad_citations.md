# Incident 5: Correct Answer with Misleading Citations

## Scenario

A legal contract copilot helps account executives answer questions about customer agreements. The assistant must cite the exact contract clause supporting each answer because users are not allowed to rely on uncited legal advice.

On 2026-07-08, an account executive asked whether a customer could terminate for convenience with 30 days’ notice. The assistant gave the correct answer, but the citation pointed to the wrong section. This is dangerous because users may trust the citation and repeat it in customer negotiations.

The incident teaches a subtle GenAI production lesson: answer correctness and citation correctness are separate evaluation dimensions.

## User-Visible Symptom

The assistant answered: “Yes, the customer may terminate for convenience with 30 days’ written notice.” That answer was correct. But the citation linked to Section 12.4, “Data Processing Addendum,” instead of Section 8.2, “Termination for Convenience.” A legal reviewer flagged the answer as misleading.

## System Context

RAG pipeline: contract search → clause chunk retrieval → reranker → answer generation → citation generation → citation verifier → legal-risk evaluator. The citation generator extracts spans from retrieved chunks after the LLM answer is generated. The system allows answers only if citation verification passes.

## Production Telemetry

```text
2026-07-08T11:28:03.331Z level=warn service=citation-verifier
  trace_id=trc_cite_2088 request_id=req_legal_33102 tenant_id=acme
  query="Can Contoso terminate for convenience with 30 days notice?"
  answer_supported=true answer_clause_id=clause_8_2
  citation_doc_id=doc_contoso_msa_2026 citation_clause_id=clause_12_4
  citation_span_match=false citation_generation_version=cite_v5

2026-07-08T11:28:03.401Z level=info service=reranker
  trace_id=trc_cite_2088 retrieved_chunk_rank_for_true_clause=7
  top_ranked_chunk_id=chk_12_4_dpa top_ranked_score=0.74
  true_supporting_chunk_id=chk_8_2_term score=0.68
  reranker_features=[semantic_similarity,heading_match] missing_feature=clause_type_boost

2026-07-08T11:28:04.010Z level=error service=response-evaluator
  trace_id=trc_cite_2088 eval=bad_citation severity=high
  grounding_score=0.91 citation_accuracy_score=0.38
  policy_action=allowed reason="answer_supported=true AND grounding_score>0.85"
```

## What Changed Recently

`citation_generation_version=cite_v5` was deployed to support shorter citations. The deployment changed citation selection from “quote the exact supporting span used in answer synthesis” to “select the most concise citation from retrieved context.” The release gate evaluated answer groundedness but did not separately evaluate citation span accuracy.

## Root Cause

The answer generator used the correct supporting clause, but the citation generator selected a nearby high-ranking chunk with similar legal language. The verifier allowed the response because it over-weighted answer groundedness and under-weighted citation span matching.

## Debugging Path

A strong engineer inspects the answer text, supporting chunks, citation chunk, retrieved ranks, and verifier decision. They check whether the cited span actually contains the claim. Then they compare `cite_v5` against the prior citation version on a golden set with clause-level labels.

The key is to avoid saying “the answer was correct, so it is fine.” In legal and compliance settings, wrong citations are a production failure even when the answer happens to be right.

## Fix / Mitigation

Immediate mitigation: roll back to `cite_v4`, require citation span match for legal workflows, and route low citation-accuracy answers to human review.

Longer-term fix: split evaluation into answer correctness, citation correctness, and quote-span faithfulness. Add clause-type features to the reranker, require citation to come from the actual supporting span, and add UI highlighting so users can verify the exact clause.

## Red-Team / Safety Risk

Misleading citations can launder unsupported legal claims. A malicious user could use a plausible citation to persuade another stakeholder that the system found contractual support. This creates legal, compliance, and trust risk.

## Interview Explanation

A strong candidate should emphasize that grounded answer quality is not enough. They should discuss citation verification, span-level evaluation, legal workflow severity, and human-in-the-loop routing.

## Weak Candidate Answer

“The answer is correct, so I would not treat this as serious. Maybe improve citation formatting.”

## Strong Candidate Answer

“I would treat this as a high-severity citation faithfulness issue. The telemetry shows `answer_supported=true` but `citation_span_match=false`, with the real clause ranked 7th. I would roll back the citation generator, require span-level verification, and add separate citation accuracy evals. In legal workflows, a correct answer with a wrong citation can be more dangerous than an answer that clearly refuses.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Separates answer correctness from citation correctness | Says correct answer is enough |
| Telemetry interpretation | Uses citation span match, clause ID, ranking, grounding score | Looks only at answer text |
| Root-cause reasoning | Identifies citation generator/verifier weakness | Blames user confusion |
| Production debugging | Runs clause-level golden evals | Manually checks one answer only |
| Security/privacy awareness | Notes legal trust and misuse risk | Ignores compliance context |
| Mitigation quality | Rollback, span verification, human review | Cosmetic citation changes |
| Communication clarity | Explains why misleading citation is severe | Minimizes incident |
