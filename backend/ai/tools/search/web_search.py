
"""
Example tool module structure under ai/tools/.
Replace with real implementation (SerpAPI, Tavily, etc.)
"""
from loguru import logger

def web_search(query: str) -> list[str]:
    logger.debug("web_search called: %s", query)
    return [f"result for {query}"]
