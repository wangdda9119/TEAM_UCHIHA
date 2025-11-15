# backend/api/v1/routes/agent.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from loguru import logger

from backend.ai.agent.react_agent import run_react_agent, TOOLS

router = APIRouter()

class AgentRequest(BaseModel):
    question: str
    session_id: str = Field(default="default_session")
    language: str = Field(default="ko")


class AgentResponse(BaseModel):
    question: str
    answer: str
    status: str
    session_id: str


@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    try:
        logger.info(f"🤖 Agent 질문: {request.question}")

        if not request.question.strip():
            raise HTTPException(status_code=400, detail="질문이 비어 있습니다")

        answer = await run_react_agent(
            request.question,
            request.session_id,
            request.language
        )

        return AgentResponse(
            question=request.question,
            answer=answer,
            session_id=request.session_id,
            status="success"
        )

    except Exception as e:
        logger.error(f"❌ Agent 실행 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/tools")
async def get_tools():
    return {"tools": ["web_search", "uhs_fetch_info", "rag_search"]}


@router.get("/health") 
async def health_check():
    return {"status": "ok"}
