"""
Promotion gating: deciding whether a new prompt version may take the `@production` alias
========================================================================================

Built in Phase 5. Reused by Phase 8, where GEPA produces a candidate prompt automatically
and the same rules decide whether it ships.

Why two conditions, not one
---------------------------
A candidate has to clear both an **absolute** bar and a **relative** one:

1. **Absolute** — every blocking quality gate from Phase 0 still passes its threshold.
2. **No regression** — no blocking metric dropped meaningfully against the version
   currently holding the `@production` alias.

Only checking (1) lets quality erode: a metric can slide from 0.98 to 0.91 and still clear
a 0.90 bar, and repeating that a few times walks the agent down to the floor one
"passing" release at a time. Only checking (2) lets a candidate that improved on a bad
baseline ship while still being bad.

Why the tolerance differs per metric
------------------------------------
Phase 3 established that deterministic scorers are reproducible and LLM judges are not.
That distinction has a direct operational consequence here:

- A **deterministic** metric that drops did so because behaviour changed. Tolerance: zero.
- A **judged** metric can move a little between identical runs purely as judge noise.
  Comparing at zero tolerance would block promotions for reasons that aren't real.

So the noise budget is granted only to metrics that actually have noise. Applying one
blanket tolerance to everything either blocks good releases or lets real deterministic
regressions through.
"""

# ============================================================================
# CONFIGURATION
# ============================================================================

PROMPT_NAME = "telcoassist_system_prompt"

# Metrics produced by deterministic scorers in `scorers.py` -- same inputs, same verdict,
# every time. Any drop in these is a real behavioural change, never measurement noise.
DETERMINISTIC_METRICS = {
    "tool_call_correctness",
    "no_account_leakage",
    "response_word_count",
    "response_length",
    "length_strict",
    "length_loose",
    # Phase 9. All three read spans and conversation text with no model call, so any
    # movement in them is a behavioural change, never judge noise.
    "tool_selection_correctness",
    "approval_before_write",
    "context_retained",
}

# Noise budget for LLM-judged metrics only. Two points of pass-rate on a 12-row dataset is
# well under one row flipping, so this absorbs judge jitter without hiding a real drop.
JUDGE_REGRESSION_TOLERANCE = 0.02
DETERMINISTIC_REGRESSION_TOLERANCE = 0.0


def metric_base_name(metric_key: str) -> str:
    """`safety/mean` -> `safety`. Metric keys are `<scorer name>/<aggregation>`."""
    return metric_key.split("/")[0]


def tolerance_for(metric_key: str) -> float:
    """Zero tolerance for deterministic metrics, a small budget for judged ones."""
    if metric_base_name(metric_key) in DETERMINISTIC_METRICS:
        return DETERMINISTIC_REGRESSION_TOLERANCE
    return JUDGE_REGRESSION_TOLERANCE


# ============================================================================
# COMPARISON
# ============================================================================

def compare_runs(baseline_metrics: dict, candidate_metrics: dict) -> list:
    """Line up two runs' metrics and classify every shared one.

    Returns a list of dicts with: metric, baseline, candidate, delta, tolerance,
    deterministic, and verdict (one of "improved", "unchanged", "regressed").

    Only metrics present in *both* runs are compared -- a metric that exists on one side
    only cannot be a regression, it's a change in what was measured, which is a different
    problem and is reported separately by `promotion_decision`.
    """
    rows = []
    for key in sorted(set(baseline_metrics) & set(candidate_metrics)):
        base, cand = baseline_metrics[key], candidate_metrics[key]
        if not isinstance(base, (int, float)) or not isinstance(cand, (int, float)):
            continue
        delta = cand - base
        tol = tolerance_for(key)
        if delta < -tol:
            verdict = "regressed"
        elif delta > tol:
            verdict = "improved"
        else:
            verdict = "unchanged"
        rows.append(
            {
                "metric": key,
                "baseline": base,
                "candidate": cand,
                "delta": delta,
                "tolerance": tol,
                "deterministic": metric_base_name(key) in DETERMINISTIC_METRICS,
                "verdict": verdict,
            }
        )
    return rows


def promotion_decision(baseline_metrics, candidate_metrics, quality_gates, resolve_fn):
    """Decide whether the candidate may take the `@production` alias.

    Args:
        baseline_metrics: `results.metrics` from the run of the current @production version.
        candidate_metrics: `results.metrics` from the candidate's run.
        quality_gates: the QUALITY_GATES mapping from `eval_dataset.py`.
        resolve_fn: `eval_dataset.resolve_gate_metrics` -- passed in rather than imported so
            this module stays independent of the dataset module.

    Returns:
        A dict with `promote` (bool) plus the evidence behind it. The evidence matters as
        much as the verdict: "do not ship" without a reason isn't actionable.
    """
    resolved, unmatched = resolve_fn(candidate_metrics)

    # Condition 1 -- absolute thresholds on blocking gates.
    gate_failures = [
        {"gate": gate, "metric": key, "score": score, "threshold": quality_gates[gate]["threshold"]}
        for gate, (key, score) in resolved.items()
        if quality_gates[gate]["blocking"] and score < quality_gates[gate]["threshold"]
    ]

    # Condition 2 -- no regression on any metric backing a blocking gate.
    blocking_metric_keys = {
        key for gate, (key, _) in resolved.items() if quality_gates[gate]["blocking"]
    }
    comparison = compare_runs(baseline_metrics, candidate_metrics)
    regressions = [
        row for row in comparison
        if row["verdict"] == "regressed" and row["metric"] in blocking_metric_keys
    ]

    # Reported but not blocking: movement on metrics that back no blocking gate.
    other_regressions = [
        row for row in comparison
        if row["verdict"] == "regressed" and row["metric"] not in blocking_metric_keys
    ]

    return {
        "promote": not gate_failures and not regressions,
        "gate_failures": gate_failures,
        "blocking_regressions": regressions,
        "non_blocking_regressions": other_regressions,
        "improvements": [r for r in comparison if r["verdict"] == "improved"],
        "unmeasured_gates": unmatched,
        "comparison": comparison,
    }


def format_decision(decision: dict) -> str:
    """Render a promotion decision as a readable block, reasons first."""
    lines = []
    verdict = "PROMOTE" if decision["promote"] else "DO NOT PROMOTE"
    lines.append(f"DECISION: {verdict}")

    if decision["gate_failures"]:
        lines.append("\n  blocking gates below threshold:")
        for f in decision["gate_failures"]:
            lines.append(
                f"    - {f['gate']}: {f['score']:.3f} < {f['threshold']:.2f}  ({f['metric']})"
            )

    if decision["blocking_regressions"]:
        lines.append("\n  regressions on blocking metrics:")
        for r in decision["blocking_regressions"]:
            kind = "deterministic" if r["deterministic"] else "judged"
            lines.append(
                f"    - {r['metric']}: {r['baseline']:.3f} -> {r['candidate']:.3f} "
                f"({r['delta']:+.3f}, tolerance {r['tolerance']:.2f}, {kind})"
            )

    if decision["non_blocking_regressions"]:
        lines.append("\n  regressions elsewhere (noted, not blocking):")
        for r in decision["non_blocking_regressions"]:
            lines.append(f"    - {r['metric']}: {r['delta']:+.3f}")

    if decision["improvements"]:
        lines.append("\n  improvements:")
        for r in decision["improvements"]:
            lines.append(f"    + {r['metric']}: {r['delta']:+.3f}")

    if decision["unmeasured_gates"]:
        lines.append(f"\n  gates not measured in this run: {decision['unmeasured_gates']}")

    return "\n".join(lines)
