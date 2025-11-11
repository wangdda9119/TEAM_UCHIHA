"""
ReAct-style Tool Calling Agent for LangChain 1.0.x (no AgentExecutor)
- Compatible with: langchain==1.0.5, langchain-core==1.0.4
- Pattern: ChatOpenAI.bind_tools() + manual tool-call loop
"""

import os
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 네가 이미 갖고 있는 툴 목록 (BaseTool / 함수 혼재 가능)
from backend.ai.tools.tools import TOOLS


def _build_tool_registry(tools: List[Any]) -> Dict[str, Callable]:
    """
    TOOLS 리스트로부터 {tool_name: callable} 레지스트리를 만든다.
    - BaseTool(.invoke/.run) 또는 단순 함수(callable) 모두 지원.
    """
    registry: Dict[str, Callable] = {}
    for t in tools:
        # BaseTool 스타일
        name = getattr(t, "name", None) or getattr(t, "__name__", None)
        if not name:
            continue

        if hasattr(t, "invoke") and callable(getattr(t, "invoke")):
            registry[name] = t.invoke
        elif hasattr(t, "run") and callable(getattr(t, "run")):
            registry[name] = t.run
        elif callable(t):
            registry[name] = t
        else:
            logger.warning(f"⚠️ Tool '{name}'는 호출 가능한 형태가 아님. 건너뜀.")
    return registry


class ReactAgent:
    """
    LangChain 1.0.x 호환 ReAct 스타일 툴 호출 에이전트
    - bind_tools()로 툴 제공
    - AIMessage.tool_calls를 읽어 직접 툴 실행
    - ToolMessage로 관찰값을 이어주며 반복
    """

    def __init__(self, max_iterations: int = 8, temperature: float = 0.3, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        self.llm = ChatOpenAI(api_key=api_key, model=model, temperature=temperature)
        self.max_iterations = max_iterations
        self.memory: List[Dict[str, Any]] = []

        # 툴 레지스트리 준비
        self.tools = TOOLS
        self.tool_registry = _build_tool_registry(self.tools)

        # 프롬프트(시스템 + 히스토리 + 유저 입력)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "당신은 ReAct 패턴을 따르는 지능형 AI 어시스턴트입니다. "
                        "단계적으로 사고하고, 필요한 경우 도구를 호출해 정확한 답을 도출하세요. "
                        "모든 응답은 한국어로 작성하세요."
                    )
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )

        logger.info("✅ ReactAgent 초기화 완료 (LangChain 1.0.x 호환)")

    def _render_messages(
        self,
        question: str,
        chat_history_msgs: List[Any],
        scratchpad_msgs: List[Any],
    ) -> List[Any]:
        """
        시스템/히스토리/유저/툴 상호작용을 합쳐 최종 메시지 리스트를 만든다.
        """
        # ChatPromptTemplate을 사용해 시스템 + 히스토리 + 유저까지 우선 구성
        rendered = self.prompt.invoke(
            {
                "chat_history": chat_history_msgs,
                "input": question,
            }
        ).to_messages()  # List[BaseMessage]

        # scratchpad(이전 loop의 AI tool_calls + ToolMessage 관찰값)를 뒤에 이어붙임
        return rendered + scratchpad_msgs

    def run(self, question: str, chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        질문을 받고 툴 호출 루프를 돌며 최종 답을 생성한다.
        """
        try:
            logger.info(f"🤖 에이전트 시작: {question}")

            # 1) 히스토리 변환
            chat_history_msgs: List[Any] = []
            if chat_history:
                for m in chat_history:
                    role = m.get("role")
                    content = m.get("content", "")
                    if role == "user":
                        chat_history_msgs.append(HumanMessage(content=content))
                    elif role == "assistant":
                        chat_history_msgs.append(AIMessage(content=content))

            # 2) 툴 바인딩된 모델
            llm_with_tools = self.llm.bind_tools(self.tools)

            # 3) 루프(툴 호출 → 관찰값 → 재질의)
            scratchpad: List[Any] = []  # AIMessage(tool_calls=...)와 ToolMessage들을 누적
            iterations = 0
            final_answer = None

            while iterations < self.max_iterations:
                messages = self._render_messages(question, chat_history_msgs, scratchpad)
                ai_msg: AIMessage = llm_with_tools.invoke(messages)

                # 툴 호출이 없으면 최종 답으로 종료
                tool_calls = getattr(ai_msg, "tool_calls", None) or []
                if not tool_calls:
                    final_answer = ai_msg.content
                    break

                # 각 툴 호출 실행
                for tc in tool_calls:
                    tool_name = tc.get("name")
                    tool_args = tc.get("args", {}) or {}
                    call_id = tc.get("id") or ""

                    func = self.tool_registry.get(tool_name)
                    if not func:
                        obs = f"[tool_error] Unknown tool: {tool_name}"
                        logger.warning(obs)
                    else:
                        try:
                            obs = func(tool_args) if isinstance(tool_args, dict) else func(tool_args)
                        except Exception as ex:
                            obs = f"[tool_error] {type(ex).__name__}: {ex}"

                    # 관찰값을 ToolMessage로 추가
                    scratchpad.append(ai_msg)  # AIMessage (tool_calls 포함)
                    scratchpad.append(ToolMessage(tool_call_id=call_id, content=str(obs)))

                iterations += 1

            if final_answer is None:
                final_answer = "충분한 정보로 답을 확정하지 못했습니다."

            # 메모리 기록
            self.memory.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "answer",
                    "question": question,
                    "answer": final_answer,
                    "iterations": iterations,
                }
            )

            logger.info(f"✅ 에이전트 완료(iter={iterations}): {final_answer[:100]}...")
            return {
                "question": question,
                "answer": final_answer,
                "iterations": iterations,
                "status": "success",
                "memory": self.memory,
            }

        except Exception as e:
            logger.exception("Agent run failed")
            return {
                "question": question,
                "answer": f"❌ 오류 발생: {e}",
                "iterations": 0,
                "status": "error",
                "memory": self.memory,
            }

    # 편의 유틸
    def clear_memory(self) -> None:
        self.memory = []
        logger.info("🗑️ 메모리 초기화됨")

    def get_memory(self) -> List[Dict[str, Any]]:
        return self.memory


# =======================================================
# 싱글톤 인스턴스
# =======================================================

_agent_instance: Optional[ReactAgent] = None


def get_react_agent(max_iterations: int = 8) -> ReactAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ReactAgent(max_iterations=max_iterations)
    return _agent_instance
