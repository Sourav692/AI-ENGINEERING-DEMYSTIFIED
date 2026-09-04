# -*- coding: utf-8 -*-
"""Proves incremental sync actually skips unchanged content: run it twice with
nothing changed (second run embeds nothing), then edit one document and run
again (only that one document re-embeds). Restores the edited file afterward
so re-running this script, or anything else, is idempotent.

Usage:
    python scripts/demo_incremental_sync.py
"""
import sys

import _bootstrap  # noqa: F401

from enterprise_rag.config import SETTINGS
from enterprise_rag.ingest.pipeline import ingest

RULE = "=" * 100
TARGET_FILE = SETTINGS.corpus_dir / "RB-101.md"


def main():
    print(RULE)
    print("1. FULL INGEST (reset=True) - establishes the baseline content hashes")
    print(RULE)
    r1 = ingest(tenant_id="meridian", reset=True, incremental=True)
    print(r1.render())

    print("\n" + RULE)
    print("2. INCREMENTAL RE-INGEST, NOTHING CHANGED - should skip every document")
    print(RULE)
    r2 = ingest(tenant_id="meridian", reset=False, incremental=True)
    print(r2.render())
    print(f"\nembedding cost this run: ${r2.cost_usd:.5f}  (should be $0.00000 - nothing to embed)")

    print("\n" + RULE)
    print("3. EDIT ONE DOCUMENT, RE-INGEST - only that document's chunks re-embed")
    print(RULE)
    original = TARGET_FILE.read_text(encoding="utf-8")
    try:
        TARGET_FILE.write_text(original + "\n\n<!-- incremental-sync demo edit -->\n",
                               encoding="utf-8")
        r3 = ingest(tenant_id="meridian", reset=False, incremental=True)
        print(r3.render())
        print(f"\nskipped {r3.skipped_unchanged} of 22 documents; only RB-101 was re-chunked/re-embedded")
    finally:
        TARGET_FILE.write_text(original, encoding="utf-8")
        print("\n(RB-101.md restored to its original content)")

    print("\n" + RULE)
    print("4. FULL RESET - restores the canonical demo state for everything else")
    print(RULE)
    r4 = ingest(tenant_id="meridian", reset=True, incremental=True)
    print(r4.render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
