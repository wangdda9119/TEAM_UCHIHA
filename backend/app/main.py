
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 환경 변수 먼저 로드 (모든 임포트 전에)
from backend.core.env_setup import setup_environment
setup_environment()

from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.api.v1.router import api_router
from backend.ai.vector.rag_pipeline import RAGPipeline

app = FastAPI(title=settings.app_name)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",      # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_logging()

# 전역 RAG 파이프라인 초기화
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    global rag_pipeline
    try:
        rag_pipeline = RAGPipeline()
        print("✅ RAG Pipeline 전역 로드 완료")
    except Exception as e:
        print(f"⚠️ RAG Pipeline 로드 실패: {e}")
        rag_pipeline = None

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}

app.include_router(api_router, prefix="/api/v1")
