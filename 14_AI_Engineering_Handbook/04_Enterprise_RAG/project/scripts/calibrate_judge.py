# -*- coding: utf-8 -*-
"""Calibrates the groundedness LLM-judge against hand-labeled cases (§4.5) -
the calibration step candidates skip, per the prep doc's own note.

Runs `GROUNDEDNESS_SYSTEM` (the exact prompt `graph/nodes.py::verify()` uses in
production) against a small, hand-labeled set of (answer, passages) pairs built
to span the spectrum: fully grounded, fully fabricated, one wrong date, one
partially-grounded mixed case. Reports the judge's agreement with the human
labels, not just "the judge ran."

Usage:
    python scripts/calibrate_judge.py
"""
import json
import sys

import _bootstrap  # noqa: F401

from enterprise_rag.config import SETTINGS
from enterprise_rag.graph.prompts import GROUNDEDNESS_SYSTEM
from enterprise_rag.llm.client import LLMClient, LLMUnavailable

RULE = "=" * 100
AGREEMENT_TOLERANCE = 0.25   # judge and human within this band counts as "agree"


def main():
    cases = json.loads((SETTINGS.corpus_dir.parent / "judge_calibration_set.json")
                       .read_text(encoding="utf-8"))["cases"]
    llm = LLMClient(SETTINGS)

    print(RULE)
    print(f"JUDGE CALIBRATION - {len(cases)} hand-labeled cases, tolerance +/-{AGREEMENT_TOLERANCE}")
    print(RULE)

    diffs = []
    agreements = 0
    for case in cases:
        passages_text = "\n\n".join(f"[{p['doc_id']}] {p['text']}" for p in case["passages"])
        try:
            result = llm.chat_json(
                GROUNDEDNESS_SYSTEM,
                f"Answer:\n{case['answer']}\n\nPassages:\n{passages_text}",
                purpose="groundedness_calibration")
            judge_score = float(result.get("groundedness", 0.0))
        except (LLMUnavailable, TypeError, ValueError) as e:
            print(f"  {case['id']:<5} JUDGE UNAVAILABLE: {e}")
            continue

        human = case["human_groundedness"]
        diff = abs(judge_score - human)
        agree = diff <= AGREEMENT_TOLERANCE
        agreements += int(agree)
        diffs.append(diff)

        tag = "AGREE" if agree else "DISAGREE"
        print(f"  {case['id']:<5} {tag:<9} judge={judge_score:.2f}  human={human:.2f}  "
             f"diff={diff:.2f}  ({case['note']})")

    print(RULE)
    if diffs:
        mae = sum(diffs) / len(diffs)
        print(f"agreement rate : {agreements}/{len(diffs)} ({agreements / len(diffs):.0%})")
        print(f"mean abs error : {mae:.3f}")
        print(f"total cost     : ${llm.usage.cost_usd:.5f}")
    else:
        print("no cases scored - judge was unavailable for all of them")

    print("\nThis is what 'calibrated against human labels' actually looks like: a number, not an")
    print("assertion. Re-run whenever GROUNDEDNESS_SYSTEM changes, and gate a prompt change on this")
    print("not regressing, the same way a retrieval change is gated on evaluation/harness.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
