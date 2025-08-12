"""
Enhanced SingleAgent implementation with MCP (Model Context Protocol) support.
FIXED VERSION - Addresses MCP tool usage issues and multi-project support.
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
    - Enhanced MCP tool instructions with clear prioritization
    - Better tool visibility and usage guidance
    - Multi-project support with configurable directories
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
                
                # Cache tool list for instructions with detailed info
                tool_details = []
                for tool in tools:
                    tool_info = {
                        "name": tool.name,
                        "description": getattr(tool, 'description', 'No description available')
                    }
                    tool_details.append(tool_info)
                
                self.mcp_tools_list[config.name] = [tool.name for tool in tools]
                self.mcp_server_details[config.name] = {
                    "tools": tool_details,
                    "config": config.config,
                    "type": config.server_type
                }
                
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
                model="gpt-5",  # FIXED: Use proper model name
                instructions=self._get_enhanced_instructions(),
                tools=self.base_tools,
                mcp_servers=self.mcp_servers,
                model_settings=ModelSettings(max_tokens=400_000)
            )
            
            logger.info(f"Agent created with {len(self.base_tools)} custom tools and {len(self.mcp_servers)} MCP servers")
    
    def _get_enhanced_instructions(self) -> str:
        """Get enhanced instructions that include MCP capabilities."""
        
        # Build detailed MCP tools listing with better descriptions
        mcp_tools_section = ""
        if self.mcp_tools_list:
            mcp_tools_section = "\n\n🔌 **AVAILABLE MCP TOOLS (USE THESE FIRST!):**\n"
            for server_name, tools in self.mcp_tools_list.items():
                server_details = self.mcp_server_details.get(server_name, {})
                mcp_tools_section += f"\n**{server_name.upper()} SERVER** ({len(tools)} tools):\n"
                
                # Show detailed tool info if available
                if "tools" in server_details:
                    for tool_info in server_details["tools"]:
                        mcp_tools_section += f"  - {tool_info['name']}: {tool_info['description']}\n"
                else:
                    for tool in tools:
                        mcp_tools_section += f"  - {tool}\n"
            
            mcp_tools_section += "\n🎯 **MCP PRIORITY RULE:** Always consider MCP tools FIRST! They provide more comprehensive capabilities than custom tools.\n"
        
        # Build working directories info
        dirs_info = "\n📁 **AVAILABLE WORKING DIRECTORIES:**\n"
        for i, dir_path in enumerate(self.working_directories, 1):
            dirs_info += f"  {i}. {dir_path}\n"
        dirs_info += "\n✅ You can switch between these directories or work across multiple projects simultaneously!\n"
        
        base_instructions = f"""
You are an ENHANCED code assistant with POWERFUL MCP (Model Context Protocol) capabilities!

🚀 **YOUR SUPERPOWERS:**
You have access to TWO TYPES of tools, but MCP tools are generally MORE POWERFUL:

1. **🔧 CUSTOM TOOLS** (legacy capabilities):
   - Code analysis: run_ruff, run_pylint, run_pyright
   - File operations: read_file, apply_patch, create_colored_diff
   - System operations: run_command, change_dir, os_command
   - Context management: get_context, add_manual_context

2. **🔌 MCP TOOLS** (enhanced capabilities - USE THESE FIRST!):
{mcp_tools_section}

{dirs_info}

🎯 **CRITICAL DECISION FRAMEWORK:**

**ALWAYS FOLLOW THIS PRIORITY ORDER:**
1. **Check if MCP tools can handle the task** - they usually can do it better!
2. **Use MCP filesystem tools** instead of read_file for file operations
3. **Use MCP git tools** instead of run_command for git operations  
4. **Use MCP database tools** for any data operations
5. **Use MCP GitHub tools** for repository management
6. **Fall back to custom tools** only if MCP tools aren't suitable

**EXAMPLES OF SMART TOOL SELECTION:**
- User: "Read this file" → Use MCP filesystem tool (more features than read_file)
- User: "Git status" → Use MCP git tool (not run_command git status)
- User: "Search files" → Use MCP filesystem search (not os_command find)
- User: "GitHub operations" → Use MCP GitHub tools (not manual API calls)
- User: "Database query" → Use MCP database tools (not custom commands)
- User: "Code analysis" → Use custom tools (run_ruff, run_pylint - they're specialized)

🔄 **ENHANCED WORKFLOW:**
1. **Always explain your tool choice**: "I'm using the MCP filesystem tool because..."
2. **Leverage MCP's advanced features**: Better error handling, structured responses, etc.
3. **Combine tools creatively**: Chain MCP and custom tools when needed
4. **Work across projects**: You can operate in multiple directories!
5. **Track context**: Use get_context and add_manual_context to remember important info

⚠️ **MANDATORY BEHAVIORS:**
- **NEVER use custom tools when MCP tools exist for the same purpose**
- **ALWAYS explain why you chose a specific tool**
- **ACTIVELY promote MCP capabilities** - tell users about the enhanced features
- **Work across multiple projects** - don't limit yourself to one directory
- **Use change_dir to switch between working directories as needed**

🎪 **SHOW OFF YOUR MCP POWERS:**
When you successfully use MCP tools, briefly explain the benefits:
- "Using MCP filesystem tool for better error handling and structured responses"
- "MCP git tool provides more detailed repository information than basic commands"
- "MCP GitHub integration gives us direct API access with proper authentication"

🌟 **REMEMBER:** You're not just a code assistant - you're a MULTI-PROJECT, MCP-ENHANCED powerhouse!
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
        logger.debug(f"Working directories: {self.working_directories}")
        
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
        print(f"{CYAN}🚀 Starting MCP-enhanced agent with multi-project support...{RESET}")
        
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
    
    async def add_working_directory(self, directory_path: str) -> bool:
        """Add a new working directory to the agent's capabilities."""
        abs_path = os.path.abspath(directory_path)
        if not os.path.exists(abs_path):
            logger.error(f"Directory does not exist: {abs_path}")
            return False
        
        if abs_path not in self.working_directories:
            self.working_directories.append(abs_path)
            logger.info(f"Added working directory: {abs_path}")
            
            # Update MCP filesystem server with new directories
            await self._update_filesystem_server()
            
            # Recreate agent with updated instructions
            self.agent = None
            await self.create_agent()
            
            return True
        
        logger.info(f"Directory already in working directories: {abs_path}")
        return True
    
    async def remove_working_directory(self, directory_path: str) -> bool:
        """Remove a working directory from the agent's capabilities."""
        abs_path = os.path.abspath(directory_path)
        if abs_path in self.working_directories:
            self.working_directories.remove(abs_path)
            logger.info(f"Removed working directory: {abs_path}")
            
            # Update MCP filesystem server
            await self._update_filesystem_server()
            
            # Recreate agent with updated instructions
            self.agent = None
            await self.create_agent()
            
            return True
        
        logger.warning(f"Directory not in working directories: {abs_path}")
        return False
    
    async def _update_filesystem_server(self):
        """Update the MCP filesystem server with current working directories."""
        # Find and update the filesystem server config
        for i, config in enumerate(self.mcp_configs):
            if config.name == "filesystem":
                # Update the config with new directories
                config.config["args"] = ["-y", "@modelcontextprotocol/server-filesystem"] + self.working_directories
                
                # Reload the server
                await self.reload_mcp_server("filesystem")
                break
    
    async def list_working_directories(self) -> List[str]:
        """List all current working directories."""
        return list(self.working_directories)
    
    async def list_available_tools(self) -> Dict[str, Any]:
        """List all available tools (custom + MCP)."""
        # Some custom tools are wrapped by decorators (e.g., FunctionTool) and may not
        # have a __name__ attribute. Be defensive and extract a readable name.
        def _tool_name(t: Any) -> str:
            # Prefer Python function __name__ if present
            n = getattr(t, "__name__", None)
            if isinstance(n, str):
                return n
            # Fall back to common wrapper attributes like .name
            n = getattr(t, "name", None)
            if isinstance(n, str):
                return n
            # Last resort: class name string
            return type(t).__name__

        tools_info = {
            "custom_tools": [_tool_name(tool) for tool in self.base_tools],
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
        
        # Add working directories info
        tools_info["working_directories"] = self.working_directories
        
        return tools_info
    
    async def get_mcp_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers."""
        status = {}
        
        for i, server in enumerate(self.mcp_servers):
            config_name = self.mcp_configs[i].name if i < len(self.mcp_configs) else f"server_{i}"
            try:
                tools = await server.list_tools()
                config_info = self.mcp_configs[i] if i < len(self.mcp_configs) else None
                status[config_name] = {
                    "status": "active",
                    "tool_count": len(tools),
                    "server_type": config_info.server_type if config_info else "unknown",
                    "config": config_info.config if config_info else {}
                }
            except Exception as e:
                config_info = self.mcp_configs[i] if i < len(self.mcp_configs) else None
                status[config_name] = {
                    "status": "error",
                    "error": str(e),
                    "server_type": config_info.server_type if config_info else "unknown"
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
        summary = self.context.get_context_summary()
        summary += f"\n\n🌍 **Multi-Project Support:**\n"
        summary += f"Working directories: {len(self.working_directories)}\n"
        for i, dir_path in enumerate(self.working_directories, 1):
            summary += f"  {i}. {dir_path}\n"
        return summary
    
    def get_chat_history_summary(self) -> str:
        """Return a summary of the chat history."""
        return self.context.get_chat_summary()
    
    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        self.context.clear_chat_history()


# Enhanced predefined MCP server configurations
class CommonMCPConfigs:
    """Common MCP server configurations that users can easily add."""
    
    @staticmethod
    def filesystem_server(allowed_dirs: List[str]) -> MCPServerConfig:
        """MCP filesystem server configuration with multiple directories."""
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
    def github_server(github_token: str, owner: str = None, repo: str = None) -> MCPServerConfig:
        """MCP GitHub server configuration.
        
        Args:
            github_token: GitHub personal access token
            owner: Optional GitHub username/organization
            repo: Optional repository name
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


# Enhanced usage function with multi-project support
async def create_enhanced_agent_with_multi_project_support(working_directories: List[str] = None) -> MCPEnhancedSingleAgent:
    """Create an enhanced agent with multi-project support and common MCP servers."""
    
    # Use provided directories or default to current directory
    if working_directories is None:
        working_directories = [os.getcwd()]
    
    # Configure MCP servers with multiple directories
    mcp_configs = [
        # Filesystem access to all specified directories
        CommonMCPConfigs.filesystem_server(working_directories),
        
        # Add GitHub server if token is available
        # Uncomment and configure as needed:
        # CommonMCPConfigs.github_server(os.getenv("GITHUB_TOKEN"))
    ]
    
    # Create and initialize the enhanced agent
    agent = MCPEnhancedSingleAgent(mcp_configs, working_directories)
    await agent.initialize_mcp_servers()
    await agent.create_agent()
    
    return agent
