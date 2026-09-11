"""
The evaluation harness.

Three things make up an evaluation: a set of examples, one or more scores you
can compute on each result, and a summary across all of them.

The scores here come in two flavours, and the difference matters:

  Checkable   - a rule decides, the same way every time, for free.
                Use these wherever you possibly can.
  Judged      - another model gives an opinion, because no rule can capture
                "is this written well". Slower, costs money, and will not
                give you the identical number twice.

Most real systems lean on the checkable ones and use a judge only for the
part that genuinely needs taste.
"""

import time
from statistics import mean

from helpers import get_llm

from .agents import run
from .dataset import CASES

judge_llm = get_llm()


def patiently(fn, *args, attempts=4):
    """Retry on rate limits.

    An evaluation fires far more requests than normal use, so shared model
    endpoints will push back. Waiting and retrying is the whole fix.
    """
    for attempt in range(attempts):
        try:
            return fn(*args)
        except Exception as exc:
            transient = "rate" in str(exc).lower() or "429" in str(exc)
            if not transient or attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt)   # 1s, 2s, 4s ...


# ---------------------------------------------------------------------------
# Checkable scores -- plain rules, no model involved
# ---------------------------------------------------------------------------

def score_routing(case, result) -> float:
    """Did the right specialists get involved? 1.0 if exactly the expected set."""
    used = {name for name in result["trajectory"] if name != "supervisor"}
    if not case.expect_agents:
        return 1.0
    return 1.0 if used == case.expect_agents else 0.0


def score_content(case, result) -> float:
    """Does the answer mention what it has to? Fraction of required snippets found."""
    if not case.expect_text:
        return 1.0
    answer = result["answer"].lower()
    hits = sum(1 for snippet in case.expect_text if snippet.lower() in answer)
    return hits / len(case.expect_text)


def score_efficiency(case, result) -> float:
    """Fewer hand-offs is better. Full marks at 3 supervisor turns or fewer."""
    return 1.0 if result["turns"] <= 3 else round(3 / result["turns"], 2)


# ---------------------------------------------------------------------------
# Judged score -- a second model gives an opinion
# ---------------------------------------------------------------------------

JUDGE_PROMPT = """Rate the reply below from 1 to 5.

5 = answers the request completely and reads naturally
1 = does not answer the request, or is confusing

Request: {task}
Reply: {answer}

Respond with a single digit and nothing else."""


def score_quality(case, result) -> float:
    """Ask a model how good the answer reads. Returns 0.0-1.0."""
    reply = patiently(
        lambda p: judge_llm.invoke(p).content.strip(),
        JUDGE_PROMPT.format(task=case.task, answer=result["answer"]),
    )

    digit = next((ch for ch in reply if ch.isdigit()), None)
    if digit is None:
        return 0.0
    return round(min(int(digit), 5) / 5, 2)


SCORES = {
    "routing": score_routing,
    "content": score_content,
    "efficiency": score_efficiency,
    "quality": score_quality,
}


# ---------------------------------------------------------------------------
# Running the whole set
# ---------------------------------------------------------------------------

def evaluate(cases=None) -> dict:
    """Run every case, score it, and summarise. Returns rows plus averages."""
    cases = cases or CASES
    rows = []

    for case in cases:
        result = patiently(run, case.task)

        row = {
            "id": case.id,
            "task": case.task,
            "answer": result["answer"],
            "trajectory": " -> ".join(result["trajectory"]),
            "turns": result["turns"],
        }
        for name, fn in SCORES.items():
            try:
                row[name] = fn(case, result)
            except Exception:
                # A broken score should not sink the whole run.
                row[name] = None
        rows.append(row)

    summary = {}
    for name in SCORES:
        values = [r[name] for r in rows if r[name] is not None]
        summary[name] = round(mean(values), 2) if values else None
    summary["cases"] = len(rows)

    return {"rows": rows, "summary": summary}
