# Fact-check follow-ups (after round 1, 27 Sep 2026)

Round 1 covered the 20 grouped case studies and the 18 Last-Day reviews plus the trigger sheet.

- 363 checkable claims were extracted: see `claims-round1.csv`.
- All 220 high- and medium-priority claims were verified against official docs and papers.
- 128 text corrections were applied.
- Sources were added to each group's full pack and to the Last-Day modules.

## Round 2 scope (not yet checked)
- The 143 low-priority claims in `claims-round1.csv`.
- The 13 standalone cases (`Case_Study_Groups/Standalone/`).
- The 22 practice worksheets and model answers.
- The Roadmap and the Rapid Revision Guide.
- The behavioural model answers (factual claims only).

## Found outside round 1's files — fix in round 2
- `Standalone/25_Configurable_Platform_Customer_Workflows/3_Tutorial_V2.md:507`: check whether the "409 Conflict" use there is an ETag/If-Match case (that should be 412) or a genuine conflict.
- `Handbook/04_Enterprise_RAG/06_Output_Guardrails.md:24` and both copies of `nodes.py`: "most common over-refusal" should say "a common" (C158).
- The study guide quoted by G18 says the first token arrives "in milliseconds"; it should be "well under a second" (C149).
- `05_Projects/Realtime_Voice_AI_Agent_with_RAG/Docs/PROJECT_REPORT.md:60` says Deepgram Nova-2. The code actually runs Nova-3 (Pipecat's default), and Deepgram now recommends Flux (C077).
- G15 quotes a Handbook passage on Redis locks inside a blockquote. The quote was corrected to add a fencing token, so the Handbook source should get the same fix so they match again (C098).

## Decisions for the owner
- **DevRev (C078).** G15 names DevRev and a "DevRev system-design prep document" as its prompt's source. There is no public source and the file isn't in the repo. Should it be anonymised, as the client stories were?
- **G11 "Research Platform".** It closely matches public third-party GitHub repos (multi-agent research platforms). Check that it isn't presented as the owner's own original build.

## Recheck dates (time-bombs)
- Claude Haiku 4.5: retirement "not sooner than 15 Oct 2026". Recheck the G18 pricing example after that date.
- Zendesk API tokens: no new tokens from 27 Oct 2026, all switched off 30 Apr 2027 (G12).
- Groq `llama-3.1-8b-instant` was shut down for free and developer tiers on 16 Aug 2026 (G11).
- Databricks renames of mid-2026: Vector Search → AI Search, Genie → Genie One, Genie Spaces → Genie Agents, AI Gateway → Unity Gateway. Expect more doc and name churn.
