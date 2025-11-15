
from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger

router = APIRouter()

class AskIn(BaseModel):
    question: str

@router.post("/ask")
def ask_lcel(inp: AskIn):
    """Mock LCEL endpoint"""
    logger.info("LCEL /ask called")
    return {"answer": f"Mock response for: {inp.question}"}

@router.post("/agent")
def ask_agent(inp: AskIn):
    """Mock Agent endpoint"""
    logger.info("Agent /agent called")
    return {"answer": f"Mock agent response for: {inp.question}"}
