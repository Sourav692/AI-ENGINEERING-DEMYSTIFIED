<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 12 — Production & Observability

**Owns:** running LLM systems in production. Stage `03_Advanced/` — it needs a working system to operate on.

| Track | State | Content |
|---|---|---|
| `LLMOps_and_AI_Infrastructure/` | Partially built | `Tracing_and_Observability/` (LangSmith built, LangFuse planned, callbacks), `Caching_and_Performance/`, `Cost_Monitoring/` |
| `Safety_and_Alignment/` | Built | Content moderation, red teaming (`deepteam`) |
| `Production_Course_Ops/` | Built | Merged-in production-course ops material |
| `DevOps_and_Deployment/`, `Security_and_Compliance/` | Planned | |

## Conventions here

- Needs the `eval` extra for the observability stack (mlflow, arize-phoenix, pyrit).
- 14 notebooks.

## Don't

- **Don't add model/agent evaluation here.** Tracing and observability are this phase's; *evaluation* lives in the sibling repo `Agent_Evaluation_Demystified`. The line: if it measures answer quality it is evaluation, if it measures system behaviour it is observability.
- Note the Arize tracing labs live with their eval course in that sibling repo, not here — kept with their course deliberately.
