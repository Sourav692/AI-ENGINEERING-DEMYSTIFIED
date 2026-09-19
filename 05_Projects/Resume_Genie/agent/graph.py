import logging
import time

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq

from agent.state import AgentState
from agent.prompts import ROUTER_PROMPT
from agent.tools import (
    run_cover_letter,
    run_resume_scorer,
    run_resume_checker,
    run_career_coach,
)

# ── Logger setup ─────────────────────────────────
logger = logging.getLogger("resume_genie.agent")

# Only add handler if none exist (avoids duplicates on Streamlit reruns)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(name)s] %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Tools that require a job description
JD_REQUIRED_TOOLS = {"cover_letter", "resume_scorer"}

# Display names for tool outputs
TOOL_LABELS = {
    "resume_checker": "Resume Evaluation",
    "resume_scorer": "ATS Match Analysis",
    "cover_letter": "Cover Letter",
}


def build_graph(llm: ChatGroq):
    """Build and compile the LangGraph StateGraph for the Resume Genie agent."""

    graph = StateGraph(AgentState)

    # ── Router node ───────────────────────────────────
    def router_node(state: AgentState) -> dict:
        """Classify user intent and decide which tool(s) to run."""
        user_msg = state["messages"][-1].content
        resume_text = state.get("resume_text", "")
        job_description = state.get("job_description")

        resume_status = "uploaded" if resume_text else "NOT uploaded"
        jd_status = "provided" if job_description else "NOT provided"

        # Build conversation history from prior messages (last 3 exchanges max)
        prior_messages = state["messages"][:-1]  # exclude current user message
        if prior_messages:
            history_lines = []
            for m in prior_messages[-6:]:  # last 6 messages ≈ 3 exchanges
                role = "User" if m.type == "human" else "Assistant"
                history_lines.append(f"{role}: {m.content[:300]}")
            conversation_history = "\n".join(history_lines)
        else:
            conversation_history = "(no prior messages)"

        logger.info(
            '[ROUTER]    query="%s" | resume=%s | jd=%s',
            user_msg[:80], resume_status, jd_status,
        )

        t0 = time.time()
        decision = llm.invoke(
            ROUTER_PROMPT.format(
                resume_status=resume_status,
                jd_status=jd_status,
                user_message=user_msg,
                conversation_history=conversation_history,
            )
        ).content.strip().lower()
        elapsed = time.time() - t0

        logger.info(
            "[ROUTER]    decision=%s (%.2fs)", decision, elapsed
        )

        if decision.startswith("multi|"):
            tools = [t.strip() for t in decision.split("|")[1].split(",")]
            # Filter out JD-required tools if no JD provided
            if not job_description:
                filtered = [t for t in tools if t not in JD_REQUIRED_TOOLS]
                logger.info(
                    "[ROUTER]    filtered chain %s → %s (no JD)", tools, filtered
                )
                tools = filtered

            # If filtering reduced to a single tool, treat as single-tool mode
            if len(tools) == 1:
                logger.info("[ROUTER]    → single tool: %s (from filtered multi)", tools[0])
                return {"tool_choice": tools[0], "tool_chain": None, "tool_outputs": {}}

            if not tools:
                logger.info("[ROUTER]    → no tools left after filtering, falling back to career_coach")
                return {"tool_choice": "career_coach", "tool_chain": None, "tool_outputs": {}}

            logger.info("[ROUTER]    tool_chain=%s", tools)
            return {"tool_choice": "multi", "tool_chain": tools, "tool_outputs": {}}

        # Programmatic guard: if LLM picks a JD-required tool but no JD exists,
        # override to need_jd regardless of what the LLM returned
        if decision in JD_REQUIRED_TOOLS and not job_description:
            logger.info(
                "[ROUTER]    → need_jd (LLM chose %s but no JD provided — overriding)",
                decision,
            )
            return {
                "tool_choice": "none",
                "messages": [
                    AIMessage(
                        content=f"I'd need a job description to generate a "
                        f"{TOOL_LABELS.get(decision, decision).lower()}. "
                        "Please paste one in the sidebar or include it in your message."
                    )
                ],
            }

        if decision == "need_jd":
            logger.info("[ROUTER]    → need_jd (asking user for JD)")
            return {
                "tool_choice": "none",
                "messages": [
                    AIMessage(
                        content="I need a job description to do that. "
                        "Please paste one in the sidebar or include it in your message."
                    )
                ],
            }

        logger.info("[ROUTER]    → single tool: %s", decision)
        return {"tool_choice": decision, "tool_chain": None, "tool_outputs": {}}

    # ── Tool nodes ────────────────────────────────────
    def cover_letter_node(state: AgentState) -> dict:
        logger.info("[NODE]      cover_letter started")
        t0 = time.time()
        result = run_cover_letter(
            llm, state["resume_text"], state["job_description"]
        )
        elapsed = time.time() - t0
        logger.info(
            "[NODE]      cover_letter completed (%d chars, %.2fs)",
            len(result), elapsed,
        )
        outputs = dict(state.get("tool_outputs") or {})
        outputs["cover_letter"] = result
        return {"tool_outputs": outputs}

    def resume_scorer_node(state: AgentState) -> dict:
        logger.info("[NODE]      resume_scorer started")
        t0 = time.time()
        result = run_resume_scorer(
            llm, state["resume_text"], state["job_description"]
        )
        elapsed = time.time() - t0
        logger.info(
            "[NODE]      resume_scorer completed (%d chars, %.2fs)",
            len(result), elapsed,
        )
        outputs = dict(state.get("tool_outputs") or {})
        outputs["resume_scorer"] = result
        return {"tool_outputs": outputs}

    def resume_checker_node(state: AgentState) -> dict:
        logger.info("[NODE]      resume_checker started")
        t0 = time.time()
        result = run_resume_checker(llm, state["resume_text"])
        elapsed = time.time() - t0
        logger.info(
            "[NODE]      resume_checker completed (%d chars, %.2fs)",
            len(result), elapsed,
        )
        outputs = dict(state.get("tool_outputs") or {})
        outputs["resume_checker"] = result
        return {"tool_outputs": outputs}

    def career_coach_node(state: AgentState) -> dict:
        logger.info("[NODE]      career_coach started")
        t0 = time.time()
        result = run_career_coach(llm, state["resume_text"], state["messages"])
        elapsed = time.time() - t0
        logger.info(
            "[NODE]      career_coach completed (%d chars, %.2fs)",
            len(result), elapsed,
        )
        return {"messages": [AIMessage(content=result)]}

    # ── Responder node ────────────────────────────────
    def responder_node(state: AgentState) -> dict:
        """Synthesize tool outputs into a final AI message."""
        outputs = state.get("tool_outputs") or {}
        if not outputs:
            logger.info("[RESPONDER] no tool outputs — skipping")
            return {}

        # Single tool — return its output directly
        if len(outputs) == 1:
            tool_name = next(iter(outputs.keys()))
            result = next(iter(outputs.values()))
            logger.info(
                "[RESPONDER] 1 tool output (%s) → final message (%d chars)",
                tool_name, len(result),
            )
            return {"messages": [AIMessage(content=result)]}

        # Multiple tools — combine with section headers
        sections = []
        for tool_name, result in outputs.items():
            label = TOOL_LABELS.get(tool_name, tool_name)
            sections.append(f"## {label}\n\n{result}")

        combined = "\n\n---\n\n".join(sections)
        logger.info(
            "[RESPONDER] %d tool output(s) → final message (%d chars)",
            len(outputs), len(combined),
        )
        return {"messages": [AIMessage(content=combined)]}

    # ── Conditional routing ───────────────────────────
    def route_after_router(state: AgentState) -> str:
        choice = state.get("tool_choice", "none")
        if choice == "multi":
            chain = state.get("tool_chain", [])
            next_node = chain[0] if chain else "career_coach"
            logger.info("[ROUTE]     after router → %s (multi, first in chain)", next_node)
            return next_node
        if choice in ("cover_letter", "resume_scorer", "resume_checker", "career_coach"):
            logger.info("[ROUTE]     after router → %s", choice)
            return choice
        logger.info("[ROUTE]     after router → END (no tool needed)")
        return "__end__"

    def route_after_tool(state: AgentState) -> str:
        """After a tool, chain to the next tool or go to responder."""
        if state.get("tool_choice") != "multi":
            logger.info("[ROUTE]     after tool → responder (single tool)")
            return "responder"

        chain = state.get("tool_chain", [])
        executed = set((state.get("tool_outputs") or {}).keys())

        for tool_name in chain:
            if tool_name not in executed:
                logger.info(
                    "[ROUTE]     after tool → %s (next in chain, done=%s)",
                    tool_name, executed,
                )
                return tool_name

        logger.info("[ROUTE]     after tool → responder (chain complete)")
        return "responder"

    # ── Wire the graph ────────────────────────────────
    graph.add_node("router", router_node)
    graph.add_node("cover_letter", cover_letter_node)
    graph.add_node("resume_scorer", resume_scorer_node)
    graph.add_node("resume_checker", resume_checker_node)
    graph.add_node("career_coach", career_coach_node)
    graph.add_node("responder", responder_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "cover_letter": "cover_letter",
            "resume_scorer": "resume_scorer",
            "resume_checker": "resume_checker",
            "career_coach": "career_coach",
            "__end__": END,
        },
    )

    # Each tool node routes to next-in-chain or responder
    for tool_node in ["cover_letter", "resume_scorer", "resume_checker"]:
        graph.add_conditional_edges(
            tool_node,
            route_after_tool,
            {
                "cover_letter": "cover_letter",
                "resume_scorer": "resume_scorer",
                "resume_checker": "resume_checker",
                "responder": "responder",
            },
        )

    # Career coach goes directly to END (adds its own message)
    graph.add_edge("career_coach", END)

    # Responder always ends
    graph.add_edge("responder", END)

    return graph.compile()
