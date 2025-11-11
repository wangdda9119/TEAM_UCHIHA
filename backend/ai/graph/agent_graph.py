
"""
Minimal LangGraph agent:
- State: {"question": str, "answer": str}
- Tool: mock_search
"""
from typing import TypedDict
from langgraph.graph import StateGraph, END
from loguru import logger

class AgentState(TypedDict):
    question: str
    answer: str

def mock_search_tool(query: str) -> str:
    # Replace with real tools in backend/ai/tools/*
    return f"[search] top result for '{query}'"

def agent_node(state: AgentState) -> AgentState:
    q = state["question"]
    logger.debug("Agent node handling question: %s", q)
    res = mock_search_tool(q)
    return {"question": q, "answer": f"Agent says: {res}"}

def get_agent_app():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)
    return graph.compile()
