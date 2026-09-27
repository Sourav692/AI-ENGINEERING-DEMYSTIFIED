# Fact-check follow-ups (after round 1, 27 Sep 2026)

Round 1 covered the 20 grouped case studies and the 18 Last-Day reviews plus the trigger sheet.

- 363 checkable claims were extracted: see `claims-round1.csv`.
- All 220 high- and medium-priority claims were verified against official docs and papers.
- 128 text corrections were applied.
- Sources were added to each group's full pack and to the Last-Day modules.

## Round 2 — done 27 Sep 2026
Everything in the round 2 scope was checked. That's 214 claims, in `verdicts-round2.json`. The main fixes:
- Idempotency-key reuse is `422`, and a retry still in flight is `409`. This follows the IETF Idempotency-Key draft -07, which has expired and isn't an RFC. The pages say so (cases 23, 25, 26). A stale version sent in the body stays `409`; an `If-Match` header would give `412`.
- FedRAMP covers cloud services only. On-prem products carry Common Criteria (NIAP) and DISA STIGs (case 19).
- Case 61's cost table: Haiku 4.5 won't cache a prefix under 4,096 tokens, so only the Sonnet share gets the caching discount. The table is recomputed (about 45% cut, not "halve").
- Google Drive: folders with limited access block inherited permissions (G01, all three copies).
- Microsoft 365 Copilot is the only public ~$30 seat price. ChatGPT Enterprise has no public price, and Claude Enterprise charges a seat fee plus usage (case 26).
- Works councils in Germany and the Netherlands must agree, not just be consulted (case 26).
- Fine-tuning "rarely", not "never", fixes missing knowledge (case 80). OAuth is authorisation only, so identity comes from SSO via OpenID Connect (case 14).
- Behavioural answers: Vector Search is now AI Search, and Genie Spaces are now Genie Agents, where the story speaks in the present tense.

## Unsettled after round 2 (low risk, left as is)
- C335 (G17 "most candidates fumble"): credited to the purchased question bank, which isn't in the repo.
- Case 14: the quote from iGrace's page can't be fetched (it only renders in a browser).
- Case 19: ITAR/EAR access. It's standard, and already hedged with "could".
- Decomposition Classics: the ~120-day card dispute window rests on secondary sources, because the Visa and Mastercard rule books aren't public.
- Behavioural "20+ tools degrades selection": the candidate's own test result. Anthropic's docs put the threshold at 30–50.
- Behavioural answers still say "Vector Search" and "Genie Space(s)" where the story is in the past tense or inside `[FILL]` markers. That's deliberate.

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
- Prices dated "checked Sep 2026": Claude Sonnet 5 at $2/$10 and Haiku 4.5 at $1/$5 (case 61, whose table depends on them), GPT-4o mini and GPT-4o list prices (case 100, labelled illustrative), Microsoft 365 Copilot at $30 (case 26), and S3 and gp3 storage (case 23).
- IETF Idempotency-Key draft: if it becomes an RFC or changes its codes, update cases 23, 25 and 26.
- Claude Haiku 4.5: retirement "not sooner than 15 Oct 2026". Recheck the G18 pricing example and the case 61 cost table (which routes 70% of traffic to Haiku 4.5) after that date.
- Zendesk API tokens: no new tokens from 27 Oct 2026, all switched off 30 Apr 2027 (G12).
- Groq `llama-3.1-8b-instant` was shut down for free and developer tiers on 16 Aug 2026 (G11).
- Databricks renames of mid-2026: Vector Search → AI Search, Genie → Genie One, Genie Spaces → Genie Agents, AI Gateway → Unity Gateway. Expect more doc and name churn.

## Found during CONTENT-17 (27 Sep 2026)
All fixed; see "Loose ends — all closed" above.
