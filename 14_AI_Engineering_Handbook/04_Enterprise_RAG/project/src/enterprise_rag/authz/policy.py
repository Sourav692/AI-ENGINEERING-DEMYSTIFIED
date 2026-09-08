# -*- coding: utf-8 -*-
"""The ABAC policy engine - the authority on who may read what.

Design rules this file exists to enforce:

1.  **Deny overrides.** Any rule that denies wins, regardless of what else allows.
2.  **The policy engine is the authority; the index filter is only an optimisation.**
    The same `decide()` function runs twice - once compiled into a vector-store
    pre-filter (cheap, approximate, fast) and once against freshly resolved
    attributes after retrieval (authoritative). If the two ever disagree, the
    post-check wins and the discrepancy is logged as a security event.
3.  **The LLM is never an enforcement point.** No prompt says "do not reveal X".
    Unauthorised text simply never reaches the model.

Rules are ordered and explicit so a reviewer - or an interviewer - can read the
policy top to bottom without running it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

from ..models import Principal, ResourceAttributes


@dataclass
class Decision:
    """The outcome of evaluating the policy for one (principal, resource) pair."""

    allowed: bool
    rule: str                                   # the rule that decided it
    reason: str
    obligations: List[str] = field(default_factory=list)   # e.g. ["redact_pii"]

    @property
    def denied(self) -> bool:
        return not self.allowed


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------
# Each rule takes (principal, resource, ctx) and returns:
#   Decision(allowed=False, ...)  -> hard deny, stop
#   None                          -> this rule has no opinion, continue
# A final default-deny catches anything no ALLOW rule spoke for.


def _rule_tenant_isolation(p: Principal, r: ResourceAttributes, ctx) -> Optional[Decision]:
    """Hard multi-tenant boundary. Nothing crosses it, ever, for any role."""
    if p.tenant_id != r.tenant_id:
        return Decision(False, "tenant_isolation",
                        f"principal tenant '{p.tenant_id}' != resource tenant '{r.tenant_id}'")
    return None


def _rule_clearance(p: Principal, r: ResourceAttributes, ctx) -> Optional[Decision]:
    """Sensitivity ladder: you may read at or below your clearance."""
    if r.sensitivity_level > p.clearance_level:
        return Decision(False, "clearance",
                        f"resource is '{r.sensitivity}' but principal clearance is '{p.clearance}'")
    return None


def _rule_data_residency(p: Principal, r: ResourceAttributes, ctx) -> Optional[Decision]:
    """Region-locked data (a real contractual term in the Vertex MSA).

    GLOBAL resources are readable from anywhere; a region-locked resource is
    readable only by a principal in that region.
    """
    if r.region != "GLOBAL" and p.region != r.region:
        return Decision(False, "data_residency",
                        f"resource is locked to region '{r.region}', principal is in '{p.region}'")
    return None


def _rule_embargo(p: Principal, r: ResourceAttributes, ctx) -> Optional[Decision]:
    """Time-bound validity: an unpublished advisory is invisible until its date."""
    today = ctx.get("as_of") or date.today().isoformat()
    if r.valid_from and today < r.valid_from:
        return Decision(False, "embargo",
                        f"resource is embargoed until {r.valid_from} (today is {today})")
    if r.valid_until and today > r.valid_until:
        return Decision(False, "expired",
                        f"resource expired on {r.valid_until} (today is {today})")
    return None


def _rule_need_to_know(p: Principal, r: ResourceAttributes, ctx) -> Optional[Decision]:
    """Compartmentalisation on top of clearance.

    Being cleared for `restricted` is not enough to read a vuln-response document;
    you must also be assigned to that compartment.
    """
    if r.need_to_know:
        missing = [t for t in r.need_to_know if t not in p.projects]
        if missing:
            return Decision(False, "need_to_know",
                            f"principal lacks need-to-know compartment(s): {', '.join(missing)}")
    return None


def _rule_external_contractor(p: Principal, r: ResourceAttributes, ctx) -> Optional[Decision]:
    """External principals never see commercial documents, whatever their groups say."""
    if p.is_external and r.source in {"contract", "pricing", "postmortem"}:
        return Decision(False, "external_restriction",
                        f"external principal may not read source '{r.source}'")
    return None


def _rule_group_membership(p: Principal, r: ResourceAttributes, ctx) -> Optional[Decision]:
    """The positive grant: overlap between the principal's groups and the doc ACL."""
    if "public" in r.allowed_groups:
        return Decision(True, "group_membership", "resource is public")
    overlap = sorted(set(p.groups) & set(r.allowed_groups))
    if overlap:
        return Decision(True, "group_membership", f"group overlap: {', '.join(overlap)}")
    return None


# Deny rules run first (deny overrides), then the single allow rule.
DENY_RULES = [
    _rule_tenant_isolation,
    _rule_clearance,
    _rule_data_residency,
    _rule_embargo,
    _rule_need_to_know,
    _rule_external_contractor,
]
ALLOW_RULES = [_rule_group_membership]


def decide(principal: Principal,
           resource: ResourceAttributes,
           ctx: Optional[Dict[str, Any]] = None) -> Decision:
    """Evaluate the full policy for one principal/resource pair."""
    ctx = ctx or {}

    for rule in DENY_RULES:
        d = rule(principal, resource, ctx)
        if d is not None and d.denied:
            return d

    for rule in ALLOW_RULES:
        d = rule(principal, resource, ctx)
        if d is not None and d.allowed:
            return _attach_obligations(principal, resource, d)

    return Decision(False, "default_deny",
                    "no grant matched; the default is deny")


def _attach_obligations(p: Principal, r: ResourceAttributes, d: Decision) -> Decision:
    """Obligations are conditions attached to an ALLOW - read it, but transformed.

    This is the part of ABAC that people forget exists, and it is how you serve a
    support agent a ticket without serving them the customer's email address.
    """
    obligations: List[str] = []
    if r.contains_pii and not p.can_view_pii:
        obligations.append("redact_pii")
    if r.sensitivity in {"confidential", "restricted"}:
        obligations.append("audit_access")
    d.obligations = obligations
    return d


# ---------------------------------------------------------------------------
# Compiling the policy into a vector-store pre-filter
# ---------------------------------------------------------------------------
def compile_prefilter(principal: Principal,
                      ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Translate the *statically decidable* part of the policy into a Chroma `where`.

    What can be pushed down into the index:
      - tenant equality
      - sensitivity_level <= clearance_level
      - region in {GLOBAL, principal.region}
      - group overlap, via the one-boolean-column-per-group encoding
      - external-contractor source exclusion

    What deliberately cannot, and is therefore enforced after retrieval:
      - embargo / expiry (needs "now", and a stale index would leak an unpublished doc)
      - need-to-know compartments (list semantics Chroma cannot express)
      - obligations such as PII redaction (a transformation, not a filter)
      - live revocation (group membership may have changed since indexing)

    The split is the whole architectural point: the filter makes retrieval cheap,
    the post-check makes it correct.
    """
    ctx = ctx or {}
    clauses: List[Dict[str, Any]] = [
        {"tenant_id": {"$eq": principal.tenant_id}},
        {"sensitivity_level": {"$lte": principal.clearance_level}},
    ]

    # Region: GLOBAL is readable by everyone, plus the principal's own region.
    clauses.append({"$or": [{"region": {"$eq": "GLOBAL"}},
                            {"region": {"$eq": principal.region}}]})

    # Group overlap. `public` is a pseudo-group every document that is public carries.
    group_clauses: List[Dict[str, Any]] = [{"grp__public": {"$eq": True}}]
    for g in principal.groups:
        group_clauses.append({f"grp__{g}": {"$eq": True}})
    clauses.append({"$or": group_clauses} if len(group_clauses) > 1 else group_clauses[0])

    if principal.is_external:
        clauses.append({"source": {"$nin": ["contract", "pricing", "postmortem"]}})

    return {"$and": clauses} if len(clauses) > 1 else clauses[0]


def explain_prefilter(principal: Principal) -> str:
    """Human-readable summary of the pushdown - used in traces and the demo output."""
    return (f"tenant={principal.tenant_id} AND sensitivity<={principal.clearance} "
            f"AND region in (GLOBAL,{principal.region}) "
            f"AND groups overlap ({', '.join(principal.groups) or 'none'})"
            + (" AND source NOT IN (contract,pricing,postmortem)" if principal.is_external else ""))


def merge_filters(where: Dict[str, Any], content_filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """AND a caller-supplied, non-ACL content filter (source, doc type, a
    recency range on `ingested_at`/`source_updated_at`, ...) onto the compiled
    ACL pre-filter (§4.4 - "metadata filters as first-class").

    Safe by construction, not by validation: combining two filters with `$and`
    can only ever narrow the result set further, never loosen it, so a content
    filter cannot be used to see past the ACL clause no matter what it contains.
    This is additive to Layer 1 only - Layer 2's authoritative re-check in
    enforcement.py never sees or needs to know about content_filters at all,
    because by the time a chunk reaches enforce() it already passed both.
    """
    if not content_filters:
        return where
    return {"$and": [where, content_filters]}
