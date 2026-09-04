# -*- coding: utf-8 -*-
"""Load corpus documents and join them with their ACL attributes.

Markdown frontmatter carries only identity (`doc_id`, `title`) - no access-control
data. Permissions come from a separate feed, the ACL manifest
(`ingest/acl_manifest.py`), the stand-in for whatever real system actually owns
entitlements in production (an admin console, an HR/entitlements system, a
Confluence-space-permissions export). The connector's real job is joining the two
by `doc_id` and translating the permission side into our ABAC attributes.

A document with no matching manifest entry has no usable access-control metadata,
so it is refused rather than defaulted to something that looks safe. Getting this
join wrong is the number one cause of enterprise RAG leaks, which is why it lives
in its own, boringly explicit function.
"""
from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..config import SETTINGS
from ..models import Document, ResourceAttributes
from .acl_manifest import load_acl_manifest

DEFAULT_TENANT = "meridian"


def _parse_frontmatter(text: str) -> (Dict[str, str], str):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    meta: Dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, body


def load_corpus(corpus_dir: Optional[Path] = None,
                tenant_id: str = DEFAULT_TENANT,
                acl_manifest_path: Optional[Path] = None) -> List[Document]:
    corpus_dir = Path(corpus_dir or SETTINGS.corpus_dir)
    acl_by_doc_id: Dict[str, ResourceAttributes] = load_acl_manifest(acl_manifest_path, tenant_id)

    docs: List[Document] = []
    for path in sorted(corpus_dir.glob("*.md")):
        raw = io.open(path, encoding="utf-8").read()
        meta, body = _parse_frontmatter(raw)
        doc_id = meta.get("doc_id")
        if not doc_id:
            raise ValueError(f"{path.name} has no doc_id in frontmatter - refusing to index "
                             f"a document with no identity")

        attrs = acl_by_doc_id.get(doc_id)
        if attrs is None:
            raise ValueError(f"{path.name} (doc_id={doc_id!r}) has no entry in the ACL manifest "
                             f"({SETTINGS.acl_manifest_file}) - refusing to index a document with "
                             f"no usable access-control metadata")

        # Content-side metadata, not ACL - when the source content itself last
        # changed. A real connector would read this from the source system's own
        # "last modified" field; here the corpus file's mtime stands in for it.
        attrs.source_updated_at = datetime.fromtimestamp(path.stat().st_mtime).isoformat()

        docs.append(Document(attrs=attrs,
                             title=meta.get("title", doc_id),
                             text=body,
                             uri=f"file://{path.as_posix()}"))
    return docs


def load_ticket_export(path: Optional[Path] = None,
                       tenant_id: str = "acme_helpdesk",
                       acl_manifest_path: Optional[Path] = None) -> List[Document]:
    """The second connector: a Zendesk-shaped JSON ticket export, deliberately
    a completely different shape from the markdown corpus (no frontmatter, no
    per-file identity, a nested `subject`/`description` structure instead).

    Exists to prove `ingest/pipeline.py::ingest()`'s validate/chunk/embed/index
    path is genuinely format-agnostic once `Document` objects exist, rather
    than hardcoded to one file's shape - see `scripts/demo_second_connector.py`.
    Joins against its own ACL manifest, same discipline as `load_corpus()`: a
    ticket with no matching manifest entry is refused, not defaulted.
    """
    data_dir = SETTINGS.corpus_dir.parent
    path = Path(path or data_dir / "ticket_export_acme.json")
    acl_manifest_path = acl_manifest_path or (data_dir / "acl_manifest_acme.json")
    acl_by_doc_id: Dict[str, ResourceAttributes] = load_acl_manifest(acl_manifest_path, tenant_id)

    raw = json.loads(path.read_text(encoding="utf-8"))
    docs: List[Document] = []
    for ticket in raw.get("tickets", []):
        doc_id = f"TKX-{ticket['ticket_id']}"
        attrs = acl_by_doc_id.get(doc_id)
        if attrs is None:
            raise ValueError(f"ticket {ticket['ticket_id']!r} (doc_id={doc_id!r}) has no entry in "
                             f"the ACL manifest ({acl_manifest_path}) - refusing to index a "
                             f"document with no usable access-control metadata")

        attrs.source_updated_at = ticket.get("created_at")
        docs.append(Document(attrs=attrs,
                             title=ticket["subject"],
                             text=f"{ticket['subject']}\n\n{ticket['description']}",
                             uri=f"ticket-export://{ticket['ticket_id']}"))
    return docs
