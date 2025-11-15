# backend/aiTools.py

from backend.ai.tools.search.web_search import web_search
from backend.ai.tools.search.hyupsung_info import uhs_fetch_info
from backend.ai.tools.search.rag_search import rag_search

TOOL_LIST = [
    web_search,
    uhs_fetch_info,
    rag_search,
]
