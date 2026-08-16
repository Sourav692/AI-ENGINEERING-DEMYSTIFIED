# Notebook Index

A single, accurate table of every notebook in this repo, in the order they're meant to be worked through. This reflects the **actual files on disk**. `README.md` and `CLAUDE.md` have since been reconciled to match (see [Known Discrepancies](#known-discrepancies) below for what was fixed and what's still open).

This repo is organized as a sequence of 13 **phases**, each owning exactly one topic — no duplication, framework-specific implementations sit as sibling tracks inside the phase that owns their topic. **Built so far: Phases 2, 3, 4, 5, 7, 8, 13 (fully); Phases 1, 10, 12 (partially).** Phases 6, 9, 11 are scaffolded placeholders with no content yet.

# Phase 1 — Theory & Foundations (`01_Theory_and_Foundations/`)

Optional / compressible. `Math_and_ML_Intuition/`, `Transformer_Architecture/`, `Fine_Tuning_and_RL/` — 🚧 Planned.

## `Model_Landscape_and_Hugging_Face/`

| Module | Notebooks | Topic |
|---|---|---|
| `00_Setup/` | `00-HF-Setup.ipynb` | Hub login, tokens, cache |
| `01_Transformers/` | `00-HF-Basics.ipynb`, `01-Pipelines-for-NLP-Tasks.ipynb`, `02-LLMs.ipynb` | Datasets, NLP pipelines, tokenization, causal LMs |
| `02_Diffusers/` | `00-Understanding-Image-Data.ipynb`, `01-Understanding-Diffusion-Models.ipynb`, `02-AutoPipelines-Diffusers.ipynb` | Image data, DDPM / Stable Diffusion, AutoPipeline |
| `03_Video_Models/` | `00-Stable-Video-Diffusion.ipynb`, `01-Image2VideoGen-XL.ipynb` | Image-to-video generation |
| `04_Audio_Models/` | `00-Audio-Data.ipynb`, `01-Audio-Classification.ipynb`, `02-Audio-Transcription.ipynb`, `03-Audio-Generation.ipynb` | Waveforms, AST, ASR/diarization, EnCodec |
| `05_Gradio/` | `01-Gradio-Introduction.ipynb` … `07-Styling-and-Themes.ipynb` (7 nb) | Gradio UIs for HF models |
| `06_Pretrained_Models/` | `Accessing_Pre_Trained_Models.ipynb` | Loading pretrained models from the Hub |

# Phase 2 — LangChain Fundamentals & Prompting (`02_LangChain_Fundamentals_and_Prompting/`)

## `LangChain_Fundamentals/`

| # | Module | Topic |
|---|---|---|
| 1 | `01_Getting_Started/` | Commercial + open-source LLMs, natively and via LangChain (8 nb) |
| 2 | `02_Inputs_Outputs_Prompts/` | Inputs/outputs, prompt templates, LLM vs ChatModel, output parsers (6 nb) |
| 3 | `03_LCEL/` | LangChain Expression Language, Runnables, chain migrations (7 nb) |
| 4 | `04_Chains/` | Chain basics, advanced chains, branching/routing/merging (4 nb) |
| 5 | `05_Summarization/` | Text summarization (2 nb) |

Also has `Docs/` (supporting PDFs/CSV), `images/`, `Reference_Links.md`. Tool-calling/agents, memory, RAG, LangSmith, advanced features, and microservices deployment moved to their own dedicated phases (see Known Discrepancies).

## `Prompt_and_Context_Engineering/Prompt_Engineering/`

| Section | Notebook | Topic |
|---|---|---|
| `01_Core_Patterns/` | `M2_Exploring_Prompt_Engineering_Patterns.ipynb` | Core prompt-engineering patterns |
| `02_Advanced_Patterns/` | `M3_Exploring_Advanced_Prompt_Engineering_Patterns.ipynb` | Advanced prompt-engineering patterns |
| `03_Hands_On_by_Model/` | `M5_Google_Gemini.ipynb`, `M5_OpenAI_ChatGPT.ipynb`, `M6_Meta_Llama_3_2_1B_HuggingFace.ipynb`, `M6_Meta_Llama_3_2_90B_Groq.ipynb` | Hands-on pattern practice across 4 models/providers |
| `04_Multimodal_Prompting/` | `M7_Google_Gemini.ipynb`, `M7_OpenAI_GPT_4o.ipynb` | Multimodal prompting |
| `05_Real_World_Applications/` | `M7_GPT_4o_and_Llama_3_2_Real_World_Tasks.ipynb` | Applying patterns to real-world tasks |
| `Assignments/` | `Assignment.ipynb` | Practice assignment (+ PDF, images) |

## `Prompt_and_Context_Engineering/Context_Engineering/` — 🚧 Planned

# Phase 3 — LangGraph Fundamentals (`03_LangGraph_Fundamentals/`)

## `01_Foundations/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_State_and_Graph_Basics.ipynb` | Building a simple agent graph and managing state |
| 2 | `02_MessageState.ipynb` | `MessagesState` — the pre-built state for chat graphs |
| 3 | `03_Conditional_Routing.ipynb` | Conditional routing (`add_conditional_edges`) |
| 4 | `04_LLM_Powered_Chatbot.ipynb` | Building an LLM-powered chatbot |
| 5 | `05_Augmented_LLM_with_Tools.ipynb` | Augmented LLM with tools (`bind_tools`) |
| 6 | `06_ReAct_Agent.ipynb` | Simple tool-use ReAct agent |
| 7 | `07_Different_Graph_States.ipynb` | Four ways to define graph state |
| 8 | `08_Pydantic_State_Validation.ipynb` | `TypedDict` vs Pydantic state validation |
| 9 | `09_Node_Patterns.ipynb` | Node arguments, config & runtime context |
| 10 | `10_Runtime_Context.ipynb` | Injecting external dependencies via runtime context |
| 11 | `11_Command_Objects.ipynb` | `Command` — combined routing + state updates |

## `02_Core_Capabilities/`

Memory lives in Phase 7 instead — see below.

| Section | Notebook | Topic |
|---|---|---|
| `02_Routing/` | `01_Router_Agentic_RAG_System.ipynb` | Customer-support router agentic RAG system |
| `02_Routing/` | `02_Customer_Support_Router_RAG_Alt.ipynb` | Alternate implementation |
| `02_Routing/` | `03_Customer_Support_Router_RAG_Databricks_Alt.ipynb` | Databricks Vector Search variant |
| `03_Human_in_the_Loop/` | `01_HITL_Basics.ipynb` | Human-in-the-loop basics |
| `03_Human_in_the_Loop/` | `02_HITL_Interrupt_and_Resume.ipynb` | Interrupt/resume approaches |
| `03_Human_in_the_Loop/` | `03_HITL_State_Modification.ipynb` | Approve/reject + state modification pattern |
| `03_Human_in_the_Loop/` | `04_HITL_Dynamic_Breakpoints.ipynb` | Dynamic breakpoints, reviewing tool calls |
| `04_Advanced_State/` | `01_Advanced_State.ipynb` | Input/output state, advanced state patterns |
| `05_Subgraphs/` | `01_Subgraphs.ipynb` | Graph composition via subgraphs |
| `06_Async_and_Streaming/` | `01_Async_and_Streaming.ipynb` | Async operations & streaming output |
| `07_Retries/` | `01_Retries.ipynb` | Fault-tolerant nodes with `RetryPolicy` |

Note: `02_Routing/`'s notebooks are also agentic RAG examples — kept here rather than moved to Phase 4/8 since they're the only routing-mechanics demo in this phase (see Known Discrepancies).

# Phase 4 — Retrieval & RAG (`04_Retrieval_and_RAG/`)

Foundational RAG only. Agentic/advanced RAG lives in Phase 8.

## `Introduction_to_RAG/`

| Notebook | Topic |
|---|---|
| `1_rag_overview.ipynb` | RAG overview |
| `Basics of RAG.ipynb` | RAG basics |
| `Indexing.ipynb` | Indexing |
| `Langchain+Rag.ipynb` | RAG with LangChain |
| `Retrieval Strategies.ipynb` | Retrieval strategies |

## `Embeddings_and_Vector_Databases/`

| Notebook | Topic |
|---|---|
| `1. Embedding_Models.ipynb`, `1.1. Embedding.ipynb`, `1.2. Openaiembeddings.ipynb` | Embedding models |
| `2. Vector_Databases.ipynb`, `2.1. Chromadb.ipynb`, `2.2. Faiss.ipynb`, `2.3. Othervectorstores.ipynb`, `2.4. Datastaxdb.ipynb`, `2.5. PineconeVectorDB.ipynb` | Vector database options |
| `3. Retrievers.ipynb` | Retrievers |
| `4. Embedding_Basics_Alt.ipynb`, `5. Openaiembeddings_Alt.ipynb` | Alternate embedding walkthroughs (from `Vector_Database_and_Embedding_Demystified`) |
| `6. Compare_Embedding_Models.ipynb` | Comparing embedding models |
| `7. Hybrid_Search_and_Reranking.ipynb` | Hybrid search + reranking |

## `RAG_Naive_to_Production/`

| # | Section | Topic |
|---|---|---|
| 1 | `01_Loading_Data/` | Document loaders — text, markdown, CSV, JSON, PDF, Word, directory, YouTube transcript, URL, custom (11 nb) |
| 2 | `02_Splitting_and_Chunking/` | Document splitters/chunkers, semantic chunking |
| 3 | `03_Hybrid_Search_Strategies/` | Dense+sparse hybrid search, reranking, MMR |
| 4 | `04_Query_Enhancement/` | Query expansion, decomposition, HyDE, multi-query retrieval |
| 5 | `05_Parent_Document_Retriever/` | Two-stage (parent-document) retrieval |
| 6 | `06_Postprocessing_Documents/` | Cross-encoder reranking |
| 7 | `07_Building_RAG_Systems/` | Simple RAG, contextual retrieval, RAG with sources, RAG with citations |

## `Query_Transformation_Techniques/`

| Notebook | Topic |
|---|---|
| `Naive_RAG.ipynb` / `Naive_RAG_Alt.ipynb` | Baseline naive RAG |
| `Multi_Query.ipynb`, `RAG_Fusion.ipynb`, `Decomposition.ipynb`, `Step_Back_Prompting.ipynb`, `HyDE.ipynb` | Query transformation techniques |
| `Multi_Representation_Indexing.ipynb`, `Parent_Document_Retrieval.ipynb`, `Self_Querying_Retrieval.ipynb` | Indexing/retrieval strategies |
| `Routing_LLM_Classifier.ipynb`, `Semantic_Routing.ipynb` | Query routing |
| `CrossEncoder_Reranking.ipynb` | Cross-encoder reranking |

## `Multimodal_and_Document_Intelligence/`

| Notebook | Topic |
|---|---|
| `1-multimodalopenai.ipynb` | Multimodal RAG with OpenAI |

Also `shared_data/` at the phase root — supporting PDFs/data referenced by several notebooks above via relative paths from the source repo (`RAG_Demystified`); exact path depth wasn't re-verified after the move.

## `RAG_with_LangGraph/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_Simple_Agentic_RAG.ipynb` | Simple RAG agent (PDF → Chroma → LLM) |
| 2 | `02_Simple_Agentic_RAG_Databricks.ipynb` | Same agent on Databricks Vector Search |

## `RAG_with_LangChain/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `7.0_RAG_Essentials.ipynb` | RAG essentials |
| 2 | `7.1_RAG_Comprehensive.ipynb` | Comprehensive RAG |
| 3 | `7.2_Filtered_Search.ipynb` | Filtered search |
| 4 | `7.3_Indexing_API.ipynb` | Indexing API |

Plus supporting `api.py`, `docker-compose.yaml`, FAISS/Postgres assets.

# Phase 5 — AI Agent Fundamentals (`05_AI_Agent_Fundamentals/`)

## `LangChain_Tools_and_Agents/`

| # | Section | Topic |
|---|---|---|
| 1 | `01_Tools_and_Functions/` | Tool calling, tool-calling agents, OpenAI tool calling (4 nb) |
| 2 | `02_Agents/` | Agents (1 nb) |
| 3 | `03_Applied_Projects/` | 16 applied projects — see `03_Applied_Projects/README.md` for the full list (research assistant, multi-user conversational research, text-to-SQL, financial analyst, travel assistant, and 11 short exercises) |

## `AI_Agents_with_LangGraph/`

| # | Notebook / Folder | Topic |
|---|---|---|
| 1 | `01_Research_Assistant_Chatbot.ipynb` | Web-search research assistant (Tavily) |
| 2 | `02_Competitive_Intelligence_Agent.ipynb` | Business/competitive intelligence agent with structured output |
| 3 | `03_Multi_Agent_Research_Summarization/` | Multi-agent research + summarization pipeline |
| 4 | `04_Planning_Agent_Deep_Research/` | Planning-pattern deep research agent |
| 5 | `05_Reflective_Code_Generation_Agent/` | Reflective, self-correcting code generation agent |
| 6 | `06_Reflective_Dynamic_Planning_Agent/` | Reflective dynamic planning agent |
| 7 | `07_Supervisor_Multi_Agent_Financial_Research/` | Supervisor-pattern multi-agent financial research system |
| 8 | `08_Web_Research_Agent_ReAct_Alt.ipynb` | Alternate ReAct-pattern web research agent |
| 9 | `09_Financial_Analyst_Tool_Use_Agent/` | Tool-use financial analyst agent |
| 10 | `10_Hotel_Reservations_Multi_Agent_System/` | Full-stack hotel reservations multi-agent system |
| 11 | `11_Software_Engineering_Multi_Agent_System/` | Full-stack software-engineering multi-agent system |

## `Workflow_and_Agent_Patterns/`

| Section | Notebook | Topic |
|---|---|---|
| `01_Tool_Use/` | `01_Tool_Use_Agentic_Systems.ipynb`, `02_Tool_Calling_vs_ReAct.ipynb`, `03_Tool_Use_Alt.ipynb`, `04_ReAct_Alt.ipynb` | Tool-use strategies |
| `02_Planning/` | `01_Parallel_Steps_Execution.ipynb`, `02_Map_Reduce_with_Send_API.ipynb`, `03_Parallelization_Alt.ipynb`, `04_Planning_Overview_Alt.ipynb` | Planning patterns |
| `03_Reflection/` | `01_Reflection_Agents.ipynb`, `02_Reflexion_Agents.ipynb`, `03/04_Reflection_Overview_Alt*.ipynb` | Reflection & Reflexion |
| `06_Router/` | `01_Routing.ipynb` | Router pattern |
| `07_Prompt_Chaining/` | `01_Prompt_Chaining.ipynb` | Sequential prompt-chaining |
| `08_Evaluator_Optimizer/` | `01_Evaluator_Optimizer.ipynb` | Evaluator-optimizer loop |
| `09_Orchestrator_Worker/` | `01_Orchestrator_Worker.ipynb` | Runtime-dynamic task delegation |
| `11_Advanced_Cognitive_Patterns/` | `01`–`12` | PEV, blackboard, episodic+semantic memory, tree-of-thoughts, mental loop, meta-controller, graph, ensemble, dry-run, RLHF, cellular automata, reflexive-metacognitive |

Also `Design_Patterns_Reference.md` + `images/`, `Reference_link_Workflow_Patterns.md`.

# Phase 6 — Agent SDKs (First-Party) (`06_Agent_SDKs_First_Party/`) — 🚧 Planned

`Google_ADK/`, `OpenAI_Agents_SDK/`, `Google_AI_SDK/`

# Phase 7 — Advanced Agentic Systems (`07_Advanced_Agentic_Systems/`)

## `Memory_and_State/LangGraph/`

| Section | Notebook | Topic |
|---|---|---|
| `01_Memory/` | `01_Memory_and_Conversational_Agent.ipynb`, `02_Memory_Optimizations.ipynb` | Memory & threads |
| `01_Memory/memory/` | `02_Agent_Memory_Types_SQLite.ipynb` | Agent memory types with SQLite persistence (self-contained sub-module) |
| `02_Long_Term_Memory/` | `01_Long_Term_Memory.ipynb` | Persistent long-term memory (PostgreSQL) |

## `Memory_and_State/LangChain/Memory/`

9 notebooks — chat message memory, conversation chains, multi-user in-memory & SQL persistent storage, ConversationQA.

## `Multi_Agent_Orchestration/`

| Section | Notebook | Topic |
|---|---|---|
| `01_Agent_Patterns/` | `01_Agent_Patterns.ipynb`, `02_Supervisor_Multi_Agent_Alt.ipynb`, `03_Multi_Agent_Overview_Alt.ipynb` | Supervisor pattern + alternates |
| `02_Multi_Agent_Swarm/` | `01_Multi_Agent_Swarm.ipynb` | Peer-to-peer/swarm multi-agent architecture |

## `Deep_Agents_and_Harness_Engineering/`

Not notebooks — Python scripts + a `deepagents`-based multi-agent system:

| Path | Content |
|---|---|
| `examples/simple_coding_agent.py` | Default agent run — `FilesystemBackend`, no code execution |
| `examples/long_term_memory_agent.py` | Adds cross-thread persistent memory (JSON, upgradeable to PostgreSQL) |
| `skills/senior-developer/`, `code-reviewer/`, `research-agent/`, `memory-manager/` | Core orchestration agents |
| `skills/aia-customer-analytics/`, `aia-distribution-channels/`, `aia-policy-underwriting/`, `aia-claims-analytics/` | Databricks Genie analytics agents |
| `app/` | Standalone deployable version (FastAPI + frontend, Docker) |
| `docs/` | Architecture diagram, memory-types writeup |

## `Evaluation_and_Eval_Harnesses/`

### `Agent_Evaluation/`

| Path | Content |
|---|---|
| `DeepLearningAI_Arize/Lab 1 - Building your Agent/L3.ipynb` | Build the sales-agent used as the eval target |
| `DeepLearningAI_Arize/Lab 2 - Tracing your Agent/L5.ipynb` | Tracing (kept with this course, not Phase 12) |
| `DeepLearningAI_Arize/Lab 3 - Adding Router & Skill Evaluations/L7.ipynb` | Router & skill evaluations |
| `DeepLearningAI_Arize/Lab 4 - Adding Trajectory Evaluations/L9.ipynb` | Trajectory evaluations |
| `DeepLearningAI_Arize/Lab 5 - Adding Structure to your Evaluations/L11.ipynb` | Structured evaluation harness |
| `DeepLearningAI_Arize/Appendix - Resources, Tips and Help/Appendix.ipynb` | Course appendix |
| `CrewAI_Travel_Planner/` | CrewAI travel-planner app + DeepEval `TaskCompletionMetric` tests (`evaluate_endtoend_test.py`) |

### `RAG_Evaluation/`

| Path | Topic |
|---|---|
| `1.Retriever_Evaluation_Metrics.ipynb` | Retriever evaluation metrics |
| `2.Generator_Evaluation_Metrics.ipynb` | Generator evaluation metrics |
| `3.Custom_LLM_as_a_Judge _(G-Eval).ipynb` | Custom LLM-as-judge (G-Eval) |
| `4. End_to_End_RAG_System_Evaluation.ipynb` | End-to-end RAG evaluation |
| `Build_RAG_Pipeline_with_Source.ipynb` | Supporting pipeline |
| `DeepEval_Metrics/Contextual_Precision.ipynb` | DeepEval contextual precision drill |
| `DeepEval_Metrics/Contexual_Recall.ipynb` | DeepEval contextual recall drill (source filename spelling kept) |
| `DeepEval_Metrics/Contextual_Relevancy.ipynb` | DeepEval contextual relevancy drill |
| `RAGAS/` | RAGAS scripts (`Faithfulness.py`, `ContextRecall.py`, `Evaluate_RAG.py`, …) + `fastapi_rag_bot/` eval target |

### `LLM_as_Judge/`

| Path | Topic |
|---|---|
| `DeepEval_GEval/test_firstdeepeval.py` | Minimal DeepEval G-Eval correctness judge |

# Phase 8 — Advanced RAG (`08_Advanced_RAG/`)

Depends on Phases 5 & 7 — sequenced after both.

## `RAG_with_LangGraph_Advanced/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_Advanced_RAG_Agent.ipynb` | Advanced retrieval — grading, rewriting |
| 2 | `02_RAG_as_Tool_in_Agents.ipynb` | RAG as a composable tool inside a larger agent (agentic RAG) |
| 3 | `1. Build_a_Healthcare_Customer_Support_Router_Agentic_RAG_System.ipynb` | Healthcare customer-support router + agentic RAG |
| 4 | `2. Build_an_Agentic_Corrective_RAG_System_with_LangGraph.ipynb` | Corrective RAG (CRAG) with LangGraph |
| 5 | `3. Build_an_Adaptive_RAG_System.ipynb` | Adaptive RAG |

## `Comprehensive_RAG_Techniques/`

The NirDiamant `RAG_Techniques` collection, merged whole (not split notebook-by-notebook — its ~35 notebooks share `helper_functions.py`/`data/`/`images/` via relative paths). Ranges basic → advanced: simple RAG, CSV RAG, reliable RAG, proposition chunking, query transformations, HyDE, context enrichment, contextual compression, contextual chunk headers, CRAG, Self-RAG, RAPTOR, fusion retrieval, hierarchical indices, GraphRAG (incl. Microsoft GraphRAG, Milvus variant), adaptive retrieval, multimodal RAG (captioning, ColPali), reranking, explainable retrieval, relevant segment extraction, dartboard, document augmentation, retrieval with feedback loop — plus LlamaIndex variants of several. See `README_ROADMAP.md` for the full breakdown and why it wasn't split.

## `GraphRAG/`

| Path | Content |
|---|---|
| `AI-Enhancement-with-Knowledge-Graphs---Mastering-RAG-Systems/` | Full KG course — intro to KG, KG+RAG systems, indexing/embedding, end-to-end KG build |
| `Constucting Knowledge Graph/` | Entity/relationship extraction, graph visualization, deployable app |
| `KG from Text/` | Exercise notebook |

## `CacheRAG/` — 🚧 Planned

## Additional apps in this phase

`building-adaptive-rag/` — standalone adaptive-RAG app. `mcp_a2a_agentic_rag/` — agentic RAG app built on MCP + A2A protocols (kept RAG-first here rather than split into Phase 9, per user decision).

# Phase 9 — Agent Protocols (`09_Agent_Protocols/`) — 🚧 Planned

`MCP/` (4 subfolders), `ACP/` (3 subfolders), `A2A/` (3 subfolders)

# Phase 10 — Alternative Agent Frameworks (`10_Alternative_Agent_Frameworks/`)

## `CrewAI/`

| Track | Content |
|---|---|
| `01_Foundations/Some_Simple_Agents/` | 8 nb — fitness tracker, travel advisor, image generation, book recommendation, data analyst, fraud detection, employee onboarding, document summarization |
| `04_Applications/` | Education assistant, mock interviewer, social media agent, research/write article, customer support automation, outreach campaign, event planning, financial analysis collaboration, job application tailoring (9 project sets) |

## `AutoGen/`

| Track | Content |
|---|---|
| `01_Foundations/Some_Simple_Agents/` | Building agents with AutoGen, research assistant, coding agent |
| `04_Applications/` | Smart content generation, smart health assistant, financial portfolio manager, agentic RAG for eCommerce, stock market analysis agent, Notion MCP agent, Data Analyzer GPT (7 project sets) |

## `DSPy/`, `PydanticAI/`, `Orchestration_Frameworks_Overview/` — 🚧 Planned

# Phase 11 — Claude Code & AI Coding Tools (`11_Claude_Code_and_AI_Coding_Tools/`) — 🚧 Planned

`Claude_Code/`, `Agent_Skills/`, `Claude_API_and_Agent_SDK/`, `AI_Coding_Tool_Landscape/`

# Phase 12 — Production & Observability (`12_Production_and_Observability/`)

## `LLMOps_and_AI_Infrastructure/`

| Section | Notebook | Topic |
|---|---|---|
| `Tracing_and_Observability/LangSmith/` | `01_LangSmith_Basics.ipynb` | LangSmith basics |
| `Tracing_and_Observability/LangFuse/` | — | 🚧 Planned |
| `Tracing_and_Observability/` | `02_Callbacks.ipynb` | LangChain callback mechanism |
| `Caching_and_Performance/` | `01_Caching.ipynb`, `02_Streaming.ipynb` | Caching, streaming |
| `Cost_Monitoring/` | `01_LLM_Cost_Monitoring.ipynb` | Tracking LLM API costs |

Also `00_Advanced_LangChain_Overview.ipynb`.

## `Safety_and_Alignment/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_Moderating_Chains.ipynb` | Content moderation in LangChain pipelines |

## `DevOps_and_Deployment/`, `Security_and_Compliance/` — 🚧 Planned

# Phase 13 — Projects (`13_Projects/`)

## `LangGraph_Fullstack_Capstone/`

Not notebooks — deployable apps and tests: `fullstackapp/` (FastAPI + Angular + Postgres), `unit_tests/` (pytest), `streamlit_apps/` (doc-entity-extractor, knowledge-graphs-with-langextract).

## `LangChain_Microservices_Capstone/`

Not notebooks — LangChain deployed as microservices: Docker, k8s-style manifests, frontend, `service2/`, `service3/`.

## `RAG_Systems_Projects/`

| Notebook | Topic |
|---|---|
| `1. Build_Document_Retriever_Search_Engine.ipynb` | Document retriever search engine |
| `2. Multi-user Conversational RAG System.ipynb` | Multi-user conversational RAG |
| `3. Multimodal RAG System.ipynb` | Multimodal RAG system |
| `4. Develop a RAG system for Question Answering.ipynb` | RAG for Q&A |
| `M8_Multimodal_RAG_System_with_GPT_4o.ipynb` | Multimodal RAG with GPT-4o |
| `M8_Simple_RAG,_Conversational_RAG_and_Multi_User_Conversational_RAG_Systems.ipynb` | Combined simple/conversational/multi-user RAG |
| `RAG system for Question Answering.ipynb` | RAG for Q&A (alternate) |

Also `data/` and `final_project/` (a built Chroma DB from the source repo).

## `ShopUNow_Agentic_RAG_Capstone/`

Not notebooks-only — `01_create_vector_databases.ipynb`, `02_agentic_rag_system.ipynb`, plus `data/` (7 domain JSON datasets), `ShopUNow_Agentic_RAG_Architecture.pptx`, `WALKTHROUGH.md`, `sample_data.py`.

## Six more full-stack apps

`AI_Powered_Customer_Support/`, `Automated_Candidate_Interview_Evaluation_System/`, `End_to_End_Medical_Chatbot/`, `Pipecat_QuickStart/`, `Realtime_Source_Code_Analyzer/`, `Realtime_Voice_AI_Agent_with_RAG/` — each a standalone deployable app (own `README.md`, dependencies, and in most cases Docker/deployment config). See `13_Projects/README.md` for a one-line summary of each.

# Planned Phases (no content yet)

| Phase | Folder |
|---|---|
| 1 | `01_Theory_and_Foundations/` *(optional)* |
| 6 | `06_Agent_SDKs_First_Party/` |
| 9 | `09_Agent_Protocols/` |
| 11 | `11_Claude_Code_and_AI_Coding_Tools/` |

## Archive (`archive/`)

Retired notebooks, kept for reference but not part of the learning path: `04_Reference_Course/` (9 notebooks) and `Ultimate_RAG_Bootcamp/` (6 notebooks + PDFs).

---

## Known Discrepancies

**Fixed (abbreviated — full detail in prior entries below):**
- Chapter/notebook count and naming fixes across the original LangGraph course.
- `deepagents` content vendored in from `Deep_Agent_Demystified`.
- `Agentic_Design_Pattern_Demystified-main` merged in — filled the Reflection gap, added Router/Prompt-Chaining/Evaluator-Optimizer/Orchestrator-Worker/Multi-Agent-Swarm/Advanced-Cognitive-Patterns, five new application builds, and several `_Alt` notebooks.
- **2026-08-16 — three successive top-level restructurings**, converging on the current 13-phase model:
  1. LangGraph's 7 chapters, originally loose at the repo root, were nested under one `01_LangGraph/` parent (framework-per-folder pattern).
  2. Replaced entirely: rebuilt around **learning phase** instead of framework, after comparing against a reference tracker (`aie-learning-tracker.vercel.app`) — `01_Theory_and_Foundations/` … `12_Projects/`, LangGraph's content split across several phase tracks.
  3. **Final restructuring (this one):** `LangChain_Demystified-main/` and `Prompt-Engineering-Demystified-main/` were merged in, which exposed real duplication in restructuring #2 (RAG, agents, memory, and observability each had 2–3 different homes across phases). Rebuilt around a stricter rule — **each topic owns exactly one phase**, framework implementations sit as sibling tracks inside it — and split into 13 phases: Theory & Foundations (1), LangChain Fundamentals & Prompting (2, trimmed to true fundamentals), LangGraph Fundamentals (3, mechanics only), Retrieval & RAG (4, foundational only), AI Agent Fundamentals (5, both frameworks' agent-building consolidated), Agent SDKs First-Party (6, promoted to its own phase), Advanced Agentic Systems (7), Advanced RAG (8, new — agentic/self-correcting RAG + CacheRAG/GraphRAG, deliberately sequenced *after* Phases 5 & 7 since it depends on knowing agents), Agent Protocols (9), Alternative Agent Frameworks (10), Claude Code & AI Coding Tools (11), Production & Observability (12, absorbed LangChain's LangSmith/advanced-features/moderation content), Projects (13, absorbed LangChain's microservices module as a second capstone). `LangChain_Demystified`'s `_Archive/` and root scaffolding were discarded per established precedent; its two `.claude/skills/` were preserved at `.claude/skills-candidates/` for separate review. Updated everywhere a path was hardcoded: `pyproject.toml` (ruff excludes — now 3 JS frontends), `README.md`, this file, `CLAUDE.md`, `docs/*.html`, and the `ai-roadmap-organizer` skill's `roadmap-map.md`/`SKILL.md`. The same Windows directory-lock issue hit `Deep_Agents_and_Harness_Engineering` and its `app/` subfolder twice more during this pass — same drain-contents-then-remove-shell workaround each time, no data lost (verified via notebook counts before/after: 132 total).

- **2026-08-17 — `RAG_Demystified-main` merged in**, filling every remaining Phase 4/7/8 placeholder that used to be empty. Split across 3 phases by the same one-topic-one-phase rule: `1. Introduction/` → Phase 4's `Introduction_to_RAG/`; `2. Concepts/4. Embedding...` → Phase 4's `Embeddings_and_Vector_Databases/` (filled the placeholder); `2. Concepts/{2,3,5,6,7,8,9}` (loading/chunking/hybrid-search/query-enhancement/parent-doc-retrieval/postprocessing/building-RAG-systems) → Phase 4's `RAG_Naive_to_Production/` (filled); `2. Concepts/10. Multi-Modal RAG` → Phase 4's `Multimodal_and_Document_Intelligence/` (filled); `2. Concepts/11. Evaluating RAG Systems` → Phase 7's `Evaluation_and_Eval_Harnesses/RAG_Evaluation/` (filled); `6. Graph_RAG` → Phase 8's `GraphRAG/` (filled); `7. Agentic_RAG/Agentic RAG Systems with LangGraph` → extended Phase 8's existing `RAG_with_LangGraph_Advanced/`; `5. Projects` → Phase 13's new `RAG_Systems_Projects/`. Two judgment calls made with the user: `4. Advanced RAG` (despite its name) is query-transformation content requiring no agent knowledge, so it went to Phase 4 as `Query_Transformation_Techniques/` rather than Phase 8; and `3. rag_technniques` (the well-known NirDiamant `RAG_Techniques` collection) was kept whole as Phase 8's `Comprehensive_RAG_Techniques/` rather than split, since its ~35 notebooks share `helper_functions.py`/`data/`/`images/` via relative paths that splitting would have broken. Two standalone apps from `7. Agentic_RAG` (`building-adaptive-rag/`, `mcp_a2a_agentic_rag/` — the latter using MCP+A2A protocols) stayed in Phase 8 rather than moving to Phase 9 or 13, per user decision. A shared root `data/` folder (referenced by several notebooks via relative paths) was brought along as `04_Retrieval_and_RAG/shared_data/` — exact relative-path depth wasn't reconstructed after the move, since fixing that would mean editing notebook content, out of scope for a reorganization. During the move, a Windows/Git-Bash `mv` quirk briefly renamed the existing `RAG_with_LangGraph_Advanced/` folder to `AgenticRAG` mid-operation (no data lost, caught immediately via notebook-count verification and fixed). Total notebook count went from 132 to 249 (117 added), verified exactly matching before executing docs updates.

- **2026-08-17 — `Vector_Database_and_Embedding_Demystified-main` merged in** (4 notebooks + a PDF) — added directly into Phase 4's existing `Embeddings_and_Vector_Databases/` track, no new sections needed. Two notebooks overlapped conceptually with existing content and were suffixed `_Alt`; two were genuinely new (embedding-model comparison, hybrid search + reranking). Root scaffolding (`README.md`, `.gitignore`) discarded per established precedent.

- **2026-08-17 — `AgenticAI_Projects_Demystified-main` merged in** (the largest merge yet — 66 new notebooks, plus 10 new full-stack apps). Before merging, checked for overlap with content already in the repo and found 5 project folders under "Projects with LangGraph" (`Customer_Support_Router_RAG`, `Multi_Agent_Research_Summarization`, `Planning_Agent_Deep_Research`, `Reflective_Code_Generation_Agent`, `Reflective_Dynamic_Planning_Agent`, `Supervisor_Multi_Agent_Financial_Research`) were byte-identical or near-identical duplicates of notebooks already merged in from `Agentic_Design_Pattern_Demystified` — skipped rather than re-added. Genuinely new content: `AI_Agents_with_LangGraph/` gained 3 more builds (09–11); `LangChain_Tools_and_Agents/` gained a 16-item `03_Applied_Projects/` track; **Phase 10 (Alternative Agent Frameworks) went from fully-planned to partially-built** — `CrewAI/` and `AutoGen/` each filled from empty 4-folder skeletons using a Foundations/Applications split (simple-agent notebooks → `01_Foundations/`, everything else → `04_Applications/`, per user decision — `02_Core_Capabilities/`/`03_Multi_Agent_Patterns/` stayed empty since the source content didn't split into those categories); Phase 13 grew from 3 to 10 projects (a new `ShopUNow_Agentic_RAG_Capstone/` plus 6 more standalone full-stack apps, kept flat per user decision rather than grouped under a parent folder). Discarded: a duplicate `Capstone Project.zip` (redundant with the unzipped folder beside it), root scaffolding, and two `.claude/skills/` confirmed byte-identical to ones already staged at `.claude/skills-candidates/` from the `LangChain_Demystified` merge. Added 2 more JS frontends to `pyproject.toml`'s ruff excludes (CrewAI's simple-agents app, the voice-RAG project's frontend). A repo-wide hardcoded-secret sweep of the new content found nothing (checked provider key formats, `CONFIG_LIST.json`, and note/cred-style filenames).

- **2026-08-17 — `Agents_Evaluation_Demystified-main` merged in**, filling Phase 7's remaining `Agent_Evaluation/` and `LLM_as_Judge/` placeholders and extending `RAG_Evaluation/`. Split by topic, not dumped wholesale: DeepLearning.AI + Arize labs stayed whole under `Agent_Evaluation/DeepLearningAI_Arize/` (Lab 2 tracing included — shared parquet/helpers, dominant identity is agent eval); CrewAI travel-planner + DeepEval task-completion tests → `Agent_Evaluation/CrewAI_Travel_Planner/` (not Phase 10); DeepEval metric drills + RAGAS → `RAG_Evaluation/`; first DeepEval G-Eval script → `LLM_as_Judge/`. Skipped the source's `Evaluating RAG Systems/` folder after hash/size compare: 3 notebooks identical to ones already merged from `RAG_Demystified`, 2 older unexecuted copies of the same retriever/generator notebooks. Discarded root scaffolding, `img/`, `.deepeval` telemetry, `data/tmp` docx, Excel lockfile. Phase 7's four tracks are now all built.

- **2026-08-17 — `Huggingface_Demystified-main` merged in**, filling Phase 1's `Model_Landscape_and_Hugging_Face/` placeholder (the other three Phase 1 tracks stay planned). Bootcamp modules mapped to `00_Setup/` … `05_Gradio/` (folder names underscored to match repo convention; notebook/asset names unchanged so relative `cat.png` / `interview.mp3` paths still resolve). The one-notebook "Mastering Generative AI with LLMs" course became `06_Pretrained_Models/`. Gradio stayed in this track (HF demo surface), not Phase 12. Not fine-tuning and not transformer-architecture theory — those remain the empty `Fine_Tuning_and_RL/` and `Transformer_Architecture/` tracks. Discarded root scaffolding and `.gitkeep`. Phase 1 went from fully-planned to partially-built.

**Still open:**
- Several notebooks don't open with a proper `# Title` markdown cell (mid-document subheading instead) — pre-existing, not fixed, would require editing notebook content.
- `LangChain_Fundamentals/` and its descendants don't use the `helpers` factory (they instantiate LLM clients directly) — a pre-existing property of the merged-in source repo, not a convention violation.
- Several `RAG_Demystified`-sourced notebooks reference a shared `data/` folder via `../../data/`-style relative paths that may no longer resolve correctly after being moved into the new phase structure — not fixed, would require editing notebook content.
