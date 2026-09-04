# What RAG Actually Is

> **Level** 🟢 Foundations · **Module** 01 · **Doc** 1 of 5 · **Time** ~20 min
> **Prerequisites:** Module 00
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/01-theory.md` §1–3

## Why this matters

A language model knows what was in its training data. It does not know your company's incident post-mortems, your customer contracts, or the ticket someone filed this morning. Every enterprise AI system you will build in this handbook exists because of that gap, and almost every one closes it the same way.

## The idea in one diagram

**Retrieval-Augmented Generation** is the obvious fix: before answering, go and *find* the relevant documents, paste them into the prompt, and tell the model to answer using only those.

```
  User question
       |
       v
  [ find relevant documents ]      <- retrieval
       |
       v
  [ question + documents -> LLM ]  <- augmented generation
       |
       v
   Answer + citations
```

That is genuinely the whole idea. Everything else in this handbook's RAG material is about making each of those two boxes work properly when the corpus is big, messy, and — crucially — **not everyone is allowed to read all of it**.

Hold onto the two-box picture. When a design conversation gets complicated, the way back is always: *which box are we talking about, and what is going wrong inside it?*

## Why "enterprise" changes the problem

A demo RAG app has one user and one folder of documents. An enterprise has:

| Demo RAG | Enterprise RAG |
|---|---|
| everyone sees everything | every user sees a *different slice* |
| one data source | Confluence + Zendesk + Salesforce + a wiki + contracts |
| wrong answer = mildly annoying | wrong answer = a contractual admission or a leaked salary |
| "it works on my question" | it must work on 10,000 questions, measurably |
| no audit | "prove this user never saw that document" |

The single hardest of those is the first one. Here is the scenario that makes it concrete, and which the rest of the handbook returns to repeatedly:

> A Tier-1 support agent asks: *"Why did Vertex Financial lose data in March, and do they get service credits?"*

The honest answer lives in three documents:

- the **ticket** — the agent may read it
- the **incident post-mortem** — confidential, engineering only
- the **customer contract** — confidential, sales and legal only

So the *correct* answer is different for four different people. Not "the same answer with bits blacked out" — genuinely different answers, from genuinely different evidence:

```
   Same question, four roles:

   Tier 1 agent    ->  "Platform-side backlog. Credits go to the account manager."
   Tier 3 engineer ->  "Cardinality explosion in ws_lmb_eu_077 saturated compaction."
   Account manager ->  "Below 99.5% means a 25% credit under their MSA."
   Contractor      ->  "I can't answer that."
```

**This is the thing to design for.** Access control is not a feature you bolt on after the RAG works. It decides the shape of the whole retrieval path. Module 04 is built around that sentence; for now, notice that the two-box diagram already has a problem: *which* documents the first box is allowed to find depends on who is asking.

## The pipeline, end to end

Two separate flows. They run at completely different times, which matters more than it sounds.

### Ingestion — runs on a schedule

```
 source systems        ┌──────────┐   ┌─────────┐   ┌──────────┐   ┌────────────┐
 (Confluence,   ────>  │  load +  │──>│ validate│──>│  chunk   │──>│  embed +   │──> vector DB
  Zendesk, ...)        │ normalise│   │  ACLs   │   │          │   │   index    │
                       └──────────┘   └─────────┘   └──────────┘   └────────────┘
                            |              |
                     translate the     refuse anything
                     source system's   with no usable
                     permissions       permissions
```

Ingestion is offline. It can be slow, it can be batched, it can be re-run. Its job is to turn documents into searchable, *permission-tagged* chunks. The "validate ACLs" box is not optional decoration: a document whose permissions cannot be determined does not get indexed, because once it is in the index it will be found.

### Query — runs per request

```
  question ──> authorize ──> plan ──> retrieve ──> enforce ──> rerank ──> grade ──> generate ──> verify ──> answer
                  |                       |            |                    |                       |
             who is this?           search only    re-check for          enough to           citations valid?
             what may they          their slice    real, drop the        answer?             grounded?
             read?                                 rest                  else refuse
```

Query is online. It has a latency budget and a user waiting. Two positions in this line are the security property of the entire system:

- **`authorize` sits first.** Before any search happens, the system resolves who is asking and what they may read.
- **`enforce` sits before the model sees anything.** Whatever retrieval returns is re-checked against the full policy before a single token enters the prompt.

Everything between them — plan, retrieve, rerank — is about quality. Everything after — grade, generate, verify — is about honesty. You will build each of these boxes in Module 04. For now, be able to draw this line and say what the two security positions are.

## The vocabulary you now own

| Term | Meaning |
|---|---|
| **Retrieval** | Finding the passages relevant to a question, from a corpus too large to put in the prompt |
| **Augmented generation** | Asking the model to answer *using the retrieved passages*, ideally with citations |
| **Ingestion** | The offline pipeline that turns source documents into indexed, permission-tagged chunks |
| **Chunk** | A passage-sized piece of a document; the unit of retrieval (next document) |
| **Vector database / index** | The store that holds chunk embeddings and answers "nearest chunks to this query" |
| **ACL** | Access-control list — who may read a document; carried from the source system into every chunk |
| **Authorize / enforce** | The two security positions in the query path: resolve permissions first, re-check before generation |

## Interview lens

"Explain RAG" is a warm-up question, and the trap is answering it as one. A strong answer draws the two boxes, then immediately says what changes when the corpus is enterprise-scale and permissioned — because that is the actual question the interviewer is about to ask. The line that carries it:

> *"RAG is retrieve-then-generate. The enterprise problem is that the correct answer is different for different people, so access control has to shape the retrieval path — it can't be bolted on after."*

## Checkpoint

- Draw the two-box diagram and the two-flow pipeline from memory.
- Why do ingestion and query run at different times, and why does that matter?
- Where do `authorize` and `enforce` sit, and what would go wrong if either moved?
- In the Vertex Financial scenario, why is "the same answer with bits blacked out" the wrong mental model?

**Next →** [Chunking, Retrieval and Fusion](02_Chunking_Retrieval_Fusion.md)
