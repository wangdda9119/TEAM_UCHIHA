
from fastapi import APIRouter
from backend.api.v1.routes import ai, stt_tts, agent

api_router = APIRouter()
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(stt_tts.router, prefix="/speech", tags=["Speech"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
