"""
데이터 도구 (Data Tools)
JSON, 텍스트 등 데이터 처리 및 변환
"""

from langchain_core.tools import tool
from loguru import logger
from pydantic import Field
import json
from typing import Optional


# ============================================================================
# JSON 파싱 도구
# ============================================================================

@tool
def json_parser(
    json_string: str = Field(..., description="파싱할 JSON 문자열"),
    pretty: bool = Field(default=True, description="보기 좋게 포맷팅할지 여부")
) -> str:
    """
    JSON 문자열을 파싱하고 검증합니다.
    
    유효한 JSON 형식인지 확인하고, 원하면 보기 좋게 포맷팅합니다.
    """
    try:
        data = json.loads(json_string)
        if pretty:
            result = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            result = json.dumps(data, ensure_ascii=False)
        logger.info(f"✅ JSON 파싱 성공")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 파싱 오류: {str(e)}")
        return f"JSON 파싱 오류: {str(e)}"


# ============================================================================
# 텍스트 요약 도구
# ============================================================================

@tool
def text_summarizer(
    text: str = Field(..., description="요약할 텍스트"),
    max_sentences: int = Field(default=3, description="최대 요약 문장 수")
) -> str:
    """
    긴 텍스트를 핵심만 추출하여 요약합니다.
    
    문장 단위로 분할하고 중요한 문장을 선택합니다.
    (주의: 간단한 휴리스틱 기반 - 정교한 요약은 LLM 사용 권장)
    """
    try:
        # 간단한 문장 분할
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) <= max_sentences:
            logger.info(f"📝 텍스트가 이미 간결함 ({len(sentences)}개 문장)")
            return text
        
        # 문장 길이 기반 상위 N개 선택
        sorted_sentences = sorted(sentences, key=len, reverse=True)[:max_sentences]
        summary = '. '.join(sorted_sentences) + '.'
        
        logger.info(f"✅ 요약 완료: {len(sentences)}개 → {len(sorted_sentences)}개 문장")
        return summary
    except Exception as e:
        logger.error(f"❌ 요약 오류: {str(e)}")
        return f"요약 오류: {str(e)}"


# ============================================================================
# 문자열 조작 도구
# ============================================================================

@tool
def string_manipulator(
    text: str = Field(..., description="처리할 문자열"),
    operation: str = Field(
        default="uppercase",
        description="연산 종류: uppercase, lowercase, reverse, count_words, count_chars"
    )
) -> str:
    """
    문자열에 다양한 연산을 수행합니다.
    
    지원하는 연산:
    - uppercase: 대문자 변환
    - lowercase: 소문자 변환
    - reverse: 문자열 역순
    - count_words: 단어 개수 세기
    - count_chars: 문자 개수 세기
    """
    try:
        if operation == "uppercase":
            result = text.upper()
            logger.info(f"✅ 대문자 변환 완료")
        elif operation == "lowercase":
            result = text.lower()
            logger.info(f"✅ 소문자 변환 완료")
        elif operation == "reverse":
            result = text[::-1]
            logger.info(f"✅ 문자열 역순 완료")
        elif operation == "count_words":
            count = len(text.split())
            result = f"단어 개수: {count}"
            logger.info(f"✅ 단어 개수: {count}")
        elif operation == "count_chars":
            count = len(text)
            result = f"문자 개수: {count}"
            logger.info(f"✅ 문자 개수: {count}")
        else:
            result = f"❌ 지원하지 않는 연산: {operation}"
        
        return result
    except Exception as e:
        logger.error(f"❌ 문자열 처리 오류: {str(e)}")
        return f"오류: {str(e)}"


# ============================================================================
# 데이터 도구 목록
# ============================================================================

DATA_TOOLS = [
    json_parser,
    text_summarizer,
    string_manipulator,
]

__all__ = [
    "json_parser",
    "text_summarizer",
    "string_manipulator",
    "DATA_TOOLS",
]
