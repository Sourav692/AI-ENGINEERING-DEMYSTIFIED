from typing import TypedDict, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State that flows through the LangGraph agent."""

    # Chat messages — add_messages reducer appends new messages automatically
    messages: Annotated[list[BaseMessage], add_messages]

    # Resume text extracted from uploaded PDF (set once per session)
    resume_text: str

    # Job description pasted by the user (may be None)
    job_description: Optional[str]

    # Router decision — which tool(s) to invoke this turn
    tool_choice: Optional[str]

    # When tool_choice == "multi", lists the tools to chain in order
    tool_chain: Optional[list[str]]

    # Accumulates tool outputs keyed by tool name for the responder
    tool_outputs: Optional[dict[str, str]]
