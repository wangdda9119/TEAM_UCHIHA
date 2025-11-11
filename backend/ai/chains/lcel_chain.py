
"""
LCEL (LangChain Expression Language) Chains
모듈화된 다양한 LLM 체인들을 정의합니다.
"""

import os
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from loguru import logger


# ============================================================================
# 1. 기본 OpenAI LLM 셋업
# ============================================================================

def get_llm(temperature: float = 0.7, model: str = "gpt-3.5-turbo"):
    """
    OpenAI ChatGPT 모델 초기화
    
    Args:
        temperature: 응답 창의성 (0.0~2.0, 기본값: 0.7)
        model: 사용할 모델 (gpt-3.5-turbo, gpt-4 등)
    
    Returns:
        ChatOpenAI 인스턴스
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다")
    
    logger.info(f"✅ LLM 초기화: {model} (temperature={temperature})")
    return ChatOpenAI(
        api_key=api_key,
        model=model,
        temperature=temperature
    )


# ============================================================================
# 2. 단순 질문-답변 체인
# ============================================================================

def get_simple_qa_chain():
    """
    기본 질문-답변 체인
    단순히 사용자 질문에 답변하는 가장 기본적인 형태
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 친절한 어시스턴트입니다. 사용자의 질문에 자세하고 정확하게 답변해주세요."),
        ("user", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info("✅ Simple QA Chain 생성됨")
    return chain


# ============================================================================
# 3. 요약 체인
# ============================================================================

def get_summarization_chain():
    """
    텍스트 요약 체인
    긴 텍스트를 짧게 요약합니다
    """
    llm = get_llm(temperature=0.3)  # 낮은 temperature로 일관성 있는 요약
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 텍스트를 핵심 내용만 추려 간결하게 요약해주세요. 3~5 문장으로 정리하세요."),
        ("user", "텍스트:\n{text}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info("✅ Summarization Chain 생성됨")
    return chain


# ============================================================================
# 4. 번역 체인
# ============================================================================

def get_translation_chain(target_language: str = "영어"):
    """
    번역 체인
    다양한 언어로 번역합니다
    
    Args:
        target_language: 목표 언어 (기본값: 영어)
    """
    llm = get_llm(temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"당신은 전문 번역가입니다. 주어진 텍스트를 {target_language}로 정확하게 번역해주세요."),
        ("user", "번역할 텍스트:\n{text}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info(f"✅ Translation Chain 생성됨 (목표 언어: {target_language})")
    return chain


# ============================================================================
# 5. 감정 분석 체인
# ============================================================================

def get_sentiment_analysis_chain():
    """
    감정 분석 체인
    텍스트의 감정을 분석합니다 (긍정/부정/중립)
    """
    llm = get_llm(temperature=0.0)  # 확정적인 답변을 위해 temperature=0
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """텍스트의 감정을 분석하고 다음 형식으로 응답하세요:
        감정: [긍정/부정/중립]
        신뢰도: [0.0~1.0]
        설명: [이유 설명]"""),
        ("user", "텍스트: {text}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info("✅ Sentiment Analysis Chain 생성됨")
    return chain


# ============================================================================
# 6. 키워드 추출 체인
# ============================================================================

def get_keyword_extraction_chain(num_keywords: int = 5):
    """
    키워드 추출 체인
    텍스트에서 중요한 키워드를 추출합니다
    
    Args:
        num_keywords: 추출할 키워드 개수
    """
    llm = get_llm(temperature=0.0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""주어진 텍스트에서 가장 중요한 {num_keywords}개의 키워드를 추출하세요.
        응답 형식: 키워드를 쉼표로 구분하여 나열하세요 (예: 키워드1, 키워드2, 키워드3)"""),
        ("user", "텍스트: {text}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info(f"✅ Keyword Extraction Chain 생성됨 (개수: {num_keywords})")
    return chain


# ============================================================================
# 7. 질문 생성 체인
# ============================================================================

def get_question_generation_chain(num_questions: int = 3):
    """
    질문 생성 체인
    주어진 텍스트를 기반으로 질문들을 생성합니다
    
    Args:
        num_questions: 생성할 질문 개수
    """
    llm = get_llm(temperature=0.8)  # 창의적인 질문을 위해 높은 temperature
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""주어진 텍스트를 기반으로 {num_questions}개의 좋은 질문을 생성하세요.
        각 질문은 번호를 매겨서 나열하세요.
        질문은 텍스트의 핵심을 이해하는 데 도움이 되어야 합니다."""),
        ("user", "텍스트: {text}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info(f"✅ Question Generation Chain 생성됨 (개수: {num_questions})")
    return chain


# ============================================================================
# 8. 스타일 변환 체인
# ============================================================================

def get_style_transform_chain(style: str = "전문적"):
    """
    스타일 변환 체인
    텍스트를 다른 스타일로 변환합니다
    
    Args:
        style: 목표 스타일 (전문적, 캐주얼, 시적, 학술적 등)
    """
    llm = get_llm(temperature=0.6)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"주어진 텍스트를 '{style}' 스타일로 다시 작성해주세요. 의미는 유지하되 톤과 표현 방식을 변경하세요."),
        ("user", "원본 텍스트: {text}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info(f"✅ Style Transform Chain 생성됨 (스타일: {style})")
    return chain


# ============================================================================
# 9. 다중 단계 처리 체인 (Chaining)
# ============================================================================

def get_multi_step_chain():
    """
    다중 단계 체인
    텍스트를 요약한 후, 요약본을 번역합니다
    """
    llm = get_llm()
    
    # Step 1: 요약
    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 텍스트를 핵심만 추려 요약해주세요."),
        ("user", "{text}")
    ])
    
    # Step 2: 번역
    translate_prompt = ChatPromptTemplate.from_messages([
        ("system", "다음을 영어로 번역해주세요."),
        ("user", "{summary}")
    ])
    
    # 체인 연결
    summarize_chain = summarize_prompt | llm | StrOutputParser()
    translate_chain = translate_prompt | llm | StrOutputParser()
    
    # 전체 체인: 입력 → 요약 → 번역
    full_chain = {
        "text": RunnablePassthrough()
    } | {
        "summary": summarize_chain,
        "text": RunnablePassthrough()
    } | RunnableLambda(lambda x: x["summary"]) | translate_chain
    
    logger.info("✅ Multi-Step Chain 생성됨 (요약 → 번역)")
    return full_chain


# ============================================================================
# 10. 병렬 처리 체인 (Parallel Processing)
# ============================================================================

def get_parallel_analysis_chain():
    """
    병렬 처리 체인
    동시에 요약, 감정 분석, 키워드 추출을 수행합니다
    """
    llm = get_llm()
    
    # 각 분석 작업
    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", "텍스트를 요약하세요."),
        ("user", "{text}")
    ])
    
    sentiment_prompt = ChatPromptTemplate.from_messages([
        ("system", "텍스트의 감정을 분석하세요. (긍정/부정/중립)"),
        ("user", "{text}")
    ])
    
    keyword_prompt = ChatPromptTemplate.from_messages([
        ("system", "주요 키워드 5개를 추출하세요."),
        ("user", "{text}")
    ])
    
    # 병렬 실행
    chain = RunnableParallel(
        summary=summarize_prompt | llm | StrOutputParser(),
        sentiment=sentiment_prompt | llm | StrOutputParser(),
        keywords=keyword_prompt | llm | StrOutputParser()
    )
    
    logger.info("✅ Parallel Analysis Chain 생성됨")
    return chain


# ============================================================================
# 11. 컨텍스트 기반 QA 체인
# ============================================================================

def get_context_aware_qa_chain():
    """
    컨텍스트 기반 질문-답변 체인
    주어진 컨텍스트를 기반으로 질문에 답변합니다
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 컨텍스트를 기반으로 사용자의 질문에 답변하세요. 컨텍스트에 없는 정보는 '정보 없음'이라고 답하세요."),
        ("user", """컨텍스트:
{context}

질문: {question}""")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info("✅ Context-Aware QA Chain 생성됨")
    return chain


# ============================================================================
# 12. 검증 체인 (Verification)
# ============================================================================

def get_verification_chain():
    """
    검증 체인
    주어진 문장이 사실인지 확인합니다
    """
    llm = get_llm(temperature=0.0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """다음 문장의 사실성을 평가하세요.
        응답 형식:
        평가: [사실/거짓/불확실]
        신뢰도: [0.0~1.0]
        설명: [이유]"""),
        ("user", "문장: {statement}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    logger.info("✅ Verification Chain 생성됨")
    return chain


# ============================================================================
# 13. 팩토리 함수 (사용자 선택)
# ============================================================================

CHAIN_REGISTRY = {
    "simple_qa": get_simple_qa_chain,
    "summarize": get_summarization_chain,
    "translate": lambda: get_translation_chain("영어"),
    "sentiment": get_sentiment_analysis_chain,
    "keywords": lambda: get_keyword_extraction_chain(5),
    "questions": lambda: get_question_generation_chain(3),
    "style_transform": lambda: get_style_transform_chain("전문적"),
    "multi_step": get_multi_step_chain,
    "parallel": get_parallel_analysis_chain,
    "context_qa": get_context_aware_qa_chain,
    "verify": get_verification_chain,
}


def get_chain(chain_type: str = "simple_qa"):
    """
    체인 팩토리 함수
    등록된 체인 중 하나를 선택해서 가져옵니다
    
    Args:
        chain_type: 체인 타입 (registry 키)
    
    Returns:
        LCEL 체인 인스턴스
    
    Example:
        >>> chain = get_chain("sentiment")
        >>> result = chain.invoke({"text": "이 제품 정말 좋아요!"})
    """
    if chain_type not in CHAIN_REGISTRY:
        raise ValueError(f"알 수 없는 체인 타입: {chain_type}. 사용 가능한 타입: {list(CHAIN_REGISTRY.keys())}")
    
    logger.info(f"체인 로드: {chain_type}")
    return CHAIN_REGISTRY[chain_type]()


# ============================================================================
# 14. 이전 호환성 (기존 코드 지원)
# ============================================================================

def get_simple_chain():
    """
    기존 코드와의 호환성을 위한 래퍼 함수
    """
    return get_simple_qa_chain()

