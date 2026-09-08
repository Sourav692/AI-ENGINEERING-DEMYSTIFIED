# What each role is actually tested on

Three roles, one overlapping core. The shared core goes in section 1 of the
tutorial and is written once. These per-role notes drive section 5, where the same
underlying concept gets probed from a different angle.

The distinction that matters: **Applied AI Engineers are asked whether the output
is good. Agentic AI Engineers are asked whether the loop terminates. FDEs are
asked whether it survives contact with a customer.**

---

## Applied AI / AI Engineer

**The job**: make a model-backed feature work well and keep it working. Retrieval
quality, output reliability, evaluation, cost and latency.

**What they probe**

| Area | The question behind the question |
|---|---|
| RAG quality | Can you diagnose *where* retrieval failed — chunking, embedding, ranking, or the prompt? |
| Chunking | Do you know why chunk size is a recall-precision dial, not a config default? |
| Hybrid search & reranking | Do you know when dense retrieval alone is not enough, and what a reranker costs? |
| Evaluation | Can you build an offline eval set and defend it? Do you know LLM-as-judge's failure modes? |
| Structured output | Do you know why schema-constrained decoding beats parsing free text, and where it still breaks? |
| Cost & latency | Can you reason about tokens, batching, caching and model tiering with real numbers? |
| Prompting vs RAG vs fine-tuning | Can you pick between them and say what evidence would change your mind? |

**Signature question shapes**
- "Your RAG system returns confident wrong answers. Walk me through debugging it."
- "How do you know your retriever got better after a change?"
- "Your p95 latency doubled after adding reranking. What do you do?"
- "When would you *not* use RAG?"

**Red flags**: treating cosine similarity as truth; no eval set; "we just use
GPT-4o for everything"; cannot say what recall@k means for their system.

---

## Agentic AI Engineer

**The job**: design loops that terminate, tools that fail safely, and state that
survives. Autonomy is the feature and the liability.

**What they probe**

| Area | The question behind the question |
|---|---|
| Topology choice | Workflow vs single agent vs multi-agent — can you justify the *least* autonomous option that works? |
| Tool design | Do your tool schemas and errors teach the model to recover, or just fail? |
| Termination | What stops an agent that never decides it is done? Call caps, budgets, timeouts. |
| State & memory | Short-term vs long-term, what gets checkpointed, what a thread means, when to summarize. |
| Human-in-the-loop | Where do you interrupt, and how does the run resume without re-executing side effects? |
| Failure containment | Retries, fallbacks, idempotency, partial failure in a fan-out. |
| Observability | Can you debug a bad run from a trace? What do you log per step? |
| Determinism | What did you make deterministic on purpose, and why there? |

**Signature question shapes**
- "Your agent loops forever on 3% of requests. Diagnose and fix."
- "Design an agent that books travel. Where does a human approve?"
- "One worker in your fan-out fails. What happens to the other nine?"
- "How do you stop a tool from being called twice after a resume?"
- "When is multi-agent actively worse than one agent?"

**Red flags**: no call cap; treating the model as the error handler; multi-agent as
a default rather than a last resort; no answer for resuming after an interrupt.

---

## Forward Deployed Engineer (FDE)

**The job**: get a working system into a specific customer's environment, fast,
then keep it alive while talking to the people who depend on it. Half engineering,
half judgment under a customer's constraints.

**What they probe**

| Area | The question behind the question |
|---|---|
| Scoping | Can you turn a vague customer ask into the smallest demonstrable slice? |
| Time-to-demo | Can you ship something real this week, knowing what you deliberately faked? |
| Integration | Their data, their auth, their VPC, their compliance. Can you work inside constraints you did not choose? |
| Debugging in prod | No repro, an unhappy customer, partial logs. What is your order of operations? |
| Evaluation with their data | Can you build an eval from the customer's examples rather than a public benchmark? |
| Cost conversations | Can you explain the bill and where it goes, to a non-engineer? |
| Security & tenancy | PII, data residency, tenant isolation, what leaves their network. |
| Communication | Can you say "that will not work, here is what will" and keep the room? |

**Signature question shapes**
- "The customer wants an agent over their 40 GB of Confluence. First two weeks?"
- "It works in your demo and fails on their data. What is different, and how do you find out?"
- "The customer asks for 99% accuracy. How do you respond?"
- "They cannot send data to OpenAI. Now what?"
- "Walk me through a deployment you owned that went badly."

**Red flags**: no plan for customer-specific evaluation; ignoring data residency;
promising accuracy numbers; building the general solution when the customer needed
one narrow thing next Tuesday.

---

## Weighting the tutorial

The shared core carries most of the value; the role tracks sharpen it.

| Section | Share of tutorial |
|---|---|
| Shared core, gotchas, tradeoffs | ~50% |
| Top 10 real-time agentic system design questions | ~15% |
| Three role tracks | ~25% |
| Mock design + self-check | ~10% |

If the source notebooks lean heavily toward one role — a pure RAG folder, say —
keep all three tracks anyway, but say so in the header and lean the mock design
scenario toward the strongest one.
