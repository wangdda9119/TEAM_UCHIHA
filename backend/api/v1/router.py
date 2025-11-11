
from fastapi import APIRouter
from backend.api.v1.routes import ai, stt, tts

api_router = APIRouter()
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(stt.router, prefix="/stt", tags=["STT"])
api_router.include_router(tts.router, prefix="/tts", tags=["TTS"])
