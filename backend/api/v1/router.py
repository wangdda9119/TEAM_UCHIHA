from fastapi import APIRouter

# 라우트 모듈 임포트
from backend.api.v1.routes import ai, stt_tts, agent

api_router = APIRouter()

# AI 기본 기능(API)
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])

# STT/TTS 엔드포인트
api_router.include_router(stt_tts.router, prefix="/stt-tts", tags=["STT-TTS"])

# 🟩 Agent 엔드포인트 — 이게 있어야 함!
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
