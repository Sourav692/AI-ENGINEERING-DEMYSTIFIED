# -*- coding: utf-8 -*-
"""Tests that keep the golden set itself honest.

An evaluation suite is only as trustworthy as its labels. These tests caught a real
bug: `Q06` listed `CT-VTX-001` as forbidden for the account manager, but she is in
fact permitted to read it - it was merely the *wrong* document for that question.
The `bm25` strategy retrieved it and the harness reported a security LEAK.

That is the worst kind of eval failure. A false security alarm trains people to
ignore the alarm, and the next one will be real. So the two ideas are now separate
fields with separate consequences, and this file enforces the distinction:

    forbidden_docs   MUST be policy-denied  -> appearing = LEAK -> blocks the release
    distractor_docs  MAY be read            -> appearing = precision miss -> a metric

No LLM, no index, no network.
"""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from enterprise_rag.authz.policy import decide                             # noqa: E402
from enterprise_rag.evaluation.harness import load_cases                   # noqa: E402
from enterprise_rag.identity import get_principal, list_principals         # noqa: E402
from enterprise_rag.ingest.loader import load_corpus                       # noqa: E402


@pytest.fixture(scope="module")
def docs():
    return {d.attrs.doc_id: d.attrs for d in load_corpus()}


@pytest.fixture(scope="module")
def cases():
    return load_cases()


# ---------------------------------------------------------------------------
# The label-integrity tests
# ---------------------------------------------------------------------------
def test_every_forbidden_doc_is_genuinely_policy_denied(cases, docs):
    """The core invariant. A 'forbidden' document the principal may actually read
    is a mislabelled case, and it would raise a false security alarm."""
    problems = []
    for c in cases:
        p = get_principal(c["user_id"])
        ctx = {"as_of": c.get("as_of")}
        for doc_id in c.get("forbidden_docs", []):
            d = decide(p, docs[doc_id], ctx)
            if d.allowed:
                problems.append(f"{c['id']}: {c['user_id']} IS allowed {doc_id} "
                                f"via [{d.rule}] - should be distractor_docs")
    assert not problems, "mislabelled forbidden_docs:\n  " + "\n  ".join(problems)


def test_every_distractor_doc_is_genuinely_readable(cases, docs):
    """The mirror invariant. A 'distractor' the principal cannot read is really a
    forbidden document, and demoting it would silently weaken the security gate."""
    problems = []
    for c in cases:
        p = get_principal(c["user_id"])
        ctx = {"as_of": c.get("as_of")}
        for doc_id in c.get("distractor_docs", []):
            d = decide(p, docs[doc_id], ctx)
            if not d.allowed:
                problems.append(f"{c['id']}: {c['user_id']} is DENIED {doc_id} "
                                f"via [{d.rule}] - should be forbidden_docs")
    assert not problems, "mislabelled distractor_docs:\n  " + "\n  ".join(problems)


def test_every_expected_doc_is_actually_readable(cases, docs):
    """A case that expects a document the principal cannot read is unsatisfiable."""
    problems = []
    for c in cases:
        p = get_principal(c["user_id"])
        ctx = {"as_of": c.get("as_of")}
        for doc_id in c.get("expected_docs", []):
            d = decide(p, docs[doc_id], ctx)
            if not d.allowed:
                problems.append(f"{c['id']}: expects {doc_id} but {c['user_id']} "
                                f"is denied it via [{d.rule}]")
    assert not problems, "unsatisfiable expectations:\n  " + "\n  ".join(problems)


def test_expected_and_forbidden_never_overlap(cases):
    for c in cases:
        overlap = set(c.get("expected_docs", [])) & set(c.get("forbidden_docs", []))
        assert not overlap, f"{c['id']} both expects and forbids {overlap}"


# ---------------------------------------------------------------------------
# Structural sanity
# ---------------------------------------------------------------------------
def test_case_ids_are_unique(cases):
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))


def test_all_referenced_docs_exist(cases, docs):
    for c in cases:
        for key in ("expected_docs", "forbidden_docs", "distractor_docs"):
            for doc_id in c.get(key, []):
                assert doc_id in docs, f"{c['id']}.{key} references unknown {doc_id}"


def test_all_referenced_users_exist(cases):
    known = {p.user_id for p in list_principals()}
    for c in cases:
        assert c["user_id"] in known, f"{c['id']} references unknown user {c['user_id']}"


def test_every_case_has_a_recognised_kind(cases):
    for c in cases:
        assert c["kind"] in {"quality", "security", "behaviour"}, c["id"]


def test_security_cases_all_declare_forbidden_docs(cases):
    """A security case that forbids nothing asserts nothing."""
    for c in cases:
        if c["kind"] == "security":
            assert c.get("forbidden_docs"), f"{c['id']} is a security case with no assertion"


def test_security_suite_covers_every_denial_rule(cases, docs):
    """Coverage check: each policy rule that can deny must be exercised somewhere.

    Without this, a rule could be deleted and the suite would still pass green.
    """
    exercised = set()
    for c in cases:
        if c["kind"] != "security":
            continue
        p = get_principal(c["user_id"])
        ctx = {"as_of": c.get("as_of")}
        for doc_id in c.get("forbidden_docs", []):
            exercised.add(decide(p, docs[doc_id], ctx).rule)

    required = {"tenant_isolation", "clearance", "data_residency",
                "embargo", "need_to_know", "external_restriction", "default_deny"}
    missing = required - exercised
    assert not missing, f"no security case exercises: {sorted(missing)}"


def test_golden_set_covers_multiple_personas(cases):
    users = {c["user_id"] for c in cases}
    assert len(users) >= 5, "the suite must exercise several roles, not one"
