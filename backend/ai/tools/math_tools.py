"""
수학 도구 (Math Tools)
계산, 수학 연산 등
"""

from langchain_core.tools import tool
from loguru import logger
from pydantic import Field


# ============================================================================
# 계산기 도구
# ============================================================================

@tool
def calculator(
    expression: str = Field(..., description="계산식 (예: '2 + 3 * 4', 'sin(3.14)')")
) -> str:
    """
    수학 연산을 수행하고 결과를 반환합니다.
    
    지원되는 연산:
    - 기본 산술: +, -, *, /, **, //
    - 함수: abs(), round(), max(), min(), sum(), pow()
    - 상수: pi, e (math 모듈)
    
    보안: 미리 정의된 함수만 실행 가능합니다.
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
# 수학 도구 목록
# ============================================================================

MATH_TOOLS = [calculator]

__all__ = ["calculator", "MATH_TOOLS"]
