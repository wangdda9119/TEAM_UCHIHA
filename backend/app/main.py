
from fastapi import FastAPI
from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.api.v1.router import api_router

app = FastAPI(title=settings.app_name)

setup_logging()

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}

app.include_router(api_router, prefix="/api/v1")
