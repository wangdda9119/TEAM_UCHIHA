"""
AI 에이전트용 도구 (Tools)
@tool 데코레이터를 사용한 간단한 도구 정의
"""

from langchain_core.tools import tool
from loguru import logger
import os
import httpx
from typing import Optional


# ============================================================================
# 웹 검색 도구
# ============================================================================

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    인터넷에서 정보를 검색합니다.
    
    Args:
        query: 검색 쿼리 (예: "파이썬 최신 버전")
        max_results: 최대 결과 수 (기본값: 5, 최대 10)
    
    Returns:
        검색 결과 문자열
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "❌ TAVILY_API_KEY가 설정되지 않았습니다."
    
    try:
        logger.info(f"🔍 웹 검색: {query}")
        
        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": min(max_results, 10),
            "include_images": False,
            "search_depth": "basic"
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://api.tavily.com/search",
                json=payload
            )
            response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return "검색 결과가 없습니다."
        
        # 결과 포맷
        formatted = f"'{query}' 검색 결과 ({len(results)}개):\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', 'N/A')}\n"
            formatted += f"   URL: {result.get('url', 'N/A')}\n"
            formatted += f"   내용: {result.get('content', 'N/A')[:150]}...\n\n"
        
        logger.info(f"✅ 검색 완료: {len(results)}개 결과")
        return formatted.strip()
    
    except Exception as e:
        logger.error(f"❌ 웹 검색 오류: {str(e)}")
        return f"검색 오류: {str(e)}"


# ============================================================================
# 계산기 도구
# ============================================================================

@tool
def calculator(expression: str) -> str:
    """
    수학 연산을 수행합니다.
    
    Args:
        expression: 계산식 (예: "2 + 3 * 4", "100 ** 2")
    
    Returns:
        계산 결과
    """
    try:
        logger.info(f"🧮 계산: {expression}")
        
        # 안전한 평가: 수학 함수만 허용
        allowed_names = {
            '__builtins__': {},
            'abs': abs,
            'round': round,
            'max': max,
            'min': min,
            'sum': sum,
            'pow': pow,
        }
        
        result = eval(expression, allowed_names)
        logger.info(f"✅ 계산 결과: {result}")
        return str(result)
    
    except ZeroDivisionError:
        return "❌ 오류: 0으로 나눌 수 없습니다."
    except SyntaxError:
        return f"❌ 문법 오류: '{expression}'는 올바른 수식이 아닙니다."
    except Exception as e:
        return f"❌ 계산 오류: {str(e)}"


# ============================================================================
# 도구 목록 (AgentExecutor에 전달용)
# ============================================================================

TOOLS = [web_search, calculator]

__all__ = ["web_search", "calculator", "TOOLS"]
