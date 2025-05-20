class MCPServerBase:
    """Minimal stub for MCP server."""
    def __init__(self, *, cache_tools_list=False):
        self.cache_tools_list = cache_tools_list
        self._tools_cache = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def list_tools(self):
        if self.cache_tools_list and self._tools_cache is not None:
            return self._tools_cache
        return []

    async def invalidate_tools_cache(self):
        self._tools_cache = None

    async def call_tool(self, name, *args, **kwargs):
        return None


class MCPServerStdio(MCPServerBase):
    def __init__(self, *, params=None, cache_tools_list=False):
        super().__init__(cache_tools_list=cache_tools_list)
        self.params = params or {}


class MCPServerSse(MCPServerBase):
    def __init__(self, *, url='', cache_tools_list=False):
        super().__init__(cache_tools_list=cache_tools_list)
        self.url = url

