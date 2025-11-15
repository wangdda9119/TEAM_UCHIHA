"""
Tools-Agent 통합 실제 사용 예제
"""

# ============================================================================
# 예제 1: 모든 도구 사용 (기본)
# ============================================================================

from backend.ai.agents import ReactAgent

def example_1_all_tools():
    """모든 도구를 사용하는 에이전트"""
    print("예제 1: 모든 도구 사용")
    print("-" * 50)
    
    agent = ReactAgent()
    
    # 도구 요약 확인
    agent.print_tools_summary()
    
    # 질문 실행 (실제 실행은 OPENAI_API_KEY 필요)
    # result = agent.run("파이썬 최신 버전은?")
    # print(f"답변: {result['answer']}")


# ============================================================================
# 예제 2: 특정 카테고리 선택
# ============================================================================

def example_2_category_selection():
    """특정 카테고리 도구만 사용"""
    print("\n예제 2: 카테고리 기반 선택")
    print("-" * 50)
    
    # 방식 1: 검색 도구만
    agent_search = ReactAgent(tool_categories=["search"])
    print(f"검색 전용 에이전트: {len(agent_search.tools)}개 도구")
    for tool_info in agent_search.get_available_tools():
        print(f"  - {tool_info['name']}")
    
    # 방식 2: 검색 + 계산
    agent_search_math = ReactAgent(tool_categories=["search", "math"])
    print(f"\n검색+계산 에이전트: {len(agent_search_math.tools)}개 도구")
    for tool_info in agent_search_math.get_available_tools():
        print(f"  - {tool_info['name']}")
    
    # 방식 3: 모든 카테고리
    agent_all = ReactAgent(tool_categories=["search", "data", "system", "math"])
    print(f"\n전체 에이전트: {len(agent_all.tools)}개 도구")


# ============================================================================
# 예제 3: 커스텀 도구 선택
# ============================================================================

def example_3_custom_tools():
    """특정 도구만 선택"""
    print("\n예제 3: 커스텀 도구 선택")
    print("-" * 50)
    
    from backend.ai.tools import calculator, web_search
    
    # 특정 도구만 사용
    agent = ReactAgent(tools=[calculator, web_search])
    print(f"커스텀 에이전트: {len(agent.tools)}개 도구")
    agent.print_tools_summary()


# ============================================================================
# 예제 4: ToolManager 직접 사용
# ============================================================================

def example_4_tool_manager():
    """ToolManager를 직접 사용"""
    print("\n예제 4: ToolManager 직접 사용")
    print("-" * 50)
    
    from backend.ai.tools import get_tool_manager
    
    manager = get_tool_manager()
    
    # 전체 도구 개수
    all_tools = manager.get_all_tools()
    print(f"✅ 총 {len(all_tools)}개 도구 로드됨")
    
    # 카테고리 정보
    print("\n📂 카테고리별 도구:")
    cat_info = manager.get_category_info()
    for category, info in cat_info.items():
        print(f"  [{category}] {info['count']}개: {', '.join(info['tools'])}")
    
    # 특정 도구 정보
    print("\n📋 도구 정보 (calculator):")
    tool_info = manager.get_tool_info("calculator")
    print(f"  이름: {tool_info['name']}")
    print(f"  설명: {tool_info['description']}")
    print(f"  카테고리: {tool_info['category']}")
    print(f"  파라미터: {list(tool_info['params'].keys())}")
    
    # 도구 검증
    print("\n🔍 도구 검증:")
    validation = manager.validate_tools()
    passed = sum(1 for v in validation.values() if v)
    print(f"  검증 통과: {passed}/{len(validation)}")
    
    # 전체 요약
    print("\n📊 전체 도구 요약:")
    manager.print_tools_summary()


# ============================================================================
# 예제 5: API 통합 시뮬레이션
# ============================================================================

def example_5_api_integration():
    """FastAPI 통합 예제"""
    print("\n예제 5: API 통합 예제")
    print("-" * 50)
    
    print("""
# API 라우트 예제:

from fastapi import APIRouter
from pydantic import BaseModel
from backend.ai.agents import ReactAgent

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    tool_categories: list[str] = None

@router.post("/agent/query")
async def agent_query(request: QueryRequest):
    '''
    에이전트 질의 엔드포인트
    '''
    # 에이전트 생성 (카테고리 선택)
    if request.tool_categories:
        agent = ReactAgent(tool_categories=request.tool_categories)
    else:
        agent = ReactAgent()
    
    # 질의 실행
    result = agent.run(request.question)
    
    return {
        "question": request.question,
        "answer": result["answer"],
        "tools_used": result.get("tool_calls", []),
        "iterations": result.get("iterations", 0)
    }

@router.get("/agent/tools")
async def agent_tools(categories: list[str] = None):
    '''
    사용 가능한 도구 목록 조회
    '''
    from backend.ai.tools import get_tool_manager
    
    manager = get_tool_manager()
    
    if categories:
        tools = manager.get_tools_by_categories(categories)
    else:
        tools = manager.get_all_tools()
    
    return {
        "count": len(tools),
        "tools": [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in tools
        ]
    }

@router.get("/agent/categories")
async def agent_categories():
    '''
    사용 가능한 카테고리 조회
    '''
    from backend.ai.tools import get_tool_manager
    
    manager = get_tool_manager()
    info = manager.get_category_info()
    
    return {
        "categories": list(info.keys()),
        "details": info
    }
    """)


# ============================================================================
# 예제 6: 고급 - 도구 필터링 및 커스타마이징
# ============================================================================

def example_6_advanced():
    """고급 사용법"""
    print("\n예제 6: 고급 사용법")
    print("-" * 50)
    
    from backend.ai.tools import get_tool_manager, ToolManager
    from backend.ai.agents import ReactAgent
    
    # 1. 특정 도구 제외
    manager = get_tool_manager()
    all_tools = manager.get_all_tools()
    
    # web_search 제외
    filtered_tools = [
        t for t in all_tools 
        if getattr(t, 'name', None) != 'web_search'
    ]
    agent = ReactAgent(tools=filtered_tools)
    print(f"web_search 제외: {len(agent.tools)}개 도구 사용")
    
    # 2. 동적 카테고리 선택
    user_preference = {
        "search_enabled": True,
        "math_enabled": False,
        "data_enabled": True,
    }
    
    categories = [
        cat for cat, enabled in user_preference.items()
        if enabled and cat.endswith('_enabled')
    ]
    categories = [cat.replace('_enabled', '') for cat in categories]
    
    if categories:
        agent = ReactAgent(tool_categories=categories)
        print(f"사용자 선호도 기반: {len(agent.tools)}개 도구")


# ============================================================================
# 메인
# ============================================================================

def main():
    print("\n" + "="*70)
    print("🛠️  Tools-Agent 통합 실제 사용 예제")
    print("="*70)
    
    try:
        example_1_all_tools()
        example_2_category_selection()
        example_3_custom_tools()
        example_4_tool_manager()
        example_5_api_integration()
        example_6_advanced()
        
        print("\n" + "="*70)
        print("✅ 모든 예제 완료!")
        print("="*70 + "\n")
        
    except ValueError as e:
        print(f"\n⚠️  환경변수 오류 (OPENAI_API_KEY 필요): {e}")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
