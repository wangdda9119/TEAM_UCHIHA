```
# 최신 LangChain @tool 데코레이터 업그레이드 가이드

## 📋 현재 상태 분석

### 기존 구조
```
┌─────────────────────────────────────────┐
│         API Routes                      │
│  • agent.py → /agent/run               │
│  • ai.py → /ai/ask                     │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
    ReactAgent      LCEL Chains
    (ReAct 패턴)    (파이프라인)
        │                 │
        └────────┬────────┘
                 ▼
            TOOLS List
         (@tool 기반)
         
    • web_search()
    • calculator()
```

### 문제점과 개선사항

| 항목 | 기존 | 개선됨 |
|------|------|--------|
| **@tool 문법** | ✅ 이미 최신 (langchain_core.tools) | ✅ Pydantic v2 필드 타입 추가 |
| **도구 수** | 2개 | 7개 (5개 새로운 도구 추가) |
| **에러 처리** | 기본 수준 | ✅ 상세한 TypeError/Exception 분리 |
| **도구 관리** | TOOLS만 사용 | ✅ ALL_TOOLS로 통합 관리 |
| **로깅** | 기본 | ✅ 단계별 상세 로깅 |
| **문서화** | 간단함 | ✅ Pydantic Field 기반 자세한 설명 |

---

## 🚀 최신 @tool 데코레이터 개선사항

### 1. Pydantic Field 기반 문서화

**기존:**
```python
@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    인터넷에서 정보를 검색합니다.
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수
    """
```

**개선:**
```python
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
```

**장점:**
- LLM이 도구 선택 시 더 정확한 매개변수 정보 제공
- 자동 스키마 생성
- IDE 자동완성 개선

### 2. 추가된 도구들

#### 데이터 도구
- `json_parser()` - JSON 파싱 및 검증
- `text_summarizer()` - 텍스트 요약
- `string_manipulator()` - 문자열 처리

#### 정보 도구
- `get_current_time()` - 현재 시간 조회
- `list_operations()` - 도구 목록 조회

### 3. ReactAgent 개선사항

```python
# 이전
agent = ReactAgent()
result = agent.run(question)

# 개선 - 커스텀 도구 사용 가능
from backend.ai.tools import ADVANCED_TOOLS
agent = ReactAgent(tools=ADVANCED_TOOLS)
result = agent.run(question)
```

**추가된 기능:**
- `tools_used` 필드 - 실제 사용된 도구 추적
- 개선된 에러 메시지 - TypeError vs Exception 분리
- 상세한 로깅 - 각 단계별 진행 상황 추적
- 커스텀 도구 지원 - 인스턴스 생성 시 도구 지정 가능

---

## 📦 파일 구조 변경사항

```
backend/ai/tools/
├── __init__.py              # 통합 exports
│   ├── TOOLS               # 기본 도구 (web_search, calculator)
│   ├── ADVANCED_TOOLS      # 고급 도구 5개
│   └── ALL_TOOLS           # 전체 도구 (TOOLS + ADVANCED_TOOLS)
├── tools.py                # @tool 데코레이터 (2개)
│   ├── web_search()        # 업그레이드: Field 사용
│   └── calculator()        # 업그레이드: Field 사용
└── advanced_tools.py       # [NEW] @tool 데코레이터 (5개)
    ├── json_parser()
    ├── text_summarizer()
    ├── string_manipulator()
    ├── get_current_time()
    └── list_operations()
```

---

## 🔄 업그레이드 체크리스트

### ✅ 완료된 작업

1. **tools.py 업그레이드**
   - [x] Pydantic Field 임포트 추가
   - [x] web_search() - Field 기반 설명 추가
   - [x] calculator() - Field 기반 설명 추가

2. **advanced_tools.py 생성**
   - [x] json_parser() 구현
   - [x] text_summarizer() 구현
   - [x] string_manipulator() 구현
   - [x] get_current_time() 구현
   - [x] list_operations() 구현

3. **tools/__init__.py 통합**
   - [x] 기본 도구 exports
   - [x] 고급 도구 exports
   - [x] ALL_TOOLS 통합

4. **ReactAgent 업그레이드**
   - [x] ALL_TOOLS 사용
   - [x] tools 파라미터 추가
   - [x] tools_used 추적
   - [x] 에러 처리 개선
   - [x] 상세한 로깅 추가
   - [x] 문서화 개선

### 📌 다음 단계 (선택사항)

- [ ] LangGraph agent_graph.py 완전 구현
- [ ] LCEL 체인에 문서 검색 기능 추가
- [ ] 벡터 스토어 (FAISS) 통합
- [ ] 도구 사용 통계 수집
- [ ] 도구별 성능 모니터링

---

## 📝 사용 예제

### 기본 사용

```python
from backend.ai.agents.react_agent import ReactAgent

# 기본 도구로 에이전트 생성
agent = ReactAgent(max_iterations=5)
result = agent.run("파이썬 최신 버전은?")

print(result["answer"])
print(f"사용 도구: {result['tools_used']}")
print(f"반복 횟수: {result['iterations']}")
```

### 커스텀 도구 사용

```python
from backend.ai.agents.react_agent import ReactAgent
from backend.ai.tools.advanced_tools import ADVANCED_TOOLS

# 고급 도구만 사용
agent = ReactAgent(tools=ADVANCED_TOOLS)
result = agent.run("현재 시간은?")
```

### 모든 도구 사용

```python
from backend.ai.agents.react_agent import ReactAgent
from backend.ai.tools import ALL_TOOLS

agent = ReactAgent(tools=ALL_TOOLS)
result = agent.run("JSON을 파싱하고 요약해줘: {\"name\":\"test\"}")
```

---

## 🔧 API 엔드포인트 변경사항

### /agent/run

**응답 (개선됨):**
```json
{
  "question": "파이썬 최신 버전은?",
  "answer": "파이썬 3.12가 최신 버전입니다...",
  "iterations": 2,
  "status": "success",
  "tools_used": ["web_search"],
  "memory": [...]
}
```

---

## ⚠️ 주의사항

1. **API 호환성**: 기존 API 호출은 동작하지만 응답에 `tools_used` 필드 추가됨
2. **도구 선택**: ALL_TOOLS 사용 시 LLM이 더 많은 선택지를 가짐 → 비용 증가 가능
3. **Pydantic v2**: `from pydantic import Field` 사용 (v1과 호환 가능)

---

## 📚 참고 링크

- [LangChain @tool 데코레이터 문서](https://python.langchain.com/docs/concepts/tools/)
- [Pydantic v2 Field 문서](https://docs.pydantic.dev/latest/concepts/fields/)
- [ReAct 논문](https://arxiv.org/abs/2210.03629)

```
