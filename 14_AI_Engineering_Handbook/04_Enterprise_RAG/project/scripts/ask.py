# -*- coding: utf-8 -*-
"""Ask one question as one persona.

Examples:
    python scripts/ask.py --user u_marco_t3 "why did EU ingest stall on 14 March?"
    python scripts/ask.py --user u_lena_t1  --strategy dense "what is MRD-5031?"
    python scripts/ask.py --list-users
"""
import argparse
import sys
import textwrap

import _bootstrap  # noqa: F401

from enterprise_rag.graph.build import RAGPlatform
from enterprise_rag.identity import get_principal, list_principals
from enterprise_rag.retrieval.strategies import STRATEGIES


def render(result, show_trace=True, show_context=False):
    answer, trace = result["answer"], result["trace"]

    print("=" * 78)
    print(f"ANSWER  (strategy={answer.strategy}"
          f"{', REFUSED' if answer.refused else ''}"
          f"{', DEGRADED' if answer.degraded else ''})")
    print("=" * 78)
    for para in answer.text.split("\n"):
        print(textwrap.fill(para, 78) if para.strip() else "")

    if answer.citations:
        print("\nSources:")
        for c in answer.citations:
            print(f"  [{c.doc_id}] {c.title}  ({c.source}/{c.sensitivity})")

    if show_context:
        print("\nContext shown to the model:")
        for row in trace.candidates:
            print(f"  {row['chunk_id']:<18} {row['source']:<11} {row['sensitivity']:<12} "
                  f"rerank={row['rerank']}  via={'+'.join(row['retrieved_by'])}"
                  f"{'  [REDACTED]' if row['redacted'] else ''}")

    if show_trace:
        print("\n" + "-" * 78)
        print(f"access filter : {trace.prefilter_explained}")
        if trace.generated_queries:
            print(f"query variants: {len(trace.generated_queries)}")
            for q in trace.generated_queries:
                print(f"    - {q}")
        if trace.subquestions:
            print(f"sub-questions : {trace.subquestions}")
        if trace.denied:
            print(f"denied        : {len(trace.denied)} chunks")
            seen = set()
            for d in trace.denied:
                key = (d["doc_id"], d["rule"])
                if key in seen:
                    continue
                seen.add(key)
                print(f"    - {d['doc_id']:<16} {d['rule']:<20} {d['reason']}")
        if trace.redacted_count:
            print(f"redacted      : {trace.redacted_count} chunks (PII obligation)")
        if trace.security_events:
            print(f"SECURITY      : {len(trace.security_events)} pre-filter disagreements!")
        if trace.groundedness is not None:
            print(f"groundedness  : {trace.groundedness:.2f}")
        print()
        print(trace.timeline())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="*")
    ap.add_argument("--user", default="u_marco_t3")
    ap.add_argument("--strategy", default="enterprise", choices=sorted(STRATEGIES))
    ap.add_argument("--as-of", default=None, help="pin 'today' (YYYY-MM-DD) for embargo rules")
    ap.add_argument("--context", action="store_true", help="show the retrieved context")
    ap.add_argument("--list-users", action="store_true")
    args = ap.parse_args()

    if args.list_users:
        for p in list_principals():
            print(f"{p.user_id:<26} {p.display_name:<28} {p.role}")
            print(f"{'':<26} groups={p.groups} clearance={p.clearance} region={p.region} "
                  f"projects={p.projects} external={p.is_external}")
        return 0

    if not args.question:
        ap.error("give a question, or use --list-users")

    principal = get_principal(args.user)
    question = " ".join(args.question)

    print(f"\nUser     : {principal.display_name} - {principal.role}")
    print(f"Question : {question}\n")

    platform = RAGPlatform()
    result = platform.ask(question, principal, strategy=args.strategy, as_of=args.as_of)
    render(result, show_context=args.context)
    return 0


if __name__ == "__main__":
    sys.exit(main())
