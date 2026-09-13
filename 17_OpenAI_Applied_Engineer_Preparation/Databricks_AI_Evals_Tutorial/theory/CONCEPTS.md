# Concept Map

Every concept in the track, grouped **by theme** rather than by build order, with a pointer
to the notebook that demonstrates it. Definitions are one or two lines by design — the
notebook is the explanation; this is the index.

---

## How the phases feed each other

The notebooks are numbered in build order, but they form a **cycle**, and the direction of
each arrow is the thing worth remembering:

```mermaid
flowchart LR
    PROD(["production traffic"]) --> MON

    MON["Phase 6 · online monitoring<br/>sampled judges on live traffic<br/>no ground truth, wide error bars"]
    MON -- "flags something" --> MINE

    MINE["Phase 4 · mine the traces<br/>novelty-targeted selection<br/>gives inputs, not labels"]
    MINE -- "a human labels them" --> ALIGN

    ALIGN["Phase 7 · align the judge<br/>expert standards distilled<br/>now the reward signal means something"]
    ALIGN -- "trusted objective" --> OPT

    OPT["Phase 8 · GEPA optimisation<br/>candidate prompt generated<br/>registered, NOT deployed"]
    OPT -- "candidate" --> GATE

    GATE{"Phase 5 · promotion gate<br/>thresholds + no regression<br/>100% coverage, paired"}
    GATE -- "only if it passes" --> PROD
    GATE -- "rejected" --> OPT

    style MON fill:#e8f0fe,stroke:#4285f4
    style GATE fill:#fef7e0,stroke:#f9ab00
    style PROD fill:#e6f4ea,stroke:#137333
```

Two properties hold it together:

- **Online discovers; offline prevents recurrence.** A finding that stops at the monitoring
  dashboard helps once. Carried through to a gated test, it protects every release after.
- **The gate is the only thing that can deploy.** Humans write prompts in Phase 5, machines
  write them in Phase 8, and both pass through the identical check. Nothing is exempt for
  being machine-generated — if anything it deserves more scrutiny, because it was optimised
  against a metric that sits *inside* the gate.

---

## 1. What evaluation is for

| Concept | In one line | Phase |
| --- | --- | --- |
| **Eval-driven development** | Decide what "good" means, with thresholds, *before* writing the code being judged. | 0 |
| **An eval that doesn't end in a decision isn't an eval** | Metrics nobody acts on are vibes wearing a lab coat; the output should be *ship* or *don't ship*. | 2 |
| **Quality gate** | A named metric + threshold + blocking flag. Turns a score into a release decision. | 0, 2 |
| **Blocking vs informational** | Whether failing it stops a release. Orthogonal to whether the dimension *matters*. | 0 |
| **Scorer ≠ gate** | Adding a scorer adds measurement, not enforcement. An ungated scorer blocks nothing. | 5, 9 |
| **Gate scope** | Some gates only resolve on certain run types (conversation gates are unmeasurable on single-turn runs) and must report "not measured" rather than 0. | 9 |

## 2. Traces and instrumentation

| Concept | In one line | Phase |
| --- | --- | --- |
| **An untraceable agent is unevaluable** | Scorers read the trace, not just the final string. | 1 |
| **Span type is a contract, not a label** | `RetrievalGroundedness()` hard-requires a RETRIEVER span; the wrong type doesn't degrade the eval, it breaks it. | 1 |
| **Combined auto + manual instrumentation** | Autolog for CHAT_MODEL spans and token counts; explicit `@mlflow.trace(span_type=…)` for the spans evaluation depends on. | 1 |
| **Retrieval as a fixed step, not a tool** | Guarantees every trace has a RETRIEVER span, so groundedness is always scoreable. | 1 |
| **Absence is behaviour** | A general question producing *no* tool span is a correct outcome worth scoring. | 1, 3 |
| **Trace nesting enables attribution** | conversation → turn → spans lets you say *which turn* a write happened on. | 9 |

## 3. Scorers

| Concept | In one line | Phase |
| --- | --- | --- |
| **Cost hierarchy** | Deterministic (free, instant) → wrapped judge → `make_judge` → trace-based judge (LLM call, large prompt). | 3 |
| **Determinism beats cost as a reason** | Deterministic scorers are *reproducible*; when one moves, behaviour really changed. Judges move on their own. | 3, 5 |
| **Scorer prerequisites** | Every scorer demands something (`expected_facts`, a RETRIEVER span). A missing prerequisite fails the run — better than silently measuring nothing. | 2 |
| **The `outputs` shape is whatever `predict_fn` returned** | No normalisation step; `outputs.get()` breaks if your agent returns a string. | 3 |
| **Function vs class-based scorer** | Use a class when the same check runs at several configurations in one run. | 3 |
| **Numeric scorer + aggregations** | Report a distribution, not a boolean — the p90 is where rambling answers hide. | 3 |
| **Custom judge (`make_judge`)** | For questions needing judgement: quality, tone, resolution. Categorical beats boolean where partial outcomes are real. | 3 |
| **Trace-based judge (`{{ trace }}`)** | Judges *how* the agent worked, not just what it said — this is what trajectory evaluation means. | 3 |
| **Deterministic + judge as complements** | Regex catches the blatant case always and the paraphrase never; the judge is the reverse. Run both. | 3 |
| **Scope of validity** | A scorer correct for a one-tool agent can become misleading when the agent gains a second tool. | 9 |

## 4. Datasets and ground truth

| Concept | In one line | Phase |
| --- | --- | --- |
| **Ground truth vs correct behaviour** | Content questions get `expected_facts`; refusals and escalations get per-row `guidelines`. | 2 |
| **Over-constrained expectations** | For ambiguous input several behaviours are acceptable; asserting one fails a good agent. | 10 |
| **Hand-written sets are structurally blind** | They contain what the author imagined, and the gap from reality is invisible from inside. | 4 |
| **Circular ground truth** | Using the agent's own outputs as expectations makes it pass by construction and freezes today's bugs as correct. | 4 |
| **Mining gives inputs, not labels** | Traces hand you the *distribution* — the expensive half to guess. Expectations stay manual. | 4 |
| **Sampling strategy decides what you learn** | Random sampling reproduces the head you already test; novelty-targeting finds the tail. | 4 |
| **Threshold over top-k** | Selecting by score returns fewer rows on a quiet day and more after a shift; top-k pads with things you already cover. | 4 |
| **Expectation provenance** | `AssessmentSource` records whether a human or a script authored a label — decisive when it later trains a judge. | 4 |
| **Merge by input hash** | Re-mining overlapping traffic updates records and accumulates expectations rather than duplicating. | 4 |
| **Fixed vs current datasets** | Curated sets must not drift (comparison validity); mined sets must stay fresh (discovery). Both are needed. | 4, 5 |

## 5. Versioning and release gating

| Concept | In one line | Phase |
| --- | --- | --- |
| **Registering is not deploying** | `register_prompt` creates a version; `set_prompt_alias` decides what serves traffic. Evaluation belongs in that gap. | 5 |
| **Alias as indirection** | Rollback is moving a pointer, not a revert-and-redeploy. | 5 |
| **Two-condition promotion** | Absolute thresholds *and* no regression vs the current production version. | 5 |
| **Threshold-only gates permit erosion** | 0.98 → 0.91 still clears a 0.90 bar; repeat it three times and you're at the floor. | 5 |
| **Per-metric-type tolerance** | Zero for deterministic metrics (no noise to absorb), a small budget for judged ones. | 5 |
| **A regression report is a diagnosis** | It should name the clause to fix, not just deliver a verdict. | 5 |
| **Numeric metrics have no "good" direction** | Word count falling reads as a regression; only a verdict-returning scorer encodes intent. | 5 |

## 6. Online evaluation

| Concept | In one line | Phase |
| --- | --- | --- |
| **Offline catches what your dataset contains** | Online exists to find what it didn't. | 6 |
| **Production has no ground truth** | Any scorer reading `expectations` is structurally offline-only, however good it is. | 6 |
| **Reference-free scorers** | Safety, relevance, groundedness, guidelines, and deterministic input/output checks transfer online. | 6 |
| **Register *and* start** | A registered-but-unstarted scorer evaluates nothing and looks identical to a working one. | 6 |
| **Sample judges, never sample deterministic scorers** | The first cost per call; the second are free. | 6 |
| **Statistical resolution of a sample** | A sampled rate is an estimate with error bars; alerts set below the resolution fire on noise. | 6 |
| **Choose sample rate from the delta you must detect** | Not from a round number that felt affordable. | 6 |
| **Traces as Delta tables** | Production behaviour becomes SQL-queryable; "slower" becomes "retrieval p95 doubled". | 6 |
| **Online discovers, offline prevents recurrence** | Carry every finding into a gated test or it only helps once. | 6 |

## 7. Judges and human calibration

| Concept | In one line | Phase |
| --- | --- | --- |
| **Who validates the validator** | Every score in Phases 2-6 came from an unvalidated judge. | 7 |
| **Agreement, not average score** | Average measures generosity; a judge rating everything 5/5 scores beautifully and is useless. | 7 |
| **A falling score after alignment is success** | The agent didn't change; the measurement stopped inflating. | 7 |
| **Exact agreement flatters** | On skewed distributions two raters agree often by luck. | 7 |
| **Cohen's kappa** | Agreement corrected for chance — but treats 4-vs-5 and 1-vs-5 as the same error. | 7 |
| **Quadratic weighted kappa** | Penalises by squared distance; the right default for ordinal scales. | 7 |
| **Alignment pairing key** | The label schema name must equal the judge name or `align()` silently learns nothing. | 7 |
| **Distilled guidelines** | Alignment's real output: your experts' tacit standard written down. | 7 |

## 8. Automated improvement

| Concept | In one line | Phase |
| --- | --- | --- |
| **The judge is the objective** | GEPA optimises toward whatever the judge rewards, so an unaligned judge makes optimisation actively harmful. | 8 |
| **Optimisation dataset ≠ eval dataset** | GEPA needs `expectations` on *every* row, describing required behaviour rather than gold text. | 8 |
| **Reflection** | The optimiser compares actual output against expected behaviour to reason about *why* a prompt underperforms. | 8 |
| **A higher optimisation score is not permission to ship** | It is by definition the metric being maximised — the most overfit number available. | 8 |
| **Same gate for machine-written prompts** | Evaluated against a scorer set strictly larger than the optimisation objective; that superset catches the overfitting. | 8 |

## 9. Conversations

| Concept | In one line | Phase |
| --- | --- | --- |
| **Turn-level metrics overstate conversation quality** | Independent turns at rate `p` give `p**n` for the conversation. | 9 |
| **Session-level vs turn-level** | A conversation can fail while every individual turn passes. | 9 |
| **Context retention** | Re-asking for something already supplied is the most visible multi-turn failure. | 9 |
| **Consent lives between turns** | "Acted without asking" has no single-turn representation at all. | 9 |
| **Three approval outcomes** | Compliant, violation, and *stalled* (agreed but nothing happened) need different fixes. | 9 |
| **Gate by prompt, verify by evaluation** | Most agent write-actions are gated by instructions, not APIs — so obedience must be tested. | 9 |
| **Tool selection ≠ tool use** | With one tool the two questions collapse; with two they separate, and wrong-tool is worse than no-tool. | 9 |
| **First-failing-turn distribution** | Failures on turn 1 mean basic competence; later turns mean context handling. | 9 |

## 10. Adversarial and edge cases

| Concept | In one line | Phase |
| --- | --- | --- |
| **Design by attack surface, not by example** | A flat list of jailbreak strings tells you nothing when it passes. | 10 |
| **Classes × variants** | Multiple phrasings per class stop one lucky string standing in for the surface. | 10 |
| **Behavioural boundaries** | Edge-case rows assert what must not happen, not one gold answer. | 10 |
| **Polite tool failure** | `{"found": False}` is easy to skate past; the answer that follows is specific, plausible, and wrong. | 10 |
| **Channel confusion** | Injection through content formatted to look like system text or tool output. | 10 |
| **Stating N/A with a reason** | Shows an item was considered; silence is indistinguishable from having missed it. | 10 |
| **Documented gap ≠ covered gap** | Writing a gap down buys honesty, not coverage — and the two are easy to confuse for a long time. | 0, 9 |

---

## Cross-cutting: the three ideas that recur

1. **Aggregates hide the thing you need to see.** Category slices (Phase 2), tool-decision
direction (Phase 3), attack class (Phase 10), turn position (Phase 9) — the same lesson
at four levels of granularity.
1. **Every measurement has a scope of validity.** Scorers (Phase 3), online eligibility
(Phase 6), gates (Phase 9). Something true of one configuration silently stops being
true when the system changes underneath it.
1. **Silence and success look identical.** An unstarted monitor, a mistyped metric name, an
ungated scorer, an unpaired label schema — each reports nothing and reads as fine.
