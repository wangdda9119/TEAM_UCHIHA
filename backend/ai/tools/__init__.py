"""
AI Tools 패키지
기능별로 분리된 도구들의 통합 포인트

구조:
- search_tools.py: 웹 검색
- data_tools.py: JSON, 텍스트 처리
- system_tools.py: 시간, 시스템 정보
- math_tools.py: 계산, 수학 연산
- manager.py: 도구 통합 관리자 (ToolManager)

사용 방법:
1. 기존 방식 (ALL_TOOLS 사용):
   from backend.ai.tools import ALL_TOOLS
   agent = ReactAgent(tools=ALL_TOOLS)

2. 새 방식 (ToolManager 사용):
   from backend.ai.tools import get_tool_manager
   manager = get_tool_manager()
   tools = manager.get_all_tools()
   agent = ReactAgent(tools=tools)

3. 선택적 도구:
   search_tools = manager.get_tools_by_category("search")
   agent = ReactAgent(tools=search_tools)
"""

# 기능별 도구 임포트
from .search_tools import SEARCH_TOOLS, web_search
from .data_tools import DATA_TOOLS, json_parser, text_summarizer, string_manipulator
from .system_tools import SYSTEM_TOOLS, get_current_time, list_operations
from .math_tools import MATH_TOOLS, calculator

# 도구 매니저 임포트
from .manager import ToolManager, get_tool_manager

# 모든 도구 통합 (에이전트가 사용할 도구)
ALL_TOOLS = SEARCH_TOOLS + DATA_TOOLS + SYSTEM_TOOLS + MATH_TOOLS

__all__ = [
    # 기능별 도구 세트
    "SEARCH_TOOLS",
    "DATA_TOOLS",
    "SYSTEM_TOOLS",
    "MATH_TOOLS",
    
    # 개별 도구 (필요시 직접 임포트)
    "web_search",
    "json_parser",
    "text_summarizer",
    "string_manipulator",
    "get_current_time",
    "list_operations",
    "calculator",
    
    # 통합 도구 (에이전트용)
    "ALL_TOOLS",
    
    # 도구 매니저 (권장)
    "ToolManager",
    "get_tool_manager",
]

