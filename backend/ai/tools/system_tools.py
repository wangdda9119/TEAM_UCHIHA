"""
시스템 도구 (System Tools)
시간, 시스템 정보, 메타 기능
"""

from langchain_core.tools import tool
from loguru import logger
from pydantic import Field
from datetime import datetime


# ============================================================================
# 현재 시간 조회 도구
# ============================================================================

@tool
def get_current_time(
    format: str = Field(default="full", description="시간 포맷: full, date, time")
) -> str:
    """
    현재 시간 정보를 조회합니다.
    
    포맷 옵션:
    - full: 날짜와 시간 모두
    - date: 날짜만
    - time: 시간만
    """
    try:
        now = datetime.now()
        
        if format == "date":
            result = now.strftime("%Y-%m-%d")
        elif format == "time":
            result = now.strftime("%H:%M:%S")
        else:  # full
            result = now.strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"⏰ 현재 시간: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ 시간 조회 오류: {str(e)}")
        return f"오류: {str(e)}"


# ============================================================================
# 도구 목록 조회 도구 (메타 도구)
# ============================================================================

@tool
def list_operations(
    action: str = Field(
        default="help",
        description="연산 종류: help, all"
    )
) -> str:
    """
    사용 가능한 모든 도구와 기능을 나열합니다.
    
    - help: 기본 도구 목록
    - all: 전체 도구와 설명
    """
    if action == "help":
        return """
📚 사용 가능한 도구:

[검색]
• web_search - 웹 검색

[계산]
• calculator - 수학 연산

[데이터]
• json_parser - JSON 파싱
• text_summarizer - 텍스트 요약
• string_manipulator - 문자열 처리

[시스템]
• get_current_time - 현재 시간
• list_operations - 도구 목록 조회
        """
    elif action == "all":
        return """
📚 전체 도구 목록:

[검색 도구]
• web_search(query, max_results) - 인터넷 검색

[계산 도구]
• calculator(expression) - 수학 연산

[데이터 도구]
• json_parser(json_string, pretty) - JSON 파싱/검증
• text_summarizer(text, max_sentences) - 텍스트 요약
• string_manipulator(text, operation) - 문자열 처리

[시스템 도구]
• get_current_time(format) - 현재 시간 조회 (full/date/time)
• list_operations(action) - 도구 목록 조회 (help/all)

[계산 도구]
• calculator(expression) - 수학 연산
        """
    else:
        return "❓ 알 수 없는 연산입니다. help 또는 all을 사용하세요."


# ============================================================================
# 시스템 도구 목록
# ============================================================================

SYSTEM_TOOLS = [
    get_current_time,
    list_operations,
]

__all__ = [
    "get_current_time",
    "list_operations",
    "SYSTEM_TOOLS",
]
