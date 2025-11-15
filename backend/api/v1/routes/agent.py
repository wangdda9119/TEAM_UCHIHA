# backend/api/v1/routes/agent.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from loguru import logger

from langchain_core.messages import BaseMessage

from backend.ai.agent.react_agent import run_react_agent

router = APIRouter()

# ------------------------
# 세션별 메모리 저장
# ------------------------
SESSION_MEMORY: Dict[str, List[BaseMessage]] = {}

def get_memory(session_id: str) -> List[BaseMessage]:
    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = []
    return SESSION_MEMORY[session_id]


class AgentRequest(BaseModel):
    session_id: str = "default_user"
    question: str


class AgentResponse(BaseModel):
    question: str
    answer: str
    status: str


@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    try:
        logger.info(f"🤖 Agent 질문: {request.question}")

        memory = get_memory(request.session_id)

        answer = await run_react_agent(
            question=request.question,
            memory=memory
        )

        return AgentResponse(
            question=request.question,
            answer=answer,
            status="success"
        )

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))
