# RAG, Agent & Tool Evaluation — Theory Guide

This is the theory companion to the 14 hands-on notebooks in this folder (`00_Evaluation_Landscape.ipynb` through `14_Capstone_CrewAI_Travel_Planner_Eval.ipynb` — see `README.md` for the full table of contents). The notebooks teach each concept through runnable code; this document teaches the *why* and *what* on its own, so you can read it standalone — to study, to prep for an interview, or to refresh before touching the code again — without spinning up an environment or spending API calls.

Every metric, class name, and framework mentioned here is exactly what the notebooks actually use (`deepeval==4.1.8`, `ragas`, `mlflow.genai.evaluate()`, Arize Phoenix) — this isn't a generic evaluation primer, it's the specific vocabulary this tutorial's code is built on, minus the code.

**How to use this document:** read Part 0 first — it's the map. After that, the parts roughly follow the notebook modules (Part 1 ≈ Module 1, Part 2 ≈ Module 2, etc.), so you can jump to whichever part matches what you're currently working through, or read straight through as a standalone theory pass before ever opening a notebook.

---

## Part 0 — The Evaluation Landscape

### 0.1 The taxonomy: what are you actually evaluating?

"Evaluate the RAG system" or "evaluate the agent" is not one task — it's a stack of narrower questions, each with its own failure modes and its own metrics. Getting the taxonomy straight up front is what stops you from, say, using a retrieval metric to diagnose a generation bug. A faithfulness failure can look identical to a retrieval failure from the outside — the answer is wrong either way — but the fix is completely different.

**By pipeline stage (RAG-specific):**

| Stage | Question it answers | Failure it catches | Example metrics |
|---|---|---|---|
| **Retrieval** | Did we fetch the right chunks? | Retriever returns irrelevant, missing, or badly-ranked context | Precision@K, Recall@K, MRR, nDCG, `ContextualPrecisionMetric`, `ContextualRecallMetric`, `ContextualRelevancyMetric` |
| **Generation (referenceless)** | Given what we retrieved, is the answer grounded and on-topic? | Hallucination on top of correct context; answering a different question than the one asked | `FaithfulnessMetric`, `AnswerRelevancyMetric`, RAGAS Faithfulness |
| **Generation (reference-based)** | Is the answer actually *correct*, against a known-good answer? | Grounded-but-wrong-because-the-context-itself-was-wrong; wording drift from the expected answer | Answer Correctness (custom `GEval`), Answer Semantic Similarity (embeddings) |
| **End-to-end** | Does the whole pipeline, run as a system, hold up against a labeled dataset? | Any of the above, measured in aggregate over many queries instead of one | A synthetic golden dataset + the full metric suite above, batched |

**By behavior (agent-specific):**

| Behavior | Question it answers | Failure it catches | Example metrics |
|---|---|---|---|
| **Tool selection** | Did the agent call the right tools? | Wrong tool, missing tool, tool called when none was needed | `ToolCorrectnessMetric` (reference-based), Tool Selection Accuracy (trace-based, coverage-only) |
| **Argument correctness** | Were the *arguments* passed to each tool correct? | Right tool, malformed or wrong arguments — a failure mode tool-selection checks can't see | `ArgumentCorrectnessMetric`, deterministic schema validation |
| **Trajectory** | Across a multi-step run, was the *sequence* of actions sound? | Redundant calls, wasted steps, no recovery from an error, right destination via a wasteful path | Step-wise Accuracy, Redundant-Call detection, Recovery Rate, fuzzy Trajectory Match |
| **Task completion** | Forget the mechanics — did the agent actually accomplish what the user asked? | Every tool call "correct" in isolation, but a stated constraint (budget, deadline, scope) silently dropped | `TaskCompletionMetric`, End-State Verification, custom `GEval` rubric |
| **Conversational quality** | Across a multi-turn dialogue, does the agent stay relevant, remember prior turns, and stay in its role/safety bounds? | Forgetting earlier context, drifting off-topic turn by turn, giving advice it shouldn't | `TurnRelevancyMetric`, `KnowledgeRetentionMetric`, `ConversationalGEval` |

Notice the shape of the agent-side taxonomy: it goes from **mechanics** (did it call the right tool, with the right arguments) to **process** (was the sequence of steps sound) to **outcome** (did it actually get the job done). A system can pass every mechanics-level check and still fail at the outcome level — that's the whole reason task-completion and end-state verification exist as separate concerns from tool correctness, not a redundant restatement of it.

### 0.2 Reference-based vs. referenceless — the axis that decides your cost

Every metric above falls into one of two camps, and this single distinction drives most of the practical decisions you'll make about *when* to use which metric:

- **Reference-based** metrics compare the system's output against a known-correct answer (`expected_output`, `expected_tools`, a gold trajectory). They're precise and great for regression testing / CI, but **someone has to write and maintain the reference** — which means they don't scale to arbitrary production traffic, only to curated test sets.
- **Referenceless** metrics judge quality *without* a ground truth — typically by checking internal consistency (is the answer grounded in the context that was actually retrieved?) or by using an LLM to judge quality directly against a rubric. They scale to any input with zero labeling cost, at the price of being less precise and dependent on judge-model quality.

**The practical rule:** use reference-based metrics in development and CI, where you control the test set and want a hard pass/fail bar. Use referenceless metrics in production monitoring, where you can't hand-label every real user query but still want a quality signal. Mature setups run **both**, at different points in the lifecycle — not as a choice between them.

### 0.3 LLM-as-judge: what it actually is, and where it actually breaks

Most referenceless metrics (and some reference-based ones, like Answer Correctness) work by asking an LLM to *judge* the output — usually against a structured rubric, sometimes extracting intermediate claims first (faithfulness checks, for example, often decompose the answer into individual factual claims, then check each one against the retrieved context, rather than judging the whole answer as one blob).

This is powerful — it's the only practical way to score open-ended text at all — but it is **not** a free "ground truth oracle," and treating it like one is the single most common mistake in eval work. Watch for:

- **Judge-model choice matters.** A weaker judge model produces noisier, less reliable scores — the judge needs to be at least as capable as the task requires, sometimes more capable than the system being judged.
- **Non-determinism.** Two runs of the same judge on the same input can disagree, especially near the threshold. Treat a single score as a noisy estimate, not an exact number, and set thresholds with that in mind.
- **Prompt/criteria sensitivity.** A vaguely-worded `GEval` criteria string produces a vague, inconsistent judge. The specificity you put into the rubric is the specificity you get back in the judgment.
- **Cost and latency compound.** Every LLM-judged metric is (at least) one extra API call per test case, per metric. A suite of 5 metrics over 500 test cases is 2,500+ judge calls — this is *why* the reference-based-vs-referenceless split matters operationally, not just conceptually.
- **It can be gamed by fluent-but-wrong output.** An LLM judge reads text and reasons about whether it *sounds* right. This is exactly why agent trajectory evaluation and the CrewAI capstone put weight on **end-state / outcome verification** — checking the real system of record directly — as the strongest signal available, precisely because it can't be fooled by a confident sentence that misrepresents what actually happened.

### 0.4 The tooling landscape

Four different tools show up across this material, deliberately, because the source content already used all four and because in practice you'll encounter systems built on each of them. Knowing what each is *for* is more useful than picking a favorite.

| Tool | What it's really for |
|---|---|
| **DeepEval** | A general-purpose metric library — dozens of pre-built metrics (retrieval, generation, tool use, task completion, conversational) plus `GEval` for custom LLM-judge rubrics. Pytest-friendly, good for CI. The primary framework throughout Parts 1–3. |
| **RAGAS** | A RAG-specific metric library, older and narrower in scope than DeepEval but a common default in the RAG ecosystem — worth knowing on its own terms, and useful as a second opinion alongside DeepEval on the same test case. |
| **MLflow (`mlflow.genai.evaluate()`)** | Evaluation as part of an experiment-tracking platform — the same conceptual metrics as DeepEval, but versioned, logged, and comparable across runs the way you'd compare model-training experiments. The right choice if your team already lives in MLflow for everything else. |
| **Arize Phoenix** | Production-grade **tracing** plus an **offline experiment framework** — instrument a live agent, capture every span (tool call, LLM call, retrieval), then run structured evaluators against captured traces and compare prompt/config versions as formal experiments. The heaviest-weight tool here, and the only one built around live tracing rather than one-off test cases. |

None of these are "the right one" in the abstract — DeepEval and RAGAS answer "is this output good," MLflow answers "is this output good, tracked as part of my experiment history," and Phoenix answers "is this output good, and here's the full trace of *how* the system produced it." A mature setup typically uses more than one, for different purposes.

### 0.5 The shape of this material

| Part | Answers | Primary tool(s) |
|---|---|---|
| **0 — Evaluation Landscape** | What kinds of evaluation exist, and how do the tools relate? | — |
| **1 — RAG Evaluation** | Retrieval quality, generation quality (with and without reference), evaluation wired into the pipeline itself, and a full build-then-evaluate capstone | DeepEval, RAGAS |
| **2 — Conversational, Tool & Task Evaluation** | Multi-turn conversational quality, tool-call correctness, task completion — then the same three questions again through MLflow | DeepEval, MLflow |
| **3 — Agent Trajectory Evaluation** | Step-by-step evaluation of a full multi-tool agent run — 9 dimensions, not just the final answer | DeepEval-adjacent, hand-rolled trace metrics |
| **4 — Production Tracing & Experimentation** | How this looks with real tracing infrastructure and a formal offline-experiment framework | Arize Phoenix |
| **5 — Capstone Lessons** | Everything above, applied to a real running multi-agent system | DeepEval |

**If you only have ten minutes:** read 0.1–0.3 above, then Part 2.3 (task completion) and Part 3 (trajectory). Those four ideas — taxonomy, reference-based vs. referenceless, LLM-as-judge caveats, and outcome-vs-mechanics evaluation — generalize to almost any RAG or agent system you'll actually be asked to evaluate, including in an interview.

---

## Part 1 — RAG Evaluation

### 1.1 Deterministic retrieval metrics

These need **no LLM judge and no API call** — just a labeled eval set (query → ground-truth relevant chunk IDs) and arithmetic. They're the cheapest, most reproducible metrics in this whole tutorial, and the right first move whenever you *do* have labeled relevance data.

- **Precision@K** — of the K chunks retrieved, how many are actually relevant? Penalizes noise in the retrieved set.
- **Recall@K** — of all relevant chunks that exist, how many did we find in the top K? Penalizes missed relevant chunks.
- **MRR (Mean Reciprocal Rank)** — 1 / rank of the *first* relevant hit. Use when there's typically one correct/best chunk and you care how early it appears.
- **nDCG (normalized Discounted Cumulative Gain)** — use when relevance is *graded* (not binary) and multiple relevant chunks can coexist; rewards relevant results appearing higher, penalized by how much higher a *more* relevant chunk should have ranked.

**The catch:** all four need **pre-labeled ground truth** (`relevant_ids` / `relevance_grades`). That's what makes them deterministic and cheap, but it's also what limits them to curated eval sets rather than arbitrary production traffic — you can't compute Precision@K on a live user query you have no relevance labels for. That gap is exactly what the LLM-judged retrieval metrics below solve.

### 1.2 LLM-judged retrieval metrics

DeepEval's three **Contextual** metrics answer the same "is retrieval working" question as 1.1, but using an LLM judge instead of hand-labeled IDs — at the cost of the general LLM-as-judge caveats from 0.3.

All three take a `retrieval_context` (the chunks your retriever actually returned) and judge it against the query and/or a reference answer — but each checks a **different failure mode**, which is exactly why DeepEval ships all three rather than one general "is retrieval good" score:

| Metric | Question | Needs `expected_output`? | Catches |
|---|---|---|---|
| **Contextual Precision** | Are the *relevant* chunks ranked *higher* than the irrelevant ones? | Yes | A good chunk buried below noise — same failure Precision@K catches, but without hand-labeled IDs |
| **Contextual Recall** | Does the retrieved context, as a whole, cover everything the expected answer needs? | Yes | Missing information — the retriever found *something*, but not *enough* |
| **Contextual Relevancy** | Of everything retrieved, how much is actually on-topic? | No | Noise/off-topic chunks diluting the context, independent of ranking or completeness |

Precision cares about **order**, Recall cares about **coverage**, Relevancy cares about **signal-to-noise** — a retriever can fail any one of these while passing the other two. Contextual Recall checks against `expected_output`, not `actual_output` — it's asking whether the retriever fetched enough to *support* the full expected answer, independent of whether the generator actually used all of it.

### 1.3 Referenceless generator metrics

These move one step past retrieval: given whatever was retrieved, **is the generated answer any good** — without needing a hand-written reference answer for every query. They're the metrics you can realistically run against live production traffic, because none of them need labeled ground truth.

| Metric | Question | Compares against |
|---|---|---|
| **Answer Relevancy** | Does the answer actually address the question asked? | `input` only |
| **Faithfulness** | Is the answer grounded in what was retrieved, with no hallucinated claims? | `retrieval_context` |
| **Hallucination** | Does the answer align with a trusted ground-truth `context`, regardless of what was retrieved? | a separately-supplied `context` (not `retrieval_context`) |

These three are the most commonly confused metrics in this whole space, because "the answer is wrong" can mean any of them failed. The distinguishing question to ask: an answer can be **faithful but irrelevant** (perfectly grounded in the retrieved context, but doesn't actually answer what was asked), **relevant but unfaithful** (directly addresses the question, but invents facts not in the context), or **faithful to bad context** (accurately reflects retrieved chunks that were themselves wrong — Faithfulness can't catch this; that's what 1.4's reference-based Answer Correctness is for).

**Faithfulness vs. Hallucination — the distinction that actually matters:** Faithfulness checks the answer against `retrieval_context` (whatever *this* query's retriever happened to fetch). Hallucination checks against a separately-supplied `context` — a trusted, curated ground truth, independent of any one query's retrieval. Use Faithfulness to catch a generator that invents things beyond what it was given; use Hallucination when you have an independent, trusted source of truth to check against regardless of what retrieval returned. Also note: `HallucinationMetric`'s score runs in the *opposite* direction from most DeepEval metrics — a **higher** score means **more** hallucination. Always check a new metric's score direction rather than assuming higher is always better.

DeepEval also has a RAGAS binding for Answer Relevancy (`RAGASAnswerRelevancyMetric`), which uses embedding cosine similarity instead of an LLM judge — cheaper and faster, at the cost of missing subtler forms of "technically similar wording, wrong answer."

**What none of these three catch:** the retrieved context itself being wrong. An answer can be perfectly faithful to bad information. That gap is exactly what reference-based Answer Correctness (1.4) exists to close.

### 1.4 Reference-based generator metrics

**Answer Correctness has no dedicated DeepEval metric class**, unlike Faithfulness or Relevancy — and that's not an oversight. "Is it factually right" is inherently specific to what "right" means for your task, so DeepEval's own recommended pattern is to write a custom `GEval` rubric rather than ship one generic class.

**Two ways to write a `GEval` rubric:**
- **`criteria`** — a single sentence describing what to check. Quick, but DeepEval has to expand it into an evaluation procedure itself, which can be inconsistent.
- **`evaluation_steps`** — you write the procedure yourself, step by step, and can weave in multiple test-case fields (e.g. relevance to `input`, agreement with `expected_output`, *and* grounding in `retrieval_context`, all in one rubric). More controllable — reach for this whenever a single-sentence criteria doesn't give you enough control over exactly what gets penalized.

**Answer Semantic Similarity** isn't a DeepEval class at all — it's plain embedding cosine similarity, cheap and fast with no LLM judge call, but weaker at catching subtle factual errors: two answers can be semantically close (same topic, similar vocabulary) while disagreeing on a key number or fact. That's its known weakness — it measures *topical* closeness, not *factual* agreement, which is why it's paired with (not a replacement for) an LLM-judged Answer Correctness check when you actually need to catch a wrong number or fact.

Both metrics need `expected_output` — a reference answer someone had to write. That's the cost side of the reference-based/referenceless tradeoff from 0.2: precise, but only as scalable as your ability to keep reference answers curated and current.

### 1.5 Evaluation inside the pipeline

Everything above scores a RAG system's output **after the fact** — build a test case, hand it to a metric, read the score. That's how you evaluate offline, against a batch of test cases. But context relevance and faithfulness are exactly the kind of checks you can also run **as part of the pipeline itself**, gating generation on bad retrieval or flagging a hallucinated answer before it ever reaches a user — a small graph like `retrieve → judge_context_relevance → generate → check_faithfulness`.

Two reasons this pattern is worth knowing, beyond "it's a different way to compute the same numbers":

1. **You can act on the result mid-pipeline.** A context-relevance check running *before* generation is cheap enough, and early enough, that a real system could branch on it — skip generation and ask a clarifying question if nothing relevant was retrieved, instead of generating a plausible-sounding answer from noise.
2. **Building the checks by hand once makes the metric classes far less of a black box.** Seeing "context relevance" and "faithfulness" built from raw judge calls first — before treating them as pre-built metric classes — makes it much clearer what those metrics are actually doing under the hood, and where you'd reach for a hand-rolled node instead of a metric class (when you need the eval signal *inside* your production control flow, not just in an offline report).

**A useful prototyping principle here:** build and debug a pipeline's graph shape against free, deterministic mocked judges first, then swap in real LLM judges once the shape is right. The node signatures and graph structure stay identical either way — only the judge implementation changes. This is also where non-determinism (0.3) becomes visible in practice: a mocked judge gives byte-identical output every run; a real judge can vary run to run, which is why production evals typically run each judge multiple times, use low/zero temperature, and sometimes track judge-agreement itself as a metric.

### 1.6 RAGAS in practice

Where DeepEval's unit of evaluation is an `LLMTestCase` (`input`, `actual_output`, `retrieval_context`, ...), RAGAS's is a `SingleTurnSample` — same idea, different field names (`user_input`, `response`, `retrieved_contexts`, `reference`). Where DeepEval takes a `model=` string and resolves the judge model internally, RAGAS wants an explicit `LangchainLLMWrapper` around any LangChain-compatible chat model — a small extra step, but it means RAGAS can use *any* LangChain-integrated provider as its judge, not just OpenAI models by name.

A few RAGAS-specific things worth knowing:

- **Reference-based/referenceless is spelled out in the class name.** RAGAS classes carry a `...WithoutReference` suffix when they don't need a ground-truth answer — the same 0.2 split, just visible in the name instead of inferred from which arguments you pass.
- **RAGAS is async-first.** Its scoring methods (`single_turn_ascore`) are `async`, called via `asyncio.run`, unlike DeepEval's default synchronous `.measure()`.
- **The metric mapping to DeepEval:** `LLMContextRecall`/`LLMContextPrecisionWithoutReference` ≈ Contextual Recall/Precision (1.2); `Faithfulness` ≈ `FaithfulnessMetric` (1.3).

**The batch/CI pattern:** in practice, RAGAS gets used against a real system via a `pytest`-parametrized test that reads questions from a spreadsheet, calls a live RAG backend for each one, scores the response, and writes the score back into the same spreadsheet — turning "one eval sample" into "one test per row," with `pytest` itself acting as the batch runner and pass/fail report. This is a general pattern, not RAGAS-specific — the same shape reappears with DeepEval's `TaskCompletionMetric` in the CrewAI capstone (Part 5).

### 1.7 Golden datasets and end-to-end evaluation

Hand-writing reference answers doesn't scale past a handful of examples. **Synthetic golden datasets** solve this: DeepEval's `Synthesizer` generates question/expected-answer pairs directly from your own documents, so you get a labeled eval set without writing reference answers by hand — evolving each generated question along configurable dimensions (e.g. requiring multi-step reasoning, or pulling from multiple context pieces). The cost: the generated questions are only as good as the synthesis process, worth spot-checking rather than blindly trusting.

The other detail that makes an evaluation genuinely **end-to-end**: build each test case's `retrieval_context` from **actually running the retriever** on the golden question, not from the documents the golden was generated from. If the retriever performs badly on a given question, its `retrieval_context` reflects that — you're testing the real, currently-running pipeline, not just checking whether the generator can produce a good answer given hand-picked perfect context.

**Reading an aggregate result table** (mean/min/max per metric, across every golden question at once) is how you diagnose *where* a RAG system is weak, using the same per-metric distinctions from 1.1–1.4: a low mean on Contextual Precision with a high mean elsewhere points at a ranking problem specifically; a low mean on Faithfulness alongside high Contextual Relevancy points at the generator hallucinating despite good retrieval — the same diagnostic logic, now applied at the dataset level instead of one hand-picked example at a time.

---

## Part 2 — Conversational, Tool & Task Evaluation

### 2.1 Multi-turn conversational evaluation

Part 1 evaluated single request/response pairs — a query in, an answer out. Real chatbots and agents hold a **conversation**: earlier turns constrain what a later turn should say, and a system can be perfectly fine turn-by-turn while still failing across the conversation as a whole — forgetting what the user said three turns ago, drifting off-topic, or giving advice it shouldn't across the arc of a dialogue.

DeepEval represents a dialogue as a `ConversationalTestCase`, a sequence of `Turn`s (each with a role and content), and applies conversational metrics to the whole thing:

- **`TurnRelevancyMetric`** — constructs sliding windows of turns, then uses the LLM to determine whether the last turn in every window has assistant content relevant to the previous conversational context in that window.
- **`KnowledgeRetentionMetric`** — evaluates whether the assistant correctly remembers and uses information from earlier turns.
- **`ConversationalGEval`** — the multi-turn counterpart to the `GEval` custom rubric from 1.4. Write your own domain-specific criteria (e.g. "safe medical advice") and apply it across the whole conversation, not just one turn.

**Scaling beyond hand-written dialogues:** a `ConversationSimulator` synthesizes multi-turn dialogues from defined user intents — a simulated user has a goal and a policy for pursuing it, including curveballs like changing requirements mid-conversation. At the end of a simulated conversation, the same metrics can check whether the goal was met, giving an automatic success signal that scales to hundreds of scenarios without writing every dialogue by hand.

### 2.2 Tool use evaluation

Tool use is the heart of any LLM agent. Regardless of how well an agent reasons or plans, if it calls the wrong function, passes malformed arguments, or invokes tools in the wrong sequence, the task fails — and the tricky part is that the final text output can look perfectly plausible even when the tool execution underneath was completely broken. A bot that confidently says "Your flight is booked!" is useless if it never actually called the booking API.

This makes tool-use evaluation fundamentally different from standard LLM evaluation. In a standard evaluation, you compare a model's output against a reference. With tool-using systems, the output is only the tip of the iceberg — beneath it is a sequence of decisions (which tools, in what order, with what arguments, how the results were interpreted), and each decision is its own potential failure point requiring its own check. An agent might skip a required lookup and hallucinate details, call the right tools with the wrong arguments, or call a tool before checking eligibility — and in every case, the final response can *sound* correct. Only tool-level evaluation catches the underlying failure.

DeepEval provides three dedicated metrics, each targeting a different dimension and granularity:

| Metric | Type | Question | Best for |
|---|---|---|---|
| **`ToolCorrectnessMetric`** | Reference-based | Do `tools_called` match `expected_tools`? | Regression/CI, when you already know correct tool behavior |
| **`ArgumentCorrectnessMetric`** | Referenceless, LLM-judged | Were the arguments passed to each call correct for the task? | Dynamic workflows and production monitoring, where exact argument values can't be predetermined |
| **`ToolUseMetric`** | Multi-turn (`ConversationalTestCase`) | Tool selection **and** argument correctness across a conversation | Chatbot-style agents where tool use spans multiple exchanges |

`ToolCorrectnessMetric` can be configured with `ToolCallParams.INPUT_PARAMETERS` (check arguments match) and `ToolCallParams.OUTPUT` (check recorded outputs align), plus `should_exact_match=True` for a strict mode that penalizes extra tools, missing tools, mismatched details, or wrong ordering. An optional `available_tools` list additionally lets an LLM judge assess whether the agent chose the *most appropriate* tools from everything available, not just whether it matched the expected set.

`ArgumentCorrectnessMetric` is fully referenceless and LLM-judged — it evaluates argument quality based on the user's input and the tool descriptions, without needing expected argument values. **The strongest pattern here layers two checks:** a deterministic schema validation step runs first (catching malformed arguments — wrong keys, badly formatted dates — cheaply and for free), and only if that passes does the LLM-judged metric run to assess semantic correctness. This separates two genuinely different kinds of correctness: structural validity (deterministic, free) and task-appropriateness (needs judgment, costs a call).

`ToolUseMetric` produces two sub-scores — tool selection and argument correctness — and the **final score is the minimum of both**, so a failure in either dimension pulls the overall score down. It requires `available_tools` so it can judge whether each selection was optimal given the alternatives.

### 2.3 Task completion evaluation

The three tool-use metrics above all judge the **mechanics** of tool use — were the right tools picked, with the right arguments, in the right order. None of them ask the question that actually matters to a user: **did the agent get the job done?**

That gap is real. An agent can call every tool correctly and still fail the task — booking the wrong hotel because it ignored a stated budget, silently dropping a constraint from a multi-part request, or handing back a technically-valid tool result wrapped in a confident sentence that doesn't reflect what actually happened. Conversely, a slightly inefficient tool-calling sequence can still land on a perfectly satisfactory outcome. Tool-level and outcome-level metrics answer different questions, and a production eval suite needs both.

**`TaskCompletionMetric`** is DeepEval's dedicated answer: an LLM-judged, referenceless metric that looks at `input` (the user's goal) together with `actual_output` and `tools_called`, and asks whether the underlying task was actually accomplished.

- It only strictly requires `input` and `actual_output` — `tools_called` is optional but strongly recommended, since it's what lets the judge see *how* the outcome was reached, not just what the agent claims happened.
- The `task` parameter is optional and, if omitted, gets inferred from `input`. Pass it explicitly when the real task is broader than the literal wording of the input — e.g. an implicit constraint mentioned earlier in a conversation, or a richer definition of "done" than the raw request conveys.
- `requires_trace = True` signals a preference for a full execution trace when one's available (a trace captures intermediate reasoning a flat `tools_called` list can't); without one, it falls back to reasoning over `input` + `actual_output` + `tools_called` directly.

**Beyond the stock metric, two escalations:**

1. **When "done" is domain-specific** — write a custom `GEval` rubric instead of relying on the generic task-completion definition (e.g. "the summary must cite at least two sources," or "a refund response must never promise a dollar amount before policy lookup"). This costs more to write, because you have to spell out exactly what satisfying the requirement means, but it lets the judge apply your exact bar instead of a generic one.
2. **When the stakes are high enough that an LLM judge isn't enough** — skip judging the text entirely and **verify the actual side effect**. Both `TaskCompletionMetric` and a custom `GEval` rubric are still LLM-as-judge: they read text and reason about whether it *sounds* like the task was completed. For agents that take real actions (booking, sending, writing to a database), the strongest signal is a deterministic state check against the system of record — e.g. querying the booking system directly for a confirmed reservation, rather than trusting the agent's sentence saying it booked one. This can't be fooled by a fluent-but-wrong response. In practice the two approaches complement each other: a deterministic state check as the pass/fail gate wherever a checkable outcome exists, and an LLM-judged metric as a secondary quality signal for the parts of "correct" that are inherently fuzzy (tone, completeness of an explanation).

**Master question-to-metric table (Part 2):**

| Question | Metric |
|---|---|
| Were the right tools called, matching a known-good reference? | `ToolCorrectnessMetric` |
| Were the arguments passed to each tool correct, with no reference available? | `ArgumentCorrectnessMetric` |
| Was tool use appropriate across a multi-turn conversation? | `ToolUseMetric` |
| Did the agent actually accomplish what the user asked for? | `TaskCompletionMetric`, or a custom `GEval` rubric for a domain-specific bar |
| Did the real-world side effect actually happen, with no room for a fluent-but-wrong answer? | Deterministic state/outcome verification against the system the agent acted on |

### 2.4 The same evaluations through MLflow

MLflow's `mlflow.genai.evaluate()` doesn't ship dedicated, named metric classes like DeepEval's `TurnRelevancyMetric` or `ToolCorrectnessMetric`. Instead it gives you lower-level building blocks — built-in scorers (`Guidelines`, `Safety`, `Correctness`, ...), custom `@scorer` functions, and custom LLM judges via `make_judge()` — that read either the dataset row (`inputs`/`outputs`/`expectations`) or the full execution `Trace` MLflow auto-captures for every evaluated row, including `TOOL`- and `CHAT_MODEL`-typed spans.

Every DeepEval check from 2.1–2.2 has an MLflow-primitive equivalent:

| DeepEval | MLflow equivalent |
|---|---|
| `TurnRelevancyMetric` | Custom `make_judge()` judge with sliding-window instructions |
| `KnowledgeRetentionMetric` | Custom `make_judge()` judge over `{{ inputs }}` |
| `ConversationalGEval` (safe advice) | `Guidelines` scorer |
| `ConversationSimulator` | LLM-as-user-simulator loop driving `predict_fn` |
| `ToolCorrectnessMetric` | `@scorer` comparing `trace.search_spans(span_type=SpanType.TOOL)` against `expectations.expected_tools` |
| `ArgumentCorrectnessMetric` | Deterministic schema check + `make_judge()` judge over `{{ trace }}` |
| `ToolUseMetric` | `@scorer` combining tool-selection and argument scores via `min()` — same combination rule as DeepEval |

**The tradeoff, in one sentence:** DeepEval gives you these as ready-made, named metrics; MLflow gives you the primitives and expects you to assemble the equivalent yourself — more flexible, more boilerplate. What MLflow adds in return is that every evaluated row produces a real `Trace` you can inspect directly in the MLflow UI, alongside the run's aggregate metrics — evaluation as part of an experiment-tracking platform, not a standalone scoring pass.

---

## Part 3 — Agent Trajectory Evaluation

The tool-use and task-completion metrics from Part 2 all score a **finished** interaction: given the tools that were called and the final answer, was it correct? This part asks a different question: given a **multi-step run**, was the *path* the agent took any good — not just where it ended up? An agent can reach the right final answer while taking twice as many steps as necessary, retrying a failed call blindly instead of correcting course, or repeating an identical tool call for no reason. None of Part 2's metrics see any of that, because they only look at the final `tools_called` list and `actual_output`, not the shape of the trace that produced them.

The standard approach: run an agent's tool-calling loop to build a **trace** (a step-by-step record of what was called, with what arguments, and what happened), then hand that trace to a *separate* evaluation pass, scored against a **gold trajectory** defined ahead of time. Keeping the agent loop and the eval logic separate mirrors real practice — the agent doesn't grade itself; a separate harness does.

### The 9 trajectory-level metrics

Computed from one recorded trace (plus, where relevant, the real state of whatever system the agent acted on) — a single run scored many ways:

1. **Tool Selection Accuracy** — checks *coverage*, not order: does the set of tools actually called include every tool in the gold set? This is the loosest of the nine — it would pass even if the agent called tools in the wrong order or threw in extra redundant calls, which is exactly why the metrics that follow narrow in on those specific failure modes.
2. **Tool Call Correctness (Arguments)** — passing #1 only confirms the *right tools* were called; this checks whether the arguments passed were actually valid. A tool can be correctly selected and still called with wrong or malformed arguments.
3. **Unnecessary / Redundant Tool Calls** — a call whose `(tool, arguments)` pair already **succeeded** earlier in the same trace, adding no new information.
4. **Step-wise Accuracy** — the fraction of *all* trace steps that made real forward progress (succeeded and weren't redundant). Unlike #1, which only checks coverage of the tool set, this penalizes wasted steps at the individual-step level.
5. **Task Success Rate** — checks the ground-truth outcome directly for one run (was the expected state actually achieved). Across many tasks, this boolean is averaged into an actual rate.
6. **Trajectory Match (fuzzy / set-based)** — compares the *set* of tools that ended successfully against the gold tool set, ignoring order, retries, and errors entirely. Deliberately looser than an exact-sequence match, which would fail purely because of a mid-trace typo or a redundant lookup, even when the agent still did the right things overall.
7. **End-State Verification** — the most important check in the suite: instead of trusting a string the agent generated (which could be wrong or fabricated), read the actual mutated system of record directly, to confirm the real-world effect really happened and wasn't just claimed.
8. **Recovery / Self-Correction Rate** — for every trace entry that errored, checks whether a *later* entry called the *same tool* and succeeded — the signal that the agent noticed its own mistake and corrected it, rather than giving up or blindly repeating the same bad call. Reported as `recovered / total errors`.
9. **Cost / Efficiency proxy** — treats redundant calls and errors as "wasted" and computes a lightweight efficiency score (a stand-in for token usage / latency, which in production you'd pull from real tracing infrastructure instead).

**The throughline across all nine: task success alone is not enough.** A trace can reach the right final answer while still being inefficient, error-prone, or lucky rather than reliable. A run can score well on tool selection and end-state verification (the agent used every tool it needed and the real effect happened) while scoring only moderately on step-wise accuracy and cost efficiency (some fraction of steps were errors or redundant calls) — that combination is exactly why outcome metrics alone can hide inefficiency, and exactly why step-level and trajectory-level metrics need to run *together*, not as a substitute for one another. A good recovery rate is also a genuinely positive signal on its own: an error that gets caught and corrected mid-run is a very different system from one that fails silently or retries blindly with the same bad input.

**A note on realistic vs. real agents:** a scripted mock agent needs synthetic failures deliberately injected into it to have something for these metrics to catch. A real, reasonably capable model will often pick a correct, minimal trajectory on its own and avoid obvious redundancy — which is exactly why a production system needs this kind of harness running *continuously*, not as a one-off check: to catch the cases (ambiguous queries, an extra tool the model reaches for unnecessarily, edge cases) where the model doesn't behave as well as it usually does.

### How this maps onto a production stack (Databricks example)

| Metric | Production mapping |
|---|---|
| Tool Selection Accuracy | Gold tool set in a table; compared against tool spans captured by automatic tracing |
| Tool Call Correctness | Tools defined with typed signatures so a malformed call fails validation before it executes |
| Unnecessary Tool Calls | Query the trace store for duplicate `(tool, inputs)` spans within the same request |
| Step-wise Accuracy | A custom per-step scorer iterating trace spans, run as part of the eval job |
| Task Success Rate | An eval set of `(task_id, expected_outcome)`; agent run as a scheduled job; pass/fail trended on a dashboard |
| Trajectory Match | Gold trajectories stored as structured data; a registered comparison function invoked as a custom eval metric |
| End-State Verification | A before/after diff of the real system-of-record table, inside the same pipeline run as the agent |
| Recovery Rate | Error-status spans marked automatically by tracing; a scheduled job pattern-matches them against later successful spans in the same trace tree |
| Cost / Efficiency | Real tracing captures token usage and latency **per span automatically** — no manual instrumentation needed |

Note the general lesson, not just the Databricks specifics: every one of the 9 hand-computed metrics above has a natural production home once real tracing infrastructure exists — you're not inventing new concepts for production, you're re-pointing the same 9 questions at real spans instead of a hand-built trace list. That's exactly the bridge Part 4 covers next.

---

## Part 4 — Production Tracing & Experimentation

Every idea above builds and scores test cases by hand — a test case object, a hand-rolled trace list, a conversational test case. That's the right way to *learn* what each metric checks, but it's not how evaluation runs against a live, deployed system. Production-grade evaluation adds two things hand-built examples can't give you:

1. **Real tracing infrastructure** — every LLM call, tool call, and agent step automatically captured as a structured span, not appended to a list by hand.
2. **A formal offline experiment framework** — a dataset, a task, and an evaluator as reusable objects you can re-run against a changed system, rather than a one-off script.

### What's genuinely new here vs. what's the same idea on real infrastructure

Some of what a production tracing setup (like Arize Phoenix) gives you is a real-infrastructure version of concepts already covered:

- **Tracing itself** is the production-grade version of a hand-rolled trace list — the same underlying idea (a structured, step-by-step record of what happened), captured by real instrumentation instead of a manual `.append()` call.
- **Router/tool evals**, run by querying captured spans with an LLM judge, are the same question as `ToolCorrectnessMetric`/`ArgumentCorrectnessMetric` (Part 2.2) — just computed from real spans instead of a manually-populated tool-call object.
- **Trajectory/path efficiency** experiments ask the same question as Step-wise Accuracy / Cost-Efficiency (Part 3) — was the path efficient, not just successful — but running through a reusable `dataset` / `task` / `evaluator` triple that generalizes to *any* agent and *any* metric, instead of a one-off script over a single hand-built trace.

But two ideas are genuinely new territory, not covered anywhere earlier:

- **Skill evals** — judging a *tool's own output quality* in isolation (is generated SQL correct? Does generated chart code actually run? Is an intermediate analysis clear?) rather than judging the agent's final answer or its choice of tool. Closest analog is the generator metrics from Part 1, but applied per-tool instead of to one final response.
- **Version comparison** — re-running the *same* experiment (same dataset, same task, same evaluators) against a system with one deliberate change (e.g. a new system prompt) and comparing results side by side. None of the earlier material compares two versions of a system against each other; everything before this judges one run in isolation. This is the production answer to "did my prompt change actually help, or did it just feel better?"

**The throughline:** building and instrumenting a system captures what it does; progressively more structured evaluation on top of that (single evaluators → multiple evaluators run together → the same evaluators re-run against a changed version) is how the earlier ideas (tool correctness, trajectory efficiency, outcome quality) get applied against a real trace store instead of a hand-built one, with the added ability to compare *versions* of a system, not just judge one run.

---

## Part 5 — Capstone Lessons: Evaluating a Real System

Every metric discussed so far can be, and in this material mostly *is*, demonstrated against a hand-built test case — a query and an answer written by hand, sometimes with a hand-crafted retrieval context or tool-call list attached. Applying the same metrics to **the real output of a real, running multi-agent system**, scored in batch over many real requests, surfaces a few lessons that hand-built examples can't teach on their own.

**A multi-agent system is a genuinely different shape from a single looping agent.** Instead of one model looping over its own tools, several narrowly-scoped agents can hand off work to each other in sequence — one agent's output becoming a later agent's input. Evaluating this kind of system means evaluating the *combined* output of that handoff chain, not any single agent's step in isolation.

**Write the task description explicitly rather than trusting inference.** `TaskCompletionMetric`'s `task` parameter is optional and, left unset, gets inferred from the raw input. But the real requirement behind a request is often richer than its raw form fields convey — a request for "a trip plan" might really mean "a plan that includes top-3 interest matches, 5 attractions, a day-by-day itinerary, and budget guidance." Spelling that out explicitly, rather than trusting the metric to infer it, is the domain-specific-rubric instinct from Part 2.3, applied via the `task` argument instead of a full custom `GEval`.

**Watch for the gap between "an eval script exists" and "an eval script sees everything the metric needs."** `TaskCompletionMetric` is meaningfully more useful when it can see `tools_called` — but a batch eval script calling a real system's public API often only has the *final* output to work with, not the internal tool calls each internal agent made. An illustrative or approximated `tools_called` list is better than none, but it's worth explicitly recognizing as a gap between what the metric *can* use and what the eval script actually captured — the fix, where it matters, is capturing tool calls from the real system's own tracing/callbacks rather than reconstructing them after the fact.

**The batch-to-spreadsheet pattern reappears, one more time.** The same shape from RAG's RAGAS CI pattern (Part 1.6) — a spreadsheet of inputs, a live backend call per row, a score written back into the same spreadsheet — is exactly how a real multi-agent system gets evaluated in batch, just with a different metric doing the scoring. This is worth recognizing as a *general* pattern (turn a dataset into a parametrized test suite, call the real system, score the real response, persist the result next to its input) rather than something specific to any one framework.

**The arc, end to end:** one metric, run once on a hand-built example, teaches what the metric checks. The same metric, run in batch against a real system's real output, with scores written back for review, is what evaluation actually looks like once a system is deployed. Everything in Parts 1–4 is building toward being able to do that last step credibly — knowing which metric answers which question, what it needs to run, what it can and can't catch, and what a real integration is missing relative to the ideal.

---

## Master Quick Reference

### Question → metric lookup (all parts)

| If you're asking... | Reach for... |
|---|---|
| Did retrieval fetch the right chunks, and I have labeled relevant-chunk IDs? | Precision@K, Recall@K, MRR, nDCG (1.1) |
| Did retrieval fetch the right chunks, and I *don't* have labeled IDs? | Contextual Precision / Recall / Relevancy (1.2) |
| Is the generated answer grounded and on-topic, with no reference answer available? | Answer Relevancy, Faithfulness, Hallucination (1.3) |
| Is the generated answer actually *correct* against a known-good answer? | Custom `GEval` (Answer Correctness), Answer Semantic Similarity (1.4) |
| Is a full RAG pipeline good, in aggregate, across many queries? | Synthetic golden dataset + full metric suite (1.7) |
| Does a multi-turn conversation stay coherent, remember context, stay in bounds? | `TurnRelevancyMetric`, `KnowledgeRetentionMetric`, `ConversationalGEval` (2.1) |
| Did the agent call the right tools, with the right arguments? | `ToolCorrectnessMetric`, `ArgumentCorrectnessMetric`, `ToolUseMetric` (2.2) |
| Did the agent actually accomplish what the user asked, mechanics aside? | `TaskCompletionMetric`, custom `GEval`, or deterministic state verification (2.3) |
| Across a multi-step run, was the *path* efficient and self-correcting? | The 9-metric trajectory suite (Part 3) |
| How does this look with real tracing and formal experiments? | Arize Phoenix — tracing + dataset/task/evaluator experiments (Part 4) |
| Did a real, deployed, possibly-multi-agent system actually work, in batch? | The batch-to-spreadsheet pattern + the outcome metric that fits the task (Part 5) |

### Framework cheat sheet

| Framework | Unit of evaluation | Sync/async | Named metric classes? |
|---|---|---|---|
| **DeepEval** | `LLMTestCase` / `ConversationalTestCase` | Sync (`.measure()`) | Yes — dozens, plus `GEval` for custom rubrics |
| **RAGAS** | `SingleTurnSample` | Async (`single_turn_ascore`) | Yes, narrower scope than DeepEval, RAG-specific |
| **MLflow** | A dataset row (`inputs`/`outputs`/`expectations`) + auto-captured `Trace` | Sync (`mlflow.genai.evaluate()`) | No — primitives (`Guidelines`, `make_judge`, `@scorer`) you assemble yourself |
| **Arize Phoenix** | A captured trace span / an experiment `dataset`+`task`+`evaluator` | — | No — a tracing + experiment platform, not a metric library |

### The five ideas worth remembering above everything else

1. **Taxonomy first.** "Evaluate the system" is never one question — know whether you're diagnosing retrieval, generation, tool mechanics, trajectory, or outcome before picking a metric.
2. **Reference-based vs. referenceless is a cost decision, not just a technical one.** Reference-based for CI with a curated test set; referenceless for production traffic you can't hand-label.
3. **LLM-as-judge is a tool with known failure modes, not an oracle.** Judge-model choice, non-determinism, prompt sensitivity, and cost all compound — and a fluent-but-wrong answer can fool it.
4. **Mechanics ≠ process ≠ outcome, for agents.** Right tool + right arguments (mechanics) doesn't guarantee a sound sequence (process), and a sound sequence doesn't guarantee the user's actual goal was met (outcome). Evaluate all three, not just the easiest to check.
5. **The strongest signal is checking the real system of record.** Wherever a real, checkable side effect exists (a database row, a booking, a sent message), end-state verification beats every LLM-judged metric — it cannot be fooled by a confident sentence that misrepresents what actually happened.
