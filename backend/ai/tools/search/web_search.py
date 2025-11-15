from langchain_core.tools import tool
from tavily import TavilyClient
from backend.core.config import settings

@tool
def web_search(query: str) -> str:
    """Tavily 웹 검색 Tool"""

    if not settings.tavily_api_key:
        return "Tavily API 키 없음"

    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        res = client.search(query=query, max_results=3)

        out = []
        for r in res.get("results", []):
            out.append(
                f"제목: {r.get('title')}\n내용: {r.get('content')}\nURL: {r.get('url')}"
            )

        return "\n\n".join(out) if out else "검색 결과 없음"
    except Exception as e:
        return f"웹검색 오류: {e}"
