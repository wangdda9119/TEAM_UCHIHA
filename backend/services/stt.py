
import io
import os
from openai import OpenAI
from loguru import logger

class STTService:
    """Speech-to-Text using OpenAI Whisper (lightweight model)"""
    
    def __init__(self):
        # 환경 변수에서 API 키 가져오기
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ OPENAI_API_KEY가 설정되지 않았습니다. "
                ".env 파일을 확인하세요."
            )
        
        self.client = OpenAI(api_key=api_key)
        self.model = "whisper-1"
        logger.info("✅ STTService initialized with Whisper model")
    
    def transcribe(self, audio_data: bytes, format: str = "webm") -> str:
        """
        Transcribe audio to text using OpenAI Whisper
        
        Args:
            audio_data: Raw audio bytes from frontend
            format: Audio format (webm, mp3, wav, etc.)
        
        Returns:
            Transcribed text
        """
        try:
            logger.debug("STTService.transcribe called (bytes=%d, format=%s)", len(audio_data), format)
            
            # Create file-like object for OpenAI API
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{format}"
            
            # Call OpenAI Whisper API
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language="ko"  # Korean language
            )
            
            result = transcript.text
            logger.info("Transcription successful: %s", result)
            return result
            
        except Exception as e:
            logger.error("STT transcription error: %s", str(e))
            raise Exception(f"Failed to transcribe audio: {str(e)}")
