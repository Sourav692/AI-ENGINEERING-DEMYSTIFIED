# Module 04 · Enterprise RAG

> **Level** 🟡 Building Production Systems · **Docs** 10 · **Time** ~5.5 h reading + 4–6 h lab
> **Prerequisites:** Module 01 (RAG concepts, LangGraph), Module 03 (robustness patterns)
> **Lab:** `project/` — Meridian Assist. Needs `OPENAI_API_KEY` in a `.env` at the project root; a full run of the golden set costs a few cents.

This module is the **Meridian Assist** project taught as a course. It is an enterprise RAG platform built around the problem that actually makes enterprise RAG hard: *not everyone is allowed to read everything, so the same question has different correct answers for different people.* You will learn attribute-based access control enforced at two layers, a permission-aware ingestion pipeline, six swappable retrieval strategies, an eight-node LangGraph query pipeline, output guardrails, an evaluation harness with a zero-leak release gate, and full run tracing — and you will run every one of them.

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [Why Enterprise Changes the Problem](01_Why_Enterprise_Changes_The_Problem.md) | The Meridian case; the three access-control patterns and why post-filtering fails twice; partition by tenant + pre-filter + post-check; "groups overlap" | 35 min |
| 2 | [Access Control with ABAC](02_Access_Control_ABAC.md) | Physical/logical vs Layer 1/Layer 2; every field; the seven checks in order with real output; obligations; the visibility matrix; four worked documents | 60 min |
| 3 | [The Ingestion Pipeline](03_Ingestion_Pipeline.md) | Content and permissions as two feeds; refuse-don't-default; the ACL catalog vs the index copy; second connector, incremental sync, DLQ; two real bugs | 35 min |
| 4 | [Retrieval — Hybrid, Expansion, Rerank](04_Retrieval_Hybrid_Rerank.md) | Six strategies behind one signature; BM25 over the authorised pool; the asymmetric enterprise strategy; rerank after enforce; reading the comparison table honestly | 35 min |
| 5 | [The Query Graph](05_The_Query_Graph.md) | Eight nodes and the ordering encoded in edges; the response-cache key; degradation everywhere; fail closed on authorisation | 40 min |
| 6 | [Output Guardrails](06_Output_Guardrails.md) | Sufficiency with a partial verdict; citations as disclosures; groundedness; refusal hygiene; why there is no injection check | 20 min |
| 7 | [Evaluation — Golden Sets, Judges and the Gate](07_Evaluation_Golden_Sets_Judges.md) | Three families kept separate; security as a gate not a metric; judge calibration; five war stories | 35 min |
| 8 | [Observability](08_Observability.md) | The `RunTrace`; three audiences, one artefact; cost by purpose; prompt version on every run | 20 min |
| 9 | [Module Reference](09_Module_Reference.md) | Every function in `src/enterprise_rag`, grouped by concept | reference |
| 10 | [Coverage Map](10_Coverage_Map.md) | What is proven in code vs what is cheat-sheet; what to say for each gap | 25 min |

## The lab — eleven notebook parts

`project/notebooks/02-hands-on-parts/` builds every component step by step. Each part pairs with a document:

| Part | Builds | Read first |
|---|---|---|
| 01 · corpus and permissions | The 22 documents, the manifest, the 9 personas | Doc 1 |
| 02 · policy engine | The seven rules, `decide()`, obligations | Doc 2 |
| 03 · compiling policy to filter | Layer 1 — `compile_prefilter()` and the `grp__*` columns | Doc 2 |
| 04 · chunking and ingestion | Heading-aware chunking; ingest into Chroma and the catalog | Doc 3 |
| 05 · hybrid search | Dense, BM25 over the allowed pool, RRF | Doc 4 |
| 06 · query transformation | Multi-query, HyDE, decomposition | Doc 4 |
| 07 · reranking | LLM and cross-encoder rerankers; why after enforce | Doc 4 |
| 08 · full graph | The eight nodes end to end | Doc 5 |
| 09 · attacking it | Prompt injection, the other-tenant attacker, embargo, live revocation | Docs 2, 6 |
| 10 · evaluation | The harness, the gate, the strategy comparison | Doc 7 |
| 11 · observability and takeaways | The trace; timeline; what to say | Doc 8 |

Quick start:

```bash
cd project
pip install -r requirements.txt
# put OPENAI_API_KEY=sk-... in ./.env
python scripts/ingest.py                              # build the index (~seconds, ~$0.0001)
python scripts/demo_access_control.py --matrix        # the visibility matrix — no LLM cost
python scripts/ask.py --user u_marco_t3 "Why did EU ingest degrade on 14 March?"
python scripts/evaluate.py --kinds security           # the release gate
python -m pytest -m "not llm"                         # 62 fast tests
```

Module 08 covers the Databricks variant (`project/notebooks/04-databricks-enterprise-rag.ipynb`, `project/databricks/`).

## Checkpoint

You are ready for Module 05 when you can:

- Explain the two failures of post-filtering and why the project's post-check is not post-filtering.
- Draw the seven ABAC checks in order and say which four things cannot be pushed into the index.
- Draw the eight-node graph and state the ordering property encoded in its edges.
- Say why security is a gate, not a metric, and tell the false-alarm story.
- Point at the file and function for any ✅ row of the coverage map.

**Next →** [Module 05 · Agentic Workflow Platforms](../05_Agentic_Workflow_Platforms/README.md)
