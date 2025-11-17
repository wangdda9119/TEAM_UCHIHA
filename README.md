# TEAM_UCHIHA – 협성대학교 AI 캠퍼스 메이트 & 자동 채점 플랫폼

> 협성대학교 구성원을 위한 **올인원 AI 도우미 서비스**  
> 캠퍼스 정보 질의응답, 강의 PDF 분석, 대용량 과제 자동 채점, 음성 인터페이스까지 한 번에 제공하는 풀스택 웹 애플리케이션입니다.

---

## 🧭 프로그램 개요

**TEAM_UCHIHA**는 협성대학교 학생·교수·교직원을 대상으로 다음과 같은 기능을 제공하는 AI 기반 캠퍼스 어시스턴트입니다.

- 협성대 내부 자료 & 공식 홈페이지 & 웹검색을 결합한 **캠퍼스 Q&A 에이전트**
- 강의 PDF를 업로드하면 단원별 요약과 객관식 퀴즈를 생성하는 **학습 보조 도구**
- 수십 개의 과제를 ZIP으로 업로드하면 루브릭 기반으로 자동 채점하는 **대용량 과제 채점기**
- STT/TTS를 활용해 음성으로 질문하고 답변을 들을 수 있는 **음성 인터페이스**

백엔드는 **FastAPI + LangChain/LangGraph + PostgreSQL + Redis**,  
프론트엔드는 **Vue 3 + Vite**로 구성되어 있습니다.

---

## ✨ 주요 기능

### 1) 협성캠퍼스 메이트 – AI 캠퍼스 Q&A 에이전트

- 협성대 관련 PDF 문서 기반 **RAG(Vector DB)** 검색
- 협성대 공식 홈페이지(동아리, 식단, 등록금, 교환학생, 취업률 등) **실시간 AI 크롤링**
- Tavily 기반 일반 웹 검색 결합
- 장학금, 셔틀버스, 동아리, 학사일정 등 **캠퍼스 전반 질의응답**

### 2) 강의 PDF 분석 & 학습 지원

- 강의계획서/강의자료 PDF 업로드
- LLM 기반 **단원(챕터) 단위 자동 분리**
- 각 단원별 요약 생성
- 단원에 맞는 **객관식 퀴즈 세트 자동 생성**  
  (문항, 보기사항, 정답, 해설까지 포함한 JSON 구조)

### 3) 대용량 과제 ZIP 자동 채점

- 학생 과제 PDF들을 ZIP으로 업로드
- 파일명을 통해 학번/이름/과제명 등 메타데이터 추출
- 교수자가 입력한 **루브릭(채점 기준 JSON)** 을 기반으로:
  - 항목별 점수
  - 항목별 피드백
  - 총점
- 여러 PDF를 비동기/병렬로 처리 후,  
  **엑셀(xlsx) 파일로 결과 다운로드** 가능

### 4) STT/TTS 기반 음성 인터페이스

- OpenAI Whisper(STT) 기반 음성 → 텍스트 변환
- OpenAI TTS 기반 텍스트 → 음성 합성
- 향후:
  - 캠퍼스 에이전트와 결합해 **음성 대화형 캠퍼스 메이트**로 확장 가능

---

## 🧱 전체 구조 & 아키텍처

### 디렉터리 구조 개요

```bash
TEAM_UCHIHA/
├─ docker-compose.yml       # Postgres, Redis 컨테이너 정의
├─ docker/
│  └─ db/
│     └─ init.sql           # DB 초기화 스크립트(로그성 메시지 위주)
├─ .env.example             # 환경변수 예시
├─ requirements.txt         # Python 의존성
├─ backend/                 # FastAPI 백엔드
└─ team_uchiha/             # Vue 3 프론트엔드
```

### 기술 스택 요약

- **Backend**
  - FastAPI, Uvicorn
  - PostgreSQL, SQLAlchemy
  - Redis
  - LangChain, LangGraph
  - OpenAI API (Chat, Embeddings, Whisper, TTS)
  - Tavily Search API
  - FAISS(Vector DB), PyPDFLoader, pandas, openpyxl
  - Loguru, python-dotenv, BeautifulSoup4

- **Frontend**
  - Vue 3 (Composition API)
  - Vue Router
  - Axios
  - Vite 빌드 시스템

---

## 🚀 시작하기 (Getting Started)

### 1) 환경 변수 설정

`.env.example`을 복사해 `.env` 파일을 생성합니다.

```bash
cp .env.example .env
```

핵심 변수 예시:

```env
APP_ENV=dev
APP_PORT=8000

DB_HOST=localhost
DB_PORT=5434
DB_NAME=uchiha_db
DB_USER=uchiha_itachi
DB_PASSWORD=sharingan

OPENAI_API_KEY=sk-...
TAVILY_API_KEY=...

VECTOR_DIR=vectorstore
UPLOAD_DIR=uploads
```

### 2) Docker로 DB & Redis 실행

```bash
docker-compose up -d
```

- PostgreSQL: `localhost:5434`
- Redis: `localhost:6379`

### 3) Python 의존성 설치

```bash
python -m venv venv
# Windows PowerShell 기준
venv\\Scripts\\activate
pip install -r requirements.txt
```

### 4) DB 초기화 & 테스트 유저 생성

```bash
python -m backend.db.init_db
python -m backend.db.create_test_users
```

- 교수 계정: `professor / prof123`
- 학생 계정: `student / stud123`

### 5) RAG VectorStore 빌드 (선택)

```bash
python -m backend.ai.vector.faiss_store
```

- `backend/ai/vector/pdfs/`에 협성대 관련 PDF를 넣어두면  
  `vectorstore/` 디렉터리에 FAISS 인덱스가 생성됩니다.

### 6) FastAPI 서버 실행

```bash
uvicorn backend.app.main:app --reload
```

- API 기본 URL: `http://localhost:8000`
- 헬스체크: `GET /health`

### 7) Vue 프론트엔드 실행

```bash
cd team_uchiha
npm install
npm run dev
```

- 기본 URL: `http://localhost:5173`

---

## 🔧 백엔드 구조 상세 설명

백엔드는 크게 다음 모듈로 구성되어 있습니다.

- `app` – FastAPI 엔트리포인트
- `core` – 설정, 로깅, 인증, Redis
- `db` – SQLAlchemy 모델 및 세션
- `ai` – Agent, RAG, Lecture Analyzer, Grading Pipeline, STT/TTS 등
- `api/v1` – 실제로 외부에서 호출하는 REST API 라우터 모음
- `services` – STT/TTS 서비스 클래스

### 1) `backend/app/main.py` – 진입점

- `.env` 로드 및 `Settings` 초기화
- `setup_logging()` 호출 → 로그 파일 및 콘솔 로깅 설정
- CORS 설정
  - `http://localhost:5173` 등 프론트 도메인 허용
- 앱 시작 시:
  - `RAGPipeline` 인스턴스를 전역으로 로딩
  - 로딩 실패 시 로그 출력, `None`으로 유지
- 라우터 등록:
  - `/health` – 서버 상태 확인
  - `/api/v1` – 버전 1 API 라우터 묶음

### 2) `backend/core` – 공통 인프라

#### `env_setup.py`

- 다양한 실행 경로를 고려해 프로젝트 루트 기준으로 `.env` 탐색
- `python-dotenv`로 자동 로딩
- `OPENAI_API_KEY` 존재 여부를 로그로 남겨 설정 문제를 빠르게 파악 가능

#### `config.py`

- `Settings(BaseSettings)`를 통해 환경변수 -> 설정 객체 변환
- 주요 필드:
  - DB 접속 정보
  - OpenAI/Tavily API 키
  - 벡터 스토어/업로드 디렉터리 경로
- `db_uri` 프로퍼티를 제공하여 SQLAlchemy Engine 생성 시 사용

#### `logging.py`

- `logs/{env}.log` 에 로그 파일 기록
- 파일 핸들러 + 콘솔 핸들러
- 환경변수 `LOG_LEVEL`에 따라 로깅 레벨 조정

#### `auth.py`

- 비밀번호 해시/검증
  - `passlib` 기반 `pbkdf2_sha256`
- JWT 발급/검증
  - `create_access_token`, `create_refresh_token`
  - Access Token: 기본 30분
  - Refresh Token: 기본 7일
- Redis 연동으로 토큰 상태 관리
  - `store_tokens_in_redis`, `get_token_from_redis`, `delete_tokens_from_redis`

#### `redis_client.py`

- 앱 전체에서 공유할 수 있는 Redis 클라이언트 제공
- `redis.Redis(host, port, db)` 인스턴스 생성
- `get_redis_client()` 헬퍼 함수 제공

### 3) `backend/db` – 데이터베이스 계층

#### `models.py`

- `User` 모델
  - `username`, `email`, `password_hash`, `role`, `is_verified` 등
- `Professor`, `Student`
- `Document` 등 학사/사용자 관련 모델 정의

#### `session.py`

- `create_engine(settings.db_uri)`
- `SessionLocal = sessionmaker(...)`
- FastAPI DI용 `get_db()` 의존성 제공

#### `init_db.py` / `create_test_users.py`

- `init_db.py` → `Base.metadata.create_all` 로 테이블 생성
- `create_test_users.py` → 교수/학생 테스트 계정 삽입

---

## 🧠 AI Agent & RAG 구조

### 1) Agent State & System Prompt

#### `ai/agent/state.py`

- `AgentState(TypedDict)` 정의
  - `messages: List[BaseMessage]` 한 필드를 중심으로 LangGraph 상태 관리

#### `ai/agent/prompts/system_prompt.py`

- 협성대학교 구성원을 돕는 **“협성캠퍼스 메이트”** 에이전트 역할 정의
- 우선순위:
  1. 로컬 RAG 문서
  2. 협성대 공식 홈페이지
  3. 일반 웹 검색
- 학사일정, 장학금, 교환학생, 취업, 동아리 등 카테고리별 답변 전략 포함

### 2) LangGraph 기반 ReAct Agent

#### `ai/agent/react_agent.py`

- `ChatOpenAI`를 이용해 LLM 초기화
- `StateGraph(AgentState)` 로 그래프 생성
  - LLM 노드: 시스템 프롬프트 + 히스토리 + 유저 메시지를 묶어 호출
  - Tool 노드: LLM 응답 내 tool_calls를 분석해 실제 Tool 함수 호출
- 그래프 구동:
  - LLM → (tool 필요 여부 판단) → tool 노드 → 다시 LLM → 종료
- `run_react_agent(question, session_id, language="ko")`
  - 세션별 메모리에서 히스토리 로드
  - LangGraph 워크플로우 한 번 실행
  - 최종 답변과 히스토리를 `chat_memory`에 다시 저장

### 3) Tools – 검색 기능

#### `ai/aiTools.py`

- 에이전트에서 사용할 Tool 목록을 한 곳에 모읍니다.
  - `web_search`, `uhs_fetch_info`, `rag_search`

#### `ai/tools/search/web_search.py`

- Tavily Search를 사용하는 웹 검색 Tool
- 쿼리를 입력받아 상위 N개 결과를 요약한 문자열을 반환
- 일반적인 정보 질의 시 사용

#### `ai/tools/search/hyupsung_info.py`

- 협성대 전용 크롤러 Tool
- 키워드에 따라 적절한 URL을 매핑
  - 동아리, 학생식단, 교직원식단, 등록금, 교환학생, 취업률 등
- `requests` + `BeautifulSoup4`로 HTML을 가져와 필요한 텍스트를 추출
- 에이전트가 이해하기 쉽도록 가공된 문자열을 반환

#### `ai/tools/search/rag_search.py`

- 전역 RAGPipeline 인스턴스를 불러와 `answer(query)` 수행
- 내부 문서 기반 검색에 최우선 사용
- “협성대 내부 자료 + 강의자료” 관련 질문에서 핵심 역할

---

## 📚 RAG(Vector DB) 파이프라인

### 1) 벡터 스토어 빌더 – `ai/vector/faiss_store.py`

- `FaissStoreBuilder` 클래스
  - PDF 로더:
    - `PyPDFLoader`로 `ai/vector/pdfs/` 디렉터리의 PDF들을 로딩
  - 텍스트 청킹:
    - `RecursiveCharacterTextSplitter`
  - 임베딩 생성:
    - `OpenAIEmbeddings`
  - VectorStore 생성:
    - `FAISS.from_texts(chunks, embeddings)`
  - 저장:
    - `vectorstore/index.faiss`
    - `vectorstore/metadata.pkl`

### 2) RAG 파이프라인 – `ai/vector/rag_pipeline.py`

- `RAGPipeline` 클래스
  - 초기화:
    - `vectorstore/`에서 FAISS 인덱스 + 메타데이터 로딩
    - `ChatOpenAI` LLM 인스턴스 준비
  - `search(query, top_k=5)`
    - `similarity_search`로 상위 문서 조회
    - 결과를 로그로 출력하여 디버깅에 활용
  - `answer(query)`
    - `search()` 결과를 컨텍스트로 묶어 LLM에 전달
    - 내부 문서 기반으로 답변을 구성해 한글로 반환

---

## 📝 강의 PDF 분석 파이프라인

### `ai/lecture/lecture_pipeline.py`

- `LectureProcessor(pdf_path)`
  - 생성자:
    - PDF 존재 여부 검증
    - `ChatOpenAI` 초기화
  - `load_pdf()`
    - `PyPDFLoader`로 PDF를 로딩해 전체 텍스트를 하나의 문자열로 반환
  - `split_chapters(text)`
    - LLM에게 “의미 단위의 단원(챕터)로 나누고, 각 단원별 요약을 JSON으로 만들어 달라”는 프롬프트 전달
    - 응답을 파싱하여:
      ```json
      {
        "chapters": [
          {
            "title": "1장 서론",
            "summary": "..."
          },
          ...
        ]
      }
      ```
      형태로 반환
  - `generate_questions(chapters)`
    - 단원별 요약을 입력으로 객관식 문제 세트를 생성
    - 각 단원별로 문제/보기/정답/해설을 포함한 구조를 반환

### 라우터

- `ai/lecture/routes.py` 및 `api/v1/routes/lecture.py`에서 사용
  - `/api/v1/lecture/upload`
    - 업로드된 PDF를 서버에 저장 후 LectureProcessor로 분석
    - 분석 결과를 Redis에 세션 단위로 저장
  - `/api/v1/lecture/summary/{session_id}`
    - 세션에 저장된 분석 결과를 가져와 프론트에 반환

---

## 🎓 과제 ZIP 자동 채점 파이프라인

### `ai/grading/grading_pipeline.py`

- `GradingPipeline`
  - LLM: `gpt-4o-mini` (temperature 0.1)
  - ZIP 처리:
    - 업로드된 ZIP을 임시 폴더에 압축 해제
    - PDF 파일 목록을 추출하고, 파일명에서 학번/이름/과제명 등의 정보 파싱
  - PDF 로딩:
    - `PyPDFLoader`로 각 PDF 텍스트 추출
  - 루브릭 기반 채점:
    - 교수자가 정의한 루브릭(JSON)을 바탕으로 LLM 프롬프트 구성
    - 항목별 점수, 총점, 피드백을 JSON으로 생성
  - 비동기/병렬 처리:
    - `asyncio` + `ThreadPoolExecutor`로 여러 과제를 동시에 채점
  - 결과 집계:
    - `pandas.DataFrame`으로 전체 결과 구성
    - `to_excel()`로 엑셀 파일 생성 후 다운로드용 경로 반환

### 라우터 – `api/v1/routes/grading.py`

- `/api/v1/grading/upload-assignments` (POST)
  - ZIP 파일 업로드 → 서버의 임시 디렉터리에 저장
  - `session_id`를 발급하고 Redis에 ZIP 위치 저장
- `/api/v1/grading/grade/{session_id}` (POST)
  - 루브릭(JSON or Form)을 받아 GradingPipeline 실행
  - 진행 상황/상태를 Redis에 기록
- `/api/v1/grading/result/{session_id}` (GET)
  - 현재 채점 진행 상태 및 중간 결과 조회
- `/api/v1/grading/download-excel/{session_id}` (GET)
  - 최종 채점 결과를 담은 엑셀 파일 다운로드
- `/api/v1/grading/cleanup/{session_id}` (DELETE)
  - 임시 ZIP/폴더 및 Redis 키 정리

---

## 🔊 STT/TTS 서비스 구조

### `services/stt.py`

- `STTService`
  - OpenAI API 클라이언트 초기화
  - `transcribe(audio_bytes, format)`
    - 업로드된 오디오 바이트를 Whisper 모델에 전달
    - 텍스트를 반환

### `services/tts.py`

- `TTSService`
  - OpenAI 음성 합성 모델 설정
  - `synthesize(text, voice=None)`
    - 입력 텍스트를 음성으로 변환 후 바이트 형태로 반환

### STT/TTS 라우터 – `api/v1/routes/stt_tts.py`

- `/api/v1/stt-tts/transcribe` (POST)
  - 파일 업로드 → STTService 호출 → 텍스트 반환
- `/api/v1/stt-tts/synthesize` (POST)
  - 텍스트 입력 → TTSService 호출 → 오디오 데이터 반환
- `/api/v1/stt-tts/health` (GET)
  - STT/TTS 모듈 상태 확인용 엔드포인트

---

## 🧑‍🏫 인증 & 사용자 관리

### `api/v1/routes/auth.py`

- `/api/v1/auth/register` (POST)
  - `username`, `email`, `password`, `role(student/professor)` 등록
- `/api/v1/auth/login` (POST)
  - 사용자 검증 후 Access/Refresh Token 발급
  - Redis에 토큰 저장
- `/api/v1/auth/verify` (GET)
  - 토큰 유효성 확인
- `/api/v1/auth/logout` (POST)
  - Redis에서 토큰 삭제

---

## 💻 프론트엔드 구조 상세 설명

### 1) 진입점 – `team_uchiha/src/main.js`

- Vue 앱 생성
- Axios 기본 설정:
  - `axios.defaults.baseURL = 'http://localhost:8000'`
- `app.config.globalProperties.$http = axios`

### 2) 라우터 – `team_uchiha/src/router/index.js`

- 주요 페이지:
  - `/` → `HomePage`
  - `/dashboard` → `Dashboard`
  - `/lecture` → `LectureAnalyzer`
  - `/agent` → `AgentInterface`
  - `/grading` → `AssignmentGrader`
- 라우트 가드:
  - `requireAuth` – access_token 존재 여부 확인
  - `requireProfessor` – `user_role === 'professor'` 확인

### 3) 주요 컴포넌트

#### `HomePage.vue`

- 서비스 소개 섹션
- 로그인/회원가입 모달
- `/api/v1/auth/login`, `/api/v1/auth/register`와 연동

#### `Dashboard.vue`

- 로그인 유저 정보 표시
- 역할(학생/교수)에 따라 다른 기능 카드 노출
- 최근 작업/진행중 세션 요약

#### `LectureAnalyzer.vue`

- PDF 업로드 UI
- `/api/v1/lecture/upload`, `/api/v1/lecture/summary/{session_id}` 호출
- 단원/요약/퀴즈를 아코디언/카드 형태로 렌더링

#### `AgentInterface.vue`

- 텍스트 기반 채팅 인터페이스
- `/api/v1/agent/...` 엔드포인트에 요청
- 세션 ID 기반으로 연속 대화 유지 가능

#### `AssignmentGrader.vue`

- ZIP 업로드
- 루브릭 입력 폼
- 채점 상태 모니터링 및 엑셀 다운로드 UI
- `/api/v1/grading/*` 전체 흐름과 연동

---

## 🧩 확장 아이디어

- RAG 문서에 **학사 공지, 교육과정, 장학 규정** 등 더 풍부한 문서 추가
- 에이전트에 **역할별 모드(신입생 모드, 교수 모드, 교환학생 모드)** 적용
- 과제 채점 파이프라인에:
  - 코드 과제 정적 분석
  - 표절 탐지
  - 보고서 구조/논리성에 대한 추가 피드백
- STT/TTS와 Agent를 결합한 **완전한 음성 기반 캠퍼스 메이트** 구현

---

## ✅ 요약

이 레포지토리는 단순한 챗봇이 아니라,  
**“캠퍼스 정보 + 강의 학습 + 과제 평가 + 음성 인터페이스”**를 한 번에 제공하는  
실전형 AI 서비스 아키텍처를 포함하고 있습니다.

- 백엔드: FastAPI + LangGraph를 중심으로 한 모듈화된 AI 파이프라인
- 프론트엔드: Vue 3 기반 SPA로 학생/교수 경험을 분리 설계
- 데이터: PostgreSQL, FAISS, Redis를 활용한 영속성/캐시/검색 구조

실제 운영 환경에 맞게 API 키, DB 설정, 보안/권한 설정만 정교하게 다듬으면  
곧바로 실사용 가능한 수준의 캠퍼스 AI 플랫폼으로 확장할 수 있습니다.
