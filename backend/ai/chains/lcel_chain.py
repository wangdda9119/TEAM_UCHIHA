
"""
LCEL minimal chain. Extend with retriever (FAISS) later:
- Build FAISS index in backend/ai/vector/faiss_store.py
- Wire retriever into LCEL chain with `RunnableParallel` etc.
"""
from langchain_core.runnables import RunnableLambda
from loguru import logger

def _answer_fn(inp: dict) -> str:
    question: str = inp.get("input", "")
    logger.debug("LCEL chain received: %s", question)
    return f"[LCEL] You asked: {question}"

def get_simple_chain():
    return RunnableLambda(_answer_fn)
