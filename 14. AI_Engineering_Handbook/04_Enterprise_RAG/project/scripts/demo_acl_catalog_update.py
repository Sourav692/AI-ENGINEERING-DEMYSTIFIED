# -*- coding: utf-8 -*-
"""ACL catalog demo: change a document's access rule, no reindexing.

This is the resource-side counterpart to demo_access_control.py's
live_revocation_demo() (which changes the PRINCIPAL). Here the DOCUMENT's ACL
changes instead - a real admin action, e.g. "loosen this runbook to internal" or
"tighten this doc to restricted" - and the very next query enforces it, because
Layer 2 reads the SQLite catalog fresh every time. No vector re-embedding, no
Chroma write, at all.

Usage:
    python scripts/demo_acl_catalog_update.py
"""
import sys

import _bootstrap  # noqa: F401

from enterprise_rag.authz.enforcement import enforce
from enterprise_rag.identity import get_principal
from enterprise_rag.ingest import catalog
from enterprise_rag.ingest.loader import load_corpus
from enterprise_rag.models import Chunk, ScoredChunk

RULE = "=" * 100
DOC_ID = "RB-101"          # Runbook, sensitivity=internal today


def _candidate(doc_id: str) -> ScoredChunk:
    """One fake retrieved chunk for doc_id, as if a strategy had just returned it."""
    doc = {d.attrs.doc_id: d for d in load_corpus()}[doc_id]
    chunk = Chunk(chunk_id=f"{doc_id}#0", doc_id=doc_id, title=doc.title,
                  text=doc.text[:400], section="", ordinal=0, attrs=doc.attrs)
    return ScoredChunk(chunk=chunk, score=1.0, retrieved_by=["demo"])


def main():
    print(RULE)
    print("ACL CATALOG LIVE UPDATE - change a document's rule, no reindexing")
    print(RULE)

    lena = get_principal("u_lena_t1")   # clearance=internal, groups=[support-tier1]

    print(f"\nprincipal : {lena.display_name}  clearance={lena.clearance}  "
          f"groups={lena.groups}")
    print(f"document  : {DOC_ID}")

    before_attrs = catalog.get_doc_attrs(DOC_ID)
    if before_attrs is None:
        print(f"\n'{DOC_ID}' is not in the ACL catalog yet - run scripts/ingest.py first.")
        return 1
    print(f"\n[BEFORE] sensitivity={before_attrs.sensitivity}  "
          f"allowed_groups={before_attrs.allowed_groups}")

    cand = _candidate(DOC_ID)
    report = enforce(lena, [cand], {"as_of": "2026-08-22"})
    verdict = "ALLOW" if report.allowed else f"DENY [{report.denied[0][1].rule}]"
    print(f"          enforce() -> {verdict}")

    # The admin action: grant Lena's group access, directly on the catalog row.
    # This is a SQLite UPDATE. Nothing in data/chroma/ is touched.
    print(f"\n>>> catalog.update_attr('{DOC_ID}', allowed_groups=[...+'support-tier1'])")
    new_groups = sorted(set(before_attrs.allowed_groups) | {"support-tier1"})
    catalog.update_attr(DOC_ID, allowed_groups=new_groups)

    after_attrs = catalog.get_doc_attrs(DOC_ID)
    print(f"\n[AFTER ] sensitivity={after_attrs.sensitivity}  "
          f"allowed_groups={after_attrs.allowed_groups}")

    cand2 = _candidate(DOC_ID)   # a fresh "retrieval" - chunk.attrs still says the OLD groups
    report2 = enforce(lena, [cand2], {"as_of": "2026-08-22"})
    verdict2 = "ALLOW" if report2.allowed else f"DENY [{report2.denied[0][1].rule}]"
    print(f"          enforce() -> {verdict2}")

    print("\nNote: cand2's chunk.attrs (the Chroma copy) still says the OLD groups - only")
    print("the catalog changed. enforce() ignored that stale copy and read the catalog")
    print("fresh, which is exactly why the verdict flipped with zero reindexing.")

    # Roll back so re-running this script is idempotent.
    catalog.update_attr(DOC_ID, allowed_groups=before_attrs.allowed_groups)
    return 0


if __name__ == "__main__":
    sys.exit(main())
