import requests
from urllib.parse import quote_plus
from typing import List
from pydantic import BaseModel, Field
from agents import function_tool, RunContextWrapper
from The_Agents.context_data import EnhancedContextData

class FetchUrlParams(BaseModel):
    """Parameters for fetching a URL."""
    url: str = Field(description="URL to fetch")

class SearchWebParams(BaseModel):
    """Parameters for searching the web."""
    query: str = Field(description="Search query")
    max_results: int = Field(description="Maximum number of results")

@function_tool
def fetch_url(wrapper: RunContextWrapper[EnhancedContextData], params: FetchUrlParams) -> str:
    """Fetch the contents of a URL."""
    try:
        resp = requests.get(params.url, timeout=10)
        resp.raise_for_status()
        wrapper.context.track_entity("url", params.url, {"status": resp.status_code})
        return resp.text
    except Exception as e:
        return f"Error fetching URL: {e}"

@function_tool
def search_web(wrapper: RunContextWrapper[EnhancedContextData], params: SearchWebParams) -> str:
    """Search the web using DuckDuckGo and return formatted results."""
    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(params.query)}&format=json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results: List[str] = []
        for topic in data.get("RelatedTopics", [])[: params.max_results]:
            if isinstance(topic, dict) and "Text" in topic and "FirstURL" in topic:
                results.append(f"{topic['Text']} - {topic['FirstURL']}")
        wrapper.context.track_entity("search_query", params.query, {"results": len(results)})
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Error searching web: {e}"
