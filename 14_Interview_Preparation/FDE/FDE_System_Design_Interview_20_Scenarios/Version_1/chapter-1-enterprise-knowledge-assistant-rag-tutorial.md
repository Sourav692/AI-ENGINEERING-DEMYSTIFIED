# Chapter 1: Design an Enterprise Knowledge Assistant with RAG

*Source: The Forward Deployed Engineer System Design Interview: 20 Real-World AI & Enterprise Scenarios*
*Tutorial format: FDE Chapter Tutorial Builder — self-reviewed against the decomposition rubric, 2 passes*

---

## 1. The Customer Problem and Discovery

**Key Points**
- The literal ask ("answer questions from Drive, SharePoint, Slack, wikis, tickets without exposing unauthorized info") hides four different definitions of success across four stakeholders.
- The job of the interview is to reframe a *feature* request into a *business outcome* with a measurable success condition.
- The single design anchor for the whole chapter: **permission fidelity is the dangerous constraint, not retrieval quality.**
- Map people, not just systems — each stakeholder notices a different failure first.
- Never start architecture before naming whose workflow changes, what success looks like, and which constraint is most dangerous if ignored.

### The first five minutes of the meeting

A multinational company asks for "an AI assistant that answers employee questions from Drive, SharePoint, Slack, wikis, and support tickets without exposing unauthorized information." Everyone agrees on the feature; nobody agrees on what success means.

- **HR** wants employees to find policy answers without opening a ticket.
- **Engineering** wants project knowledge searchable without digging through Slack threads.
- **Security** wants proof the assistant will never surface content a user cannot already see.
- **Support** wants fewer repetitive questions, plus a way to investigate wrong answers.

These are not four separate problems — they are four views of the same workflow.

> **Design anchor:** Your job is not to pick a vector database or a model. It is to turn the request into a measurable business result: deliver grounded answers with source citations while preserving source-system permissions and freshness. Everything else — indexing, retrieval, ranking, approval flows, deletion handling, logging — exists to make that outcome real.

### Reframe the request before you design

| Weak restatement | Strong restatement |
|---|---|
| "We need a chatbot over company documents." | "We need an internal assistant that helps employees resolve work questions by retrieving and summarizing approved content from several source systems, while respecting the source system's access rules and showing where each answer came from." |

The strong version separates the user experience from the underlying workflow, names the permission boundary, and implies an evaluation standard — all at once. Notice the difference between the requested *feature* ("ask questions in one place") and the business *result* ("employees spend less time hunting for information, support sees fewer repetitive issues, security can audit access behavior"). If you cannot say how the workflow changes, you cannot defend the architecture.

### Map the people, not just the systems

The obvious map is the systems (Drive, SharePoint, Slack, wikis, tickets). The more important map is human:

| Role | What they care about | Typical failure they will notice first |
|---|---|---|
| End user | Fast, correct answers with citations | Wrong or missing answer |
| Operator / support | Diagnosing bad answers and gaps | No trace of why the system failed |
| Security owner | Permission leakage and auditability | Answer exposes content user should not see |
| Executive sponsor | Adoption and cost-to-value | Tool looks impressive but does not reduce work |

Optimizing only for employee delight can create a shadow information channel security cannot defend. Optimizing only for control kills adoption.

### One concise opening answer

> "We need an internal knowledge assistant for employees across departments. The assistant should answer questions using approved content from Drive, SharePoint, Slack, wikis, and support tickets, but only from material the requesting user is allowed to see. The success metric is grounded answers with citations, low hallucination risk, and freshness that matches source updates. I'd start by clarifying authority sources, permission inheritance, freshness expectations, and what the business wants to happen when the system is unsure or the sources conflict."

That answer does not lock you into a specific technology. It proves you can frame the problem before you solve it.

### The first design rule

Do not start architecture until you can answer three questions: **whose workflow changes, what does success look like, and which constraint is most dangerous if ignored.** For this problem, the dangerous constraint is **permission preservation** — a useful assistant that leaks content is worse than no assistant at all. Once that is clear, the rest of the design becomes a search for the safest path to grounded answers, citations, and freshness.

---

## 2. Clarifying Questions, Requirements, and Constraints

**Key Points**
- Ask fewer, sharper questions — ones that actually move architecture, not generic intake.
- Split requirements into functional (what it must do) vs. non-functional (how safely/reliably it must do it).
- Use a must/should/could lens to protect the MVP boundary under time pressure.
- Turn operating goals into measurable constraints, not vague preferences.
- Declare explicit non-goals to stop the assistant from sprawling into a platform.

### Ask fewer questions, but make them sharper

Interview time is limited, so discovery should target the questions that most change the design:

- Which sources are authoritative for each content type?
- Must the assistant inherit source-system permissions in real time, or is periodic synchronization acceptable?
- Is the assistant allowed to answer only from retrieved passages, or can it synthesize across sources?
- What should happen when sources conflict?
- How fresh must answers be for policies, tickets, and project updates?
- Who can view audit logs and answer traces?
- What is the fallback when retrieval fails or the model is uncertain?

These questions build an *assumption ledger*. If the interviewer withholds information, state your assumption explicitly: "I will assume source permissions must be enforced at query time, because that is the safest default and it changes the retrieval layer," or "I will assume citations must point to the exact passage used, not merely the document title." Clear assumptions prevent accidental design drift.

### A useful stakeholder snapshot (recap for reference)

| Role | What they care about | Typical failure they will notice first |
|---|---|---|
| End user | Fast, correct answers with citations | Wrong or missing answer |
| Operator / support | Diagnosing bad answers and gaps | No trace of why the system failed |
| Security owner | Permission leakage and auditability | Answer exposes content user should not see |
| Executive sponsor | Adoption and cost-to-value | Tool looks impressive but does not reduce work |

### Separate functional requirements from operating constraints

**Functional requirements** describe what the assistant must do. For the MVP, prioritize:

1. **Ingest heterogeneous sources incrementally.** Drive, SharePoint, Slack, wikis, and support tickets should not require a full reindex on every change.
2. **Preserve document versions and ACL metadata.** Retrieval must answer "what was visible to this user at this time?"
3. **Perform hybrid retrieval and reranking.** Keyword and semantic retrieval together are usually more robust than either alone.
4. **Generate answers grounded in retrieved passages.** The model should respond from evidence, not free-form memory.
5. **Show citations and abstain when evidence is weak.** A correct refusal is better than a confident hallucination.
6. **Record safe feedback for evaluation.** Thumbs-up, thumbs-down, and "missing source" signals help improve retrieval and answer quality without collecting unrestricted user prompts indiscriminately.

Use a must/should/could lens explicitly:

- **Must-have:** the system cannot ship without incremental ingestion, ACL preservation, grounded answers, and cross-user isolation.
- **Should-have:** hybrid retrieval, reranking, citations, and safe feedback are important and should be in the first usable version if possible.
- **Could-have:** richer analytics, broader source coverage, and more advanced UX niceties can wait until the core trust path works.

This distinction matters because it changes the MVP boundary. Must-haves define the launch gate. Should-haves are the next layer if time and risk allow. Could-haves are future expansions that should not distort the first architecture. If the interviewer forces a tradeoff, the must-have category gets protected first, because it is the smallest set that still preserves the customer promise.

**Non-functional requirements (operating constraints)** describe how safely and reliably the system must behave:

- **No cross-user information disclosure.** A user should only see content allowed by their source permissions and identity mapping.
- **p95 answer latency under an agreed target.** The exact number depends on the business, but the requirement should be stated as a percentile, not a vague "fast enough."
- **Deletions reflected within a freshness SLO.** If a document is removed or access is revoked, the system must stop serving it within the agreed window.
- **Graceful degradation when a connector or model fails.** The assistant should fall back to partial coverage, stale-but-labeled answers, or a refusal rather than silently producing unsupported results.

These are constraints, not preferences. A preference is "we would like prettier citations." A constraint is "we cannot expose content from another user's SharePoint folder." Saying that out loud in an interview is showing judgment.

### Scope boundary — explicit non-goals

Every enterprise assistant can sprawl into an unbounded platform if you let it. Declare what the MVP will not support and why. A strong non-goals list might exclude:

- Generating tasks in downstream systems.
- Editing documents or tickets.
- Using personal files outside approved enterprise repositories.
- Answering from unapproved web sources.
- Cross-tenant search across subsidiaries unless authorization is already standardized.
- Long-term conversational memory beyond a session.

That exclusion list is not evasive; it is protective. It prevents the design from conflating knowledge retrieval with workflow automation, content management, and agentic action execution. In an interview, that distinction signals you can deliver a bounded product instead of a fragile showcase.

### A concise interview question tree

1. Who uses it, and how often?
2. What content sources are in scope?
3. How fresh must source changes and deletions be?
4. What permissions model governs each source?
5. What languages, file types, and citation style are required?
6. What latency, residency, retention, and cost limits must we honor?
7. When should the assistant refuse, cite, or escalate to a human?

That tree helps you avoid random follow-up questions and lets the interviewer see how you turn open-ended discovery into a design agenda.

### Example MVP shape

A practical MVP for this scenario is not "an AI assistant." It is a smaller, sharper promise: ingest heterogeneous sources incrementally; preserve document versions and ACL metadata; and perform hybrid retrieval and reranking before answering with citations. Everything else is secondary until that path is trusted. If the customer later wants deeper workflow actions, richer analytics, or broader source coverage, those become follow-on increments rather than hidden assumptions inside version one.

### Requirement-to-component traceability

A candidate who can map requirements to components looks ready to build and support the system, not just describe it:

| Requirement | Primary component(s) |
|---|---|
| Incremental heterogeneous ingestion | Connectors, change-event processor, ingestion queue |
| Version and ACL preservation | Metadata store, permission-aware index, audit log |
| Hybrid retrieval and reranking | Search index, semantic retriever, reranker service |
| Grounded answers with citations | Answer generator, citation formatter, evidence selector |
| No cross-user disclosure | Identity mapping, authorization filter, policy enforcement point |
| p95 latency target | Query service, caching, reranking budget, model timeout policy |
| Deletions freshness SLO | Connector sync, tombstone handling, reindex pipeline |
| Graceful degradation | Circuit breakers, fallback paths, partial-answer policy |

The value of the table is not the formatting; it is the discipline. It forces you to prove that every must-have has an owner in the architecture.

### What the interviewer is really testing

The job-market signal here is broader than one AI system. This kind of answer shows you can discover requirements, prioritize under ambiguity, and protect delivery when the customer has not finished defining the problem. That is core FDE work: translating uncertainty into a plan that is useful, safe, and shippable. The strongest move is not to claim certainty — it is to say, "Here are the assumptions I need to proceed, here is the highest-risk constraint, and here is the smallest viable scope that still delivers customer value."

---

## 3. Scale Estimates, SLOs, and Capacity

**Key Points**
- The first architecture that "sounds reasonable" at average load is often the one that fails at peak load or during a deadline surge.
- Use round, explicit, and clearly labeled scale assumptions — precision is not the point, sensitivity is.
- Estimate embedding cost, index cost, and model-token cost independently — they have different owners and failure modes.
- Define service levels tied to the customer workflow (freshness, recall, citation precision, groundedness), not just infrastructure uptime.
- Find the real bottleneck — it's usually peak QPS, freshness requirements, or permission complexity, not raw document count.

### Start with the numbers that change the architecture

A useful capacity discussion starts with one uncomfortable fact: the first architecture that sounds reasonable at average load is often the one that fails at peak load, during a deadline surge, or when a connector falls behind. In this scenario, the customer wants an enterprise assistant that can answer employee questions from Drive, SharePoint, Slack, wikis, and support tickets without exposing unauthorized information. That means the scale estimate has to drive the design, not decorate it.

Use round, explicit assumptions:

- 100,000 employees
- 50 million chunks after document splitting
- 20 QPS average query load
- 100 QPS peak query load

Those four inputs already force several decisions. A design that works for 20 QPS may still collapse under 100 QPS if retrieval, reranking, and generation all happen synchronously. Likewise, a system that can index 50 million chunks once may fail if it cannot refresh stale permissions or deletions quickly enough.

### Cost drivers — estimate each independently

For storage, separate the costs and scaling drivers instead of collapsing everything into "index size." The embedding store grows with chunk count and embedding dimensionality. The search index grows with chunk text, metadata, ACL fields, and inverted terms. The model-token cost grows at query time with prompt construction, retrieved context, citations, and answer generation. Those are different budgets, with different owners and different failure modes.

A clean interview move is to estimate each independently:

- **Embedding cost:** one-time or periodic cost to create embeddings for 50 million chunks, plus ongoing cost for changed chunks.
- **Index cost:** storage and maintenance cost for vector index, keyword index, and metadata/ACL index.
- **Model-token cost:** per-query cost from retrieval context plus generation, which scales with QPS and prompt length.

If the customer says support tickets and Slack change frequently, the refresh pipeline becomes a larger cost driver than the initial embedding job. If the answer must cite multiple sources, the prompt budget grows and may force shorter top-*k* retrieval, more aggressive reranking, or chunk-size changes.

### Define the service levels that matter to the customer workflow

This system should not be judged only on uptime. The customer outcome is: employees get grounded answers quickly enough that they trust the assistant and keep using it. That translates into a small set of service-level indicators and objectives:

- **Freshness lag:** time from source change or deletion to reflected availability in retrieval.
- **Retrieval recall:** fraction of truly relevant documents that appear in the candidate set.
- **Citation precision:** fraction of cited passages that actually support the answer.
- **Answer groundedness:** fraction of answers whose claims are supported by retrieved sources rather than model memory or inference.

Availability and latency still matter, but they serve the workflow. A slow system that gives correct, permission-safe answers can still be valuable if the user is searching for a policy, procedure, or troubleshooting step. A fast system that returns stale or unauthorized content is worse than useless because it creates false confidence.

A practical way to say this in the interview: the latency budget must preserve enough time for authorization, retrieval, reranking, grounding, and answer generation. If p95 latency is the user-facing objective, then each stage gets a budget slice. For example, the query path might allocate time for identity resolution, ACL filtering, hybrid retrieval, reranking, and the model call separately, with a timeout policy that degrades gracefully rather than failing open.

### A whiteboard derivation for hybrid retrieval

Hybrid search is the right default when the corpus mixes policy language, product terms, ticket identifiers, and natural-language questions. Vector similarity helps semantic matches; keyword matching helps exact names, codes, and rare terms. Make the weighting explicit:

```
S_hybrid = α · S_vector + (1 − α) · S_keyword
```

Interpretation matters as much as the formula. `α` is not a sacred constant; it is a tuning parameter. If users ask for exact policy titles, team names, error codes, or ticket numbers, keyword score deserves more weight. If they ask conceptually — "How do I request access to the finance dashboard?" — semantic similarity may deserve more weight. The right `α` should come from a representative evaluation set, not intuition. A strong answer here explains that the hybrid weighting should be tested against real query types, permission filters, and citation quality — the goal is not to maximize a single retrieval metric in isolation, but to improve useful, grounded answers under enterprise constraints.

### Where the real bottleneck usually appears

The estimate that most often changes component selection is not raw document count. It is usually one of three things:

1. **Peak QPS and latency budget**, which determine whether the query stack needs caching, precomputed metadata, batched reranking, or a smaller context window.
2. **Freshness requirements**, which determine whether you need near-real-time change capture, tombstones, and reindex prioritization.
3. **Permission complexity**, which determines whether ACL checks happen before retrieval, during retrieval, or at answer assembly.

If peak QPS is 5x average load, the system cannot be sized to average alone. If a deletion must disappear quickly, the ingestion path cannot be purely batch. If authorization is per-document and per-user, the retrieval layer needs to enforce it before anything reaches the model. That is why the first plausible architecture often gets revised. A candidate might sketch a single vector database, one nightly indexing job, and a single answer endpoint. It sounds clean at 20 QPS. But at 100 QPS, with frequent changes and strict permission boundaries, that design can miss deadlines or leak stale access paths. The correction is not just "add more servers." It is to split ingestion, retrieval, authorization, and generation into independently scalable pieces with explicit freshness and timeout policies.

### Sensitivity beats false precision

Say the numbers with honesty. State average, peak, growth, and headroom rather than pretending there is one exact answer:

- Average query load: 20 QPS
- Peak query load: 100 QPS
- Growth assumption: perhaps 2x to 10x over the planning horizon, depending on rollout and adoption
- Headroom target: enough spare capacity to handle bursts, retries, connector backlog, and reindex jobs without starving interactive traffic

A simple sensitivity table can change the design conversation:

| Scenario | Query load | Implication |
|---|---|---|
| Baseline | 20 QPS average | Single-region interactive path may be sufficient if retrieval and model latency are stable |
| Peak | 100 QPS | Requires queueing control, caching, and tighter per-stage latency budgets |
| 10x growth | 200 QPS average, 1,000 QPS peak-equivalent bursts | Likely forces partitioning, autoscaling, and more selective retrieval/candidate generation |

The point of the table is not numerical perfection. It is to show which assumption is load-bearing. If 10x growth breaks the current search shard size, you discover that early. If the answer-token budget becomes the cost hotspot, you shorten prompts or reduce evidence windows before launch.

### Unit economics are part of the design, not an afterthought

For an enterprise assistant, unit economics are not only about cloud spend. They are also about how much trust and support cost each answer consumes. Ask three questions:

- What does each answered question cost in embeddings, retrieval, reranking, and model tokens?
- What does each freshness update cost in connector processing and reindexing?
- What does each security failure cost in investigation, rollback, and customer trust?

That is why the capacity discussion belongs early. If the answer path is too expensive, the product may need smaller context windows, better caching, or narrower retrieval. If the freshness path is too slow, the customer may need to prioritize connectors or a stricter definition of "fresh enough." If the ACL model is too expensive per query, the system may need permission-aware partitioning.

The interview signal is pragmatic judgment. You are not trying to overengineer every possible future. You are proving that you can size the system well enough to meet the customer outcome, protect permissions, and keep the design economically sane. The best closing sentence in this part of the interview is simple: every estimate should justify an architectural choice or an operational limit. If it does not change the design, it does not belong in the design.

---

## 4. Architecture and End-to-End Flow

**Key Points**
- The hidden constraint is permission fidelity, not retrieval quality — connecting every source and indexing everything is the wrong first instinct.
- The design splits into a control plane (policy, config, credentials) and a data plane (live queries, evidence, permissions, responses).
- Every component exists because it owns a requirement — if you can't say what requirement a box serves, it's probably decorative.
- The query path is synchronous and permission-gated; ingestion is asynchronous and must tolerate backpressure and outages.
- Trust boundaries need explicit failure assumptions — a connector can miss an event, a cache can serve stale data, a model can fabricate a claim.

### Start with the user request, then expose the hidden constraint

A multinational company wants an AI assistant that answers employee questions from Drive, SharePoint, Slack, wikis, and support tickets without exposing unauthorized information. The obvious solution is to connect every source, index everything, and let the model answer from retrieved documents. That is the wrong first instinct. The hidden constraint is not retrieval quality; it is **permission fidelity**. If the assistant cannot preserve source-system access rules at query time and at ingestion time, the rest of the design is just a faster way to leak information.

So the architecture has to do two things at once: answer well and answer safely. That means the system is not a single "chat app." It is a chain of systems with separate responsibilities, separate trust boundaries, and different consistency requirements.

### Top-down architecture

At the highest level, the design splits into a control plane and a data plane.

- The **control plane** manages policy, configuration, credentials, connector scheduling, tenant settings, evaluation rules, and operational controls.
- The **data plane** serves live user questions, fetches evidence, enforces permissions, and returns responses.

A useful way to draw it is as a layered system rather than decorative boxes.

```mermaid
flowchart TB
    subgraph Sources["External Systems of Record"]
        Drive[Drive]
        SP[SharePoint]
        Slack[Slack]
        Wiki[Wikis]
        Tix[Support Ticket System]
    end

    subgraph Ingest["Ingestion &amp; Indexing Path — async"]
        Conn[Source Connectors]
        Queue[Event + Backfill Queue]
        Parse[Parser / OCR / Chunker]
        ACLNorm[ACL Normalizer]
        KIdx[(Keyword Index)]
        VIdx[(Vector Index)]
    end

    subgraph QueryPath["Query Path — sync"]
        Auth[User Auth + Group Resolution]
        Rewrite[Query Rewrite Service]
        Retriever[Permission-Aware Retriever]
        Rerank[Reranker]
        Budget[Context Budget Manager]
        Gateway[LLM Gateway]
        CiteBuilder[Citation Builder]
        Policy[Output Policy Engine]
    end

    Trace[(Evaluation &amp; Trace Store)]

    Sources --> Conn --> Queue --> Parse --> ACLNorm
    ACLNorm --> KIdx
    ACLNorm --> VIdx

    User((Employee)) --> Auth --> Rewrite --> Retriever
    KIdx --> Retriever
    VIdx --> Retriever
    Retriever --> Rerank --> Budget --> Gateway --> CiteBuilder --> Policy
    Policy --> Response[["Grounded answer + citations, or abstain"]]

    Policy -.log.-> Trace
    Retriever -.log.-> Trace
```

**External systems of record:** Drive, SharePoint, Slack, wikis, support ticket system.

**Ingestion and indexing path:** source connectors → event queue and backfill queue → parser/OCR/chunker → ACL normalizer → keyword index → vector index → evaluation and trace store.

**Query path:** user auth and group resolution → query rewrite service → permission-aware retriever → reranker → context budget manager → LLM gateway → citation builder → output policy engine → response API.

**Operational dependencies:** identity provider, secret manager, observability pipeline, admin console, feedback capture store.

### Component responsibilities in dependency order

The ingestion side should be explained from the outside in:

1. **Source connectors** talk to the external systems of record. They are the boundary where the assistant first depends on another system's API, export format, rate limits, and deletion semantics.
2. **Event and backfill queue** decouples source changes from indexing work. Events handle near-real-time updates; backfill catches missed items, connector outages, and historical ingestion.
3. **Parser / OCR / chunker** turns heterogeneous documents into normalized text units. This is where PDFs, images, slides, tickets, and chat threads become searchable content.
4. **ACL normalizer** converts source-specific permissions into a common internal representation. This is one of the most load-bearing parts of the design because a search hit is useless if the caller cannot see it.
5. **Keyword and vector indexes** store two complementary retrieval surfaces: exact-match and semantic match. The keyword index helps with names, IDs, error codes, and policy phrases. The vector index helps with paraphrase and natural-language questions.
6. **Permission-aware retriever** applies ACL filters before or during candidate selection so unauthorized documents never become answer evidence.
7. **Reranker** improves ranking quality after retrieval, usually with a smaller, cheaper model or scoring layer than the final generator.
8. **LLM gateway** is the controlled point where prompts, model selection, rate limiting, and guardrails are centralized.
9. **Citation builder** attaches source references to each answerable claim so the user can verify where the answer came from.
10. **Evaluation and trace store** records privacy-safe traces, quality signals, and feedback for debugging and continuous improvement.

On the query side, the order matters because it encodes risk. Authentication comes first. Permission filtering comes before answer generation. Output policy comes before the user sees the result. Tracing happens after the decision but must be privacy-aware.

### Happy path: from question to grounded answer

A good interview walkthrough should narrate one request all the way through the stack:

1. **Authenticate the user and resolve groups.** The request enters the service, the user is authenticated through the enterprise identity provider, and group membership is resolved. This step is synchronous because the system cannot decide access without it.
2. **Rewrite the question only when meaning is preserved.** The system may rewrite the query for search quality, but only if it preserves intent. "What is the PTO policy for contractors?" can become a cleaner retrieval query; "Can I share customer data with vendors?" must not be softened into a vague synonym that changes meaning.
3. **Retrieve candidates with ACL filters.** The retriever searches the keyword and vector indexes while filtering to only documents the user is allowed to see. This is the point where permission-aware design becomes concrete, not aspirational.
4. **Rerank and enforce a context budget.** The top candidates are reranked, then trimmed to fit token and latency constraints. The budget manager decides how much evidence the model gets and which sources matter most.
5. **Generate from evidence with citations.** The LLM gateway produces an answer only from the selected evidence. The citation builder attaches document links, timestamps, or source identifiers so the answer can be audited.
6. **Apply output policy and return or abstain.** If confidence is too low, evidence is insufficient, or the request looks unsafe, the assistant should abstain or ask for clarification instead of hallucinating.
7. **Capture a privacy-safe trace and feedback.** The system records enough to diagnose the path later without storing unnecessary sensitive content. User feedback is preserved as a signal for evaluation and retraining of ranking or retrieval logic.

```mermaid
sequenceDiagram
    participant U as User
    participant ID as Identity Provider
    participant QR as Query Rewrite
    participant R as Retriever (keyword + vector)
    participant RR as Reranker
    participant G as LLM Gateway
    participant C as Citation Builder / Policy
    participant T as Trace Store

    U->>ID: Authenticate, resolve groups
    ID-->>U: Group membership
    U->>QR: Ask question
    QR->>R: Rewritten query (intent preserved)
    R->>R: Filter candidates by ACL
    R-->>RR: Candidate passages
    RR-->>G: Top-k reranked, budget-trimmed evidence
    G-->>C: Draft answer grounded in evidence
    C-->>U: Answer + citations, or abstain
    C->>T: Log privacy-safe trace + feedback hook
```

That sequence is the architecture in motion. In the interview, say it out loud in clean order exactly once. It shows that you understand not only the boxes, but the control flow between them.

### Sync versus async boundaries

The most important synchronous boundary is the live question path. Users expect an answer now, so authentication, retrieval, reranking, generation, and policy enforcement happen synchronously. The ingest path is different. Connectors, OCR, chunking, ACL normalization, and indexing are best treated as asynchronous work because they are throughput-heavy, bursty, and failure-prone.

This is where backpressure and flow control matter. If a connector floods the pipeline with updates, the queues should absorb the burst up to a safe limit, then slow the producer or prioritize fresher changes over stale backfills. If OCR falls behind, the system should continue serving already-indexed content instead of blocking live questions. If the model gateway is degraded, the system should fail closed for sensitive requests rather than degrade into unsafe guesses.

### Trust boundaries and state ownership

A strong design names who owns each piece of state:

- **Systems of record** own the original documents, messages, tickets, and permissions.
- **The assistant's indexes** own derived search state, not source truth.
- **The ACL mapping store** owns the normalized permission model.
- **The trace store** owns diagnostic metadata, not raw source content unless explicitly allowed.
- **The LLM gateway** owns model routing and prompt assembly, but not source permissions.

Trust boundaries appear where the assistant crosses from one owner to another: source API calls, identity resolution, search indexing, model invocation, and outbound citations. Each boundary deserves a failure-mode discussion. A connector can miss an event. A group lookup can be stale. A cached result can outlive its permission. A model can generate a plausible but unsupported claim. The design must assume every boundary can fail independently.

### Partitioning, caches, and queues

Partitioning key choice is not a storage footnote; it determines scale behavior and blast radius. You may partition ingestion by tenant, by source system, or by document namespace. For query serving, tenant-level isolation is often the safest default because it simplifies quotas, billing, and administrative controls. Within a tenant, source or corpus partitioning can help with reindexing and cache locality.

Caches belong in narrow places where staleness is acceptable and bounded. Identity and group lookups may be cached briefly to reduce latency. Hot retrieval results may be cached only if cache invalidation is tied to permission changes and document updates. A cache is not a permission model; it is a latency optimization that must never outrun policy.

Queues belong anywhere work is asynchronous or retryable: connector syncs, parsing jobs, backfills, embedding jobs, and citation enrichment. They also absorb spikes, but only if you define dead-letter behavior, retry limits, and tenant-level fairness. Without backpressure, one noisy source can starve another.

### Failure-path overlay: the connector missed a deletion event

Now repeat the path under one failure that matters: a connector misses a deletion event from the source system. The user asks about a policy that was deleted yesterday.

1. The question arrives and the user authenticates normally.
2. The retriever finds an old chunk because the stale index still contains old content.
3. The ACL filter passes because permission data is still valid; the problem is freshness, not access.
4. The reranker promotes the stale chunk because the text matches well.
5. The generator is about to answer from evidence that should no longer exist.

```mermaid
flowchart LR
    A[Connector misses a deletion event] --> B[Stale chunk stays in the index]
    B --> C{ACL check at query time}
    C -->|Passes — permission data still valid| D[Reranker promotes the stale chunk]
    D --> E{About to generate from deleted evidence}
    E -->|Freshness threshold / staleness check| F[Suppress, mark stale, or revalidate against source of record]
    F --> G[Backfill + reconciliation replays the deletion]
    G --> H[Trace shows a prior answer used a now-deleted document]
    style E fill:#a63d40,stroke:#7a2b2d,color:#ffffff
```

This is exactly why the architecture needs deletion handling, backfill, and freshness checks. A robust design can respond in several ways depending on the customer requirement: mark the result as stale, suppress content once deletion is confirmed, trigger revalidation against the system of record, or use a freshness threshold that rejects old material for sensitive corpora. The key interview point is that deletion is not only an indexing problem; it is a trust problem. If deletion events can be missed, then backfill, reconciliation, and source-of-record checks become part of the safety story.

### What belongs in the MVP and what can wait

An MVP should prove the loop end to end with the minimum number of moving parts that still respect permissions and freshness.

**MVP should include:**
- one or two high-value connectors
- event ingestion plus periodic backfill
- text extraction and chunking
- ACL normalization
- keyword plus vector retrieval
- permission-aware filtering
- a basic reranker
- LLM gateway with citations
- output policy for abstain and redaction
- trace capture and feedback

**Later evolution can include:**
- more source systems
- richer multimodal OCR
- tenant-specific ranking models
- advanced freshness policies by content class
- deeper analytics on retrieval quality
- automated regression tests for prompt and retrieval drift
- human review workflows for high-risk domains

This distinction matters in interviews because it shows you can land value early without pretending the final architecture must be built all at once.

### Component responsibility table

| Component | Primary responsibility | Trust boundary | Sync/async | System of record? |
|---|---|---|---|---|
| Source connectors | Read source content and metadata | Crosses into external APIs | Async | No |
| Event and backfill queue | Decouple source changes from indexing | Internal service boundary | Async | No |
| Parser / OCR / chunker | Normalize content into retrievable units | Derived-content boundary | Async | No |
| ACL normalizer | Map source permissions to internal policy | Security boundary | Async, with query-time checks | No |
| Keyword and vector indexes | Store searchable derived representations | Internal storage boundary | Async writes, sync reads | No |
| Permission-aware retriever | Filter by access and fetch candidates | Data access boundary | Sync | No |
| Reranker | Improve candidate ordering | Internal inference boundary | Sync | No |
| LLM gateway | Manage model calls and prompt assembly | External model boundary | Sync | No |
| Citation builder | Attach evidence references | Output trust boundary | Sync | No |
| Evaluation and trace store | Record diagnostics and feedback | Observability boundary | Mixed | No |

### Why this architecture matters in an FDE interview

This design is not just technically coherent; it is customer-legible. It lets you explain to a business stakeholder why permissions are preserved, why freshness is not optional, and why a "better answer" is useless if it is unauthorized or stale. It also lets you explain to an engineering stakeholder where to tune latency, how to partition work, where to cache, what to queue, and what must remain synchronous.

That is the FDE signal: system decomposition plus stakeholder translation. The same architecture should satisfy both the person asking for business value and the engineer worrying about failure modes. The diagram is useful only when you can narrate data, identity, state, and failure through it. If you can do that cleanly, you are not just drawing boxes; you are defending a production system.

---

## 5. Data Model, APIs, and Working Code

**Key Points**
- Three records do most of the work: `Document`, `Chunk`, and `QueryTrace` — each with an explicit owner and retention rule.
- API contracts need explicit idempotency, versioning, and structured error semantics — not just a happy-path shape.
- The riskiest part of the system is not the prompt template; it's the decision about what evidence the model is allowed to see.
- A small, typed permission-and-grounding function proves the design safely, without building the whole product.
- Contract tests and failure-injection tests prove the safety property in code, not just in words.

### Turning the boxes into durable state

The fastest way to make this architecture interviewable is to stop speaking in abstractions and name the records that keep the system honest. In this assistant, three records do most of the work:

- **`Document(id, source, version, owner, acl_policy_id, deleted_at)`** is the source-of-truth envelope for anything ingested from Drive, SharePoint, Slack, a wiki, or a ticketing system. `id` is the internal surrogate key; `source` identifies the upstream system and object reference; `version` captures the latest imported revision; `owner` is the accountable human or team; `acl_policy_id` points to the permission policy that decides who may see it; and `deleted_at` marks tombstone state so the document can disappear from search without pretending it never existed. Its lifecycle is: discovered, ingested, indexed, updated, tombstoned, and eventually retained or purged according to policy. The retention rule must distinguish between the live document record, which may be needed for audit and deduplication, and any derived embeddings or trace data, which may have different retention windows.

- **`Chunk(id, document_id, text, embedding_ref, offsets, metadata)`** is the retrieval unit. `id` is the primary key; `document_id` links back to the parent document; `text` stores the exact passage shown to the model; `embedding_ref` points to vector storage rather than embedding bytes bloated into the relational store; `offsets` preserve passage boundaries for citations; and `metadata` carries version, source type, language, and indexing hints. Its lifecycle is born during parsing, updated when the parent document changes, and invalidated when the source version changes or the document is deleted. The retention rule should be simpler than the document: a chunk should not outlive the authorization and freshness guarantees of its parent.

- **`QueryTrace(id, actor_hash, retrieval_set, model_version, latency, outcome)`** is the operational memory. `id` is the trace key; `actor_hash` is a privacy-safe pseudonymous identifier for the user or service principal; `retrieval_set` captures which chunks were considered and which were selected; `model_version` records the assistant variant used; `latency` supports SLO debugging; and `outcome` distinguishes answered, abstained, escalated, or errored. Keep this record long enough to reconstruct incidents, demonstrate policy enforcement, and support feedback analysis, but not so long that it becomes a shadow copy of sensitive content.

Those records define the design boundary. Once you can describe them clearly, you can discuss ownership, update rules, and failure recovery without hand-waving.

### Contracts that make the system safe to change

The API surface should be small enough to reason about under pressure and strict enough to support replay, retries, and observability.

**`POST /v1/knowledge/query`** is the user-facing read path. It should authenticate with the same identity layer that determines document permissions, because query-time authorization is not a secondary concern. The request body should carry the user question, optional conversation state, and a client idempotency key if the caller may retry after a timeout. The response should include the answer, citations, confidence or abstention status, and a trace identifier. Error semantics matter: `401` for missing authentication, `403` when the caller lacks access to the requested corpus, `422` when the request body fails validation, `429` for throttling, and `5xx` only for infrastructure failures. If the assistant cannot ground the answer, a structured abstention is better than an embellished guess.

**`POST /v1/connectors/{id}/sync`** is the ingestion trigger. It should be idempotent because schedulers, webhooks, and operator retries will all eventually double-submit. The connector id plus the source checkpoint should define the deduplication boundary. If the same sync request arrives twice, the second request should be a no-op or a fast acknowledgment. Response bodies should expose which checkpoint was processed and whether the run was incremental, full, or backfill. This is also where versioning matters: changing the sync payload shape should produce a new contract version rather than silently overloading existing fields.

**`DELETE /v1/documents/{source_id}`** is the deletion path. It should accept the external source identifier, map it to the internal `Document`, mark the tombstone, queue index invalidation, and return a response that makes the delete durable even if downstream cleanup is asynchronous. The contract must be explicit that the delete is idempotent: deleting the same source twice should leave the system in the same state and should not resurrect derived chunks.

**`POST /v1/feedback`** closes the loop. It should accept a query trace reference, a coarse feedback label, and optionally a user comment. Feedback is not a side quest; it is part of the system contract because it tells you whether the model answered, abstained correctly, or exposed a usability problem. Keep it authenticated, rate-limited, and decoupled from the answer path so that angry users cannot stall search latency with a feedback burst.

Versioning belongs everywhere. Schema version, API version, connector checkpoint, embedding model version, and retrieval policy version all need to be visible in logs and traces. If an interviewer asks how you avoid breakage during iteration, the best answer is not "we move carefully"; it is "we make version boundaries explicit."

### The smallest safe code path

The riskiest part of the system is not the prompt template; it is the decision about what evidence the model is allowed to see. The candidate in a strong interview zooms directly into that path and implements the smallest function that proves the design can work safely. The point is not to build the whole product in miniature. The point is to show that permissions are checked before generation, that retrieval is hybrid, and that the system can abstain.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Protocol, Sequence


@dataclass(frozen=True)
class User:
    id: str


@dataclass(frozen=True)
class Passage:
    id: str
    score: float
    text: str
    source_id: str
    acl_policy_id: str
    citation: str | None = None


@dataclass(frozen=True)
class Citation:
    source_id: str
    quote: str
    offsets: tuple[int, int]


@dataclass(frozen=True)
class AnswerResult:
    status: str
    answer: str | None
    citations: List[Citation]


class IdentityService(Protocol):
    async def groups_for(self, user_id: str) -> List[str]: ...


class SearchService(Protocol):
    async def hybrid(self, query: str, filters: Dict[str, Any], top_k: int) -> List[Passage]: ...


class Reranker(Protocol):
    async def top(self, question: str, candidates: Sequence[Passage], k: int) -> List[Passage]: ...


class PolicyEngine(Protocol):
    def check(self, question: str, passages: Sequence[Passage]) -> Any: ...


class GroundedModel(Protocol):
    async def answer(self, question: str, passages: Sequence[Passage], require_citations: bool) -> Dict[str, Any]: ...


@dataclass(frozen=True)
class Dependencies:
    identity: IdentityService
    search: SearchService
    reranker: Reranker
    policy: PolicyEngine
    grounded_model: GroundedModel


class InsufficientEvidence(Exception):
    pass


async def answer(user: User, question: str, deps: Dependencies) -> Dict[str, Any]:
    groups = await deps.identity.groups_for(user.id)
    if not groups:
        return {"status": "forbidden", "citations": []}

    candidates = await deps.search.hybrid(
        query=question,
        filters={"allowed_groups": {"$overlap": groups}},
        top_k=40,
    )

    passages = await deps.reranker.top(question, candidates, k=8)
    if not passages or passages[0].score < 0.62:
        return {"status": "insufficient_evidence", "citations": []}

    validated = validate_passages(passages)
    policy_result = deps.policy.check(question=question, passages=validated)
    if not policy_result.allowed:
        return {"status": "policy_blocked", "citations": []}

    result = await deps.grounded_model.answer(
        question,
        validated,
        require_citations=True,
    )
    return validate_answer_response(result)


def validate_passages(passages: Sequence[Passage]) -> List[Passage]:
    if not passages:
        raise InsufficientEvidence("no passages")
    safe: List[Passage] = []
    for passage in passages:
        if not passage.id or not passage.source_id or not passage.acl_policy_id:
            raise ValueError("invalid passage metadata")
        if not 0.0 <= passage.score <= 1.0:
            raise ValueError("invalid passage score")
        safe.append(passage)
    return safe


def validate_citations(citations: Any) -> List[Citation]:
    if not isinstance(citations, list) or not citations:
        raise ValueError("missing citations")
    safe: List[Citation] = []
    for citation in citations:
        if not isinstance(citation, dict):
            raise ValueError("citation must be an object")
        source_id = citation.get("source_id")
        quote = citation.get("quote")
        offsets = citation.get("offsets")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("citation source_id missing")
        if not isinstance(quote, str) or not quote.strip():
            raise ValueError("citation quote missing")
        if (
            not isinstance(offsets, (list, tuple))
            or len(offsets) != 2
            or not all(isinstance(v, int) and v >= 0 for v in offsets)
            or offsets[0] > offsets[1]
        ):
            raise ValueError("invalid citation offsets")
        safe.append(Citation(source_id=source_id, quote=quote, offsets=(offsets[0], offsets[1])))
    return safe


def validate_answer_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    status = payload.get("status")
    answer_text = payload.get("answer")

    if status not in {"answered", "insufficient_evidence", "policy_blocked"}:
        raise ValueError("unexpected model status")

    if status == "answered":
        if not isinstance(answer_text, str) or not answer_text.strip():
            raise ValueError("missing answer text")
        citations = validate_citations(payload.get("citations"))
        payload = {**payload, "citations": citations}
    else:
        payload = {**payload, "citations": []}

    return payload
```

Read this like an interview whiteboard, but with production habits preserved. `User` and `Passage` are tiny typed boundaries so the function doesn't drift into dictionary soup. `answer()` first resolves the user's groups. That is the permission gate; without it, search is forbidden to widen the blast radius. Then it performs hybrid retrieval with a group filter, which is the practical union of lexical and vector search under authorization constraints. Then a reranker narrows the evidence set. Then the policy engine checks candidate passages before the model sees them. Only after those steps does the grounded model run.

The critical teaching warning here is that the snippet is intentionally incomplete. In production, the dependencies would still be real services with timeouts, retries, circuit breakers, request correlation IDs, and metrics, but the `Dependencies` wrapper makes the integration boundary explicit enough that the snippet is no longer hand-wavy. The code also omits chunk pagination, streaming tokens, cache layers, and background index repair. That is correct for an interview-sized sketch: you want the smallest code path that proves permission-aware hybrid retrieval before model generation, not a monolith.

### Why the code is organized this way

The line `groups = await deps.identity.groups_for(user.id)` is not a convenience call; it is the data-ownership boundary. The search system is not entitled to infer permissions from the question text, the inbox, or the embedding space. It needs explicit identity data.

The hybrid search call takes `filters={"allowed_groups": {"$overlap": groups}}`. The precise filter syntax is illustrative, but the design principle is durable: authorization must constrain candidate generation, not merely final answer rendering. If the retrieval set is wrong, no amount of prompt engineering can make the answer safe.

`reranker.top(..., k=8)` is where quality starts to converge. Many FDE interview answers fail because they either rely only on vector search or defer all ranking to the model. A reranker lets you make the model's job narrower and more deterministic.

`if not passages or passages[0].score < 0.62:` is the abstention hinge. The numeric threshold is illustrative; in a real system it would be tuned with offline evaluation and production telemetry. The important point is that there is a fail-closed branch. If evidence quality is weak, the assistant should say so rather than fabricate a plausible answer.

`validate_passages()` is the typed boundary validation that keeps malformed metadata from reaching the LLM. This matters more than it seems. In a production incident, the most common failure is not a dramatic exploit; it is a sloppy edge case — missing source IDs, stale ACL labels, or impossible scores — that leaks into the generation path because someone assumed the upstream service was already clean.

`policy.check(...)` is where domain constraints live: blocked content classes, citation requirements, prompt-injection heuristics, or source-type restrictions. The code does not claim the policy engine is perfect. It only makes the interface explicit so the interview answer can defend where policy belongs.

`validate_answer_response(result)` forces the model output back through a typed contract. That is the difference between "the model said it" and "the system accepted it." The assistant should never trust raw text as a finished product. It should expect a structured payload and reject anything that does not match. The tightened `validate_citations()` helper matters because a credible assistant does not merely return a non-empty citation list; it returns citations with source IDs, quotes, and offsets that are structurally sound enough to be checked against retrieved evidence.

### What the interview answer should say about concurrency, retries, and observability

A whiteboard snippet does not show the messiest parts: concurrent refreshes, retries, partial failures, and observability. You should name them anyway.

- **Concurrency:** two sync jobs may target the same connector, and one delete may race with an incremental ingest. Use optimistic concurrency on `Document.version` and checkpoint tokens so the later writer can detect whether it is applying a stale view. If the version has advanced, the sync should re-read before writing derived chunks.
- **Idempotency:** the query path usually does not need write idempotency, but ingestion, delete, and feedback absolutely do. A retry-safe request key or checkpoint token prevents duplicated chunk writes, duplicate tombstones, and duplicate feedback rows.
- **Validation:** both input requests and model outputs need typed validation. Validate the request before touching search, and validate the response before returning citations. This is how you keep boundary corruption from becoming user-visible corruption.
- **Retry:** only retry operations that are safe to repeat. A query can be retried if it is read-only and the request context is preserved. A connector sync can be retried if it carries a checkpoint. A delete can be retried if it is idempotent. A partially completed model generation should not be blindly re-run if the upstream evidence has changed.
- **Observability:** `QueryTrace` should capture request duration, retrieval set size, reranker score distribution, model version, and outcome so you can tell whether latency came from search, the LLM gateway, or policy enforcement. Emit spans around identity lookup, retrieval, reranking, policy checks, and model generation.

### A duplicate request and a failure drill

Suppose the connector service submits `POST /v1/connectors/42/sync` twice because the first request timed out after the server had already committed the checkpoint. The first request ingests the new wiki page version and writes chunks. The second request arrives with the same checkpoint token. The service recognizes that the checkpoint has already been processed and returns the same processed state without duplicating rows or re-embedding unchanged text. That is idempotency doing its job.

Now take the critical failure drill from the chapter scenario: the connector misses deletion events. If the delete path is explicit and the tombstone is versioned, the system can eventually reconcile by re-reading the source of truth and invalidating stale chunks. More importantly, the trace store can show that the assistant once answered from a document that later disappeared, which is exactly the kind of evidence you need during incident review. The operational lesson is simple: design the data model so that stale state is visible, not hidden.

### Contract test and failure-injection test

A strong answer does not stop at describing the API; it proves the contract in miniature.

```python
import pytest

@pytest.mark.asyncio
async def test_query_is_permission_aware_and_idempotent_lookup_path():
    calls = {"groups": 0, "search": 0, "rerank": 0, "policy": 0, "model": 0}

    class FakeIdentity:
        async def groups_for(self, user_id: str):
            calls["groups"] += 1
            return ["eng"]

    class FakeSearch:
        async def hybrid(self, query, filters, top_k):
            calls["search"] += 1
            assert filters == {"allowed_groups": {"$overlap": ["eng"]}}
            return [Passage(id="p1", score=0.9, text="x", source_id="doc1", acl_policy_id="acl1")]

    class FakeReranker:
        async def top(self, question, candidates, k):
            calls["rerank"] += 1
            return list(candidates)

    class FakePolicy:
        def check(self, question, passages):
            calls["policy"] += 1
            return type("R", (), {"allowed": True})()

    class FakeModel:
        async def answer(self, question, passages, require_citations):
            calls["model"] += 1
            return {
                "status": "answered",
                "answer": "Use policy doc A",
                "citations": [{"source_id": "doc1", "quote": "policy doc A", "offsets": [0, 12]}],
            }

    deps = Dependencies(
        identity=FakeIdentity(),
        search=FakeSearch(),
        reranker=FakeReranker(),
        policy=FakePolicy(),
        grounded_model=FakeModel(),
    )

    first = await answer(User(id="u1"), "where is the policy?", deps)
    second = await answer(User(id="u1"), "where is the policy?", deps)

    assert first["status"] == "answered"
    assert second["status"] == "answered"
    assert calls["groups"] == 2
    assert calls["search"] == 2
    assert calls["rerank"] == 2
    assert calls["policy"] == 2
    assert calls["model"] == 2
    assert first["citations"][0]["source_id"] == "doc1"


@pytest.mark.asyncio
async def test_failure_injection_when_metadata_is_stale_or_malformed():
    class FakeIdentity:
        async def groups_for(self, user_id: str):
            return ["eng"]

    class FakeSearch:
        async def hybrid(self, query, filters, top_k):
            # Failure injection: stale metadata loses acl_policy_id and score is invalid.
            return [Passage(id="p1", score=1.5, text="x", source_id="doc1", acl_policy_id="")]

    class FakeReranker:
        async def top(self, question, candidates, k):
            return list(candidates)

    class FakePolicy:
        def check(self, question, passages):
            raise AssertionError("policy should not run when metadata is invalid")

    class FakeModel:
        async def answer(self, question, passages, require_citations):
            raise AssertionError("model should not run when metadata is invalid")

    deps = Dependencies(
        identity=FakeIdentity(),
        search=FakeSearch(),
        reranker=FakeReranker(),
        policy=FakePolicy(),
        grounded_model=FakeModel(),
    )

    with pytest.raises(ValueError, match="invalid passage metadata|invalid passage score"):
        await answer(User(id="u1"), "where is the policy?", deps)
```

The first test is the contract test. It asserts that a permitted user reaches hybrid search with the authorization filter intact, then passes through reranking, policy, and model generation, and that the model response includes structurally valid citations. The key point is not pytest syntax; it is the contract: permission-aware retrieval happens before generation, and the output must remain citation-bearing and typed.

The second test is the failure-injection test. It simulates a stale or malformed passage, which is exactly the kind of edge case that causes permission or freshness bugs in real systems. The expected behavior is fail-closed: the function raises before policy or model execution. That proves the code protects the highest-risk boundary instead of hoping downstream services are perfect.

### What makes this a strong FDE answer

This is the point where an interviewer sees the difference between a systems thinker and a slide-deck thinker. A strong FDE answer does not stop at "we use RAG." It shows how state changes, how contracts prevent ambiguity, how retrieval is restricted before generation, and how code proves the safest part of the design first.

That is also the job-market signal. An FDE is expected to move from architecture into production-grade implementation details without losing the customer goal. In this case the goal is not "an AI assistant." The goal is grounded answers with citations while preserving source-system permissions and freshness. Concrete records, explicit contracts, typed validation, and a fail-closed retrieval path are what make that claim believable.

A good closing sentence in the interview is: the system is credible because every write boundary is idempotent or versioned, every read boundary is permission-aware, every model output must pass typed policy checks before a user ever sees it, and the implementation is small enough to test the highest-risk path directly.

---

## 6. Security, Reliability, and Failure Handling

**Key Points**
- Threat model first, not last: the security boundary is identity and authorization sitting in front of retrieval, indexing, logging, and fallback behavior — not the prompt.
- Separate four questions: what may be retrieved, what may be shown to the model, what may be logged, what may be returned when a dependency fails.
- Defense in depth = least privilege + blast radius containment + explicit fail-open/fail-closed policy per component.
- Treat retrieved content as untrusted evidence, never as instructions — defend against prompt injection embedded in tickets or wikis.
- A named failure drill (missed deletion) proves you can contain, preserve evidence, and reconcile — not just list components.

### Threat model first, not last

The hidden trap in this design is that the assistant is not just reading text; it is acting on behalf of a user who may not be allowed to see every source the model can technically reach. That means the security boundary is not the prompt. It is the identity and authorization layer that sits in front of retrieval, indexing, logging, and fallback behavior.

A strong design answer starts by separating four questions:

- What may be retrieved?
- What may be shown to the model?
- What may be emitted to logs and traces?
- What may be returned to the user if a dependency fails?

That separation is defense in depth. Least privilege means the assistant should fetch only content the current user can actually open in the source system, not merely content that is nearby in semantic space. Blast radius means a fault should be limited by tenant, region, workflow, and dependency so one bad connector or bad index does not expose or corrupt the whole enterprise corpus. Failure policy means each stage explicitly chooses whether to fail closed, degrade, queue, or escalate.

### The security controls that matter in this system

First, filter by effective permissions before content reaches the model. If a user cannot open a board folder in the source system, those chunks never enter retrieval candidates for that request. Do not rely on the model to "ignore" forbidden text after it has already seen it.

Second, propagate revocations and deletions to every index and cache. A document removal, ACL change, or ticket purge must fan out to the search index, vector index, permission cache, citation store, and any response cache. If one layer lags, the safest answer is to treat the record as uncertain and withhold it until reconciliation completes.

Third, redact secrets from traces. Prompt text, retrieved snippets, and tool payloads often contain credentials, tokens, customer data, or incident details. Observability is essential, but raw logs are not a dumping ground. Keep the minimum necessary identifiers, hash or redact sensitive fields, and make sure the trace path cannot become a shadow data lake.

Fourth, defend against instructions embedded in retrieved documents. A support ticket, wiki page, or pasted note may contain text that tries to override the assistant's behavior. The model should treat retrieved content as untrusted evidence, not as instructions. A retrieval layer, prompt template, and output policy should all assume hostile or malformed source text.

### What happens when things go wrong

The failure drill in this chapter is specific: security and operations must handle the case where the connector misses deletion events. The candidate should say three things immediately:

1. **Contain impact.**
2. **Preserve evidence.**
3. **Reconcile from source of truth.**

Containment means marking the affected connector or tenant as suspect, disabling fresh answers that depend on the stale feed if necessary, and preventing new retrievals from using the potentially orphaned chunks. Preserving evidence means keeping immutable audit records of the original source record, the deletion signal, index versions, and the time the assistant last referenced the item. Reconciliation means re-reading the authoritative source, invalidating all dependent embeddings and caches, and replaying the deletion through the indexing pipeline.

### Other required failure modes

Now widen the lens to the other required failures:

| Failure | Detect | Contain | Recover | Prevent |
|---|---|---|---|---|
| ACL cache becomes stale | Source-system version mismatch or periodic authorization sampling | Force live permission checks on sensitive requests | Expire the cache and replay revocation events | Short TTLs, versioned ACL snapshots, negative-cache invalidation |
| Retriever finds semantically similar but irrelevant text | Citations do not support the answer, or answer confidence is low | Lower rank thresholds or require evidence from multiple chunks | Return a grounded refusal or clarification request | Hybrid retrieval, metadata filters, evaluation sets that include near-miss queries |
| Model invents a citation | Validate that every cited document ID exists in the retrieval set and is open to the requester | Strip unsupported citations and force a fallback answer | Return "I can't verify that source" | Structured citation generation and post-generation verification |
| Vector index or model provider is unavailable | Detect with timeouts and health checks | Circuit-break the dependency and limit retries | Queue non-urgent sync jobs or fall back to a narrower search mode | Multi-region redundancy, provider abstraction, and graceful degradation |

### A practical fail-open / fail-closed decision table

| Component | If unavailable or stale | Policy |
|---|---|---|
| Permission check | Fail closed | Better to withhold an answer than expose unauthorized content |
| Source-of-truth deletion sync | Fail closed for affected records | Old content must not silently persist |
| Vector retrieval | Degrade | Use keyword or metadata search if safe |
| Citation validation | Fail closed | Unsupported citations should never be shown |
| Telemetry export | Degrade with redaction | Preserve service health, not raw secrets |
| Background reindexing | Queue | Catch up without blocking user-facing reads |
| Security review gate | Human intervention | Launch should wait if unresolved exposure risk remains |

### Why the design review should preserve evidence

This is where an FDE is judged on production judgment, not only technical fluency. If the system returns a bad answer after a deletion was missed, the team needs to know whether the root cause was connector lag, cache staleness, retrieval policy, or model behavior. That requires durable audit evidence: source event IDs, index version stamps, ACL version stamps, request IDs, and the exact citation set shown to the user.

Before launch, you would want runbooks for deletion reconciliation, stale-permission handling, citation mismatch, model-provider outage, and human escalation. You would also want an explicit rollback path for any rollout that widens retrieval scope or changes authorization semantics.

### Production sketch: one critical invariant

The invariant is simple: a user may only receive citations for documents they are allowed to open at answer time.

```python
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class Document:
    document_id: str
    title: str
    allowed_users: frozenset[str]

    def can_open(self, user: str) -> bool:
        return user in self.allowed_users


@dataclass(frozen=True)
class Answer:
    text: str
    document_ids: List[str]
    citations: List[Document]


class PermissionError(RuntimeError):
    pass


class KnowledgeAssistant:
    def __init__(self, documents: Iterable[Document]):
        self._documents = list(documents)

    async def query(self, as_user: str, text: str) -> Answer:
        # Interview-scale sketch: retrieval, ranking, generation, and citation validation
        # are simplified here. In production, retrieval would be permission-filtered first,
        # and every citation would be rechecked against the live authorization source.
        visible = [doc for doc in self._documents if doc.can_open(as_user)]
        if not visible:
            raise PermissionError(f"{as_user} has no accessible sources")

        cited = visible[:2]
        answer_text = f"Grounded answer for: {text}"
        return Answer(
            text=answer_text,
            document_ids=[doc.document_id for doc in cited],
            citations=cited,
        )


# Minimal self-contained harness so the invariant test is runnable as written.
class _Client:
    def __init__(self) -> None:
        self._assistant = KnowledgeAssistant(
            documents=[
                Document("board-only", "Board forecast", frozenset({"executive", "board-member"})),
                Document("finance-public", "Finance FAQ", frozenset({"finance-intern", "finance-analyst"})),
            ]
        )

    async def query(self, as_user: str, text: str) -> Answer:
        return await self._assistant.query(as_user=as_user, text=text)


client = _Client()


async def test_acl_is_enforced():
    answer = await client.query(as_user="finance-intern", text="Board forecast?")
    assert "board-only" not in answer.document_ids
    assert all(doc.can_open("finance-intern") for doc in answer.citations)
```

The teaching warning here is deliberate: this is an interview-sized sketch, not a complete service. A production version would add request validation, structured logging with redaction, cancellation timeouts, retries only for safe operations, idempotency keys for sync jobs, circuit breakers around the model and vector store, and tests that simulate stale ACLs and deletion replay. The companion test encodes the core security invariant, proving that the most important safety property is enforced before generation, not after the model has already spoken.

### What to say in the interview

If I had 90 seconds, I would say: the assistant is permission-aware before retrieval, revocation-aware across every cache and index, trace-safe through redaction, and hostile-document aware through instruction filtering. If the connector misses deletion events, the system contains the blast radius by tenant and dependency, preserves audit evidence, and replays from the source of truth. The riskiest trade-off is between availability and authorization strictness; for sensitive data, we fail closed on permissions and citations, degrade on retrieval quality, and queue background repair work. The first production rollout gate is a successful deletion-reconciliation drill with verified audit evidence and no unauthorized citation leakage.

---

## 7. Delivery Plan, Observability, and Business Impact

**Key Points**
- The prototype answering questions is not the finish line — the customer question that matters is "when can we trust this in production?"
- A staged rollout (one corpus → access-leakage test suite → silent evaluation → source-by-source expansion) beats a big-bang launch.
- Metrics must be layered — technical health, model quality, adoption, business outcome — so no single number gets over-optimized.
- A risk register with owner/mitigation/trigger per failure mode makes failure actionable, not folklore.
- Success is measured by workflow change, not demo polish: fewer tickets, faster resolution, permission boundaries holding under load.

### From prototype to production without a trust cliff

The prototype works, but the customer asks the only question that matters: when can we trust this in production? That is the FDE pivot point. At this stage, the job is no longer to prove the assistant can answer; it is to prove it can be rolled out safely, measured honestly, and operated by a team that does not need the original builders in the room every time something drifts.

The cleanest path is a staged rollout with explicit owners and exit criteria. Start with one low-risk corpus: for example, a public internal wiki or a narrow policy set that is important enough to matter but not sensitive enough to make every mistake catastrophic. The goal of this first phase is not broad utility; it is to validate ingestion, retrieval, citation formatting, and support workflows in a controlled environment.

Next, build an access-leakage test suite. This is not a single test but a repeatable harness that asks the assistant questions from the perspective of users with different roles and then checks whether the retrieved documents, citations, and final answers respect source permissions. The suite should cover obvious forbidden queries, indirect phrasing, stale ACLs, deleted documents, and cross-tenant edge cases. The exit criterion is simple: if the system ever exposes a document, citation, or paraphrase that the test user should not see, the release does not advance.

```mermaid
flowchart LR
    S1["1. One low-risk corpus"] --> G1{Access-leakage<br/>test suite}
    G1 -->|Pass| S2["2. Silent evaluation<br/>vs. real traffic"]
    G1 -->|Fail: exposure found| S1
    S2 --> G2{Grounded rate + latency<br/>acceptable?}
    G2 -->|Pass| S3["3. Source-by-source<br/>expansion"]
    G2 -->|Fail| S2
    S3 --> S4["4. Full rollout with<br/>per-source freshness dashboards"]
```

A compact sequence view helps make that rollout concrete. In the happy path, a user asks a question, the assistant authenticates the user, retrieves only permitted sources, generates a grounded answer with citations, and logs the interaction for evaluation. In the failure path that matters most here, a connector misses deletion events, the freshness dashboard flags a mismatch, the reconciliation job detects a stale document, and the rollout is paused before the bad state can reach a broader audience.

After that, run silent evaluation before broad release. In silent mode, real employee questions are sent through the retrieval and answer pipeline, but the user still receives the current manual or legacy workflow. This is where the team learns what people actually ask, how often the system would have had a grounded answer, where citations fail, and whether the latency profile is acceptable under real load. It also catches the embarrassing gap between a demo dataset and the messy distribution of live enterprise questions.

Only then expand source by source, adding Drive, SharePoint, Slack, wikis, and support tickets in sequence, not all at once. Each new source gets its own freshness dashboard, reconciliation rules, owner, and rollback trigger. That source-by-source approach keeps one bad connector from defining the whole product. It also makes the operational story legible: when a source drifts, you know who owns it, what changed, and how to pause it without shutting down the assistant entirely.

### The metric stack that tells the truth

A good dashboard separates technical health, model quality, adoption, and business outcome. If those layers are blended together, people will optimize the wrong thing.

**Technical health**
- **Freshness lag:** how long it takes a change in a source system to become searchable in retrieval. Calculate it as the elapsed time between a source update event and successful availability in retrieval. The source is connector telemetry plus the index update timestamp. The owner is the ingestion or platform team. The alert threshold should be tight enough to catch connector degradation early, especially for systems where policy changes or deletions matter.
- **p95 latency:** the 95th percentile end-to-end answer time from user request to final response. Measure it from request ingress to answer delivery, including retrieval and generation. The owner is the application platform team. If p95 spikes, users feel it immediately, even if average latency looks fine.
- **Cost per answered query:** total inference, retrieval, and infrastructure cost divided by the number of queries that produced a usable answer. The owner is the product or platform lead with finance visibility. This metric keeps the team honest about over-retrieval, verbose prompting, and unnecessary re-ranking.

**Model quality**
- **Grounded answer rate:** the share of answers that are supported by retrieved sources and do not require unsupported inference. Use a labeled evaluation set from silent mode plus sampled production traffic. The owner is the ML or evaluation lead. It should be watched over time, not treated as a one-time launch gate. A practical alert threshold is a sustained drop of more than 5 percentage points from the agreed baseline, or any step change that cannot be explained by a controlled release.
- **Citation precision and recall:** precision asks whether cited sources are actually relevant and support the answer; recall asks whether the answer used the right sources among those available. Use human or expert review on a sampled set of responses. The owner is the evaluation or QA lead. A practical launch gate is precision above the agreed bar on the evaluation set and no unexplained decline of more than 5 percentage points in either precision or recall relative to the pre-launch baseline. A high answer rate with weak citation precision is not enough in an enterprise setting.
- **Permission leakage count:** the number of confirmed cases where a user saw content, metadata, or a citation they were not authorized to access. The owner is security or trust engineering. The threshold is effectively zero for launch decisions, and any confirmed case should trigger a rollback review.

**Adoption**
- **Weekly active users:** the count of distinct employees who used the assistant in a given week. The owner is the product manager. This tells you whether the system has moved from novelty to habit. A practical alert threshold is a sustained week-over-week decline of more than 20 percent, or flat usage after a broader launch was expected.

**Business outcome**
Adoption alone is not impact. The assistant matters only if it changes the workflow: fewer repeated helpdesk tickets, faster policy lookup, less time spent hunting across systems, and fewer escalation loops. The business-outcome metric should be tied to the customer's stated objective, not to model vanity. If the goal is employee self-service, then the proof is reduced time-to-answer and improved resolution rates in the supported workflow.

### Example scorecard and risk register

A practical scorecard might list: grounded answer rate, citation precision and recall, permission leakage count, freshness lag, p95 latency, cost per answered query, and weekly active users. The point is not to track everything forever; it is to build a narrow, interpretable set of measurements that can explain why the rollout is safe, useful, or blocked.

| Risk | Owner | Mitigation | Trigger |
|---|---|---|---|
| Connector misses deletion events | Ingestion lead | Periodic reconciliation and deletion replay tests | Stale document appears in access-leakage test or freshness dashboard shows divergence |
| Citation quality drops after a retrieval tuning change | ML lead | Holdout evaluation and canary comparisons | Precision falls below the agreed threshold on sampled traffic |

A matching risk register should name the owner, mitigation, and trigger for each major failure mode. The point of the register is not paperwork; it is to make failure actionable before the system becomes folklore.

### What operations actually needs to own

The rollout plan should specify canary, rollback, migration, training, support, and documentation before the first broad release. Canarying means a small user segment or one region sees the new behavior first. Rollback means the team can revert to a prior model, retrieval configuration, or connector state without manual heroics. Migration means source onboarding follows a repeatable adapter pattern rather than a one-off script. Training means support and internal champions know how to explain citations, report bad answers, and recognize permission-related issues. Documentation means there is a stable playbook for ingestion, access control, incident triage, and source-specific quirks.

Ownership should be explicit: product owns user outcomes and prioritization; platform owns uptime and latency; ML or search owns retrieval quality; security owns permission leakage review; source-system integrators own connector health; support owns frontline intake. If an FDE cannot name the owner of a metric or the owner of a rollback, the design is still fragile.

### What becomes a product, what stays a configuration, and what remains an adapter

An FDE also has to decide what should be reusable. The core product should include the permission-aware query path, citation rendering, logging, evaluation hooks, and rollback controls. Source-specific auth flows, field mappings, and transformation quirks should stay in adapters. Per-customer ranking rules, source priority, retention windows, and corpus inclusion lists are usually configuration. Anything that must be repeated for every new enterprise should be pushed toward a shared service or platform primitive; anything that exists because of one integration should not become hard-coded into the core.

That boundary matters because it determines whether the pilot stays a bespoke engagement or becomes leverage. If every new source requires custom logic in the answer path, operational cost grows with adoption. If the product has a clean adapter interface and a common observability layer, new corpora can be added without rewriting the trust model.

### What success looks like after launch

The system is successful only when users adopt it, the workflow improves, and the operating team can support it without constant escalation. That means a real business outcome, not just a technically impressive demo: employees can find grounded answers with citations, permission boundaries hold, stale content is visible quickly, and the support team has dashboards and runbooks instead of guesswork. For an FDE, that is the delivery story the interview is really testing: can you turn a strong prototype into a measured, owned, incrementally expanding service that earns trust and keeps it?

### 90-second interview summary

"I would roll this out in four phases: one low-risk corpus, an access-leakage test suite, silent evaluation, and then source-by-source expansion with freshness dashboards. I would track grounded answer rate, citation precision and recall, permission leakage count, freshness lag, p95 latency, cost per answered query, and weekly active users, with separate dashboards for technical health, model quality, adoption, and business outcome. The riskiest trade-off is availability versus authorization strictness, so we fail closed on permissions, gate expansion on leakage tests, and use rollback and reconciliation drills before broad release. The first production gate is a successful deletion-reconciliation and access-leakage drill with no unauthorized citation leakage and clear audit evidence. That is how I would prove the assistant is not just accurate in a demo, but supportable and valuable in production."

---

## 8. Interview Walkthrough, Trade-Offs, and Practice

**Key Points**
- Lead with outcome and risk in the opening 30 seconds — the interviewer decides where you'll spend your time based on this.
- Spend time in proportion to risk, not diagram size — authorization and freshness deserve more minutes than embeddings.
- Four trade-offs you must be able to defend, both ways, with a balanced verdict — not a one-sided pitch.
- Repair patterns exist for the most common weak answers — know them before you say the weak version out loud.
- Score yourself on discovery, estimation, architecture, depth, security, delivery, and communication — not just "did it work."

### Minute-zero move: lead with outcome, not architecture

In a 45–60 minute interview, the fastest way to sound senior is to start from the business result and the risk model, then earn the right to draw boxes. Open with the customer outcome in one sentence: the assistant must deliver grounded answers with source citations while preserving source-system permissions and freshness. Then immediately say what could break the design: unauthorized disclosure, stale results, and low trust in citations. That opening does two things. It shows you understand the job-to-be-done, and it tells the interviewer where you will spend your time.

A strong opening sounds like this: "I'll assume we need a multinational enterprise assistant over Drive, SharePoint, Slack, wikis, and tickets. My default design is permission-aware retrieval with citations, but I want to confirm whether the bigger risk is leak prevention, freshness, or cost, because that changes how much I invest in real-time sync, ACL enforcement, and evaluation." That is assumption management in practice: state the default, name the uncertainty, invite redirection.

### A practical 50-minute answer plan

Use time in proportion to risk, not diagram size. If you spend twenty minutes on embeddings and one minute on permissions, you have probably optimized for the wrong thing. A useful pacing model is:

- **0–5 minutes: discovery.** Clarify users, corpora, permission model, freshness needs, latency target, and whether answers need citations for every claim or only for high-risk domains.
- **5–10 minutes: success criteria and non-goals.** Define what "good" means: grounded answers, no unauthorized passage exposure, acceptable lag, measurable adoption, and supportable operations.
- **10–18 minutes: scale and data flow.** Estimate corpus size at a coarse level, identify ingestion sources, and separate real-time updates from batch backfills.
- **18–30 minutes: core architecture.** Walk through ingestion, parsing, chunking, embedding, retrieval, permission filtering, answer generation, citation assembly, and logging.
- **30–38 minutes: trade-offs and failure modes.** Compare retrieval strategies, ACL strategies, sync strategies, and context-window choices.
- **38–45 minutes: security, reliability, and observability.** Cover deletion events, group changes, retries, auditability, and what you would monitor.
- **45–50 minutes: close with rollout plan and risks.** State the first gate, the biggest residual risk, and the next production step.

If the interviewer asks for more depth, spend it where the stakes are highest: authorization, freshness, and failure recovery. If they care about product leverage, talk about reuse across departments and source connectors. If they care about infra, talk about indexing cadence, query fanout, and observability.

### The main trade-offs you should defend

**1. Hybrid retrieval versus vector-only retrieval.** A vector-only system is tempting because it is simple: embed the documents, search semantically, and hand the top passages to the model. The problem is that enterprise questions are not always pure semantic matches. Users ask with acronyms, exact product names, policy IDs, ticket numbers, and formulaic wording that dense retrieval may blur. Hybrid retrieval combines lexical search with vector search, often with reranking, so exact terms and semantic similarity can both contribute. The balanced answer is not "hybrid is always better." It is: hybrid usually gives better recall and better resilience to odd enterprise language, but it adds tuning complexity and another failure surface. If the corpus is small and the language is clean, vector-only may be enough for a first pilot. If the corpus is heterogeneous or policy-heavy, hybrid is safer because missing the right passage is worse than carrying a little extra retrieval complexity. In an FDE interview, make the trade-off explicit: higher engineering complexity in exchange for better coverage and fewer silent misses.

```mermaid
flowchart TD
    Q1{Corpus is small<br/>and language is clean?}
    Q1 -->|Yes| V[Vector-only may suffice for a first pilot]
    Q1 -->|No — heterogeneous, policy-heavy| H[Hybrid: lexical + vector + reranking]
    H --> R[Better recall, fewer silent misses,<br/>more tuning complexity + another failure surface]
```

**2. Query-time ACL checks versus precomputed ACL expansion.** This is the most important security trade-off in the whole design. Query-time ACL checks mean you retrieve candidate passages and filter them against the requester's current permissions at read time. Precomputed ACL expansion means you materialize permission-aware indexes or document variants ahead of time so queries can run faster. Query-time checking is the cleaner default because it uses the freshest identity state and reduces the chance that a stale permission snapshot leaks content. It also keeps the access decision close to the request. The downside is latency and system complexity, especially if many sources have different authorization models. Precomputed expansion can reduce query latency, but it increases reprocessing cost, storage, and the chance of stale permissions if memberships change. It also complicates revocation, which is exactly the kind of edge case interviewers like to probe. A strong answer is: use query-time ACL checks as the primary control, then selectively precompute only where source permissions are stable, well-modeled, and performance requires it. That way you do not let a performance optimization quietly become a security policy.

```mermaid
flowchart TD
    Q["Where to enforce permissions?"] --> QT["Query-time ACL check<br/>(default)"]
    Q --> PC["Precomputed ACL expansion<br/>(selective)"]
    QT --> QTp["+ Freshest identity state<br/>+ Access decision stays close to request"]
    QT --> QTc["- Adds latency/complexity<br/>across heterogeneous auth models"]
    PC --> PCp["+ Faster queries"]
    PC --> PCc["- Reprocessing cost, storage,<br/>stale-on-revocation risk"]
    QTc --> Verdict["Verdict: query-time as the primary control;<br/>precompute only where permissions are stable + perf-critical"]
    PCc --> Verdict
```

**3. Larger context versus cost and distraction.** The obvious instinct is to stuff as much evidence as possible into the prompt. That can help the model synthesize across documents, but large context creates two problems: cost rises with every token, and the more subtle issue is that the model may overfit to irrelevant passages, especially if the retriever is noisy. In enterprise knowledge work, more context is not automatically better context. The practical position is to keep the candidate set tight, prefer high-precision retrieval, and use citations to expose provenance rather than rely on brute-force prompt stuffing. If the answer needs synthesis across multiple sources, increase context only as far as needed for that task. The interviewer is looking for evidence that you understand the difference between "more evidence" and "more useful evidence."

**4. Real-time sync versus scheduled indexing.** Real-time sync improves freshness, which matters when policy, tickets, or support guidance change quickly. Scheduled indexing is easier to operate, cheaper, and often good enough for wikis or slower-moving repositories. The right answer is usually mixed: incremental or event-driven updates for high-churn sources, scheduled re-indexing for stable collections, and periodic reconciliation jobs to catch missed events. The risk is that real-time pipelines are more fragile, especially across many SaaS connectors, while scheduled indexing risks stale answers. For interview purposes, frame this as a service-level decision, not a purely technical preference. Ask what freshness actually means for the customer: minutes, hours, or same-day. Then design to that tolerance.

### Minute-by-minute walkthrough of a strong interview

- **Minute 0–3: clarify the user and the failure mode.** Ask which employees use the assistant, what kinds of questions they ask, and whether the biggest concern is leakage, incorrect answers, or stale answers. State that you will optimize for permission safety and grounded citations.
- **Minute 3–8: define the operating constraints.** Ask about source systems, document volume, update rate, permission model, geography, and whether answers need to cite only internal documents or also external references. State any assumptions clearly: for example, "I'll assume standard enterprise identity groups and that source APIs support incremental sync."
- **Minute 8–15: estimate and bound the system.** You do not need precise numbers; you need enough scale to choose architecture. Identify which corpora dominate traffic, which are most sensitive, and which change most often. That tells you where to spend complexity.
- **Minute 15–25: draw the data flow.** Ingest from each source, normalize documents, extract metadata, chunk carefully, store raw text and embeddings separately, and attach security labels. At query time, authenticate the user, resolve effective permissions, retrieve candidates, filter by authorization, rerank if needed, generate an answer, and attach citations.
- **Minute 25–32: explain the trust boundary.** Make it obvious where raw data is stored, where permissions are checked, and which services can see sensitive content. If the interviewer challenges you, describe how you would avoid passing unauthorized passages into the model context at all.
- **Minute 32–40: cover failure modes.** Talk through deletion events, stale groups, duplicate documents, connector outages, and corrupted chunks. State what happens when the system is unsure: fail closed on permissions, degrade to no-answer rather than fabricate when freshness is material.
- **Minute 40–46: discuss rollout and measurement.** Begin with one corpus, one or two use cases, and a small set of users. Measure grounded answer quality, citation precision, leakage tests, freshness lag, latency, and support burden. Add corpora only after the system proves stable.
- **Minute 46–50: close succinctly.** Summarize the design in one pass, name the hardest trade-off, and state the next gate.

### Strong answers to likely follow-up questions

**"How do you prove users never see a passage they cannot open?"** You prove it by design and by test, not by confidence. Design-wise, the authorization decision should happen before a passage can enter the model context or the final response. The effective permissions for the requesting identity must be resolved at query time, and every candidate passage must carry the source object's access metadata. If a passage is not allowed, it is excluded before generation. If the model outputs a citation that is not permitted, the response should be rejected or rewritten. Then test the invariant aggressively. Build a regression suite with known-denied documents, user identities with changing group membership, and adversarial queries that try to coax hidden content. Verify that the retrieval layer, reranker, answer assembler, and citation renderer all respect the same policy. The key interview phrase is: "I would not rely on prompt instructions to enforce access control; access control must be enforced in the application and retrieval layers."

**"How do you handle group membership changing during a session?"** Treat permissions as dynamic, not session-static, with a user's rights resolved against the current identity state, using short-lived caches and explicit invalidation when the identity provider reports changes. If a user loses access mid-session, the next retrieval must see the new state. If a user gains access, they can benefit on the next query after reconciliation. The nuance is cache design: you want enough caching to avoid hammering identity systems, but not so much that the assistant serves stale permissions for long. A good answer is to cache permission resolutions briefly, version the identity snapshot, and revoke on change events when the source supports it. If revocation signals are delayed, bound the maximum stale window and state it explicitly.

**"How do you re-index after changing chunking?"** Changing chunking changes retrieval behavior, so treat it as a versioned migration. Keep the old and new chunking schemes side by side during backfill, re-embed the corpus under a new index version, and run offline evaluation before cutover. If the new chunking improves recall but harms precision, you may need to revise chunk size, overlap, or reranking rather than just shipping the change. Operationally, expose index version in metadata, route a small percentage of traffic to the new version, compare answer quality and leakage tests, and maintain rollback. The important interview point is that re-chunking is not a silent maintenance task; it is a retrieval-model change and should be treated like one.

**"How do you debug a bad answer without storing the prompt?"** Store structured traces, not raw prompts. Keep the user question type, retrieval candidates, document IDs, permission decision, reranker scores, model version, prompt template version, citation set, and response outcome. If you need more detail, store an obfuscated or redacted prompt fingerprint, not the full user content, unless policy and consent allow more. This gives you enough observability to answer the real debugging questions: Did retrieval miss the right source? Did permissions filter too aggressively? Did the model ignore the evidence? Did the prompt template change? In enterprise settings, traceability often matters more than raw prompt retention, because prompt retention itself can create privacy and security problems.

### Common weak answers and how to repair them

- **Weak:** "I'd just use vector search because it's modern." **Repair:** Explain why hybrid search better handles exact terms, policy IDs, and noisy enterprise language.
- **Weak:** "Permissions are handled by the database." **Repair:** Separate storage permissions from retrieval-time authorization and explain effective identity resolution.
- **Weak:** "I'd store the whole prompt for debugging." **Repair:** Replace raw prompt storage with structured traces, redaction, and versioned metadata.
- **Weak:** "Real-time sync everywhere." **Repair:** Use a mixed strategy based on freshness needs and connector reliability.
- **Weak:** "More context will solve it." **Repair:** Discuss precision, cost, distraction, and the need to keep candidate sets tight.
- **Weak:** "If the model is confident, it's probably right." **Repair:** Tie confidence to evidence quality, citations, and retrieval coverage, not to model tone.

### Scoring rubric you can use on yourself

- **Discovery:** Did you identify the business outcome, user types, data sources, and permission constraints early?
- **Estimation:** Did you make reasonable scale assumptions and use them to test feasibility?
- **Architecture:** Did you propose a design that is replayable, observable, and safe to operate?
- **Depth:** Can you explain batch sizing, skew handling, retries, and publish gates in detail?
- **Security:** Did you treat credentials, data access, and output handling as part of the design, not an afterthought?
- **Delivery:** Did you understand rollout, monitoring, and what to do when the batch is behind schedule?
- **Communication:** Did you stay structured, concise, and willing to revise assumptions when challenged?

If the candidate only scores high on architecture and low on delivery or communication, the answer may be technically clever but not interview-strong for an FDE role. FDE work is customer-facing and operationally grounded; the interview should reflect that.

### Practice plan before the interview

For solo practice, do a timed 50-minute dry run and record yourself answering from the opening sentence to the closing summary. Watch for two failure modes: over-talking early, and hiding assumptions. For a pair mock, have your partner interrupt you with one security challenge and one freshness challenge; practice recovering without losing structure. For implementation practice, rebuild the retrieval-and-filtering flow from memory and then add one failure case: a deleted document, a changed group membership, or a re-chunking migration. The point is not to memorize a script. The point is to build a repeatable way to think, so you can defend the design live.

### The interview posture to carry forward

The best FDE candidates do three things at once: they speak in outcomes, they surface trade-offs honestly, and they control the conversation with structure. If you can say, "I'll optimize for grounded answers, permission safety, and freshness; I'll choose hybrid retrieval unless the corpus is trivial; I'll enforce ACLs at query time; I'll mix real-time sync with scheduled reconciliation; and I'll prove it with leakage tests and rollout gates," you are already speaking the language of a strong customer-facing systems designer. That is what this interview is really measuring.

---

## Coverage Notes (self-review against the decomposition rubric)

Two review passes ran against the 20-item, 4-phase decomposition rubric before finalizing this tutorial. Pass 2 found no additional gaps the source chapter could close, so the loop stopped early (max allowed was 3).

**Fully covered (16 of 20):** feature→outcome reframing, stakeholder mapping, clarifying questions, requirements + MoSCoW prioritization, explicit non-goals, back-of-envelope scale math, unit economics, end-to-end architecture, data model & API contracts, named trade-off pairs, threat model & fail-open/closed policy, failure-mode drills, contract + failure-injection testing, layered evaluation metrics, phased rollout & risk register, and the structured communication/self-scoring rubric.

**Left Partial or Absent — genuinely not designed in the source, not fabricated here:**

- **Build-vs-buy / vendor & model-selection trade-offs — Absent.** The chapter deliberately stays vendor-agnostic ("the customer does not buy containers; they buy confidence"), so no comparison of managed vs. self-hosted retrieval infrastructure or proprietary vs. open-weight model choice exists in the source to reproduce.
- **Regulatory / data-governance depth — Partial.** Residency and retention appear only as a discovery question and a config knob (retention windows); there's no designed answer for cross-region residency or right-to-erasure through derived embeddings.
- **Responsible-AI framing beyond hallucination — Partial.** Grounding, citations, and abstention address factuality well, but the source doesn't address retrieval bias or equitable answer quality across departments/languages.
- **Change-management / adoption narrative — Partial.** Training and documentation are named as operational owners, but there's no executive-facing adoption narrative for winning over a skeptical team.

If you're using this tutorial for a live interview, treat these four as the layer you add in your own words rather than reading them as oversights in the source material.
