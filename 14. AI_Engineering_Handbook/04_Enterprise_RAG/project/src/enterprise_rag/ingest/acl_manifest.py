# -*- coding: utf-8 -*-
"""The ACL manifest - where access-control data is actually authored.

Content and permissions are two different feeds from two different owners, so they
live in two different files. `data/corpus/*.md` is content (what a document says);
`data/acl_manifest.json` is permissions (who may read it) - the stand-in for
whatever real system actually owns this in production (an entitlements/HR system,
an admin console, a Confluence-space-permissions export). Markdown frontmatter
carries only `doc_id` and `title` - identity, not access control.

`loader.py` joins the two by `doc_id` to build a `ResourceAttributes` per document,
which is what gets denormalised onto chunks (the Layer-1 cache) and written into
the SQLite ACL catalog (the Layer-2 source of truth) - see ingest/catalog.py.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from ..config import SETTINGS
from ..models import ResourceAttributes


def load_acl_manifest(path: Optional[Path] = None,
                      tenant_id: str = "meridian") -> Dict[str, ResourceAttributes]:
    """Read the ACL manifest file into a doc_id -> ResourceAttributes map."""
    path = Path(path or SETTINGS.acl_manifest_file)
    data = json.loads(path.read_text(encoding="utf-8"))

    out: Dict[str, ResourceAttributes] = {}
    for rec in data["documents"]:
        out[rec["doc_id"]] = ResourceAttributes(
            doc_id=rec["doc_id"],
            tenant_id=tenant_id,
            source=rec["source"],
            sensitivity=rec["sensitivity"],
            allowed_groups=list(rec.get("allowed_groups") or []),
            region=rec.get("region", "GLOBAL"),
            product=rec.get("product", "platform"),
            owner=rec.get("owner", "unassigned"),
            contains_pii=bool(rec.get("contains_pii", False)),
            need_to_know=list(rec.get("need_to_know") or []),
            valid_from=rec.get("valid_from") or None,
            valid_until=rec.get("valid_until") or None,
        )
    return out
