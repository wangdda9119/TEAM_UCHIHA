루트
├─ docker-compose.yml            ← Postgres(+pgvector)만 도커로 실행
├─ .env                          ← 환경변수 (예: DB_HOST, OPENAI_API_KEY)
└─ backend
   ├─ app/main.py                ← FastAPI 시작점(+ 라우터 등록)
   ├─ api/v1/router.py           ← /api/v1 하위 라우터 묶음
   │  ├─ routes/ai.py            ← /ai/ask, /ai/agent 엔드포인트
   │  ├─ routes/stt.py           ← /stt/transcribe (STT)
   │  └─ routes/tts.py           ← /tts/synthesize (TTS)
   ├─ core/config.py             ← .env 읽어서 설정 제공(DB URI 등)
   ├─ core/logging.py            ← loguru 로깅 설정(콘솔+파일)
   ├─ db/session.py              ← SQLAlchemy 엔진/세션 주입(get_db)
   ├─ db/models.py               ← 예시 모델(Document)
   ├─ ai/chains/lcel_chain.py    ← LCEL 체인(간단 Q→A)
   ├─ ai/graph/agent_graph.py    ← LangGraph 에이전트(툴 호출 지점)
   ├─ ai/tools/search/web_search.py ← 예시 툴(웹검색 자리에 대체)
   └─ ai/vector/faiss_store.py   ← FAISS 인덱스 헬퍼(add/search/save/load)


요청 → FastAPI → 라우터 → (도메인 로직) → 응답

1) 헬스체크
   GET /health
   app/main.py (직접 응답)

2) 단순 체인(LCEL)
   POST /api/v1/ai/ask
      → routes/ai.py: ask_lcel()
         → ai/chains/lcel_chain.get_simple_chain()
            → RunnableLambda(_answer_fn)  ← (여기에 나중에 RAG/리트리버 연결)
         ← answer 문자열
      ← {"answer": ...}

3) 에이전트(Graph)
   POST /api/v1/ai/agent
      → routes/ai.py: ask_agent()
         → ai/graph/agent_graph.get_agent_app()
            → LangGraph(StateGraph)
               → agent_node() 에서 mock_search_tool() 호출
                  → ai/tools/search/web_search.web_search() (예시 툴)
         ← state {"question","answer"}
      ← {"result": ...}

4) STT
   POST /api/v1/stt/transcribe (파일 업로드)
      → routes/stt.py: STTService.transcribe(data)  ← (여기에 Whisper/클라우드 STT 연결)
      ← {"text": ...}

5) TTS
   POST /api/v1/tts/synthesize
      → routes/tts.py: TTSService.synthesize(text)  ← (여기에 Azure/OPENAI TTS 연결)
      ← {"bytes": ...}



환경 설정(.env ↔ core/config.py)
.env 값이 core/config.py의 Settings로 로드되고, DB URI·경로·키가 여기서 생성됨.
변경 예) DB 포트 바꾸면 DB_PORT만 수정 → 재시작.

DB 연결(db/session.py)
config.db_uri로 SQLAlchemy 엔진 생성 → get_db()로 FastAPI DI에 주입.
모델은 db/models.py, 초기 테이블은 db/init_db.py로 생성.

LCEL 체인(ai/chains/lcel_chain.py)
현재는 모의 응답.
실제 RAG로 바꾸려면:

벡터화/색인: ai/vector/faiss_store.py → add()/save()

질문 임베딩 후 search() → 상위 K개 문서 → 체인 프롬프트에 컨텍스트로 전달.

에이전트(ai/graph/agent_graph.py)
mock_search_tool() 자리에 실제 툴 넣기.
새 툴은 ai/tools/<domain>/<tool>.py에 함수로 구현 → 노드에서 호출.

툴(ai/tools/... )
외부 API/검색/DB조회 등 “행동”을 캡슐화하는 자리.
I/O 타입, 예외 처리, 로깅을 이 레벨에서 표준화.

FAISS(ai/vector/faiss_store.py)
로컬 벡터 인덱스 파일 관리.
임베딩 차원(dim)을 사용하는 모델에 맞춰 조정(예: BGE-m3-ko=1024).

STT/ TTS(backend/services)
서비스 어댑터. 공급자 SDK 코드/토큰/옵션은 여기서 관리.
엔드포인트는 routes/stt.py, routes/tts.py가 thin wrapper로 호출.

도커(DB만)와 앱의 연결
docker-compose.yml   ← Postgres(pgvector) 실행
        │
        └── .env 의 DB_HOST/PORT/NAME/USER/PASSWORD
                 ↓
backend/core/config.py (Settings.db_uri)
                 ↓
backend/db/session.py (SQLAlchemy 엔진/세션)


DB 컨테이너는 5433:5432로 포트 매핑. 로컬 앱은 .env의 DB_PORT=5433로 접속.

pgvector 확장은 docker/db/init.sql에서 활성화.

최소 호출 예

LCEL 체인
POST /api/v1/ai/ask

{ "question": "사례 기반 답변 준비해줘" }


→ ai/chains/lcel_chain.py의 _answer_fn()이 실행

에이전트(툴 호출)
POST /api/v1/ai/agent

{ "question": "웹검색 통해 한 줄 요약" }


→ agent_node() → mock_search_tool() → (툴 교체 지점)

네가 자주 보게 될 파일만 딱 집어서

엔드포인트 뼈대: backend/api/v1/routes/*.py

비즈 로직(간단 체인): backend/ai/chains/lcel_chain.py

에이전트/툴 콜: backend/ai/graph/agent_graph.py + backend/ai/tools/...

벡터 스토어: backend/ai/vector/faiss_store.py

DB 세팅: backend/core/config.py, backend/db/session.py

실행 순서(초단계)

docker compose up -d (DB 준비)

pip install -r requirements.txt

cp .env.example .env 값 채우기

python backend/db/init_db.py (테이블 생성)

uvicorn backend.app.main:app --reload --port 8000