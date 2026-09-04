# -*- coding: utf-8 -*-
"""The access-control demo: one question, many personas, provably different answers.

This is the script to run in front of an interviewer. It shows, without any LLM
involvement in the security decision, that:

  1. the same question returns different material to different roles,
  2. denials are attributed to a named policy rule,
  3. a cross-tenant principal gets literally nothing,
  4. compartment (need-to-know) and embargo rules bite even at full clearance,
  5. revoking a group in the IdP takes effect on the very next query, with no
     reindexing, and is caught by the post-retrieval check as a pre-filter
     disagreement.

Usage:
    python scripts/demo_access_control.py             # the full demo
    python scripts/demo_access_control.py --matrix    # just the visibility matrix (no LLM cost)
"""
import argparse
import sys
from collections import defaultdict

import _bootstrap  # noqa: F401

from enterprise_rag.authz.policy import compile_prefilter, decide, explain_prefilter
from enterprise_rag.graph.build import RAGPlatform
from enterprise_rag.identity import get_principal, list_principals
from enterprise_rag.ingest.loader import load_corpus
from enterprise_rag.ingest.store import fetch_all_allowed

RULE = "=" * 100
SUB = "-" * 100


# ---------------------------------------------------------------------------
def visibility_matrix(as_of=None):
    """Document x persona visibility, computed by the policy engine alone.

    No embeddings, no LLM, no retrieval. Pure policy - which is the point: access
    control is decidable statically and is never delegated to the model.
    """
    docs = load_corpus()
    principals = [p for p in list_principals()]

    print(RULE)
    print("VISIBILITY MATRIX - decided by the policy engine only (no LLM involved)")
    print(RULE)

    header = f"{'document':<16}{'src':<11}{'sens':<13}"
    for p in principals:
        header += f"{p.user_id.replace('u_', '')[:9]:>11}"
    print(header)
    print(SUB)

    denials = defaultdict(int)
    for d in sorted(docs, key=lambda x: (x.attrs.source, x.attrs.doc_id)):
        row = f"{d.attrs.doc_id:<16}{d.attrs.source:<11}{d.attrs.sensitivity:<13}"
        for p in principals:
            dec = decide(p, d.attrs, {"as_of": as_of})
            row += f"{('  Y' if dec.allowed else '  .'):>11}"
            if not dec.allowed:
                denials[dec.rule] += 1
        print(row)

    print(SUB)
    legend = f"{'':<40}"
    for p in principals:
        legend += f"{p.user_id.replace('u_', '')[:9]:>11}"
    print(legend)
    print(f"\nY = readable    . = denied\n")

    print("Denials by rule:")
    for rule, n in sorted(denials.items(), key=lambda kv: -kv[1]):
        print(f"  {rule:<22} {n}")

    print("\nPersonas:")
    for p in principals:
        print(f"  {p.user_id:<26} {p.role}")
        print(f"  {'':<26} clearance={p.clearance:<13} region={p.region:<7} "
              f"groups={','.join(p.groups)}"
              f"{'  projects=' + ','.join(p.projects) if p.projects else ''}"
              f"{'  EXTERNAL' if p.is_external else ''}")


# ---------------------------------------------------------------------------
def candidate_pool_sizes():
    """How much of the index each persona can even see, straight from the store."""
    print("\n" + RULE)
    print("RETRIEVABLE POOL - chunks surviving the compiled pre-filter, per persona")
    print(RULE)
    for p in list_principals():
        where = compile_prefilter(p)
        try:
            pool = fetch_all_allowed(p.tenant_id, where)
        except Exception:
            pool = []
        by_source = defaultdict(int)
        for c in pool:
            by_source[c.attrs.source] += 1
        detail = ", ".join(f"{k}={v}" for k, v in sorted(by_source.items())) or "nothing"
        print(f"  {p.user_id:<26} {len(pool):>3} chunks   {detail}")
        print(f"  {'':<26} filter: {explain_prefilter(p)}")


# ---------------------------------------------------------------------------
def same_question_many_users(question, users, strategy="hybrid", as_of=None):
    platform = RAGPlatform()
    print("\n" + RULE)
    print(f"SAME QUESTION, DIFFERENT PRINCIPALS   (strategy={strategy})")
    print(f'Q: "{question}"')
    print(RULE)

    for uid in users:
        p = get_principal(uid)
        result = platform.ask(question, p, strategy=strategy, as_of=as_of)
        ans, tr = result["answer"], result["trace"]

        print(f"\n### {p.display_name} - {p.role}")
        print(f"    clearance={p.clearance} region={p.region} groups={','.join(p.groups)}")
        print(SUB)
        text = ans.text.strip().replace("\n", "\n    ")
        print(f"    {text[:900]}")
        if ans.citations:
            print(f"\n    cited: {', '.join(c.doc_id + ' (' + c.sensitivity + ')' for c in ans.citations)}")
        else:
            print("\n    cited: none")
        if tr.denied:
            rules = sorted({d["rule"] for d in tr.denied})
            docs = sorted({d["doc_id"] for d in tr.denied})
            print(f"    denied: {len(tr.denied)} chunks from {docs} by rule(s) {rules}")
        if tr.redacted_count:
            print(f"    redacted: {tr.redacted_count} chunks (PII obligation)")


# ---------------------------------------------------------------------------
def live_revocation_demo(question, as_of=None):
    """Revoke a group between two queries. No reindexing. Next query enforces it.

    This is the demo that answers "what happens when someone leaves the team?" -
    the index still holds the vectors, but the principal's resolved attributes no
    longer satisfy the policy, so the material becomes unreachable immediately.
    """
    platform = RAGPlatform()
    print("\n" + RULE)
    print("LIVE REVOCATION - group removed in the IdP, no reindexing, next query is enforced")
    print(RULE)

    p = get_principal("u_marco_t3")
    print(f'\nQ: "{question}"')
    print(f"\n[BEFORE] {p.display_name} groups={p.groups}")
    before = platform.ask(question, p, strategy="hybrid", as_of=as_of)
    print(f"  answer  : {before['answer'].text.strip()[:260]}")
    print(f"  cited   : {[c.doc_id for c in before['answer'].citations] or 'none'}")
    print(f"  refused : {before['answer'].refused}")

    # Simulate the IdP change: Marco moves off the escalation rota.
    p_after = get_principal("u_marco_t3")
    p_after.groups = ["support-tier1"]
    p_after.clearance = "internal"
    p_after.role = "Tier 1 Support Agent"

    print(f"\n[AFTER ] {p_after.display_name} groups={p_after.groups} clearance={p_after.clearance}")
    after = platform.ask(question, p_after, strategy="hybrid", as_of=as_of)
    print(f"  answer  : {after['answer'].text.strip()[:260]}")
    print(f"  cited   : {[c.doc_id for c in after['answer'].citations] or 'none'}")
    print(f"  refused : {after['answer'].refused}")
    print("\n  The index was not touched. Only the resolved principal changed.")


# ---------------------------------------------------------------------------
def embargo_demo():
    """The same principal, the same document, two different dates."""
    print("\n" + RULE)
    print("TIME-BOUND POLICY - an embargoed advisory, before and after its publication date")
    print(RULE)

    docs = {d.attrs.doc_id: d for d in load_corpus()}
    advisory = docs["SA-2026-07"]
    ravi = get_principal("u_ravi_sec")       # restricted clearance + vuln-response
    erin = get_principal("u_erin_secmgr")    # restricted clearance, NO compartment

    print(f"\ndocument : {advisory.attrs.doc_id} ({advisory.attrs.sensitivity}, "
          f"embargoed until {advisory.attrs.valid_from}, "
          f"need-to-know={advisory.attrs.need_to_know})")

    for who in (ravi, erin):
        print(f"\n  {who.display_name} (clearance={who.clearance}, projects={who.projects or 'none'})")
        for as_of in ("2026-08-22", "2026-09-02"):
            dec = decide(who, advisory.attrs, {"as_of": as_of})
            verdict = "ALLOW" if dec.allowed else f"DENY  [{dec.rule}]"
            print(f"    as of {as_of}:  {verdict:<26} {dec.reason}")

    print("\n  Clearance alone is not enough: Erin is cleared for 'restricted' but lacks the")
    print("  vuln-response compartment, so the date never helps her.")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", action="store_true", help="policy-only sections (no LLM cost)")
    ap.add_argument("--as-of", default="2026-08-22")
    args = ap.parse_args()

    visibility_matrix(as_of=args.as_of)
    candidate_pool_sizes()
    embargo_demo()

    if args.matrix:
        print("\n(--matrix: skipping the LLM-backed sections)")
        return 0

    same_question_many_users(
        "What caused the Vertex Financial ingestion problem in March, and are they owed service credits?",
        ["u_lena_t1", "u_marco_t3", "u_sofia_am", "u_tom_contractor", "u_attacker_other_tenant"],
        strategy="hybrid", as_of=args.as_of)

    live_revocation_demo(
        "What was the root cause of the March EU ingest incident?", as_of=args.as_of)

    return 0


if __name__ == "__main__":
    sys.exit(main())
