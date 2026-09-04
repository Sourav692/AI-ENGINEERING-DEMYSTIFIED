# Appendix A · Glossary

Every term links to the document that explains it. Terms are grouped by the module where they are first taught in depth; many recur later.

## Foundations (Modules 00–02)

| Term | Meaning | Where |
|---|---|---|
| **The first ten minutes** | The five question areas — customer, data reality, access and blast radius, scale and SLAs, definition of done — to ask before drawing anything; the signal is visibly adapting to the answers | [00·3](../00_Orientation/03_The_First_Ten_Minutes.md) |
| **Three lenses** | Technical build, customer-facing, guiding the team — a senior FDE's three interdependent responsibilities | [00·2](../00_Orientation/02_The_Three_Roles.md), [10·1](../10_FDE_Delivery_Operating_Model/01_A_Day_In_The_Life.md) |
| **RAG** | Retrieval-augmented generation: find relevant documents, then generate an answer using only them | [01·1](../01_LLM_Systems_Foundations/01_What_RAG_Actually_Is.md) |
| **Ingestion / query paths** | The offline pipeline that indexes permission-tagged chunks, and the per-request pipeline that answers | [01·1](../01_LLM_Systems_Foundations/01_What_RAG_Actually_Is.md) |
| **Chunk** | A passage-sized piece of a document; the unit of retrieval and therefore of access control | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **Dense retrieval** | Vector search on embeddings — finds what *means* the same; weak on exact identifiers | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **BM25 / lexical retrieval** | Keyword scoring — finds what *says* the same; strong on identifiers, blind to paraphrase | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **Hybrid search** | Dense + lexical together | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **RRF** | Reciprocal Rank Fusion — merging ranked lists by rank, not score; agreement across retrievers wins | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **Multi-Query / RAG-Fusion** | Rewrite the question N ways, search each, fuse | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **HyDE** | Search with an invented hypothetical answer as the probe, anchored by the original question | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **Decomposition** | Splitting a multi-hop question into sub-questions | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **Reranking** | A cross-encoder or LLM judging query and passage *together* over ~20 candidates; the biggest single quality win | [01·2](../01_LLM_Systems_Foundations/02_Chunking_Retrieval_Fusion.md) |
| **Agent / ReAct loop** | A brain picks a tool or finishes; the loop executes and feeds the result back, under a step budget | [01·3](../01_LLM_Systems_Foundations/03_What_An_Agent_Actually_Is.md) |
| **Tool, registry, `destructive` flag** | A named, described, callable action; the lookup; the declared property that triggers the confirmation gate | [01·3](../01_LLM_Systems_Foundations/03_What_An_Agent_Actually_Is.md) |
| **Brain / `Decision` / `Observation`** | The `(query, observations) → Decision` contract; a tool call or a final answer; one past result | [01·3](../01_LLM_Systems_Foundations/03_What_An_Agent_Actually_Is.md) |
| **Max-iteration guard** | The loop bound that makes an agent a terminating process | [01·4](../01_LLM_Systems_Foundations/04_Tool_Calling_Loop_From_Scratch.md) |
| **Session** | Cross-turn state: history, memo, trace | [01·4](../01_LLM_Systems_Foundations/04_Tool_Calling_Loop_From_Scratch.md) |
| **`add_messages` reducer** | LangGraph's append-not-replace for the message list | [01·5](../01_LLM_Systems_Foundations/05_Same_Loop_In_LangGraph.md) |
| **12-part framework** | Problem → requirements → capacity → architecture → data → components → flow → scale → reliability → security → trade-offs | [02·1](../02_System_Design_Fundamentals/01_The_12_Part_Framework.md) |
| **Circuit breaker** | Closed → open → half-open; fails fast to prevent a cascade | [02·1](../02_System_Design_Fundamentals/01_The_12_Part_Framework.md) |
| **Reliability vs availability** | Correct and lossless vs responding at all; containment vs redundancy | [02·1](../02_System_Design_Fundamentals/01_The_12_Part_Framework.md) |
| **Short-circuiting** | Stopping a pipeline the moment a step already satisfies the task | [02·1](../02_System_Design_Fundamentals/01_The_12_Part_Framework.md) |
| **Active-active vs active-passive** | All regions live vs a standby; the cost is on the data layer | [02·1](../02_System_Design_Fundamentals/01_The_12_Part_Framework.md) |
| **SCALED** | Simplicity, Cohesion/coupling, Availability, Latency, Extensibility, Durability — plus five cross-cutting lenses | [02·2](../02_System_Design_Fundamentals/02_The_15_Principles.md) |
| **Modular monolith** | Clean module boundaries without network boundaries — the right starting shape | [02·3](../02_System_Design_Fundamentals/03_Monolith_vs_Microservices.md) |
| **Synthesiser agent** | The named component where parallel agent outputs converge and conflicts are resolved | [02·4](../02_System_Design_Fundamentals/04_Worked_Example_Travel_Agent.md) |
| **The 60-minute method** | Clarify → entities → architecture → deep dive → cross-cutting → close; with the forward-deployed close | [02·5](../02_System_Design_Fundamentals/05_The_60_Minute_Whiteboard_Method.md) |

## Building production systems (Modules 03–05)

| Term | Meaning | Where |
|---|---|---|
| **Confirmation gate / `ConfirmPolicy`** | Destructive tools run only if a policy says yes; default deny | [03·1](../03_Robust_Agents/01_Retry_Fallback_Memo_Confirm.md) |
| **Memoization** | Caching identical `(tool, args)` results within a session; never routes around the gate | [03·1](../03_Robust_Agents/01_Retry_Fallback_Memo_Confirm.md) |
| **Transient vs permanent failure** | Retry the first, bounded; never retry the second — fall back or escalate | [03·1](../03_Robust_Agents/01_Retry_Fallback_Memo_Confirm.md) |
| **Fallback** | A declared alternative tool, run through the same gate and validation | [03·1](../03_Robust_Agents/01_Retry_Fallback_Memo_Confirm.md) |
| **Checkpointer** | Persists graph state after every node — crash recovery and human-in-the-loop pauses | [03·2](../03_Robust_Agents/02_State_Memory_Sessions.md) |
| **Three layers of memory** | Short-term session, long-term user, enterprise knowledge (which is retrieval, not memory) | [03·2](../03_Robust_Agents/02_State_Memory_Sessions.md) |
| **Per-call telemetry** | One record per tool call: tool, args, status, latency, result | [03·4](../03_Robust_Agents/04_Observability_For_Tool_Calls.md) |
| **The eight guard checks** | Argument validation, destructive gate, step guard, spend guard, retry+fallback, memoization, disambiguation, telemetry | [03·5](../03_Robust_Agents/05_The_Eight_Guard_Checks.md) |
| **Disambiguation** | Deterministic choice between overlapping tools; never a destructive tool on a tie | [03·5](../03_Robust_Agents/05_The_Eight_Guard_Checks.md) |
| **Post-filter / partition / pre-filter** | The three access-control patterns; pre-filter is the default, partition by tenant, post-check is authoritative | [04·1](../04_Enterprise_RAG/01_Why_Enterprise_Changes_The_Problem.md) |
| **Existence oracle** | Leaking that restricted documents exist through result counts or timing | [04·1](../04_Enterprise_RAG/01_Why_Enterprise_Changes_The_Problem.md) |
| **ABAC** | Attribute-based access control: principal attributes vs resource attributes through ordered rules | [04·2](../04_Enterprise_RAG/02_Access_Control_ABAC.md) |
| **Physical vs logical; Layer 1 vs Layer 2** | Where the tenant wall sits (collection vs filter) vs when a check runs (pre- vs post-retrieval) | [04·2](../04_Enterprise_RAG/02_Access_Control_ABAC.md) |
| **Deny overrides / default deny** | Any deny wins; only one rule can grant; no grant is a denial | [04·2](../04_Enterprise_RAG/02_Access_Control_ABAC.md) |
| **Clearance, groups, compartments** | A ladder, a grant, and orthogonal need-to-know | [04·2](../04_Enterprise_RAG/02_Access_Control_ABAC.md) |
| **Obligation** | A condition attached to an allow — redact PII, audit the access | [04·2](../04_Enterprise_RAG/02_Access_Control_ABAC.md) |
| **Filter disagreement / security event** | Layer 2 denying what Layer 1 should have caught — a stale index or a broken filter | [04·2](../04_Enterprise_RAG/02_Access_Control_ABAC.md) |
| **Visibility matrix** | Documents × personas, every cell decided by a named rule | [04·2](../04_Enterprise_RAG/02_Access_Control_ABAC.md) |
| **ACL catalog** | The authoritative permission store, separate from the index's cached copy | [04·3](../04_Enterprise_RAG/03_Ingestion_Pipeline.md) |
| **Refuse, don't default** | An unmappable document is quarantined, never indexed as "internal" | [04·3](../04_Enterprise_RAG/03_Ingestion_Pipeline.md) |
| **Incremental sync / content hash** | Skip re-embedding unchanged text; ACL changes never need it | [04·3](../04_Enterprise_RAG/03_Ingestion_Pipeline.md) |
| **Enterprise strategy** | Multi-query + HyDE + sub-questions through dense; original + sub-questions through BM25; fused; reranked | [04·4](../04_Enterprise_RAG/04_Retrieval_Hybrid_Rerank.md) |
| **The eight-node graph** | authorize → plan → retrieve → enforce → grade → generate / refuse → verify | [04·5](../04_Enterprise_RAG/05_The_Query_Graph.md) |
| **Fail closed on authorisation** | Policy engine down → refuse; degrade on everything else | [04·5](../04_Enterprise_RAG/05_The_Query_Graph.md) |
| **Sufficient / partial / insufficient** | The three-verdict grade; partial answers what it can | [04·6](../04_Enterprise_RAG/06_Output_Guardrails.md) |
| **Citation as disclosure** | Naming a document confirms it exists; a citation alone can leak | [04·6](../04_Enterprise_RAG/06_Output_Guardrails.md) |
| **Refusal hygiene** | Never hint that withheld material exists | [04·6](../04_Enterprise_RAG/06_Output_Guardrails.md) |
| **Golden set** | Fixed cases with expected, forbidden and distractor documents | [04·7](../04_Enterprise_RAG/07_Evaluation_Golden_Sets_Judges.md) |
| **Leak gate** | Forbidden documents reaching context or citation must be exactly zero; blocks the release | [04·7](../04_Enterprise_RAG/07_Evaluation_Golden_Sets_Judges.md) |
| **Distractor** | Allowed but irrelevant — a precision miss, never gating | [04·7](../04_Enterprise_RAG/07_Evaluation_Golden_Sets_Judges.md) |
| **Judge calibration** | Checking an LLM judge against human labels before trusting it | [04·7](../04_Enterprise_RAG/07_Evaluation_Golden_Sets_Judges.md) |
| **`RunTrace`** | One replayable record per request; three audiences, one artefact | [04·8](../04_Enterprise_RAG/08_Observability.md) |
| **Coverage map** | ✅ built · 🟡 partial · ❌ not built, with to-close and what-to-say | [04·10](../04_Enterprise_RAG/10_Coverage_Map.md), [11·2](../11_Telling_The_Story/02_Proof_vs_Cheat_Sheet_Honesty.md) |
| **Canonical event / channel adapter** | One shape downstream; translate once at the edge | [05·2](../05_Agentic_Workflow_Platforms/02_Canonical_Events_And_Channels.md) |
| **Priority vs entity lock** | A design-time choice of which workflow wins vs a run-time guarantee that two never run on one target | [05·2](../05_Agentic_Workflow_Platforms/02_Canonical_Events_And_Channels.md) |
| **`WorkflowSpec`** | The declarative step list the orchestrator walks; the reviewable artefact a non-technical user confirms | [05·3](../05_Agentic_Workflow_Platforms/03_Determinism_Over_Free_Text.md) |
| **Determinism over free text** | The model chooses argument values; it never improvises control flow | [05·3](../05_Agentic_Workflow_Platforms/03_Determinism_Over_Free_Text.md) |
| **Checkpoint = `next_step_index`** | One loop for run and resume; no separate recovery path | [05·4](../05_Agentic_Workflow_Platforms/04_Durability_And_Idempotency.md) |
| **Idempotency key on the action** | `{run_id}:{step_name}` — a retried loop is fine, a retried side effect is a no-op; cost is a side effect too | [05·4](../05_Agentic_Workflow_Platforms/04_Durability_And_Idempotency.md) |
| **Step budget vs spend cap** | How many steps vs how many dollars — two quantities | [05·5](../05_Agentic_Workflow_Platforms/05_Approvals_Spend_Caps_Staged_Rollout.md) |
| **Staged rollout** | DRAFT → TESTING → SHADOW → LIVE → AUTONOMOUS, each answering one question; author cannot promote | [05·5](../05_Agentic_Workflow_Platforms/05_Approvals_Spend_Caps_Staged_Rollout.md) |
| **Shadow mode** | Watches real traffic, decides, never acts | [05·5](../05_Agentic_Workflow_Platforms/05_Approvals_Spend_Caps_Staged_Rollout.md) |
| **Autonomous ≠ unlimited** | Autonomy raises the ceiling on which actions skip approval; the cap remains | [05·5](../05_Agentic_Workflow_Platforms/05_Approvals_Spend_Caps_Staged_Rollout.md) |
| **Negative-control demo** | A demo of things being stopped — stronger than a demo of things working | [05·5](../05_Agentic_Workflow_Platforms/05_Approvals_Spend_Caps_Staged_Rollout.md) |

## Scale, security, operations (Modules 06–08)

| Term | Meaning | Where |
|---|---|---|
| **SSO/OIDC as verification** | Validate the token, map the customer's groups, provision just-in-time | [06·1](../06_Cross_Cutting_Concerns/01_Identity_Secrets_Tenant_Fairness.md) |
| **Envelope encryption** | A secret encrypted with its own key, wrapped by a master key | [06·1](../06_Cross_Cutting_Concerns/01_Identity_Secrets_Tenant_Fairness.md) |
| **Per-tenant keys** | Blast radius of a key compromise is one tenant | [06·1](../06_Cross_Cutting_Concerns/01_Identity_Secrets_Tenant_Fairness.md) |
| **Fair queue** | Order under load — orthogonal to a rate limit's ceiling | [06·1](../06_Cross_Cutting_Concerns/01_Identity_Secrets_Tenant_Fairness.md) |
| **OpenTelemetry-style spans** | Standard trace format with domain fields as attributes | [06·2](../06_Cross_Cutting_Concerns/02_Observability_Standards_Failure_Patterns.md) |
| **Bulkhead** | Isolating a slow dependency's resources so it hurts only itself | [06·2](../06_Cross_Cutting_Concerns/02_Observability_Standards_Failure_Patterns.md) |
| **Kill switch** | A fast, blunt override that halts in-flight work — the opposite instinct from staged rollout | [06·2](../06_Cross_Cutting_Concerns/02_Observability_Standards_Failure_Patterns.md) |
| **Semantic cache** | Similarity-threshold caching; a false hit is a wrong answer; never across permission scopes | [06·3](../06_Cross_Cutting_Concerns/03_Caching_Streaming_CICD_BuildVsBuy.md) |
| **Streaming after the refusal decision** | Perceived-latency fix, applied only after "can I answer at all" is settled | [06·3](../06_Cross_Cutting_Concerns/03_Caching_Streaming_CICD_BuildVsBuy.md) |
| **Nightly regression run** | A second trigger for the eval suite — catches provider drift | [06·3](../06_Cross_Cutting_Concerns/03_Caching_Streaming_CICD_BuildVsBuy.md) |
| **Build vs buy** | Buy undifferentiated layers; build what encodes this customer's business | [06·3](../06_Cross_Cutting_Concerns/03_Caching_Streaming_CICD_BuildVsBuy.md) |
| **Data is not instructions** | Separate channels for content and system instructions; the schema as firewall | [06·4](../06_Cross_Cutting_Concerns/04_Prompt_Injection_Egress_Tenancy.md) |
| **Egress allow-list** | Per tenant per tool, where a call may send data | [06·4](../06_Cross_Cutting_Concerns/04_Prompt_Injection_Egress_Tenancy.md) |
| **Three tenancy levels** | Shared + tag; schema per tenant; dedicated deployment; enforce in the data layer | [06·4](../06_Cross_Cutting_Concerns/04_Prompt_Injection_Egress_Tenancy.md) |
| **Intent router** | Structured vs semantic vs hybrid, in front of retrieval | [06·5](../06_Cross_Cutting_Concerns/05_Structured_Data_Routers_Connectors.md) |
| **Connector registry** | Config-driven sources, independent schedules, change tokens, health, backfill vs incremental | [06·5](../06_Cross_Cutting_Concerns/05_Structured_Data_Routers_Connectors.md) |
| **Filtered ANN** | Metadata filters inside the approximate search, not after it | [06·6](../06_Cross_Cutting_Concerns/06_Scaling_To_20M_Documents.md) |
| **ACL free at scale** | The post-check is O(candidates), not O(corpus) | [06·6](../06_Cross_Cutting_Concerns/06_Scaling_To_20M_Documents.md) |
| **Parent-child chunking** | Retrieve on the small child, generate on the parent | [06·6](../06_Cross_Cutting_Concerns/06_Scaling_To_20M_Documents.md) |
| **Blue/green index** | Build beside the old, cut over when backfilled | [06·6](../06_Cross_Cutting_Concerns/06_Scaling_To_20M_Documents.md) |
| **Single-agent multi-step vs multi-agent** | One sequence with shared tools vs independently scoped agents with a coordinator and defined handoffs | [07·1](../07_Multi_Agent_Systems/01_When_Multi_Agent_Is_Justified.md) |
| **The two triggers** | Conflicting contexts; unmanageable tool count | [07·1](../07_Multi_Agent_Systems/01_When_Multi_Agent_Is_Justified.md) |
| **Handoff package** | Case, asked, attempted, why insufficient, gathered, permission scope — carried, not re-derived | [07·2](../07_Multi_Agent_Systems/02_Reference_Architecture_Handoffs.md) |
| **Supervisor vs deep agent** | Central routing with specialists vs an orchestrator over self-contained sub-agents | [07·2](../07_Multi_Agent_Systems/02_Reference_Architecture_Handoffs.md), [07·5](../07_Multi_Agent_Systems/05_Case_Study_Supervisor_To_Deep_Agent.md) |
| **Hop cap** | A bounded number of handoffs per case with a forced outcome | [07·3](../07_Multi_Agent_Systems/03_Failure_Isolation_And_Evaluation.md) |
| **Model gateway** | One sidecar routing functions to providers with fallback | [07·4](../07_Multi_Agent_Systems/04_Case_Study_Research_Platform.md) |
| **Alias (Model Registry)** | `@champion`, `@prod` — code references the alias; promotion repoints it | [08·2](../08_AgentOps_And_Platform/02_AgentOps_On_Databricks.md) |
| **MemAlign** | Calibrating a judge against SME labels | [08·2](../08_AgentOps_And_Platform/02_AgentOps_On_Databricks.md) |
| **The two Vector Search facts** | It does not enforce UC row filters; it will not build on a governed table | [08·3](../08_AgentOps_And_Platform/03_Enterprise_RAG_On_Databricks.md) |
| **On-behalf-of-user (OBO)** | The governed re-read runs as the actual user so UC enforces | [08·3](../08_AgentOps_And_Platform/03_Enterprise_RAG_On_Databricks.md) |
| **`no_leak` scorer** | The deterministic gate — set arithmetic, never a judge | [08·3](../08_AgentOps_And_Platform/03_Enterprise_RAG_On_Databricks.md) |
| **Thin channel adapter** | Changes only latency budget and formatting; never the security layer | [08·4](../08_AgentOps_And_Platform/04_Multi_Channel_And_HITL_Escalation.md) |
| **Escalation as a workflow** | Create a record, attach context, route by cause, inherit scope, feed evaluation | [08·4](../08_AgentOps_And_Platform/04_Multi_Channel_And_HITL_Escalation.md) |
| **XPIA / Crescendo / Skeleton Key** | Cross-prompt injection; gradual escalation; a permissive "mode" | [08·5](../08_AgentOps_And_Platform/05_Red_Teaming.md) |
| **DABs** | Databricks Asset Bundles — infrastructure and policy SQL as code | [08·6](../08_AgentOps_And_Platform/06_Infra_And_CICD.md) |

## Design mastery and the FDE role (Modules 09–11)

| Term | Meaning | Where |
|---|---|---|
| **REST → function calling → MCP → agent framework** | Layers: what executes; the model deciding to invoke; discovery without hardcoded schemas; coordination | [09·1](../09_AI_System_Design_Casebook/01_Enterprise_AI_Assistant.md) |
| **Tool registry (at scale)** | Loads only the MCP servers relevant to the task | [09·1](../09_AI_System_Design_Casebook/01_Enterprise_AI_Assistant.md) |
| **Context engineering funnel** | Repository → signals → ranked context → prompt | [09·3](../09_AI_System_Design_Casebook/03_Coding_Assistant.md) |
| **Explainable weighted ranking** | Multiple named signals with explicit weights, not one opaque score | [09·4](../09_AI_System_Design_Casebook/04_Recruiting_Platform.md) |
| **Policy Gate** | The always-human rule checked first; independently testable | [09·5](../09_AI_System_Design_Casebook/05_Logistics_Exception_Handling.md) |
| **Shared control plane, regional data plane** | Identical logic everywhere; data never crosses a residency boundary | [09·5](../09_AI_System_Design_Casebook/05_Logistics_Exception_Handling.md) |
| **Six-stage delivery story** | Problem → data → approach → architecture → deployment → impact | [10·2](../10_FDE_Delivery_Operating_Model/02_End_To_End_AI_Delivery_Six_Stages.md) |
| **Accelerator library / reuse rate** | Pull, don't invent; the numeric answer to "productised or bespoke?" | [10·3](../10_FDE_Delivery_Operating_Model/03_Scoping_To_Production_In_Two_Weeks.md) |
| **Intake refusal** | No measurable metric, no SME, no sources → no engagement, no clock | [10·3](../10_FDE_Delivery_Operating_Model/03_Scoping_To_Production_In_Two_Weeks.md) |
| **The six gates** | security review · data access · golden set · eval baseline · rollback tested · success metrics — each with its signing role | [10·4](../10_FDE_Delivery_Operating_Model/04_Gates_Risks_Metrics.md) |
| **Evidence bar** | A gate can be structurally real and still a rubber stamp if evidence is free text | [10·4](../10_FDE_Delivery_Operating_Model/04_Gates_Risks_Metrics.md) |
| **RACI** | Responsible, Accountable, Consulted, Informed — exactly one A per workstream | [10·5](../10_FDE_Delivery_Operating_Model/05_Cross_Team_Collaboration.md) |
| **Data contract** | An interface agreement that turns an ownership argument into a phased delivery | [10·5](../10_FDE_Delivery_Operating_Model/05_Cross_Team_Collaboration.md) |
| **Two-pass Action** | Analogy pass, then technical pass only on a "go deeper" signal | [11·1](../11_Telling_The_Story/01_Deep_Dive_And_Conversational_Formats.md) |
| **Story beat / bridge** | A 30–60 s self-contained unit; the sentence that moves between business and technical framing | [11·1](../11_Telling_The_Story/01_Deep_Dive_And_Conversational_Formats.md) |
| **Offered vs extracted honesty** | State the limitation before it is asked | [11·2](../11_Telling_The_Story/02_Proof_vs_Cheat_Sheet_Honesty.md) |
