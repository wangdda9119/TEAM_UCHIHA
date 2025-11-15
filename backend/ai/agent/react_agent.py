# backend/ai/agent/react_agent.py

from typing import List, Any, TypedDict

from loguru import logger
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph
from langgraph.constants import END

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage
)

from backend.core.config import settings
from langchain_core.prompts import ChatPromptTemplate

# Tools
from backend.ai.tools.search.web_search import web_search
from backend.ai.tools.search.hyupsung_info import uhs_fetch_info
from backend.ai.tools.search.rag_search import rag_search

from backend.ai.agent.prompts.system_prompt import SYSTEM_PROMPT
from backend.ai.memory.chat_memory import chat_memory


# ---------------------------------------------------
# 1) LLM 초기화
# ---------------------------------------------------
llm = ChatOpenAI(
    api_key=settings.openai_api_key,
    model="gpt-4o",
    temperature=0.2
)

# ---------------------------------------------------
# 2) 도구 목록
# ---------------------------------------------------
TOOLS = [web_search, uhs_fetch_info, rag_search]
TOOL_REGISTRY = {t.name: t for t in TOOLS}


# ---------------------------------------------------
# 3) LangGraph 상태 정의
# ---------------------------------------------------
class AgentState(TypedDict):
    messages: List[Any]
    session_id: str


# ---------------------------------------------------
# 4) 노드 정의
# ---------------------------------------------------
def call_agent(state: AgentState):
    """
    LLM 호출 노드
    """
    llm_with_tools = llm.bind_tools(TOOLS)
    ai_msg = llm_with_tools.invoke(state["messages"])

    return {
        "messages": state["messages"] + [ai_msg]
    }


def call_tool(state: AgentState):
    """
    Tool 호출 노드
    """
    last_msg = state["messages"][-1]

    tool_call = last_msg.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call.get("args", {})
    call_id = tool_call["id"]

    logger.info(f"🔧 Tool 호출: {tool_name}({tool_args})")

    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None:
        result = f"[ERROR] 존재하지 않는 도구: {tool_name}"
    else:
        try:
            result = tool.invoke(tool_args)
        except Exception as e:
            result = f"[ERROR] 도구 실행 실패: {str(e)}"

    tool_msg = ToolMessage(content=str(result), tool_call_id=call_id)

    return {
        "messages": state["messages"] + [tool_msg]
    }


# ---------------------------------------------------
# 5) Graph 설계
# ---------------------------------------------------
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_agent)
workflow.add_node("tool", call_tool)

workflow.set_entry_point("agent")


def should_continue(state: AgentState):
    last_msg = state["messages"][-1]

    if getattr(last_msg, "tool_calls", None):
        return "tool"

    return END


workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tool", "agent")

app = workflow.compile()


# ---------------------------------------------------
# 6) FastAPI에서 호출하는 메인 함수
# ---------------------------------------------------
async def run_react_agent(question: str, session_id: str, language: str = "ko"):
    """
    ◆ session_id 기반 대화 기억 포함
    ◆ 언어별 번역 지원
    """
    logger.info(f"🤖 run_react_agent(): session={session_id}, question={question}, language={language}")
    
    # 영어 질문을 한국어로 번역
    if language == "en":
        translated_question = await translate_text(question, "ko")
        logger.info(f"🔄 번역된 질문: {translated_question}")
    else:
        translated_question = question

    # 기존 memory 불러오기
    history = chat_memory.get(session_id)

    # 이번 질문 추가 (번역된 질문 사용)
    history.append(HumanMessage(content=translated_question))

    # 초기 상태
    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            *history
        ],
        "session_id": session_id
    }

    result = app.invoke(initial_state)

    final_msg = result["messages"][-1]

    # 메모리에 AI 답변도 저장
    chat_memory.add(session_id, final_msg)

    # 영어 요청시 답변을 영어로 번역
    if language == "en":
        translated_answer = await translate_text(final_msg.content, "en")
        return translated_answer
    
    return final_msg.content


async def translate_text(text: str, target_lang: str) -> str:
    """
    텍스트를 대상 언어로 번역
    """
    try:
        translate_prompt = ChatPromptTemplate.from_messages([
            ("system", f"Translate the following text to {'Korean' if target_lang == 'ko' else 'English'}. Only return the translated text, nothing else."),
            ("human", "{text}")
        ])
        
        chain = translate_prompt | llm
        result = chain.invoke({"text": text})
        return result.content
    except Exception as e:
        logger.error(f"번역 오류: {e}")
        return text  # 번역 실패시 원본 반환
