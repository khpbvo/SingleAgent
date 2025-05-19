"""Tools for the SearchAgent.

These tools follow the OpenAI Agents SDK specification and use
Pydantic v2 compatible models for the parameters.
"""

from typing import List
from urllib.parse import quote_plus

import requests
from pydantic import BaseModel, Field

from agents import function_tool, RunContextWrapper
from The_Agents.context_data import EnhancedContextData


class SearchQueryParams(BaseModel):
    """Parameters for searching the web."""

    query: str = Field(description="Query string to search for")
    max_results: int = Field(5, description="Maximum number of results to return")


class FetchResultParams(BaseModel):
    """Parameters for fetching a URL."""

    url: str = Field(description="URL to fetch")


@function_tool
async def search_internet(
    wrapper: RunContextWrapper[EnhancedContextData], params: SearchQueryParams
) -> str:
    """Search the internet using DuckDuckGo and return a list of results."""

    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(params.query)}&format=json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results: List[str] = []
        for topic in data.get("RelatedTopics", [])[: params.max_results]:
            if isinstance(topic, dict) and "Text" in topic and "FirstURL" in topic:
                results.append(f"{topic['Text']} - {topic['FirstURL']}")
        wrapper.context.track_entity(
            "search_query", params.query, {"results": len(results)}
        )
        return "\n".join(results) if results else "No results found."
    except Exception as e:  # pragma: no cover - network errors not tested
        return f"Error searching internet: {e}"


@function_tool
async def fetch_result(
    wrapper: RunContextWrapper[EnhancedContextData], params: FetchResultParams
) -> str:
    """Fetch the contents of a URL."""

    try:
        resp = requests.get(params.url, timeout=10)
        resp.raise_for_status()
        wrapper.context.track_entity(
            "url", params.url, {"status": resp.status_code}
        )
        return resp.text
    except Exception as e:  # pragma: no cover - network errors not tested
        return f"Error fetching URL: {e}"

