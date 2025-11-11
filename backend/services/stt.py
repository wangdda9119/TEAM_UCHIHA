
from loguru import logger

class STTService:
    """Placeholder STT. Replace with Whisper/OpenAI Realtime/etc."""
    def transcribe(self, data: bytes) -> str:
        logger.debug("STTService.transcribe called (bytes=%d)", len(data))
        # TODO: Plug real STT
        return "[STT] (mock) This is a placeholder transcription."
