"""
Measuring whether a judge agrees with humans
============================================

Built in Phase 7. Pure Python, so the reasoning is checkable without a workspace.

The problem this exists to solve
---------------------------------
Every number produced in Phases 2 through 6 came from an LLM judge that nobody validated.
The judges were written by the same person who wrote the agent and the dataset, and their
verdicts were taken at face value throughout. The OpenAI evaluation guide names this
directly as an anti-pattern — "neglecting human feedback for metric validation" — and the
fix it prescribes is to calibrate automated metrics against human judgement.

Calibration needs a number, and the obvious candidate is the wrong one
----------------------------------------------------------------------
The instinct is to watch the judge's **average score**. That is not a measure of judge
quality at all; it's a measure of how generous the judge is. A judge that rates everything
5/5 has a wonderful average and is worthless.

What actually matters is **agreement with the humans whose standards the judge is supposed
to encode**. That is why alignment routinely makes the average score go *down* while making
the judge *better*: an unaligned judge grades against generic best practice and inflates,
and alignment replaces that with the stricter domain standard.

So this module measures agreement three ways, because raw agreement alone misleads:

- `exact_agreement` — the headline number, and the most flattering one.
- `cohens_kappa` — corrects for agreement that would happen by chance. On a skewed rating
  distribution two raters can agree 80% of the time while being statistically independent;
  kappa exposes that, raw agreement does not.
- `quadratic_weighted_kappa` — for ordinal scales (a 1-5 Likert), where being off by one
  point is a near-miss and being off by four is a different opinion entirely. Unweighted
  kappa treats those as the same error.
"""

# ============================================================================
# AGREEMENT MEASURES
# ============================================================================

def exact_agreement(judge_scores, human_scores) -> float:
    """Fraction of items where judge and human gave an identical rating."""
    _check_pair(judge_scores, human_scores)
    if not judge_scores:
        return 0.0
    matches = sum(1 for j, h in zip(judge_scores, human_scores) if j == h)
    return matches / len(judge_scores)


def within_one_agreement(judge_scores, human_scores) -> float:
    """Fraction of items where the two ratings differ by at most one point.

    On a Likert scale this is often the more honest headline: two careful humans frequently
    disagree by a point, so demanding exact matches sets a bar humans themselves fail.
    """
    _check_pair(judge_scores, human_scores)
    if not judge_scores:
        return 0.0
    close = sum(1 for j, h in zip(judge_scores, human_scores) if abs(j - h) <= 1)
    return close / len(judge_scores)


def cohens_kappa(judge_scores, human_scores) -> float:
    """Cohen's kappa: agreement corrected for chance.

    0.0 means "no better than two raters guessing with these marginal frequencies"; 1.0 is
    perfect. Negative values mean systematically worse than chance.
    """
    _check_pair(judge_scores, human_scores)
    n = len(judge_scores)
    if n == 0:
        return 0.0

    categories = sorted(set(judge_scores) | set(human_scores))
    observed = exact_agreement(judge_scores, human_scores)

    # Chance agreement from the two raters' marginal distributions.
    expected = 0.0
    for c in categories:
        p_judge = sum(1 for s in judge_scores if s == c) / n
        p_human = sum(1 for s in human_scores if s == c) / n
        expected += p_judge * p_human

    if expected == 1.0:
        # Both raters used exactly one category for everything; kappa is undefined.
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1 - expected)


def quadratic_weighted_kappa(judge_scores, human_scores, min_rating=None, max_rating=None) -> float:
    """Quadratic weighted kappa, for ordinal rating scales.

    Disagreements are penalised by the *square* of their distance, so a 4-vs-5 disagreement
    barely counts and a 1-vs-5 disagreement counts heavily. This is the right measure for a
    Likert judge; plain kappa treats every disagreement as total.
    """
    _check_pair(judge_scores, human_scores)
    n = len(judge_scores)
    if n == 0:
        return 0.0

    lo = min_rating if min_rating is not None else min(min(judge_scores), min(human_scores))
    hi = max_rating if max_rating is not None else max(max(judge_scores), max(human_scores))
    if hi == lo:
        return 1.0 if exact_agreement(judge_scores, human_scores) == 1.0 else 0.0

    ratings = list(range(int(lo), int(hi) + 1))
    index = {r: i for i, r in enumerate(ratings)}
    k = len(ratings)

    observed = [[0.0] * k for _ in range(k)]
    for j, h in zip(judge_scores, human_scores):
        observed[index[j]][index[h]] += 1

    judge_marginal = [sum(1 for s in judge_scores if s == r) / n for r in ratings]
    human_marginal = [sum(1 for s in human_scores if s == r) / n for r in ratings]

    num = den = 0.0
    for i in range(k):
        for j in range(k):
            weight = ((i - j) ** 2) / ((k - 1) ** 2)
            num += weight * observed[i][j] / n
            den += weight * judge_marginal[i] * human_marginal[j]

    if den == 0:
        return 1.0
    return 1 - num / den


def mean(scores) -> float:
    return sum(scores) / len(scores) if scores else 0.0


def _check_pair(a, b):
    if len(a) != len(b):
        raise ValueError(f"paired ratings must be the same length, got {len(a)} and {len(b)}")


# ============================================================================
# THE BEFORE/AFTER REPORT
# ============================================================================

def alignment_report(human, judge_before, judge_after, min_rating=1, max_rating=5) -> dict:
    """Compare an unaligned and an aligned judge against the same human ratings.

    The shape of the result is the lesson: `mean_score` can fall while every agreement
    measure rises. Read the agreement columns, not the score column.
    """
    def measures(judge):
        return {
            "mean_score": mean(judge),
            "exact_agreement": exact_agreement(judge, human),
            "within_one": within_one_agreement(judge, human),
            "cohens_kappa": cohens_kappa(judge, human),
            "quadratic_weighted_kappa": quadratic_weighted_kappa(
                judge, human, min_rating, max_rating
            ),
        }

    before, after = measures(judge_before), measures(judge_after)
    return {
        "human_mean": mean(human),
        "before": before,
        "after": after,
        "deltas": {k: after[k] - before[k] for k in before},
        # The judge improved if it agrees with the humans more -- regardless of whether its
        # average score went up, down, or nowhere.
        "judge_improved": after["quadratic_weighted_kappa"] > before["quadratic_weighted_kappa"],
        "score_fell": after["mean_score"] < before["mean_score"],
    }


def format_alignment_report(report: dict) -> str:
    """Render the report with the interpretation attached, since it is counterintuitive."""
    lines = [
        f"{'MEASURE':<30}{'BEFORE':>10}{'AFTER':>10}{'DELTA':>10}",
        "-" * 60,
    ]
    labels = {
        "mean_score": "mean score (NOT quality)",
        "exact_agreement": "exact agreement",
        "within_one": "within-one agreement",
        "cohens_kappa": "Cohen's kappa",
        "quadratic_weighted_kappa": "quadratic weighted kappa",
    }
    for key, label in labels.items():
        lines.append(
            f"{label:<30}{report['before'][key]:>10.3f}{report['after'][key]:>10.3f}"
            f"{report['deltas'][key]:>+10.3f}"
        )

    lines.append("")
    lines.append(f"human mean rating: {report['human_mean']:.3f}")
    lines.append("")
    if report["judge_improved"] and report["score_fell"]:
        lines.append("VERDICT: the judge got BETTER and its average score went DOWN.")
        lines.append("  The unaligned judge was inflating. The aligned one applies the")
        lines.append("  experts' standard, which is stricter. This is a success, not a")
        lines.append("  regression -- the agent did not change at all between these runs.")
    elif report["judge_improved"]:
        lines.append("VERDICT: the judge agrees with the experts more than it did.")
    else:
        lines.append("VERDICT: alignment did NOT improve agreement. Check that the label")
        lines.append("  schema name matches the judge name -- if they differ, align() cannot")
        lines.append("  pair SME ratings with judge scores and silently learns nothing.")
    return "\n".join(lines)
