# -*- coding: utf-8 -*-
"""Run the golden-set evaluation.

    python scripts/evaluate.py                          # enterprise strategy, all cases
    python scripts/evaluate.py --kinds security         # the security gate only
    python scripts/evaluate.py --compare dense hybrid multi_query hyde enterprise
"""
import argparse
import sys

import _bootstrap  # noqa: F401

from enterprise_rag.evaluation.harness import compare_strategies, run_eval
from enterprise_rag.retrieval.strategies import STRATEGIES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", default="enterprise", choices=sorted(STRATEGIES))
    ap.add_argument("--kinds", nargs="*", default=None,
                    choices=["quality", "security", "behaviour"])
    ap.add_argument("--compare", nargs="*", default=None)
    args = ap.parse_args()

    if args.compare:
        for s in args.compare:
            if s not in STRATEGIES:
                ap.error(f"unknown strategy '{s}'")
        print(f"Comparing {len(args.compare)} strategies on the golden set "
              f"({'all kinds' if not args.kinds else ', '.join(args.kinds)})...\n")
        rows = compare_strategies(args.compare, kinds=args.kinds, verbose=True)

        cols = list(rows[0].keys())
        widths = {c: max(len(c), max(len(str(r[c])) for r in rows)) + 2 for c in cols}
        print("\n" + "".join(c.ljust(widths[c]) for c in cols))
        print("-" * sum(widths.values()))
        for r in rows:
            print("".join(str(r[c]).ljust(widths[c]) for c in cols))

        leaked = [r for r in rows if r["leaks"] > 0]
        print("\nSECURITY GATE: " + ("PASS - zero leaks across all strategies"
                                     if not leaked else
                                     f"FAIL - {[r['strategy'] for r in leaked]} leaked"))
        return 1 if leaked else 0

    print(f"Running golden set with strategy='{args.strategy}'\n")
    report = run_eval(args.strategy, kinds=args.kinds)
    print("\n" + "=" * 70)
    print(report.render())
    print("=" * 70)
    return 0 if report.leak_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
