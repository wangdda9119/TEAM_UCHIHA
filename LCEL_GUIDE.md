# LCEL (LangChain Expression Language) 모듈화 가이드

완전히 모듈화된 LCEL 체인 시스템입니다. 다양한 NLP 작업을 쉽게 수행할 수 있습니다.

## 📋 목차
1. [구조 소개](#구조-소개)
2. [사용 가능한 체인들](#사용-가능한-체인들)
3. [API 사용 예제](#api-사용-예제)
4. [Python 코드로 직접 사용](#python-코드로-직접-사용)
5. [커스텀 체인 만들기](#커스텀-체인-만들기)

---

## 🏗️ 구조 소개

### 계층 구조

```
backend/ai/chains/lcel_chain.py
├── get_llm()                          # LLM 초기화
├── 각 기능별 체인 함수
│   ├── get_simple_qa_chain()
│   ├── get_summarization_chain()
│   ├── get_sentiment_analysis_chain()
│   └── ... (더 많음)
├── CHAIN_REGISTRY                     # 모든 체인 등록
└── get_chain()                        # 팩토리 함수

backend/api/v1/routes/lcel.py
└── FastAPI 엔드포인트들
```

### 특징

✅ **완전 모듈화**: 각 체인이 독립적으로 동작  
✅ **팩토리 패턴**: `get_chain("type")`으로 쉽게 선택  
✅ **등록 기반**: 새 체인 추가가 간단  
✅ **타입 안전성**: Pydantic 모델로 검증  
✅ **에러 처리**: 명확한 에러 메시지  

---

## 🎯 사용 가능한 체인들

| 체인명 | 기능 | 사용 사례 |
|--------|------|---------|
| `simple_qa` | 기본 질문-답변 | 일반적인 질문에 답변 |
| `summarize` | 텍스트 요약 | 긴 문서를 짧게 요약 |
| `translate` | 번역 | 다국어 번역 |
| `sentiment` | 감정 분석 | 리뷰/댓글 감정 분석 |
| `keywords` | 키워드 추출 | 문서의 핵심 키워드 |
| `questions` | 질문 생성 | 학습용 질문 생성 |
| `style_transform` | 스타일 변환 | 텍스트 톤 변경 |
| `multi_step` | 다중 단계 | 요약 → 번역 등 |
| `parallel` | 병렬 분석 | 여러 분석 동시 실행 |
| `context_qa` | 컨텍스트 QA | 문서 기반 질문 답변 |
| `verify` | 사실성 검증 | 정보 사실 여부 확인 |

---

## 🌐 API 사용 예제

### 1️⃣ 기본 질문-답변

```bash
curl -X POST http://localhost:8000/api/v1/lcel/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "파이썬이란 무엇인가?"}'
```

**응답:**
```json
{
  "result": "파이썬은 1991년 Guido van Rossum이 만든 고급 프로그래밍 언어입니다...",
  "chain_type": "simple_qa"
}
```

### 2️⃣ 텍스트 요약

```bash
curl -X POST http://localhost:8000/api/v1/lcel/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "긴 텍스트를 요약하려고 합니다. 이 텍스트는 매우 길고 많은 정보를 포함하고 있습니다..."
  }'
```

**응답:**
```json
{
  "result": "이 텍스트는 방대한 정보를 담고 있으며 요약이 필요합니다.",
  "chain_type": "summarize"
}
```

### 3️⃣ 감정 분석

```bash
curl -X POST http://localhost:8000/api/v1/lcel/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "이 제품 정말 최고예요! 추천합니다!"}'
```

**응답:**
```json
{
  "result": "감정: 긍정\n신뢰도: 0.95\n설명: '최고예요', '추천합니다' 등 긍정적 표현 사용",
  "chain_type": "sentiment"
}
```

### 4️⃣ 키워드 추출

```bash
curl -X POST http://localhost:8000/api/v1/lcel/keywords \
  -H "Content-Type: application/json" \
  -d '{"text": "기계 학습은 인공지능의 하위 분야입니다. 데이터 과학자들은 기계 학습 알고리즘을 사용합니다."}'
```

**응답:**
```json
{
  "result": "기계 학습, 인공지능, 데이터 과학, 알고리즘, 하위 분야",
  "chain_type": "keywords"
}
```

### 5️⃣ 질문 생성

```bash
curl -X POST http://localhost:8000/api/v1/lcel/generate-questions \
  -H "Content-Type: application/json" \
  -d '{"text": "파이썬은 인터프리터 언어입니다. 동적 타이핑을 지원합니다."}'
```

**응답:**
```json
{
  "result": "1. 파이썬의 주요 특징은 무엇인가?\n2. 인터프리터 언어가 무엇인가?\n3. 동적 타이핑의 장점은?",
  "chain_type": "questions"
}
```

### 6️⃣ 컨텍스트 기반 QA

```bash
curl -X POST http://localhost:8000/api/v1/lcel/context-qa \
  -H "Content-Type: application/json" \
  -d '{
    "context": "파이썬은 1991년 Guido van Rossum이 만들었습니다.",
    "question": "파이썬을 누가 만들었나요?"
  }'
```

**응답:**
```json
{
  "result": "파이썬은 Guido van Rossum이 1991년에 만들었습니다.",
  "chain_type": "context_qa"
}
```

### 7️⃣ 병렬 분석

```bash
curl -X POST http://localhost:8000/api/v1/lcel/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "이 제품은 정말 훌륭합니다! 품질도 좋고 가격도 합리적입니다."}'
```

**응답:**
```json
{
  "summary": "고품질의 합리적인 가격 제품에 대한 긍정적 평가",
  "sentiment": "감정: 긍정\n신뢰도: 0.98",
  "keywords": "제품, 품질, 가격, 훌륭함, 합리적",
  "chain_type": "parallel"
}
```

### 8️⃣ 사실성 검증

```bash
curl -X POST http://localhost:8000/api/v1/lcel/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "지구는 태양 주위를 공전합니다."}'
```

**응답:**
```json
{
  "result": "평가: 사실\n신뢰도: 0.99\n설명: 과학적으로 증명된 천문학 사실입니다.",
  "chain_type": "verify"
}
```

### 📚 사용 가능한 체인 목록

```bash
curl http://localhost:8000/api/v1/lcel/chains
```

**응답:**
```json
{
  "available_chains": [
    "simple_qa",
    "summarize",
    "translate",
    "sentiment",
    "keywords",
    "questions",
    "style_transform",
    "multi_step",
    "parallel",
    "context_qa",
    "verify"
  ],
  "count": 11,
  "description": { ... }
}
```

---

## 🐍 Python 코드로 직접 사용

### 기본 사용법

```python
from backend.ai.chains.lcel_chain import get_chain

# 체인 선택
chain = get_chain("simple_qa")

# 실행
result = chain.invoke({"question": "파이썬이란?"})
print(result)
```

### 각 체인별 사용법

```python
# 1. 질문-답변
chain = get_chain("simple_qa")
result = chain.invoke({"question": "AI란 무엇인가?"})

# 2. 요약
chain = get_chain("summarize")
result = chain.invoke({"text": "긴 텍스트..."})

# 3. 감정 분석
chain = get_chain("sentiment")
result = chain.invoke({"text": "좋은 제품입니다!"})

# 4. 키워드 추출
chain = get_chain("keywords")
result = chain.invoke({"text": "기계 학습은 AI의 일부입니다..."})

# 5. 질문 생성
chain = get_chain("questions")
result = chain.invoke({"text": "파이썬은..."})

# 6. 컨텍스트 QA
chain = get_chain("context_qa")
result = chain.invoke({
    "context": "파이썬은 1991년 만들어졌습니다.",
    "question": "파이썬은 언제 만들어졌나요?"
})

# 7. 병렬 분석
chain = get_chain("parallel")
result = chain.invoke({"text": "훌륭한 제품입니다!"})
# result = {
#     "summary": "...",
#     "sentiment": "...",
#     "keywords": "..."
# }

# 8. 사실성 검증
chain = get_chain("verify")
result = chain.invoke({"statement": "지구는 둥글다."})
```

---

## 🛠️ 커스텀 체인 만들기

### 방법 1: 기존 함수 수정

`lcel_chain.py`에 새 함수를 추가하고 `CHAIN_REGISTRY`에 등록하세요.

```python
# lcel_chain.py에 추가

def get_code_review_chain():
    """코드 리뷰 체인"""
    llm = get_llm(temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 경험 많은 소프트웨어 엔지니어입니다. 코드를 검토하고 개선 사항을 제시하세요."),
        ("user", "코드:\n{code}")
    ])
    
    return prompt | llm | StrOutputParser()

# CHAIN_REGISTRY에 추가
CHAIN_REGISTRY["code_review"] = get_code_review_chain
```

### 방법 2: 직접 체인 만들기

```python
from backend.ai.chains.lcel_chain import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 커스텀 체인 생성
llm = get_llm()
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 창의적인 작가입니다."),
    ("user", "{topic}에 대해 짧은 이야기를 써주세요.")
])

story_chain = prompt | llm | StrOutputParser()

# 사용
result = story_chain.invoke({"topic": "마법의 숲"})
print(result)
```

---

## ⚙️ 설정 및 조정

### LLM 파라미터 조정

```python
from backend.ai.chains.lcel_chain import get_llm

# 온도 조정 (창의성)
# - 0.0: 결정적 (일관성)
# - 0.5: 균형
# - 1.0+: 창의적
llm = get_llm(temperature=0.5, model="gpt-3.5-turbo")
```

### 다양한 모델 사용

```python
# GPT-4 사용
llm = get_llm(model="gpt-4")

# GPT-3.5-turbo 사용
llm = get_llm(model="gpt-3.5-turbo")
```

---

## 🐛 트러블슈팅

### OpenAI API 키 오류

```
OpenAIError: The api_key client option must be set
```

**해결:**
```bash
# .env 파일 확인
echo $OPENAI_API_KEY

# 또는 PowerShell
$env:OPENAI_API_KEY
```

### 타임아웃 오류

```python
# timeout 추가
llm = ChatOpenAI(
    api_key=api_key,
    model="gpt-3.5-turbo",
    request_timeout=30
)
```

### 메모리 부족

병렬 처리 수 줄이기:

```python
# 병렬 처리 대신 순차 처리
chain1 | chain2 | chain3
```

---

## 📊 성능 팁

1. **온도 최적화**: 분석 작업은 낮게(0.1), 창의 작업은 높게(0.8)
2. **모델 선택**: 비용 vs 성능 트레이드오프 고려
3. **캐싱**: 동일한 입력은 캐시되도록 설정
4. **배치 처리**: 대량의 텍스트는 배치로 처리

---

## 📚 참고 자료

- [LangChain 문서](https://python.langchain.com/)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [LangChain Expression Language](https://python.langchain.com/docs/expression_language/)

---

## 💡 다음 단계

1. **Retrieval**: FAISS와 통합하여 RAG 구현
2. **Memory**: 대화 이력 저장 및 관리
3. **Tools**: 외부 API/도구 통합
4. **Agents**: 자동 의사결정 에이전트 구축
