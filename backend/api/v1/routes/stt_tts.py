"""
STT/TTS API Routes
Test endpoint for speech-to-text and text-to-speech functionality
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from loguru import logger

from backend.services.stt import STTService
from backend.services.tts import TTSService

router = APIRouter()
stt_service = STTService()
tts_service = TTSService()


class TextInput(BaseModel):
    """Text input for TTS"""
    text: str
    voice: str = "alloy"  # Optional voice selection


class TranscriptionResponse(BaseModel):
    """Response for STT"""
    text: str
    status: str = "success"


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file to text using OpenAI Whisper
    
    Args:
        file: Audio file (webm, mp3, wav, m4a, ogg, flac)
    
    Returns:
        Transcribed text
    """
    try:
        logger.info("Transcribe request received: %s (%s)", file.filename, file.content_type)
        
        # Validate file type
        if not file.content_type or "audio" not in file.content_type:
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file"
            )
        
        # Read file content
        audio_data = await file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Audio file is empty"
            )
        
        # Get file extension
        file_ext = file.filename.split(".")[-1].lower() if file.filename else "webm"
        
        # Transcribe
        transcribed_text = stt_service.transcribe(audio_data, format=file_ext)
        
        return TranscriptionResponse(text=transcribed_text)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Transcription error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/synthesize")
async def synthesize_speech(input_data: TextInput):
    """
    Convert text to speech using OpenAI TTS
    
    Args:
        input_data: Text and optional voice selection
    
    Returns:
        Audio file (mp3)
    """
    try:
        logger.info("Synthesize request received: %s", input_data.text[:50])
        
        if not input_data.text or len(input_data.text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        # Synthesize
        audio_bytes = tts_service.synthesize(
            input_data.text,
            voice=input_data.voice
        )
        
        return {
            "status": "success",
            "audio": audio_bytes.hex(),  # Convert bytes to hex string for JSON
            "format": "mp3",
            "text": input_data.text[:100]  # Return first 100 chars for verification
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Synthesis error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Synthesis failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "services": {
            "stt": "OpenAI Whisper",
            "tts": "OpenAI TTS"
        }
    }
