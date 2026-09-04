# -*- coding: utf-8 -*-
"""Chroma-backed vector store with per-tenant collections.

Two isolation layers, deliberately:

  1. **Physical** - one collection per tenant. A missing or malformed metadata
     filter still cannot return another tenant's data, because it is not in the
     collection being queried.
  2. **Logical** - the compiled ABAC pre-filter inside the collection.

Defence in depth. If the interviewer asks "what if someone forgets the filter?",
the answer is that the blast radius stops at the tenant boundary.

Chunk metadata here (including ACL fields) is a DENORMALISED COPY used only for
the Layer-1 pre-filter pushdown. The authoritative ACL source is the separate
SQLite catalog (ingest/catalog.py), read fresh by the Layer-2 post-retrieval
check - see get_doc_attrs() below.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

# Must be set before chromadb is imported; the library reads it at import time.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.telemetry.product.posthog import Posthog as _ChromaPosthog

from . import catalog
from ..config import SETTINGS
from ..models import Chunk, ResourceAttributes, ScoredChunk


def _drop_chroma_telemetry(self, event) -> None:
    """Chroma 0.5 still calls posthog.capture(distinct_id, event, props) even when
    anonymized_telemetry is False (it only sets posthog.disabled). PostHog SDK 6+
    made those arguments keyword-only, so every collection open logs
    ClientCreateCollectionEvent. Retrieval is unaffected; drop the send.
    """


_ChromaPosthog._direct_capture = _drop_chroma_telemetry

_client: Optional[chromadb.ClientAPI] = None


def get_client(settings=SETTINGS) -> chromadb.ClientAPI:
    global _client
    if _client is None:
        settings.chroma_dir.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(settings.chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )
    return _client


def reset_store(settings=SETTINGS, tenant_id: Optional[str] = None):
    """Wipe the index - the WHOLE store by default, or just one tenant's
    collection if `tenant_id` is given.

    A bug caught while adding a second connector/tenant to this demo: the
    unscoped version deletes `chroma_dir` wholesale, which is every tenant's
    data, not just the one being re-ingested. Ingesting a brand-new
    "acme_helpdesk" tenant with `reset=True` silently wiped the unrelated
    22-document "meridian" corpus that was already indexed - `pipeline.ingest()`
    now always passes its own `tenant_id` through so a normal reset only ever
    touches the tenant actually being ingested.
    """
    global _client
    if tenant_id is not None:
        client = get_client(settings)
        try:
            client.delete_collection(name=settings.collection_for(tenant_id))
        except Exception:
            pass   # collection didn't exist yet - nothing to delete
        return
    _client = None
    if settings.chroma_dir.exists():
        shutil.rmtree(settings.chroma_dir, ignore_errors=True)


def get_collection(tenant_id: str, settings=SETTINGS):
    client = get_client(settings)
    return client.get_or_create_collection(
        name=settings.collection_for(tenant_id),
        metadata={"hnsw:space": "cosine", "tenant_id": tenant_id},
    )


def get_doc_attrs(doc_id: str, settings=SETTINGS) -> Optional[ResourceAttributes]:
    """Authoritative document attributes - a fresh SQLite lookup, not a vector query.

    This is the Layer-2 source of truth (see authz/enforcement.py::enforce() and
    docs/04 §0). It is independent of whatever a chunk's denormalised Chroma
    metadata says, and independent of embeddings entirely - an ACL change never
    needs to touch the vector index.
    """
    attrs = catalog.get_doc_attrs(doc_id, settings)
    if attrs is not None:
        return attrs
    # Fall back to a live index scan only if the catalog has no row for this doc
    # (e.g. a test/demo that wrote straight to Chroma without going through the
    # ingest pipeline). In a real deployment the catalog is always populated first.
    try:
        col = get_collection("meridian", settings)
        res = col.get(where={"doc_id": {"$eq": doc_id}}, limit=1, include=["metadatas"])
        if res["metadatas"]:
            return Chunk.attrs_from_metadata(res["metadatas"][0])
    except Exception:
        pass
    return None


def upsert_chunks(tenant_id: str, chunks: List[Chunk],
                  embeddings: List[List[float]], settings=SETTINGS) -> int:
    if not chunks:
        return 0
    col = get_collection(tenant_id, settings)
    col.upsert(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[c.to_metadata() for c in chunks],
    )
    return len(chunks)


def _to_scored(ids, docs, metas, distances, retrieved_by: str,
               matched_query: Optional[str]) -> List[ScoredChunk]:
    out: List[ScoredChunk] = []
    for rank, (cid, text, md, dist) in enumerate(zip(ids, docs, metas, distances)):
        chunk = Chunk(
            chunk_id=cid,
            doc_id=md["doc_id"],
            title=md["title"],
            text=text,
            section=md.get("section", ""),
            ordinal=int(md.get("ordinal", 0)),
            attrs=Chunk.attrs_from_metadata(md),
        )
        out.append(ScoredChunk(
            chunk=chunk,
            score=1.0 - float(dist),        # cosine distance -> similarity
            dense_rank=rank,
            retrieved_by=[retrieved_by],
            matched_query=matched_query,
        ))
    return out


def dense_search(tenant_id: str,
                 query_embedding: List[float],
                 where: Optional[Dict[str, Any]],
                 k: int,
                 matched_query: Optional[str] = None,
                 settings=SETTINGS) -> List[ScoredChunk]:
    """Vector search *with the ACL pre-filter applied inside the store*.

    This is the line that matters: unauthorised chunks are never scored, never
    ranked, never returned. Post-filtering instead would leak through result
    counts and would silently degrade top-k quality for restricted users.
    """
    col = get_collection(tenant_id, settings)
    res = col.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    if not res["ids"] or not res["ids"][0]:
        return []
    return _to_scored(res["ids"][0], res["documents"][0], res["metadatas"][0],
                      res["distances"][0], "dense", matched_query)


def fetch_all_allowed(tenant_id: str,
                      where: Optional[Dict[str, Any]],
                      settings=SETTINGS) -> List[Chunk]:
    """Every chunk this principal may see - the candidate pool for BM25.

    A lexical index cannot push an ACL filter down the way a vector store can, so
    the honest approach is to build the keyword index over the *already authorised*
    subset. At real scale this becomes a per-principal-group cached BM25 shard or a
    hybrid store like Elasticsearch with document-level security; the semantics are
    the same and that trade-off is worth naming out loud.
    """
    col = get_collection(tenant_id, settings)
    res = col.get(where=where, include=["documents", "metadatas"])
    chunks: List[Chunk] = []
    for cid, text, md in zip(res["ids"], res["documents"], res["metadatas"]):
        chunks.append(Chunk(
            chunk_id=cid,
            doc_id=md["doc_id"],
            title=md["title"],
            text=text,
            section=md.get("section", ""),
            ordinal=int(md.get("ordinal", 0)),
            attrs=Chunk.attrs_from_metadata(md),
        ))
    return chunks


def collection_stats(tenant_id: str, settings=SETTINGS) -> Dict[str, Any]:
    col = get_collection(tenant_id, settings)
    res = col.get(include=["metadatas"])
    by_source: Dict[str, int] = {}
    by_sensitivity: Dict[str, int] = {}
    docs = set()
    for md in res["metadatas"]:
        by_source[md["source"]] = by_source.get(md["source"], 0) + 1
        by_sensitivity[md["sensitivity"]] = by_sensitivity.get(md["sensitivity"], 0) + 1
        docs.add(md["doc_id"])
    return {"chunks": len(res["ids"]), "documents": len(docs),
            "by_source": by_source, "by_sensitivity": by_sensitivity}
