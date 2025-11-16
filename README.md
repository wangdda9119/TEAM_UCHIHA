루트
├─ docker-compose.yml            ← Postgres 도커로 실행
├─ .env                          ← 환경변수 (DB_HOST, OPENAI_API_KEY 등)
├─ LCEL_GUIDE.md                 ← LCEL 체인 상세 가이드
├─ STT_TTS_GUIDE.md              ← STT/TTS 음성 기능 가이드
└─ backend
   ├─ app/main.py                ← FastAPI 시작점(+ 라우터 등록)
   ├─ api/v1/router.py           ← /api/v1 하위 라우터 묶음
   │  ├─ routes/ai.py            ← /ai/* 엔드포인트
   │  ├─ routes/stt_tts.py       ← /speech/* 음성 엔드포인트
   │  └─ routes/lcel.py          ← /lcel/* LCEL 체인 엔드포인트
   ├─ core/config.py             ← .env 읽어서 설정 제공(DB URI 등)
   ├─ core/logging.py            ← loguru 로깅 설정
   ├─ core/env_setup.py          ← 환경 변수 초기화 (모듈화)
   ├─ db/session.py              ← SQLAlchemy 엔진/세션
   ├─ db/models.py               ← 데이터베이스 모델
   ├─ services/stt.py            ← OpenAI Whisper STT 서비스
   ├─ services/tts.py            ← OpenAI TTS 서비스
   ├─ ai/chains/lcel_chain.py    ← 모듈화된 LCEL 체인 (11개)
   ├─ ai/graph/agent_graph.py    ← LangGraph 에이전트
   ├─ ai/tools/search/web_search.py ← 검색 도구
   └─ ai/vector/faiss_store.py   ← FAISS 벡터 스토어


## 📡 API 엔드포인트

### 1. LCEL 체인 엔드포인트 (11개 체인)
```
POST /api/v1/lcel/qa              ← 질문-답변
POST /api/v1/lcel/summarize       ← 텍스트 요약
POST /api/v1/lcel/sentiment       ← 감정 분석
POST /api/v1/lcel/keywords        ← 키워드 추출
POST /api/v1/lcel/generate-questions ← 질문 생성
POST /api/v1/lcel/context-qa      ← 컨텍스트 기반 QA
POST /api/v1/lcel/analyze         ← 병렬 분석 (요약+감정+키워드)
POST /api/v1/lcel/verify          ← 사실성 검증
GET  /api/v1/lcel/chains          ← 사용 가능한 체인 목록
GET  /api/v1/lcel/health          ← 헬스 체크
```

### 2. STT/TTS 음성 엔드포인트
```
POST /api/v1/speech/transcribe    ← 음성 인식 (Whisper)
POST /api/v1/speech/synthesize    ← 음성 합성 (TTS)
GET  /api/v1/speech/health        ← 헬스 체크
```

### 3. 인증 엔드포인트
```
POST /api/v1/auth/register        ← 회원가입
POST /api/v1/auth/login           ← 로그인
POST /api/v1/auth/logout          ← 로그아웃
```

### 4. AI 에이전트 엔드포인트
```
POST /api/v1/ai/ask               ← LCEL 체인
POST /api/v1/ai/agent             ← LangGraph 에이전트
```
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

## 🔐 인증 시스템

### 사용자 역할
- **student**: 일반 학생 (AI 챗봇, PDF 학습 지원 이용 가능)
- **professor**: 교수 (모든 기능 + 과제 자동 채점 이용 가능)

### 테스트 계정
- 교수: `professor` / `prof123`
- 학생: `student` / `stud123`

## 🚀 실행 순서

1. **DB 준비**
   ```bash
   docker compose up -d
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **환경변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일에서 필요한 값들 설정
   ```

4. **데이터베이스 초기화**
   ```bash
   python backend/db/init_db.py
   python backend/db/create_test_users.py
   ```

5. **백엔드 서버 실행**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

6. **프론트엔드 실행**
   ```bash
   cd team_uchiha
   npm install
   npm run dev
   ```
