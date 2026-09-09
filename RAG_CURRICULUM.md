# RAG Curriculum - Reorganization Plan

- **Status:** Planning document only; notebook reorganization has not started.
- **Audit date:** September 9, 2026.
- **Scope of this change:** Create this plan file only. Moving, merging, rewriting, or archiving notebooks requires a separate go-ahead.
- **Recommendation:** Build a concept-first RAG curriculum with one authoritative active teaching notebook per concept. Preserve unique material and retain recoverable originals rather than permanently deleting content.

## Contents

1. [Audit findings and limitations](#1-audit-findings-and-limitations)
2. [Organization principles](#2-organization-principles)
3. [Proposed learning structure](#3-proposed-learning-structure)
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

| Finding | Audit result |
| --- | --- |
| Notebook files discovered | 632 |
| Notebook files parseable as JSON | 631 |
| Foundational RAG notebooks in `04_Retrieval_and_RAG/` | 74 |
| Advanced RAG notebooks outside the nested source checkout | 52 |
| Notebooks inside the nested `RAG_TECHNIQUES` checkout | 46 |
| Byte-identical Enterprise RAG notebook pairs | 13 pairs between the handbook and interview-preparation projects |
| Notebook titles in the nested checkout absent from the outer anthology | 9; a new title is not necessarily a new concept |
| Zero-byte notebook files | 1 project notebook |

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

| Learning stage | Canonical concepts | Home |
| --- | --- | --- |
| RAG foundations | RAG lifecycle and baseline pipeline; document loading and metadata; embeddings; vector-store operations; structured-data retrieval | Phase 4 |
| Chunking and indexing | Structural/token chunking; semantic chunking; proposition chunking; chunk-size experiments; incremental indexing; parent-document retrieval; multi-representation indexing; document augmentation; HyPE | Phase 4 |
| Retrieval strategies | Dense/sparse retrieval; metadata filtering; hybrid search; MMR; reranking; Dartboard retrieval | Phase 4 |
| Query transformation and routing | Rewriting/expansion; multi-query; RAG-Fusion; decomposition; step-back prompting; HyDE; classifier routing; semantic routing; self-querying | Phase 4 |
| Context and generation | Context windows; compression; contextual headers/retrieval; relevant-segment extraction; explainable retrieval; citations; conversational and multi-user RAG | Phase 4 |
| Evaluation | Deterministic retrieval metrics; contextual metrics; answer quality/groundedness; golden datasets; in-pipeline and end-to-end evaluation; evaluator calibration | Phase 7's RAG evaluation track |
| Agentic RAG | Retrieval as a tool; domain-router RAG; corrective RAG; adaptive RAG; Self-RAG; feedback-driven retrieval | Phase 8 |
| Advanced architectures | Hierarchical retrieval/RAPTOR; memory-guided retrieval; knowledge-graph construction; graph retrieval; Microsoft GraphRAG; LightRAG; verifiable graph attribution | Phase 8 |
| Multimodal RAG | Captioning/multi-vector retrieval; shared text/image embedding retrieval; visual retrieval with ColPali | Phase 8 |
| Production and applications | Access control; security testing; governed Databricks deployment; observability; integrated capstones | Existing production, handbook, and project homes |

These are stages and folders, not giant all-in-one notebooks. Each distinct technique receives its own canonical lesson. Final concept IDs and source-to-target paths will be recorded in the migration manifest; do not force an arbitrary final notebook count before that mapping is complete.

After implementation, this document should become the learner-facing route across the canonical homes, with links, prerequisites, and runtime requirements. Until then, it remains a proposal. Preserve the existing ownership of general agent, memory, evaluation, and production concepts rather than creating a second RAG-specific copy of every supporting topic.

## 4. Preferred canonical sources

These are proposed starting points based on teaching content, not completed destination files. Preserve the richest explanation while incorporating stronger implementations and experiments from donors. Validate compatibility before marking any consolidated lesson runnable.

| Concept | Preferred existing source | Consolidation and preservation decision |
| --- | --- | --- |
| Basic RAG | [`7.1_RAG_Comprehensive.ipynb`][rag-comprehensive] | Preserve the indexing/retrieval walkthrough from [`1_rag_overview.ipynb`][rag-overview] and the fallback, structured-output, and exercise material from [`06_rag_pipeline.ipynb`][rag-pipeline]. Move detailed component instruction to its canonical lesson instead of repeating it here. |
| Document ingestion | The detailed [`01_Loading_Data/` lessons][loader-lessons] | Preserve format-specific examples and custom-loader material. Consolidate repeated setup and loader introductions. Keep advanced multimodal extraction distinct from basic document-loading contracts. |
| Embeddings | [`4. Embedding_Basics_Alt.ipynb`][embedding-basics] | Merge OpenAI examples from [`5. Openaiembeddings_Alt.ipynb`][openai-embeddings] and batching/caching from [`04_embeddings_deep.ipynb`][embeddings-deep]. Keep model benchmarking as a distinct learning objective. |
| Vector-store fundamentals | [`05_vector_stores.ipynb`][vector-stores] | Preserve useful Chroma/FAISS operations, persistence, and exercises. Other backends become optional comparisons rather than repeated basic-RAG tutorials. |
| Chunking fundamentals | [`1. Document_Splitters_and_Chunkers.ipynb`][chunking-comprehensive] | Incorporate focused examples/exercises from [`02_text_splitters.ipynb`][text-splitters]. Extract semantic and proposition chunking into their own lessons. |
| Semantic chunking | The outer anthology's current [`semantic_chunking.ipynb`][semantic-chunking] | Preserve the user's current edits and incorporate the from-scratch threshold implementation from [`2. Semantichunking.ipynb`][semantic-chunking-manual]. Do not replace the working copy with the nested version automatically. |
| Query transformations | The eight dedicated notebooks in [`04_Query_Transformation_Techniques/`][query-transformations] | Retain their strong explanations, baselines, inspection steps, and tradeoffs. Merge useful additions from the production-course and ecosystem versions into the matching individual concept. |
| Hybrid retrieval | [`1.1. Hybrid_Search_RAG.ipynb`][hybrid-rag] | Preserve dense/sparse explanations, fusion implementations, and the Databricks comparison material. Carry forward current edits to [`1-densesparse.ipynb`][dense-sparse]. Do not conflate this with query-based RAG-Fusion. |
| Parent-document retrieval | [`Parent_Document_Retrieval.ipynb`][parent-document] | Preserve the custom PostgreSQL document-store implementation from [`08_BetterRetriever.ipynb`][postgres-parent] as an advanced section. |
| Reranking | The outer anthology's [`reranking.ipynb`][reranking] | Merge useful cross-encoder examples, LCEL integration, provider comparisons, and the LlamaIndex variant. Route extraction/compression-specific material to contextual compression rather than mixing objectives. |
| Corrective RAG | [`2. Build_an_Agentic_Corrective_RAG_System_with_LangGraph.ipynb`][corrective-rag] | Preserve unique scoring/explanation material from the smaller [`crag.ipynb`][crag-anthology]. |
| Adaptive RAG | [`3. Build_an_Adaptive_RAG_System.ipynb`][adaptive-rag] | Preserve additional routing strategies, while distinguishing query-type strategy selection from the corrective graph workflow. Do not merge solely because both filenames contain adaptive. |
| Self-RAG | [`4. Build_a_Self_RAG_System.ipynb`][self-rag] | Preserve useful comparisons from the anthology version. Retain the dedicated lesson's separation of retrieval, relevance, groundedness, utility, and retry decisions. |
| Conversational and multi-user RAG | The Phase 13 [`M8_Simple_RAG,_Conversational_RAG_and_Multi_User_Conversational_RAG_Systems.ipynb`][conversational-m8] walkthrough | Extract separate conversational-RAG and multi-user-isolation lessons. Its SQL-backed session-history material is richer than the shorter notebook labeled Multi-user. Preserve the database/session behavior and shared pipeline dependencies. |
| Captioning/multi-vector multimodal RAG | [`M8_Multimodal_RAG_System_with_GPT_4o.ipynb`][multimodal-m8] | Preserve its text/table/image processing and document-store material. Keep shared text/image embedding retrieval and ColPali visual retrieval as separate techniques. |
| RAG evaluation | The [modular evaluation tutorial][evaluation-tutorial] plus the [detailed per-metric drills][evaluation-drills] | Use richer drills for contextual precision/recall/relevancy, together with modular explanations and offline/live examples. Distribute useful RAG material from repeated walkthroughs and the master notebook; retain unrelated agent/tool evaluation in its existing home. |
| Enterprise RAG | The [handbook Enterprise RAG project][enterprise-handbook] | Make this the authoritative enterprise example. Replace the 13 [interview-preparation notebook duplicates][enterprise-interview] with links after preserving originals. Keep project source, datasets, configuration, and tests intact. |

### Dedicated query lessons to retain individually

- [`a. Multi_Query.ipynb`][multi-query]: query variations and result union.
- [`b. RAG_Fusion.ipynb`][rag-fusion]: reciprocal rank fusion across query results.
- [`c. Step_Back_Prompting.ipynb`][step-back]: abstraction and dual-context retrieval.
- [`d. HyDE.ipynb`][hyde]: hypothetical-document retrieval, including manual and packaged implementations.
- [`Decomposition.ipynb`][decomposition]: sub-question decomposition and synthesis.
- [`a. Routing_LLM_Classifier.ipynb`][classifier-routing]: classifier-based routing.
- [`b. Semantic_Routing.ipynb`][semantic-routing]: embedding-based routing and confidence inspection.
- [`c. Self_Querying_Retrieval.ipynb`][self-querying]: natural-language query construction with metadata filters.

Give query rewriting/expansion its own canonical objective where it adds material beyond multi-query generation. Preserve relevant source sections rather than retaining a second broad query-techniques notebook.

## 5. Anthologies, nested sources, and project boundaries

### Broad notebooks become donors and navigation guides

Map overlapping material in these notebooks to the relevant canonical concepts:

- [`rag_ecosystem.ipynb`][rag-ecosystem].
- [`07_advanced_rag.ipynb`][advanced-rag-overview].
- [`Agent_RAG_Tools_Evaluation_MASTER.ipynb`][evaluation-master].

Their overview/navigation role becomes Markdown documentation. Their original notebooks remain recoverable in the archive. Extract genuinely unique content, such as the ecosystem's ColBERT material, rather than dropping it when retiring the broad walkthrough.

Do not replace several duplicates with another oversized master notebook. For mixed agent/RAG/evaluation sources, preserve non-RAG material in its correct existing home rather than broadening this task into an unrelated reorganization.

### Unique advanced methods remain first-class lessons

Explicitly preserve RAPTOR, HyPE, proposition chunking, relevant-segment extraction, Dartboard retrieval, feedback loops, graph attribution, and additional methods found in the nested source checkout.

LightRAG's dual-level graph retrieval and MemoRAG's global-memory-guided retrieval warrant separate lessons, rather than generic GraphRAG or memory appendices. See the [LightRAG paper][lightrag-paper] and [MemoRAG paper][memorag-paper]. Where a notebook is a pedagogical reimplementation or a managed-service example, label that clearly rather than implying it implements an official research system unchanged.

### Additional titles in the nested checkout

The [nested source checkout][nested-checkout] has 46 notebooks. Nine titles were absent from the outer anthology during the audit:

| Nested notebook | Proposed treatment |
| --- | --- |
| [`Agentic_RAG.ipynb`][nested-agentic] | Preserve its managed RAG/component-evaluation material. Its larger size alone does not make it the best generic agentic-RAG foundation. |
| [`graph_rag_local_attribution.ipynb`][nested-attribution] | Preserve verifiable graph attribution and multi-hop examples; distinguish the provenance objective from a mere local-model variant. |
| [`json_rag.ipynb`][nested-json] | Merge useful JSON-to-retrieval material into structured-data retrieval. Do not describe retrieval-only examples as a complete generation pipeline. |
| [`light_rag.ipynb`][nested-lightrag] | Retain a dedicated LightRAG concept lesson. |
| [`local_rag_huggingface_faiss.ipynb`][nested-local] | Preserve local execution, privacy/resource considerations, and useful implementation material. Separate optional cloud evaluation from any claim of fully local operation. |
| [`memorag.ipynb`][nested-memorag] | Retain memory-guided retrieval as a distinct concept from conversational history. |
| [`multi_faceted_filtering.ipynb`][nested-filtering] | Preserve layered filtering examples in the canonical filtering lesson, with links to distinct diversity/retrieval concepts. |
| [`end-2-end_rag_evaluation.ipynb`][nested-end-to-end] | Preserve completeness, benchmark, and evaluation material in the appropriate evaluation lessons. |
| [`open-rag-eval-example.ipynb`][nested-open-eval] | Preserve useful completeness, citation, and framework-integration examples without duplicating the whole evaluation curriculum. |

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

| Field | Purpose |
| --- | --- |
| Concept ID and learning objective | Enforce one active canonical lesson per concept and distinguish similarly named methods. |
| Canonical destination | Identify the single active notebook path and owning phase. |
| Source notebook paths and cell IDs/sections | Trace preserved explanations, code, diagrams, and exercises back to their donors. |
| Source disposition | Classify every affected source as keep, merge, extract, reference-only, or archive. |
| Input assets and resolved locations | Record PDFs, text, CSV/JSON/JSONL, images, attachments, and other required inputs. |
| Asset identity and checksums | Distinguish real duplicates from unrelated files sharing a basename; support integrity and rollback checks. |
| Local modules and helper interfaces | Preserve imports, function signatures, namespace assumptions, and supporting scripts. |
| Environment and service requirements | Record package pins/extras, environment-variable names, local services, cloud services, and platform constraints. Do not record secret values. |
| Generated artifacts and runtime state | Distinguish caches, vector indexes, extracted figures, reports, database files, collections, and external tables from immutable inputs. |
| Prerequisite lessons/artifacts | Preserve producer -> consumer ordering and document initialization requirements. |
| Validation and blockers | Record checks performed, existing failures, untested cloud paths, and unresolved dependencies honestly. |
| Archive/restore mapping | Make the original material recoverable without relying on memory or notebook titles. |

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

[repo-guidance]: <CLAUDE.md>
[notebook-index]: <NOTEBOOK_INDEX.md>
[requirements]: <requirements.txt>
[empty-qa-project]: <13_Projects/RAG_Systems_Projects/4. Develop a RAG system for Question Answering.ipynb>
[empty-multimodal-project]: <13_Projects/RAG_Systems_Projects/3. Multimodal RAG System.ipynb>
[rag-comprehensive]: <04_Retrieval_and_RAG/09_RAG_with_LangChain/7.1_RAG_Comprehensive.ipynb>
[rag-overview]: <04_Retrieval_and_RAG/01_Introduction_to_RAG/1_rag_overview.ipynb>
[rag-pipeline]: <04_Retrieval_and_RAG/RAG_Production_Course/06_rag_pipeline.ipynb>
[loader-lessons]: <04_Retrieval_and_RAG/06_RAG_Naive_to_Production/01_Loading_Data/>
[embedding-basics]: <04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/4. Embedding_Basics_Alt.ipynb>
[openai-embeddings]: <04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/5. Openaiembeddings_Alt.ipynb>
[embeddings-deep]: <04_Retrieval_and_RAG/RAG_Production_Course/04_embeddings_deep.ipynb>
[vector-stores]: <04_Retrieval_and_RAG/RAG_Production_Course/05_vector_stores.ipynb>
[chunking-comprehensive]: <04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking/1. Document_Splitters_and_Chunkers.ipynb>
[text-splitters]: <04_Retrieval_and_RAG/RAG_Production_Course/02_text_splitters.ipynb>
[semantic-chunking]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/semantic_chunking.ipynb>
[semantic-chunking-manual]: <04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking/2. Semantichunking.ipynb>
[query-transformations]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/>
[hybrid-rag]: <04_Retrieval_and_RAG/06_RAG_Naive_to_Production/03_Hybrid_Search_Strategies/1.1. Hybrid_Search_RAG.ipynb>
[dense-sparse]: <04_Retrieval_and_RAG/06_RAG_Naive_to_Production/03_Hybrid_Search_Strategies/1-densesparse.ipynb>
[parent-document]: <04_Retrieval_and_RAG/03_Indexing_Techniques/Parent_Document_Retrieval.ipynb>
[postgres-parent]: <04_Retrieval_and_RAG/06_RAG_Naive_to_Production/05_Parent_Document_Retriever/08_BetterRetriever.ipynb>
[reranking]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/reranking.ipynb>
[corrective-rag]: <08_Advanced_RAG/RAG_with_LangGraph_Advanced/2. Build_an_Agentic_Corrective_RAG_System_with_LangGraph.ipynb>
[crag-anthology]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/crag.ipynb>
[adaptive-rag]: <08_Advanced_RAG/RAG_with_LangGraph_Advanced/3. Build_an_Adaptive_RAG_System.ipynb>
[self-rag]: <08_Advanced_RAG/RAG_with_LangGraph_Advanced/4. Build_a_Self_RAG_System.ipynb>
[conversational-m8]: <13_Projects/RAG_Systems_Projects/M8_Simple_RAG,_Conversational_RAG_and_Multi_User_Conversational_RAG_Systems.ipynb>
[multimodal-m8]: <13_Projects/RAG_Systems_Projects/M8_Multimodal_RAG_System_with_GPT_4o.ipynb>
[evaluation-tutorial]: <07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/Tutorial_RAG_Agent_Tool_Evaluation/>
[evaluation-drills]: <07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/RAG_Evaluation/DeepEval_Metrics/>
[enterprise-handbook]: <14_AI_Engineering_Handbook/04_Enterprise_RAG/project/>
[enterprise-interview]: <16_AI_Engineer_Interview_Preparation/Enterprise RAG Platform/>
[multi-query]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/1. Rewriting or Query Expansion/a. Multi_Query.ipynb>
[rag-fusion]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/1. Rewriting or Query Expansion/b. RAG_Fusion.ipynb>
[step-back]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/1. Rewriting or Query Expansion/c. Step_Back_Prompting.ipynb>
[hyde]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/1. Rewriting or Query Expansion/d. HyDE.ipynb>
[decomposition]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/2. Decomposition/Decomposition.ipynb>
[classifier-routing]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/3. Routing/a. Routing_LLM_Classifier.ipynb>
[semantic-routing]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/3. Routing/b. Semantic_Routing.ipynb>
[self-querying]: <04_Retrieval_and_RAG/04_Query_Transformation_Techniques/3. Routing/c. Self_Querying_Retrieval.ipynb>
[rag-ecosystem]: <08_Advanced_RAG/RAG_Ecosystem/rag_ecosystem.ipynb>
[advanced-rag-overview]: <04_Retrieval_and_RAG/RAG_Production_Course/07_advanced_rag.ipynb>
[evaluation-master]: <07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/Agent_RAG_Tools_Evaluation_MASTER.ipynb>
[nested-checkout]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/>
[nested-agentic]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/Agentic_RAG.ipynb>
[nested-attribution]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/graph_rag_local_attribution.ipynb>
[nested-json]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/json_rag.ipynb>
[nested-lightrag]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/light_rag.ipynb>
[nested-local]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/local_rag_huggingface_faiss.ipynb>
[nested-memorag]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/memorag.ipynb>
[nested-filtering]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/all_rag_techniques/multi_faceted_filtering.ipynb>
[nested-end-to-end]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/evaluation/end-2-end_rag_evaluation.ipynb>
[nested-open-eval]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/RAG_TECHNIQUES/evaluation/open-rag-eval-example.ipynb>
[shopunow]: <13_Projects/ShopUNow_Agentic_RAG_Capstone/>
[cache-rag]: <08_Advanced_RAG/CacheRAG/README.md>
[shared-data]: <04_Retrieval_and_RAG/shared_data/>
[anthology-root]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/>
[graph-extraction-bundle]: <08_Advanced_RAG/GraphRAG/Constucting Knowledge Graph/>
[anthology-roadmap]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/README_ROADMAP.md>
[anthology-test-config]: <08_Advanced_RAG/Comprehensive_RAG_Techniques/tests/conftest.py>
[lightrag-paper]: <https://arxiv.org/abs/2410.05779>
[memorag-paper]: <https://arxiv.org/abs/2409.05591>
