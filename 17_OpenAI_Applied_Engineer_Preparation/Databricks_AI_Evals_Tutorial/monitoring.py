"""
Online evaluation helpers: what can be scored in production, and how much to sample
===================================================================================

Built in Phase 6. Pure Python — no MLflow import — so the reasoning here can be checked
without a Databricks workspace attached.

Three things this module encodes
--------------------------------

**1. Not every scorer can run online.** A production trace has no ground truth. Nobody
wrote `expected_facts` for a question a real customer asked thirty seconds ago, and nobody
ever will. So any scorer that reads `expectations` is structurally offline-only — it will
score every production trace "skip" no matter how well it works in Phase 3. Reference-free
scorers (safety, relevance, groundedness, guidelines, and deterministic checks over
inputs/outputs) are the ones that transfer.

**2. Sampling is the central economic decision.** Scoring 100% of production traffic with
LLM judges routinely costs more than serving the traffic did. Deterministic scorers are
free and should run at 100%; judges get a sample rate.

**3. A sampled metric is an estimate, and estimates have error bars.** This is where
production monitoring most often goes wrong: a team samples 5% of traffic, sees a pass rate
move from 0.95 to 0.93, and pages someone — when the confidence interval on that sample was
±0.04 and the move means nothing. The functions below make that arithmetic explicit so an
alert threshold can be set against what the sample can actually resolve.
"""

import math

# ============================================================================
# WHICH SCORERS CAN RUN ONLINE
# ============================================================================
# The test is simple: does the scorer need `expectations`? If yes, it cannot run against
# production traffic, because production traffic has no ground truth attached.

ONLINE_CAPABLE = {
    "Safety": "Reference-free — judges the response alone.",
    "RelevanceToQuery": "Reference-free — compares response to the request.",
    "RetrievalGroundedness": "Reference-free — compares response to the RETRIEVER span.",
    "Guidelines": "Reference-free — judges against a fixed rule you wrote.",
    "no_account_leakage": "Deterministic, reads only inputs and outputs. Free, so run at 100%.",
    "response_word_count": "Deterministic, reads only outputs. Free, so run at 100%.",
}

OFFLINE_ONLY = {
    "Correctness": "Requires expectations.expected_facts — no ground truth exists in production.",
    "ExpectationsGuidelines": "Requires per-row expectations.guidelines — same problem.",
    "tool_call_correctness": (
        "Reads expectations['expects_tool_call']. Works perfectly offline; online it would "
        "return 'skip' on every single trace. A scorer built for a labelled dataset does not "
        "automatically transfer to unlabelled traffic."
    ),
}


def classify_scorer(name: str) -> tuple:
    """Return (can_run_online, reason) for a scorer name."""
    if name in ONLINE_CAPABLE:
        return True, ONLINE_CAPABLE[name]
    if name in OFFLINE_ONLY:
        return False, OFFLINE_ONLY[name]
    return None, "Unknown scorer — check whether it reads `expectations`."


# ============================================================================
# COST
# ============================================================================

def monitoring_cost(daily_traces, judge_scorers, sample_rate, cost_per_judge_call=0.002):
    """Estimate the daily cost of running LLM judges over production traffic.

    Args:
        daily_traces: requests served per day.
        judge_scorers: how many LLM-judge scorers are registered.
        sample_rate: fraction of traces scored, 0.0-1.0.
        cost_per_judge_call: rough cost of one judge invocation, in currency units.

    Returns a dict with scored-trace count, judge calls, and daily/annual cost.
    Deterministic scorers are deliberately excluded — they cost nothing, which is exactly
    why they should not be sampled.
    """
    scored = daily_traces * sample_rate
    calls = scored * judge_scorers
    daily = calls * cost_per_judge_call
    return {
        "traces_scored_per_day": scored,
        "judge_calls_per_day": calls,
        "cost_per_day": daily,
        "cost_per_year": daily * 365,
    }


# ============================================================================
# STATISTICAL RESOLUTION OF A SAMPLE
# ============================================================================

Z_95 = 1.959963985


def wilson_interval(successes, n, z=Z_95):
    """95% Wilson score interval for a proportion.

    Wilson rather than the normal approximation because monitoring pass rates live near
    1.0, where the normal approximation produces intervals that run past 100% and
    understates uncertainty on small samples — precisely the regime production sampling
    puts you in.
    """
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(0.0, center - margin), min(1.0, center + margin))


def interval_halfwidth(p, n, z=Z_95):
    """Half-width of the Wilson interval for an observed rate — the resolution of a sample."""
    low, high = wilson_interval(p * n, n, z)
    return (high - low) / 2


def min_samples_to_detect(baseline_rate, delta, z=Z_95, max_n=1_000_000):
    """Smallest sample size whose interval half-width is below `delta`.

    Answers the practical question: "we want to catch a `delta` drop in this metric — how
    many traces must we actually score?" Searched numerically rather than solved in closed
    form, because the point is the number, not the algebra.
    """
    n = 10
    while n < max_n:
        if interval_halfwidth(baseline_rate, n, z) < delta:
            return n
        n = int(n * 1.3) + 1
    return None


def required_sample_rate(daily_traces, baseline_rate, delta):
    """Sample rate needed to resolve a `delta` change within one day of traffic.

    Returns None when even 100% sampling of a day's traffic cannot resolve the change —
    a genuinely useful answer, because it means the alert you were about to configure
    could only ever have fired on noise.
    """
    needed = min_samples_to_detect(baseline_rate, delta)
    if needed is None or needed > daily_traces:
        return None
    return needed / daily_traces
