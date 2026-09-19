"""Agent tool-calling demo — a DevRev-flavored ReAct agent, built two ways.

Modules
-------
tools          : the tool registry + an in-memory "DevRev" ticket backend.
observability  : a logger that records every tool call (args, result, latency, cache).
robustness     : retry, memoization, fallback, and a confirmation gate.
brain          : the "decision maker" — a deterministic rule-based router (offline),
                 with a hook to swap in a real LLM.
scratch_agent  : the ReAct loop coded FROM SCRATCH (no framework) — the interview version.
langgraph_agent: the SAME loop built with LangGraph's StateGraph — the framework version.
"""
