# -*- coding: utf-8 -*-
"""The ACL catalog - a SQLite table of document-level access-control attributes.

This is the "row in the document catalogue" the rest of the codebase's docstrings
already promised. It is deliberately a *separate* store from the vector index:

  - the vector store (ingest/store.py) holds a DENORMALISED COPY of these
    attributes on every chunk, used only to push the ABAC pre-filter into the
    Chroma query (Layer 1 - cheap, allowed to be stale);
  - this catalog is the AUTHORITATIVE source, queried fresh by the post-retrieval
    enforcement check (Layer 2 - authz/enforcement.py::enforce()) and by citation
    verification. A permission change here does not require touching the vector
    index or re-embedding anything - see update_attr() below.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import SETTINGS
from ..models import ResourceAttributes

_conn: Optional[sqlite3.Connection] = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id          TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL,
    source          TEXT NOT NULL,
    sensitivity     TEXT NOT NULL,
    region          TEXT NOT NULL,
    product         TEXT NOT NULL DEFAULT 'platform',
    owner           TEXT NOT NULL DEFAULT 'unassigned',
    contains_pii    INTEGER NOT NULL DEFAULT 0,
    allowed_groups  TEXT NOT NULL DEFAULT '[]',   -- JSON list
    need_to_know    TEXT NOT NULL DEFAULT '[]',   -- JSON list
    valid_from      TEXT,
    valid_until     TEXT,
    source_updated_at TEXT,
    ingested_at     TEXT,
    authority_rank  INTEGER NOT NULL DEFAULT 0
);
"""


_COLUMN_DEFAULTS = {
    "source_updated_at": "TEXT",
    "ingested_at": "TEXT",
    "authority_rank": "INTEGER NOT NULL DEFAULT 0",
}


def _migrate(conn: sqlite3.Connection):
    """`CREATE TABLE IF NOT EXISTS` only creates a table that doesn't exist yet -
    it does NOT add new columns to one that already does, so an on-disk catalog
    from before a schema change is missing them and every read of that column
    raises. This adds whatever's missing, in place, without touching existing
    rows or requiring a full reset - a real bug hit while adding
    `authority_rank` to an already-ingested demo database."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(documents)")}
    for column, decl in _COLUMN_DEFAULTS.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE documents ADD COLUMN {column} {decl}")
    conn.commit()


def get_connection(settings=SETTINGS) -> sqlite3.Connection:
    """Cached connection, created lazily - mirrors ingest/store.py::get_client()."""
    global _conn
    if _conn is None:
        settings.acl_catalog_path.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(settings.acl_catalog_path), check_same_thread=False)
        _conn.execute(_SCHEMA)
        _conn.commit()
        _migrate(_conn)
    return _conn


def reset_catalog(settings=SETTINGS, tenant_id: Optional[str] = None):
    """Drop and recreate the table - the WHOLE catalog by default, or just one
    tenant's rows if `tenant_id` is given. Same tenant-scoping fix as
    `ingest/store.py::reset_store()`, for the same reason: an unscoped reset
    while ingesting one tenant deletes every other tenant's ACL rows too."""
    global _conn
    if tenant_id is not None:
        conn = get_connection(settings)
        conn.execute("DELETE FROM documents WHERE tenant_id = ?", (tenant_id,))
        conn.commit()
        return
    if _conn is not None:
        _conn.close()
        _conn = None
    if settings.acl_catalog_path.exists():
        settings.acl_catalog_path.unlink()
    get_connection(settings)


def _row_to_attrs(row: sqlite3.Row) -> ResourceAttributes:
    return ResourceAttributes(
        doc_id=row["doc_id"],
        tenant_id=row["tenant_id"],
        source=row["source"],
        sensitivity=row["sensitivity"],
        allowed_groups=json.loads(row["allowed_groups"]),
        region=row["region"],
        product=row["product"],
        owner=row["owner"],
        contains_pii=bool(row["contains_pii"]),
        need_to_know=json.loads(row["need_to_know"]),
        valid_from=row["valid_from"],
        valid_until=row["valid_until"],
        source_updated_at=row["source_updated_at"],
        ingested_at=row["ingested_at"],
        authority_rank=row["authority_rank"] or 0,
    )


def upsert_doc_attrs(attrs: ResourceAttributes, settings=SETTINGS):
    """Write (or overwrite) one document's authoritative ACL row."""
    conn = get_connection(settings)
    conn.execute(
        """
        INSERT INTO documents
            (doc_id, tenant_id, source, sensitivity, region, product, owner,
             contains_pii, allowed_groups, need_to_know, valid_from, valid_until,
             source_updated_at, ingested_at, authority_rank)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(doc_id) DO UPDATE SET
            tenant_id=excluded.tenant_id, source=excluded.source,
            sensitivity=excluded.sensitivity, region=excluded.region,
            product=excluded.product, owner=excluded.owner,
            contains_pii=excluded.contains_pii, allowed_groups=excluded.allowed_groups,
            need_to_know=excluded.need_to_know, valid_from=excluded.valid_from,
            valid_until=excluded.valid_until, source_updated_at=excluded.source_updated_at,
            ingested_at=excluded.ingested_at, authority_rank=excluded.authority_rank
        """,
        (attrs.doc_id, attrs.tenant_id, attrs.source, attrs.sensitivity, attrs.region,
         attrs.product, attrs.owner, int(attrs.contains_pii),
         json.dumps(attrs.allowed_groups), json.dumps(attrs.need_to_know),
         attrs.valid_from, attrs.valid_until, attrs.source_updated_at, attrs.ingested_at,
         attrs.authority_rank),
    )
    conn.commit()


def upsert_many(attrs_list: List[ResourceAttributes], settings=SETTINGS):
    for a in attrs_list:
        upsert_doc_attrs(a, settings)


def get_doc_attrs(doc_id: str, settings=SETTINGS) -> Optional[ResourceAttributes]:
    """The authoritative lookup - one indexed SELECT, no vector query involved."""
    conn = get_connection(settings)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
    row = cur.fetchone()
    return _row_to_attrs(row) if row else None


def update_attr(doc_id: str, **fields: Any):
    """Change one or more ACL fields on an already-catalogued document.

    Demonstrates the point of the split: this touches ONLY this SQLite row. No
    re-embedding, no Chroma write, no reindexing - and the very next call to
    enforce() for this doc_id sees the new value, because Layer 2 reads the
    catalog fresh on every request.
    """
    attrs = get_doc_attrs(doc_id)
    if attrs is None:
        raise KeyError(f"'{doc_id}' is not in the ACL catalog")
    for k, v in fields.items():
        if not hasattr(attrs, k):
            raise AttributeError(f"ResourceAttributes has no field '{k}'")
        setattr(attrs, k, v)
    upsert_doc_attrs(attrs)
    return attrs


def all_doc_ids(settings=SETTINGS) -> List[str]:
    conn = get_connection(settings)
    return [r[0] for r in conn.execute("SELECT doc_id FROM documents").fetchall()]
