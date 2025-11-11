
"""
웹 검색 도구들
- Tavily API를 사용한 고급 웹 검색
- 다양한 검색 옵션 지원
"""

import os
import json
from typing import Optional, List, Dict, Any
import httpx
from loguru import logger


class TavilySearchTool:
    """
    Tavily API를 사용한 웹 검색 도구
    고급 검색 기능과 결과 필터링 제공
    """
    
    def __init__(self):
        """Tavily API 초기화"""
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "❌ TAVILY_API_KEY가 설정되지 않았습니다. "
                ".env 파일을 확인하세요."
            )
        
        self.base_url = "https://api.tavily.com/search"
        self.timeout = httpx.Timeout(30.0)
        logger.info("✅ TavilySearchTool 초기화됨")
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        include_images: bool = False,
        search_depth: str = "basic"
    ) -> List[Dict[str, Any]]:
        """
        Tavily API를 사용한 웹 검색
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수 (기본값: 5)
            include_images: 이미지 포함 여부 (기본값: False)
            search_depth: 검색 깊이 ('basic' 또는 'advanced')
        
        Returns:
            검색 결과 리스트
        """
        try:
            if not query or len(query.strip()) == 0:
                raise ValueError("검색 쿼리가 비어있습니다")
            
            logger.info(f"🔍 Tavily 검색: {query}")
            
            # API 요청 페이로드
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": min(max_results, 10),  # 최대 10개
                "include_images": include_images,
                "search_depth": search_depth
            }
            
            # API 호출
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.base_url, json=payload)
                response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            logger.info(f"✅ 검색 완료: {len(results)}개 결과")
            
            # 결과 정제
            processed_results = []
            for result in results:
                processed_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date")
                })
            
            return processed_results
        
        except httpx.HTTPError as e:
            logger.error(f"❌ Tavily API 오류: {str(e)}")
            raise Exception(f"웹 검색 실패: {str(e)}")
        except Exception as e:
            logger.error(f"❌ 검색 오류: {str(e)}")
            raise
    
    def search_simple(self, query: str) -> str:
        """
        간단한 웹 검색 (문자열 반환)
        AI 에이전트용
        
        Args:
            query: 검색 쿼리
        
        Returns:
            포맷된 검색 결과 문자열
        """
        results = self.search(query, max_results=3)
        
        if not results:
            return "검색 결과가 없습니다."
        
        # 결과를 문자열로 포맷
        formatted = f"'{query}' 검색 결과:\n"
        for i, result in enumerate(results, 1):
            formatted += f"\n{i}. {result['title']}\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   내용: {result['content'][:200]}...\n"
        
        return formatted
    
    def search_with_context(
        self,
        query: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        컨텍스트를 포함한 검색
        
        Args:
            query: 검색 쿼리
            context: 추가 컨텍스트 정보
        
        Returns:
            결과와 메타데이터를 포함한 딕셔너리
        """
        results = self.search(query, max_results=5)
        
        return {
            "query": query,
            "context": context,
            "results": results,
            "total_results": len(results),
            "status": "success" if results else "no_results"
        }


# ============================================================================
# 싱글톤 인스턴스
# ============================================================================

_tavily_instance = None

def get_tavily_tool() -> TavilySearchTool:
    """Tavily 도구 싱글톤 인스턴스 반환"""
    global _tavily_instance
    if _tavily_instance is None:
        _tavily_instance = TavilySearchTool()
    return _tavily_instance


# ============================================================================
# 편의 함수
# ============================================================================

def web_search(query: str) -> str:
    """
    간단한 웹 검색 함수
    
    Args:
        query: 검색 쿼리
    
    Returns:
        포맷된 검색 결과
    """
    tool = get_tavily_tool()
    return tool.search_simple(query)
