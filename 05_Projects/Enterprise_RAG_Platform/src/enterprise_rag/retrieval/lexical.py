# -*- coding: utf-8 -*-
"""BM25 keyword retrieval over the ACL-authorised candidate pool.

Why this exists at all: enterprise questions are full of tokens that embeddings
handle badly - `MRD-5031`, `ws_vtx_eu_001`, `ING-2291`, `99.9%`. An embedding of
"MRD-5031" sits near every other error code in vector space, because they look
alike. BM25 treats it as a rare token and nails it.

Dense search finds things that *mean* the same. Lexical search finds things that
*say* the same. Enterprise corpora need both, which is why hybrid + RRF is the
default strategy in this platform.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from rank_bm25 import BM25Okapi

from ..models import Chunk, ScoredChunk

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*")


def tokenize(text: str) -> List[str]:
    """Keep hyphenated identifiers intact - `MRD-5031` must not become `mrd`,`5031`."""
    return [t.lower() for t in TOKEN_RE.findall(text)]


class BM25Index:
    """A BM25 index built per request over the principal's authorised chunks.

    Rebuilding per request is honest for a demo corpus and wrong at scale; the
    production answer is a lexical store that supports document-level security
    natively (Elasticsearch/OpenSearch DLS) or a cached per-group shard. Naming
    that trade-off is more valuable in the interview than hiding it.
    """

    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self._corpus = [tokenize(c.text) for c in chunks]
        self._bm25 = BM25Okapi(self._corpus) if self._corpus else None

    def search(self, query: str, k: int, matched_query: Optional[str] = None) -> List[ScoredChunk]:
        if not self._bm25:
            return []
        scores = self._bm25.get_scores(tokenize(query))
        ordered: List[Tuple[int, float]] = sorted(
            enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
        out: List[ScoredChunk] = []
        for rank, (idx, s) in enumerate(ordered):
            if s <= 0:
                continue                      # no lexical overlap at all
            out.append(ScoredChunk(
                chunk=self.chunks[idx],
                score=float(s),
                bm25_rank=rank,
                retrieved_by=["bm25"],
                matched_query=matched_query or query,
            ))
        return out
