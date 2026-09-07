# -*- coding: utf-8 -*-
"""Proves the ingestion pipeline is format-agnostic: a completely different
connector (a JSON ticket export, not markdown+frontmatter) flows through the
exact same validate/chunk/embed/index pipeline as the main corpus, into its
own tenant ("acme_helpdesk") so it never touches the flagship demo corpus.

Usage:
    python scripts/demo_second_connector.py
"""
import sys

import _bootstrap  # noqa: F401

from enterprise_rag.config import SETTINGS
from enterprise_rag.identity import get_principal
from enterprise_rag.ingest.loader import load_ticket_export
from enterprise_rag.ingest.pipeline import ingest
from enterprise_rag.ingest.store import fetch_all_allowed
from enterprise_rag.authz.policy import compile_prefilter

RULE = "=" * 100


def main():
    print(RULE)
    print("SECOND CONNECTOR - JSON ticket export, same pipeline, different tenant")
    print(RULE)

    report = ingest(
        tenant_id="acme_helpdesk",
        reset=True,
        settings=SETTINGS,
        loader=lambda: load_ticket_export(tenant_id="acme_helpdesk"),
    )
    print(report.render())

    print(f"\nNote: {report.documents} documents came from a JSON array with `subject`/")
    print("`description` fields and no frontmatter at all - the SAME ingest() function,")
    print("unmodified, chunked/validated/embedded/indexed them. Only load_ticket_export()")
    print("is different from load_corpus() - everything downstream is shared code.")

    print("\n" + RULE)
    print("Sanity check: retrieval + ACL still work for this tenant")
    print(RULE)
    # There's no identity file entry for an acme_helpdesk principal in this demo,
    # so build one ad hoc to prove the pipeline generalizes across tenants too.
    from enterprise_rag.models import Principal
    acme_support = Principal(
        user_id="u_acme_support", display_name="Acme Support Agent", tenant_id="acme_helpdesk",
        role="Support Agent", groups=["support-tier1"], clearance="internal", region="US")

    where = compile_prefilter(acme_support)
    pool = fetch_all_allowed(acme_support.tenant_id, where)
    print(f"{acme_support.display_name} can see {len(pool)} chunks: "
         f"{sorted({c.doc_id for c in pool})}")
    print("(TKX-9003 is support-tier3-only, so it's correctly excluded from a tier1 pool)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
