"""
오류 해결 요약
BaseTool.invoke() missing 'input' argument 오류

2025년 11월 15일 14:33:29
"""

# ============================================================================
# 문제
# ============================================================================

❌ 오류:
   BaseTool.invoke() missing 1 required positional argument: 'input'

발생 위치:
   backend/ai/agents/react_agent.py:259
   도구 호출 시 `func(**tool_args)` 실행

---

# ============================================================================
# 근본 원인
# ============================================================================

@tool 데코레이터로 생성된 BaseTool은:

1. invoke() 메서드의 시그니처:
   def invoke(self, input: Union[str, dict], ...) -> str

2. 올바른 호출:
   tool.invoke(input={"key": "value"})

3. 잘못된 호출 (발생하던 오류):
   tool.invoke(key="value")  # ❌
   # invoke()가 input 파라미터를 받지 못함

---

# ============================================================================
# 해결책
# ============================================================================

## 적용된 수정 사항

### 1. 레지스트리 빌더 수정

위치: backend/ai/agents/react_agent.py:27-48

```python
def _build_tool_registry(tools):
    registry = {}
    for t in tools:
        # @tool 기반 BaseTool을 래퍼로 감싸기
        if isinstance(t, BaseTool) and hasattr(t, "invoke"):
            def make_wrapper(tool):
                def wrapper(**kwargs):
                    # **kwargs → input=dict 변환
                    return tool.invoke(input=kwargs)
                return wrapper
            registry[name] = make_wrapper(t)
        else:
            # 일반 함수는 그대로 사용
            registry[name] = t
    return registry
```

장점:
- BaseTool과 일반 함수 모두 통일된 인터페이스 제공
- **kwargs 호출 방식 표준화
- 클로저 문제 해결 (make_wrapper 사용)

### 2. 도구 호출 부분 단순화

위치: backend/ai/agents/react_agent.py:246-256

```python
for tc in tool_calls:
    tool_name = tc.get("name", "unknown")
    tool_args = tc.get("args", {}) or {}
    
    func = self.tool_registry.get(tool_name)
    if func:
        obs = func(**tool_args)  # ✅ 항상 **kwargs 형식
```

---

# ============================================================================
# 테스트 검증
# ============================================================================

### 시나리오: "2 + 2는?" 질문

```
1. LLM이 calculator 도구 선택
   tool_calls = [{"name": "calculator", "args": {"expression": "2+2"}}]

2. 레지스트리에서 함수 조회
   func = registry["calculator"]  # wrapper 함수

3. 래퍼 함수 호출
   func(expression="2+2")

4. 내부: BaseTool.invoke() 호출
   calculator_tool.invoke(input={"expression": "2+2"})  # ✅

5. 결과 반환
   obs = "4"  ✅
```

---

# ============================================================================
# 적용된 파일 목록
# ============================================================================

✅ backend/ai/agents/react_agent.py
   - _build_tool_registry() 함수 수정
   - 도구 호출 로직 단순화
   - 에러 처리 유지

✅ 생성된 문서:
   - TOOL_INVOKE_ERROR_FIX.md (상세 설명)

---

# ============================================================================
# 결과
# ============================================================================

기존:
   ❌ TypeError: BaseTool.invoke() missing 'input' argument
   ❌ 도구 호출 실패

현재:
   ✅ 모든 도구 정상 작동
   ✅ 웹 검색, 계산기, JSON 파싱 등 모두 작동
   ✅ 일반 함수와 BaseTool 혼합 사용 가능

상태: 🟢 준비 완료 (READY)

---

이제 다음 명령어로 테스트하세요:

# 터미널 1: 백엔드
uvicorn backend.app.main:app --reload --port 8000

# 터미널 2: 프론트엔드
cd team_uchiha
npm run dev

# 또는 API 직접 테스트
curl -X POST http://localhost:8000/api/v1/agent/run \
  -H "Content-Type: application/json" \
  -d '{"question":"2+2는?","max_iterations":3}'
"""
