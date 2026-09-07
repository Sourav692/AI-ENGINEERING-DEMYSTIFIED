# -*- coding: utf-8 -*-
"""The ingestion pipeline: load -> validate ACLs -> chunk -> embed -> index.

The validation step is deliberately loud. A document that reaches the index without
usable access-control metadata is a latent data leak, so the pipeline refuses it
rather than defaulting it to "internal" and hoping.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional

from ..config import SETTINGS
from ..llm.client import LLMClient
from ..models import SENSITIVITY_RANK, Chunk, Document
from . import catalog, freshness, store
from .chunker import chunk_corpus
from .loader import load_corpus


def _content_hash(doc: Document) -> str:
    """Content only, deliberately - an ACL-only change never needs this check
    at all (the catalog is always refreshed unconditionally below), so hashing
    attrs in here would make incremental sync skip re-embedding LESS often for
    no benefit."""
    return hashlib.sha256(doc.text.encode("utf-8")).hexdigest()


@dataclass
class IngestReport:
    documents: int = 0
    chunks: int = 0
    embedded: int = 0
    skipped_unchanged: int = 0
    rejected: List[str] = field(default_factory=list)
    by_source: Dict[str, int] = field(default_factory=dict)
    by_sensitivity: Dict[str, int] = field(default_factory=dict)
    cost_usd: float = 0.0

    def render(self) -> str:
        lines = [f"documents indexed : {self.documents}",
                 f"chunks indexed    : {self.chunks}",
                 f"embedding cost    : ${self.cost_usd:.5f}"]
        if self.skipped_unchanged:
            lines.append(f"skipped unchanged : {self.skipped_unchanged}  "
                        f"(incremental sync - content hash matched)")
        if self.rejected:
            lines.append(f"REJECTED          : {len(self.rejected)}  "
                        f"(persisted - see freshness.recent_rejections())")
            lines.extend(f"    - {r}" for r in self.rejected)
        lines.append("by source         : " + ", ".join(
            f"{k}={v}" for k, v in sorted(self.by_source.items())))
        lines.append("by sensitivity    : " + ", ".join(
            f"{k}={v}" for k, v in sorted(self.by_sensitivity.items(),
                                          key=lambda kv: SENSITIVITY_RANK[kv[0]])))
        return "\n".join(lines)


def validate_acl(doc: Document) -> Optional[str]:
    """Refuse anything we cannot enforce a policy on. Returns an error string or None."""
    a = doc.attrs
    if a.sensitivity not in SENSITIVITY_RANK:
        return f"{a.doc_id}: unknown sensitivity '{a.sensitivity}'"
    if not a.allowed_groups:
        return f"{a.doc_id}: no allowed_groups - refusing to index an unowned document"
    if a.region not in {"EU", "US", "GLOBAL"}:
        return f"{a.doc_id}: unknown region '{a.region}'"
    if a.sensitivity == "public" and "public" not in a.allowed_groups:
        return f"{a.doc_id}: marked public but the 'public' group is not in allowed_groups"
    if a.sensitivity != "public" and "public" in a.allowed_groups:
        return f"{a.doc_id}: non-public document grants the 'public' group"
    return None


def ingest(tenant_id: str = "meridian",
           reset: bool = True,
           batch_size: int = 64,
           settings=SETTINGS,
           loader: Optional[Callable[[], List[Document]]] = None,
           incremental: bool = False) -> IngestReport:
    """Load -> validate -> chunk -> embed -> index.

    `loader` lets a different connector's `Document` list flow through this
    same validate/chunk/embed/index path - defaults to the markdown corpus
    loader. This is the proof that the pipeline is format-agnostic once
    `Document` objects exist, not hardcoded to one file's shape - see
    `ingest/loader.py::load_ticket_export()` for the second connector this
    demo ships.

    `incremental`, when True AND `reset` is False, skips chunking/embedding for
    any accepted document whose content hash is unchanged since the last run
    recorded one - only what actually changed gets re-embedded. It has no
    effect when combined with `reset=True`: a stored hash only means "already
    embedded" relative to an index that's still there, and reset just wiped
    it - comparing against a pre-reset hash would skip re-embedding into an
    index that no longer has those vectors. The ACL catalog is always
    refreshed regardless of either flag; a permission-only change was already
    reindex-free before this existed (see docs/06 §2).
    """
    report = IngestReport()

    if reset:
        # Tenant-scoped, not global - see store.py::reset_store()'s docstring
        # for the bug this fixes: an unscoped reset while ingesting one tenant
        # used to wipe every other tenant's already-indexed data too.
        store.reset_store(settings, tenant_id=tenant_id)
        catalog.reset_catalog(settings, tenant_id=tenant_id)

    load_fn = loader or (lambda: load_corpus(settings.corpus_dir, tenant_id))
    docs = load_fn()
    ingested_at = datetime.now().isoformat()
    accepted: List[Document] = []
    for d in docs:
        err = validate_acl(d)
        if err:
            report.rejected.append(err)
            # Persisted, not just printed - a DLQ entry that survives past this
            # process exiting, queryable later by source or by doc_id.
            freshness.record_rejection(d.attrs.doc_id, d.attrs.source, err, ingested_at, settings)
        else:
            accepted.append(d)
    report.documents = len(accepted)

    for d in accepted:
        d.attrs.ingested_at = ingested_at

    # Per-source "last successful sync" - a first-class, user-visible signal
    # (§4.2), not something inferred from a log file. Every source with at
    # least one accepted document in this run gets its timestamp bumped.
    accepted_by_source: Dict[str, int] = {}
    for d in accepted:
        accepted_by_source[d.attrs.source] = accepted_by_source.get(d.attrs.source, 0) + 1
    for source, count in accepted_by_source.items():
        freshness.record_sync(source, ingested_at, count, settings)

    # The ACL catalog is the authoritative source (Layer 2 reads it fresh on every
    # request). It is populated here, independently of embedding/chunking below -
    # a permission-only change later never needs to touch this step again.
    catalog.upsert_many([d.attrs for d in accepted], settings)

    # A content hash only means "already embedded" relative to a vector index
    # that's still there to compare against. `reset=True` just wiped it, so a
    # stored hash from before the reset is stale and comparing against it would
    # skip re-embedding into an index that no longer has those vectors -
    # silently producing a near-empty "successful" ingest. A real bug caught
    # while building this: running reset=True with incremental=True together
    # skipped 21 of 22 documents because their hashes matched records from
    # before the reset, leaving the freshly-wiped collection mostly empty.
    # Incremental skipping is therefore only meaningful when NOT resetting.
    to_embed: List[Document] = accepted
    if incremental and not reset:
        to_embed = []
        for d in accepted:
            h = _content_hash(d)
            if freshness.get_content_hash(d.attrs.doc_id, settings) == h:
                report.skipped_unchanged += 1
                continue
            to_embed.append(d)
            freshness.set_content_hash(d.attrs.doc_id, h, ingested_at, settings)
    else:
        for d in accepted:
            freshness.set_content_hash(d.attrs.doc_id, _content_hash(d), ingested_at, settings)

    chunks: List[Chunk] = chunk_corpus(to_embed, settings)
    report.chunks = len(chunks)
    for c in chunks:
        report.by_source[c.attrs.source] = report.by_source.get(c.attrs.source, 0) + 1
        report.by_sensitivity[c.attrs.sensitivity] = \
            report.by_sensitivity.get(c.attrs.sensitivity, 0) + 1

    llm = LLMClient(settings)
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        vectors = llm.embed([c.text for c in batch], purpose="embed_document")
        report.embedded += store.upsert_chunks(tenant_id, batch, vectors, settings)

    report.cost_usd = llm.usage.cost_usd
    return report
