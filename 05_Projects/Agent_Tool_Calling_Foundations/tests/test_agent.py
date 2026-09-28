# -*- coding: utf-8 -*-
"""Pytest suite for the agent tool-calling demo. Run:  pytest -q"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools import TicketStore, build_registry
from src.scratch_agent import Agent, Session
from src.robustness import (always_approve, deny_destructive, execute_tool,
                            with_fallback, disambiguate)
from src.observability import ToolCallLogger


# ---------- core loop ----------
def test_search_single_step():
    reg = build_registry(TicketStore())
    r = Agent(reg, confirm=always_approve).run("find tickets about auth")
    assert "TKT-1" in r.answer and "TKT-3" in r.answer
    assert r.iterations == 1


def test_lookup_by_id():
    reg = build_registry(TicketStore())
    r = Agent(reg, confirm=always_approve).run("what is the status of TKT-2")
    assert "TKT-2" in r.answer and "open" in r.answer


def test_multi_step_search_then_close():
    store = TicketStore(); reg = build_registry(store)
    r = Agent(reg, confirm=always_approve).run("close the ticket about login")
    assert "Closed TKT-3" in r.answer
    assert store.tickets["TKT-3"]["status"] == "closed"
    assert r.iterations == 2                      # search + close


# ---------- max-iteration guard ----------
def test_max_iteration_guard():
    reg = build_registry(TicketStore())
    # A brain that never finishes -> the guard must stop it.
    class NeverEnds:
        def decide(self, query, observations):
            from src.brain import Decision
            return Decision(tool="search_tickets", args={"query": "x"})
    r = Agent(reg, brain=NeverEnds(), max_iterations=3, confirm=always_approve).run("loop")
    assert "max-iteration guard" in r.answer
    assert r.iterations == 3


# ---------- confirmation gate ----------
def test_confirmation_blocks_destructive():
    store = TicketStore(); reg = build_registry(store)
    r = Agent(reg, confirm=deny_destructive).run("close the ticket about login")
    assert r.blocked_on == ("close_ticket", {"ticket_id": "TKT-3"})
    assert store.tickets["TKT-3"]["status"] == "open"   # nothing was closed


def test_confirmation_allows_when_approved():
    store = TicketStore(); reg = build_registry(store)
    r = Agent(reg, confirm=always_approve).run("close the ticket about login")
    assert store.tickets["TKT-3"]["status"] == "closed"


# ---------- robustness helpers ----------
def test_retry_on_flaky_tool():
    log = ToolCallLogger()
    reg = build_registry(TicketStore(), flaky_search=True)
    res = execute_tool(reg.get("search_tickets"), {"query": "auth"}, logger=log, retries=3)
    assert [h["id"] for h in res] == ["TKT-1", "TKT-3"]
    assert log.count("retry") == 2 and log.count("ok") == 1


def test_memoization():
    log = ToolCallLogger(); memo = {}
    reg = build_registry(TicketStore())
    execute_tool(reg.get("search_tickets"), {"query": "billing"}, logger=log, memo=memo)
    execute_tool(reg.get("search_tickets"), {"query": "billing"}, logger=log, memo=memo)
    assert log.count("ok") == 1 and log.count("cache_hit") == 1


def test_fallback():
    log = ToolCallLogger(); reg = build_registry(TicketStore())
    out = with_fallback(reg.get("get_ticket"), reg.get("search_tickets"),
                        {"ticket_id": "NOPE"}, adapt=lambda a: {"query": "login"}, logger=log)
    assert out[0]["id"] == "TKT-3"


def test_disambiguation_prefers_safe_tool():
    reg = build_registry(TicketStore())
    picked = disambiguate([reg.get("search_tickets"), reg.get("close_ticket")], "find and close")
    assert picked.name == "search_tickets"


# ---------- multi-turn state ----------
def test_session_memo_persists_across_turns():
    reg = build_registry(TicketStore()); sess = Session()
    agent = Agent(reg, confirm=always_approve)
    agent.run("find tickets about auth", sess)
    agent.run("find tickets about auth", sess)     # identical -> should hit cache
    assert sess.logger.count("cache_hit") >= 1


# ---------- langgraph parity ----------
def test_langgraph_matches_scratch():
    from src.langgraph_agent import build_graph, run_query
    store = TicketStore(); reg = build_registry(store); sess = Session()
    app = build_graph(reg, sess, confirm=always_approve)
    ans = run_query(app, "close the ticket about billing")
    assert "Closed TKT-2" in ans
    assert store.tickets["TKT-2"]["status"] == "closed"
