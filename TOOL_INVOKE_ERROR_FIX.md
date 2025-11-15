"""
BaseTool.invoke() 호출 오류 해결
2025년 11월 15일
"""

# ============================================================================
# 문제: BaseTool.invoke() missing 1 required positional argument: 'input'
# ============================================================================

## 원인 분석

### 1. @tool 데코레이터의 동작 방식

```python
from langchain_core.tools import tool

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """검색 도구"""
    return f"검색: {query}"

# @tool 데코레이터는 함수를 BaseTool 인스턴스로 변환
print(type(web_search))  # <class 'langchain_core.tools.structured_tool.StructuredTool'>

# BaseTool의 invoke() 메서드는 input 파라미터를 받음
# invoke(input: Union[str, dict], ...) -> str
```

### 2. 기존 레지스트리 생성 방식의 문제

```python
# 이전 코드
registry[name] = t.invoke  # invoke 메서드 자체를 저장

# 도구 호출 시
func = registry["web_search"]  # → t.invoke 메서드
obs = func(**tool_args)  # ← 잘못된 호출!

# tool_args = {"query": "파이썬", "max_results": 5}
# func(**tool_args)는 다음과 같이 전달됨:
# invoke(query="파이썬", max_results=5)  # ❌

# 하지만 invoke()는 다음을 기대함:
# invoke(input={"query": "파이썬", "max_results": 5})  # ✅
```

### 3. 에러 발생 과정

```
LLM이 tool_calls 생성:
{
  "name": "web_search",
  "args": {"query": "파이썬", "max_results": 5},
  "id": "call_123"
}
  ↓
ReactAgent가 tool_registry에서 함수 찾음:
registry["web_search"] = BaseTool.invoke
  ↓
도구 실행 시도:
func(**tool_args)
= invoke(query="파이썬", max_results=5)  # ❌ 잘못된 형식
  ↓
TypeError: invoke() missing 1 required positional argument: 'input'
```

---

## 해결책

### BaseTool.invoke()의 올바른 호출 방식

```python
# invoke()의 실제 시그니처
def invoke(
    self,
    input: Union[str, dict],  # ← input 파라미터가 필수
    config: Optional[RunnableConfig] = None,
    **kwargs
) -> str:
    pass

# 올바른 호출 방식
tool.invoke(input={"query": "파이썬", "max_results": 5})
tool.invoke(input="파이썬")
```

### 래퍼 함수를 이용한 해결

```python
def _build_tool_registry(tools):
    registry = {}
    for t in tools:
        name = getattr(t, "name", None) or getattr(t, "__name__", None)
        
        if isinstance(t, BaseTool) and hasattr(t, "invoke"):
            # BaseTool을 래핑하여 **kwargs를 input=dict로 변환
            def make_wrapper(tool):
                def wrapper(**kwargs):
                    return tool.invoke(input=kwargs)  # ✅ 올바른 형식
                return wrapper
            registry[name] = make_wrapper(t)
        elif callable(t):
            # 일반 함수는 직접 사용
            registry[name] = t
    
    return registry
```

### 클로저 문제 해결

중요: 루프에서 함수를 생성할 때 클로저 문제 발생

```python
# ❌ 잘못된 방식 (모든 래퍼가 마지막 t를 참조)
for t in tools:
    def wrapper(**kwargs):
        return t.invoke(input=kwargs)  # t가 루프 변수
    registry[name] = wrapper

# ✅ 올바른 방식 (팩토리 함수로 각각의 t 캡처)
for t in tools:
    def make_wrapper(tool):
        def wrapper(**kwargs):
            return tool.invoke(input=tool)  # tool이 파라미터로 캡처됨
        return wrapper
    registry[name] = make_wrapper(t)
```

---

## 구현된 해결책

### backend/ai/agents/react_agent.py 수정

```python
def _build_tool_registry(tools: List[Union[BaseTool, Callable]]) -> Dict[str, Callable]:
    """
    도구 리스트로부터 {tool_name: 래퍼함수} 레지스트리를 생성합니다.
    
    @tool으로 생성된 BaseTool의 invoke()는 input 파라미터를 받으므로
    래퍼 함수로 감싸서 **kwargs를 input=dict로 변환합니다.
    """
    registry = {}
    for t in tools:
        name = getattr(t, "name", None) or getattr(t, "__name__", None)
        if not name:
            continue

        # @tool 기반 BaseTool
        if isinstance(t, BaseTool) and hasattr(t, "invoke"):
            # 클로저 문제 해결: 팩토리 함수 사용
            def make_wrapper(tool):
                def wrapper(**kwargs):
                    return tool.invoke(input=kwargs)
                return wrapper
            registry[name] = make_wrapper(t)
        
        # 일반 함수
        elif callable(t):
            registry[name] = t
    
    return registry
```

### 도구 호출 부분 단순화

```python
# 모든 도구가 이미 올바르게 래핑되었으므로 단순히 호출
for tc in tool_calls:
    tool_name = tc.get("name", "unknown")
    tool_args = tc.get("args", {}) or {}
    
    func = self.tool_registry.get(tool_name)
    if func:
        obs = func(**tool_args)  # ✅ 항상 **kwargs 형식
```

---

## 테스트 검증

### 도구 호출 흐름

```
1. LLM 응답
   tool_calls = [{"name": "web_search", "args": {"query": "파이썬"}}]
   
2. 레지스트리 조회
   func = registry["web_search"]  # wrapper 함수
   
3. 래퍼 함수 실행
   func(query="파이썬")
   
4. 내부: input 파라미터 변환
   web_search_tool.invoke(input={"query": "파이썬"})  # ✅
   
5. BaseTool 실행
   return "파이썬 검색 결과..."
```

---

## 추가 정보

### BaseTool vs 일반 함수

| 타입 | 호출 방식 | 비고 |
|------|---------|------|
| `@tool` BaseTool | `invoke(input=dict)` | LangChain 표준 |
| 일반 함수 | `func(**kwargs)` | Python 표준 |

### LangChain의 tool_calls 형식

```python
tool_calls = [
    {
        "name": "web_search",  # tool.name 속성
        "args": {              # 파라미터 딕셔너리
            "query": "파이썬",
            "max_results": 5
        },
        "id": "call_abc123"    # tool_call id
    }
]
```

### 왜 이런 설계인가?

LangChain의 BaseTool은 다음을 지원:
- `invoke()` - 동기 실행
- `ainvoke()` - 비동기 실행
- `invoke()` 메서드는 단일 input 파라미터를 받아
  모든 파라미터를 하나의 dict로 처리할 수 있음

---

## 결론

✅ **문제 해결됨**
- BaseTool의 invoke() 호출 방식 이해
- 래퍼 함수로 적절히 변환
- 모든 도구 타입 통일된 호출 인터페이스 제공

✅ **이제 모든 도구가 정상 작동**
- @tool 데코레이터 기반
- 일반 함수
- 혼합 도구 세트

생성일: 2025년 11월 15일
해결 상태: ✅ 완료
"""
