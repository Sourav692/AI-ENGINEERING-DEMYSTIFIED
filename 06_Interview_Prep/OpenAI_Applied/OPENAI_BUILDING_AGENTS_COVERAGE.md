# OpenAI "Building Agents" Track — Repo Coverage

Maps every topic in OpenAI's [Building Agents track](https://developers.openai.com/tracks/building-agents)
to where this repo teaches it, and names what is genuinely missing.

**Checked against disk 2026-09-19; rows re-verified and the tally recounted 2026-09-20.**
Every path below was verified to exist. **All paths are relative to the repository root**,
not to this file — this document moved into `06_Interview_Prep/OpenAI_Applied/` on
2026-09-20 and the paths were deliberately left absolute-from-root so they stay copy-pasteable.

**The headline, as of 2026-09-20: every row is resolved.** The repo taught the *concepts*
well from the start — agent loops, tool calling, routing, handoffs, memory, guardrails,
structured output and RAG, all through LangChain/LangGraph. What was thin was OpenAI's own
surface. Four notebooks closed the part of that surface which carried a concept the repo
lacked — hosted vs client-side execution, hosted code execution, vision-driven computer use,
and agentic image generation — and four rows were descoped because they were a vendor
spelling of something already taught more deeply. The rule that separated the two is at the
bottom of this document.


|                                                          | Count |
| -------------------------------------------------------- | ----- |
| ✅ Covered                                                | 22    |
| 🟡 Partial — concept taught, OpenAI's implementation not | 0     |
| ⏭️ Descoped — deliberately not building                  | 4     |
| ❌ Gap                                                    | 0     |


*(26 rows. The count previously read 18 — it had been carried forward without recounting as
rows flipped; corrected 2026-09-20 by counting the badges.)*

---



## 1. Core Concepts


| Track topic                                                       | Repo coverage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Status      |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Reasoning vs. non-reasoning model choice; reasoning-effort levers | **Closed 2026-09-19.** `01_Foundations/00_Theory_and_Foundations/Reasoning_and_Model_Selection/` — `01_Reasoning_vs_NonReasoning.ipynb` (measured on identical tasks, including one where reasoning loses) and `02_Reasoning_Effort_Levers.ipynb` (effort swept, knee located, plus the case where effort is the wrong lever). Applied at `02_Core/05_AI_Agent_Fundamentals/4. Workflow_Pattern/2. Routing/notebooks/Routing_By_Model_Tier.ipynb`. `get_llm()` gained a `reasoning_effort` passthrough to make it reachable                                                                                                                                                                                                                                                                                 | ✅ Covered   |
| **Responses API** (OpenAI's stateful core API)                    | ⏭️ **Descoped 2026-09-20 — not being built.** The prep is concept-led, not OpenAI-API-led, so the vendor's own request layer is not worth notebook time. Kept in the table for completeness. *Re-checked 2026-09-20: it is used once*, in `02_Core/05_AI_Agent_Fundamentals/3. AI_Agents_with_LangGraph/10_Hotel_Reservations_Multi_Agent_System/Module_2_Core_Agents/1_Environment_Setup.ipynb` — a `client.responses.create(model=..., instructions=..., input=...)` smoke test reading `response.output_text`. It appears, it is not taught: no statefulness, no conversation chaining, no contrast with chat-completions, and the cell depends on `google.colab.userdata` so it will not run locally. `ChatOpenAI` also exposes `use_responses_api`, so the stack can reach it without new dependencies | ⏭️ Descoped |
| **Agents SDK** (OpenAI's own)                                     | ⏭️ **Descoped 2026-09-20 — not building the remaining folders.** `01_Foundations/01_Agents_Handoffs_Guardrails.ipynb` (23 cells) already covers Agent, tools, handoffs and input guardrails **and carries the LangGraph comparison table**, which was the only thing this partial was really worth. Its concepts are all taught generically elsewhere — the agent loop in Phase 3, handoffs in `Multi_Agent_Orchestration/`, guardrails in `Safety_and_Alignment/`. `02_Core_Capabilities/`, `03_Multi_Agent_Patterns/` and `04_Applications/` would add SDK surface, not concepts.                                                                                                                                                                                                                         | ⏭️ Descoped |
| Augmenting agents with tools                                      | `02_Core/03_LangGraph_Fundamentals/01_Foundations/` (`05_Augmented_LLM_with_Tools.ipynb`), `02_Core/05_AI_Agent_Fundamentals/2. LangChain_Tools_and_Agents/01_Tools_and_Functions/`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | ✅ Covered   |




## 2. Tools


| Track topic                                                         | Repo coverage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Status    |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| Function calling mechanics                                          | `02_Core/05_AI_Agent_Fundamentals/2. LangChain_Tools_and_Agents/01_Tools_and_Functions/`, plus `5. Agent Pattern/01_Tool_Use/02_Tool_Calling_vs_ReAct.ipynb`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | ✅ Covered |
| Function calling **vs. hosted built-ins** — the architectural split | **Closed 2026-09-20.** `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/07_Hosted_vs_Client_Side_Tools.ipynb` runs the same capability both ways — `chat.completions` with your own function, then `responses.create` with a hosted `web_search` — and compares them on who executes, what you can see, what you can intercept, how they fail, and cost. Includes a guard cell that refuses a tool call, which is only possible client-side                                                                                                                                                                                                                                                                 | ✅ Covered |
| Web search                                                          | **Both halves now.** Client-side: Tavily across **38 notebooks**, e.g. `02_Core/05_AI_Agent_Fundamentals/3. AI_Agents_with_LangGraph/01_Research_Assistant_Chatbot.ipynb`. Hosted: `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/07_Hosted_vs_Client_Side_Tools.ipynb` calls `responses.create(tools=[{"type": "web_search"}])` and contrasts the two. *(Was marked partial for "client-side provider only"; that stopped being true when 07 was built on 2026-09-20 and the row was not updated with it.)*                                                                                                                                                                                              | ✅ Covered |
| File search (managed RAG)                                           | `02_Core/04_Retrieval_and_RAG/` and `03_Advanced/08_Advanced_RAG/` — chunking, embeddings, vector stores, retrieval, reranking. Far deeper than the track. What is absent is the *managed* vector store where you hand OpenAI the files                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | ✅ Covered |
| Code interpreter                                                    | **Closed 2026-09-20.** `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/09_Hosted_Code_Execution.ipynb` calls the hosted tool (`{"type": "code_interpreter", "container": {"type": "auto"}}`) on a statistics task the model gets wrong unaided, reads back **the source it executed**, and configures the container's `memory_limit` and `network_policy`. Code *generation* remains in `05_SWE_Agent_Applied.ipynb` and `3. AI_Agents_with_LangGraph/05_Reflective_Code_Generation_Agent/`                                                                                                                                                                                                                | ✅ Covered |
| Computer use                                                        | **Closed 2026-09-20.** `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/08_Vision_Driven_Computer_Use.ipynb` runs a real vision loop: the agent receives an actual PNG and returns `click(x, y)` from pixels alone — no element names, no accessibility tree. Pairs with `06_BrowserAgent_Computer_Use_Applied.ipynb`, which teaches the same loop with text observations                                                                                                                                                                                                                                                                                                                                   | ✅ Covered |
| Image generation as a mid-conversation tool call                    | **Closed 2026-09-20.** `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/10_Agentic_Image_Generation.ipynb` — the agent decides to generate, writes its own prompt (readable as `revised_prompt`), and is also tested for **restraint** with the tool attached. Its core finding, reproduced on two independent runs: the agent narrates its artefact confidently while the label reads `NINTH STRFET` / `BET WI MORSIT ANED`, because the narration is written from the prompt, not the pixels. The notebook closes that with a vision-input audit turn and a refinement turn where `action` flips to `edit` on its own. Phase 1's `02_Diffusers/` keeps the *models*; this is the agentic loop around them | ✅ Covered |
| MCP                                                                 | `03_Advanced/09_Agent_Protocols/MCP/` — foundations, building servers, building clients, applications, plus `04_Applications/mcp_a2a_agentic_rag/`. Deeper than the track                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | ✅ Covered |




## 3. Orchestration


| Track topic                                                        | Repo coverage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Status      |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Agent loop management                                              | `02_Core/03_LangGraph_Fundamentals/` (whole phase)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | ✅ Covered   |
| Handoffs                                                           | `03_Advanced/07_Advanced_Agentic_Systems/Multi_Agent_Orchestration/Production_Course_Multi_Agent/03_agent_handoffs.ipynb`, plus the OpenAI-SDK version in the foundations notebook above                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | ✅ Covered   |
| Guardrails                                                         | `03_Advanced/12_Production_and_Observability/Safety_and_Alignment/01_Moderating_Chains.ipynb`, `Production_Course_Ops/03_security_patterns.ipynb`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | ✅ Covered   |
| Sessions / automatic history                                       | ⏭️ **Descoped 2026-09-20 — deliberately not building this.** OpenAI's `Session` is a *subset* of what the repo already teaches, so implementing it would teach less, not more. `Memory_and_State/` (23 notebooks) plus LangGraph checkpointing cover `thread_id` isolation (20 files), the `add_messages` reducer (21), `SqliteSaver` (7), summarisation (14), `get_state_history` time travel (3) and `update_state` (4) — none of which `Session` offers. Its one distinct idea, `conversation_id` server-side state, is the hosted-vs-client-side axis applied to memory, already taught in `01_Tool_Use/07_Hosted_vs_Client_Side_Tools.ipynb` and `09_Hosted_Code_Execution.ipynb`; the trade-offs transfer unchanged. | ⏭️ Descoped |
| Tracing                                                            | ⏭️ **Descoped 2026-09-20.** A different vendor's UI for a concept already taught: `LLMOps_and_AI_Infrastructure/Tracing_and_Observability/LangSmith/01_LangSmith_Basics.ipynb` plus the hand-rolled `InstrumentedLLM` wrapper in `Production_Course_Ops/01_monitoring.ipynb`, which builds spans, metrics and logging from scratch. Spans, latency and token accounting do not change with the dashboard rendering them.                                                                                                                                                                                                                                                                                                   | ⏭️ Descoped |
| Multi-agent collaboration: routing, agent-as-tool, parallelization | `03_Advanced/07_Advanced_Agentic_Systems/Multi_Agent_Orchestration/` (supervisor, swarm), `02_Core/03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/`, CrewAI + AutoGen in `03_Advanced/10_Alternative_Agent_Frameworks/`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | ✅ Covered   |




## 4. Example Use Cases


| Track topic                                                    | Repo coverage                                                                                                                                                                                                                                                                                                                                                                                         | Status    |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| Support agent with human-in-the-loop                           | `02_Core/03_LangGraph_Fundamentals/02_Core_Capabilities/03_Human_in_the_Loop/`                                                                                                                                                                                                                                                                                                                        | ✅ Covered |
| Customer-service agent network                                 | `03_Advanced/08_Advanced_RAG/Agentic_RAG/1. Build_a_Healthcare_Customer_Support_Router_Agentic_RAG_System.ipynb`, `05_Projects/AI_Powered_Customer_Support/`                                                                                                                                                                                                                                          | ✅ Covered |
| Frontend testing agent (computer use)                          | **Closed 2026-09-20.** Section 4 of `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/08_Vision_Driven_Computer_Use.ipynb` points the agent at a build with a deliberately broken coupon button and asserts on the end state. It also separates the two failure causes from the click log — control hit but state unchanged means the UI is broken; control never hit means the agent is | ✅ Covered |
| Optimizing for speed / reliability / cost as an upfront choice | `03_Advanced/12_Production_and_Observability/LLMOps_and_AI_Infrastructure/` and `06_Interview_Prep/Study_Guides/Cost_Latency_Optimization/` (playbook, cram sheets, drill decks) cover this well — as operations, and the Study_Guides material does frame it as design levers                                                                                                                        | ✅ Covered |




## 5. Best Practices


| Track topic                            | Repo coverage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Status    |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| Input guardrails, jailbreak prevention | `03_Advanced/12_Production_and_Observability/Safety_and_Alignment/`, `Production_Course_Ops/03_security_patterns.ipynb`                                                                                                                                                                                                                                                                                                                                                                                                            | ✅ Covered |
| Structured outputs                     | `02_Core/01_LangChain_Fundamentals/07_LangChain_1x_Agents_and_Middleware/7.4_Structured_Output.ipynb`, `02_Core/03_LangGraph_Fundamentals/01_Foundations/08_Pydantic_State_Validation.ipynb`                                                                                                                                                                                                                                                                                                                                       | ✅ Covered |
| Output guardrails                      | **Re-checked 2026-09-20: covered, and better than this row claimed.** `03_Advanced/12_Production_and_Observability/Safety_and_Alignment/03_Guardrails_LLM_and_Rule_Based.ipynb` implements `rule_based_output_guardrail()` and `llm_output_guardrail()`, wires a full input-guardrail → agent → output-guardrail pipeline, and walks a response blocked for leaking the system prompt. *(Was marked partial as "covered as moderation; a separate output-validation stage is thinner" — that description predated this notebook.)* | ✅ Covered |
| Production monitoring                  | `03_Advanced/12_Production_and_Observability/` (whole phase)                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | ✅ Covered |


---



## No gaps left

All four originally identified gaps are closed or deliberately descoped:


| Gap                                  | Outcome                                                                                               |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Reasoning-model selection            | **Built** 2026-09-19 — `Reasoning_and_Model_Selection/` (2 notebooks) + `Routing_By_Model_Tier.ipynb` |
| Hosted vs client-side tools          | **Built** 2026-09-20 — `01_Tool_Use/07_Hosted_vs_Client_Side_Tools.ipynb`                             |
| Real computer use / frontend testing | **Built** 2026-09-20 — `01_Tool_Use/08_Vision_Driven_Computer_Use.ipynb`                              |
| Responses API                        | **Descoped** 2026-09-20 — concept-led prep; conversation state is covered by LangGraph checkpointing  |
| Image generation as a tool call      | **Built** 2026-09-20 — `01_Tool_Use/10_Agentic_Image_Generation.ipynb`                                |


**Nothing is partial any more.** Every row is either built or deliberately descoped with a
recorded reason. The four descopes share one shape — a vendor surface over a concept the
repo teaches more deeply — so if the target ever becomes OpenAI-API-specific rather than
concept-led, those four rows flip back and the reasons are already written down per row.

## When a partial is worth closing

Three partials were closed by building (web search, code interpreter, computer use) and two
were descoped. The test that separated them:

> **Close it when the vendor's version teaches a concept you lack. Descope it when it is a
> different spelling of one you have.**

- **Web search, code interpreter, computer use** — passed. Hosted execution is a genuinely
different control, failure and cost model, and code interpreter went further by showing
that hosted visibility varies per tool.
- **Responses API** — descoped. Concept-led prep; conversation state is covered by LangGraph
checkpointing. It remains in use as a *vehicle* for the hosted-tool notebooks.
- **Sessions** — descoped, and for a stronger reason: `Session` is a strict subset of the
repo's memory coverage, so building it would teach a simpler API for a problem already
understood more deeply. The risk is not wasted effort but a worse mental model — a notebook
implying `Session` and LangGraph checkpointing are peers.

Applying the rule to the rest (2026-09-20) descoped two more:

- **Agents SDK** — the foundations notebook already carries the LangGraph comparison table,
which was the real value. The rest is SDK surface over concepts taught generically in
Phases 3, 5 and 7.
- **Tracing** — a different vendor's dashboard for observability the repo already builds from
scratch. Spans and token accounting do not change with the UI rendering them.

**Image generation was the last partial, and it passed the rule — built 2026-09-20.** It
earned its place by adding a third axis rather than a fourth hosted tool. `07_` split tools
by *who executes*; `09_` split hosted tools by *what you can see*; `10_` splits them by
**what you can verify**:


|                    | `web_search` | `code_interpreter`     | `image_generation`                          |
| ------------------ | ------------ | ---------------------- | ------------------------------------------- |
| Oracle available   | the source   | re-run the computation | **none**                                    |
| Checking is        | cheap, exact | cheap, exact           | costly, approximate                         |
| Failure looks like | a wrong fact | a wrong number         | a *confident description of something else* |


That last cell is the concept the repo did not have. Phase 1 teaches diffusion models, and
`09_` teaches a tool whose output you can assert on. Neither teaches a tool that manufactures
something unverifiable and then tells you it went well — which is why the notebook's verification
turn (feed the PNG back to a vision model, ask for a *transcription* rather than a judgement)
is the actual lesson, not the generation call.

## Related

`[OPENAI_BUILDING_AGENTS_TUTORIAL.md](OPENAI_BUILDING_AGENTS_TUTORIAL.md)` (beside this file) is the teaching companion — the
same track walked through in plain language, 3–4 lines per concept, with the notebook path
for each and Mermaid diagrams for the loop, the hosted/client-side split, the multi-agent
shapes and the guardrail pipeline. **This document is the audit; that one is the lesson.**
Keep them in step: if a row here changes status, the matching section there changes too.

`[OpenAI_Applied_AI_Engineer_Coverage_Gap_Analysis.md](OpenAI_Applied_AI_Engineer_Coverage_Gap_Analysis.md)` (also beside this file) analyses
this same track alongside OpenAI's Evaluation Best Practices guide, scoped to interview prep.
Its section 1 now points here rather than restating the mapping — it had drifted, claiming the
Agents SDK track was empty and that computer use had no coverage, both of which were out of date.



## What actually moves the needle for this specific round

This is a decomposition/discussion interview, not a build check — so the fix isn't "go build 5 more notebooks," it's:

- **Vocabulary mapping** (cheap, ~15-30 min): skim the Agents SDK and Responses API docs and mentally re-tag what you already know — supervisor pattern → `Handoff`, moderation chain → `Guardrail`, LangGraph checkpointing → `Session`. The architectural judgment already transfers; only the OpenAI-specific nouns are missing.
- **Rehearse the decomposition format out loud**, not silently: `06_Interview_Prep/FDE/Cracking_Agentic_AI_System_Design_Interviews/ch28_system_design_interview.md` already has the 45-minute script, two worked designs, and a levelling rubric for exactly this interview shape — that's higher-leverage prep time than closing any single content gap above.
- If there's time left, skim the OpenAI eval guide's **edge-case list** (multilingual, circular handoffs, ambiguous tool responses) once more right before the interview — it's the one area where the guide's framing genuinely differs from how this repo teaches evaluation.

