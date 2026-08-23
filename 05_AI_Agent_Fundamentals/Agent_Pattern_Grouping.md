# Agent Pattern Grouping

How this roadmap groups agent patterns. Teach and number like Anthropic / Gulli (primitives → loops → coordination). Name like Fareed Khan (Reflection vs Reflexion vs LATS). Store on disk by **topic + prerequisite** — never dump every named architecture into Phase 5.

Sources this map reconciles:

- [FareedKhan-dev/all-agentic-architectures](https://github.com/FareedKhan-dev/all-agentic-architectures) — 35 architectures in mechanism families
- [evoiz/Agentic-Design-Patterns](https://github.com/evoiz/Agentic-Design-Patterns) (Gulli) — 21 chapters as a book TOC
- Anthropic “Building Effective Agents” — five workflow primitives (already in `4. Workflow_Pattern/`)

Do not copy either GitHub repo as a single folder. Layer A and B live in Phase 5. Layer C already has other phase owners.

**Nothing from either repo is excluded.** Every Fareed architecture and every Gulli chapter/appendix is in the map. “Not a Phase 5 peer” means *put it in the phase that already owns that topic*, not *skip it*.

---

## Disk shape (target)

```
05_AI_Agent_Fundamentals/                    # Layers A + B only
├── 4. Workflow_Pattern/                     # Layer A — workflow primitives
│   ├── 1_Prompt_Chaining/
│   ├── 2_Routing/
│   ├── 3_parallelization/
│   ├── 4_orchestrator-worker/
│   └── 5_Evaluator-optimizer/
│
└── 5. Agent Pattern/                        # Layer B — single-agent loops
    ├── 01_Tool_Use/                         # Tool use, ReAct
    ├── 02_Planning/                         # Decompose → execute → replan; PEV
    ├── 03_Reflection/                       # Reflection, Reflexion, CoVe
    └── 11_Advanced_Cognitive_Patterns/      # Search / ToT / LATS / ensemble / …
        # (rename later if desired: Sampling_and_Search)

07_Advanced_Agentic_Systems/                 # Layer C — coordination + memory
├── Memory_and_State/
└── Multi_Agent_Orchestration/

08_Advanced_RAG/                             # Layer C — agentic retrieval
09_Agent_Protocols/                          # Layer C — MCP, A2A
12_Production_and_Observability/             # Layer C — safety, guardrails, HITL ops
03_LangGraph_Fundamentals/…/Human_in_the_Loop/   # HITL mechanics (LangGraph)
```

`Building_Agents_From_Scratch/` is a **from-scratch twin** of Layer B (same patterns, no LangGraph) — not a third taxonomy.

Notebook bases:

- Fareed: `https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/`
- Gulli: `https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/`

---

## Source notebooks by suggested folder

Each bullet is a notebook that would land in that folder if these two repos were merged. Links are the upstream GitHub files, not copies already in this repo.

### Phase 5 — `4. Workflow_Pattern/` (Layer A)

#### `4. Workflow_Pattern/1_Prompt_Chaining/`

| Source | Notebook                                                                                                                                                                       |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Gulli  | [Chapter_01_Prompt_Chaining_(Code_Example).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_01_Prompt_Chaining_(Code_Example).ipynb) |
| Gulli  | [Chapter_01_Prompt_Chaining_(JSON_Example).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_01_Prompt_Chaining_(JSON_Example).ipynb) |

Fareed has no first-class prompt-chaining notebook.

#### `4. Workflow_Pattern/2_Routing/`

| Source | Notebook                                                                                                                                                                                                                       |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Gulli  | [Chapter_02_Routing_(Google_ADK).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_02_Routing_(Google_ADK).ipynb)                                                                     |
| Gulli  | [Chapter_02_Routing_(LangGraph).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_02_Routing_(LangGraph).ipynb)                                                                       |
| Gulli  | [Chapter_02_Routing_(Openrouter).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_02_Routing_(Openrouter).ipynb)                                                                     |
| Fareed | [17_reflexive_metacognitive.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/17_reflexive_metacognitive.ipynb) (capability *routing* half; safety-gate half also listed under Phase 12) |

#### `4. Workflow_Pattern/3_parallelization/`

| Source | Notebook                                                                                                                                                                   |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gulli  | [Chapter_03_Parallelization_(Google_ADK).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_03_Parallelization_(Google_ADK).ipynb) |
| Gulli  | [Chapter_03_Parallelization_(LangChain).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_03_Parallelization_(LangChain).ipynb)   |

#### `4. Workflow_Pattern/4_orchestrator-worker/`

No Fareed or Gulli notebook is titled orchestrator–worker (Anthropic primitive). Keep the local `4-orchestrator-worker.ipynb`. Closest upstream: Fareed [04_planning.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/04_planning.ipynb) and [05_multi_agent.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/05_multi_agent.ipynb) — those stay in B2 / Phase 7, not here.

#### `4. Workflow_Pattern/5_Evaluator-optimizer/`

No Fareed or Gulli notebook is titled evaluator–optimizer. Keep the local `5-Evaluator-optimizer.ipynb`. Closest upstream: Fareed [01_reflection.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/01_reflection.ipynb) — that stays in `03_Reflection/`, not here.

---

### Phase 5 — `5. Agent Pattern/` (Layer B)

#### `5. Agent Pattern/01_Tool_Use/`

| Source | Notebook                                                                                                                                                                 |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Fareed | [02_tool_use.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/02_tool_use.ipynb)                                                    |
| Fareed | [03_react.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/03_react.ipynb)                                                          |
| Gulli  | [Chapter_05_Tool_Use_(LangChain).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_05_Tool_Use_(LangChain).ipynb)               |
| Gulli  | [Chapter_05_Tool_Use_(CrewAI).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_05_Tool_Use_(CrewAI).ipynb)                     |
| Gulli  | [Chapter_05_Tool_Use_(Google_Search).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_05_Tool_Use_(Google_Search).ipynb)       |
| Gulli  | [Chapter_05_Tool_Use_(Vertex_AI_Search).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_05_Tool_Use_(Vertex_AI_Search).ipynb) |
| Gulli  | [Chapter_05_Tool_Use_(Executing_Code).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_05_Tool_Use_(Executing_Code).ipynb)     |

##### `5. Agent Pattern/01_Tool_Use/` (environment / computer-use — applied, not a new primitive)

| Source | Notebook                                                                                                                                                                                                     |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Fareed | [33_swe_agent.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/33_swe_agent.ipynb)                                                                                      |
| Fareed | [34_computer_use.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/34_computer_use.ipynb) (BrowserAgent)                                                                 |
| Gulli  | [Appendix_B_AI_Agentic_From_GUI_to_Real_world_environment.ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_B_AI_Agentic_From_GUI_to_Real_world_environment.ipynb) |

`Appendix_G_Coding_agents.ipynb` is listed under Phase 11 (coding-tools phase), not here.

#### `5. Agent Pattern/02_Planning/`

| Source | Notebook                                                                                                                                                                   |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fareed | [04_planning.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/04_planning.ipynb)                                                      |
| Fareed | [06_pev.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/06_pev.ipynb)                                                                |
| Gulli  | [Chapter_06_Planning_(Code_Example).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_06_Planning_(Code_Example).ipynb)           |
| Gulli  | [Chapter_06_Planning_(Deep_Research_API).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_06_Planning_(Deep_Research_API).ipynb) |

#### `5. Agent Pattern/03_Reflection/`

| Source | Notebook                                                                                                                                                                                               |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Fareed | [01_reflection.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/01_reflection.ipynb)                                                                              |
| Fareed | [18_reflexion.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/18_reflexion.ipynb)                                                                                |
| Fareed | [20_chain_of_verification.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/20_chain_of_verification.ipynb)                                                        |
| Fareed | [19_self_discover.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/19_self_discover.ipynb)                                                                        |
| Fareed | [32_constitutional_ai.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/32_constitutional_ai.ipynb) (critique-loop teaching copy; production policy also Phase 12) |
| Gulli  | [Chapter_04_Reflection_(LangChain).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_04_Reflection_(LangChain).ipynb)                                         |
| Gulli  | [Chapter_04_Reflection_(ADK).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_04_Reflection_(ADK).ipynb)                                                     |
| Gulli  | [Chapter_04_Reflection_(Iterative_Loop).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_04_Reflection_(Iterative_Loop).ipynb)                               |
| Gulli  | [Chapter_17_Reasoning_(Self_Correction).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_17_Reasoning_(Self_Correction).ipynb)                               |

#### `5. Agent Pattern/11_Advanced_Cognitive_Patterns/` (sampling, search, specialty)

| Source | Notebook                                                                                                                                                                           |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fareed | [21_self_consistency.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/21_self_consistency.ipynb)                                              |
| Fareed | [09_tree_of_thoughts.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/09_tree_of_thoughts.ipynb)                                              |
| Fareed | [22_lats.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/22_lats.ipynb)                                                                      |
| Fareed | [10_mental_loop.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/10_mental_loop.ipynb)                                                        |
| Fareed | [13_ensemble.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/13_ensemble.ipynb)                                                              |
| Fareed | [15_rlhf_self_improvement.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/15_rlhf_self_improvement.ipynb)                                    |
| Fareed | [16_cellular_automata.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/16_cellular_automata.ipynb)                                            |
| Gulli  | [Chapter_17_Reasoning_(CoT_Prompt).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_17_Reasoning_(CoT_Prompt).ipynb)                     |
| Gulli  | [Chapter_17_Reasoning_(Executing_Code).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_17_Reasoning_(Executing_Code).ipynb)             |
| Gulli  | [Chapter_17_Reasoning_(Google_DeepSearch).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_17_Reasoning_(Google_DeepSearch).ipynb)       |
| Gulli  | [Appendix_F_Under_the_Hood_Reasoning_Engines.ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_F_Under_the_Hood_Reasoning_Engines.ipynb) |

---

### Phase 7 — `07_Advanced_Agentic_Systems/`

#### `Memory_and_State/`

| Source | Notebook                                                                                                                                                                                 |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fareed | [08_episodic_semantic_memory.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/08_episodic_semantic_memory.ipynb)                                    |
| Fareed | [12_graph_memory.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/12_graph_memory.ipynb)                                                            |
| Fareed | [31_memgpt.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/31_memgpt.ipynb)                                                                        |
| Fareed | [29_voyager.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/29_voyager.ipynb)                                                                      |
| Fareed | [35_agent_workflow_memory.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/35_agent_workflow_memory.ipynb)                                          |
| Gulli  | [Chapter_08_Memory_(LangChain_LangGraph).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_08_Memory_(LangChain_LangGraph).ipynb)               |
| Gulli  | [Chapter_08_Memory_(ADK_SessionService).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_08_Memory_(ADK_SessionService).ipynb)                 |
| Gulli  | [Chapter_08_Memory_(ADK_MemoryService_InMemory).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_08_Memory_(ADK_MemoryService_InMemory).ipynb) |
| Gulli  | [Chapter_08_Memory_(ADK_LlmAgent_output_key).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_08_Memory_(ADK_LlmAgent_output_key).ipynb)       |
| Gulli  | [Chapter_08_Memory_(ADK_Explicit_State_Update).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_08_Memory_(ADK_Explicit_State_Update).ipynb)   |
| Gulli  | [Chapter_09_Adaptation_(OpenEvolve).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_09_Adaptation_(OpenEvolve).ipynb)                         |

#### `Multi_Agent_Orchestration/`

| Source | Notebook                                                                                                                                                                                           |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fareed | [05_multi_agent.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/05_multi_agent.ipynb)                                                                        |
| Fareed | [07_blackboard.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/07_blackboard.ipynb)                                                                          |
| Fareed | [28_debate.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/28_debate.ipynb)                                                                                  |
| Fareed | [30_storm.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/30_storm.ipynb)                                                                                    |
| Fareed | [11_meta_controller.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/11_meta_controller.ipynb)                                                                |
| Gulli  | [Chapter_07_Multi_Agent_(ADK_Gemini_Coordinator).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_07_Multi_Agent_(ADK_Gemini_Coordinator).ipynb)         |
| Gulli  | [Chapter_07_Multi_Agent_(ADK_Gemini_AgentTool).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_07_Multi_Agent_(ADK_Gemini_AgentTool).ipynb)             |
| Gulli  | [Chapter_07_Multi_Agent_(ADK_Gemini_Loop).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_07_Multi_Agent_(ADK_Gemini_Loop).ipynb)                       |
| Gulli  | [Chapter_07_Multi_Agent_(ADK_Gemini_Parallel).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_07_Multi_Agent_(ADK_Gemini_Parallel).ipynb)               |
| Gulli  | [Chapter_07_Multi_Agent_(ADK_Gemini_Sequential).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_07_Multi_Agent_(ADK_Gemini_Sequential).ipynb)           |
| Gulli  | [Chapter_07_Multi_Agent_(CrewAI_Gemini).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_07_Multi_Agent_(CrewAI_Gemini).ipynb)                           |
| Gulli  | [Chapter_20_Prioritization_(SuperSimplePM).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_20_Prioritization_(SuperSimplePM).ipynb)                     |
| Gulli  | [Chapter_21_Exploration_Discovery_(Agent_Laboratory).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_21_Exploration_Discovery_(Agent_Laboratory).ipynb) |

#### `Evaluation_and_Eval_Harnesses/` (Gulli eval; Fareed has no dedicated eval architecture)

| Source | Notebook                                                                                                                                                                                       |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gulli  | [Chapter_19_Evaluation_(Basic_Response_Evaluation).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_19_Evaluation_(Basic_Response_Evaluation).ipynb) |
| Gulli  | [Chapter_19_Evaluation_(LLM_as_Judge).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_19_Evaluation_(LLM_as_Judge).ipynb)                           |
| Gulli  | [Chapter_11_Goal_Setting_(Iteration).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_11_Goal_Setting_(Iteration).ipynb)                             |

---

### Phase 8 — `08_Advanced_RAG/`

Naive / indexing RAG already in Phase 4; these notebooks are the **agentic** retrieval set.

| Source | Notebook                                                                                                                                                                                         |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Fareed | [23_agentic_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/23_agentic_rag.ipynb)                                                                      |
| Fareed | [24_corrective_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/24_corrective_rag.ipynb)                                                                |
| Fareed | [25_self_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/25_self_rag.ipynb)                                                                            |
| Fareed | [26_adaptive_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/26_adaptive_rag.ipynb)                                                                    |
| Fareed | [27_graph_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/27_graph_rag.ipynb)                                                                          |
| Gulli  | [Chapter_14_Knowledge_Retrieval_(RAG_LangChain).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_14_Knowledge_Retrieval_(RAG_LangChain).ipynb)         |
| Gulli  | [Chapter_14_Knowledge_Retrieval_(RAG_Google_Search).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_14_Knowledge_Retrieval_(RAG_Google_Search).ipynb) |
| Gulli  | [Chapter_14_Knowledge_Retrieval_(RAG_VertexAI).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_14_Knowledge_Retrieval_(RAG_VertexAI).ipynb)           |

---

### Phase 9 — `09_Agent_Protocols/`

#### `MCP/`

| Source | Notebook                                                                                                                                                                         |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gulli  | [Chapter_10_MCP_(ADK_FastMCP_Server).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_10_MCP_(ADK_FastMCP_Server).ipynb)               |
| Gulli  | [Chapter_10_MCP_(FastMCP_Client_Agent_init).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_10_MCP_(FastMCP_Client_Agent_init).ipynb) |
| Gulli  | [Chapter_10_MCP_(FastMCP_Server_Example).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_10_MCP_(FastMCP_Server_Example).ipynb)       |
| Gulli  | [Chapter_10_MCP_(Filesystem_Example_agent).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_10_MCP_(Filesystem_Example_agent).ipynb)   |
| Gulli  | [Chapter_10_MCP_(Filesystem_Example_init).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_10_MCP_(Filesystem_Example_init).ipynb)     |

#### `A2A/`

| Source | Notebook                                                                                                                                                                                       |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gulli  | [Chapter_15_Inter_Agent_(A2A).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_15_Inter_Agent_(A2A).ipynb)                                           |
| Gulli  | [Chapter_15_Inter_Agent_(A2A_AgentCard_WeatherBot).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_15_Inter_Agent_(A2A_AgentCard_WeatherBot).ipynb) |
| Gulli  | [Chapter_15_Inter_Agent_(Sync_Streaming_Requests).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_15_Inter_Agent_(Sync_Streaming_Requests).ipynb)   |

---

### Phase 3 HITL + Phase 12 production / safety

#### `03_LangGraph_Fundamentals/…/Human_in_the_Loop/` (mechanics)

| Source | Notebook                                                                                                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Gulli  | [Chapter_13_Human_in_the_Loop_(Customer_Support).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_13_Human_in_the_Loop_(Customer_Support).ipynb) |
| Fareed | [14_dry_run.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/14_dry_run.ipynb)                                                                        |

#### `12_Production_and_Observability/Safety_and_Alignment/`

| Source | Notebook                                                                                                                                                                                                     |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Gulli  | [Chapter_18_Guardrails_(ADK_Validate_Tool).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_18_Guardrails_(ADK_Validate_Tool).ipynb)                               |
| Gulli  | [Chapter_18_Guardrails_(LLM_as_Guardrail).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_18_Guardrails_(LLM_as_Guardrail).ipynb)                                 |
| Gulli  | [Chapter_18_Guardrails_(Practical_Examples).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_18_Guardrails_(Practical_Examples).ipynb)                             |
| Fareed | [32_constitutional_ai.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/32_constitutional_ai.ipynb) (policy / per-rule safety; teaching copy also in `03_Reflection/`) |
| Fareed | [17_reflexive_metacognitive.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/17_reflexive_metacognitive.ipynb) (safety-gate half)                                       |

#### `12_Production_and_Observability/` (exceptions, cost, resources)

| Source | Notebook                                                                                                                                                                                           |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gulli  | [Chapter_12_Exception_Handling_(Fallback).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_12_Exception_Handling_(Fallback).ipynb)                       |
| Gulli  | [Chapter_16_Resource_Optimization_(Code_Snippets).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_16_Resource_Optimization_(Code_Snippets).ipynb)       |
| Gulli  | [Chapter_16_Resource_Optimization_(OI_Google_Search).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Chapter_16_Resource_Optimization_(OI_Google_Search).ipynb) |

---

### Other phases (Gulli appendices only — Fareed has no matching notebooks)

#### Phase 2 — `02_LangChain_Fundamentals_and_Prompting/Prompt_and_Context_Engineering/`

| Source | Notebook                                                                                                                                                                     |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gulli  | [Appendix_A_Advanced_Prompting_Techniques.ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_A_Advanced_Prompting_Techniques.ipynb) |

#### Phase 6 — `06_Agent_SDKs_First_Party/`

| Source | Notebook                                                                                                                                                                             |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Gulli  | [Appendix_D_Building_an_Agent_with_AgentSpace.ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_D_Building_an_Agent_with_AgentSpace.ipynb) |

#### Phase 10 — `10_Alternative_Agent_Frameworks/`

| Source | Notebook                                                                                                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Gulli  | [Appendix_C_Quick_overview_of_Agentic_Frameworks.ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_C_Quick_overview_of_Agentic_Frameworks.ipynb) |
| Gulli  | [Appendix_C_(Code).ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_C_(Code).ipynb)                                                             |
| Gulli  | [Appendix_Pydantic.ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_Pydantic.ipynb)                                                             |

#### Phase 11 — `11_Claude_Code_and_AI_Coding_Tools/`

| Source | Notebook                                                                                                                                                   |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gulli  | [Appendix_E_AI_Agents_on_the_CLI.ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_E_AI_Agents_on_the_CLI.ipynb) |
| Gulli  | [Appendix_G_Coding_agents.ipynb](https://github.com/evoiz/Agentic-Design-Patterns/blob/main/chapter_notebooks/Appendix_G_Coding_agents.ipynb)               |

---

## Layer A — Workflow primitives (Phase 5)

Fixed or lightly dynamic graphs. No long “agent in a loop” yet. Gulli ch. 1–3 plus Anthropic’s five.

| # | Pattern              | What it controls                        | Gulli | Fareed family                             |
| - | -------------------- | --------------------------------------- | ----- | ----------------------------------------- |
| 1 | Prompt chaining      | Sequential decomposition                | Ch. 1 | (missing as first-class)                  |
| 2 | Routing              | Classify → one path                    | Ch. 2 | Safety & Routing (partial)                |
| 3 | Parallelization      | Independent fan-out / fan-in            | Ch. 3 | Sampling & Search (related, not the same) |
| 4 | Orchestrator–worker | Runtime-dynamic subtask split           | —    | Tools & Actions / Planning (adjacent)     |
| 5 | Evaluator–optimizer | Generate ↔ evaluate loop (fixed graph) | —    | Reasoning & Reflection (adjacent)         |

Home: `05_AI_Agent_Fundamentals/4. Workflow_Pattern/`.

---

## Layer B — Single-agent loops (Phase 5)

The model stays in a loop. Named papers live here as **patterns**, not as a second “agents” phase.

### B1. Tools and actions

| Pattern            | Idea                                 | Gulli      | Fareed                  |
| ------------------ | ------------------------------------ | ---------- | ----------------------- |
| Tool use           | One or more tools, no ReAct required | Ch. 5      | Tool Use                |
| ReAct              | Thought → Action → Observation     | Ch. 5      | ReAct                   |
| Environment agents | SWE-Agent, BrowserAgent              | App. B / G | SWE-Agent, BrowserAgent |

Home: `5. Agent Pattern/01_Tool_Use/`. SWE/Browser are **applied builds** (Phase 5 LangGraph apps or Phase 13), not extra primitive folders.

### B2. Planning

| Pattern                     | Idea                             | Gulli | Fareed   |
| --------------------------- | -------------------------------- | ----- | -------- |
| Planning                    | Decompose → execute → replan   | Ch. 6 | Planning |
| Plan–Execute–Verify (PEV) | Verify each step after execution | —    | PEV      |

Home: `5. Agent Pattern/02_Planning/` and `11_Advanced_Cognitive_Patterns/01_PEV.ipynb`.

### B3. Reasoning and reflection

| Pattern                      | Idea                                  | Gulli               | Fareed            |
| ---------------------------- | ------------------------------------- | ------------------- | ----------------- |
| Reflection                   | Generate → critique → refine        | Ch. 4               | Reflection        |
| Reflexion                    | Verbal reflections in episodic memory | Ch. 4               | Reflexion         |
| Chain-of-Verification (CoVe) | Verify claims independently           | Ch. 17-ish          | CoVe              |
| Self-Discover                | SELECT → ADAPT → IMPLEMENT → SOLVE | —                  | Self-Discover     |
| Constitutional AI            | Per-rule pass/fail → revise          | Ch. 18 (guardrails) | Constitutional AI |

Home: `5. Agent Pattern/03_Reflection/`. Constitutional AI is **taught** here as a critique loop; production safety policy still belongs in Phase 12.

### B4. Sampling and search

| Pattern          | Idea                      | Fareed           |
| ---------------- | ------------------------- | ---------------- |
| Self-Consistency | Sample N paths, vote      | Self-Consistency |
| Tree of Thoughts | Beam / tree over thoughts | Tree of Thoughts |
| LATS             | MCTS + rewards            | LATS             |
| Ensemble         | N voters, aggregate       | Ensemble         |
| Mental Loop      | Simulate → score         | Mental Loop      |

Home: `5. Agent Pattern/11_Advanced_Cognitive_Patterns/` (ToT, ensemble, mental loop). Gulli does not treat these as a separate part.

---

## Layer C — Other phase owners (do not peer them with A/B)

Same keywords as Fareed/Gulli, different **prerequisites**. Putting them in Phase 5 would recreate the old “duplicate RAG / memory / agents everywhere” problem.

### Memory — Phase 7 `Memory_and_State/`

| Pattern                 | Fareed                | Gulli            |
| ----------------------- | --------------------- | ---------------- |
| Episodic + semantic     | Episodic + Semantic   | Ch. 8            |
| Graph memory            | Graph Memory          | Ch. 8            |
| MemGPT / OS-style tiers | MemGPT                | Ch. 8            |
| Voyager skill library   | Voyager               | Ch. 9 (learning) |
| Agent workflow memory   | Agent Workflow Memory | Ch. 8–9         |

Notebooks that currently sit under `11_Advanced_Cognitive_Patterns/03_Episodic_With_Semantic_Memory.ipynb` are **pattern demos**; the phase that *owns* memory systems is still Phase 7.

### Multi-agent — Phase 7 `Multi_Agent_Orchestration/`

| Pattern                                     | Fareed          | Gulli |
| ------------------------------------------- | --------------- | ----- |
| Supervisor + specialists                    | Multi-Agent     | Ch. 7 |
| Swarm / peer-to-peer                        | —              | Ch. 7 |
| Blackboard                                  | Blackboard      | Ch. 7 |
| Debate                                      | Debate          | Ch. 7 |
| STORM                                       | STORM           | Ch. 7 |
| Meta-controller (router over architectures) | Meta-Controller | —    |

Keep one overview notebook in Phase 5 if needed; builds and orchestration live in Phase 7.

### Agentic retrieval — Phase 8 `08_Advanced_RAG/`

Foundational RAG (no agents required) stays in Phase 4.

| Pattern               | Fareed       | Gulli  |
| --------------------- | ------------ | ------ |
| Agentic RAG           | Agentic RAG  | Ch. 14 |
| Corrective RAG (CRAG) | CRAG         | Ch. 14 |
| Self-RAG              | Self-RAG     | Ch. 14 |
| Adaptive RAG          | Adaptive RAG | Ch. 14 |
| GraphRAG              | GraphRAG     | Ch. 14 |

### Protocols — Phase 9 `09_Agent_Protocols/`

| Pattern                 | Gulli  | Notes                        |
| ----------------------- | ------ | ---------------------------- |
| MCP                     | Ch. 10 | Not an agent loop            |
| A2A / inter-agent comms | Ch. 15 | Not a Phase 5 pattern folder |

### Safety, HITL, eval — Phases 3, 7, 12

| Pattern                                  | Fareed                      | Gulli      | Home                                                                              |
| ---------------------------------------- | --------------------------- | ---------- | --------------------------------------------------------------------------------- |
| Human-in-the-loop                        | —                          | Ch. 13     | Phase 3 HITL mechanics                                                            |
| Dry-run / approval gate                  | Dry-Run                     | Ch. 12–13 | Phase 12 + HITL                                                                   |
| Reflexive metacognitive routing          | Reflexive Metacognitive     | —         | Routing (A) vs safety (12); don’t fuse                                           |
| Guardrails                               | Constitutional AI (overlap) | Ch. 18     | Phase 12`Safety_and_Alignment/`                                                 |
| Exception handling / recovery            | —                          | Ch. 12     | Phase 12                                                                          |
| Evaluation and monitoring                | —                          | Ch. 19     | Phase 7 eval + Phase 12 observability                                             |
| Goal setting / monitoring                | —                          | Ch. 11     | Phase 7 / production                                                              |
| Resource-aware optimization              | —                          | Ch. 16     | Phase 12                                                                          |
| Prioritization                           | —                          | Ch. 20     | Phase 7 orchestration / Phase 12 — still in scope                                |
| Exploration and discovery                | —                          | Ch. 21     | Phase 7 / later cognitive notebooks — still in scope                             |
| RLHF self-improvement, cellular automata | Specialty                   | —         | Layer B4 notebooks (`11_Advanced_Cognitive_Patterns/`), not a junk-drawer track |

---

## Fareed families → this map

| Fareed family                        | This roadmap                                             |
| ------------------------------------ | -------------------------------------------------------- |
| Reasoning & Reflection               | Layer B3 (Phase 5)                                       |
| Sampling & Search                    | Layer B4 (Phase 5)                                       |
| Tools & Actions                      | Split: B1 tools/ReAct, B2 planning, apps for SWE/Browser |
| Retrieval (RAG)                      | Phase 8 (foundational RAG already Phase 4)               |
| Memory                               | Phase 7                                                  |
| Multi-Agent                          | Phase 7                                                  |
| Safety & Routing                     | Split: routing = Layer A; safety gates = Phase 12        |
| Specialty                            | Optional notebooks under B4, not a junk-drawer track     |
| Cross-cutting (deterministic-picker) | Implementation discipline inside notebooks, not a folder |

---

## Gulli parts → this map

| Gulli part          | This roadmap                                                            |
| ------------------- | ----------------------------------------------------------------------- |
| Part 1 ch. 1–3     | Layer A                                                                 |
| Part 1 ch. 4–6     | Layer B                                                                 |
| Part 1 ch. 7        | Phase 7 multi-agent                                                     |
| Part 2 ch. 8–9, 11 | Phase 7 memory / goals                                                  |
| Part 2 ch. 10       | Phase 9 MCP                                                             |
| Part 3 ch. 12–13   | Phase 12 + Phase 3 HITL                                                 |
| Part 3 ch. 14       | Phase 8 (after Phase 5)                                                 |
| Part 4 ch. 15       | Phase 9 A2A                                                             |
| Part 4 ch. 16–21   | Phase 12 / eval / later                                                 |
| Appendices          | Frameworks → Phase 10; coding agents → Phase 11; prompting → Phase 2 |

Gulli is the **reading order**. It is not the folder tree.

---

## Coverage checklist (nothing dropped)

### Fareed — all 35 architectures

One notebook each. Same links as the folder sections above.

| # | Architecture | Layer / home | Notebook |
|---|--------------|--------------|----------|
| 1 | Reflection | B3 `03_Reflection/` | [01_reflection.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/01_reflection.ipynb) |
| 2 | Reflexion | B3 `03_Reflection/` | [18_reflexion.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/18_reflexion.ipynb) |
| 3 | Chain-of-Verification | B3 | [20_chain_of_verification.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/20_chain_of_verification.ipynb) |
| 4 | Self-Discover | B3 | [19_self_discover.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/19_self_discover.ipynb) |
| 5 | Constitutional AI | B3 + Phase 12 | [32_constitutional_ai.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/32_constitutional_ai.ipynb) |
| 6 | Self-Consistency | B4 | [21_self_consistency.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/21_self_consistency.ipynb) |
| 7 | Tree of Thoughts | B4 | [09_tree_of_thoughts.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/09_tree_of_thoughts.ipynb) |
| 8 | LATS | B4 | [22_lats.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/22_lats.ipynb) |
| 9 | Mental Loop | B4 | [10_mental_loop.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/10_mental_loop.ipynb) |
| 10 | Ensemble | B4 | [13_ensemble.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/13_ensemble.ipynb) |
| 11 | Agentic RAG | Phase 8 | [23_agentic_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/23_agentic_rag.ipynb) |
| 12 | Corrective RAG | Phase 8 | [24_corrective_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/24_corrective_rag.ipynb) |
| 13 | Self-RAG | Phase 8 | [25_self_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/25_self_rag.ipynb) |
| 14 | Adaptive RAG | Phase 8 | [26_adaptive_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/26_adaptive_rag.ipynb) |
| 15 | GraphRAG | Phase 8 | [27_graph_rag.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/27_graph_rag.ipynb) |
| 16 | Episodic + Semantic | Phase 7 memory | [08_episodic_semantic_memory.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/08_episodic_semantic_memory.ipynb) |
| 17 | Graph Memory | Phase 7 memory | [12_graph_memory.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/12_graph_memory.ipynb) |
| 18 | MemGPT | Phase 7 memory | [31_memgpt.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/31_memgpt.ipynb) |
| 19 | Voyager | Phase 7 memory | [29_voyager.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/29_voyager.ipynb) |
| 20 | Agent Workflow Memory | Phase 7 memory | [35_agent_workflow_memory.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/35_agent_workflow_memory.ipynb) |
| 21 | Tool Use | B1 | [02_tool_use.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/02_tool_use.ipynb) |
| 22 | ReAct | B1 | [03_react.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/03_react.ipynb) |
| 23 | Planning | B2 | [04_planning.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/04_planning.ipynb) |
| 24 | PEV | B2 | [06_pev.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/06_pev.ipynb) |
| 25 | SWE-Agent | B1 applied | [33_swe_agent.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/33_swe_agent.ipynb) |
| 26 | BrowserAgent | B1 applied | [34_computer_use.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/34_computer_use.ipynb) |
| 27 | Multi-Agent (supervisor) | Phase 7 | [05_multi_agent.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/05_multi_agent.ipynb) |
| 28 | Blackboard | Phase 7 | [07_blackboard.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/07_blackboard.ipynb) |
| 29 | Debate | Phase 7 | [28_debate.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/28_debate.ipynb) |
| 30 | STORM | Phase 7 | [30_storm.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/30_storm.ipynb) |
| 31 | Meta-Controller | Phase 7 | [11_meta_controller.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/11_meta_controller.ipynb) |
| 32 | Dry-Run | Phase 12 + HITL | [14_dry_run.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/14_dry_run.ipynb) |
| 33 | Reflexive Metacognitive | A routing + Phase 12 | [17_reflexive_metacognitive.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/17_reflexive_metacognitive.ipynb) |
| 34 | RLHF Self-Improvement | B4 | [15_rlhf_self_improvement.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/15_rlhf_self_improvement.ipynb) |
| 35 | Cellular Automata | B4 | [16_cellular_automata.ipynb](https://github.com/FareedKhan-dev/all-agentic-architectures/blob/main/notebooks/16_cellular_automata.ipynb) |

Cross-cutting (not a 36th architecture): **deterministic-picker** stays an implementation rule inside notebooks, not a folder.

### Gulli — all 21 chapters + appendices

| Item                                   | Home                                   |
| -------------------------------------- | -------------------------------------- |
| Ch. 1 Prompt chaining                  | Layer A                                |
| Ch. 2 Routing                          | Layer A                                |
| Ch. 3 Parallelization                  | Layer A                                |
| Ch. 4 Reflection                       | Layer B3                               |
| Ch. 5 Tool use                         | Layer B1                               |
| Ch. 6 Planning                         | Layer B2                               |
| Ch. 7 Multi-agent                      | Phase 7                                |
| Ch. 8 Memory                           | Phase 7                                |
| Ch. 9 Learning and adaptation          | Phase 7 (Voyager / skill memory)       |
| Ch. 10 MCP                             | Phase 9                                |
| Ch. 11 Goal setting and monitoring     | Phase 7 / 12                           |
| Ch. 12 Exception handling and recovery | Phase 12                               |
| Ch. 13 Human-in-the-loop               | Phase 3 HITL + Phase 12                |
| Ch. 14 Knowledge retrieval (RAG)       | Phase 4 foundational + Phase 8 agentic |
| Ch. 15 A2A                             | Phase 9                                |
| Ch. 16 Resource-aware optimization     | Phase 12                               |
| Ch. 17 Reasoning techniques            | Layer B3 / B4 (ToT, CoVe, search)      |
| Ch. 18 Guardrails / safety             | Phase 12 (+ Constitutional AI in B3)   |
| Ch. 19 Evaluation and monitoring       | Phase 7 eval + Phase 12                |
| Ch. 20 Prioritization                  | Phase 7 / 12                           |
| Ch. 21 Exploration and discovery       | Phase 7 / B4                           |
| App. A Advanced prompting              | Phase 2                                |
| App. B GUI → real-world               | B1 environment agents                  |
| App. C Agentic frameworks              | Phase 10                               |
| App. D AgentSpace                      | Phase 6 first-party SDKs / Google      |
| App. E CLI agents                      | Phase 11                               |
| App. F Reasoning engines               | Phase 1 theory / B4                    |
| App. G Coding agents                   | Phase 11                               |

Orchestrator–worker and evaluator–optimizer are **not** Fareed first-class names and **not** Gulli chapter titles; they come from Anthropic and stay in Layer A. That is additive, not a replacement.

---

## Learning order (inside this repo)

1. Layer A workflows (`4. Workflow_Pattern/`)
2. Tool use → ReAct → Planning → Reflection (`5. Agent Pattern/` + from-scratch twin)
3. Sampling / search (ToT, LATS, …) when the loop is solid
4. Memory and multi-agent (Phase 7)
5. Agentic RAG (Phase 8)
6. MCP / A2A (Phase 9)
7. Safety, cost, eval in production (Phase 12)

That matches Fareed’s beginner path (Reflection → Tool Use → ReAct → Planning → Self-Consistency) **after** the five workflows, and keeps RAG/multi-agent/safety as later paths instead of Phase 5 siblings.

---

## What not to do

- Do not create `Agentic-Design-Patterns/` or `all-agentic-architectures/` as a new phase or a second home for RAG/memory/MCP.
- Do not merge Layer A into `01_Tool_Use/` (Fareed’s mistake: chaining/routing disappear).
- Do not merge routing and safety into one folder (Fareed’s “Safety & Routing”).
- Do not treat Gulli chapters 8–21 as “more agent patterns” in Phase 5.
