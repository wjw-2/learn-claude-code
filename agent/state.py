from langgraph.graph import MessagesState


class CodeAgentState(MessagesState):
    """Custom state for the code agent, extending MessagesState with metadata."""

    summary: str = ""
