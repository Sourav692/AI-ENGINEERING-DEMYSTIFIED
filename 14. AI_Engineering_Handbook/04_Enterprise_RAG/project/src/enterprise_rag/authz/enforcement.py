# -*- coding: utf-8 -*-
"""Post-retrieval enforcement: the authoritative access check.

Everything retrieved from the vector store is treated as *candidate* material that
passed a cached, possibly stale filter. This module re-resolves the principal's
attributes from the identity provider and re-evaluates the full policy before any
text is allowed near the model.

It also carries out obligations - currently PII redaction - and records a security
event whenever the pre-filter and the post-check disagree, which is the signal that
the index is stale or the filter is wrong.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..models import Principal, ScoredChunk
from .policy import Decision, decide

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"\b(?:\+\d{1,3}[ -]?)?(?:\(\d{2,4}\)[ -]?)?\d{3,4}[ -]?\d{3,4}\b")


@dataclass
class EnforcementReport:
    """What enforcement did, in a form that can be logged and asserted on in tests."""

    allowed: List[ScoredChunk] = field(default_factory=list)
    denied: List[Tuple[ScoredChunk, Decision]] = field(default_factory=list)
    redacted_count: int = 0
    audit_events: List[Dict[str, Any]] = field(default_factory=list)
    filter_disagreements: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def denied_doc_ids(self) -> List[str]:
        return sorted({sc.chunk.doc_id for sc, _ in self.denied})

    def summary(self) -> str:
        parts = [f"{len(self.allowed)} allowed", f"{len(self.denied)} denied"]
        if self.redacted_count:
            parts.append(f"{self.redacted_count} redacted")
        if self.filter_disagreements:
            parts.append(f"{len(self.filter_disagreements)} PREFILTER DISAGREEMENTS")
        return ", ".join(parts)


def redact_pii(text: str) -> Tuple[str, int]:
    """Mask direct identifiers. Deliberately conservative and simple.

    In production this would be a dedicated PII service (Presidio, a cloud DLP API)
    - the point here is that redaction is an *obligation attached to an allow*, not
    a separate feature bolted on afterwards.
    """
    text, n = EMAIL_RE.subn("[REDACTED_EMAIL]", text)
    return text, n


def _apply_redaction(sc: ScoredChunk) -> bool:
    masked, n = redact_pii(sc.chunk.text)
    if n:
        sc.chunk.text = masked
        sc.redacted = True
        return True
    return False


def enforce(principal: Principal,
            candidates: List[ScoredChunk],
            ctx: Optional[Dict[str, Any]] = None,
            came_from_prefilter: bool = True) -> EnforcementReport:
    """Re-evaluate the policy against every retrieved chunk. Authoritative.

    Deliberately re-fetches each chunk's attributes from the ACL catalog rather
    than trusting `sc.chunk.attrs` (the denormalised Chroma metadata attached at
    retrieval time). That metadata is Layer 1's cache; this function IS Layer 2,
    so it reads the source of truth fresh, independent of whatever the vector
    store's copy says.
    """
    from ..ingest.store import get_doc_attrs   # local import avoids a cycle

    ctx = ctx or {}
    report = EnforcementReport()

    for sc in candidates:
        # Catalog is authoritative when it has a row; fall back to the chunk's own
        # (denormalised) attrs only if the doc was never catalogued - e.g. a chunk
        # built by hand in a test rather than through the real ingest pipeline.
        attrs = get_doc_attrs(sc.chunk.doc_id) or sc.chunk.attrs
        decision = decide(principal, attrs, ctx)

        if decision.denied:
            report.denied.append((sc, decision))
            # The chunk came back from a store that was supposed to have filtered it
            # out. Either the index is stale (a revoked grant) or the pushdown is
            # incomplete by design (embargo, need-to-know). Both are worth logging;
            # only the first is a bug.
            if came_from_prefilter and decision.rule not in {"embargo", "expired", "need_to_know"}:
                report.filter_disagreements.append({
                    "chunk_id": sc.chunk.chunk_id,
                    "doc_id": sc.chunk.doc_id,
                    "rule": decision.rule,
                    "reason": decision.reason,
                    "severity": "security_event",
                })
            continue

        if "redact_pii" in decision.obligations:
            if _apply_redaction(sc):
                report.redacted_count += 1

        if "audit_access" in decision.obligations:
            report.audit_events.append({
                "user_id": principal.user_id,
                "doc_id": sc.chunk.doc_id,
                "sensitivity": sc.chunk.attrs.sensitivity,
                "rule": decision.rule,
            })

        report.allowed.append(sc)

    return report


def verify_citations(principal: Principal,
                     cited_doc_ids: List[str],
                     ctx: Optional[Dict[str, Any]] = None) -> List[str]:
    """Final belt-and-braces check on the way out.

    Even with correct retrieval, a citation rendered into the answer is a claim that
    the user may see that document. Re-check each one; drop any that fails. This
    catches a synthesiser that hallucinated a document ID.
    """
    from ..ingest.store import get_doc_attrs   # local import avoids a cycle

    ok: List[str] = []
    for doc_id in cited_doc_ids:
        attrs = get_doc_attrs(doc_id)
        if attrs is None:
            continue                      # hallucinated citation - drop silently
        if decide(principal, attrs, ctx).allowed:
            ok.append(doc_id)
    return ok
