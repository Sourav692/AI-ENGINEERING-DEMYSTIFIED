# -*- coding: utf-8 -*-
"""Domain model.

Deliberately small and explicit. Every access-control attribute lives on the
`ResourceAttributes` object, so there is exactly one place to look when someone
asks "what does the system know about this document?".
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Any, Dict, List, Optional

# Sensitivity is a ladder, not a set: a principal cleared for `confidential`
# can read everything at or below it. Storing the rank as an int is what lets the
# vector store do a numeric `$lte` pre-filter.
SENSITIVITY_RANK: Dict[str, int] = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3,
}
RANK_TO_SENSITIVITY = {v: k for k, v in SENSITIVITY_RANK.items()}


@dataclass
class ResourceAttributes:
    """The ABAC attributes of a document (and, inherited, of each of its chunks)."""

    doc_id: str
    tenant_id: str
    source: str
    sensitivity: str
    allowed_groups: List[str]
    region: str                             # "EU" | "US" | "GLOBAL"
    product: str = "platform"
    owner: str = "unassigned"
    contains_pii: bool = False
    need_to_know: List[str] = field(default_factory=list)
    valid_from: Optional[str] = None        # ISO date; embargo start
    valid_until: Optional[str] = None       # ISO date; expiry
    source_updated_at: Optional[str] = None # ISO datetime; last change to the content itself
    ingested_at: Optional[str] = None       # ISO datetime; when this pipeline run indexed it
    authority_rank: int = 0                 # non-ACL: higher wins when passages disagree (§4.6)

    @property
    def sensitivity_level(self) -> int:
        return SENSITIVITY_RANK[self.sensitivity]


@dataclass
class Principal:
    """The authenticated caller. Comes from the IdP, never from user input."""

    user_id: str
    display_name: str
    tenant_id: str
    role: str
    groups: List[str]
    clearance: str                          # highest sensitivity readable
    region: str                             # "EU" | "US" | "GLOBAL"
    projects: List[str] = field(default_factory=list)   # need-to-know tags
    can_view_pii: bool = False
    is_external: bool = False

    @property
    def clearance_level(self) -> int:
        return SENSITIVITY_RANK[self.clearance]

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Principal":
        return cls(**d)


@dataclass
class Document:
    """A source document before chunking."""

    attrs: ResourceAttributes
    title: str
    text: str
    uri: str


@dataclass
class Chunk:
    """An indexed unit. Carries a full copy of the parent's ACL attributes.

    Denormalising the ACL onto every chunk is what makes a single-pass pre-filter
    inside the vector store possible - the alternative (join back to a document
    table after retrieval) means retrieving unauthorised vectors first.
    """

    chunk_id: str
    doc_id: str
    title: str
    text: str
    section: str
    ordinal: int
    attrs: ResourceAttributes

    def to_metadata(self) -> Dict[str, Any]:
        """Flatten to Chroma-compatible metadata.

        Chroma metadata values must be scalars - no lists. Group membership is
        therefore encoded as one boolean column per group (`grp__engineering: True`)
        so an `$or` of `$eq True` reproduces list-overlap semantics. This is the
        standard bridge between a rich policy language and a thin filter language.
        """
        md: Dict[str, Any] = {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "title": self.title,
            "section": self.section,
            "ordinal": self.ordinal,
            "tenant_id": self.attrs.tenant_id,
            "source": self.attrs.source,
            "product": self.attrs.product,
            "owner": self.attrs.owner,
            "sensitivity": self.attrs.sensitivity,
            "sensitivity_level": self.attrs.sensitivity_level,
            "region": self.attrs.region,
            "contains_pii": self.attrs.contains_pii,
            "need_to_know": ",".join(self.attrs.need_to_know),
            "valid_from": self.attrs.valid_from or "",
            "valid_until": self.attrs.valid_until or "",
            "source_updated_at": self.attrs.source_updated_at or "",
            "ingested_at": self.attrs.ingested_at or "",
            "authority_rank": self.attrs.authority_rank,
        }
        for g in self.attrs.allowed_groups:
            md[f"grp__{g}"] = True
        return md

    @staticmethod
    def attrs_from_metadata(md: Dict[str, Any]) -> ResourceAttributes:
        groups = [k[len("grp__"):] for k, v in md.items() if k.startswith("grp__") and v]
        ntk = [s for s in str(md.get("need_to_know", "")).split(",") if s]
        return ResourceAttributes(
            doc_id=md["doc_id"],
            tenant_id=md["tenant_id"],
            source=md["source"],
            sensitivity=md["sensitivity"],
            allowed_groups=groups,
            region=md["region"],
            product=md.get("product", "platform"),
            owner=md.get("owner", "unassigned"),
            contains_pii=bool(md.get("contains_pii", False)),
            need_to_know=ntk,
            valid_from=md.get("valid_from") or None,
            valid_until=md.get("valid_until") or None,
            source_updated_at=md.get("source_updated_at") or None,
            ingested_at=md.get("ingested_at") or None,
            authority_rank=int(md.get("authority_rank", 0) or 0),
        )


@dataclass
class ScoredChunk:
    """A chunk with the provenance of how it was retrieved and scored."""

    chunk: Chunk
    score: float = 0.0
    dense_rank: Optional[int] = None
    bm25_rank: Optional[int] = None
    fused_score: Optional[float] = None
    rerank_score: Optional[float] = None
    retrieved_by: List[str] = field(default_factory=list)
    matched_query: Optional[str] = None
    redacted: bool = False

    @property
    def citation(self) -> str:
        return f"[{self.chunk.doc_id}#{self.chunk.ordinal}]"


@dataclass
class Citation:
    doc_id: str
    title: str
    section: str
    source: str
    sensitivity: str


@dataclass
class Answer:
    """The final, user-facing result."""

    text: str
    citations: List[Citation] = field(default_factory=list)
    refused: bool = False
    refusal_reason: Optional[str] = None
    escalate_to_human: bool = False
    strategy: str = "enterprise"
    degraded: bool = False
    degraded_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def today_iso() -> str:
    return date.today().isoformat()
