# Fact-check follow-ups (after round 1, 27 Sep 2026)

Round 1 covered the 20 grouped case studies and the 18 Last-Day reviews plus the trigger sheet.

- 363 checkable claims were extracted: see `claims-round1.csv`.
- All 220 high- and medium-priority claims were verified against official docs and papers.
- 128 text corrections were applied.
- Sources were added to each group's full pack and to the Last-Day modules.

## Round 2 scope (not yet checked)

CONTENT-17 labels are applied to all of this (27 Sep 2026). What's left is the CONTENT-18 source check. Start with the 29 open rows in `claims-round2-queue.csv`.

- The 143 low-priority claims in `claims-round1.csv`.
- The 13 standalone cases (`Case_Study_Groups/Standalone/`).
- The 22 practice worksheets and model answers.
- The Roadmap and the Rapid Revision Guide.
- The behavioural model answers (factual claims only).

## Loose ends — all closed 27 Sep 2026
- Handbook `06_Output_Guardrails.md` and both `nodes.py`: "most common over-refusal" → "a common" (C158).
- Study guide 12: first token "in well under a second", not "in milliseconds" (C149).
- Voice project `PROJECT_REPORT.md` and the quiz in `ASSIGNMENTS_AND_QUIZZES.md`: Nova-3, Pipecat's default (C077).
- Handbook `05_Agentic_Workflow_Platforms/04_Durability_And_Idempotency.md`: Redis lease now checked with a fencing token, matching G15 (C098).
- Standalone 25 409 vs 412: the version is in the body, not `If-Match`, so 409 stands. Idempotency-key reuse is Q016 in `claims-round2-queue.csv`.
- V1/V2 chapter 15: "salted hash" is now a keyed hash, and the code's `salt` is now `key` / `TELEMETRY_HASH_KEY`.
- The 10 Discovery answer keys: each Availability line now fits its case (support desk hours, 24/7 for SRE, deal deadlines for legal, and so on).
- Standalone 23 Coverage Notes: the second pass "narrowed, but didn't close" the two gaps, and cost is "one of the six SLIs in Section 3".
- Standalone 61: the rollout column credits Module 08 doc 1 for shadow, canary and promote only. Cohort waves are the author's.
- British spelling: 442 prose edits across the published practice worksheets, answer keys and standalone tabs. Code, inline code, links, URLs and `[FILL]` markers were not touched; neither were HTTP reason phrases (in backticks), "Synthesizer Agent", "prior authorization" (a US payer process name), or *size*/*licensed*. In-page anchor links were updated with their headings.

## Owner decisions — made 27 Sep 2026
- **DevRev (C078):** anonymised on the site. G15 now says "a company's system-design prep guide". The `AI_Engineer/Delivery Framework…` docs and the Handbook README aren't site pages and still name it.
- **G11 Research Platform:** it's the author's own build. G11 and its Main copy now say so.

## Recheck dates (time-bombs)
- Claude Haiku 4.5: retirement "not sooner than 15 Oct 2026". Recheck the G18 pricing example after that date.
- Zendesk API tokens: no new tokens from 27 Oct 2026, all switched off 30 Apr 2027 (G12).
- Groq `llama-3.1-8b-instant` was shut down for free and developer tiers on 16 Aug 2026 (G11).
- Databricks renames of mid-2026: Vector Search → AI Search, Genie → Genie One, Genie Spaces → Genie Agents, AI Gateway → Unity Gateway. Expect more doc and name churn.

## Found during CONTENT-17 (27 Sep 2026) — not fixed
- `FDE/FDE_System_Design_Interview_20_Scenarios/Version_1` and `Version_2` chapter 15 still say "salted hash … HMAC-SHA256". The published V3 key now says "keyed hash with a secret key".
- The 10 Discovery answer keys share one "Availability: design for business-critical support hours" line, which doesn't fit every case (retail demand, executive dashboard).
- Standalone 23 Coverage Notes: item 17 (regulatory) is still "Partial" though the note says the second pass closed it; cost is called "one of six scorecard SLIs" but it's one of the six Section 3 SLIs.
- Standalone 61: the rollout table's column header credits Handbook Module 08 doc 1, which doesn't contain the cohort-wave numbers (the cell now says "In this design").
- Several standalone tutorials and practice keys still use American spelling (normalize, behavior). Deliberately left to keep the label diffs small.

