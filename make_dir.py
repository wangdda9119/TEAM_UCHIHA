#!/usr/bin/env python3
"""
Project scaffold generator for:
- FastAPI backend
- Postgres (docker-compose, pgvector extension ready)
- LangChain (LCEL) + LangGraph agent pipeline
- FAISS local vector store
- STT/TTS service interfaces
- PEP8-friendly layout with logging, concise code, and comments
- Git ignore & .env templates
"""

from pathlib import Path
import textwrap

ROOT = Path(".").resolve()

FILES = {
    # ------------------------------
    # Top-level project files
    # ------------------------------
    ".gitignore": textwrap.dedent(
        """
        # Python
        __pycache__/
        *.pyc
        .pytest_cache/
        .mypy_cache/
        .ruff_cache/
        .venv/
        venv/
        .env
        .env.*.local
        .DS_Store

        # Editor/OS
        .idea/
        .vscode/
        Thumbs.db

        # Logs & data
        logs/
        data/
        vectorstore/
        uploads/

        # Node (in case you add FE later)
        node_modules/
        dist/

        # Docker
        *.pid
        .docker/
        """
    ),
    ".env.example": textwrap.dedent(
        """
        # ---- Application ----
        APP_NAME=ai-webapp
        APP_ENV=dev
        APP_HOST=0.0.0.0
        APP_PORT=8000
        LOG_LEVEL=INFO

        # ---- Security ----
        SECRET_KEY=change-this-in-production

        # ---- Database (docker compose uses POSTGRES_*) ----
        DB_HOST=localhost
        DB_PORT=5433
        DB_NAME=aiapp
        DB_USER=aiuser
        DB_PASSWORD=aiuserpw

        # ---- AI Providers ----
        OPENAI_API_KEY=sk-xxxxx

        # ---- Paths ----
        VECTOR_DIR=vectorstore
        UPLOAD_DIR=uploads
        """
    ),
    "README.md": textwrap.dedent(
        """
        # AI Web App Skeleton (FastAPI + Postgres + LangChain/LangGraph + FAISS)

        ## Quickstart
        ```bash
        cp .env.example .env
        docker compose up -d
        pip install -r requirements.txt
        uvicorn backend.app.main:app --reload --port 8000
        ```

        ## Endpoints
        - `GET  /health` : health check
        - `POST /api/v1/ai/ask` : LCEL chain (simple RAG-ready)
        - `POST /api/v1/ai/agent` : LangGraph agent (mock tool)
        - `POST /api/v1/stt/transcribe` : STT interface (placeholder)
        - `POST /api/v1/tts/synthesize` : TTS interface (placeholder)
        """
    ),
    "requirements.txt": textwrap.dedent(
        """
        fastapi>=0.115
        uvicorn[standard]>=0.30
        pydantic>=2.9
        pydantic-settings>=2.6
        SQLAlchemy>=2.0
        psycopg[binary,pool]>=3.2
        alembic>=1.13

        python-dotenv>=1.0
        loguru>=0.7
        numpy>=2.1

        # AI stack
        langchain>=0.3.9
        langgraph>=0.2.39
        faiss-cpu>=1.8.0
        openai>=1.51

        # Optional: file parsing later
        python-multipart>=0.0.9
        """
    ),
    "docker-compose.yml": textwrap.dedent(
        """
        services:
          db:
            image: ankane/pgvector:latest
            container_name: ai_pgvector
            environment:
              POSTGRES_USER: aiuser
              POSTGRES_PASSWORD: aiuserpw
              POSTGRES_DB: aiapp
            ports:
              - "5433:5432"
            volumes:
              - db_data:/var/lib/postgresql/data
              - ./docker/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
            healthcheck:
              test: ["CMD-SHELL", "pg_isready -U aiuser -d aiapp"]
              interval: 5s
              timeout: 5s
              retries: 10
        volumes:
          db_data:
        """
    ),
    "docker/db/init.sql": textwrap.dedent(
        """
        -- Enable pgvector (already present in image, ensure extension)
        CREATE EXTENSION IF NOT EXISTS vector;
        """
    ),

    # ------------------------------
    # Backend package
    # ------------------------------
    "backend/app/__init__.py": "",
    "backend/app/main.py": textwrap.dedent(
        """
        from fastapi import FastAPI
        from backend.core.config import settings
        from backend.core.logging import setup_logging
        from backend.api.v1.router import api_router

        app = FastAPI(title=settings.app_name)

        setup_logging()

        @app.get("/health")
        def health():
            return {"status": "ok", "env": settings.app_env}

        app.include_router(api_router, prefix="/api/v1")
        """
    ),

    "backend/core/__init__.py": "",
    "backend/core/config.py": textwrap.dedent(
        """
        from pydantic_settings import BaseSettings, SettingsConfigDict

        class Settings(BaseSettings):
            app_name: str = "ai-webapp"
            app_env: str = "dev"
            app_host: str = "0.0.0.0"
            app_port: int = 8000
            log_level: str = "INFO"

            secret_key: str = "change-this-in-production"

            db_host: str = "localhost"
            db_port: int = 5433
            db_name: str = "aiapp"
            db_user: str = "aiuser"
            db_password: str = "aiuserpw"

            openai_api_key: str | None = None

            vector_dir: str = "vectorstore"
            upload_dir: str = "uploads"

            model_config = SettingsConfigDict(env_file=".env", extra="ignore")

            @property
            def db_uri(self) -> str:
                return (
                    f"postgresql+psycopg://{self.db_user}:{self.db_password}"
                    f"@{self.db_host}:{self.db_port}/{self.db_name}"
                )

        settings = Settings()
        """
    ),
    "backend/core/logging.py": textwrap.dedent(
        """
        from loguru import logger
        from backend.core.config import settings
        from pathlib import Path

        def setup_logging() -> None:
            # Simple, rotating log file per environment; console by default.
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            logger.remove()
            logger.add(
                log_dir / f"{settings.app_env}.log",
                rotation="10 MB",
                retention="10 files",
                level=settings.log_level,
                enqueue=True,
            )
            logger.add(lambda msg: print(msg, end=""), level=settings.log_level)
        """
    ),

    # ------------------------------
    # DB Layer
    # ------------------------------
    "backend/db/__init__.py": "",
    "backend/db/session.py": textwrap.dedent(
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from backend.core.config import settings

        engine = create_engine(settings.db_uri, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        """
    ),
    "backend/db/models.py": textwrap.dedent(
        """
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        from sqlalchemy import Integer, String, DateTime, func

        class Base(DeclarativeBase):
            pass

        class Document(Base):
            __tablename__ = "documents"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
            created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
        """
    ),
    "backend/db/init_db.py": textwrap.dedent(
        """
        from backend.db.session import engine
        from backend.db.models import Base

        def init_db() -> None:
            Base.metadata.create_all(bind=engine)

        if __name__ == "__main__":
            init_db()
        """
    ),

    # ------------------------------
    # API layer
    # ------------------------------
    "backend/api/__init__.py": "",
    "backend/api/v1/__init__.py": "",
    "backend/api/v1/router.py": textwrap.dedent(
        """
        from fastapi import APIRouter
        from backend.api.v1.routes import ai, stt, tts

        api_router = APIRouter()
        api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
        api_router.include_router(stt.router, prefix="/stt", tags=["STT"])
        api_router.include_router(tts.router, prefix="/tts", tags=["TTS"])
        """
    ),
    "backend/api/v1/routes/__init__.py": "",
    "backend/api/v1/routes/ai.py": textwrap.dedent(
        """
        from fastapi import APIRouter
        from pydantic import BaseModel
        from loguru import logger

        from backend.ai.chains.lcel_chain import get_simple_chain
        from backend.ai.graph.agent_graph import get_agent_app

        router = APIRouter()

        class AskIn(BaseModel):
            question: str

        @router.post("/ask")
        def ask_lcel(inp: AskIn):
            \"\"\"Minimal LCEL chain example. Plug retriever/FAISS later.\"\"\"
            chain = get_simple_chain()
            logger.info("LCEL /ask called")
            answer = chain.invoke({"input": inp.question})
            return {"answer": answer}

        @router.post("/agent")
        def ask_agent(inp: AskIn):
            \"\"\"Minimal LangGraph agent with a mock tool.\"\"\"
            app = get_agent_app()
            logger.info("LangGraph /agent called")
            out = app.invoke({"question": inp.question})
            return {"result": out}
        """
    ),
    "backend/api/v1/routes/stt.py": textwrap.dedent(
        """
        from fastapi import APIRouter, UploadFile, File
        from pydantic import BaseModel
        from loguru import logger
        from backend.services.stt import STTService

        router = APIRouter()
        stt_service = STTService()

        class STTOut(BaseModel):
            text: str

        @router.post("/transcribe", response_model=STTOut)
        async def transcribe(file: UploadFile = File(...)):
            \"\"\"Placeholder STT endpoint: returns mock transcription.\"\"\"
            logger.info("STT /transcribe called")
            data = await file.read()
            text = stt_service.transcribe(data)
            return STTOut(text=text)
        """
    ),
    "backend/api/v1/routes/tts.py": textwrap.dedent(
        """
        from fastapi import APIRouter
        from pydantic import BaseModel
        from loguru import logger
        from backend.services.tts import TTSService

        router = APIRouter()
        tts_service = TTSService()

        class TTSIn(BaseModel):
            text: str

        @router.post("/synthesize")
        def synthesize(inp: TTSIn):
            \"\"\"Placeholder TTS endpoint: returns bytes length as a mock.\"\"\"
            logger.info("TTS /synthesize called")
            audio = tts_service.synthesize(inp.text)
            return {"bytes": len(audio)}
        """
    ),

    # ------------------------------
    # AI Layer
    # ------------------------------
    "backend/ai/__init__.py": "",
    "backend/ai/chains/__init__.py": "",
    "backend/ai/chains/lcel_chain.py": textwrap.dedent(
        '''
        """
        LCEL minimal chain. Extend with retriever (FAISS) later:
        - Build FAISS index in backend/ai/vector/faiss_store.py
        - Wire retriever into LCEL chain with `RunnableParallel` etc.
        """
        from langchain_core.runnables import RunnableLambda
        from loguru import logger

        def _answer_fn(inp: dict) -> str:
            question: str = inp.get("input", "")
            logger.debug("LCEL chain received: %s", question)
            return f"[LCEL] You asked: {question}"

        def get_simple_chain():
            return RunnableLambda(_answer_fn)
        '''
    ),
    "backend/ai/graph/__init__.py": "",
    "backend/ai/graph/agent_graph.py": textwrap.dedent(
        '''
        """
        Minimal LangGraph agent:
        - State: {"question": str, "answer": str}
        - Tool: mock_search
        """
        from typing import TypedDict
        from langgraph.graph import StateGraph, END
        from loguru import logger

        class AgentState(TypedDict):
            question: str
            answer: str

        def mock_search_tool(query: str) -> str:
            # Replace with real tools in backend/ai/tools/*
            return f"[search] top result for '{query}'"

        def agent_node(state: AgentState) -> AgentState:
            q = state["question"]
            logger.debug("Agent node handling question: %s", q)
            res = mock_search_tool(q)
            return {"question": q, "answer": f"Agent says: {res}"}

        def get_agent_app():
            graph = StateGraph(AgentState)
            graph.add_node("agent", agent_node)
            graph.set_entry_point("agent")
            graph.add_edge("agent", END)
            return graph.compile()
        '''
    ),
    "backend/ai/tools/__init__.py": "",
    "backend/ai/tools/search/__init__.py": "",
    "backend/ai/tools/search/web_search.py": textwrap.dedent(
        '''
        """
        Example tool module structure under ai/tools/.
        Replace with real implementation (SerpAPI, Tavily, etc.)
        """
        from loguru import logger

        def web_search(query: str) -> list[str]:
            logger.debug("web_search called: %s", query)
            return [f"result for {query}"]
        '''
    ),
    "backend/ai/vector/__init__.py": "",
    "backend/ai/vector/faiss_store.py": textwrap.dedent(
        '''
        """
        Minimal FAISS index utility.
        Store path controlled by VECTOR_DIR (.env).
        """
        from pathlib import Path
        import numpy as np
        import faiss
        from backend.core.config import settings

        class SimpleFaissStore:
            def __init__(self, dim: int = 384, index_name: str = "faiss.index"):
                self.dim = dim
                self.index_path = Path(settings.vector_dir) / index_name
                self.index_path.parent.mkdir(parents=True, exist_ok=True)
                self.index = faiss.IndexFlatL2(self.dim)

            def add(self, vecs: np.ndarray):
                assert vecs.ndim == 2 and vecs.shape[1] == self.dim
                self.index.add(vecs.astype("float32"))

            def search(self, q: np.ndarray, k: int = 5):
                assert q.ndim == 2 and q.shape[1] == self.dim
                D, I = self.index.search(q.astype("float32"), k)
                return D, I

            def save(self):
                faiss.write_index(self.index, str(self.index_path))

            def load(self):
                if self.index_path.exists():
                    self.index = faiss.read_index(str(self.index_path))
        '''
    ),

    # ------------------------------
    # Services (STT/TTS)
    # ------------------------------
    "backend/services/__init__.py": "",
    "backend/services/stt.py": textwrap.dedent(
        """
        from loguru import logger

        class STTService:
            \"\"\"Placeholder STT. Replace with Whisper/OpenAI Realtime/etc.\"\"\"
            def transcribe(self, data: bytes) -> str:
                logger.debug("STTService.transcribe called (bytes=%d)", len(data))
                # TODO: Plug real STT
                return "[STT] (mock) This is a placeholder transcription."
        """
    ),
    "backend/services/tts.py": textwrap.dedent(
        """
        from loguru import logger

        class TTSService:
            \"\"\"Placeholder TTS. Replace with provider-specific SDK.\"\"\"
            def synthesize(self, text: str) -> bytes:
                logger.debug("TTSService.synthesize called: '%s'", text)
                # TODO: Plug real TTS
                return b"FAKEAUDIOBYTES"
        """
    ),

    # ------------------------------
    # Schemas (Pydantic)
    # ------------------------------
    "backend/schemas/__init__.py": "",

    # ------------------------------
    # Utils (upload dirs, etc.)
    # ------------------------------
    "uploads/.gitkeep": "",
    "vectorstore/.gitkeep": "",
    "logs/.gitkeep": "",
}

DIRS = [
    "docker/db",
    "backend/app",
    "backend/core",
    "backend/db",
    "backend/api/v1/routes",
    "backend/ai/chains",
    "backend/ai/graph",
    "backend/ai/tools/search",
    "backend/ai/vector",
    "backend/services",
    "backend/schemas",
    "uploads",
    "vectorstore",
    "logs",
]


def ensure_dirs():
    for d in DIRS:
        Path(d).mkdir(parents=True, exist_ok=True)


def write_files():
    for path, content in FILES.items():
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def main():
    ensure_dirs()
    write_files()
    print("✅ Project skeleton generated.")


if __name__ == "__main__":
    main()
