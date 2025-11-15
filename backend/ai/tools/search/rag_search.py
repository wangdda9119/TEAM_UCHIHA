# backend/ai/tools/search/rag_search.py

from typing import Optional

from langchain_core.tools import tool
from loguru import logger

from backend.ai.vector.rag_pipeline import RAGPipeline

# 전역 RAGPipeline 인스턴스 (한 번만 생성)
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """전역 RAGPipeline 싱글톤 생성/반환."""
    global _rag_pipeline
    if _rag_pipeline is None:
        logger.info("[rag_search] 최초 RAGPipeline 생성")
        _rag_pipeline = RAGPipeline()
    else:
        logger.info("[rag_search] 기존 RAGPipeline 재사용")
    return _rag_pipeline


@tool
def rag_search(query: str) -> str:
    """협성대학교 문서 기반 RAG 검색 Tool"""
    logger.info(f"[rag_search] 호출됨 / query={query!r}")

    try:
        rag = get_rag_pipeline()
        answer = rag.answer(query)  # <-- 여기서 RAGPipeline.answer를 반드시 호출
        logger.info(f"[rag_search] RAG answer 앞 200자:\n{answer[:200]}")
        return answer
    except Exception as e:
        logger.exception("[rag_search] RAG 검색 중 예외 발생")
        return f"RAG 검색 오류: {e}"
