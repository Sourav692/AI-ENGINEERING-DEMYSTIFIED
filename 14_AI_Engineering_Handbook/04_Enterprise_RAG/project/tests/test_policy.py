# -*- coding: utf-8 -*-
"""Policy engine unit tests - no LLM, no vector store, no network.

These are the tests that must never be allowed to go red. Every one of them
encodes a rule that, if broken, is a data leak rather than a bug.
"""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from enterprise_rag.authz.policy import compile_prefilter, decide          # noqa: E402
from enterprise_rag.identity import get_principal                          # noqa: E402
from enterprise_rag.ingest.loader import load_corpus                       # noqa: E402
from enterprise_rag.models import Principal, ResourceAttributes            # noqa: E402

TODAY = "2026-08-22"


@pytest.fixture(scope="module")
def docs():
    return {d.attrs.doc_id: d.attrs for d in load_corpus()}


def allowed(user_id, attrs, as_of=TODAY):
    return decide(get_principal(user_id), attrs, {"as_of": as_of}).allowed


def rule(user_id, attrs, as_of=TODAY):
    return decide(get_principal(user_id), attrs, {"as_of": as_of}).rule


# ---------------------------------------------------------------------------
# Tenant isolation - the hardest boundary
# ---------------------------------------------------------------------------
def test_cross_tenant_denied_for_every_document(docs):
    """A maximally privileged principal in another tenant sees nothing at all."""
    for doc_id, attrs in docs.items():
        assert not allowed("u_attacker_other_tenant", attrs), f"{doc_id} leaked cross-tenant"
        assert rule("u_attacker_other_tenant", attrs) == "tenant_isolation"


def test_tenant_isolation_beats_every_other_grant():
    """Even a perfect group/clearance match cannot cross the tenant line."""
    intruder = Principal(user_id="x", display_name="x", tenant_id="acme", role="admin",
                         groups=["public", "engineering"], clearance="restricted",
                         region="GLOBAL", projects=["vuln-response"])
    public_doc = ResourceAttributes(doc_id="D", tenant_id="meridian", source="helpcenter",
                                    sensitivity="public", allowed_groups=["public"],
                                    region="GLOBAL")
    d = decide(intruder, public_doc, {"as_of": TODAY})
    assert not d.allowed and d.rule == "tenant_isolation"


# ---------------------------------------------------------------------------
# Clearance ladder
# ---------------------------------------------------------------------------
def test_tier1_cannot_read_confidential(docs):
    assert not allowed("u_lena_t1", docs["PM-2026-03-14"])
    assert rule("u_lena_t1", docs["PM-2026-03-14"]) == "clearance"
    assert not allowed("u_lena_t1", docs["CT-VTX-001"])


def test_tier3_can_read_confidential_postmortem(docs):
    assert allowed("u_marco_t3", docs["PM-2026-03-14"])


def test_everyone_in_tenant_reads_public(docs):
    for uid in ["u_lena_t1", "u_marco_t3", "u_sofia_am", "u_ravi_sec", "u_tom_contractor"]:
        assert allowed(uid, docs["HC-001"]), uid


# ---------------------------------------------------------------------------
# Group membership
# ---------------------------------------------------------------------------
def test_engineer_cannot_read_pricing(docs):
    """Clearance is sufficient; group membership is not. Both are required."""
    assert not allowed("u_marco_t3", docs["PR-001"])
    assert rule("u_marco_t3", docs["PR-001"]) == "default_deny"


def test_account_manager_cannot_read_postmortem(docs):
    assert not allowed("u_sofia_am", docs["PM-2026-03-14"])


def test_account_manager_can_read_contract_and_pricing(docs):
    assert allowed("u_sofia_am", docs["CT-VTX-001"])
    assert allowed("u_sofia_am", docs["PR-001"])


# ---------------------------------------------------------------------------
# Data residency
# ---------------------------------------------------------------------------
def test_us_engineer_denied_eu_locked_postmortem(docs):
    """Same role, same clearance, same groups as Marco - different region."""
    assert allowed("u_marco_t3", docs["PM-2026-03-14"])
    assert not allowed("u_jin_us_t3", docs["PM-2026-03-14"])
    assert rule("u_jin_us_t3", docs["PM-2026-03-14"]) == "data_residency"


def test_global_documents_readable_from_any_region(docs):
    assert allowed("u_jin_us_t3", docs["RB-101"])
    assert allowed("u_marco_t3", docs["RB-101"])


def test_global_principal_still_blocked_from_region_locked_doc(docs):
    """GLOBAL is not a wildcard on the principal side - it is its own region."""
    assert not allowed("u_ravi_sec", docs["PM-2026-03-14"])
    assert rule("u_ravi_sec", docs["PM-2026-03-14"]) == "data_residency"


# ---------------------------------------------------------------------------
# Embargo / time-bound
# ---------------------------------------------------------------------------
def test_embargoed_advisory_hidden_before_publication(docs):
    assert not allowed("u_ravi_sec", docs["SA-2026-07"], as_of="2026-08-22")
    assert rule("u_ravi_sec", docs["SA-2026-07"], as_of="2026-08-22") == "embargo"


def test_embargoed_advisory_visible_after_publication(docs):
    assert allowed("u_ravi_sec", docs["SA-2026-07"], as_of="2026-09-02")


def test_embargo_is_evaluated_at_query_time_not_index_time(docs):
    """The same principal and document flip purely on the clock."""
    before = decide(get_principal("u_ravi_sec"), docs["SA-2026-07"], {"as_of": "2026-08-31"})
    after = decide(get_principal("u_ravi_sec"), docs["SA-2026-07"], {"as_of": "2026-09-01"})
    assert not before.allowed and after.allowed


# ---------------------------------------------------------------------------
# Need-to-know compartments
# ---------------------------------------------------------------------------
def test_clearance_without_compartment_is_not_enough(docs):
    """Erin has 'restricted' clearance but no vuln-response compartment."""
    assert not allowed("u_erin_secmgr", docs["SA-2026-05"])
    assert rule("u_erin_secmgr", docs["SA-2026-05"]) == "need_to_know"
    assert allowed("u_ravi_sec", docs["SA-2026-05"])


# ---------------------------------------------------------------------------
# External principals
# ---------------------------------------------------------------------------
def test_external_contractor_blocked_from_commercial_sources(docs):
    for doc_id in ["CT-VTX-001", "PR-001", "PM-2026-01-22"]:
        d = decide(get_principal("u_tom_contractor"), docs[doc_id], {"as_of": TODAY})
        assert not d.allowed, doc_id


def test_external_restriction_applies_even_with_matching_groups():
    """The source-based block is independent of group membership."""
    contractor = Principal(user_id="c", display_name="c", tenant_id="meridian",
                           role="contractor", groups=["sales", "legal"],
                           clearance="confidential", region="EU", is_external=True)
    contract = ResourceAttributes(doc_id="CT", tenant_id="meridian", source="contract",
                                  sensitivity="confidential",
                                  allowed_groups=["sales", "legal"], region="EU")
    d = decide(contractor, contract, {"as_of": TODAY})
    assert not d.allowed and d.rule == "external_restriction"


# ---------------------------------------------------------------------------
# Obligations
# ---------------------------------------------------------------------------
def test_pii_obligation_attached_when_principal_cannot_view_pii(docs):
    """Tom may read the US ticket, but only with PII redacted."""
    d = decide(get_principal("u_tom_contractor"), docs["TK-4488"], {"as_of": TODAY})
    assert d.allowed
    assert "redact_pii" in d.obligations


def test_no_pii_obligation_for_authorised_viewer(docs):
    d = decide(get_principal("u_lena_t1"), docs["TK-4471"], {"as_of": TODAY})
    assert d.allowed and "redact_pii" not in d.obligations


def test_confidential_access_is_always_audited(docs):
    d = decide(get_principal("u_sofia_am"), docs["CT-VTX-001"], {"as_of": TODAY})
    assert d.allowed and "audit_access" in d.obligations


# ---------------------------------------------------------------------------
# Default deny
# ---------------------------------------------------------------------------
def test_unknown_group_document_is_denied_by_default():
    p = get_principal("u_marco_t3")
    orphan = ResourceAttributes(doc_id="X", tenant_id="meridian", source="wiki",
                                sensitivity="internal", allowed_groups=["finance-only"],
                                region="GLOBAL")
    d = decide(p, orphan, {"as_of": TODAY})
    assert not d.allowed and d.rule == "default_deny"


# ---------------------------------------------------------------------------
# Pre-filter compilation
# ---------------------------------------------------------------------------
def test_prefilter_always_pins_tenant_and_clearance():
    for uid in ["u_lena_t1", "u_marco_t3", "u_sofia_am", "u_ravi_sec",
                "u_tom_contractor", "u_attacker_other_tenant"]:
        p = get_principal(uid)
        where = compile_prefilter(p)
        clauses = where["$and"]
        assert {"tenant_id": {"$eq": p.tenant_id}} in clauses
        assert {"sensitivity_level": {"$lte": p.clearance_level}} in clauses


def test_prefilter_excludes_commercial_sources_for_externals():
    where = compile_prefilter(get_principal("u_tom_contractor"))
    assert any("source" in c and c["source"].get("$nin") for c in where["$and"])


def _mentions_public_group(clause) -> bool:
    """A single-element group clause is emitted bare, not wrapped in $or."""
    if clause == {"grp__public": {"$eq": True}}:
        return True
    return isinstance(clause, dict) and "$or" in clause and \
        {"grp__public": {"$eq": True}} in clause["$or"]


def test_prefilter_never_omits_group_clause():
    """A principal with no groups still gets a group clause - public only.

    Asserted semantically: the filter must constrain by group in either the bare
    or the $or-wrapped form, so the test does not break when the compiler
    legitimately collapses a one-element disjunction.
    """
    p = Principal(user_id="n", display_name="n", tenant_id="meridian", role="none",
                  groups=[], clearance="public", region="EU")
    where = compile_prefilter(p)
    assert any(_mentions_public_group(c) for c in where["$and"])


def test_prefilter_group_clause_covers_every_group_the_principal_holds():
    p = get_principal("u_marco_t3")
    where = compile_prefilter(p)
    group_clause = next(c for c in where["$and"] if _mentions_public_group(c))
    encoded = {list(d.keys())[0] for d in group_clause["$or"]}
    for g in p.groups:
        assert f"grp__{g}" in encoded
