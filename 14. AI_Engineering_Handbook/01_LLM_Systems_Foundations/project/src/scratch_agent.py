"""The ReAct-style tool-calling loop, coded FROM SCRATCH (no framework).

This is the version the DevRev prep prioritizes ("tool-calling loop, coded from
scratch"). It shows every moving part explicitly:

    query -> brain decides -> execute tool -> observe -> loop -> synthesize answer

with a max-iteration guard, a confirmation gate for destructive tools, memoization,
retry, and full observability.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from .tools import ToolRegistry
from .brain import RuleBasedBrain, Decision, Observation
from .observability import ToolCallLogger
from .robustness import execute_tool, ConfirmationRequired, ConfirmPolicy, deny_destructive


@dataclass
class Session:
    """State that persists ACROSS turns of a conversation.

    - history : the (query, answer) pairs so far (multi-turn memory).
    - memo    : cache of tool results, shared across turns (don't re-call the API).
    - logger  : the observability trace for the whole session.
    """
    history: List[Tuple[str, str]] = field(default_factory=list)
    memo: dict = field(default_factory=dict)
    logger: ToolCallLogger = field(default_factory=ToolCallLogger)


@dataclass
class RunResult:
    answer: str
    iterations: int
    observations: List[Observation]
    blocked_on: Optional[Tuple[str, dict]] = None      # set if paused for confirmation


class Agent:
    """A minimal ReAct agent: a registry of tools + a brain + robustness."""

    def __init__(
        self,
        registry: ToolRegistry,
        brain: Optional[RuleBasedBrain] = None,
        *,
        max_iterations: int = 6,
        confirm: ConfirmPolicy = deny_destructive,
    ) -> None:
        self.registry = registry
        self.brain = brain or RuleBasedBrain()
        self.max_iterations = max_iterations        # the loop guard — never run forever
        self.confirm = confirm

    def run(self, query: str, session: Optional[Session] = None) -> RunResult:
        """Execute the loop for one user query."""
        session = session or Session()
        observations: List[Observation] = []
        iterations = 0

        while iterations < self.max_iterations:      # MAX-ITERATION GUARD
            decision: Decision = self.brain.decide(query, observations)   # 1) THINK

            if decision.is_final:                    # 2a) the brain is done -> synthesize
                session.history.append((query, decision.final))
                return RunResult(decision.final, iterations, observations)

            # 2b) the brain chose a tool -> ACT
            tool = self.registry.get(decision.tool)
            try:
                result = execute_tool(
                    tool, decision.args,
                    logger=session.logger,
                    memo=session.memo,               # cache across the whole session
                    confirm=self.confirm,            # confirmation gate for destructive tools
                )
            except ConfirmationRequired as e:
                # Pause and hand control back to the caller to approve the action.
                msg = f"Awaiting confirmation to run '{e.tool}' with {e.call_args}."
                return RunResult(msg, iterations, observations, blocked_on=(e.tool, e.call_args))

            observations.append((decision.tool, result))   # 3) OBSERVE
            iterations += 1

        # Fell out of the loop without finishing.
        return RunResult("Stopped: hit the max-iteration guard.", iterations, observations)
