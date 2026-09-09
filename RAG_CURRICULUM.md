# RAG Curriculum - Reorganization Plan

- **Status:** Planning document only; notebook reorganization has not started.
- **Audit date:** September 9, 2026.
- **Scope of this change:** Create this plan file only. Moving, merging, rewriting, or archiving notebooks requires a separate go-ahead.
- **Recommendation:** Build a concept-first RAG curriculum with one authoritative active teaching notebook per concept. Preserve unique material and retain recoverable originals rather than permanently deleting content.

## Contents

1. [Audit findings and limitations](#1-audit-findings-and-limitations)
2. [Organization principles](#2-organization-principles)
3. [Proposed learning structure](#3-proposed-learning-structure)
   - [Target product structure](#target-product-structure)
   - [Folder and notebook coverage](#folder-and-notebook-coverage)
4. [Preferred canonical sources](#4-preferred-canonical-sources)
5. [Anthologies, nested sources, and project boundaries](#5-anthologies-nested-sources-and-project-boundaries)
6. [Standard structure for each canonical notebook](#6-standard-structure-for-each-canonical-notebook)
7. [Dependency-preservation plan](#7-dependency-preservation-plan)
8. [Implementation sequence after approval](#8-implementation-sequence-after-approval)
9. [Acceptance checklist](#9-acceptance-checklist)
10. [Approval scope and exclusions](#10-approval-scope-and-exclusions)
11. [Sources and repository references](#11-sources-and-repository-references)

## 1. Audit findings and limitations

The read-only audit inventoried notebook files across the repository and inspected notebook sources, markdown structure, imports, asset references, supporting helpers, and repository indexes. It compared lesson content and notebook hashes without executing the notebooks.

### Inventory snapshot

| Finding                                                                | Audit result                                                     |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Notebook files discovered                                              | 632                                                              |
| Notebook files parseable as JSON                                       | 631                                                              |
| Foundational RAG notebooks in`04_Retrieval_and_RAG/`                 | 74                                                               |
| Advanced RAG notebooks outside the nested source checkout              | 52                                                               |
| Notebooks inside the nested`RAG_TECHNIQUES` checkout                 | 46                                                               |
| Byte-identical Enterprise RAG notebook pairs                           | 13 pairs between the handbook and interview-preparation projects |
| Notebook titles in the nested checkout absent from the outer anthology | 9; a new title is not necessarily a new concept                  |
| Zero-byte notebook files                                               | 1 project notebook                                               |

These are the audit's final inventory counts, not a continuously updated inventory. The folder counts are subsets of the repository total. Re-scan before implementation because the working tree is changing.

### Main findings

- Basic RAG, embeddings, chunking, hybrid retrieval, query transformations, reranking, and evaluation have substantial conceptual overlap across courses and phases.
- The handbook and interview-preparation Enterprise RAG projects contain 13 byte-identical notebook pairs. The handbook project should become the authoritative enterprise example, with interview-preparation links instead of duplicate lessons.
- The nested checkout contains material absent from the outer anthology, including LightRAG, MemoRAG, graph attribution, and additional evaluation examples. Do not discard it as an entirely redundant copy.
- The [question-answering project placeholder][empty-qa-project] is zero bytes. The [short multimodal project placeholder][empty-multimodal-project] contains an empty code cell. Neither should count as a completed lesson.
- Some document references are already fragile or incorrect. For example, loaders reference `../../data/dummy.txt` and `../../docs/layoutparser_paper.pdf`, while those assets live in `04_Retrieval_and_RAG/shared_data/`. The [notebook index][notebook-index] already records this issue in its known discrepancies.
- The existing `semantic_chunking.ipynb` changed during the audit. At plan-creation time, there are also working-copy changes to `1-densesparse.ipynb` and `Reference_Links.md`, along with untracked local settings and the nested checkout. Preserve the current working state; do not overwrite it with an older audited copy.

### What the audit did not verify

- No notebooks were executed, packages installed, or database/cloud services contacted.
- JSON parseability is not proof of notebook-schema validity, sequential execution, or API compatibility.
- Literal-path checks identify candidates for investigation, not an exact count of broken inputs. Some references describe generated files, downloads, metadata, or external-service resources.
- No blanket claim is made that the current notebooks or the proposed merged versions run successfully under the repository's pinned environment.

## 2. Organization principles

### One concept, one active lesson

A concept has a specific learning objective, such as semantic chunking, HyDE, or parent-document retrieval. Course provenance, filenames, model providers, and framework names do not automatically create new concepts.

- Give every canonical lesson a stable concept ID and exactly one active notebook path.
- Combine equivalent LangChain/LlamaIndex implementations into clearly separated implementation sections or supporting examples within the same lesson.
- Keep genuinely distinct algorithms separate. Do not collapse RAG-Fusion into hybrid search, HyDE into HyPE, parent-document retrieval into context-window enrichment, or CRAG into Self-RAG.
- Separate query-type-adaptive retrieval from an adaptive corrective graph when their learning objectives and control flow differ.
- Allow a separate platform/deployment lesson only when it teaches a distinct concern, such as authorization enforcement, rather than merely swapping a provider.
- Let projects apply several concepts, but link to canonical lessons instead of repeating their complete teaching material.
- Exclude archived source notebooks from the active curriculum index and uniqueness checks.

### Preserve insight, not duplication

For each overlapping group:

1. Choose the strongest conceptual explanation, not simply the largest file, newest filename, or notebook with the most saved output.
2. Preserve useful implementations, comparisons, exercises, diagrams, and failure cases from other sources.
3. Use the stronger implementation where appropriate without discarding the richer explanation.
4. Remove repeated setup and repeated explanations from the active lesson.
5. Record where unique material went and preserve recoverable originals.

Selection should consider conceptual depth first, then implementation completeness, meaningful comparisons, limitations, exercises, and reproducibility. Compatibility must be checked before a candidate becomes a validated canonical lesson. Saved execution counts are not sufficient evidence.

**One active notebook per concept does not mean permanent deletion of source material.**

## 3. Proposed learning structure

Keep foundational RAG and advanced RAG as separate phases. This is an explicit repository decision in [CLAUDE.md][repo-guidance]. Improve organization inside those phases rather than merging Phase 4 and Phase 8 into a new competing home.

| Learning stage                   | Canonical concepts                                                                                                                                                                                      | Home                                             |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| RAG foundations                  | RAG lifecycle and baseline pipeline; document loading and metadata; embeddings; vector-store operations; structured-data retrieval                                                                      | Phase 4                                          |
| Chunking and indexing            | Structural/token chunking; semantic chunking; proposition chunking; chunk-size experiments; incremental indexing; parent-document retrieval; multi-representation indexing; document augmentation; HyPE | Phase 4                                          |
| Retrieval strategies             | Dense/sparse retrieval; metadata filtering; hybrid search; MMR; reranking; Dartboard retrieval                                                                                                          | Phase 4                                          |
| Query transformation and routing | Rewriting/expansion; multi-query; RAG-Fusion; decomposition; step-back prompting; HyDE; classifier routing; semantic routing; self-querying                                                             | Phase 4                                          |
| Context and generation           | Context windows; compression; contextual headers/retrieval; relevant-segment extraction; explainable retrieval; citations; conversational and multi-user RAG                                            | Phase 4                                          |
| Evaluation                       | Deterministic retrieval metrics; contextual metrics; answer quality/groundedness; golden datasets; in-pipeline and end-to-end evaluation; evaluator calibration                                         | Phase 7's RAG evaluation track                   |
| Agentic RAG                      | Retrieval as a tool; domain-router RAG; corrective RAG; adaptive RAG; Self-RAG; feedback-driven retrieval                                                                                               | Phase 8                                          |
| Advanced architectures           | Hierarchical retrieval/RAPTOR; memory-guided retrieval; knowledge-graph construction; graph retrieval; Microsoft GraphRAG; LightRAG; verifiable graph attribution                                       | Phase 8                                          |
| Multimodal RAG                   | Captioning/multi-vector retrieval; shared text/image embedding retrieval; visual retrieval with ColPali                                                                                                 | Phase 8                                          |
| Production and applications      | Access control; security testing; governed Databricks deployment; observability; integrated capstones                                                                                                   | Existing production, handbook, and project homes |

These are stages and folders, not giant all-in-one notebooks. Each distinct technique receives its own canonical lesson. Final concept IDs and source-to-target paths will be recorded in the migration manifest; do not force an arbitrary final notebook count before that mapping is complete.

After implementation, this document should become the learner-facing route across the canonical homes, with links, prerequisites, and runtime requirements. Until then, it remains a proposal. Preserve the existing ownership of general agent, memory, evaluation, and production concepts rather than creating a second RAG-specific copy of every supporting topic.

### Target product structure

The following is the proposed product structure for the reorganized curriculum. It is a target layout, not a claim that these folders or destination notebooks already exist. Existing notebooks remain in place until the migration is approved, mapped, and validated.

```text
RAG_Curriculum/
├── 00_Curriculum_Guide/
│   ├── README.md
│   └── RAG_Curriculum_Map.ipynb
├── 01_Foundations/
│   ├── 01_RAG_Lifecycle_and_Baseline.ipynb
│   ├── 02_Document_Loading_and_Metadata.ipynb
│   ├── 03_Embeddings_and_Model_Selection.ipynb
│   ├── 04_Vector_Stores_and_Index_Operations.ipynb
│   └── 05_Structured_Data_RAG.ipynb
├── 02_Chunking_and_Indexing/
│   ├── 01_Document_Splitting_and_Chunking.ipynb
│   ├── 02_Semantic_Chunking.ipynb
│   ├── 03_Proposition_Chunking.ipynb
│   ├── 04_Choosing_Chunk_Size.ipynb
│   ├── 05_Incremental_Indexing_and_Record_Management.ipynb
│   ├── 06_Parent_Document_Retrieval.ipynb
│   ├── 07_Multi_Representation_Indexing.ipynb
│   ├── 08_Document_Augmentation.ipynb
│   └── 09_HyPE_Hypothetical_Prompt_Embeddings.ipynb
├── 03_Retrieval/
│   ├── 01_Dense_and_Sparse_Retrieval.ipynb
│   ├── 02_Metadata_Filtering_and_Self_Query.ipynb
│   ├── 03_Hybrid_Search.ipynb
│   ├── 04_MMR_and_Diversity_Retrieval.ipynb
│   ├── 05_Reranking_and_Contextual_Compression.ipynb
│   └── 06_Dartboard_and_Diverse_Passage_Selection.ipynb
├── 04_Query_Transformation_and_Routing/
│   ├── 01_Query_Rewriting_and_Expansion.ipynb
│   ├── 02_Multi_Query.ipynb
│   ├── 03_RAG_Fusion.ipynb
│   ├── 04_Query_Decomposition.ipynb
│   ├── 05_Step_Back_Prompting.ipynb
│   ├── 06_HyDE_Hypothetical_Document_Embeddings.ipynb
│   ├── 07_Classifier_Routing.ipynb
│   └── 08_Semantic_Routing.ipynb
├── 05_Context_and_Generation/
│   ├── 01_Context_Windows_and_Neighboring_Chunks.ipynb
│   ├── 02_Contextual_Chunk_Headers_and_Retrieval.ipynb
│   ├── 03_Contextual_Compression.ipynb
│   ├── 04_Relevant_Segment_Extraction.ipynb
│   ├── 05_Explainable_Retrieval_and_Evidence.ipynb
│   ├── 06_Citations_and_Source_Grounded_Answers.ipynb
│   └── 07_Conversational_and_Multi_User_RAG.ipynb
├── 06_Evaluation/
│   ├── 01_Deterministic_Retrieval_Metrics.ipynb
│   ├── 02_LLM_Judged_Retrieval_Metrics.ipynb
│   ├── 03_Generator_Quality_and_Faithfulness.ipynb
│   ├── 04_RAGAS_and_DeepEval_in_Practice.ipynb
│   ├── 05_Golden_Datasets_and_Synthetic_Testing.ipynb
│   ├── 06_End_to_End_RAG_Evaluation.ipynb
│   └── 07_Evaluator_Calibration_and_Meta_Evaluation.ipynb
├── 07_Agentic_RAG/
│   ├── 01_Retrieval_as_an_Agent_Tool.ipynb
│   ├── 02_Domain_Router_Agentic_RAG.ipynb
│   ├── 03_Corrective_RAG_CRAG.ipynb
│   ├── 04_Adaptive_RAG.ipynb
│   ├── 05_Self_RAG.ipynb
│   └── 06_Feedback_Driven_Retrieval.ipynb
├── 08_Advanced_Architectures/
│   ├── 01_Hierarchical_Retrieval_and_RAPTOR.ipynb
│   ├── 02_Memory_Guided_RAG.ipynb
│   ├── 03_Knowledge_Graph_Construction.ipynb
│   ├── 04_Graph_RAG_Fundamentals.ipynb
│   ├── 05_Microsoft_Community_GraphRAG.ipynb
│   ├── 06_LightRAG.ipynb
│   └── 07_Graph_Attribution_and_Verifiable_Provenance.ipynb
├── 09_Multimodal_RAG/
│   ├── 01_Captioning_and_Multi_Vector_Retrieval.ipynb
│   ├── 02_Shared_Image_Text_Embeddings.ipynb
│   ├── 03_Visual_Retrieval_with_ColPali.ipynb
│   └── 04_Late_Interaction_Retrieval_with_ColBERT.ipynb
├── 10_Production_RAG/
│   ├── 01_Enterprise_Access_Control_and_ACL_Retrieval.ipynb
│   ├── 02_RAG_Security_and_Red_Teaming.ipynb
│   ├── 03_Governed_Databricks_RAG.ipynb
│   ├── 04_Observability_and_Release_Gates.ipynb
│   └── 05_Local_and_Provider_Agnostic_RAG.ipynb
├── 11_Applications_and_Capstones/
│   ├── 01_Document_Search_Engine.ipynb
│   ├── 02_Healthcare_Router_RAG.ipynb
│   ├── 03_ShopUNow_Agentic_RAG.ipynb
│   ├── 04_Enterprise_RAG_Platform.ipynb
│   └── 05_Research_Assistant_RAG.ipynb
├── _support/
│   ├── shared_data/
│   ├── helpers/
│   ├── evaluation_data/
│   └── environment_and_path_manifest.md
└── _archive/
    └── source_notebooks_preserved_by_migration_manifest/
```

The folders have deliberate boundaries. `01` teaches the reusable RAG building blocks; `02` changes what is indexed; `03` changes how candidates are selected; `04` changes the query before retrieval; `05` changes the context supplied to generation; `06` measures quality; `07` adds control loops and tools; `08` covers graph, hierarchy, and memory architectures; `09` handles image/document modalities; `10` handles production constraints; and `11` keeps end-to-end applications with their coupled data and code. `_support` contains dependencies rather than lessons, while `_archive` is recoverable history and is excluded from the active curriculum.

### Folder and notebook coverage

Each row below describes one proposed active notebook. The source column identifies the strongest existing material to consolidate; it does not authorize moving or deleting that source. Donor notebooks that contain unique examples should be mined into the target and then recorded in the future migration manifest.

#### `00_Curriculum_Guide/`

| Proposed notebook            | Topics and learning outcomes                                                                                           | Existing source or guidance                                                                                           |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `RAG_Curriculum_Map.ipynb` | Prerequisite graph, concept IDs, canonical lesson links, environment choices, and a small end-to-end orientation demo. | Build from the stage map in this document and`[rag-comprehensive]`; navigation only, not a second technical lesson. |

#### `01_Foundations/`

| Proposed notebook                               | Topics and learning outcomes                                                                                                                                            | Existing source or guidance                                                                                     |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `01_RAG_Lifecycle_and_Baseline.ipynb`         | Ingest, split, embed, index, retrieve, prompt, generate; inspect retrieved evidence; establish a minimal baseline and failure modes.                                    | `[rag-comprehensive]`, with unique material from `[rag-overview]` and `[rag-pipeline]`.                   |
| `02_Document_Loading_and_Metadata.ipynb`      | Text, Markdown, CSV, JSON, PDF, Word, directory, URL, YouTube, research-paper, and custom loaders; metadata contracts and provenance.                                   | `[loader-lessons]`; retain format-specific examples without creating a lesson per file format.                |
| `03_Embeddings_and_Model_Selection.ipynb`     | Embedding intuition, dimensions, normalization, batching, caching, provider configuration, similarity inspection, and model trade-offs.                                 | `[embedding-basics]`, `[openai-embeddings]`, `[embeddings-deep]`; benchmarking remains a focused section. |
| `04_Vector_Stores_and_Index_Operations.ipynb` | Collections, persistence, upsert/delete, similarity search, filters, retriever adapters, and backend trade-offs across Chroma, FAISS, PostgreSQL, Pinecone, and others. | `[vector-stores]`; backend examples become comparisons, not duplicate introductions.                          |
| `05_Structured_Data_RAG.ipynb`                | CSV/JSON records, schema-aware retrieval, structured filters, serialization boundaries, and limitations of treating tables as plain text.                               | `simple_csv_rag.ipynb`, `json_rag.ipynb`, and structured-data sections from existing baseline donors.       |

#### `02_Chunking_and_Indexing/`

| Proposed notebook                                       | Topics and learning outcomes                                                                                                                 | Existing source or guidance                                                                                                                             |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `01_Document_Splitting_and_Chunking.ipynb`            | Recursive, token, character, fixed, sliding-window, Markdown, code, and structural splitters; overlap and metadata.                          | `[chunking-comprehensive]` plus `[text-splitters]`.                                                                                                 |
| `02_Semantic_Chunking.ipynb`                          | Embedding-based boundaries, threshold selection, inspection, cost/latency trade-offs, and failure cases.                                     | `[semantic-chunking]` and `[semantic-chunking-manual]`.                                                                                             |
| `03_Proposition_Chunking.ipynb`                       | Atomic factual propositions, proposition generation, indexing, retrieval behavior, and precision/completeness trade-offs.                    | `proposition_chunking.ipynb`.                                                                                                                         |
| `04_Choosing_Chunk_Size.ipynb`                        | Experimental comparison of chunk size, latency, faithfulness, relevancy, and task-specific selection.                                        | `choose_chunk_size.ipynb`.                                                                                                                            |
| `05_Incremental_Indexing_and_Record_Management.ipynb` | Stable IDs, upsert/delete, changed documents, cleanup, re-indexing, and repeatable index lifecycle.                                          | `7.3_Indexing_API.ipynb`; keep application-specific setup separate.                                                                                   |
| `06_Parent_Document_Retrieval.ipynb`                  | Small child chunks for matching, larger parent/full-document return, parent-child stores, context assembly, and a PostgreSQL implementation. | `[parent-document]`, `[postgres-parent]`, and the parent section of `07_advanced_rag.ipynb`; this is the single canonical parent-document lesson. |
| `07_Multi_Representation_Indexing.ipynb`              | Summary or alternate representation embeddings mapped back to original documents; representation quality and provenance.                     | `Multi_Representation_Indexing.ipynb`.                                                                                                                |
| `08_Document_Augmentation.ipynb`                      | Generate questions or metadata to improve recall, index-time augmentation, deduplication, and hallucination risks.                           | `document_augmentation.ipynb`.                                                                                                                        |
| `09_HyPE_Hypothetical_Prompt_Embeddings.ipynb`        | Generate hypothetical questions at index time, embed them, map hits to source documents, and distinguish HyPE from query-time HyDE.          | `HyPE_Hypothetical_Prompt_Embeddings.ipynb`.                                                                                                          |

#### `03_Retrieval/`

| Proposed notebook                                    | Topics and learning outcomes                                                                                          | Existing source or guidance                                                                                                                                          |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `01_Dense_and_Sparse_Retrieval.ipynb`              | Dense vectors, lexical/BM25 retrieval, scoring, thresholds, top-k, and when each signal fails.                        | `[dense-sparse]` and retriever lessons in `02_Embeddings_and_Vector_Databases`.                                                                                  |
| `02_Metadata_Filtering_and_Self_Query.ipynb`       | Metadata predicates, filter compilation, self-querying, security boundaries, and filtered recall.                     | `[self-querying]`, `7.2_Filtered_Search.ipynb`, and `[nested-filtering]`; self-query is taught here as a retrieval interface, not duplicated in query routing. |
| `03_Hybrid_Search.ipynb`                           | Dense+sparse fusion, reciprocal-rank-style combinations, score normalization, backend implementation, and evaluation. | `[hybrid-rag]`; preserve comparisons from `7_Hybrid_Search_and_Reranking`.                                                                                       |
| `04_MMR_and_Diversity_Retrieval.ipynb`             | Relevance/diversity objective, lambda tuning, redundancy inspection, and use in multi-document context.               | `3-mmr.ipynb` and retriever donors.                                                                                                                                |
| `05_Reranking_and_Contextual_Compression.ipynb`    | Cross-encoder reranking, LLM reranking, document compression, ordering, and cost/latency decisions.                   | `[reranking]`, `10_RerankingCrossEncoder.ipynb`, and contextual compression anthology sources.                                                                   |
| `06_Dartboard_and_Diverse_Passage_Selection.ipynb` | Dartboard relevance/diversity selection, passage coverage, comparison with MMR, and context-budget behavior.          | `dartboard.ipynb`; keep it distinct from generic MMR.                                                                                                              |

#### `04_Query_Transformation_and_Routing/`

| Proposed notebook                                  | Topics and learning outcomes                                                                                                         | Existing source or guidance                                                                    |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| `01_Query_Rewriting_and_Expansion.ipynb`         | Rewrite ambiguous queries, add terminology, preserve intent, and inspect recall/precision changes.                                   | `1-queryexpansion.ipynb`, `6. query_transformations.ipynb`, and `7_BetterQueries.ipynb`. |
| `02_Multi_Query.ipynb`                           | Generate multiple query perspectives, retrieve independently, merge evidence, and analyze redundancy.                                | `[multi-query]`.                                                                             |
| `03_RAG_Fusion.ipynb`                            | Query generation plus rank fusion, reciprocal-rank reasoning, and distinction from dense/sparse hybrid search.                       | `[rag-fusion]`; preserve as its own concept.                                                 |
| `04_Query_Decomposition.ipynb`                   | Break multi-hop questions into subqueries, sequence retrieval, synthesize evidence, and handle dependency failures.                  | `[decomposition]` and `2-querydecomposition.ipynb`.                                        |
| `05_Step_Back_Prompting.ipynb`                   | Move from specific question to abstract principle, retrieve general context, and combine with the original question.                 | `[step-back]`.                                                                               |
| `06_HyDE_Hypothetical_Document_Embeddings.ipynb` | Generate a hypothetical answer/document at query time, embed it, retrieve real evidence, and compare with direct retrieval and HyPE. | `[hyde]` and `3-HyDE.ipynb`.                                                               |
| `07_Classifier_Routing.ipynb`                    | Classify query type/domain, select retriever or workflow, define fallback behavior, and measure routing errors.                      | `[classifier-routing]` and router-RAG donors.                                                |
| `08_Semantic_Routing.ipynb`                      | Route by semantic similarity to prompt/examples, compare to LLM classification, and inspect ambiguous routes.                        | `[semantic-routing]`.                                                                        |

#### `05_Context_and_Generation/`

| Proposed notebook                                   | Topics and learning outcomes                                                                                                               | Existing source or guidance                                                                                           |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `01_Context_Windows_and_Neighboring_Chunks.ipynb` | Expand around a retrieved chunk, preserve neighboring order, manage token budgets, and distinguish windows from parent-document retrieval. | `context_enrichment_window_around_chunk.ipynb` and its LlamaIndex variant.                                          |
| `02_Contextual_Chunk_Headers_and_Retrieval.ipynb` | Add document title/header context and compare lightweight headers with full per-chunk contextual retrieval.                                | `contextual_chunk_headers.ipynb` and the contextual-retrieval RAG lesson.                                           |
| `03_Contextual_Compression.ipynb`                 | Extract query-relevant spans, compress documents, preserve evidence, and measure lost context.                                             | `contextual_compression.ipynb` and post-processing donors.                                                          |
| `04_Relevant_Segment_Extraction.ipynb`            | Reconstruct contiguous passages from scored chunks, resolve gaps, and compare segment extraction with independent top-k chunks.            | `relevant_segment_extraction.ipynb`.                                                                                |
| `05_Explainable_Retrieval_and_Evidence.ipynb`     | Show why passages were selected, expose scores/metadata, highlight evidence, and communicate limitations.                                  | `explainable_retrieval.ipynb` and `reliable_rag.ipynb`.                                                           |
| `06_Citations_and_Source_Grounded_Answers.ipynb`  | Source IDs, citation formatting, evidence spans, answer verification, and citation failure modes.                                          | `3. Building a RAG System with Sources`, `4. Building a RAG System with Citations`, and `[nested-attribution]`. |
| `07_Conversational_and_Multi_User_RAG.ipynb`      | History-aware retrieval, session isolation, SQL-backed users, permissions boundaries, and conversation-aware prompts.                      | `[conversational-m8]`; the shorter project notebook is a donor, not a second canonical lesson.                      |

#### `06_Evaluation/`

| Proposed notebook                                      | Topics and learning outcomes                                                                                            | Existing source or guidance                                                                              |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `01_Deterministic_Retrieval_Metrics.ipynb`           | Precision@k, recall@k, MRR, nDCG, hit rate, relevance labels, and limitations of deterministic metrics.                 | `[evaluation-drills]` deterministic retrieval lesson.                                                  |
| `02_LLM_Judged_Retrieval_Metrics.ipynb`              | Contextual precision, recall, and relevance; judge prompts, calibration, variance, and cost.                            | `[evaluation-tutorial]`, `1.Retriever_Evaluation_Metrics.ipynb`, and DeepEval metric notebooks.      |
| `03_Generator_Quality_and_Faithfulness.ipynb`        | Answer relevance, faithfulness, groundedness, hallucination detection, reference-based and reference-free assessment.   | Generator metrics lessons and`[evaluation-tutorial]`.                                                  |
| `04_RAGAS_and_DeepEval_in_Practice.ipynb`            | Dataset schemas, RAGAS/DeepEval execution, metric interpretation, and framework limitations.                            | `06_RAGAS_in_Practice`, DeepEval notebooks, and `SigleTurnSample.ipynb`.                             |
| `05_Golden_Datasets_and_Synthetic_Testing.ipynb`     | Question/context/answer goldens, synthetic generation, stratified cases, regression fixtures, and contamination checks. | `4. End_to_End_RAG_System_Evaluation.ipynb` and `[nested-end-to-end]`.                               |
| `06_End_to_End_RAG_Evaluation.ipynb`                 | Evaluate retrieval and generation together inside a pipeline, compare variants, and produce release decisions.          | `05_RAG_Eval_Inside_the_Pipeline`, `07_RAG_Capstone_Build_and_Evaluate`, and `[nested-open-eval]`. |
| `07_Evaluator_Calibration_and_Meta_Evaluation.ipynb` | Judge agreement, rubric calibration, evaluator bias, meta-evaluation, and open evaluation methods.                      | `evaluation_grouse.ipynb` and open-RAG evaluation donors.                                              |

#### `07_Agentic_RAG/`

| Proposed notebook                       | Topics and learning outcomes                                                                                            | Existing source or guidance                                                                                   |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `01_Retrieval_as_an_Agent_Tool.ipynb` | Tool schemas, retrieval invocation, state, generation, grading, retries, and safe fallbacks.                            | `01_Simple_Agentic_RAG`, `02_RAG_as_Tool_in_Agents`, and `[nested-agentic]`.                            |
| `02_Domain_Router_Agentic_RAG.ipynb`  | Domain routing, specialist retrievers, sentiment/escalation, human-in-the-loop, and failure containment.                | Healthcare router project and advanced LangGraph router donors.                                               |
| `03_Corrective_RAG_CRAG.ipynb`        | Grade retrieved documents, rewrite when weak, web/fallback branch, and corrective control flow.                         | `[corrective-rag]` and `[crag-anthology]`.                                                                |
| `04_Adaptive_RAG.ipynb`               | Choose retrieval strategy by query type or confidence, compare to CRAG, and test adaptive policies.                     | `[adaptive-rag]` and `adaptive_retrieval.ipynb`; keep query-type routing distinct from corrective graphs. |
| `05_Self_RAG.ipynb`                   | Retrieve-on-demand, critique tokens/steps, self-evaluation, grounded generation, and control-loop costs.                | `[self-rag]` and `self_rag.ipynb`.                                                                        |
| `06_Feedback_Driven_Retrieval.ipynb`  | Persist user feedback, update relevance/index content, close the feedback loop, and separate feedback from chat memory. | `retrieval_with_feedback_loop.ipynb`.                                                                       |

#### `08_Advanced_Architectures/`

| Proposed notebook                                        | Topics and learning outcomes                                                                                         | Existing source or guidance                                                     |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `01_Hierarchical_Retrieval_and_RAPTOR.ipynb`           | Coarse-to-fine summaries, recursive clustering, tree navigation, and hierarchy failure modes.                        | `hierarchical_indices.ipynb` and `raptor.ipynb`.                            |
| `02_Memory_Guided_RAG.ipynb`                           | Long-term memory as retrieval guidance, memory formation, global context, and distinction from conversation history. | `[nested-memorag]`; do not claim CacheRAG is implemented.                     |
| `03_Knowledge_Graph_Construction.ipynb`                | Entity/relation extraction, schema design, graph loading, quality checks, and Cypher CRUD.                           | `kg_simple.ipynb`, healthcare KG, and entity-relationship extraction sources. |
| `04_Graph_RAG_Fundamentals.ipynb`                      | Graph traversal plus vector retrieval, graph expansion, conversational graph queries, and hybrid evidence.           | `roman_emp_graph_rag.ipynb`, `graph_rag.ipynb`, and Milvus graph sources.   |
| `05_Microsoft_Community_GraphRAG.ipynb`                | Community detection, local/global search, community summaries, indexing stages, and deployment trade-offs.           | `Microsoft_GraphRag.ipynb`; it remains distinct from generic graph RAG.       |
| `06_LightRAG.ipynb`                                    | Lightweight entity/relation indexing, dual-level retrieval, graph traversal, and implementation constraints.         | `[nested-lightrag]`.                                                          |
| `07_Graph_Attribution_and_Verifiable_Provenance.ipynb` | Trace graph paths to claims, expose provenance, generate citations, and test attribution gaps.                       | `[nested-attribution]`.                                                       |

#### `09_Multimodal_RAG/`

| Proposed notebook                                  | Topics and learning outcomes                                                                                    | Existing source or guidance                                                                        |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `01_Captioning_and_Multi_Vector_Retrieval.ipynb` | Caption images, index captions and/or image vectors, retrieve multimodal evidence, and compare representations. | `[multimodal-m8]` and `multi_model_rag_with_captioning.ipynb`.                                 |
| `02_Shared_Image_Text_Embeddings.ipynb`          | Shared embedding space, text-to-image/image-to-text retrieval, preprocessing, and modality mismatch.            | `1-multimodalopenai.ipynb`.                                                                      |
| `03_Visual_Retrieval_with_ColPali.ipynb`         | Page-image embeddings, late interaction, visual document search, and resource constraints.                      | `multi_model_rag_with_colpali.ipynb` and the unique ColBERT material in `rag_ecosystem.ipynb`. |
| `04_Late_Interaction_Retrieval_with_ColBERT.ipynb` | Token-level late interaction, ColBERT indexing/scoring, text retrieval, and distinction from page-image ColPali retrieval. | Unique ColBERT material in `rag_ecosystem.ipynb`; keep separate from ColPali. |

#### `10_Production_RAG/`

| Proposed notebook                                        | Topics and learning outcomes                                                                                              | Existing source or guidance                                                                                          |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `01_Enterprise_Access_Control_and_ACL_Retrieval.ipynb` | Corpus permissions, policy engine, filter compilation, authoritative reread, revocation, and tenant isolation.            | `[enterprise-handbook]`; consolidate the handbook full lesson and parts without leaving duplicate active lessons.  |
| `02_RAG_Security_and_Red_Teaming.ipynb`                | Prompt injection, data exfiltration, retrieval poisoning, citation attacks, threat modeling, and mitigations.             | Enterprise attacks/evaluation parts and`02_Red_Teaming_Agents_and_RAG.ipynb`.                                      |
| `03_Governed_Databricks_RAG.ipynb`                     | Unity Catalog ACL boundaries, Vector Search, filtered retrieval, authoritative reads, PII, revocation, and release gates. | `04-databricks-enterprise-rag.ipynb`; this is a governed deployment lesson, not a duplicate ACL introduction.      |
| `04_Observability_and_Release_Gates.ipynb`             | Traces, latency/cost/error budgets, evaluation gates, regression monitoring, and operational diagnosis.                   | Enterprise observability material and production/observability sources; inspect exact source paths during migration. |
| `05_Local_and_Provider_Agnostic_RAG.ipynb`             | Local embeddings/generation, FAISS, Ollama-style dependencies, offline constraints, and provider substitution.            | `[nested-local]`; providers are compared only when the deployment objective is distinct.                           |

#### `11_Applications_and_Capstones/`

Applications remain coherent bundles. They may link to canonical lessons and demonstrate several concepts, but their application code, data, tests, and setup stay together.

| Proposed notebook or bundle          | Topics and learning outcomes                                                                                           | Existing source or guidance                                                                                                              |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `01_Document_Search_Engine.ipynb`  | Ingestion-to-search application, indexing lifecycle, filters, ranking, and user-facing evidence.                       | `1. Build_Document_Retriever_Search_Engine.ipynb`.                                                                                     |
| `02_Healthcare_Router_RAG.ipynb`   | Domain routing, specialist retrieval, sentiment, escalation, HITL, and production-style failure paths.                 | Advanced LangGraph healthcare router project.                                                                                            |
| `03_ShopUNow_Agentic_RAG.ipynb`    | Two-stage vector database creation followed by agentic retrieval over department data.                                 | `[shopunow]`; preserve the `01_create_vector_databases` → `02_agentic_rag_system` dependency and all seven department JSON files. |
| `04_Enterprise_RAG_Platform.ipynb` | Complete ACL-aware enterprise application, tests, policy enforcement, hybrid retrieval, evaluation, and observability. | `[enterprise-handbook]`; the interview-preparation copy becomes a reference after approval, not a second active lesson.                |
| `05_Research_Assistant_RAG.ipynb`  | Loader, citation, query transformation, multi-step research workflow, and integrated evaluation.                       | `08_research_assistant.ipynb` plus project-specific assets.                                                                            |

#### `_support/` and `_archive/`

| Folder                                        | Contents and rule                                                                                                                           | Existing material                                                                                          |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `_support/shared_data/`                     | PDFs, text, images, CSV/JSON fixtures, and other inputs referenced by multiple lessons; preserve relative relationships through a manifest. | Phase 4`shared_data/` and anthology `data/`/`images/`.                                               |
| `_support/helpers/`                         | Shared Python helpers, evaluation utilities, scripts, and setup modules; version and test them independently of lessons.                    | Anthology`helper_functions.py`, `evaluation/evalute_rag.py`, enterprise `src/`, and project helpers. |
| `_support/evaluation_data/`                 | Goldens, labels, judge prompts, and regression fixtures; keep provenance and licensing metadata.                                            | Phase 7 evaluation assets and nested evaluation folders.                                                   |
| `_support/environment_and_path_manifest.md` | Runtime matrix, package versions, environment variables, asset roots, generated-output policy, and source-to-target dependency mapping.     | To be created only during approved implementation.                                                         |
| `_archive/`                                 | Original notebooks or superseded copies retained with stable source IDs, hashes, and an archive manifest; never imported as active lessons. | Existing duplicate donors, nested checkout, and byte-identical enterprise copies after migration approval. |

This catalogue intentionally does not turn every existing file into an active destination. For example, the 11 loader notebooks become sections of one ingestion lesson, the many backend notebooks become vector-store comparisons, and application notebooks remain bundled projects. A later migration manifest must list every source notebook as `canonical`, `donor`, `application`, `support`, `reference-only`, or `archive-candidate`, and must record the destination concept ID plus every data/helper dependency.

### Explicit coverage of `08_Advanced_RAG/`

The advanced-RAG area was included in the audit and in the proposed mapping. The current snapshot contains **6 top-level folders and 98 notebooks**. The nested `RAG_TECHNIQUES` directory is treated as a source checkout/reference bundle, not as a second active curriculum. Counts should be rechecked immediately before migration.

| Existing folder | Notebook/source coverage in the proposed product | Treatment |
| --- | --- | --- |
| `Comprehensive_RAG_Techniques/all_rag_techniques/` | Baseline RAG, CSV RAG, reliable RAG, chunk-size experiments, proposition chunking, query transformations, HyDE, better queries, adaptive retrieval, context windows, contextual headers/compression, CRAG, Dartboard, augmentation, explainability, fusion, graph RAG, hierarchical indexes, HyPE, Microsoft GraphRAG, captioning, ColPali, RAPTOR, relevant-segment extraction, reranking, feedback loops, Self-RAG, semantic chunking, plus LlamaIndex variants. | Primary advanced-technique donor pool. Consolidate each concept into the corresponding `02`–`09` target folder; framework variants become sections or supporting examples. |
| `Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/` | Includes the outer anthology duplicates plus unique `Agentic_RAG`, local graph attribution, JSON RAG, LightRAG, local HuggingFace/FAISS RAG, MemoRAG, multi-faceted filtering, and additional evaluation notebooks. | Preserve pending dependency mapping. Unique notebooks map to `01`, `03`, `06`, `07`, or `08`; duplicate notebooks remain donor/reference copies rather than active duplicates. |
| `Comprehensive_RAG_Techniques/evaluation/` and nested `RAG_TECHNIQUES/evaluation/` | Evaluation definitions, DeepEval, G-Eval/Grouse-style meta-evaluation, end-to-end evaluation, open-RAG evaluation, completeness, golden benchmarks, judge calibration, hallucination, and citation evaluation. | Consolidate into `06_Evaluation/`; retain helper scripts, test fixtures, and evaluation data under `_support/`. |
| `GraphRAG/` | Knowledge-graph CRUD, healthcare KG construction, manual Cypher through LangChain, vector indexing/embeddings, end-to-end graph-plus-vector RAG, entity/relation extraction, and an incomplete KG-from-text exercise. | Map completed material to `08_Advanced_Architectures/03`–`07`. Keep the incomplete exercise clearly labelled as an exercise/reference source; do not present it as a finished lesson. |
| `RAG_Ecosystem/` | Omnibus RAG ecosystem overview, framework survey, and unique ColBERT material. | Use the overview as navigation/context and move the unique ColBERT insight to `09_Multimodal_RAG/04`; do not create another omnibus active notebook. |
| `RAG_with_LangGraph_Advanced/` | Advanced conversational agent, retrieval-as-tool, healthcare router, CRAG, Adaptive RAG, and Self-RAG. | Map to `07_Agentic_RAG/`; preserve LangGraph implementation as a framework section or application donor. The healthcare router also supports `11_Applications_and_Capstones/02`. |
| `building-adaptive-rag/` | Adaptive-RAG application/protocol implementation files and supporting code. | Keep as an application/support bundle; use only conceptually relevant sections for `07_Agentic_RAG/04`. |
| `CacheRAG/` | Planned CacheRAG area; no completed CacheRAG teaching notebook was verified. | Do not claim coverage or create a canonical lesson until a runnable source exists. Track as planned/missing content. |

The 98-notebook count includes repeated anthology files in the nested checkout. Those repetitions are intentionally accounted for through the donor/reference treatment above; they are not intended to become 98 active lessons. The migration manifest must still enumerate every file individually, including notebooks that are ultimately classified as duplicates, applications, incomplete exercises, or support references.

### Source-to-destination mapping and disposition

This mapping makes the proposed treatment of `08_Advanced_RAG/` explicit. A destination is a proposed canonical location; it does not exist until implementation is approved. `Donor` means useful content is merged into the destination. `Support/reference` means the notebook is retained for code, framework comparison, setup, or provenance but is not indexed as an active concept lesson. `Archive candidate` means it may be moved to recoverable history only after dependency validation and approval. Nothing is deleted by this plan.

#### Mapping legend

| Disposition | Meaning |
| --- | --- |
| `Canonical` | The concept receives the one active teaching notebook at the proposed destination. |
| `Donor` | Content, examples, comparisons, or exercises are consolidated into a canonical notebook. |
| `Support/reference` | Kept outside the active lesson index for helpers, framework variants, setup, provenance, or optional implementation detail. |
| `Application bundle` | Kept with its application code, data, tests, and runtime files; it demonstrates concepts but does not duplicate their lessons. |
| `Incomplete/planned` | Not counted as completed curriculum coverage. |
| `Archive candidate` | Recoverable original or duplicate after the migration manifest and dependency checks pass. |

#### Outer anthology: `Comprehensive_RAG_Techniques/all_rag_techniques/`

| Source notebook(s) | Proposed destination | Disposition and reason |
| --- | --- | --- |
| `1. simple_rag.ipynb`, `simple_rag_with_llamaindex.ipynb` | `01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb` | Donor; retain both framework implementations as optional sections, not duplicate lessons. |
| `2. simple_csv_rag.ipynb`, `simple_csv_rag_with_llamaindex.ipynb` | `01_Foundations/05_Structured_Data_RAG.ipynb` | Donor; consolidate CSV schema and retrieval examples. |
| `3. reliable_rag.ipynb` | `05_Context_and_Generation/05_Explainable_Retrieval_and_Evidence.ipynb` and `06_Evaluation/03_Generator_Quality_and_Faithfulness.ipynb` | Donor; split relevance grading, evidence highlighting, and hallucination checks by learning objective. |
| `4. choose_chunk_size.ipynb` | `02_Chunking_and_Indexing/04_Choosing_Chunk_Size.ipynb` | Canonical source/donor for chunk-size experiments. |
| `5. proposition_chunking.ipynb` | `02_Chunking_and_Indexing/03_Proposition_Chunking.ipynb` | Canonical source/donor. |
| `6. query_transformations.ipynb`, `7_BetterQueries.ipynb` | `04_Query_Transformation_and_Routing/01_Query_Rewriting_and_Expansion.ipynb` | Donor; use as overview and preserve unique query-improvement examples. |
| `7. HyDe_Hypothetical_Document_Embedding.ipynb` | `04_Query_Transformation_and_Routing/06_HyDE_Hypothetical_Document_Embeddings.ipynb` | Donor; combine with the richer dedicated HyDE lesson. |
| `adaptive_retrieval.ipynb` | `07_Agentic_RAG/04_Adaptive_RAG.ipynb` | Donor; preserve query-type strategy routing and distinguish it from CRAG. |
| `context_enrichment_window_around_chunk.ipynb`, `context_enrichment_window_around_chunk_with_llamaindex.ipynb` | `05_Context_and_Generation/01_Context_Windows_and_Neighboring_Chunks.ipynb` | Donor; the LlamaIndex version is a support/reference implementation. |
| `contextual_chunk_headers.ipynb` | `05_Context_and_Generation/02_Contextual_Chunk_Headers_and_Retrieval.ipynb` | Canonical source/donor. |
| `contextual_compression.ipynb` | `05_Context_and_Generation/03_Contextual_Compression.ipynb` | Canonical source/donor. |
| `crag.ipynb` | `07_Agentic_RAG/03_Corrective_RAG_CRAG.ipynb` | Donor; combine with the LangGraph CRAG implementation. |
| `dartboard.ipynb` | `03_Retrieval/06_Dartboard_and_Diverse_Passage_Selection.ipynb` | Canonical source/donor. |
| `document_augmentation.ipynb` | `02_Chunking_and_Indexing/08_Document_Augmentation.ipynb` | Canonical source/donor. |
| `explainable_retrieval.ipynb` | `05_Context_and_Generation/05_Explainable_Retrieval_and_Evidence.ipynb` | Canonical source/donor. |
| `fusion_retrieval.ipynb`, `fusion_retrieval_with_llamaindex.ipynb` | `04_Query_Transformation_and_Routing/03_RAG_Fusion.ipynb` | Donor; the LlamaIndex version is support/reference. Keep RAG-Fusion distinct from dense/sparse hybrid search. |
| `graph_rag.ipynb`, `graphrag_with_milvus_vectordb.ipynb` | `08_Advanced_Architectures/04_Graph_RAG_Fundamentals.ipynb` | Donor; Milvus implementation becomes a backend section. |
| `hierarchical_indices.ipynb` | `08_Advanced_Architectures/01_Hierarchical_Retrieval_and_RAPTOR.ipynb` | Donor; combine coarse-to-fine indexing with RAPTOR. |
| `HyPE_Hypothetical_Prompt_Embeddings.ipynb` | `02_Chunking_and_Indexing/09_HyPE_Hypothetical_Prompt_Embeddings.ipynb` | Canonical source/donor. |
| `Microsoft_GraphRag.ipynb` | `08_Advanced_Architectures/05_Microsoft_Community_GraphRAG.ipynb` | Canonical source/donor. |
| `multi_model_rag_with_captioning.ipynb` | `09_Multimodal_RAG/01_Captioning_and_Multi_Vector_Retrieval.ipynb` | Canonical source/donor. |
| `multi_model_rag_with_colpali.ipynb` | `09_Multimodal_RAG/03_Visual_Retrieval_with_ColPali.ipynb` | Canonical source/donor. |
| `raptor.ipynb` | `08_Advanced_Architectures/01_Hierarchical_Retrieval_and_RAPTOR.ipynb` | Canonical source/donor. |
| `relevant_segment_extraction.ipynb` | `05_Context_and_Generation/04_Relevant_Segment_Extraction.ipynb` | Canonical source/donor. |
| `reranking.ipynb`, `reranking_with_llamaindex.ipynb` | `03_Retrieval/05_Reranking_and_Contextual_Compression.ipynb` | Donor; the LlamaIndex version is support/reference. |
| `retrieval_with_feedback_loop.ipynb` | `07_Agentic_RAG/06_Feedback_Driven_Retrieval.ipynb` | Canonical source/donor. |
| `self_rag.ipynb` | `07_Agentic_RAG/05_Self_RAG.ipynb` | Canonical source/donor. |
| `semantic_chunking.ipynb` | `02_Chunking_and_Indexing/02_Semantic_Chunking.ipynb` | Donor; prefer the richer dedicated semantic-chunking source identified in Section 4. |

#### Nested source checkout: `all_rag_techniques/RAG_TECHNIQUES/`

| Source notebook(s) | Proposed destination | Disposition and reason |
| --- | --- | --- |
| Duplicate copies of the outer anthology notebooks | Same destinations listed above | Support/reference and archive candidates after hash/dependency verification; do not create duplicate active lessons. |
| `Agentic_RAG.ipynb` | `07_Agentic_RAG/01_Retrieval_as_an_Agent_Tool.ipynb` | Donor/support; preserve the managed SDK, parsing, reranking, and grounded-generation examples as an optional implementation. |
| `graph_rag_local_attribution.ipynb` | `08_Advanced_Architectures/07_Graph_Attribution_and_Verifiable_Provenance.ipynb` | Canonical donor for local attribution and provenance. |
| `json_rag.ipynb` | `01_Foundations/05_Structured_Data_RAG.ipynb` | Donor; preserve structured semantic retrieval, but do not claim it is a complete generation pipeline without adding and validating that section. |
| `light_rag.ipynb` | `08_Advanced_Architectures/06_LightRAG.ipynb` | Canonical source/donor. |
| `local_rag_huggingface_faiss.ipynb` | `10_Production_RAG/05_Local_and_Provider_Agnostic_RAG.ipynb` | Canonical donor; retain local model setup as a deployment variant. |
| `memorag.ipynb` | `08_Advanced_Architectures/02_Memory_Guided_RAG.ipynb` | Canonical source/donor. |
| `multi_faceted_filtering.ipynb` | `03_Retrieval/02_Metadata_Filtering_and_Self_Query.ipynb` | Donor; preserve metadata, threshold, content, and diversity filtering examples. |
| `evaluation/end-2-end_rag_evaluation.ipynb` | `06_Evaluation/06_End_to_End_RAG_Evaluation.ipynb` | Canonical donor for completeness, golden benchmarks, and judge calibration. |
| `evaluation/open-rag-eval-example.ipynb` | `06_Evaluation/07_Evaluator_Calibration_and_Meta_Evaluation.ipynb` | Donor; preserve UMBRELA, AutoNuggetizer, hallucination, and citation evaluation as optional advanced methods. |

#### Evaluation folders

| Source folder/notebooks | Proposed destination | Disposition and reason |
| --- | --- | --- |
| `Comprehensive_RAG_Techniques/evaluation/define_evaluation_metrics.ipynb` | `06_Evaluation/01_Deterministic_Retrieval_Metrics.ipynb` and `02_LLM_Judged_Retrieval_Metrics.ipynb` | Donor; split metric definitions by evaluation family. |
| `Comprehensive_RAG_Techniques/evaluation/evaluation_deep_eval.ipynb` | `06_Evaluation/04_RAGAS_and_DeepEval_in_Practice.ipynb` | Donor. |
| `Comprehensive_RAG_Techniques/evaluation/evaluation_grouse.ipynb` | `06_Evaluation/07_Evaluator_Calibration_and_Meta_Evaluation.ipynb` | Donor. |
| Nested `RAG_TECHNIQUES/evaluation/` helper notebooks and evaluation scripts | `06_Evaluation/` plus `_support/evaluation_data/` and `_support/helpers/` | Support/reference; preserve imports, fixtures, judge prompts, and test utilities. |

#### Graph, ecosystem, and LangGraph folders

| Source folder/notebooks | Proposed destination | Disposition and reason |
| --- | --- | --- |
| `GraphRAG/AI-Enhancement-with-Knowledge-Graphs---Mastering-RAG-Systems/1. Introduction_of_KG/kg_simple.ipynb` | `08_Advanced_Architectures/03_Knowledge_Graph_Construction.ipynb` | Donor for graph primitives and Cypher CRUD. |
| `GraphRAG/.../2. KG_and_RAG System/1. health_care_kg.ipynb`, `2. query_kg_using_langchain.ipynb` | `08_Advanced_Architectures/03_Knowledge_Graph_Construction.ipynb` and `04_Graph_RAG_Fundamentals.ipynb` | Donor; manual Cypher remains explicitly labelled as manual, not verified natural-language text-to-Cypher. |
| `GraphRAG/.../3. Index and Embedding/vector_indexing_embedding.ipynb`, `4. End to End Knowledge Graph/roman_emp_graph_rag.ipynb` | `08_Advanced_Architectures/04_Graph_RAG_Fundamentals.ipynb` | Donor for graph/vector hybrid retrieval and conversational graph RAG. |
| `GraphRAG/Constucting Knowledge Graph/entity_relationship_extraction.ipynb` | `08_Advanced_Architectures/03_Knowledge_Graph_Construction.ipynb` | Donor; keep co-located raw text and graph visualization files under `_support/` or the application bundle. |
| `GraphRAG/KG from Text/Exercise.ipynb` | `08_Advanced_Architectures/03_Knowledge_Graph_Construction.ipynb` | Incomplete exercise/reference; not counted as a completed canonical lesson. |
| `RAG_Ecosystem/rag_ecosystem.ipynb` | `00_Curriculum_Guide/RAG_Curriculum_Map.ipynb` and `09_Multimodal_RAG/04_Late_Interaction_Retrieval_with_ColBERT.ipynb` | Support/reference for the ecosystem overview; donor for unique ColBERT content. |
| `RAG_with_LangGraph_Advanced/01_Advanced_RAG_Agent.ipynb`, `02_RAG_as_Tool_in_Agents.ipynb` | `07_Agentic_RAG/01_Retrieval_as_an_Agent_Tool.ipynb` | Donor; preserve advanced conversational rewrite, filtering, fallback, and retry patterns. |
| `RAG_with_LangGraph_Advanced/1. Build_a_Healthcare_Customer_Support_Router_Agentic_RAG_System.ipynb` | `07_Agentic_RAG/02_Domain_Router_Agentic_RAG.ipynb` and `11_Applications_and_Capstones/02_Healthcare_Router_RAG.ipynb` | Application donor; keep the full domain application bundled while extracting the general routing concepts. |
| `RAG_with_LangGraph_Advanced/2. Build_an_Agentic_Corrective_RAG_System_with_LangGraph.ipynb`, `3. Build_an_Adaptive_RAG_System.ipynb`, `4. Build_a_Self_RAG_System.ipynb` | `07_Agentic_RAG/03`–`05` | Canonical donors; preserve LangGraph-specific setup as support/reference rather than duplicate lessons. |

#### Application, support, and planned folders

| Source folder | Proposed destination | Disposition and reason |
| --- | --- | --- |
| `building-adaptive-rag/` | `11_Applications_and_Capstones/` plus `_support/helpers/` | Application bundle; preserve protocol/app code, configuration, and tests. Extract only general adaptive-RAG teaching content. |
| `CacheRAG/` | No active destination yet | Planned/missing; retain as reference/planning material and do not count it as completed CacheRAG coverage. |
| Anthology `data/`, `images/`, `helper_functions.py`, `evaluation/`, runnable scripts, and `tests/` | `_support/shared_data/`, `_support/evaluation_data/`, `_support/helpers/` | Support; preserve hardcoded path relationships through the dependency manifest before any notebook move. |
| Nested checkout repository metadata and package-specific helper files | `_support/helpers/` or source checkout reference | Support/reference; do not flatten or delete until imports and licensing/provenance are mapped. |

The same disposition model will be extended to the remaining repository phases during implementation: every source path receives one source ID, one destination concept or folder, one disposition, and a dependency list. This prevents a notebook being silently classified as “not needed” when it actually contains a required helper, dataset, test, or framework-specific implementation.

## 4. Preferred canonical sources

These are proposed starting points based on teaching content, not completed destination files. Preserve the richest explanation while incorporating stronger implementations and experiments from donors. Validate compatibility before marking any consolidated lesson runnable.

| Concept                                | Preferred existing source                                                                                      | Consolidation and preservation decision                                                                                                                                                                                                                                    |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Basic RAG                              |                                                                                                                | Preserve the indexing/retrieval walkthrough from and the fallback, structured-output, and exercise material from . Move detailed component instruction to its canonical lesson instead of repeating it here.                                                               |
| Document ingestion                     | The detailed[ lessons][loader-lessons]                                                                         | Preserve format-specific examples and custom-loader material. Consolidate repeated setup and loader introductions. Keep advanced multimodal extraction distinct from basic document-loading contracts.                                                                     |
| Embeddings                             |                                                                                                                | Merge OpenAI examples from and batching/caching from . Keep model benchmarking as a distinct learning objective.                                                                                                                                                           |
| Vector-store fundamentals              |                                                                                                                | Preserve useful Chroma/FAISS operations, persistence, and exercises. Other backends become optional comparisons rather than repeated basic-RAG tutorials.                                                                                                                  |
| Chunking fundamentals                  |                                                                                                                | Incorporate focused examples/exercises from. Extract semantic and proposition chunking into their own lessons.                                                                                                                                                             |
| Semantic chunking                      | The outer anthology's current                                                                                  | Preserve the user's current edits and incorporate the from-scratch threshold implementation from. Do not replace the working copy with the nested version automatically.                                                                                                   |
| Query transformations                  | The eight dedicated notebooks in                                                                               | Retain their strong explanations, baselines, inspection steps, and tradeoffs. Merge useful additions from the production-course and ecosystem versions into the matching individual concept.                                                                               |
| Hybrid retrieval                       |                                                                                                                | Preserve dense/sparse explanations, fusion implementations, and the Databricks comparison material. Carry forward current edits to. Do not conflate this with query-based RAG-Fusion.                                                                                      |
| Parent-document retrieval              |                                                                                                                | Preserve the custom PostgreSQL document-store implementation from as an advanced section.                                                                                                                                                                                  |
| Reranking                              | The outer anthology's                                                                                          | Merge useful cross-encoder examples, LCEL integration, provider comparisons, and the LlamaIndex variant. Route extraction/compression-specific material to contextual compression rather than mixing objectives.                                                           |
| Corrective RAG                         |                                                                                                                | Preserve unique scoring/explanation material from the smaller.                                                                                                                                                                                                             |
| Adaptive RAG                           |                                                                                                                | Preserve additional routing strategies, while distinguishing query-type strategy selection from the corrective graph workflow. Do not merge solely because both filenames contain adaptive.                                                                                |
| Self-RAG                               |                                                                                                                | Preserve useful comparisons from the anthology version. Retain the dedicated lesson's separation of retrieval, relevance, groundedness, utility, and retry decisions.                                                                                                      |
| Conversational and multi-user RAG      | The Phase 13 walkthrough                                                                                       | Extract separate conversational-RAG and multi-user-isolation lessons. Its SQL-backed session-history material is richer than the shorter notebook labeled Multi-user. Preserve the database/session behavior and shared pipeline dependencies.                             |
| Captioning/multi-vector multimodal RAG |                                                                                                                | Preserve its text/table/image processing and document-store material. Keep shared text/image embedding retrieval and ColPali visual retrieval as separate techniques.                                                                                                      |
| RAG evaluation                         | The[modular evaluation tutorial][evaluation-tutorial] plus the [detailed per-metric drills][evaluation-drills] | Use richer drills for contextual precision/recall/relevancy, together with modular explanations and offline/live examples. Distribute useful RAG material from repeated walkthroughs and the master notebook; retain unrelated agent/tool evaluation in its existing home. |
| Enterprise RAG                         | The[handbook Enterprise RAG project][enterprise-handbook]                                                      | Make this the authoritative enterprise example. Replace the 13[interview-preparation notebook duplicates][enterprise-interview] with links after preserving originals. Keep project source, datasets, configuration, and tests intact.                                     |

### Dedicated query lessons to retain individually

- : query variations and result union.
- : reciprocal rank fusion across query results.
- : abstraction and dual-context retrieval.
- : hypothetical-document retrieval, including manual and packaged implementations.
- : sub-question decomposition and synthesis.
- : classifier-based routing.
- : embedding-based routing and confidence inspection.
- : natural-language query construction with metadata filters.

Give query rewriting/expansion its own canonical objective where it adds material beyond multi-query generation. Preserve relevant source sections rather than retaining a second broad query-techniques notebook.

## 5. Anthologies, nested sources, and project boundaries

### Broad notebooks become donors and navigation guides

Map overlapping material in these notebooks to the relevant canonical concepts:

- .
- .
- .

Their overview/navigation role becomes Markdown documentation. Their original notebooks remain recoverable in the archive. Extract genuinely unique content, such as the ecosystem's ColBERT material, rather than dropping it when retiring the broad walkthrough.

Do not replace several duplicates with another oversized master notebook. For mixed agent/RAG/evaluation sources, preserve non-RAG material in its correct existing home rather than broadening this task into an unrelated reorganization.

### Unique advanced methods remain first-class lessons

Explicitly preserve RAPTOR, HyPE, proposition chunking, relevant-segment extraction, Dartboard retrieval, feedback loops, graph attribution, and additional methods found in the nested source checkout.

LightRAG's dual-level graph retrieval and MemoRAG's global-memory-guided retrieval warrant separate lessons, rather than generic GraphRAG or memory appendices. See the [LightRAG paper][lightrag-paper] and [MemoRAG paper][memorag-paper]. Where a notebook is a pedagogical reimplementation or a managed-service example, label that clearly rather than implying it implements an official research system unchanged.

### Additional titles in the nested checkout

The [nested source checkout][nested-checkout] has 46 notebooks. Nine titles were absent from the outer anthology during the audit:

| Nested notebook | Proposed treatment                                                                                                                                                         |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|                 | Preserve its managed RAG/component-evaluation material. Its larger size alone does not make it the best generic agentic-RAG foundation.                                    |
|                 | Preserve verifiable graph attribution and multi-hop examples; distinguish the provenance objective from a mere local-model variant.                                        |
|                 | Merge useful JSON-to-retrieval material into structured-data retrieval. Do not describe retrieval-only examples as a complete generation pipeline.                         |
|                 | Retain a dedicated LightRAG concept lesson.                                                                                                                                |
|                 | Preserve local execution, privacy/resource considerations, and useful implementation material. Separate optional cloud evaluation from any claim of fully local operation. |
|                 | Retain memory-guided retrieval as a distinct concept from conversational history.                                                                                          |
|                 | Preserve layered filtering examples in the canonical filtering lesson, with links to distinct diversity/retrieval concepts.                                                |
|                 | Preserve completeness, benchmark, and evaluation material in the appropriate evaluation lessons.                                                                           |
|                 | Preserve useful completeness, citation, and framework-integration examples without duplicating the whole evaluation curriculum.                                            |

Some nested titles are implementation variants or donors for existing concepts, not nine additional mandatory canonical notebooks. Inspect source-level differences before selecting material.

The nested checkout may supply live helper imports as well as teaching content. Resolve that dependency role before relocating, replacing, or archiving it. Do not copy a similarly named helper module into another bundle without checking its callers and interface.

### Project boundaries

- Keep the [ShopUNow capstone][shopunow] datasets and its vector-database creation -> agentic-system sequence intact. A prerequisite producer notebook is not a duplicate of the notebook that consumes its outputs.
- Keep the handbook Enterprise RAG project as the single source of its enterprise example. Consolidate repeated split-out teaching sections into canonical concepts or project documentation, while retaining the integrated application as an application rather than a second concept course.
- Preserve genuinely distinct governed-deployment material, such as authorization behavior on Databricks, rather than treating every platform example as a cosmetic provider swap.
- Leave unrelated applications and general framework lessons in their existing homes. Replace repeated teaching with links only where the RAG consolidation justifies it.

### Missing and planned content

Do not invent missing lessons during a reorganization. Keep placeholders and incomplete content honestly labeled. In particular, [CacheRAG][cache-rag] should not be marked complete merely because embedding-caching examples exist elsewhere. Record missing assets, unavailable services, and unresolved compatibility separately from migration-created problems.

## 6. Standard structure for each canonical notebook

Use a consistent instructional pattern:

**Objectives -> prerequisites -> intuition -> baseline -> implementation -> inspection/comparison -> limitations -> exercise -> summary and next lesson.**

Each canonical notebook should include:

1. **Title and objectives:** one primary concept, its problem, and the intended learner level.
2. **Prerequisites:** links to prerequisite lessons, required packages, input assets, model/service requirements, and any prerequisite-generated artifacts.
3. **Intuition:** a diagram or explanation of where the technique fits in the RAG pipeline and why a simpler baseline can fail.
4. **Baseline:** a small, understandable comparison using an appropriate corpus.
5. **Step-by-step implementation:** show the core mechanism before hiding it in framework helpers. Keep optional framework/provider variants clearly separated.
6. **Inspection and comparison:** expose useful intermediate artifacts, such as chunks, query variants, retrieved documents, scores, graph routes, citations, or evaluation results.
7. **Limitations and tradeoffs:** discuss failure cases and relevant accuracy, latency, cost, context-length, and infrastructure considerations. Do not present unmeasured performance as a benchmark.
8. **Exercise:** preserve valuable existing exercises and add a focused task only where needed to complete the merged lesson's teaching objective.
9. **Summary and next lesson:** explain when to use the technique and link to the next concept.
10. **Provenance and runtime status:** identify contributing sources and distinguish statically checked, offline-tested, service-required, and not-yet-validated examples.

Maintain one readable main learning path. Use optional advanced sections for valuable depth instead of duplicating introductory cells. Preserve notebook attachments, meaningful metadata/tags, and any intentional legacy-comparison cells; label demonstrations that should not execute by default.

## 7. Dependency-preservation plan

Dependency mapping is a prerequisite to moving notebooks, not cleanup to attempt afterward. A notebook migration is complete only when its content, assets, helper imports, and prerequisite relationships remain accounted for.

### A. Create a concept registry and source-to-target manifest

Before the first notebook move, record the following planned fields:

| Field                                       | Purpose                                                                                                                                        |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Concept ID and learning objective           | Enforce one active canonical lesson per concept and distinguish similarly named methods.                                                       |
| Canonical destination                       | Identify the single active notebook path and owning phase.                                                                                     |
| Source notebook paths and cell IDs/sections | Trace preserved explanations, code, diagrams, and exercises back to their donors.                                                              |
| Source disposition                          | Classify every affected source as keep, merge, extract, reference-only, or archive.                                                            |
| Input assets and resolved locations         | Record PDFs, text, CSV/JSON/JSONL, images, attachments, and other required inputs.                                                             |
| Asset identity and checksums                | Distinguish real duplicates from unrelated files sharing a basename; support integrity and rollback checks.                                    |
| Local modules and helper interfaces         | Preserve imports, function signatures, namespace assumptions, and supporting scripts.                                                          |
| Environment and service requirements        | Record package pins/extras, environment-variable names, local services, cloud services, and platform constraints. Do not record secret values. |
| Generated artifacts and runtime state       | Distinguish caches, vector indexes, extracted figures, reports, database files, collections, and external tables from immutable inputs.        |
| Prerequisite lessons/artifacts              | Preserve producer -> consumer ordering and document initialization requirements.                                                               |
| Validation and blockers                     | Record checks performed, existing failures, untested cloud paths, and unresolved dependencies honestly.                                        |
| Archive/restore mapping                     | Make the original material recoverable without relying on memory or notebook titles.                                                           |

The manifest must account for every affected source, including nested-checkout variants and mixed-topic notebooks. Do not select keepers solely by filename or move a donor to the archive before its unique material has a recorded destination.

### B. Keep assets stationary initially

The first implementation pass should leave shared documents and supporting bundles in their existing locations. Move lesson files only after adapting their references.

Protect these dependency groups in particular:

- [Phase 4 shared data][shared-data]: the 23 supporting files identified in the audit, including `dummy.txt`, `layoutparser_paper.pdf`, `Transformer.pdf`, and `wikidata_rag_demo.jsonl`.
- [Outer anthology assets and helpers][anthology-root]: `data/`, `images/`, `helper_functions.py`, evaluation code, runnable scripts, and tests.
- [Nested source checkout][nested-checkout]: its additional datasets, notebooks, helpers, and evaluation dependencies until the source-level comparison is complete.
- GraphRAG's [entity-extraction bundle][graph-extraction-bundle]: co-located text, visualization helpers, and supporting application code.
- [ShopUNow][shopunow]: department datasets, sample-data code, and the database-building sequence required by the agentic system.
- [Enterprise RAG][enterprise-handbook]: `src/`, ACL manifests, identities, golden datasets, judge-calibration data, configuration, and tests.

The anthology's dependency coupling is explicitly documented in its [roadmap note][anthology-roadmap]. A similarly named module or document elsewhere in the repository is not automatically an interchangeable replacement.

Do not move, merge, or delete data solely because filenames match. Verify identity and usage first. Do not silently substitute a different document for a missing input.

### C. Make paths independent of notebook depth

Introduce a small, consistent repository-root/resource resolver where needed, using the existing shared-helper structure rather than a large new abstraction layer.

- Replace fragile `../../...` paths and implicit working-directory assumptions with explicit resource locations.
- Check for local module-name collisions, such as multiple `helpers`, `utils`, or evaluation modules. Preserve intended imports rather than relying on whichever directory appears first in `sys.path`.
- Resolve image paths, HTML image references, notebook links, and attachments as well as code-based file reads.
- Update supporting scripts, documentation, and tests that reference moved notebooks.
- Update the anthology's hardcoded notebook/script discovery paths in [its test configuration][anthology-test-config].

Validate supported launch modes, including a kernel started from the repository root and one started from the notebook's directory. Do not globally change the working directory as a shortcut that could break unrelated cells or environment loading.

### D. Preserve environments and runtime behavior

- Keep the current dependency pins and existing environment boundaries unless a specific compatibility fix is separately justified and approved.
- Preserve optional-dependency requirements instead of installing every framework into the main environment. The [requirements file][requirements] documents deliberate exclusions and constraints.
- Preserve the existing LLM/embedding configuration behavior; do not silently change providers or require a new paid service for a previously local example.
- Keep environment-variable names in documentation, but leave `.env`, credentials, and private runtime settings in place and out of published content archives.
- Preserve metadata, model/dimension assumptions, document IDs, collection names, and index schemas that couple ingestion to retrieval.
- Separate immutable inputs from per-lesson generated outputs. Do not overwrite or rebuild existing vector indexes, caches, or database collections merely to test a move.
- Clearly identify cells that download models/data, incur API charges, create cloud resources, or mutate state. Such cells are not authorized by the plan-file request.

### E. Archive with a recovery contract

- Preserve the latest working copies, not just the last committed versions.
- Maintain original relative layout in a restorable bundle, or provide an explicit restore mapping covering notebooks and their supporting assets.
- Keep archived sources outside the active learning index. Archive copies do not count as additional active lessons.
- Do not claim archived notebooks run in place unless that has been verified; the minimum requirement is reliable restoration of the original dependency layout.
- Do not commit or export secret-bearing notebook outputs or private settings as part of a backup.
- Avoid destructive Git operations, implicit stashing, or repository-wide resets. Existing unrelated work must remain untouched.

### F. Validate in layers

1. **Static checks:** notebook JSON/schema, required metadata, source coverage, local resource resolution, internal links, and uniqueness of active concept IDs.
2. **Import checks:** validate against the intended environment, accounting for optional dependencies and modules with import-time side effects.
3. **Isolated offline execution:** use fresh kernels and temporary outputs for eligible examples. Do not target existing user indexes or databases.
4. **Service-backed validation:** run only after separate authorization for the relevant model downloads, API costs, credentials, and mutable external resources.
5. **Regression checks:** compare relevant behavior, intermediate artifacts, and expected lesson outcomes with the preserved source behavior where a baseline is available.

Record pre-existing issues separately from migration regressions. A skipped cloud test is not a passing test, and a successful import is not proof that an entire pipeline works.

## 8. Implementation sequence after approval

### Step 1 - Freeze and re-inventory the current working state

- Re-scan the repository and nested checkout before relying on the audit counts.
- Capture recoverable copies and checksums of affected notebooks and assets, excluding secrets from content archives.
- Preserve current uncommitted edits, including changes made after this plan was written.
- Record baseline dependency problems without silently changing them.

### Step 2 - Create the registry and migration manifest

- Assign each distinct learning objective a concept ID and owning phase.
- Give each source a keep, merge, extract, reference-only, or archive disposition.
- Map unique donor cells, dependencies, prerequisite relationships, and proposed destinations.
- Resolve ambiguous concept boundaries before moving their sources.

### Step 3 - Pilot basic RAG

- Consolidate the basic-RAG group first, including its document/helper dependencies.
- Establish the notebook teaching template and root-relative resource approach.
- Check that valuable source material has not been lost and that the pilot does not create a new oversized omnibus notebook.
- Validate within the authorized execution boundary before applying the pattern more widely.

### Step 4 - Work through bounded batches

1. Foundations, ingestion, embeddings, vector stores, and chunking.
2. Indexing, retrieval, query transformation/routing, context processing, and conversational RAG.
3. Agentic RAG, hierarchical/memory architectures, graph RAG, and multimodal methods.
4. Evaluation consolidation and cross-repository enterprise duplicates.

Keep changes scoped to the current batch. Do not promote or archive a donor until its unique material and dependency mapping are accounted for. Preserve application bundles rather than reorganizing unrelated source code along the way.

### Step 5 - Validate each batch

- Check notebook structure, imports, source coverage, assets, links, prerequisite order, and applicable isolated execution.
- Update affected script/test references in the same batch as the notebook move.
- Stop promotion of a batch if it introduces unresolved dependency or content-loss regressions; retain a clear recovery path.
- Record what passed, what was not run, and what remains blocked by existing missing assets or external services.

### Step 6 - Publish navigation and archive superseded originals

- Update this file into the actual linked learning path only after canonical locations are established.
- Update the repository README, [NOTEBOOK_INDEX.md][notebook-index], relevant phase READMEs, and any directly affected source indexes or links.
- Replace duplicate interview/course entry points with references to their canonical lessons or applications.
- Archive superseded originals with provenance and restore information; do not permanently delete them.
- Re-check that every active concept has one canonical notebook and that the archives do not appear as competing curriculum routes.

## 9. Acceptance checklist

- [ ] Every affected source notebook has a recorded disposition.
- [ ] Every active concept has exactly one canonical notebook path.
- [ ] Distinct algorithms are not merged merely because their names or frameworks overlap.
- [ ] Unique explanations, implementations, exercises, diagrams, and comparisons have recorded destinations.
- [ ] The strongest teaching content is preserved, including useful sections from shorter donors and the nested checkout.
- [ ] User working-copy edits and unrelated files remain intact.
- [ ] Required local input assets resolve without silently substituting different documents.
- [ ] Local helper imports and their interfaces still resolve to the intended modules.
- [ ] Producer/consumer sequences and generated-artifact requirements are explicit.
- [ ] Notebook attachments, important metadata, and meaningful tags survive consolidation.
- [ ] Markdown/image links, README/index links, supporting scripts, and test discovery references are updated.
- [ ] Immutable inputs are separated from generated outputs; existing indexes and databases are not overwritten by validation.
- [ ] Dependencies and environment boundaries are preserved or specifically approved changes are documented.
- [ ] Validation status is recorded honestly, including unrun service-backed examples and pre-existing blockers.
- [ ] No missing/planned topic is mislabeled as complete.
- [ ] Original sources are recoverable with their dependency layout or an explicit restore mapping.
- [ ] Archived material is excluded from the active curriculum route.
- [ ] No permanent deletion, paid execution, cloud mutation, or destructive Git operation occurs without separate authorization.

These are future implementation criteria, not claims that the reorganization has already passed them.

## 10. Approval scope and exclusions

### Requested implementation scope

- Concept-first organization within existing phase ownership.
- Content consolidation into richer canonical lessons.
- Necessary dependency/path repairs for affected notebooks and their direct references.
- Updated learning indexes, prerequisites, provenance, and validation records.
- Recoverable archiving of superseded originals.

### Not implicitly authorized

- Permanent deletion of notebooks, assets, projects, or the nested checkout.
- Blanket dependency upgrades, global environment changes, or provider migrations.
- Paid API calls, cloud resource creation, remote database/index mutation, or large model downloads.
- Reorganization or bug fixing unrelated to the RAG notebook task.
- Overwriting user edits, stashing/resetting the working tree, creating branches, or making commits without a separate request.

**The current request authorizes creation of this plan file only. Do not begin creating canonical notebooks or moving, merging, rewriting, or archiving sources until the user gives a separate go-ahead.**

## 11. Sources and repository references

The primary evidence is the local notebook/source audit. External references support distinctions between algorithms, not claims that the local implementations have been runtime-validated.

- [Repository guidance][repo-guidance]: existing topic ownership, separation of foundational and advanced RAG, shared-helper conventions, environment constraints, and known path issues.
- [Notebook index][notebook-index]: current source locations and recorded discrepancies; update after implementation rather than treating historical descriptions as execution proof.
- [Anthology roadmap note][anthology-roadmap]: why its notebooks, helpers, data, images, scripts, and tests were originally kept together.
- [Anthology test configuration][anthology-test-config]: hardcoded notebook/script discovery roots that must be updated with any relocation.
- [Requirements and exclusions][requirements]: preserve the repository's existing pinned environment choices.
- [LightRAG paper][lightrag-paper]: dual-level graph retrieval.
- [MemoRAG paper][memorag-paper]: global-memory-enhanced retrieval.

All source links below point to the locations observed during planning. Update them to the canonical locations or recorded archive/provenance destinations during implementation.

[repo-guidance]: CLAUDE.md
[notebook-index]: NOTEBOOK_INDEX.md
[requirements]: requirements.txt
[empty-qa-project]: 13_Projects/RAG_Systems_Projects/4. Develop a RAG system for Question Answering.ipynb
[empty-multimodal-project]: 13_Projects/RAG_Systems_Projects/3. Multimodal RAG System.ipynb
[rag-comprehensive]: 04_Retrieval_and_RAG/09_RAG_with_LangChain/7.1_RAG_Comprehensive.ipynb
[rag-overview]: 04_Retrieval_and_RAG/01_Introduction_to_RAG/1_rag_overview.ipynb
[rag-pipeline]: 04_Retrieval_and_RAG/RAG_Production_Course/06_rag_pipeline.ipynb
[loader-lessons]: 04_Retrieval_and_RAG/06_RAG_Naive_to_Production/01_Loading_Data/
[embedding-basics]: 04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/4. Embedding_Basics_Alt.ipynb
[openai-embeddings]: 04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/5. Openaiembeddings_Alt.ipynb
[embeddings-deep]: 04_Retrieval_and_RAG/RAG_Production_Course/04_embeddings_deep.ipynb
[vector-stores]: 04_Retrieval_and_RAG/RAG_Production_Course/05_vector_stores.ipynb
[chunking-comprehensive]: 04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking/1. Document_Splitters_and_Chunkers.ipynb
[text-splitters]: 04_Retrieval_and_RAG/RAG_Production_Course/02_text_splitters.ipynb
[semantic-chunking]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/semantic_chunking.ipynb
[semantic-chunking-manual]: 04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking/2. Semantichunking.ipynb
[query-transformations]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/
[hybrid-rag]: 04_Retrieval_and_RAG/06_RAG_Naive_to_Production/03_Hybrid_Search_Strategies/1.1. Hybrid_Search_RAG.ipynb
[dense-sparse]: 04_Retrieval_and_RAG/06_RAG_Naive_to_Production/03_Hybrid_Search_Strategies/1-densesparse.ipynb
[parent-document]: 04_Retrieval_and_RAG/03_Indexing_Techniques/Parent_Document_Retrieval.ipynb
[postgres-parent]: 04_Retrieval_and_RAG/06_RAG_Naive_to_Production/05_Parent_Document_Retriever/08_BetterRetriever.ipynb
[reranking]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/reranking.ipynb
[corrective-rag]: 08_Advanced_RAG/RAG_with_LangGraph_Advanced/2. Build_an_Agentic_Corrective_RAG_System_with_LangGraph.ipynb
[crag-anthology]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/crag.ipynb
[adaptive-rag]: 08_Advanced_RAG/RAG_with_LangGraph_Advanced/3. Build_an_Adaptive_RAG_System.ipynb
[self-rag]: 08_Advanced_RAG/RAG_with_LangGraph_Advanced/4. Build_a_Self_RAG_System.ipynb
[conversational-m8]: 13_Projects/RAG_Systems_Projects/M8_Simple_RAG,_Conversational_RAG_and_Multi_User_Conversational_RAG_Systems.ipynb
[multimodal-m8]: 13_Projects/RAG_Systems_Projects/M8_Multimodal_RAG_System_with_GPT_4o.ipynb
[evaluation-tutorial]: 07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/Tutorial_RAG_Agent_Tool_Evaluation/
[evaluation-drills]: 07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/RAG_Evaluation/DeepEval_Metrics/
[enterprise-handbook]: 14_AI_Engineering_Handbook/04_Enterprise_RAG/project/
[enterprise-interview]: 16_AI_Engineer_Interview_Preparation/Enterprise RAG Platform/
[multi-query]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/1. Rewriting or Query Expansion/a. Multi_Query.ipynb
[rag-fusion]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/1. Rewriting or Query Expansion/b. RAG_Fusion.ipynb
[step-back]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/1. Rewriting or Query Expansion/c. Step_Back_Prompting.ipynb
[hyde]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/1. Rewriting or Query Expansion/d. HyDE.ipynb
[decomposition]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/2. Decomposition/Decomposition.ipynb
[classifier-routing]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/3. Routing/a. Routing_LLM_Classifier.ipynb
[semantic-routing]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/3. Routing/b. Semantic_Routing.ipynb
[self-querying]: 04_Retrieval_and_RAG/04_Query_Transformation_Techniques/3. Routing/c. Self_Querying_Retrieval.ipynb
[rag-ecosystem]: 08_Advanced_RAG/RAG_Ecosystem/rag_ecosystem.ipynb
[advanced-rag-overview]: 04_Retrieval_and_RAG/RAG_Production_Course/07_advanced_rag.ipynb
[evaluation-master]: 07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/Agent_RAG_Tools_Evaluation_MASTER.ipynb
[nested-checkout]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/
[nested-agentic]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/Agentic_RAG.ipynb
[nested-attribution]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/graph_rag_local_attribution.ipynb
[nested-json]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/json_rag.ipynb
[nested-lightrag]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/light_rag.ipynb
[nested-local]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/local_rag_huggingface_faiss.ipynb
[nested-memorag]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/memorag.ipynb
[nested-filtering]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/multi_faceted_filtering.ipynb
[nested-end-to-end]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/evaluation/end-2-end_rag_evaluation.ipynb
[nested-open-eval]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/evaluation/open-rag-eval-example.ipynb
[shopunow]: 13_Projects/ShopUNow_Agentic_RAG_Capstone/
[cache-rag]: 08_Advanced_RAG/CacheRAG/README.md
[shared-data]: 04_Retrieval_and_RAG/shared_data/
[anthology-root]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/
[graph-extraction-bundle]: 08_Advanced_RAG/GraphRAG/Constucting Knowledge Graph/
[anthology-roadmap]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/README_ROADMAP.md
[anthology-test-config]: 08_Advanced_RAG/Comprehensive_RAG_Techniques/tests/conftest.py
[lightrag-paper]: https://arxiv.org/abs/2410.05779
[memorag-paper]: https://arxiv.org/abs/2409.05591
