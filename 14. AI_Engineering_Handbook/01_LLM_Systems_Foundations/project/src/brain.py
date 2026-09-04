"""The 'brain' — the component that decides the next action given the query so far.

In a real agent this is an LLM (e.g. ChatOpenAI with `bind_tools`). For a demo that
runs offline and deterministically, we use a rule-based router that mimics what an
LLM's tool-selection would produce. The agent code doesn't care which brain it uses,
so you can swap in a real LLM by implementing the same `.decide()` contract.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass
class Decision:
    """What the brain wants to do next: either call a tool, or finish."""
    tool: Optional[str] = None          # tool name to call (None if finishing)
    args: Optional[dict] = None         # arguments for that tool
    final: Optional[str] = None         # the final answer text (None if still working)

    @property
    def is_final(self) -> bool:
        return self.final is not None


# An "observation" is one past tool result: (tool_name, python_result).
Observation = Tuple[str, Any]


class RuleBasedBrain:
    """A deterministic intent router — no LLM, no API key, fully reproducible.

    It reads (a) the user's query and (b) the observations gathered so far, and
    returns the next Decision. Because it's reactive (it looks at observations),
    it naturally produces multi-step plans like search -> then close.
    """

    def decide(self, query: str, observations: List[Observation]) -> Decision:
        intent, arg = self._classify(query)
        n = len(observations)

        if intent == "close_by_topic":
            if n == 0:                                  # step 1: find the ticket
                return Decision(tool="search_tickets", args={"query": arg})
            if n == 1:                                  # step 2: close the first match
                hits = observations[0][1]
                if not hits:
                    return Decision(final=f"No open ticket found about '{arg}'.")
                return Decision(tool="close_ticket", args={"ticket_id": hits[0]["id"]})
            closed = observations[1][1]                 # step 3: report
            return Decision(final=f"Closed {closed['id']} — '{closed['subject']}'.")

        if intent == "lookup":
            if n == 0:
                return Decision(tool="get_ticket", args={"ticket_id": arg})
            t = observations[0][1]
            return Decision(final=f"{t['id']}: '{t['subject']}' is currently {t['status']}.")

        if intent == "search":
            if n == 0:
                return Decision(tool="search_tickets", args={"query": arg})
            hits = observations[0][1]
            ids = ", ".join(h["id"] for h in hits) or "none"
            return Decision(final=f"Found {len(hits)} ticket(s): {ids}.")

        if intent == "create":
            if n == 0:
                return Decision(tool="create_ticket", args={"subject": arg})
            t = observations[0][1]
            return Decision(final=f"Created {t['id']} — '{t['subject']}'.")

        return Decision(final="Sorry, I can't help with that request.")

    # --- naive intent classification (an LLM would do this far better) ---
    def _classify(self, query: str) -> Tuple[str, str]:
        q = query.strip()
        low = q.lower()

        m = re.search(r"\b(TKT-\d+)\b", q, re.IGNORECASE)   # explicit ticket id?
        if m and any(w in low for w in ("show", "detail", "status", "get", "what")):
            return "lookup", m.group(1).upper()

        if low.startswith("close") or "close the ticket" in low or "resolve the ticket" in low:
            topic = _after(low, ("about", "regarding", "for")) or _strip_words(low, ("close", "the", "ticket", "resolve"))
            return "close_by_topic", topic.strip()

        if low.startswith("create") or "create a ticket" in low or "open a ticket" in low:
            subject = _after(low, ("titled", "about", "for", "saying", ":")) or "New ticket"
            return "create", subject.strip().title()

        if any(w in low for w in ("find", "search", "list", "show tickets", "which tickets")):
            topic = _after(low, ("about", "regarding", "for", "matching")) or _strip_words(low, ("find", "search", "list", "tickets", "the", "show", "which"))
            return "search", topic.strip()

        return "unknown", q


def _after(text: str, markers) -> str:
    """Return the substring after the first marker word found (or '')."""
    for mk in markers:
        idx = text.find(mk)
        if idx != -1:
            return text[idx + len(mk):].strip(" :'\"")
    return ""


def _strip_words(text: str, words) -> str:
    kept = [w for w in text.split() if w not in words]
    return " ".join(kept)


def make_llm_brain(model_name: str = "gpt-4o-mini"):
    """OPTIONAL: a real LLM brain (needs `langchain-openai` and an OPENAI_API_KEY).

    Returned object exposes the same `.decide(query, observations)` contract so the
    agents work unchanged. Kept thin on purpose — the offline RuleBasedBrain is what
    the demo runs by default.
    """
    from langchain_openai import ChatOpenAI            # imported lazily
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = ChatOpenAI(model=model_name, temperature=0)

    class LLMBrain:
        SYSTEM = ("You are a support agent. Decide the single next tool call as JSON "
                  "{\"tool\": name, \"args\": {...}} or {\"final\": answer}.")

        def decide(self, query, observations):
            import json
            ctx = "\n".join(f"OBSERVATION {t}: {r}" for t, r in observations)
            msg = self.SYSTEM + "\nQUERY: " + query + ("\n" + ctx if ctx else "")
            reply = llm.invoke([SystemMessage(content=self.SYSTEM), HumanMessage(content=msg)])
            data = json.loads(reply.content)
            if "final" in data:
                return Decision(final=data["final"])
            return Decision(tool=data["tool"], args=data.get("args", {}))

    return LLMBrain()
