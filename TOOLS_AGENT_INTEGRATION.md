## AI Tools와 Agent 통합 - 구현 가이드

### 📋 개요

`ai/tools/` 구조와 `ReactAgent`를 `ToolManager`라는 중앙 관리 클래스로 연결했습니다.

---

## 🏗️ 아키텍처

```
backend/ai/
├── tools/                          # 도구 관리 계층
│   ├── __init__.py                 # 통합 export
│   ├── manager.py                  # ✨ ToolManager (새로 추가)
│   ├── search_tools.py            # 웹 검색
│   ├── data_tools.py              # 데이터 처리
│   ├── system_tools.py            # 시스템 정보
│   └── math_tools.py              # 계산
│
├── agents/
│   └── react_agent.py             # ✨ ToolManager 통합
│
└── chains/
    └── lcel_chain.py
```

---

## 🔧 ToolManager 클래스

### 주요 기능

| 메서드 | 설명 |
|------|------|
| `get_all_tools()` | 모든 도구 반환 |
| `get_tools_by_category(cat)` | 카테고리별 도구 선택 |
| `get_tools_by_categories(cats)` | 여러 카테고리 선택 |
| `get_tool_by_name(name)` | 이름으로 도구 검색 |
| `get_tool_info(name)` | 도구 메타데이터 조회 |
| `list_tools_with_info()` | 모든 도구 정보 조회 |
| `validate_tools()` | 도구 검증 |
| `print_tools_summary()` | 도구 요약 출력 |

### 카테고리

- `search` - 웹 검색 (web_search)
- `data` - 데이터 처리 (json_parser, text_summarizer, string_manipulator)
- `system` - 시스템 정보 (get_current_time, list_operations)
- `math` - 계산 (calculator)

---

## 💡 사용 방법

### 1️⃣ 기본 사용 - 모든 도구

```python
from backend.ai.agents import ReactAgent

# 모든 도구 사용 (기본값)
agent = ReactAgent()
print(f"✅ {len(agent.tools)}개 도구 로드")
```

### 2️⃣ 카테고리 선택

```python
# 검색과 계산 도구만 사용
agent = ReactAgent(tool_categories=["search", "math"])

# 도구 목록 확인
agent.print_tools_summary()
```

### 3️⃣ 커스텀 도구

```python
from backend.ai.tools import calculator, web_search

# 특정 도구만
agent = ReactAgent(tools=[calculator, web_search])
```

### 4️⃣ ToolManager 직접 사용

```python
from backend.ai.tools import get_tool_manager

manager = get_tool_manager()

# 도구 조회
tools = manager.get_all_tools()
print(f"🛠️  사용 가능한 도구: {len(tools)}개")

# 카테고리 정보
info = manager.get_category_info()
for cat, details in info.items():
    print(f"  {cat}: {details['count']}개")

# 도구 정보
tool_info = manager.get_tool_info("calculator")
print(f"  {tool_info['name']}: {tool_info['description']}")

# 요약 출력
manager.print_tools_summary()
```

---

## 📊 ReactAgent 개선사항

### 새 파라미터

```python
ReactAgent(
    max_iterations=8,              # 최대 반복 횟수
    temperature=0.3,               # LLM 창의성
    model="gpt-4o-mini",          # 모델명
    
    # ✨ 새로운 도구 관리 옵션
    tools=None,                    # 도구 리스트 (우선순위 3)
    tool_categories=None,          # 카테고리 선택 (우선순위 2)
    tool_manager=None,             # 커스텀 매니저 (우선순위 1)
)
```

### 새 메서드

```python
# 현재 사용 중인 도구 정보
tools_info = agent.get_available_tools()
# => [{"name": "web_search", "description": "..."}, ...]

# 도구 요약 출력
agent.print_tools_summary()
```

---

## 🔗 통합 흐름

```
User Request
    ↓
ReactAgent.__init__(tool_categories=["search", "math"])
    ↓
ToolManager.get_tools_by_categories(["search", "math"])
    ↓
[web_search, calculator] 반환
    ↓
_build_tool_registry(tools)
    ↓
tool_registry = {
    "web_search": wrapper_func,
    "calculator": wrapper_func
}
    ↓
Agent 실행 시 도구 호출
```

---

## 📝 파일 변경 사항

### 1. `backend/ai/tools/manager.py` (새 파일)
- `ToolManager` 클래스 (중앙 관리)
- `get_tool_manager()` 싱글톤 함수
- 160+ 라인의 완벽한 도구 관리

### 2. `backend/ai/tools/__init__.py` (수정)
```python
from .manager import ToolManager, get_tool_manager

__all__ = [
    # ... 기존 exports ...
    "ToolManager",
    "get_tool_manager",
]
```

### 3. `backend/ai/agents/react_agent.py` (수정)
```python
# 임포트 추가
from backend.ai.tools import get_tool_manager, ToolManager

# __init__ 개선
def __init__(
    self,
    ...,
    tool_categories: Optional[List[str]] = None,
    tool_manager: Optional[ToolManager] = None,
):
    self.tool_manager = tool_manager or get_tool_manager()
    # 우선순위로 도구 선택
    if tool_categories is not None:
        self.tools = self.tool_manager.get_tools_by_categories(tool_categories)
    elif tools is not None:
        self.tools = tools
    else:
        self.tools = self.tool_manager.get_all_tools()

# 새 메서드
def get_available_tools(self) -> List[Dict[str, str]]:
    ...

def print_tools_summary(self) -> None:
    ...
```

---

## 🧪 테스트

`test_tools_integration.py` 작성 완료 (테스트 파일 참고)

### 테스트 내용

1. ToolManager 기본 기능
2. 도구 선택 (카테고리)
3. 도구 메타데이터
4. 도구 검증
5. ReactAgent - 모든 도구
6. ReactAgent - 카테고리 선택
7. ReactAgent - 커스텀 도구
8. ToolManager 요약

---

## ✨ 장점

1. **중앙 관리** - 모든 도구를 한 곳에서 관리
2. **유연성** - 필요한 도구만 선택 가능
3. **확장성** - 새 도구 추가 용이
4. **메타데이터** - 도구 정보 자동 추출
5. **검증** - 도구 상태 체크
6. **문서화** - 도구 정보 자동 제공

---

## 🚀 다음 단계

1. 테스트 실행
   ```bash
   python test_tools_integration.py
   ```

2. API 라우트에 통합
   ```python
   from backend.ai.agents import ReactAgent
   
   @router.post("/agent/query")
   async def query(request: QueryRequest):
       agent = ReactAgent(tool_categories=["search", "math"])
       result = agent.run(request.question)
       return result
   ```

3. 프론트엔드에서 활용
   ```javascript
   const response = await fetch("/api/v1/agent/query", {
     method: "POST",
     body: JSON.stringify({
       question: "파이썬 최신 버전은?",
       tool_categories: ["search"]
     })
   });
   ```

---

## 📚 참고

- **ToolManager**: 도구 중앙 관리 시스템
- **ReactAgent**: LangChain ReAct 패턴 구현
- **@tool**: LangChain의 도구 데코레이터
- **BaseTool**: LangChain 도구 기본 클래스
