# LangChain 0.3+ & LangGraph 버전 업그레이드 가이드

## 📋 변경 사항 요약

### 1. 라이브러리 버전 업데이트 (`requirements.txt`)

| 라이브러리 | 이전 버전 | 새 버전 |
|----------|---------|---------|
| langchain | ≥0.3.9 | ≥0.3.12 |
| langchain-core | 자동 | ≥0.3.5 |
| langchain-openai | ≥0.1.0 | ≥0.2.0 |
| langgraph | ≥0.2.39 | ≥0.2.50 |
| langgraph-checkpoint | 추가 | ≥1.0.0 |

### 2. ReactAgent 리팩토링

#### 이전 방식 (LangChain 0.2 스타일)
```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
# ❌ LangChain 0.3+에서는 이 import가 작동하지 않음
```

#### 새로운 방식 (LangChain 0.3+ & LangGraph)
```python
from langgraph.prebuilt import create_react_agent
# ✅ 최신 방식: LangGraph를 사용한 에이전트

agent = create_react_agent(
    model=self.llm,
    tools=TOOLS,
    prompt=prompt,
)
```

### 3. 핵심 변경 사항

#### 에이전트 생성
```python
# 이전
agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent, tools, max_iterations=10)
result = executor.invoke({"input": question, ...})

# 현재
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=prompt
)
result = agent.invoke({"messages": messages}, config={...})
```

#### 메시지 처리
```python
# 이전
result.get("output")  # 문자열 반환

# 현재
messages = result.get("messages", [])
# 메시지 객체 배열 반환
for msg in messages:
    if hasattr(msg, 'content'):
        answer = msg.content
```

#### 도구 호출 추적
```python
# 이전
intermediate_steps = result.get("intermediate_steps", [])

# 현재
for msg in messages:
    if hasattr(msg, 'tool_calls'):
        tool_calls = msg.tool_calls
```

---

## 🚀 사용 가능한 도구 (@tool 데코레이터)

### 1. web_search
```python
@tool
def web_search(query: str, max_results: int = 5) -> str:
    """인터넷에서 정보를 검색합니다."""
    # Tavily API 사용
```

**사용 예시:**
```
질문: "파이썬 최신 버전은?"
→ 에이전트가 web_search("파이썬 최신 버전") 자동 호출
```

### 2. calculator
```python
@tool
def calculator(expression: str) -> str:
    """수학 연산을 수행합니다."""
    # eval 기반 계산
```

**사용 예시:**
```
질문: "100 * 200은?"
→ 에이전트가 calculator("100 * 200") 자동 호출
```

---

## 🔧 API 엔드포인트 (변경 없음)

모든 API 엔드포인트는 동일하게 작동합니다:

### POST /api/v1/agent/run
```bash
curl -X POST http://localhost:8000/api/v1/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "question": "파이썬 최신 버전은?",
    "max_iterations": 10
  }'
```

응답:
```json
{
  "question": "파이썬 최신 버전은?",
  "answer": "파이썬의 최신 버전은 3.12.1입니다...",
  "iterations": 1,
  "status": "success",
  "memory": [...]
}
```

---

## ✅ 테스트 체크리스트

- [ ] 백엔드 서버 시작: `python -m backend.app.main`
- [ ] `/api/v1/agent/health` 엔드포인트 확인
- [ ] 웹 검색 질문: "현재 시간은?"
- [ ] 계산 질문: "1234 + 5678은?"
- [ ] 복합 질문: "파이썬 3.12의 주요 기능은?"

---

## 📊 성능 개선 사항

| 항목 | 개선 사항 |
|------|---------|
| 코드 라인 | ~363줄 → ~200줄 |
| 복잡도 | 높음 → 낮음 |
| 유지보수성 | 어려움 → 쉬움 |
| 버그 가능성 | 높음 → 낮음 |
| 도구 추가 난이도 | 어려움 → 매우 쉬움 |

---

## 🐛 트러블슈팅

### ImportError: cannot import name 'AgentExecutor'
**원인:** 구형 import 경로 사용  
**해결:** 이미 수정됨 (`langgraph.prebuilt.create_react_agent` 사용)

### 도구가 호출되지 않음
**확인 사항:**
1. `TAVILY_API_KEY` 설정 확인 (웹 검색용)
2. 도구 정의가 `@tool` 데코레이터로 되어 있는지 확인
3. 도구 함수의 docstring이 명확한지 확인

---

## 🎯 다음 단계

1. **백엔드 재시작**
   ```bash
   # uvicorn 터미널에서 Ctrl+C 후 다시 시작
   python -m backend.app.main
   ```

2. **테스트**
   ```bash
   # 프론트엔드에서 AgentInterface 탭 이용
   http://localhost:5173
   ```

3. **모니터링**
   - 로그에서 도구 호출 확인
   - 메모리에서 agent_run 타입의 레코드 확인

---

## 📚 참고 자료

- [LangChain 0.3 마이그레이션 가이드](https://python.langchain.com/docs/guides/migration)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)

---

**업그레이드 완료일:** 2025-11-12  
**상태:** ✅ 완료 및 테스트 준비 완료
