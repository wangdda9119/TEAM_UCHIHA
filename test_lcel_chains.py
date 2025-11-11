"""
LCEL 체인 사용 예제 (테스트용 스크립트)
"""

import asyncio
from backend.ai.chains.lcel_chain import get_chain


async def main():
    """다양한 LCEL 체인 테스트"""
    
    print("=" * 80)
    print("🚀 LCEL 체인 모듈화 테스트")
    print("=" * 80)
    
    # 1. 간단한 QA
    print("\n1️⃣  [Simple QA]")
    print("-" * 40)
    try:
        chain = get_chain("simple_qa")
        result = chain.invoke({"question": "파이썬이란 무엇인가?"})
        print(f"Q: 파이썬이란 무엇인가?")
        print(f"A: {result[:100]}...")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 2. 텍스트 요약
    print("\n2️⃣  [Summarization]")
    print("-" * 40)
    try:
        chain = get_chain("summarize")
        text = "파이썬은 1991년 Guido van Rossum이 만든 프로그래밍 언어입니다. 간단하고 읽기 쉬운 문법으로 유명합니다. 데이터 과학, 웹 개발, 자동화 등 다양한 분야에서 사용됩니다."
        result = chain.invoke({"text": text})
        print(f"원본: {text}")
        print(f"요약: {result}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 3. 감정 분석
    print("\n3️⃣  [Sentiment Analysis]")
    print("-" * 40)
    try:
        chain = get_chain("sentiment")
        result = chain.invoke({"text": "이 제품 정말 최고예요! 강력히 추천합니다!"})
        print(f"분석: {result}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 4. 키워드 추출
    print("\n4️⃣  [Keyword Extraction]")
    print("-" * 40)
    try:
        chain = get_chain("keywords")
        text = "기계 학습은 인공지능의 하위 분야입니다. 데이터 과학자들은 기계 학습 알고리즘을 사용하여 패턴을 찾습니다."
        result = chain.invoke({"text": text})
        print(f"텍스트: {text}")
        print(f"키워드: {result}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 5. 질문 생성
    print("\n5️⃣  [Question Generation]")
    print("-" * 40)
    try:
        chain = get_chain("questions")
        text = "파이썬은 인터프리터 언어입니다. 동적 타이핑을 지원하며 객체 지향 프로그래밍을 가능하게 합니다."
        result = chain.invoke({"text": text})
        print(f"텍스트: {text}")
        print(f"생성된 질문:\n{result}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 6. 컨텍스트 기반 QA
    print("\n6️⃣  [Context-Aware QA]")
    print("-" * 40)
    try:
        chain = get_chain("context_qa")
        context = "파이썬은 1991년 Guido van Rossum이 만들었습니다. 현재 가장 인기 있는 프로그래밍 언어 중 하나입니다."
        question = "파이썬을 누가 만들었나요?"
        result = chain.invoke({
            "context": context,
            "question": question
        })
        print(f"컨텍스트: {context}")
        print(f"질문: {question}")
        print(f"답변: {result}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 7. 병렬 분석
    print("\n7️⃣  [Parallel Analysis]")
    print("-" * 40)
    try:
        chain = get_chain("parallel")
        text = "이 제품은 정말 훌륭합니다! 품질도 좋고 가격도 합리적입니다. 매우 만족합니다."
        result = chain.invoke({"text": text})
        print(f"텍스트: {text}")
        print(f"요약: {result.get('summary', 'N/A')}")
        print(f"감정: {result.get('sentiment', 'N/A')[:50]}...")
        print(f"키워드: {result.get('keywords', 'N/A')}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 8. 사실성 검증
    print("\n8️⃣  [Verification]")
    print("-" * 40)
    try:
        chain = get_chain("verify")
        result = chain.invoke({"statement": "지구는 태양 주위를 공전합니다."})
        print(f"검증: {result}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n" + "=" * 80)
    print("✅ 모든 테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    # 환경 변수 로드
    from backend.core.env_setup import setup_environment
    setup_environment()
    
    # 테스트 실행
    asyncio.run(main())
