# Gotchas

Every trap hit while building this track, as **symptom → cause → fix**. Each one is
stranded in the single notebook where it surfaced; this is the collected version.

They are ordered by how badly they mislead. The first group is the dangerous one: **silent
failures that look exactly like success.**

---

## A. Silent failures — no error, wrong answer

### A1. A scorer you added blocks nothing
**Symptom:** A metric is measured, reported, and a regression in it ships anyway.
**Cause:** The scorer has no entry in `QUALITY_GATES`. Scorers are informational by default.
**Fix:** Add a gate whenever you add a scorer.
**Note:** This happened **twice** in this track — Phase 5 (account protection, escalation)
and Phase 9 (tool selection, approval gate, context retention). The second time, an agent
opening a support ticket nobody asked for would have been measured and released.

### A2. A mistyped metric name scores zero
**Symptom:** A gate fails at 0.000 and looks like a badly broken agent.
**Cause:** `results.metrics["saftey/mean"]` doesn't exist, so the lookup defaults to 0.
**Fix:** Resolve gates against the keys a run *actually produced* and report unmatched gates
as **not measured**, separately from failures. An unmeasured gate and a failed gate must
never look alike.

### A3. A registered monitor that was never started
**Symptom:** Production monitoring dashboard is quiet. Everything looks healthy.
**Cause:** `.register()` creates the scorer; `.start()` begins evaluating. Registering alone
produces a scorer that exists and does nothing.
**Fix:** Always both. Verify with `list_scorers()` — anything showing no sampling config is
inert.

### A4. Judge alignment that learns nothing
**Symptom:** `align()` completes without error; the aligned judge is identical to the base.
**Cause:** The label schema `name` doesn't match the judge `name`. That pairing is how SME
ratings get matched to judge scores on the same traces.
**Fix:** Define the name **once** as a variable and use it in both places.

### A5. An offline-only scorer registered for production
**Symptom:** A production scorer reports `skip` on 100% of traces while appearing healthy.
**Cause:** It reads `expectations`, and production traffic has no ground truth. Hit by
`tool_call_correctness` — one of the most useful scorers in the track.
**Fix:** Before registering, check the scorer is reference-free. The test is mechanical:
does it read `expectations`?

### A6. GEPA optimises for a whole budget and changes nothing
**Symptom:** Optimisation runs its full `max_metric_calls` and the prompt barely moves.
**Cause:** `predict_fn` closed over a fixed prompt string instead of re-loading from the
registry each call, so every candidate ran against the same old text.
**Fix:** `prompt = mlflow.genai.load_prompt(uri)` **inside** `predict_fn`.

### A7. A flat adversarial list that passes while a surface is wide open
**Symptom:** "Passed 12/15 jailbreak strings" — and one attack class is undefended.
**Cause:** Examples without a taxonomy. A simulated agent here scored **80% overall with
one class at 0%**.
**Fix:** Organise as classes × variants and report per class.

### A8. A polite tool failure followed by a confident answer
**Symptom:** The agent states a plan and balance for an account that doesn't exist.
**Cause:** Tools return `{"found": False}` rather than raising; the model skates past it.
**Fix:** A deterministic scorer that reads the TOOL span output and checks the response
doesn't assert the facts the failed tool was supposed to supply.

---

## B. Hard errors — loud, but the message doesn't name the cause

### B9. `RetrievalGroundedness()` cannot score the trace
**Cause:** No span typed RETRIEVER. A retrieval function traced without `span_type` doesn't
count.
**Fix:** `@mlflow.trace(span_type=SpanType.RETRIEVER)`, returning `mlflow.entities.Document`
objects — the scorer reads `page_content` off them.

### B10. `Correctness()` fails the run
**Cause:** No `expectations.expected_facts` or `expected_response` on the row.
**Fix:** Supply them, or don't run `Correctness()` on rows that have no factual answer
(adversarial rows genuinely don't).

### B11. `outputs.get(...)` raises `AttributeError`
**Cause:** The published examples assume `predict_fn` returns a dict. Ours returns a string,
so `outputs` **is** that string. There is no normalisation step — the shape of `outputs` is
exactly what your `predict_fn` returned.
**Fix:** Normalise in one helper every scorer routes through.

### B12. Prompt Registry operations fail
**Cause:** Registry features require a **SQL-backed** tracking store. `file:./mlruns` does
not support them.
**Fix:** `sqlite:///mlflow.db` locally, or Databricks.

### B13. Evaluation datasets fail the same way
**Cause:** Same constraint, independently — `mlflow.genai.datasets` also needs a SQL backend.
**Fix:** Same. Two features now depend on that choice.

### B14. `merge_records` rejects your traces
**Cause:** You passed the default DataFrame. It needs `search_traces(..., return_type="list")`.
**Fix:** Pass the list form. Easy to miss because the default *looks* right.

### B15. Linking a UC schema hides your existing traces
**Cause:** Linking an experiment to Unity Catalog conceals that experiment's previously
MLflow-stored traces. Unlinking restores them.
**Fix:** Use a **separate** experiment for production traces. Linking the evaluation
experiment would have hidden everything from Phases 1-5.

### B16. `set_experiment_trace_location` fails
**Cause:** `MLFLOW_TRACING_SQL_WAREHOUSE_ID` must be set **before** the link call.
**Fix:** Set the env var first.

### B17. Trace-table permission errors despite `ALL_PRIVILEGES`
**Cause:** `ALL_PRIVILEGES` is explicitly **not sufficient** for the
`mlflow_experiment_trace_*` tables.
**Fix:** Grant `MODIFY, SELECT` on each of the three tables by name, plus `USE_CATALOG` and
`USE_SCHEMA`.

### B18. Invalid aggregation name
**Cause:** Only six are valid: `min`, `max`, `mean`, `median`, `variance`, `p90`.
**Fix:** Use `median` for p50. There is no p99.

---

## C. Misreadings — the number is right, the interpretation isn't

### C19. "The aligned judge scored lower, so the agent regressed"
**Reality:** The agent didn't change at all. The unaligned judge was inflating; the aligned
one applies your experts' stricter standard. **A falling score after alignment is the
success condition.** Read the agreement measures, not the average.

### C20. "Raw agreement is 85%, the judge is fine"
**Reality:** On a skewed rating distribution two raters agree often by luck. Cohen's kappa
on that same data was **0.20**.

### C21. "Plain kappa says both judges are equally bad"
**Reality:** Plain kappa treats 4-vs-5 and 1-vs-5 as the same error. Two judges with
*identical* exact agreement (0.00) and *identical* plain kappa (−0.250) scored **+0.71 and
−0.82** under quadratic weighted kappa. On ordinal scales use the weighted form.

### C22. "A 5% sample shows a 2-point drop — page someone"
**Reality:** At 2,000 traces/day a 5% sample resolves to about **±4.5 points**. A 2-point
move is indistinguishable from noise. Detecting it needs ~30% sampling.

### C23. "Conciseness improved, ship it"
**Reality:** The metric someone asked about improving can rise while three nobody watched
collapse. This is interview Case #8 and it is built deliberately into Phase 5.

### C24. "95% of turns pass, the assistant is in good shape"
**Reality:** At five turns that's a **77%** conversation success rate, and the overstatement
grows with length — the metric looks best where the product is worst.

### C25. "`_episodic_memory` is empty, alignment failed"
**Reality:** It loads lazily. Inspect `.instructions`, which carries the distilled
guidelines.

### C26. "Word count went down, that's a regression"
**Reality:** A raw numeric metric carries no information about which direction is good.
Wrap it in a scorer that returns a verdict if you want it to gate anything.

---

## D. Design traps found by tests, not by errors

### D27. Approval gate off by one turn
**Bug:** Treating a write on the *same* turn consent arrived as premature (`t <= consent`).
**Why wrong:** Consent arrives in the user's message at the *start* of a turn; the write
happens in the agent's response *within* that turn. Same-turn is correct.
**Effect if shipped:** Fails the agent for behaving correctly.

### D28. Session identity scoped to one turn
**Bug:** Applying `customer_id` only to turn 1.
**Why wrong:** The agent loses the customer's identity from turn 2 onward, so every
conversation fails context-retention for a plumbing reason — measuring the harness, not the
agent.

### D29. Gate resolution ignoring candidate priority
**Bug:** Iterating the *metrics* dict instead of the *candidate* list, so which scorer backed
a gate depended on dict ordering rather than documented preference.
**Effect:** A judged scorer could silently outrank the deterministic one meant to take
precedence.

### D30. The published tool-selection pattern ignores extra calls
**Bug:** Computing both missing and unexpected tools, then basing the verdict only on
missing ones.
**Effect:** An agent that calls *every* tool on *every* request scores 100%.
**Fix:** Fail both directions. An unexpected account lookup is a privacy problem, not an
inefficiency.

---

## E. Environment

### E31. The pre-commit hook isn't actually running
**Symptom:** Notebook outputs land in commits despite documentation saying they can't.
**Cause:** `pre-commit install` was never run in the clone. Installing the packages does
nothing on its own.
**Check:** `test -f .git/hooks/pre-commit`.

### E32. A JSON-rewriting git clean filter leaves everything dirty
**Cause:** The filter re-serialises the whole file, so its output only byte-matches the
committed blob if that blob was produced by the same filter. Verified: files that parsed
*identically* differed by 78 bytes of whitespace.
**Fix:** One `git add --renormalize .` pass after installing such a filter — and be aware
that a hand-rolled filter must byte-match forever.
