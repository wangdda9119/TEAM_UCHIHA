
from loguru import logger

class TTSService:
    """Placeholder TTS. Replace with provider-specific SDK."""
    def synthesize(self, text: str) -> bytes:
        logger.debug("TTSService.synthesize called: '%s'", text)
        # TODO: Plug real TTS
        return b"FAKEAUDIOBYTES"
