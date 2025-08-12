"""
Enhanced SingleAgent implementation with MCP (Model Context Protocol) support.
FIXED VERSION - Addresses MCP tool usage issues.
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
from agents.model_settings import ModelSettings
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
    
    FIXES:
    - Proper model configuration
    - Enhanced MCP tool instructions
    - Better tool visibility and usage guidance
    - Improved error handling and logging
    """
    
    def __init__(self, mcp_configs: Optional[List[MCPServerConfig]] = None, working_directories: Optional[List[str]] = None):
        """
        Initialize the MCP-enhanced SingleAgent.
        
        Args:
            mcp_configs: List of MCP server configurations to load
            working_directories: List of directories the agent can work with (default: current dir only)
        """
        # Initialize context first
        cwd = os.getcwd()
        self.context = EnhancedContextData(
            working_directory=cwd,
            project_name=os.path.basename(cwd),
            project_info=discover_project_info(cwd),
            current_file=None,
            max_tokens=400_000,
        )
        
        # Store working directories for multi-project support
        self.working_directories = working_directories or [cwd]
        logger.info(f"Initialized with working directories: {self.working_directories}")
        
        # MCP servers
        self.mcp_servers = []
        self.mcp_configs = mcp_configs or []
        self.mcp_tools_list = {}  # Cache for tool listings
        self.mcp_server_details = {}  # Detailed info about each server
        
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
        async def init_server(config: MCPServerConfig):
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
                raise ValueError(f"Unknown MCP server type: {config.server_type}")

            await server.__aenter__()
            tools = await server.list_tools()
            logger.info(f"MCP server '{config.name}' loaded with {len(tools)} tools")
            return server, tools

        tasks = [asyncio.create_task(init_server(config)) for config in self.mcp_configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for config, result in zip(self.mcp_configs, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to initialize MCP server '{config.name}': {result}")
                continue

            server, tools = result
            self.mcp_tools_list[config.name] = [tool.name for tool in tools]
            self.mcp_servers.append(server)

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
                model="gpt-5",  # FIXED: Use correct model name
                instructions=self._get_enhanced_instructions(),
                tools=self.base_tools,
                mcp_servers=self.mcp_servers,
                model_settings=ModelSettings(max_tokens=400_000)
            )
            
            logger.info(f"Agent created with {len(self.base_tools)} custom tools and {len(self.mcp_servers)} MCP servers")
    
    def _get_enhanced_instructions(self) -> str:
        """Get enhanced instructions that include MCP capabilities."""
        
        # Build detailed MCP tools listing
        mcp_tools_section = ""
        if self.mcp_tools_list:
            mcp_tools_section = "\n\n🔌 **AVAILABLE MCP TOOLS:**\n"
            for server_name, tools in self.mcp_tools_list.items():
                mcp_tools_section += f"\n**{server_name.upper()} SERVER:**\n"
                for tool in tools:
                    mcp_tools_section += f"  - {tool}\n"
            mcp_tools_section += "\n**IMPORTANT:** These MCP tools provide extended capabilities beyond your custom tools. USE THEM when they're more appropriate for the task!"
        
        base_instructions = f"""
You are an enhanced code assistant with access to both CUSTOM TOOLS and MCP (Model Context Protocol) TOOLS.

🎯 **CORE PRINCIPLE:** You have access to TWO TYPES of tools:
1. **Custom Tools** (your original capabilities)
2. **MCP Tools** (extended capabilities via MCP servers)

**ALWAYS choose the BEST tool for the task, whether it's custom or MCP!**

📋 **
- Code analysis: run_ruff, run_pylint, run_pyright
- File operations: read_file, apply_patch, create_colored_diff
- System operations: run_command, change_dir, os_command
- Context management: get_context, add_manual_context
{mcp_tools_section}

🚀 **ENHANCED WORKFLOW:**
1. **Check context first** using get_context
2. **Identify the best tool** for your task:
   - Use MCP filesystem tools for advanced file operations
   - Use MCP git tools for version control operations
   - Use MCP database tools for data operations
   - Use MCP GitHub tools for repository management
   - Use custom tools for code analysis and patching
3. **Combine tools creatively** - you can chain custom and MCP tools
4. **Always explain your tool choices** - tell the user why you picked a specific tool
5. **Track important context** as you work

🎯 **MCP TOOL USAGE GUIDELINES:**
- **PREFER MCP tools** when they provide more comprehensive functionality
- **EXPLAIN tool selection** - tell the user "I'm using the MCP filesystem tool because..."
- **Leverage unique MCP capabilities** like database queries, GitHub API calls, etc.
- **Fall back to custom tools** if MCP tools fail or aren't suitable

⚠️ **CRITICAL:** Don't just use your familiar custom tools! The MCP tools often provide better, more comprehensive solutions. Always consider them first!

🔄 **EXAMPLE DECISION PROCESS:**
- User asks to "read a file" → Consider: read_file (custom) vs MCP filesystem read → Choose based on complexity needed
- User asks for "git operations" → Prefer MCP git tools over run_command with git
- User asks for "database query" → Use MCP database tools, not custom command tools
- User asks for "code analysis" → Use custom analysis tools (run_ruff, etc.) - they're specialized for this
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
        
        # Update agent instructions with latest context and MCP tool info
        self.agent.instructions = self._get_enhanced_instructions()
        
        logger.debug(f"Running agent with input: {user_input}")
        logger.debug(f"Available MCP servers: {list(self.mcp_tools_list.keys())}")
        
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
    
    async def list_available_tools(self) -> Dict[str, Any]:
        """List all available tools (custom + MCP)."""
        tools_info = {
            "custom_tools": [getattr(tool, '__name__', getattr(tool, 'name', str(tool))) for tool in self.base_tools],
            "mcp_tools": {},
            "working_directories": self.working_directories
        }

        # Gather tool lists from all servers concurrently
        tasks = []
        server_names = []
        for i, server in enumerate(self.mcp_servers):
            server_name = self.mcp_configs[i].name if i < len(self.mcp_configs) else f"server_{i}"
            server_names.append(server_name)
            tasks.append(server.list_tools())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for server_name, result in zip(server_names, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to list tools for MCP server {server_name}: {result}")
                tools_info["mcp_tools"][server_name] = ["ERROR: Could not list tools"]
            else:
                tools_info["mcp_tools"][server_name] = [tool.name for tool in result]

        return tools_info
    
    async def add_working_directory(self, directory_path: str) -> bool:
        """Add a new working directory to the MCP filesystem server."""
        try:
            abs_path = os.path.abspath(directory_path)
            if not os.path.exists(abs_path):
                logger.warning(f"Directory does not exist: {abs_path}")
                return False
            
            if abs_path not in self.working_directories:
                self.working_directories.append(abs_path)
                # Update filesystem server with new directories
                await self._update_filesystem_server()
                logger.info(f"Added working directory: {abs_path}")
                return True
            else:
                logger.info(f"Directory already in working directories: {abs_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to add working directory {directory_path}: {e}")
            return False
    
    async def remove_working_directory(self, directory_path: str) -> bool:
        """Remove a working directory from the MCP filesystem server."""
        try:
            abs_path = os.path.abspath(directory_path)
            if abs_path in self.working_directories:
                self.working_directories.remove(abs_path)
                # Update filesystem server with remaining directories
                await self._update_filesystem_server()
                logger.info(f"Removed working directory: {abs_path}")
                return True
            else:
                logger.warning(f"Directory not in working directories: {abs_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to remove working directory {directory_path}: {e}")
            return False
    
    async def _update_filesystem_server(self):
        """Update the filesystem server with current working directories."""
        try:
            # Find the filesystem server config
            for i, config in enumerate(self.mcp_configs):
                if config.name == "filesystem":
                    # Update the config args
                    config.config["args"] = ["-y", "@modelcontextprotocol/server-filesystem"] + self.working_directories
                    
                    # Reload the filesystem server
                    await self.reload_mcp_server("filesystem")
                    break
        except Exception as e:
            logger.error(f"Failed to update filesystem server: {e}")
    
    async def list_working_directories(self) -> List[str]:
        """List all working directories."""
        return self.working_directories.copy()
    
    async def get_mcp_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers."""
        status = {}

        tasks = []
        server_names = []
        server_types = []
        for i, server in enumerate(self.mcp_servers):
            server_name = self.mcp_configs[i].name if i < len(self.mcp_configs) else f"server_{i}"
            server_type = self.mcp_configs[i].server_type if i < len(self.mcp_configs) else "unknown"
            server_names.append(server_name)
            server_types.append(server_type)
            tasks.append(server.list_tools())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for server_name, server_type, result in zip(server_names, server_types, results):
            if isinstance(result, Exception):
                status[server_name] = {
                    "status": "error",
                    "error": str(result),
                    "server_type": server_type
                }
            else:
                status[server_name] = {
                    "status": "active",
                    "tool_count": len(result),
                    "server_type": server_type
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
                    
                    # Update tools list
                    tools = await server.list_tools()
                    self.mcp_tools_list[config.name] = [tool.name for tool in tools]
                    
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
    
    # DISABLED: Git server removed due to faults with @modelcontextprotocol/server-git
    # @staticmethod
    # def git_server(repo_path: str = ".") -> MCPServerConfig:
    #     """MCP Git server configuration."""
    #     return MCPServerConfig(
    #         name="git",
    #         server_type="stdio",
    #         config={
    #             "command": "npx",
    #             "args": ["-y", "@modelcontextprotocol/server-git", repo_path]
    #         }
    #     )
    
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
    
    @staticmethod
    def github_server(github_token: str, owner: Optional[str] = None, repo: Optional[str] = None) -> MCPServerConfig:
        """MCP GitHub server configuration.
        
        Args:
            github_token: GitHub personal access token
            owner: Optional GitHub username/organization (if provided, repo must also be provided)
            repo: Optional repository name (if provided, owner must also be provided)
        """
        args = ["-y", "@modelcontextprotocol/server-github"]
        
        # Add owner and repo if both are provided
        if owner and repo:
            args.extend([owner, repo])
        
        return MCPServerConfig(
            name="github",
            server_type="stdio",
            config={
                "command": "npx",
                "args": args,
                "env": {"GITHUB_TOKEN": github_token}
            }
        )


# Example usage function
async def create_enhanced_agent_with_common_servers() -> MCPEnhancedSingleAgent:
    """Create an enhanced agent with commonly useful MCP servers."""
    
    # Configure MCP servers
    mcp_configs = [
        # Filesystem access to current directory and subdirectories
        CommonMCPConfigs.filesystem_server([os.getcwd()]),
        
        # Add GitHub server if token is available
        # CommonMCPConfigs.github_server(os.getenv("GITHUB_TOKEN"))
    ]
    
    # Create and initialize the enhanced agent
    agent = MCPEnhancedSingleAgent(mcp_configs)
    await agent.initialize_mcp_servers()
    await agent.create_agent()
    
    return agent
