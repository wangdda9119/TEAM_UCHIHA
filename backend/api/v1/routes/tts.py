
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
    """Placeholder TTS endpoint: returns bytes length as a mock."""
    logger.info("TTS /synthesize called")
    audio = tts_service.synthesize(inp.text)
    return {"bytes": len(audio)}
