import requests
from pydantic import BaseModel, Field
from agents import function_tool, RunContextWrapper, WebSearchTool
from The_Agents.context_data import EnhancedContextData

class FetchUrlParams(BaseModel):
    """Parameters for fetching a URL."""
    url: str = Field(description="URL to fetch")


# Expose the built-in web search tool from the Agents SDK
search_web = WebSearchTool()

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

