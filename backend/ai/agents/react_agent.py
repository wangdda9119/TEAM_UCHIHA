"""
ReAct-style Tool Calling Agent for LangChain 1.0.x+
- 호환: langchain>=1.0.5, langchain-core>=1.0.4
- 패턴: ChatOpenAI.bind_tools() + 수동 tool-call 루프
- 최신 @tool 데코레이터 사용 (Pydantic v2)
- ToolManager를 통한 도구 관리
"""

import os
from typing import Optional, List, Dict, Any, Callable, Union
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
from langchain_core.tools import BaseTool

# 도구 및 도구 매니저
from backend.ai.tools import ALL_TOOLS, get_tool_manager, ToolManager


def _build_tool_registry(tools: List[Union[BaseTool, Callable]]) -> Dict[str, Callable]:
    """
    도구 리스트로부터 {tool_name: 래퍼함수} 레지스트리를 생성합니다.
    
    지원하는 도구 타입:
    - @tool 데코레이터 기반 함수 (BaseTool - invoke(input=dict))
    - BaseTool 인스턴스 (.invoke / .run 메서드)
    - 일반 함수 (**kwargs 형식)
    
    주의: @tool으로 생성된 BaseTool의 invoke()는 input 파라미터를 받으므로
    래퍼 함수로 감싸서 **kwargs를 input=dict로 변환합니다.
    
    Args:
        tools: 도구 리스트 (혼합 타입 가능)
    
    Returns:
        {도구_이름: 호출가능_래퍼함수} 딕셔너리
    """
    registry: Dict[str, Callable] = {}
    for t in tools:
        # 도구 이름 추출
        name = getattr(t, "name", None) or getattr(t, "__name__", None)
        if not name:
            logger.warning(f"⚠️ 도구 이름을 결정할 수 없음: {t}")
            continue

        # @tool 데코레이터 기반 BaseTool 인지 확인
        # (invoke 메서드가 input 파라미터를 받는 방식)
        if isinstance(t, BaseTool) and hasattr(t, "invoke"):
            # BaseTool.invoke(input=dict_or_str) 형식을 래핑
            def make_wrapper(tool):
                def wrapper(**kwargs):
                    # invoke()는 input 파라미터로 dict나 str을 받음
                    return tool.invoke(input=kwargs)
                return wrapper
            registry[name] = make_wrapper(t)
        elif callable(t):
            # 일반 함수는 직접 사용
            registry[name] = t
        else:
            logger.warning(f"⚠️ 도구 '{name}'는 호출 불가능: {type(t)}")
    
    logger.info(f"✅ 도구 레지스트리 구성 완료: {len(registry)}개 도구")
    return registry


class ReactAgent:
    """
    LangChain 1.0.x+ 호환 ReAct 스타일 도구 호출 에이전트
    
    특징:
    - bind_tools()로 도구 제공
    - AIMessage.tool_calls 구조로 도구 호출
    - ToolMessage로 관찰값 피드백
    - 최신 @tool 데코레이터 (Pydantic v2) 지원
    
    사용 예:
        agent = ReactAgent()
        result = agent.run("파이썬 최신 버전은?")
        print(result["answer"])
    """

    def __init__(
        self,
        max_iterations: int = 8,
        temperature: float = 0.3,
        model: str = "gpt-4o-mini",
        tools: Optional[List[Union[BaseTool, Callable]]] = None,
        tool_categories: Optional[List[str]] = None,
        tool_manager: Optional[ToolManager] = None,
    ):
        """
        ReAct 에이전트 초기화
        
        Args:
            max_iterations: 최대 도구 호출 반복 횟수
            temperature: LLM 응답 창의성 (0~2)
            model: OpenAI 모델명
            tools: 사용할 도구 리스트 (None이면 ALL_TOOLS 사용)
            tool_categories: 특정 카테고리만 사용 (예: ["search", "math"])
                            이 옵션이 지정되면 tools 파라미터는 무시됨
            tool_manager: 커스텀 ToolManager 인스턴스 (기본값: 글로벌 인스턴스)
        
        사용 예:
            # 방식 1: 기본 도구 모두 사용
            agent = ReactAgent()
            
            # 방식 2: 특정 카테고리만 사용
            agent = ReactAgent(tool_categories=["search", "math"])
            
            # 방식 3: 커스텀 도구 리스트
            agent = ReactAgent(tools=[web_search, calculator])
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

        self.llm = ChatOpenAI(api_key=api_key, model=model, temperature=temperature)
        self.max_iterations = max_iterations
        self.memory: List[Dict[str, Any]] = []

        # 도구 매니저 설정
        self.tool_manager = tool_manager or get_tool_manager()
        
        # 도구 선택 로직
        if tool_categories is not None:
            # 카테고리로 도구 선택
            self.tools = self.tool_manager.get_tools_by_categories(tool_categories)
            logger.info(f"📂 카테고리 기반 도구 선택: {tool_categories}")
        elif tools is not None:
            # 직접 전달된 도구 리스트 사용
            self.tools = tools
            logger.info(f"📋 커스텀 도구 리스트 사용: {len(tools)}개")
        else:
            # 모든 도구 사용
            self.tools = self.tool_manager.get_all_tools()
            logger.info(f"📦 모든 도구 사용: {len(self.tools)}개")
        
        self.tool_registry = _build_tool_registry(self.tools)

        # 프롬프트 템플릿
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "당신은 ReAct (Reasoning + Acting) 패턴을 따르는 지능형 AI 어시스턴트입니다.\n\n"
                        "작동 방식:\n"
                        "1. Thought: 질문을 분석하고 해결 방법을 생각합니다\n"
                        "2. Action: 필요한 도구를 선택해 호출합니다\n"
                        "3. Observation: 도구 실행 결과를 확인합니다\n"
                        "4. 반복: 최종 답을 얻을 때까지 반복합니다\n\n"
                        "지침:\n"
                        "- 모든 응답은 한국어로 작성하세요\n"
                        "- 단계적으로 논리적으로 접근하세요\n"
                        "- 정확한 답변을 위해 필요한 도구를 적극 활용하세요"
                    )
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )

        logger.info(
            f"✅ ReactAgent 초기화: {model} (tools={len(self.tool_registry)}, "
            f"max_iter={max_iterations}, manager_enabled=True)"
        )

    def get_available_tools(self) -> List[Dict[str, str]]:
        """
        사용 가능한 도구 목록을 반환합니다.
        
        Returns:
            [{"name": str, "description": str}, ...] 형식의 리스트
        """
        tools_info = []
        for tool in self.tools:
            tool_name = getattr(tool, "name", getattr(tool, "__name__", "unknown"))
            tool_desc = getattr(tool, "description", "설명 없음")
            tools_info.append({
                "name": tool_name,
                "description": tool_desc
            })
        return tools_info
    
    def print_tools_summary(self) -> None:
        """사용 중인 도구의 요약을 출력합니다."""
        print("\n" + "="*70)
        print(f"🛠️  ReAct 에이전트 - {len(self.tools)}개 도구 사용 중")
        print("="*70 + "\n")
        
        for i, tool_info in enumerate(self.get_available_tools(), 1):
            print(f"{i}. {tool_info['name']}")
            print(f"   {tool_info['description'][:60]}...")
        
        print("\n" + "="*70 + "\n")

    def _render_messages(
        self,
        question: str,
        chat_history_msgs: List[Any],
        scratchpad_msgs: List[Any],
    ) -> List[Any]:
        """
        최종 메시지 리스트를 생성합니다.
        
        구조: [시스템 메시지] + [채팅 히스토리] + [사용자 입력] + [스크래치패드]
        - 스크래치패드: 이전 루프의 도구 호출 + 결과 메시지들
        
        Args:
            question: 사용자 질문
            chat_history_msgs: 채팅 히스토리 메시지
            scratchpad_msgs: 도구 상호작용 스크래치패드
        
        Returns:
            최종 메시지 리스트
        """
        rendered = self.prompt.invoke(
            {
                "chat_history": chat_history_msgs,
                "input": question,
            }
        ).to_messages()
        
        return rendered + scratchpad_msgs

    def run(
        self,
        question: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        에이전트를 실행하여 질문에 답합니다.
        
        프로세스:
        1. 히스토리 변환
        2. 도구 바인딩
        3. ReAct 루프:
           - LLM에 도구 호출 요청
           - 각 도구 실행 및 결과 수집
           - ToolMessage로 피드백
           - 최종 답변 도출까지 반복
        
        Args:
            question: 사용자 질문
            chat_history: 이전 대화 히스토리 [{"role": "user"|"assistant", "content": "..."}]
        
        Returns:
            {
                "question": str,
                "answer": str,
                "iterations": int,
                "status": "success" | "error",
                "memory": List[Dict],
                "tools_used": List[str]
            }
        """
        try:
            logger.info(f"🤖 에이전트 시작: {question}")

            # 1) 히스토리 메시지 변환
            chat_history_msgs: List[Any] = []
            if chat_history:
                for m in chat_history:
                    role = m.get("role", "").lower()
                    content = m.get("content", "")
                    
                    if role == "user":
                        chat_history_msgs.append(HumanMessage(content=content))
                    elif role == "assistant":
                        chat_history_msgs.append(AIMessage(content=content))
                    else:
                        logger.warning(f"⚠️ 알 수 없는 역할: {role}")

            # 2) 도구 바인딩된 LLM
            llm_with_tools = self.llm.bind_tools(self.tools)

            # 3) ReAct 루프
            scratchpad: List[Any] = []
            iterations = 0
            final_answer = None
            tools_used: List[str] = []

            while iterations < self.max_iterations:
                logger.debug(f"🔄 반복 {iterations + 1}/{self.max_iterations}")
                
                messages = self._render_messages(question, chat_history_msgs, scratchpad)
                ai_msg: AIMessage = llm_with_tools.invoke(messages)

                # 도구 호출 확인
                tool_calls = getattr(ai_msg, "tool_calls", None) or []
                if not tool_calls:
                    # 도구 호출 없음 → 최종 답변
                    final_answer = ai_msg.content
                    logger.info(f"✅ 최종 답변 도출 (반복: {iterations})")
                    break

                # 도구 호출 실행
                for tc in tool_calls:
                    tool_name = tc.get("name", "unknown")
                    tool_args = tc.get("args", {}) or {}
                    call_id = tc.get("id", "")

                    logger.debug(f"🔧 도구 호출: {tool_name}")

                    func = self.tool_registry.get(tool_name)
                    if not func:
                        obs = f"[오류] 알 수 없는 도구: {tool_name}"
                        logger.warning(obs)
                    else:
                        try:
                            # 도구 실행: 모든 도구는 이미 래핑되어 있음
                            # **kwargs 형식으로 호출
                            obs = func(**tool_args)
                            
                            tools_used.append(tool_name)
                            logger.debug(f"✅ {tool_name} 완료")
                        except TypeError as te:
                            obs = f"[오류] 도구 인자 오류: {str(te)}"
                            logger.error(f"도구 {tool_name} 인자 오류: {str(te)}")
                        except Exception as ex:
                            obs = f"[오류] {type(ex).__name__}: {str(ex)}"
                            logger.error(f"도구 {tool_name} 실행 오류: {str(ex)}")

                    # 스크래치패드에 추가
                    scratchpad.append(ai_msg)
                    scratchpad.append(ToolMessage(tool_call_id=call_id, content=str(obs)))

                iterations += 1

            if final_answer is None:
                final_answer = "충분한 정보로 최종 답을 도출하지 못했습니다."
                logger.warning("⚠️ 최대 반복 횟수 도달")

            # 메모리 기록
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "answer",
                "question": question,
                "answer": final_answer,
                "iterations": iterations,
                "tools_used": list(set(tools_used)),  # 중복 제거
            }
            self.memory.append(memory_entry)

            logger.info(f"✅ 에이전트 완료: {iterations}반복, 사용 도구={len(set(tools_used))}")
            
            return {
                "question": question,
                "answer": final_answer,
                "iterations": iterations,
                "status": "success",
                "memory": self.memory,
                "tools_used": list(set(tools_used)),
            }

        except Exception as e:
            logger.exception("❌ 에이전트 실행 오류")
            return {
                "question": question,
                "answer": f"❌ 오류 발생: {str(e)}",
                "iterations": 0,
                "status": "error",
                "memory": self.memory,
                "tools_used": [],
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
