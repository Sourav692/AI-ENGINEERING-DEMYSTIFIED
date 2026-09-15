# AIA Group — Multi-Agent Architecture, End-to-End (Mermaid)

### Governed Multi-Agent Data Assistant on Databricks · companion to AIA_Technical_Implementation_Flow.md

> Six views of the same system. Section 1 is split into four small panels — panel **1a** is the one to draw on a whiteboard; the rest are the layers an interviewer will ask you to zoom into.

---

## 1. End-to-end request flow (Stage 2 — the Supervisor pattern that shipped)

> Four small panels instead of one crowded canvas. Draw **1a** on the whiteboard — it is the whole system in ten boxes. The other three are the zoom-ins an interviewer will ask for, in the order they usually ask.

### 1a · The whole system in ten boxes

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 55, 'rankSpacing': 90}, 'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    U(["Business user<br/>actuary · claims manager · analyst"]) --> APP["Databricks App<br/>Dash chat UI"]
    APP --> GW["AI Gateway<br/>rate limiting · PII filtering · guardrails"]
    GW --> SUP{"Supervisor<br/>what kind of<br/>question is this?"}

    SUP -->|"simple KPI"| W1["Genie Agent<br/>BI specialist"]
    SUP -->|"find a document"| W2["Multi-Tool Agent<br/>SQL + RAG generalist"]
    SUP -->|"deep analysis"| W3["Data Analysis Agent<br/>deterministic stats"]
    SUP -->|"make a chart"| W4["Visualization Agent<br/>dashboard creator"]

    W1 --> ANS["Cited, traceable answer"]
    W2 --> ANS
    W3 --> ANS
    W4 --> ANS
    ANS --> APP

    classDef spec fill:#e8f4e8,stroke:#2e7d32,color:#000
    class W1,W2,W3,W4 spec
```

**Talk track:** a question enters through the App and the AI Gateway, the Supervisor decides *what kind* of question it is, exactly one specialist does the work, and the answer comes back cited. One sentence, and the interviewer has the shape of the system.

### 1b · Inside the Supervisor

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 50, 'rankSpacing': 65}, 'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    Q["Question arrives<br/>from the AI Gateway"] --> C{"1 · classify_intent<br/>+ confidence score"}
    C -->|"confidence < 60%"| ASK["2 · clarify_or_disambiguate<br/>ask the user instead of guessing"]
    ASK -.->|"user replies"| Q
    C -->|"confidence >= 60%"| R["3 · resolve_assets_with_context_index<br/>Vector Search over 16 governed assets<br/>endorsed assets ranked first"]
    R --> RT["4 · route_to_*<br/>resolved asset list attached to shared state"]
    RT --> SPEC(["one specialist runs"])
    SPEC --> CA["5 · compose_answer<br/>cited, traceable"]
```

**Talk track:** two design decisions live here and both get lost in a bigger picture. First, the system **asks when it is unsure** rather than guessing confidently — that is the 60% gate. Second, asset resolution happens **once, centrally**, so every specialist works from the same governed asset list instead of each rediscovering it.

Intents in full: `simple_kpi` · `deep_analysis` · `document_lookup` · `visualization` · `conversational`.

### 1c · What each specialist actually reads

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 50, 'rankSpacing': 80}, 'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    W1["Genie Agent"] --> GS["Genie Spaces<br/>managed text-to-SQL"]
    W3["Data Analysis Agent"] --> MV["7 governed Metric Views<br/>claims · policy performance<br/>agent productivity · fraud"]
    GS --> MV
    W2["Multi-Tool Agent"] --> RAG["Vector Search RAG<br/>policy docs · claims files<br/>underwriting notes"]
    W2 --> SQL["LLM-generated SQL<br/>ad-hoc, narrower governance"]
    W4["Visualization Agent"] --> LV["Lakeview REST API<br/>publishes a real dashboard, returns a link"]
    MV --> GOLD[("Unity Catalog<br/>gold / silver")]
    SQL --> GOLD

    classDef gov fill:#e8f4e8,stroke:#2e7d32,color:#000
    class GS,MV,GOLD gov
```

**Talk track:** green is the governed path — a KPI question lands on a versioned metric view, so the agent and a human analyst computing "claims by region" get the same number. `W2 → SQL` is the one edge that leaves that lane, and naming it before the interviewer finds it is the strong move: ad-hoc SQL is the escape hatch for questions no governed asset covers, and it is deliberately the narrowest-trust path in the system.

> Section 3 below shows how this data gets *built* (bronze → silver → gold). This panel only shows who reads what.

### 1d · The cross-cutting layer

Four things wrap every request. They have no flow of their own, so they read better as a list than as dotted lines crossing the diagram:

| Layer | What it is | Why it is there |
| --- | --- | --- |
| **Context Index** | 16 governed assets in Vector Search — Genie Spaces, metric views, tables, document indexes | Queried **once per question, only by the Supervisor** (node 3 above) |
| **Short-term memory** | `ai_ops.conversations` — Delta checkpoints keyed by `thread_id`, 30-day retention | Checkpoint at each key node; resume a conversation, replay a failure |
| **Prompt store** | `ai_ops.agent_instructions` — base + overlay, 5-minute cache | Tune prompts with no redeploy |
| **MLflow Tracing** | `@mlflow.trace` on every node | One span per node and per tool call |
| **Agent Evaluation** | Held-out eval set, LLM-as-judge | Offline accuracy gate before release |

<details>
<summary><strong>The original single-canvas version</strong> — everything above on one diagram, kept for reference</summary>

```mermaid
flowchart TD
    U["Business user<br/>actuary · claims manager · analyst"] --> APP["Databricks App<br/>Dash chat UI"]
    APP --> GW["AI Gateway<br/>rate limiting · PII filtering · guardrails"]
    GW --> EP["Model Serving endpoint<br/>Databricks Agent Framework"]

    subgraph SUP["Supervisor — LangGraph StateGraph, 8 nodes"]
        direction TB
        N1["1. classify_intent<br/>simple_kpi · deep_analysis · document_lookup<br/>visualization · conversational<br/>+ confidence score"]
        N2["2. clarify_or_disambiguate<br/>fires only if confidence < 60%"]
        N3["3. resolve_assets_with_context_index<br/>Vector Search over 16 governed assets<br/>endorsed assets ranked first"]
        N4["4. route_to_*<br/>resolved asset list attached to shared state"]
        N5["5. compose_answer<br/>cited, traceable final answer"]
        N1 -->|"confidence >= 60%"| N3
        N1 -->|"confidence < 60%"| N2
        N2 -->|"clarifying question back to user"| APP
        N3 --> N4
    end

    EP --> N1

    N4 -->|"simple_kpi"| W1["Genie Agent<br/>BI specialist"]
    N4 -->|"document_lookup / ad-hoc"| W2["Multi-Tool Agent<br/>SQL + RAG generalist"]
    N4 -->|"deep_analysis"| W3["Data Analysis Agent<br/>z-score anomaly · trend stats<br/>deterministic, no LLM maths"]
    N4 -->|"visualization"| W4["Visualization Agent<br/>dashboard creator"]

    W1 --> GS["Genie Spaces<br/>managed text-to-SQL"]
    W2 --> SQL["LLM-generated SQL<br/>ad-hoc, narrower governance"]
    W2 --> RAG["Vector Search RAG<br/>policy docs · claims files · underwriting notes"]
    W3 --> MV["7 governed Metric Views<br/>claims · policy performance<br/>agent productivity · fraud"]
    W4 --> LV["Lakeview REST API<br/>publishes real AI/BI dashboard, returns link"]

    GS --> MV
    SQL --> GOLD["Unity Catalog gold / silver tables"]
    MV --> GOLD

    W1 --> N5
    W2 --> N5
    W3 --> N5
    W4 --> N5
    N5 --> APP

    CI[("Context Index<br/>16 assets in Vector Search<br/>Genie Spaces · metric views<br/>tables · document indexes")] -.->|"queried once per question,<br/>only by the Supervisor"| N3
    STM[("Short-term memory<br/>ai_ops.conversations<br/>Delta checkpoints by thread_id · 30-day")] <-.->|"checkpoint at each key node"| SUP
    PR[("Prompt store<br/>ai_ops.agent_instructions<br/>base + overlay · 5-min cache")] -.->|"no redeploy to tune"| SUP
    TR["MLflow Tracing<br/>@mlflow.trace on every node"] -.->|"span per node & tool call"| SUP
    EV["MLflow Agent Evaluation<br/>held-out eval set · LLM-as-judge"] -.->|"offline accuracy gate"| SUP

    classDef gov fill:#e8f4e8,stroke:#2e7d32,color:#000
    classDef mem fill:#fff4e0,stroke:#ef6c00,color:#000
    classDef obs fill:#e8eefc,stroke:#1a56db,color:#000
    class MV,GOLD,GS,CI gov
    class STM,PR mem
    class TR,EV obs
```

</details>

---

## 2. One question, step by step (sequence view)

```mermaid
sequenceDiagram
    autonumber
    actor User as Claims manager
    participant App as Databricks App
    participant GW as AI Gateway
    participant Sup as Supervisor (LangGraph)
    participant CI as Context Index (Vector Search)
    participant Mem as Delta checkpoints
    participant Genie as Genie Agent
    participant GS as Genie Space
    participant MV as Metric Views (UC)
    participant Tr as MLflow Tracing

    User->>App: "Claims loss ratio trend for Hong Kong this quarter?"
    App->>GW: request
    GW->>GW: rate limit · PII filter · guardrails
    GW->>Sup: forward
    Sup->>Mem: load thread_id state
    Sup->>Sup: classify_intent → simple_kpi (confidence 0.87)
    Note over Sup: >= 60% → skip clarification
    Sup->>CI: semantic search: "claims loss ratio, Hong Kong, quarterly"
    CI-->>Sup: [claims_analytics Genie Space (endorsed), claims metric view (endorsed)]
    Sup->>Mem: checkpoint (resolved assets in shared state)
    Sup->>Genie: route_to_genie + resolved assets
    Genie->>GS: natural-language question scoped to resolved assets
    GS->>MV: governed SQL against claims metric view
    MV-->>GS: rows
    GS-->>Genie: result + generated SQL
    Genie-->>Sup: structured output (data, SQL, source)
    Sup->>Sup: compose_answer (cited)
    Sup->>Mem: checkpoint
    Sup-->>App: answer + SQL + source lineage
    App-->>User: answer, minutes not days
    Sup-)Tr: spans for every node and tool call
```

**Low-confidence branch (not shown above):** "show me the numbers" → `classify_intent` confidence 0.35 → `clarify_or_disambiguate` → *"Which numbers — claims, policies, agents, or customers?"* → user answers → re-enters at `classify_intent`.

---

## 3. The governed data foundation underneath the agents

```mermaid
flowchart LR
    subgraph BR["Bronze — raw domains"]
        B1["products"]
        B2["agents"]
        B3["customers"]
        B4["policies"]
        B5["claims"]
        B6["policy documents"]
    end

    subgraph SV["Silver — enrichment joins"]
        S1["enriched_claims"]
        S2["enriched_policies"]
        S3["customer_360"]
    end

    subgraph GD["Gold — 7 governed Metric Views"]
        G1["claims KPIs"]
        G2["policy performance"]
        G3["agent productivity"]
        G4["fraud analysis"]
    end

    subgraph AI["ai_ops schema"]
        A1["conversations<br/>short-term checkpoints"]
        A2["agent_instructions<br/>prompts, base + overlay"]
        A3["long-term memory<br/>Stage 3 only"]
    end

    B5 --> S1
    B4 --> S2
    B3 --> S3
    B2 --> S3
    B1 --> S2
    S1 --> G1
    S1 --> G4
    S2 --> G2
    S3 --> G2
    S1 --> G3
    S2 --> G3

    B6 --> VS["Vector Search index<br/>policy-doc RAG"]
    GD --> GEN["4 Genie Spaces<br/>customer · distribution<br/>policy & underwriting · claims"]

    GD --> CTX[("Context Index<br/>16 assets")]
    GEN --> CTX
    VS --> CTX
    SV --> CTX

    CTX -->|"resolved once per question"| SUP["Supervisor"]
    GEN --> W1["Genie Agent"]
    GD --> W3["Data Analysis Agent"]
    VS --> W2["Multi-Tool Agent"]
    SV --> W2

    classDef uc fill:#e8f4e8,stroke:#2e7d32,color:#000
    class BR,SV,GD,AI uc
```

**Why this matters:** agents never touch raw tables. A KPI question resolves to one of the seven metric views, so an agent and a human analyst computing "claims by region" share one versioned definition — that is what keeps trust in the system intact.

---

## 4. Stage 3 — Deep Agent / "Synaptic Command" (evolved as domains grew)

```mermaid
flowchart TD
    U["User"] --> GW["AI Gateway → Model Serving"]
    GW --> ORC["Orchestrator<br/>picks the domain, delegates<br/>must check + update long-term memory every turn"]

    subgraph SA["Self-contained subagents — own prompt · own tools · own context window"]
        D1["Customer Analytics<br/>subagent"]
        D2["Distribution Channels<br/>subagent"]
        D3["Policy & Underwriting<br/>subagent"]
        D4["Claims Analytics<br/>subagent"]
        MM["Memory Manager<br/>subagent"]
    end

    ORC --> D1
    ORC --> D2
    ORC --> D3
    ORC --> D4
    ORC <--> MM

    D1 --> G1["Genie Space:<br/>customer"] --> T1["customer gold/silver tables"]
    D2 --> G2["Genie Space:<br/>distribution"] --> T2["distribution gold/silver tables"]
    D3 --> G3["Genie Space:<br/>policy & underwriting"] --> T3["policy gold/silver tables"]
    D4 --> G4["Genie Space:<br/>claims"] --> T4["claims gold/silver tables"]

    MM <--> LTM[("Long-term memory · Delta<br/>preference · fact · decision<br/>project · feedback")]

    D1 --> ORC
    D2 --> ORC
    D3 --> ORC
    D4 --> ORC
    ORC --> U

    classDef mem fill:#fff4e0,stroke:#ef6c00,color:#000
    class MM,LTM mem
```

**What changed vs Stage 2:** asset resolution moved *inside* each domain subagent (each is wired to its own Genie Space and tables), the orchestrator's job narrowed to picking a domain, and cross-conversation memory became a dedicated subagent. Same principle as the first pivot — specialize, keep each unit's context small — applied one level up.

---

## 5. Architecture evolution — why there were two pivots

```mermaid
flowchart LR
    subgraph S1["Stage 1 — Monolithic agent · FAILED in testing"]
        A["One agent<br/>one prompt · 20+ tools · full history"] --> AF["Context bloat +<br/>wrong tool selected"]
    end
    subgraph S2["Stage 2 — Supervisor · SHIPPED (8–9 wk MVP)"]
        B["Supervisor<br/>8-node LangGraph"] --> B1["Genie"]
        B --> B2["Multi-Tool"]
        B --> B3["Analysis"]
        B --> B4["Visualization"]
    end
    subgraph S3["Stage 3 — Deep Agent · EVOLVED"]
        C["Orchestrator"] --> C1["4 domain subagents<br/>own context each"]
        C --> C2["Memory Manager"]
    end
    S1 -.->|"pivot 1: split 'decide' from 'do'"| S2
    S2 -.->|"pivot 2: Supervisor's tool list<br/>re-approaching the same bloat"| S3
```

---

## 6. Platform constraint and guardrails (the cross-cutting layer)

```mermaid
flowchart LR
    subgraph WANTED["Wanted"]
        AB["Agent Bricks<br/>Multi-Agent Supervisor<br/>(managed)"]
    end
    subgraph BLOCK["Blocked"]
        R["Not GA in AIA's Azure region<br/>SEA / East Asia"]
    end
    subgraph BUILT["Built instead — GA primitives only"]
        P1["Agent Framework"]
        P2["Model Serving + AI Gateway"]
        P3["Genie Spaces"]
        P4["Vector Search"]
        P5["Metric Views"]
        P6["MLflow Tracing + Eval"]
    end
    AB --> R --> BUILT
```

**Trade-off stated plainly:** more code to own than a managed service, in exchange for a production path that did not depend on a regional Beta timeline nobody controlled.

---

## Quick reference — the numbers on the diagrams

| Item | Value |
| --- | --- |
| Supervisor nodes | 8 (LangGraph StateGraph) |
| Clarification threshold | confidence < 60% |
| Context Index | 16 governed assets, Vector Search, endorsed-first ranking |
| Specialist workers (Stage 2) | 4 — Genie · Multi-Tool · Data Analysis · Visualization |
| Domain subagents (Stage 3) | 4 + Memory Manager |
| Governed metric views | 7 |
| Genie Spaces | 4 domains |
| Short-term memory | `ai_ops.conversations`, Delta, keyed by `thread_id`, 30-day retention |
| Prompt store | `ai_ops.agent_instructions`, base + overlay, 5-minute cache |
| Long-term memory categories | preference · fact · decision · project · feedback |
| Outcome | 2–10 days → minutes · ~4 wk dashboards → self-serve · ~35% YTD consumption growth (correlated, not causal) · MVP in 8–9 weeks |

---

*Companion to *`AIA_Technical_Implementation_Flow.md`* and *`AIA_MultiAgent_DeepDive_15-20min.md`* · MongoDB Staff FDE prep*
