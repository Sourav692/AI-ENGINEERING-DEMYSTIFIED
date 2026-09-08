# -*- coding: utf-8 -*-
"""Build the index.  Usage:  python scripts/ingest.py [--keep]"""
import argparse
import sys

import _bootstrap  # noqa: F401

from enterprise_rag.config import SETTINGS
from enterprise_rag.ingest.pipeline import ingest
from enterprise_rag.ingest.store import collection_stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="do not wipe the existing index")
    ap.add_argument("--tenant", default="meridian")
    args = ap.parse_args()

    print(f"corpus     : {SETTINGS.corpus_dir}")
    print(f"index      : {SETTINGS.chroma_dir}")
    print(f"collection : {SETTINGS.collection_for(args.tenant)}")
    print(f"embeddings : {SETTINGS.embedding_model}\n")

    report = ingest(tenant_id=args.tenant, reset=not args.keep)
    print(report.render())

    if report.rejected:
        print("\nIngestion refused one or more documents. Fix their frontmatter and re-run.")
        return 1

    print("\nindex verification:")
    for k, v in collection_stats(args.tenant).items():
        print(f"  {k:16} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
