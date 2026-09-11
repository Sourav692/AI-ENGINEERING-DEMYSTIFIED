"""
The multi-agent system.

One supervisor, two specialists. The supervisor reads the task and decides who
works next; each specialist does its bit and hands control straight back. When
the supervisor decides there is nothing left to do, the run ends.

That loop -- decide, delegate, come back, decide again -- is the whole pattern.
"""

from typing import Annotated, Literal, TypedDict
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from helpers import get_llm

llm = get_llm()

# The supervisor may only ever choose one of these.
SPECIALISTS = ["calculator", "writer"]

# Safety net: stop after this many supervisor turns even if it never says done.
MAX_TURNS = 6


# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------
# Every node reads and writes this one dict. It is the only way the agents
# communicate -- there are no direct calls between them.

class TeamState(TypedDict):
    task: str                          # what the user asked for
    notes: Annotated[list[str], add]   # what each specialist produced
    visited: Annotated[list[str], add] # who ran, in order (the trajectory)
    answer: str                        # the final reply
    turns: int                         # how many times the supervisor decided


# ---------------------------------------------------------------------------
# The supervisor
# ---------------------------------------------------------------------------

SUPERVISOR_PROMPT = """You coordinate a small team.

Team members:
- calculator: does arithmetic and numeric work
- writer: turns rough facts into one clear, friendly sentence

The task: {task}

Already worked: {already}

Work done so far:
{progress}

Rules:
- Never pick someone who has already worked.
- If the task needs no arithmetic, skip the calculator.
- If the task needs no rewriting, skip the writer.
- Once everyone who is needed has worked, reply DONE.

Reply with exactly one word - the name of who should work next,
or DONE if the task is fully handled. Nothing else."""


def supervisor(state: TeamState) -> Command[Literal["calculator", "writer", "finish"]]:
    """Decide who works next, or that the work is finished."""
    progress = "\n".join(state["notes"]) if state["notes"] else "(nothing yet)"
    worked = [name for name in state["visited"] if name in SPECIALISTS]

    reply = llm.invoke(
        SUPERVISOR_PROMPT.format(
            task=state["task"],
            already=", ".join(worked) if worked else "(nobody yet)",
            progress=progress,
        )
    ).content.strip().lower()

    # Pick whichever specialist the model named. Anything else means stop.
    choice = next((name for name in SPECIALISTS if name in reply), "finish")

    # Two guards, because a model will sometimes ignore the rules above.
    # Without them a supervisor can loop forever, which is the classic way
    # this pattern fails.
    if choice in worked:                 # already had their turn
        choice = "finish"
    if state["turns"] >= MAX_TURNS:      # gone around too many times
        choice = "finish"

    return Command(
        goto=choice,
        update={"turns": state["turns"] + 1, "visited": ["supervisor"]},
    )


# ---------------------------------------------------------------------------
# The specialists
# ---------------------------------------------------------------------------
# Each one does a narrow job, records what it did, and returns to the
# supervisor. Neither knows the other exists.

def calculator(state: TeamState) -> Command[Literal["supervisor"]]:
    """Handle the numeric part of the task."""
    result = llm.invoke(
        f"Do only the arithmetic needed for this task. "
        f"Show the number and nothing else.\n\nTask: {state['task']}"
    ).content.strip()

    return Command(
        goto="supervisor",
        update={"notes": [f"calculator: {result}"], "visited": ["calculator"]},
    )


def writer(state: TeamState) -> Command[Literal["supervisor"]]:
    """Turn whatever has been worked out into one clear sentence."""
    progress = "\n".join(state["notes"]) if state["notes"] else "(nothing yet)"

    result = llm.invoke(
        f"Write one short, friendly sentence answering the task, "
        f"using the findings below.\n\n"
        f"Task: {state['task']}\n\nFindings:\n{progress}"
    ).content.strip()

    return Command(
        goto="supervisor",
        update={
            "notes": [f"writer: {result}"],
            "visited": ["writer"],
            "answer": result,
        },
    )


def finish(state: TeamState) -> TeamState:
    """Last stop. If the writer never ran, fall back to the latest note."""
    if state.get("answer"):
        return {}
    latest = state["notes"][-1] if state["notes"] else "No answer produced."
    return {"answer": latest}


# ---------------------------------------------------------------------------
# Wiring it together
# ---------------------------------------------------------------------------
# Note there are no edges between supervisor and the specialists. Routing is
# decided at run time by what each node returns, not fixed when we build.

def build_team():
    builder = StateGraph(TeamState)

    builder.add_node("supervisor", supervisor)
    builder.add_node("calculator", calculator)
    builder.add_node("writer", writer)
    builder.add_node("finish", finish)

    builder.add_edge(START, "supervisor")
    builder.add_edge("finish", END)

    return builder.compile()


team = build_team()


def run(task: str) -> dict:
    """Run one task through the team and report what happened."""
    final = team.invoke(
        {"task": task, "notes": [], "visited": [], "answer": "", "turns": 0}
    )
    return {
        "task": task,
        "answer": final["answer"],
        "trajectory": final["visited"],
        "turns": final["turns"],
        "notes": final["notes"],
    }
