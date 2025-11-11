
from loguru import logger
from backend.core.config import settings
from pathlib import Path

def setup_logging() -> None:
    # Simple, rotating log file per environment; console by default.
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger.remove()
    logger.add(
        log_dir / f"{settings.app_env}.log",
        rotation="10 MB",
        retention=10,
        level=settings.log_level,
        enqueue=True,
    )
    logger.add(lambda msg: print(msg, end=""), level=settings.log_level)
