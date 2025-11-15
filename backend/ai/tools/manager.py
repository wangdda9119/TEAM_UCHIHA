"""
도구 매니저 (Tool Manager)
모든 AI 도구를 중앙에서 관리하고 에이전트에 제공하는 통합 모듈

역할:
- 도구의 동적 로딩 및 검증
- 도구 메타데이터 관리
- 도구 그룹별 선택적 제공
- 에이전트 통합
"""

from typing import Dict, List, Optional, Union, Callable
from langchain_core.tools import BaseTool
from loguru import logger
import inspect

# 도구 임포트
from .search_tools import SEARCH_TOOLS, web_search
from .data_tools import DATA_TOOLS, json_parser, text_summarizer, string_manipulator
from .system_tools import SYSTEM_TOOLS, get_current_time, list_operations
from .math_tools import MATH_TOOLS, calculator


class ToolManager:
    """
    AI 에이전트용 도구 관리자
    
    기능:
    1. 도구 그룹 관리 (검색, 데이터, 시스템, 계산)
    2. 선택적 도구 세트 제공
    3. 도구 메타데이터 조회
    4. 에이전트에 최적화된 형식으로 변환
    
    사용 예:
        manager = ToolManager()
        
        # 모든 도구 가져오기
        all_tools = manager.get_all_tools()
        
        # 특정 카테고리만
        search_tools = manager.get_tools_by_category("search")
        
        # 도구 정보 조회
        info = manager.get_tool_info("web_search")
        
        # 에이전트용 포맷
        for tool_info in manager.list_tools_with_info():
            print(tool_info)
    """
    
    def __init__(self):
        """도구 매니저 초기화"""
        # 도구 그룹 정의
        self._tool_groups: Dict[str, List[Union[BaseTool, Callable]]] = {
            "search": SEARCH_TOOLS,
            "data": DATA_TOOLS,
            "system": SYSTEM_TOOLS,
            "math": MATH_TOOLS,
        }
        
        # 전체 도구 맵 (이름 -> 도구)
        self._tool_map: Dict[str, Union[BaseTool, Callable]] = {}
        self._build_tool_map()
        
        logger.info(f"✅ ToolManager 초기화 완료: {len(self._tool_map)}개 도구")
    
    def _build_tool_map(self) -> None:
        """도구 맵 구성"""
        for group_name, tools in self._tool_groups.items():
            for tool in tools:
                tool_name = self._get_tool_name(tool)
                self._tool_map[tool_name] = tool
                logger.debug(f"  📌 {group_name}: {tool_name}")
    
    def _get_tool_name(self, tool: Union[BaseTool, Callable]) -> str:
        """도구에서 이름 추출"""
        if hasattr(tool, "name"):
            return tool.name
        elif hasattr(tool, "__name__"):
            return tool.__name__
        else:
            return str(tool)
    
    def get_all_tools(self) -> List[Union[BaseTool, Callable]]:
        """
        모든 도구 반환
        
        Returns:
            도구 리스트
        """
        all_tools = []
        for tools in self._tool_groups.values():
            all_tools.extend(tools)
        logger.info(f"📦 모든 도구 반환: {len(all_tools)}개")
        return all_tools
    
    def get_tools_by_category(self, category: str) -> List[Union[BaseTool, Callable]]:
        """
        특정 카테고리의 도구만 반환
        
        Args:
            category: 카테고리명 (search, data, system, math)
        
        Returns:
            해당 카테고리의 도구 리스트
        
        Raises:
            ValueError: 존재하지 않는 카테고리
        """
        if category not in self._tool_groups:
            available = list(self._tool_groups.keys())
            raise ValueError(f"카테고리 '{category}' 없음. 사용 가능: {available}")
        
        tools = self._tool_groups[category]
        logger.info(f"🎯 {category} 도구 반환: {len(tools)}개")
        return tools
    
    def get_tools_by_categories(self, categories: List[str]) -> List[Union[BaseTool, Callable]]:
        """
        여러 카테고리의 도구를 반환
        
        Args:
            categories: 카테고리 리스트
        
        Returns:
            선택된 카테고리들의 도구 리스트
        """
        selected_tools = []
        for category in categories:
            selected_tools.extend(self.get_tools_by_category(category))
        logger.info(f"🎯 선택 도구 반환: {len(selected_tools)}개 ({', '.join(categories)})")
        return selected_tools
    
    def get_tool_by_name(self, name: str) -> Optional[Union[BaseTool, Callable]]:
        """
        이름으로 특정 도구 검색
        
        Args:
            name: 도구 이름
        
        Returns:
            도구 객체 또는 None
        """
        return self._tool_map.get(name)
    
    def get_tool_info(self, tool_name: str) -> Dict:
        """
        도구의 메타데이터 조회
        
        Args:
            tool_name: 도구 이름
        
        Returns:
            도구 정보 딕셔너리
            {
                "name": str,
                "description": str,
                "category": str,
                "params": Dict[str, str]  # 파라미터 설명
            }
        """
        tool = self.get_tool_by_name(tool_name)
        if not tool:
            return {"error": f"도구 '{tool_name}' 없음"}
        
        # 카테고리 찾기
        category = "unknown"
        for cat, tools in self._tool_groups.items():
            if tool in tools:
                category = cat
                break
        
        info = {
            "name": tool_name,
            "description": tool.description if hasattr(tool, "description") else "설명 없음",
            "category": category,
            "params": {}
        }
        
        # 파라미터 정보 추출
        if hasattr(tool, "args_schema") and tool.args_schema:
            try:
                schema = tool.args_schema
                if hasattr(schema, "model_fields"):
                    # Pydantic v2
                    for field_name, field_info in schema.model_fields.items():
                        info["params"][field_name] = field_info.description or "설명 없음"
            except Exception as e:
                logger.warning(f"파라미터 정보 추출 실패: {str(e)}")
        
        return info
    
    def list_tools_with_info(self) -> List[Dict]:
        """
        모든 도구의 정보를 반환
        
        Returns:
            도구 정보 리스트
        """
        tools_info = []
        for tool_name in sorted(self._tool_map.keys()):
            info = self.get_tool_info(tool_name)
            tools_info.append(info)
        
        logger.info(f"📋 도구 정보 리스트: {len(tools_info)}개")
        return tools_info
    
    def print_tools_summary(self) -> None:
        """도구 요약을 콘솔에 출력"""
        print("\n" + "="*70)
        print("🛠️  AI 도구 매니저 - 모든 도구 요약")
        print("="*70 + "\n")
        
        for category, tools in self._tool_groups.items():
            print(f"\n📂 [{category.upper()}] ({len(tools)}개)")
            print("-" * 70)
            for tool in tools:
                tool_name = self._get_tool_name(tool)
                desc = tool.description if hasattr(tool, "description") else "설명 없음"
                # 첫 줄만 출력
                desc_line = desc.split("\n")[0] if desc else "설명 없음"
                print(f"  • {tool_name}: {desc_line[:50]}...")
        
        print("\n" + "="*70)
        print(f"총 {len(self._tool_map)}개 도구")
        print("="*70 + "\n")
    
    def validate_tools(self) -> Dict[str, bool]:
        """
        모든 도구가 올바르게 로드되었는지 검증
        
        Returns:
            {도구_이름: 검증_결과} 딕셔너리
        """
        validation_results = {}
        
        logger.info("🔍 도구 검증 시작...")
        for tool_name, tool in self._tool_map.items():
            try:
                # 기본 검증
                assert hasattr(tool, "name") or hasattr(tool, "__name__"), "이름 없음"
                assert callable(tool), "호출 불가능"
                
                if hasattr(tool, "invoke"):
                    # BaseTool 검증
                    assert hasattr(tool, "description"), "설명 없음"
                
                validation_results[tool_name] = True
                logger.debug(f"✅ {tool_name}: 검증 통과")
            except AssertionError as e:
                validation_results[tool_name] = False
                logger.warning(f"⚠️  {tool_name}: {str(e)}")
        
        passed = sum(1 for v in validation_results.values() if v)
        total = len(validation_results)
        logger.info(f"🔍 검증 완료: {passed}/{total} 통과")
        
        return validation_results
    
    def get_categories(self) -> List[str]:
        """사용 가능한 도구 카테고리 반환"""
        return list(self._tool_groups.keys())
    
    def get_category_info(self) -> Dict[str, Dict]:
        """카테고리별 도구 개수와 설명 반환"""
        info = {}
        for category, tools in self._tool_groups.items():
            info[category] = {
                "count": len(tools),
                "tools": [self._get_tool_name(t) for t in tools]
            }
        return info


# 전역 매니저 인스턴스
_tool_manager: Optional[ToolManager] = None


def get_tool_manager() -> ToolManager:
    """
    도구 매니저 싱글톤 인스턴스 반환
    
    Returns:
        ToolManager 인스턴스
    """
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager


__all__ = [
    "ToolManager",
    "get_tool_manager",
]
