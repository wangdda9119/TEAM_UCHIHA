
import os
from openai import OpenAI
from loguru import logger
from io import BytesIO

class TTSService:
    """Text-to-Speech using OpenAI TTS"""
    
    def __init__(self):
        # 환경 변수에서 API 키 가져오기
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ OPENAI_API_KEY가 설정되지 않았습니다. "
                ".env 파일을 확인하세요."
            )
        
        self.client = OpenAI(api_key=api_key)
        self.model = "tts-1"  # Fast model, good for real-time
        self.voice = "alloy"  # Voice option: alloy, echo, fable, onyx, nova, shimmer
        logger.info("✅ TTSService initialized with TTS model")
    
    def synthesize(self, text: str, voice: str = None) -> bytes:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (optional, default: alloy)
        
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")
            
            if len(text) > 4096:
                logger.warning("Text truncated to 4096 chars (OpenAI limit)")
                text = text[:4096]
            
            logger.debug("TTSService.synthesize called: '%s...' (len=%d)", text[:50], len(text))
            
            selected_voice = voice or self.voice
            
            # Call OpenAI TTS API
            response = self.client.audio.speech.create(
                model=self.model,
                voice=selected_voice,
                input=text,
                response_format="mp3"
            )
            
            # Get audio bytes
            audio_bytes = response.content
            logger.info("TTS synthesis successful: %d bytes", len(audio_bytes))
            return audio_bytes
            
        except Exception as e:
            logger.error("TTS synthesis error: %s", str(e))
            raise Exception(f"Failed to synthesize speech: {str(e)}")
