
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
    """Placeholder STT endpoint: returns mock transcription."""
    logger.info("STT /transcribe called")
    data = await file.read()
    text = stt_service.transcribe(data)
    return STTOut(text=text)
