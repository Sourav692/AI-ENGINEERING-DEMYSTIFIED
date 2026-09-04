# -*- coding: utf-8 -*-
"""Per-source freshness tracking and a persisted rejected-docs record (§4.2).

Extends `IngestReport.rejected` from an ephemeral in-memory list - gone the
moment the ingest script process exits - into a queryable record: which
document, from which source, was rejected and why, and when each source was
last successfully synced. "Last successful sync" is a first-class,
user-visible signal per the prep doc, not something you have to infer from a
log file.

Shares the ACL catalog's SQLite file (`ingest/catalog.py`) rather than opening
a second database - this is the same kind of local ingest bookkeeping, just two
more tables. A side effect worth naming: an unscoped `catalog.reset_catalog()`
(no `tenant_id`) deletes and recreates the whole file, wiping freshness/rejection
history along with every tenant's ACL rows - correct for "start completely
fresh," which is why `pipeline.ingest()` instead passes its own `tenant_id`
through by default, scoping a normal reset to one tenant's `documents` rows
only. Freshness/rejection rows themselves are not tenant-scoped (they're keyed
by source and doc_id, not tenant), so they persist across a tenant-scoped
reset either way.
"""
from __future__ import annotations

import sqlite3
from typing import List, Optional

from ..config import SETTINGS
from . import catalog

_SCHEMA = """
CREATE TABLE IF NOT EXISTS source_freshness (
    source          TEXT PRIMARY KEY,
    last_synced_at  TEXT NOT NULL,
    documents_seen  INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS rejected_docs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id       TEXT NOT NULL,
    source       TEXT,
    reason       TEXT NOT NULL,
    rejected_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS document_hashes (
    doc_id       TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    hashed_at    TEXT NOT NULL
);
"""


def _conn(settings=SETTINGS) -> sqlite3.Connection:
    conn = catalog.get_connection(settings)
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def record_sync(source: str, synced_at: str, documents_seen: int, settings=SETTINGS):
    """One source just finished a successful ingest pass."""
    conn = _conn(settings)
    conn.execute(
        """
        INSERT INTO source_freshness (source, last_synced_at, documents_seen)
        VALUES (?, ?, ?)
        ON CONFLICT(source) DO UPDATE SET
            last_synced_at=excluded.last_synced_at, documents_seen=excluded.documents_seen
        """,
        (source, synced_at, documents_seen),
    )
    conn.commit()


def record_rejection(doc_id: str, source: Optional[str], reason: str, rejected_at: str,
                     settings=SETTINGS):
    """One document failed ACL validation and was refused, not indexed."""
    conn = _conn(settings)
    conn.execute(
        "INSERT INTO rejected_docs (doc_id, source, reason, rejected_at) VALUES (?, ?, ?, ?)",
        (doc_id, source, reason, rejected_at),
    )
    conn.commit()


def last_synced(source: str, settings=SETTINGS) -> Optional[str]:
    conn = _conn(settings)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT last_synced_at FROM source_freshness WHERE source = ?", (source,)).fetchone()
    return row["last_synced_at"] if row else None


def all_freshness(settings=SETTINGS) -> List[sqlite3.Row]:
    """Every source's last-sync timestamp - the "is this stale?" dashboard row."""
    conn = _conn(settings)
    conn.row_factory = sqlite3.Row
    return conn.execute("SELECT * FROM source_freshness ORDER BY source").fetchall()


def recent_rejections(limit: int = 50, settings=SETTINGS) -> List[sqlite3.Row]:
    conn = _conn(settings)
    conn.row_factory = sqlite3.Row
    return conn.execute(
        "SELECT * FROM rejected_docs ORDER BY rejected_at DESC, id DESC LIMIT ?", (limit,)
    ).fetchall()


def get_content_hash(doc_id: str, settings=SETTINGS) -> Optional[str]:
    """The content hash recorded the last time this doc_id was actually
    embedded - what incremental sync compares against to decide whether a
    document's CONTENT changed (as opposed to just its ACL, which never needs
    this check - see catalog.py)."""
    conn = _conn(settings)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT content_hash FROM document_hashes WHERE doc_id = ?", (doc_id,)).fetchone()
    return row["content_hash"] if row else None


def set_content_hash(doc_id: str, content_hash: str, hashed_at: str, settings=SETTINGS):
    conn = _conn(settings)
    conn.execute(
        """
        INSERT INTO document_hashes (doc_id, content_hash, hashed_at) VALUES (?, ?, ?)
        ON CONFLICT(doc_id) DO UPDATE SET
            content_hash=excluded.content_hash, hashed_at=excluded.hashed_at
        """,
        (doc_id, content_hash, hashed_at),
    )
    conn.commit()
