"""
LCEL Chains API Routes
다양한 LLM 체인들을 테스트할 수 있는 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from loguru import logger

from backend.ai.chains.lcel_chain import get_chain, CHAIN_REGISTRY

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class SimpleQARequest(BaseModel):
    """간단한 질문 요청"""
    question: str = Field(..., description="사용자의 질문")


class TextProcessingRequest(BaseModel):
    """텍스트 처리 요청"""
    text: str = Field(..., description="처리할 텍스트")


class ContextQARequest(BaseModel):
    """컨텍스트 기반 QA 요청"""
    context: str = Field(..., description="컨텍스트 정보")
    question: str = Field(..., description="질문")


class TranslationRequest(BaseModel):
    """번역 요청"""
    text: str = Field(..., description="번역할 텍스트")
    target_language: str = Field(default="영어", description="목표 언어")


class StyleTransformRequest(BaseModel):
    """스타일 변환 요청"""
    text: str = Field(..., description="원본 텍스트")
    style: str = Field(default="전문적", description="목표 스타일")


class ChainResponse(BaseModel):
    """체인 응답 기본 모델"""
    result: str = Field(..., description="처리 결과")
    chain_type: str = Field(..., description="사용된 체인 타입")


# ============================================================================
# 1. Simple QA Endpoint
# ============================================================================

@router.post("/qa", response_model=ChainResponse)
async def simple_qa(request: SimpleQARequest):
    """
    간단한 질문-답변 엔드포인트
    
    Example:
        {"question": "파이썬이란 무엇인가?"}
    """
    try:
        logger.info(f"QA 요청: {request.question[:50]}...")
        
        chain = get_chain("simple_qa")
        result = chain.invoke({"question": request.question})
        
        return ChainResponse(
            result=result,
            chain_type="simple_qa"
        )
    except Exception as e:
        logger.error(f"QA 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"QA 처리 실패: {str(e)}")


# ============================================================================
# 2. Summarization Endpoint
# ============================================================================

@router.post("/summarize", response_model=ChainResponse)
async def summarize(request: TextProcessingRequest):
    """
    텍스트 요약 엔드포인트
    
    Example:
        {"text": "긴 텍스트를 요약해주세요..."}
    """
    try:
        logger.info(f"요약 요청: {len(request.text)}자")
        
        chain = get_chain("summarize")
        result = chain.invoke({"text": request.text})
        
        return ChainResponse(
            result=result,
            chain_type="summarize"
        )
    except Exception as e:
        logger.error(f"요약 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"요약 처리 실패: {str(e)}")


# ============================================================================
# 3. Sentiment Analysis Endpoint
# ============================================================================

@router.post("/sentiment", response_model=ChainResponse)
async def sentiment_analysis(request: TextProcessingRequest):
    """
    감정 분석 엔드포인트
    
    Example:
        {"text": "이 제품 정말 좋아요!"}
    """
    try:
        logger.info(f"감정 분석 요청: {request.text[:50]}...")
        
        chain = get_chain("sentiment")
        result = chain.invoke({"text": request.text})
        
        return ChainResponse(
            result=result,
            chain_type="sentiment"
        )
    except Exception as e:
        logger.error(f"감정 분석 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"감정 분석 실패: {str(e)}")


# ============================================================================
# 4. Keyword Extraction Endpoint
# ============================================================================

@router.post("/keywords", response_model=ChainResponse)
async def extract_keywords(request: TextProcessingRequest):
    """
    키워드 추출 엔드포인트
    
    Example:
        {"text": "기계 학습은 인공지능의 하위 분야입니다..."}
    """
    try:
        logger.info(f"키워드 추출 요청: {request.text[:50]}...")
        
        chain = get_chain("keywords")
        result = chain.invoke({"text": request.text})
        
        return ChainResponse(
            result=result,
            chain_type="keywords"
        )
    except Exception as e:
        logger.error(f"키워드 추출 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"키워드 추출 실패: {str(e)}")


# ============================================================================
# 5. Question Generation Endpoint
# ============================================================================

@router.post("/generate-questions", response_model=ChainResponse)
async def generate_questions(request: TextProcessingRequest):
    """
    질문 생성 엔드포인트
    
    Example:
        {"text": "파이썬은 고급 프로그래밍 언어입니다..."}
    """
    try:
        logger.info(f"질문 생성 요청: {request.text[:50]}...")
        
        chain = get_chain("questions")
        result = chain.invoke({"text": request.text})
        
        return ChainResponse(
            result=result,
            chain_type="questions"
        )
    except Exception as e:
        logger.error(f"질문 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"질문 생성 실패: {str(e)}")


# ============================================================================
# 6. Context-Aware QA Endpoint
# ============================================================================

@router.post("/context-qa", response_model=ChainResponse)
async def context_qa(request: ContextQARequest):
    """
    컨텍스트 기반 QA 엔드포인트
    주어진 컨텍스트를 기반으로 질문에 답변합니다
    
    Example:
        {
            "context": "파이썬은 1991년에 만들어진 프로그래밍 언어입니다.",
            "question": "파이썬이 만들어진 연도는?"
        }
    """
    try:
        logger.info(f"컨텍스트 QA 요청: {request.question}")
        
        chain = get_chain("context_qa")
        result = chain.invoke({
            "context": request.context,
            "question": request.question
        })
        
        return ChainResponse(
            result=result,
            chain_type="context_qa"
        )
    except Exception as e:
        logger.error(f"컨텍스트 QA 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"컨텍스트 QA 실패: {str(e)}")


# ============================================================================
# 7. Sentiment Analysis Endpoint
# ============================================================================

@router.post("/verify", response_model=ChainResponse)
async def verify_statement(request: TextProcessingRequest):
    """
    사실성 검증 엔드포인트
    
    Example:
        {"text": "지구는 태양 주위를 공전합니다."}
    """
    try:
        logger.info(f"검증 요청: {request.text[:50]}...")
        
        chain = get_chain("verify")
        result = chain.invoke({"statement": request.text})
        
        return ChainResponse(
            result=result,
            chain_type="verify"
        )
    except Exception as e:
        logger.error(f"검증 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"검증 실패: {str(e)}")


# ============================================================================
# 8. Parallel Analysis Endpoint
# ============================================================================

class ParallelAnalysisResponse(BaseModel):
    """병렬 분석 응답"""
    summary: str
    sentiment: str
    keywords: str
    chain_type: str = "parallel"


@router.post("/analyze", response_model=ParallelAnalysisResponse)
async def parallel_analysis(request: TextProcessingRequest):
    """
    병렬 분석 엔드포인트
    요약, 감정 분석, 키워드 추출을 동시에 수행합니다
    
    Example:
        {"text": "분석할 텍스트..."}
    """
    try:
        logger.info(f"병렬 분석 요청: {len(request.text)}자")
        
        chain = get_chain("parallel")
        result = chain.invoke({"text": request.text})
        
        return ParallelAnalysisResponse(
            summary=result.get("summary", ""),
            sentiment=result.get("sentiment", ""),
            keywords=result.get("keywords", ""),
            chain_type="parallel"
        )
    except Exception as e:
        logger.error(f"병렬 분석 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"병렬 분석 실패: {str(e)}")


# ============================================================================
# 9. Available Chains List Endpoint
# ============================================================================

@router.get("/chains")
async def list_chains():
    """
    사용 가능한 모든 체인 목록 반환
    """
    return {
        "available_chains": list(CHAIN_REGISTRY.keys()),
        "count": len(CHAIN_REGISTRY),
        "description": {
            "simple_qa": "기본 질문-답변",
            "summarize": "텍스트 요약",
            "translate": "텍스트 번역",
            "sentiment": "감정 분석",
            "keywords": "키워드 추출",
            "questions": "질문 생성",
            "style_transform": "스타일 변환",
            "multi_step": "다중 단계 처리",
            "parallel": "병렬 분석",
            "context_qa": "컨텍스트 기반 QA",
            "verify": "사실성 검증"
        }
    }


# ============================================================================
# 10. Health Check Endpoint
# ============================================================================

@router.get("/health")
async def health_check():
    """
    LCEL 서비스 헬스 체크
    """
    return {
        "status": "ok",
        "service": "LCEL Chains",
        "available_chains": len(CHAIN_REGISTRY)
    }
