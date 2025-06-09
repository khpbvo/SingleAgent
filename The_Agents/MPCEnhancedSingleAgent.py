"""
Enhanced SingleAgent implementation with MCP (Model Context Protocol) support.
Integrates MCP servers alongside existing custom tools for maximum capability.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import asyncio
import os
import sys
import logging
import json
import re
import time
from logging.handlers import RotatingFileHandler

# MCP imports
from agents.mcp.server import MCPServerStdio, MCPServerSse

# Your existing imports
from agents import Agent, Runner, ItemHelpers, function_tool
from The_Agents.context_data import EnhancedContextData
from Tools.singleagent_tools import (
    run_ruff, run_pylint, run_pyright, run_command,
    read_file, create_colored_diff, apply_patch,
    change_dir, os_command, get_context,
    get_context_response, add_manual_context
)
from utilities.tool_usage import handle_stream_events
from utilities.project_info import discover_project_info

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
os.makedirs("logs", exist_ok=True)
mcp_handler = RotatingFileHandler('logs/mcp_singleagent.log', maxBytes=10*1024*1024, backupCount=3)
mcp_handler.setLevel(logging.DEBUG)
mcp_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(mcp_handler)
logger.propagate = False

# ANSI color codes
GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW = "\033[33m"
BLUE  = "\033[34m" 
CYAN  = "\033[36m"
BOLD  = "\033[1m"
RESET = "\033[0m"

class MCPServerConfig:
    """Configuration for MCP servers"""
    def __init__(self, name: str, server_type: str, config: Dict[str, Any]):
        self.name = name
        self.server_type = server_type  # 'stdio' or 'sse'
        self.config = config

class MCPEnhancedSingleAgent:
    """
    Enhanced SingleAgent with MCP (Model Context Protocol) support.
    
    Features:
    - All existing SingleAgent capabilities
    - MCP server integration for expanded tool ecosystem
    - Dynamic MCP server management
    - Unified tool interface (custom + MCP)
    - Enhanced logging and monitoring
    """
    
    def __init__(self, mcp_configs: Optional[List[MCPServerConfig]] = None):
        """
        Initialize the MCP-enhanced SingleAgent.
        
        Args:
            mcp_configs: List of MCP server configurations to load
        """
        # Initialize context first
        cwd = os.getcwd()
        self.context = EnhancedContextData(
            working_directory=cwd,
            project_name=os.path.basename(cwd),
            project_info=discover_project_info(cwd),
            current_file=None,
        )
        
        # MCP servers
        self.mcp_servers = []
        self.mcp_configs = mcp_configs or []
        
        # Initialize agent with base tools (will add MCP tools later)
        self.base_tools = [
            run_ruff, run_pylint, run_pyright, run_command,
            read_file, create_colored_diff, apply_patch,
            change_dir, os_command, get_context,
            get_context_response, add_manual_context
        ]
        
        # Agent will be created after MCP servers are loaded
        self.agent = None
        
        logger.info("MCPEnhancedSingleAgent initialized")
    
    async def initialize_mcp_servers(self):
        """Initialize all configured MCP servers."""
        logger.info(f"Initializing {len(self.mcp_configs)} MCP servers...")
        
        for config in self.mcp_configs:
            try:
                if config.server_type == "stdio":
                    server = MCPServerStdio(
                        params=config.config,
                        cache_tools_list=True  # Cache for performance
                    )
                elif config.server_type == "sse":
                    server = MCPServerSse(
                        params=config.config,
                        cache_tools_list=True
                    )
                else:
                    logger.error(f"Unknown MCP server type: {config.server_type}")
                    continue
                
                # Start the server and verify it works
                await server.__aenter__()
                tools = await server.list_tools()
                logger.info(f"MCP server '{config.name}' loaded with {len(tools)} tools")
                
                self.mcp_servers.append(server)
                
            except Exception as e:
                logger.error(f"Failed to initialize MCP server '{config.name}': {e}")
                continue
        
        logger.info(f"Successfully initialized {len(self.mcp_servers)} MCP servers")
    
    async def create_agent(self):
        """Create the agent with all tools (custom + MCP)."""
        if not self.agent:
            # Ensure MCP servers are initialized
            if not self.mcp_servers and self.mcp_configs:
                await self.initialize_mcp_servers()
            
            # Create agent with custom tools and MCP servers
            self.agent = Agent[EnhancedContextData](
                name="MCPEnhancedCodeAssistant",
                model="gpt-4.1",
                instructions=self._get_enhanced_instructions(),
                tools=self.base_tools,
                mcp_servers=self.mcp_servers
            )
            
            logger.info(f"Agent created with {len(self.base_tools)} custom tools and {len(self.mcp_servers)} MCP servers")
    
    def _get_enhanced_instructions(self) -> str:
        """Get enhanced instructions that include MCP capabilities."""
        base_instructions = """
You are an enhanced code assistant with access to both custom tools and MCP (Model Context Protocol) servers.

CAPABILITIES:
- All original SingleAgent capabilities (code analysis, patching, etc.)
- Extended capabilities via MCP servers (filesystem, databases, web, etc.)
- Unified tool interface - you can seamlessly use both custom and MCP tools
- Enhanced context management with token tracking and entity recognition

AVAILABLE TOOL TYPES:
1. Custom Tools (your original capabilities):
   - Code analysis: run_ruff, run_pylint, run_pyright
   - File operations: read_file, apply_patch, create_colored_diff
   - System operations: run_command, change_dir, os_command
   - Context management: get_context, add_manual_context

2. MCP Tools (extended capabilities):
   - Additional filesystem operations
   - Database connections and queries
   - Web browsing and scraping
   - Cloud service integrations
   - Development workflow tools

WORKFLOW:
1. Always check context first using get_context
2. Use the most appropriate tool for the task (custom or MCP)
3. Combine tools creatively for complex workflows
4. Track important files and commands in context
5. Provide clear explanations of your actions

Remember: You now have access to a much broader ecosystem of tools via MCP servers.
Think creatively about how to combine your existing capabilities with new MCP tools.
"""
        
        # Add context summary
        if hasattr(self, 'context'):
            context_summary = self.context.get_context_summary()
            base_instructions += f"\n\n--- CURRENT CONTEXT ---\n{context_summary}\n-----------------------\n"
        
        return base_instructions
    
    async def run(self, user_input: str, stream_output: bool = True) -> str:
        """
        Run the agent with enhanced MCP capabilities.
        
        Args:
            user_input: The user's query or request
            stream_output: Whether to stream the output
            
        Returns:
            The agent's response
        """
        # Ensure agent is created
        if not self.agent:
            await self.create_agent()
        
        # Add user message to context
        self.context.add_chat_message("user", user_input)
        
        # Update agent instructions with latest context
        self.agent.instructions = self._get_enhanced_instructions()
        
        logger.debug(f"Running agent with input: {user_input}")
        
        if stream_output:
            result = await self._run_streamed(user_input)
        else:
            res = await Runner.run(
                starting_agent=self.agent,
                input=user_input,
                context=self.context,
            )
            result = res.final_output
        
        # Add assistant response to context
        self.context.add_chat_message("assistant", result)
        
        return result
    
    async def _run_streamed(self, user_input: str) -> str:
        """Run the agent with streamed output."""
        logger.debug("Starting streamed run with MCP support")
        print(f"{CYAN}Starting MCP-enhanced agent...{RESET}")
        
        # Run the agent with streaming
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=user_input,
            max_turns=999,
            context=self.context,
        )
        
        # Use the shared stream event handler
        output_text_buffer = await handle_stream_events(
            result.stream_events(),
            self.context,
            logger,
            ItemHelpers
        )
        
        logger.debug("Streamed run completed")
        return output_text_buffer
    
    async def list_available_tools(self) -> Dict[str, List[str]]:
        """List all available tools (custom + MCP)."""
        tools_info = {
            "custom_tools": [tool.__name__ for tool in self.base_tools],
            "mcp_tools": {}
        }
        
        for i, server in enumerate(self.mcp_servers):
            config_name = self.mcp_configs[i].name if i < len(self.mcp_configs) else f"server_{i}"
            try:
                mcp_tools = await server.list_tools()
                tools_info["mcp_tools"][config_name] = [tool.name for tool in mcp_tools]
            except Exception as e:
                logger.error(f"Failed to list tools for MCP server {config_name}: {e}")
                tools_info["mcp_tools"][config_name] = ["ERROR: Could not list tools"]
        
        return tools_info
    
    async def get_mcp_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers."""
        status = {}
        
        for i, server in enumerate(self.mcp_servers):
            config_name = self.mcp_configs[i].name if i < len(self.mcp_configs) else f"server_{i}"
            try:
                tools = await server.list_tools()
                status[config_name] = {
                    "status": "active",
                    "tool_count": len(tools),
                    "server_type": self.mcp_configs[i].server_type if i < len(self.mcp_configs) else "unknown"
                }
            except Exception as e:
                status[config_name] = {
                    "status": "error",
                    "error": str(e),
                    "server_type": self.mcp_configs[i].server_type if i < len(self.mcp_configs) else "unknown"
                }
        
        return status
    
    async def reload_mcp_server(self, server_name: str) -> bool:
        """Reload a specific MCP server."""
        for i, config in enumerate(self.mcp_configs):
            if config.name == server_name:
                try:
                    # Close existing server if it exists
                    if i < len(self.mcp_servers):
                        await self.mcp_servers[i].__aexit__(None, None, None)
                    
                    # Recreate server
                    if config.server_type == "stdio":
                        server = MCPServerStdio(params=config.config, cache_tools_list=True)
                    else:
                        server = MCPServerSse(params=config.config, cache_tools_list=True)
                    
                    await server.__aenter__()
                    
                    # Replace in list
                    if i < len(self.mcp_servers):
                        self.mcp_servers[i] = server
                    else:
                        self.mcp_servers.append(server)
                    
                    # Recreate agent with new servers
                    self.agent = None
                    await self.create_agent()
                    
                    logger.info(f"Successfully reloaded MCP server: {server_name}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Failed to reload MCP server {server_name}: {e}")
                    return False
        
        logger.warning(f"MCP server not found: {server_name}")
        return False
    
    async def save_context(self):
        """Save context to persistent storage."""
        try:
            context_file = os.path.join(os.path.expanduser("~"), ".mcp_singleagent_context.json")
            await self.context.save_to_json(context_file)
            logger.info(f"Saved context to {context_file}")
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
    
    async def cleanup(self):
        """Clean up MCP servers and save context."""
        logger.info("Cleaning up MCP servers...")
        
        for server in self.mcp_servers:
            try:
                await server.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing MCP server: {e}")
        
        await self.save_context()
        logger.info("Cleanup completed")
    
    def get_context_summary(self) -> str:
        """Return a summary of the current context."""
        return self.context.get_context_summary()
    
    def get_chat_history_summary(self) -> str:
        """Return a summary of the chat history."""
        return self.context.get_chat_summary()
    
    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        self.context.clear_chat_history()


# Predefined MCP server configurations for common use cases
class CommonMCPConfigs:
    """Common MCP server configurations that users can easily add."""
    
    @staticmethod
    def filesystem_server(allowed_dirs: List[str]) -> MCPServerConfig:
        """MCP filesystem server configuration."""
        return MCPServerConfig(
            name="filesystem",
            server_type="stdio",
            config={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"] + allowed_dirs
            }
        )
    
    @staticmethod
    def git_server(repo_path: str = ".") -> MCPServerConfig:
        """MCP Git server configuration."""
        return MCPServerConfig(
            name="git",
            server_type="stdio",
            config={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-git", repo_path]
            }
        )
    
    @staticmethod
    def sqlite_server(db_path: str) -> MCPServerConfig:
        """MCP SQLite server configuration."""
        return MCPServerConfig(
            name="sqlite",
            server_type="stdio",
            config={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sqlite", db_path]
            }
        )
    
    @staticmethod
    def web_search_server(api_key: str) -> MCPServerConfig:
        """MCP web search server configuration."""
        return MCPServerConfig(
            name="web_search",
            server_type="stdio",
            config={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-web-search"],
                "env": {"API_KEY": api_key}
            }
        )


# Example usage function
async def create_enhanced_agent_with_common_servers() -> MCPEnhancedSingleAgent:
    """Create an enhanced agent with commonly useful MCP servers."""
    
    # Configure MCP servers
    mcp_configs = [
        # Filesystem access to current directory and subdirectories
        CommonMCPConfigs.filesystem_server([os.getcwd()]),
        
        # Note: Git server not available in official packages yet
        # Git operations on current repository
        # CommonMCPConfigs.git_server("."),
        
        # SQLite database operations (if you have a project database)
        # CommonMCPConfigs.sqlite_server("./project.db"),
        
        # Web search capabilities (requires API key)
        # CommonMCPConfigs.web_search_server("your_api_key_here"),
    ]
    
    # Create and initialize the enhanced agent
    agent = MCPEnhancedSingleAgent(mcp_configs)
    await agent.initialize_mcp_servers()
    await agent.create_agent()
    
    return agent
