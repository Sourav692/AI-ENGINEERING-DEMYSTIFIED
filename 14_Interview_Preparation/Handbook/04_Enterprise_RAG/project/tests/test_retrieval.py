# -*- coding: utf-8 -*-
"""Retrieval-layer tests.

Split into two groups:
  - pure unit tests (RRF, tokenisation, chunking) that need nothing external
  - store-level tests that need an index but still no LLM, by asserting on the
    ACL pre-filter rather than on answer quality

Anything needing OpenAI lives in test_pipeline.py and is marked `llm`.
"""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from enterprise_rag.authz.policy import compile_prefilter                  # noqa: E402
from enterprise_rag.identity import get_principal                          # noqa: E402
from enterprise_rag.ingest.chunker import chunk_document                   # noqa: E402
from enterprise_rag.ingest.loader import load_corpus                       # noqa: E402
from enterprise_rag.ingest.store import fetch_all_allowed                  # noqa: E402
from enterprise_rag.models import Chunk, Document, ResourceAttributes, ScoredChunk  # noqa: E402
from enterprise_rag.retrieval.fusion import reciprocal_rank_fusion         # noqa: E402
from enterprise_rag.retrieval.lexical import BM25Index, tokenize           # noqa: E402


def _chunk(cid, text="x", doc_id=None, source="helpcenter"):
    attrs = ResourceAttributes(doc_id=doc_id or cid.split("#")[0], tenant_id="meridian",
                               source=source, sensitivity="public",
                               allowed_groups=["public"], region="GLOBAL")
    return Chunk(chunk_id=cid, doc_id=attrs.doc_id, title="t", text=text,
                 section="", ordinal=0, attrs=attrs)


def _scored(cid, text="x", by="dense"):
    return ScoredChunk(chunk=_chunk(cid, text), retrieved_by=[by])


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------
def test_rrf_rewards_agreement_across_lists():
    """A doc placed 2nd by both retrievers beats one placed 1st by only one."""
    list_a = [_scored("A#0"), _scored("B#0")]          # A 1st, B 2nd
    list_b = [_scored("C#0", by="bm25"), _scored("B#0", by="bm25")]   # C 1st, B 2nd

    fused = reciprocal_rank_fusion([list_a, list_b], k=60)
    assert fused[0].chunk.chunk_id == "B#0", "agreement across retrievers should win"


def test_rrf_merges_provenance():
    fused = reciprocal_rank_fusion([[_scored("A#0", by="dense")],
                                    [_scored("A#0", by="bm25")]])
    assert sorted(fused[0].retrieved_by) == ["bm25", "dense"]


def test_rrf_deduplicates():
    fused = reciprocal_rank_fusion([[_scored("A#0")], [_scored("A#0")], [_scored("A#0")]])
    assert len(fused) == 1


def test_rrf_handles_empty_lists():
    assert reciprocal_rank_fusion([[], []]) == []
    fused = reciprocal_rank_fusion([[], [_scored("A#0")]])
    assert len(fused) == 1


def test_rrf_smoothing_constant_flattens_rank_advantage():
    """A large k compresses the gap between 1st and 2nd place - that is its job.

    Note: fusion annotates the ScoredChunk objects it is given, so each call needs
    its own freshly built inputs rather than a shared list.
    """
    def gap(k):
        fused = reciprocal_rank_fusion([[_scored("A#0"), _scored("B#0")]], k=k)
        return fused[0].fused_score - fused[1].fused_score

    assert gap(1000) < gap(1)


# ---------------------------------------------------------------------------
# Lexical retrieval
# ---------------------------------------------------------------------------
def test_tokenizer_preserves_hyphenated_identifiers():
    """`MRD-5031` must survive as one token, or BM25's whole advantage is lost."""
    toks = tokenize("Error MRD-5031 hit workspace ws_vtx_eu_001 (ticket TK-4471).")
    assert "mrd-5031" in toks
    assert "ws_vtx_eu_001" in toks
    assert "tk-4471" in toks


def test_bm25_finds_exact_identifier():
    chunks = [_chunk("A#0", "General guidance about ingesting metrics and buffers."),
              _chunk("B#0", "Error MRD-5031 means the write-ahead buffer is full."),
              _chunk("C#0", "Query timeouts are reported as MRD-4080.")]
    hits = BM25Index(chunks).search("MRD-5031", k=3)
    assert hits and hits[0].chunk.chunk_id == "B#0"


def test_bm25_returns_nothing_on_zero_overlap():
    chunks = [_chunk("A#0", "ingest backpressure and compaction")]
    assert BM25Index(chunks).search("parental leave policy", k=5) == []


def test_bm25_empty_index_is_safe():
    assert BM25Index([]).search("anything", k=5) == []


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def test_chunks_carry_parent_acl():
    doc = load_corpus()[0]
    chunks = chunk_document(doc)
    assert chunks
    for c in chunks:
        assert c.attrs.sensitivity == doc.attrs.sensitivity
        assert c.attrs.allowed_groups == doc.attrs.allowed_groups
        assert c.attrs.tenant_id == doc.attrs.tenant_id


def test_chunk_text_is_prefixed_with_title_for_retrievability():
    doc = next(d for d in load_corpus() if d.attrs.doc_id == "HC-002")
    for c in chunk_document(doc):
        assert c.text.startswith(doc.title)


def test_metadata_roundtrip_preserves_groups_and_compartments():
    attrs = ResourceAttributes(doc_id="D1", tenant_id="meridian", source="advisory",
                               sensitivity="restricted",
                               allowed_groups=["security", "engineering"],
                               region="GLOBAL", need_to_know=["vuln-response"],
                               valid_from="2026-09-01", contains_pii=True)
    c = Chunk(chunk_id="D1#0", doc_id="D1", title="t", text="body",
              section="s", ordinal=0, attrs=attrs)
    back = Chunk.attrs_from_metadata(c.to_metadata())
    assert sorted(back.allowed_groups) == ["engineering", "security"]
    assert back.need_to_know == ["vuln-response"]
    assert back.valid_from == "2026-09-01"
    assert back.sensitivity == "restricted"
    assert back.contains_pii is True


def test_metadata_values_are_all_chroma_scalars():
    """Chroma rejects list values - this is why groups are boolean columns."""
    attrs = ResourceAttributes(doc_id="D1", tenant_id="meridian", source="ticket",
                               sensitivity="internal", allowed_groups=["a", "b"],
                               region="EU", need_to_know=["x"])
    md = Chunk(chunk_id="D1#0", doc_id="D1", title="t", text="b", section="",
               ordinal=0, attrs=attrs).to_metadata()
    for k, v in md.items():
        assert isinstance(v, (str, int, float, bool)), f"{k} is {type(v)}"


# ---------------------------------------------------------------------------
# Store-level ACL enforcement (needs an index, no LLM)
# ---------------------------------------------------------------------------
@pytest.mark.index
def test_prefiltered_pool_never_exceeds_clearance():
    for uid in ["u_lena_t1", "u_marco_t3", "u_sofia_am", "u_tom_contractor"]:
        p = get_principal(uid)
        pool = fetch_all_allowed(p.tenant_id, compile_prefilter(p))
        assert pool, f"{uid} retrieved nothing at all - index missing?"
        for c in pool:
            assert c.attrs.sensitivity_level <= p.clearance_level, \
                f"{uid} pool contains {c.chunk_id} at {c.attrs.sensitivity}"


@pytest.mark.index
def test_cross_tenant_pool_is_empty():
    p = get_principal("u_attacker_other_tenant")
    assert fetch_all_allowed(p.tenant_id, compile_prefilter(p)) == []


@pytest.mark.index
def test_tier1_pool_contains_no_commercial_or_postmortem_material():
    p = get_principal("u_lena_t1")
    sources = {c.attrs.source for c in fetch_all_allowed(p.tenant_id, compile_prefilter(p))}
    assert sources.isdisjoint({"contract", "pricing", "postmortem", "advisory"})


@pytest.mark.index
def test_us_engineer_pool_excludes_eu_locked_documents():
    p = get_principal("u_jin_us_t3")
    docs = {c.doc_id for c in fetch_all_allowed(p.tenant_id, compile_prefilter(p))}
    assert "PM-2026-03-14" not in docs      # EU-locked
    assert "TK-4471" not in docs            # EU-locked ticket
    assert "RB-101" in docs                 # GLOBAL runbook still visible
