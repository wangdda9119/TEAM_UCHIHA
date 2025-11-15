"""
AI Tools 연결 구조 및 최신 LangChain @tool 업그레이드 가이드

2025년 11월 15일
"""

# ============================================================================
# 1️⃣ 현재 Tools 연결 구조
# ============================================================================

## 구조도

```
┌────────────────────────────────────────────────────────────────┐
│                       FastAPI Routes                            │
├────────────────────────────────────────────────────────────────┤
│  
│  POST /agent/run      POST /ai/ask          POST /agent/...
│   (React Agent)        (LCEL Chain)         (기타 API)
│
└──────────────┬────────────────┬────────────────────────────────┘
               │                │
        ┌──────▼────┐     ┌─────▼────────┐
        │ ReactAgent │     │ LCEL Chains  │
        │(agents/)  │     │  (chains/)   │
        ├────────────┤     ├──────────────┤
        │ ReAct 패턴 │     │ ChatPrompt   │
        │ 도구 호출  │     │ + LLM        │
        │ 루프 제어  │     │ + Parser     │
        └──────┬─────┘     └──────────────┘
               │
        ┌──────▼────────────────────┐
        │  Tools Module (tools/)     │
        ├────────────────────────────┤
        │ @tool 데코레이터 기반      │
        │                            │
        │ 기본 도구:                 │
        │ • web_search()            │
        │ • calculator()            │
        │                            │
        │ 고급 도구:                 │
        │ • json_parser()           │
        │ • text_summarizer()       │
        │ • string_manipulator()    │
        │ • get_current_time()      │
        │ • list_operations()       │
        └────────────────────────────┘
               │
        ┌──────▼─────────────────┐
        │ LLM (ChatOpenAI)        │
        │ • bind_tools()          │
        │ • tool_calls 처리       │
        └────────────────────────┘
```

## 동작 흐름 (ReAct Agent)

```
1. 사용자 질문 입력
   ↓
2. ReactAgent.run(question)
   ├─ 히스토리 메시지 변환 (Dict → Message 객체)
   └─ 도구 바인딩 (LLM에 모든 @tool 전달)
   ↓
3. ReAct Loop (최대 8회 반복)
   ├─ Step A: LLM 추론 (ChatOpenAI.invoke)
   │  └─ "이 도구를 사용해야겠다" → tool_calls 생성
   ├─ Step B: 도구 호출 여부 확인
   │  ├─ tool_calls 있음 → 도구 실행
   │  └─ tool_calls 없음 → 최종 답 반환
   ├─ Step C: 각 도구 실행
   │  ├─ tool_registry에서 함수 찾기
   │  ├─ **kwargs로 함수 호출
   │  └─ 결과를 ToolMessage로 변환
   ├─ Step D: 스크래치패드에 추가
   │  └─ [AIMessage(tool_calls)] + [ToolMessage(result)]
   └─ 반복 (다시 Step A로)
   ↓
4. 최종 답변 반환
   ├─ question: 원본 질문
   ├─ answer: LLM 최종 답변
   ├─ iterations: 실제 반복 횟수
   ├─ tools_used: 사용된 도구 목록
   ├─ status: "success" | "error"
   └─ memory: 대화 히스토리
```

## 도구 등록 및 호출 메커니즘

```python
# 1. 도구 정의 (tools.py)
@tool
def web_search(query: str, max_results: int = 5) -> str:
    """검색 도구"""
    ...

# 2. 도구 리스트 생성
TOOLS = [web_search, calculator]
ADVANCED_TOOLS = [json_parser, text_summarizer, ...]
ALL_TOOLS = TOOLS + ADVANCED_TOOLS

# 3. 레지스트리 구성 (ReactAgent에서)
tool_registry = _build_tool_registry(ALL_TOOLS)
# 결과: {
#   "web_search": <function>,
#   "calculator": <function>,
#   "json_parser": <function>,
#   ...
# }

# 4. LLM에 도구 바인딩
llm_with_tools = llm.bind_tools(ALL_TOOLS)

# 5. 도구 호출
result = llm_with_tools.invoke(messages)
# result.tool_calls = [
#   {"id": "call_xxx", "name": "web_search", "args": {"query": "..."}},
#   ...
# ]

# 6. 도구 실행
for tc in result.tool_calls:
    func = tool_registry[tc["name"]]
    obs = func(**tc["args"])  # ← 도구 함수 호출
```

---

# ============================================================================
# 2️⃣ 최신 LangChain @tool 데코레이터 개선사항
# ============================================================================

## A. Pydantic v2 Field 기반 문서화

### 이전 방식 (기본 @tool)
```python
@tool
def web_search(query: str, max_results: int = 5) -> str:
    """인터넷에서 정보를 검색합니다."""
```

문제점:
- LLM이 파라미터 설명을 못 봄
- 자동 스키마 생성 불가
- 도구 선택 시 부정확함

### 개선 방식 (Field 기반)
```python
from pydantic import Field

@tool
def web_search(
    query: str = Field(..., description="검색 쿼리 (예: '파이썬 최신 버전')"),
    max_results: int = Field(default=5, description="최대 결과 수 (기본값: 5, 최대 10)")
) -> str:
    """인터넷에서 정보를 검색하고 상위 결과를 반환합니다.
    
    이 도구는 Tavily Search API를 사용합니다.
    """
```

장점:
- ✅ LLM이 각 파라미터의 설명을 받음
- ✅ 자동 JSON 스키마 생성
- ✅ 도구 선택 정확도 ↑
- ✅ 파라미터 타입 검증 강화

## B. 새로운 도구 추가 (5개)

### 데이터 처리
1. **json_parser()**
   - JSON 문자열 파싱 및 검증
   - 포맷팅 옵션

2. **text_summarizer()**
   - 간단한 휴리스틱 기반 요약
   - 최대 문장 수 지정 가능

3. **string_manipulator()**
   - 대문자/소문자 변환
   - 문자열 역순
   - 단어/문자 개수 세기

### 정보 조회
4. **get_current_time()**
   - 현재 시간 조회
   - 포맷 옵션 (날짜만, 시간만, 전체)

5. **list_operations()**
   - 사용 가능한 모든 도구 목록
   - 도구별 설명

## C. 도구 관리 개선

```python
# 이전: 단일 도구 세트
from backend.ai.tools.tools import TOOLS

# 개선: 유연한 도구 관리
from backend.ai.tools import (
    TOOLS,              # 기본 도구 (2개)
    ADVANCED_TOOLS,     # 고급 도구 (5개)
    ALL_TOOLS           # 전체 (7개)
)

# 커스텀 도구 세트 사용
agent = ReactAgent(tools=ADVANCED_TOOLS)
```

## D. 에러 처리 개선

### 이전
```python
except Exception as ex:
    obs = f"[tool_error] {type(ex).__name__}: {ex}"
```

### 개선
```python
try:
    if isinstance(tool_args, dict):
        obs = func(**tool_args)  # 올바른 호출
    else:
        obs = func(tool_args)
except TypeError as te:
    obs = f"[오류] 도구 인자 오류: {str(te)}"
except Exception as ex:
    obs = f"[오류] {type(ex).__name__}: {str(ex)}"
```

장점:
- TypeError와 다른 예외 분리
- `**kwargs` vs 위치 인자 자동 선택
- 상세한 에러 메시지

## E. 상세한 로깅

```python
logger.info(f"🤖 에이전트 시작: {question}")
logger.debug(f"🔄 반복 {iterations + 1}/{self.max_iterations}")
logger.debug(f"🔧 도구 호출: {tool_name}")
logger.info(f"✅ {tool_name} 완료")
logger.warning(f"⚠️ 최대 반복 횟수 도달")
logger.info(f"✅ 에이전트 완료: {iterations}반복, 사용 도구={len(set(tools_used))}")
```

각 단계별 진행 상황 추적 가능

## F. tools_used 추적

### 응답에 추가된 필드

```python
{
    "question": "파이썬 최신 버전?",
    "answer": "...",
    "iterations": 2,
    "status": "success",
    "tools_used": ["web_search"],  # ← NEW
    "memory": [...]
}
```

용도:
- 도구 사용 통계 수집
- 성능 분석
- 비용 계산

---

# ============================================================================
# 3️⃣ 파일 구조 변경사항
# ============================================================================

```
backend/ai/tools/
├── __init__.py
│   ├── from .tools import TOOLS, web_search, calculator
│   ├── from .advanced_tools import ADVANCED_TOOLS, ...
│   └── ALL_TOOLS = TOOLS + ADVANCED_TOOLS
│
├── tools.py (기존)
│   ├── @tool web_search()          [업그레이드: Field 추가]
│   ├── @tool calculator()          [업그레이드: Field 추가]
│   └── TOOLS = [web_search, calculator]
│
└── advanced_tools.py               [NEW 파일]
    ├── @tool json_parser()
    ├── @tool text_summarizer()
    ├── @tool string_manipulator()
    ├── @tool get_current_time()
    ├── @tool list_operations()
    └── ADVANCED_TOOLS = [...]
```

## 사용 가능한 imports

```python
# 방법 1: 기본 도구만
from backend.ai.tools import TOOLS

# 방법 2: 고급 도구만
from backend.ai.tools import ADVANCED_TOOLS

# 방법 3: 모든 도구
from backend.ai.tools import ALL_TOOLS

# 방법 4: 개별 도구
from backend.ai.tools import web_search, calculator, json_parser, ...
```

---

# ============================================================================
# 4️⃣ 사용 예제
# ============================================================================

## 예제 1: 기본 사용

```python
from backend.ai.agents.react_agent import ReactAgent

agent = ReactAgent(max_iterations=5)
result = agent.run("파이썬 최신 버전은 뭔가요?")

print(f"질문: {result['question']}")
print(f"답변: {result['answer']}")
print(f"반복: {result['iterations']}")
print(f"사용 도구: {result['tools_used']}")
```

## 예제 2: 커스텀 도구 사용

```python
from backend.ai.agents.react_agent import ReactAgent
from backend.ai.tools import ADVANCED_TOOLS

# 데이터 처리에 특화된 에이전트
agent = ReactAgent(tools=ADVANCED_TOOLS, max_iterations=3)
result = agent.run('JSON을 파싱하고 정보를 요약해: {"name":"test","desc":"example"}')
```

## 예제 3: 혼합 도구 사용

```python
from backend.ai.agents.react_agent import ReactAgent
from backend.ai.tools import TOOLS, ADVANCED_TOOLS

# 모든 도구 사용
all_tools = TOOLS + ADVANCED_TOOLS
agent = ReactAgent(tools=all_tools)
result = agent.run("현재 시간은? 그리고 간단한 계산 2+2는?")
```

## 예제 4: 채팅 히스토리와 함께

```python
from backend.ai.agents.react_agent import ReactAgent

agent = ReactAgent()

# 첫 번째 질문
result1 = agent.run("파이썬이 뭔가요?")

# 히스토리 생성
history = [
    {"role": "user", "content": "파이썬이 뭔가요?"},
    {"role": "assistant", "content": result1["answer"]},
]

# 두 번째 질문 (컨텍스트 유지)
result2 = agent.run("그럼 최신 버전은?", chat_history=history)
```

---

# ============================================================================
# 5️⃣ API 응답 변화
# ============================================================================

## /agent/run POST 응답

### 이전
```json
{
  "question": "파이썬 최신 버전은?",
  "answer": "...",
  "iterations": 2,
  "status": "success",
  "memory": [...]
}
```

### 개선 (신규 필드)
```json
{
  "question": "파이썬 최신 버전은?",
  "answer": "파이썬 3.12가 2023년 10월에 릴리스되었습니다.",
  "iterations": 2,
  "status": "success",
  "tools_used": ["web_search"],
  "memory": [
    {
      "timestamp": "2025-11-15T10:30:45.123456",
      "type": "answer",
      "question": "파이썬 최신 버전은?",
      "answer": "...",
      "iterations": 2,
      "tools_used": ["web_search"]
    }
  ]
}
```

신규 필드:
- `tools_used`: 이번 호출에서 실제 사용된 도구 목록

---

# ============================================================================
# 6️⃣ 체크리스트
# ============================================================================

## ✅ 완료됨

- [x] tools.py에 Pydantic Field 임포트
- [x] web_search() - Field 기반 설명 추가
- [x] calculator() - Field 기반 설명 추가
- [x] advanced_tools.py 생성 (5개 도구)
- [x] tools/__init__.py 통합 (TOOLS, ADVANCED_TOOLS, ALL_TOOLS)
- [x] ReactAgent 업그레이드
  - [x] ALL_TOOLS 기본값
  - [x] tools 파라미터 추가
  - [x] tools_used 추적
  - [x] TypeError/Exception 분리
  - [x] 단계별 로깅
  - [x] 문서화 개선

## 📌 선택사항 (향후)

- [ ] LangGraph agent_graph.py 완전 구현
- [ ] LCEL 체인에 RAG 기능 추가
- [ ] FAISS 벡터 스토어 활성화
- [ ] 도구 사용 통계 대시보드
- [ ] 커스텀 도구 개발 가이드

---

# ============================================================================
# 7️⃣ 주의사항
# ============================================================================

⚠️ **Backward Compatibility**
- 기존 API 호출 계속 작동
- 새로운 `tools_used` 필드만 추가

⚠️ **비용 영향**
- ALL_TOOLS 사용 시 LLM 입력 토큰 증가
- tool_calls 검색 시간 미세 증가 가능

⚠️ **Pydantic 버전**
- `from pydantic import Field` (v1과 v2 모두 호환)
- 현재 프로젝트는 Pydantic v2 기반

---

생성일: 2025년 11월 15일
최종 업데이트: 완료
"""
