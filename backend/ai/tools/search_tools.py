"""
검색 도구 (Search Tools)
웹 검색 및 정보 수집
"""

from langchain_core.tools import tool
from loguru import logger
import os
import httpx
from pydantic import Field


# ============================================================================
# 웹 검색 도구
# ============================================================================

@tool
def web_search(
    query: str = Field(..., description="검색 쿼리 (예: '파이썬 최신 버전')"),
    max_results: int = Field(default=5, description="최대 결과 수 (기본값: 5, 최대 10)")
) -> str:
    """
    인터넷에서 정보를 검색하고 상위 결과를 반환합니다.
    
    이 도구는 Tavily Search API를 사용하여 웹 검색을 수행합니다.
    검색 결과는 제목, URL, 내용요약을 포함합니다.
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
# 검색 도구 목록
# ============================================================================

SEARCH_TOOLS = [web_search]

__all__ = ["web_search", "SEARCH_TOOLS"]
