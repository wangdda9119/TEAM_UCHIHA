"""
고급 도구 모음
최신 LangChain @tool 데코레이터 사용
- 문서 처리
- 데이터 변환
- 시스템 정보 조회
"""

from langchain_core.tools import tool
from loguru import logger
from pydantic import Field
from datetime import datetime
import json
from typing import Optional, List, Dict, Any


# ============================================================================
# 데이터 도구
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
# 정보 도구
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


@tool
def list_operations(
    action: str = Field(
        default="help",
        description="연산 종류: help, all, search"
    )
) -> str:
    """
    사용 가능한 모든 도구와 기능을 나열합니다.
    
    - help: 기본 도구 목록
    - all: 전체 도구와 설명
    - search: 특정 도구 검색 (구현 필요)
    """
    if action == "help":
        return """
📚 사용 가능한 도구:
1. web_search - 웹 검색
2. calculator - 수학 계산
3. json_parser - JSON 파싱
4. text_summarizer - 텍스트 요약
5. string_manipulator - 문자열 처리
6. get_current_time - 현재 시간
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

[정보 도구]
• get_current_time(format) - 현재 시간 조회
• list_operations(action) - 도구 목록 조회
        """
    else:
        return "❓ 알 수 없는 연산입니다. help 또는 all을 사용하세요."


# ============================================================================
# 전체 도구 목록
# ============================================================================

ADVANCED_TOOLS = [
    json_parser,
    text_summarizer,
    string_manipulator,
    get_current_time,
    list_operations,
]

__all__ = [
    "json_parser",
    "text_summarizer",
    "string_manipulator",
    "get_current_time",
    "list_operations",
    "ADVANCED_TOOLS",
]
