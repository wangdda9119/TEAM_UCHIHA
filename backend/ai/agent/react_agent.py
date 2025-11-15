# ========================================
# LangGraph ReAct Agent - 완전 정상 작동 버전
# ========================================

from typing import Dict, Any, List, TypedDict

from loguru import logger
from langgraph.graph import StateGraph
from langgraph.constants import END
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool

from backend.core.config import settings
from backend.ai.tools.search.web_search import web_search
from backend.ai.tools.search.hyupsung_info import uhs_fetch_info
from backend.ai.tools.search.rag_search import rag_search
from backend.ai.agent.prompts.system_prompt import SYSTEM_PROMPT


# ======================================================
# 1) LLM & Tools 정의
# ======================================================
llm = ChatOpenAI(
    api_key=settings.openai_api_key,
    model="gpt-4o",
    temperature=0.2,
)

# 도구 정의
TOOLS: List[BaseTool] = [web_search, uhs_fetch_info, rag_search]
TOOL_REGISTRY: Dict[str, BaseTool] = {t.name: t for t in TOOLS}


# ======================================================
# 2) LangGraph State Schema
# ======================================================
class AgentState(TypedDict):
    messages: List[Any]


# ======================================================
# 3) 노드 함수
# ======================================================

def call_agent(state: AgentState) -> Dict[str, Any]:
    """
    LLM 호출 노드
    """
    messages = state["messages"]
    llm_with_tools = llm.bind_tools(TOOLS)

    logger.info("🧠 call_agent 실행")

    ai_msg = llm_with_tools.invoke(messages)

    # 메시지 추가 후 반환
    return {"messages": messages + [ai_msg]}


def call_tool(state: AgentState) -> Dict[str, Any]:
    """
    Tool 호출 노드
    """
    messages = state["messages"]
    last_msg = messages[-1]

    logger.info("🔧 call_tool 실행")

    # tool_calls가 없으면 그대로 반환
    tool_calls = getattr(last_msg, "tool_calls", None)
    if not tool_calls:
        logger.warning("⚠️ tool_calls 없음. agent로 복귀.")
        return {"messages": messages}

    tc = tool_calls[0]
    tool_name = tc.get("name")
    tool_args = tc.get("args", {})
    tool_call_id = tc.get("id")

    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        observation = f"[ERROR] Unknown tool: {tool_name}"
    else:
        try:
            observation = tool.invoke(tool_args)
        except Exception as e:
            observation = f"[도구 실행 오류] {e}"

    tool_msg = ToolMessage(content=str(observation), tool_call_id=tool_call_id)

    return {"messages": messages + [tool_msg]}


# ======================================================
# 4) Workflow Graph 구성
# ======================================================

workflow = StateGraph(AgentState)

workflow.add_node("agent", call_agent)
workflow.add_node("tool", call_tool)

workflow.set_entry_point("agent")


def should_continue(state: AgentState):
    last = state["messages"][-1]

    tool_calls = getattr(last, "tool_calls", None)

    if tool_calls:
        return "tool"

    return END   # 종료


# agent → tool or end
workflow.add_conditional_edges("agent", should_continue)

# tool → agent 반복
workflow.add_edge("tool", "agent")

app = workflow.compile()


# ======================================================
# 5) 최종 실행 함수
# ======================================================
async def run_react_agent(question: str, memory=None) -> str:
    """
    FastAPI에서 호출하는 엔트리포인트 함수.
    memory 인자는 현재 사용하지 않지만 향후 확장을 위해 남겨둠.
    """
    logger.info(f"🤖 run_react_agent: {question}")

    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
    }

    result = app.invoke(initial_state)

    final_msg = result["messages"][-1]

    return final_msg.content
