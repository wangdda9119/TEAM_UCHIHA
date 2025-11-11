
from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger

from backend.ai.chains.lcel_chain import get_simple_chain
from backend.ai.graph.agent_graph import get_agent_app

router = APIRouter()

class AskIn(BaseModel):
    question: str

@router.post("/ask")
def ask_lcel(inp: AskIn):
    """Minimal LCEL chain example. Plug retriever/FAISS later."""
    chain = get_simple_chain()
    logger.info("LCEL /ask called")
    answer = chain.invoke({"input": inp.question})
    return {"answer": answer}

@router.post("/agent")
def ask_agent(inp: AskIn):
    """Minimal LangGraph agent with a mock tool."""
    app = get_agent_app()
    logger.info("LangGraph /agent called")
    out = app.invoke({"question": inp.question})
    return {"result": out}
