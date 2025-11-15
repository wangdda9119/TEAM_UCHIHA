"""
React AI Agent API Routes
ReAct 패턴을 사용하는 지능형 에이전트 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from loguru import logger

from backend.ai.agents.react_agent import get_react_agent

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class AgentRequest(BaseModel):
    """에이전트 요청"""
    question: str = Field(..., description="에이전트에게 할 질문")
    max_iterations: int = Field(default=5, description="최대 반복 횟수")


class MemoryItem(BaseModel):
    """메모리 항목"""
    timestamp: str
    type: str  # "agent_step" 또는 "observation"
    iteration: int
    thought: Optional[str] = None
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None


class AgentResponse(BaseModel):
    """에이전트 응답"""
    question: str
    answer: str
    iterations: int
    status: str  # "success" 또는 "error"
    memory: Optional[List[Dict[str, Any]]] = None


class WebSearchRequest(BaseModel):
    """웹 검색 요청"""
    query: str = Field(..., description="검색 쿼리")
    max_results: int = Field(default=5, description="최대 결과 수")


class WebSearchResult(BaseModel):
    """웹 검색 결과"""
    title: str
    url: str
    content: str
    score: float


class WebSearchResponse(BaseModel):
    """웹 검색 응답"""
    query: str
    results: List[WebSearchResult]
    total_results: int
    status: str


# ============================================================================
# 1. React Agent Endpoint
# ============================================================================

@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """
    React 에이전트 실행
    
    ReAct (Reasoning + Acting) 패턴 사용:
    1. Thought: 현재 상황 분석
    2. Action: 도구 선택
    3. Observation: 결과 관찰
    4. 반복...
    
    Example:
        {
            "question": "파이썬 최신 버전은 무엇인가?",
            "max_iterations": 5
        }
    """
    try:
        logger.info(f"🤖 에이전트 요청: {request.question}")
        
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="질문이 비어있습니다"
            )
        
        # 에이전트 실행
        agent = get_react_agent(max_iterations=request.max_iterations)
        result = agent.run(request.question)
        
        return AgentResponse(
            question=result["question"],
            answer=result["answer"],
            iterations=result["iterations"],
            status=result["status"],
            memory=result["memory"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 에이전트 실행 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"에이전트 실행 실패: {str(e)}"
        )


# ============================================================================
# 2. Web Search Tool Endpoint
# ============================================================================

@router.post("/search", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest):
    """
    웹 검색 도구 (Tavily API 사용)
    
    Example:
        {
            "query": "파이썬 최신 버전",
            "max_results": 5
        }
    """
    try:
        logger.info(f"🔍 웹 검색 요청: {request.query}")
        
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="검색 쿼리가 비어있습니다"
            )
        
        from backend.ai.tools.search.web_search import get_tavily_tool
        
        tool = get_tavily_tool()
        results = tool.search(
            query=request.query,
            max_results=request.max_results
        )
        
        return WebSearchResponse(
            query=request.query,
            results=[
                WebSearchResult(
                    title=r["title"],
                    url=r["url"],
                    content=r["content"],
                    score=r["score"]
                )
                for r in results
            ],
            total_results=len(results),
            status="success" if results else "no_results"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 웹 검색 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"웹 검색 실패: {str(e)}"
        )


# ============================================================================
# 3. Agent Memory Endpoint
# ============================================================================

@router.get("/memory")
async def get_agent_memory():
    """
    에이전트 메모리 조회
    최근 대화 및 사고 과정 확인
    """
    try:
        agent = get_react_agent()
        memory = agent.get_memory()
        
        return {
            "memory_count": len(memory),
            "memory": memory,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"❌ 메모리 조회 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"메모리 조회 실패: {str(e)}"
        )


# ============================================================================
# 4. Clear Memory Endpoint
# ============================================================================

@router.delete("/memory")
async def clear_agent_memory():
    """
    에이전트 메모리 초기화
    """
    try:
        agent = get_react_agent()
        agent.clear_memory()
        
        return {
            "status": "success",
            "message": "메모리가 초기화되었습니다"
        }
    except Exception as e:
        logger.error(f"❌ 메모리 초기화 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"메모리 초기화 실패: {str(e)}"
        )


# ============================================================================
# 5. Available Tools Endpoint
# ============================================================================

@router.get("/tools")
async def list_tools():
    """
    사용 가능한 도구 목록 조회
    
    모든 @tool 데코레이터 기반 도구를 반환합니다:
    - 기본 도구: web_search, calculator
    - 고급 도구: json_parser, text_summarizer, string_manipulator, get_current_time, list_operations
    """
    try:
        from backend.ai.tools import ALL_TOOLS
        
        tools_info = []
        for tool in ALL_TOOLS:
            tools_info.append({
                "tool_id": tool.name,
                "name": tool.name,
                "description": tool.description or "설명 없음"
            })
        
        return {
            "tools": tools_info,
            "total_tools": len(tools_info),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"❌ 도구 목록 조회 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"도구 목록 조회 실패: {str(e)}"
        )


# ============================================================================
# 6. Health Check Endpoint
# ============================================================================

@router.get("/health")
async def health_check():
    """
    React AI Agent 서비스 헬스 체크
    
    서비스 상태와 사용 가능한 도구 정보를 반환합니다.
    """
    try:
        from backend.ai.tools import ALL_TOOLS
        
        agent = get_react_agent()
        
        return {
            "status": "ok",
            "service": "React AI Agent",
            "available_tools": len(ALL_TOOLS),
            "memory_size": len(agent.get_memory()),
            "tools": [tool.name for tool in ALL_TOOLS]
        }
    except Exception as e:
        logger.error(f"❌ 헬스 체크 오류: {str(e)}")
        return {
            "status": "error",
            "service": "React AI Agent",
            "error": str(e)
        }
