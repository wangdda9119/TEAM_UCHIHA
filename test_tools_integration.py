"""
AI 도구 및 에이전트 통합 테스트

테스트:
1. ToolManager 기능 검증
2. ReactAgent와의 도구 연결
3. 도구 카테고리 기반 선택
4. 도구 메타데이터 조회
"""

import sys
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.ai.tools import get_tool_manager, ToolManager
from backend.ai.agent.react_agent import ReactAgent
from loguru import logger


def test_tool_manager_basic():
    """테스트 1: ToolManager 기본 기능"""
    print("\n" + "="*70)
    print("✅ 테스트 1: ToolManager 기본 기능")
    print("="*70)
    
    manager = ToolManager()
    
    # 모든 도구 조회
    all_tools = manager.get_all_tools()
    print(f"✓ 모든 도구: {len(all_tools)}개 로드됨")
    
    # 카테고리 확인
    categories = manager.get_categories()
    print(f"✓ 사용 가능한 카테고리: {categories}")
    
    # 카테고리별 도구 개수
    cat_info = manager.get_category_info()
    for cat, info in cat_info.items():
        print(f"  - {cat}: {info['count']}개 ({', '.join(info['tools'])})")


def test_tool_manager_selection():
    """테스트 2: ToolManager 도구 선택"""
    print("\n" + "="*70)
    print("✅ 테스트 2: ToolManager 도구 선택")
    print("="*70)
    
    manager = ToolManager()
    
    # 단일 카테고리
    search_tools = manager.get_tools_by_category("search")
    print(f"✓ 검색 도구: {len(search_tools)}개")
    
    # 여러 카테고리
    selected = manager.get_tools_by_categories(["search", "math"])
    print(f"✓ 검색 + 계산 도구: {len(selected)}개")
    
    # 특정 도구 조회
    calc_tool = manager.get_tool_by_name("calculator")
    print(f"✓ 특정 도구 조회 (calculator): {calc_tool is not None}")


def test_tool_info():
    """테스트 3: 도구 메타데이터"""
    print("\n" + "="*70)
    print("✅ 테스트 3: 도구 메타데이터")
    print("="*70)
    
    manager = ToolManager()
    
    # 특정 도구 정보
    info = manager.get_tool_info("calculator")
    print(f"✓ 도구: {info['name']}")
    print(f"  - 카테고리: {info['category']}")
    print(f"  - 설명: {info['description'][:60]}...")
    print(f"  - 파라미터: {list(info['params'].keys())}")
    
    # 모든 도구 정보
    all_info = manager.list_tools_with_info()
    print(f"\n✓ 도구 정보 목록: {len(all_info)}개")
    for tool in all_info[:3]:
        print(f"  - {tool['name']} ({tool['category']})")
    print(f"  ... 및 {len(all_info)-3}개 더")


def test_tool_validation():
    """테스트 4: 도구 검증"""
    print("\n" + "="*70)
    print("✅ 테스트 4: 도구 검증")
    print("="*70)
    
    manager = ToolManager()
    results = manager.validate_tools()
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"✓ 검증 결과: {passed}/{total} 도구 정상")
    
    failed = [k for k, v in results.items() if not v]
    if failed:
        print(f"  ⚠️  실패한 도구: {failed}")
    else:
        print(f"  모든 도구 정상! 🎉")


def test_react_agent_with_all_tools():
    """테스트 5: ReactAgent - 모든 도구 사용"""
    print("\n" + "="*70)
    print("✅ 테스트 5: ReactAgent - 모든 도구 사용")
    print("="*70)
    
    try:
        agent = ReactAgent()
        print(f"✓ ReactAgent 초기화: {len(agent.tools)}개 도구")
        
        # 도구 목록 출력
        tools_info = agent.get_available_tools()
        print(f"✓ 사용 가능한 도구:")
        for info in tools_info:
            print(f"  - {info['name']}: {info['description'][:40]}...")
        
    except ValueError as e:
        print(f"⚠️  환경변수 없음: {e}")


def test_react_agent_with_categories():
    """테스트 6: ReactAgent - 카테고리별 도구"""
    print("\n" + "="*70)
    print("✅ 테스트 6: ReactAgent - 카테고리별 도구")
    print("="*70)
    
    try:
        # 검색과 계산만 사용
        agent = ReactAgent(tool_categories=["search", "math"])
        print(f"✓ ReactAgent 초기화 (검색+계산): {len(agent.tools)}개 도구")
        
        tools_info = agent.get_available_tools()
        for info in tools_info:
            print(f"  - {info['name']}")
        
    except ValueError as e:
        print(f"⚠️  환경변수 없음: {e}")


def test_react_agent_with_custom_tools():
    """테스트 7: ReactAgent - 커스텀 도구"""
    print("\n" + "="*70)
    print("✅ 테스트 7: ReactAgent - 커스텀 도구")
    print("="*70)
    
    try:
        from backend.ai.tools import calculator, web_search
        
        # 특정 도구만 사용
        agent = ReactAgent(tools=[calculator, web_search])
        print(f"✓ ReactAgent 초기화 (커스텀): {len(agent.tools)}개 도구")
        
        tools_info = agent.get_available_tools()
        for info in tools_info:
            print(f"  - {info['name']}")
        
    except ValueError as e:
        print(f"⚠️  환경변수 없음: {e}")


def test_tool_manager_summary():
    """테스트 8: ToolManager 요약 출력"""
    print("\n" + "="*70)
    print("✅ 테스트 8: ToolManager 요약")
    print("="*70)
    
    manager = ToolManager()
    manager.print_tools_summary()


def main():
    """모든 테스트 실행"""
    print("\n")
    print("█" * 70)
    print("🧪 AI 도구 및 에이전트 통합 테스트 시작")
    print("█" * 70)
    
    try:
        # 기본 테스트
        test_tool_manager_basic()
        test_tool_manager_selection()
        test_tool_info()
        test_tool_validation()
        
        # 에이전트 테스트
        test_react_agent_with_all_tools()
        test_react_agent_with_categories()
        test_react_agent_with_custom_tools()
        
        # 요약
        test_tool_manager_summary()
        
        print("\n" + "█" * 70)
        print("✅ 모든 테스트 완료!")
        print("█" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
