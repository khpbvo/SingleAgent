#!/usr/bin/env python3
"""
Enhanced main.py with MCP (Model Context Protocol) support.
Extends the existing dual-agent system with MCP server integration and multi-project support.
"""

import asyncio
import sys
import logging
import json
import os
from functools import lru_cache
from datetime import datetime
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add these imports for prompt_toolkit with status bar
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings

# Import spaCy singleton
from The_Agents.spacy_singleton import SpacyModelSingleton, nlp_singleton

# Import both agents and shared context manager
from The_Agents.SingleAgent import SingleAgent
from The_Agents.ArchitectAgent import ArchitectAgent

# Import the MCP-enhanced agent
from The_Agents.MCPEnhancedSingleAgent_fixed import MCPEnhancedSingleAgent, CommonMCPConfigs, MCPServerConfig

from The_Agents.shared_context_manager import SharedContextManager
from The_Agents.workflows import WorkflowOrchestrator

# ANSI escape codes
GREEN = "\033[32m"
RED   = "\033[31m"
BLUE  = "\033[34m"
YELLOW = "\033[33m"
CYAN  = "\033[36m"
BOLD  = "\033[1m"
RESET = "\033[0m"

# Configure logging
os.makedirs("logs", exist_ok=True)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
# Remove default handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
main_handler = RotatingFileHandler('logs/main.log', maxBytes=10*1024*1024, backupCount=3)
main_handler.setLevel(logging.DEBUG)
main_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
root_logger.addHandler(main_handler)

# Enhanced agent modes
class AgentMode:
    CODE = "code"
    ARCHITECT = "architect"
    MCP_ENHANCED = "mcp_enhanced"

# Simple caches for status bar computations
_working_dir_cache = {"path": None, "basename": None}
_mcp_cache = {"servers": None, "dirs": None, "counts": (0, 0)}


def _get_cached_basename(working_directory: str) -> str:
    """Return cached basename for the working directory."""
    if _working_dir_cache["path"] != working_directory:
        _working_dir_cache["path"] = working_directory
        _working_dir_cache["basename"] = os.path.basename(working_directory)
    return _working_dir_cache["basename"]


def _get_cached_mcp_counts(mcp_servers, working_dirs):
    """Return cached counts for MCP servers and directories."""
    servers_tuple = tuple(mcp_servers) if mcp_servers else ()
    dirs_tuple = tuple(working_dirs) if working_dirs else ()
    if (_mcp_cache["servers"] != servers_tuple or
            _mcp_cache["dirs"] != dirs_tuple):
        _mcp_cache["servers"] = servers_tuple
        _mcp_cache["dirs"] = dirs_tuple
        _mcp_cache["counts"] = (len(servers_tuple), len(dirs_tuple))
    return _mcp_cache["counts"]

def create_status_bar_text(current_agent, mode, shared_manager=None):
    """Enhanced status bar that shows MCP server status."""
    context = current_agent.context
    token_count = context.token_count
    max_tokens = context.max_tokens
    percentage = (token_count / max_tokens) * 100 if max_tokens > 0 else 0
    
    # Create progress bar
    bar_width = 20
    filled = int((percentage / 100) * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    # Color coding based on percentage
    if percentage < 50:
        token_style = "good"
    elif percentage < 80:
        token_style = "warning"
    else:
        token_style = "danger"
    
    # Mode styling
    if mode == AgentMode.CODE:
        mode_style = "mode-code"
        mode_display = "CODE"
    elif mode == AgentMode.ARCHITECT:
        mode_style = "mode-arch"
        mode_display = "ARCH"
    else:  # MCP_ENHANCED
        mode_style = "mode-mcp"
        mode_display = "MCP+"
    
    # Get collaboration info
    collab_info = ""
    if shared_manager:
        agent_name = "code" if mode == AgentMode.CODE else "architect"
        pending_tasks = shared_manager.get_pending_tasks(agent_name)
        if pending_tasks:
            task_count = len(pending_tasks)
            collab_info = f' │ <collab>📋 {task_count} tasks</collab>'
    
    # Add MCP server count and working directories if applicable
    mcp_info = ""
    if hasattr(current_agent, 'mcp_servers') and current_agent.mcp_servers:
        servers = current_agent.mcp_servers
        dirs = getattr(current_agent, 'working_directories', [])
        mcp_count, dir_count = _get_cached_mcp_counts(servers, dirs)
        mcp_info = f" │ 🔌 {mcp_count} MCP"
        if dir_count:
            mcp_info += f" │ 📁 {dir_count} dirs"
    
    return HTML(
        f'<{mode_style}>[{mode_display}]</{mode_style}> │ '
        f'<{token_style}>Tokens: {token_count:,}/{max_tokens:,} ({percentage:.1f}%) [{bar}]</{token_style}> │ '
        f'<path>📁 {_get_cached_basename(context.working_directory)}</path>{collab_info}{mcp_info}'
    )

@lru_cache(maxsize=None)
def get_common_project_directories():
    """Get common project directories for multi-project support."""
    common_dirs = []

    # Add current directory
    current_dir = os.getcwd()
    common_dirs.append(current_dir)

    # Add parent directory if it looks like a projects folder
    parent_dir = os.path.dirname(current_dir)
    if any(word in parent_dir.lower() for word in ['projects', 'development', 'dev', 'code', 'workspace']):
        # Add other project directories in the same parent
        try:
            with os.scandir(parent_dir) as it:
                for entry in it:
                    if entry.is_dir() and entry.path != current_dir:
                        if any(os.path.exists(os.path.join(entry.path, file)) for file in [
                            '.git', 'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml'
                        ]):
                            common_dirs.append(entry.path)
        except PermissionError:
            pass  # Skip if we can't read the parent directory

    # Add common development directories
    home_dir = os.path.expanduser("~")
    potential_dirs = [
        os.path.join(home_dir, "Projects"),
        os.path.join(home_dir, "Development"),
        os.path.join(home_dir, "dev"),
        os.path.join(home_dir, "code"),
        os.path.join(home_dir, "workspace"),
        os.path.join(home_dir, "Documents", "Projects"),
        os.path.join(home_dir, "Documents", "Development"),
    ]

    for potential_dir in potential_dirs:
        if os.path.exists(potential_dir) and potential_dir not in common_dirs:
            try:
                with os.scandir(potential_dir) as it:
                    for entry in it:
                        if entry.is_dir():
                            if any(os.path.exists(os.path.join(entry.path, file)) for file in [
                                '.git', 'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml'
                            ]):
                                if entry.path not in common_dirs:
                                    common_dirs.append(entry.path)
            except PermissionError:
                pass

    # Limit to reasonable number and sort by relevance
    common_dirs = common_dirs[:10]  # Limit to 10 directories max

    return common_dirs

async def setup_mcp_servers() -> list:
    """Setup common MCP servers for the enhanced agent with multi-project support."""
    print(f"{YELLOW}Configuring MCP servers with multi-project support...{RESET}")
    
    mcp_configs = []
    
    # Get working directories for multi-project support
    working_directories = get_common_project_directories()
    print(f"{BLUE}Detected {len(working_directories)} project directories:{RESET}")
    for i, dir_path in enumerate(working_directories, 1):
        print(f"  {i}. {dir_path}")
    
    # Add filesystem server with multiple directories
    mcp_configs.append(CommonMCPConfigs.filesystem_server(working_directories))
    print(f"{GREEN}✓ Added Filesystem MCP server for {len(working_directories)} directories{RESET}")
    
    # DISABLED: Git server removed due to faults
    # git_repos = [d for d in working_directories if os.path.exists(os.path.join(d, '.git'))]
    # if git_repos:
    #     # For now, use the current directory's git repo
    #     # In the future, we could set up multiple git servers
    #     current_git_repo = next((d for d in git_repos if d == os.getcwd()), git_repos[0])
    #     mcp_configs.append(CommonMCPConfigs.git_server(current_git_repo))
    #     print(f"{GREEN}✓ Added Git MCP server for {current_git_repo}{RESET}")
    print(f"{YELLOW}ℹ Git MCP server disabled (was causing issues){RESET}")
    
    # Add SQLite server if there are .db files in any directory
    db_files = []
    for directory in working_directories:
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if entry.is_file() and entry.name.endswith('.db'):
                        db_files.append(entry.path)
        except PermissionError:
            continue
    
    if db_files:
        # Use the first database found
        mcp_configs.append(CommonMCPConfigs.sqlite_server(db_files[0]))
        print(f"{GREEN}✓ Added SQLite MCP server for {db_files[0]}{RESET}")
    
    # Add GitHub server if token is available
    github_token = (os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT') or 
                   os.getenv('GH_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN'))
    if github_token:
        # Try to detect if we're in a GitHub repo and get owner/repo info
        owner, repo = None, None
        try:
            current_dir = os.getcwd()
            if os.path.exists(os.path.join(current_dir, '.git')):
                import subprocess
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      capture_output=True, text=True, cwd=current_dir)
                if result.returncode == 0:
                    remote_url = result.stdout.strip()
                    # Parse GitHub URL
                    if 'github.com' in remote_url:
                        # Handle both SSH and HTTPS URLs
                        if remote_url.startswith('git@github.com:'):
                            # SSH format: git@github.com:owner/repo.git
                            repo_path = remote_url.replace('git@github.com:', '').replace('.git', '')
                        elif 'github.com/' in remote_url:
                            # HTTPS format: https://github.com/owner/repo.git
                            repo_path = remote_url.split('github.com/')[-1].replace('.git', '')
                        
                        if '/' in repo_path:
                            owner, repo = repo_path.split('/', 1)
        except Exception:
            pass  # Ignore errors in repo detection
        
        mcp_configs.append(CommonMCPConfigs.github_server(github_token, owner, repo))
        if owner and repo:
            print(f"{GREEN}✓ Added GitHub MCP server for {owner}/{repo}{RESET}")
        else:
            print(f"{GREEN}✓ Added GitHub MCP server (general access){RESET}")
    else:
        print(f"{YELLOW}⚠ GitHub token not found. Set GITHUB_TOKEN, GITHUB_PAT, GH_TOKEN, or GITHUB_PERSONAL_ACCESS_TOKEN to enable GitHub MCP server{RESET}")
    
    # You can add more MCP servers here based on your needs
    # Example: Web search (requires API key)
    # if os.getenv('WEB_SEARCH_API_KEY'):
    #     mcp_configs.append(CommonMCPConfigs.web_search_server(os.getenv('WEB_SEARCH_API_KEY')))
    
    print(f"{GREEN}✓ Configured {len(mcp_configs)} MCP servers with multi-project support{RESET}")
    return mcp_configs, working_directories

async def main():
    """Enhanced main function with MCP support and multi-project capabilities."""
    # Initialize spaCy model at startup
    print(f"{YELLOW}Initializing spaCy model (this may take a moment)...{RESET}")
    await nlp_singleton.initialize(model_name="en_core_web_lg", disable=["parser"])
    
    # Initialize shared context manager and workflow orchestrator
    shared_manager = SharedContextManager()
    workflow_orchestrator = WorkflowOrchestrator(shared_manager)
    
    # Initialize agents
    current_mode = AgentMode.CODE
    code_agent = SingleAgent()
    architect_agent = ArchitectAgent()
    
    # Setup MCP-enhanced agent with multi-project support
    print(f"{YELLOW}Setting up MCP-enhanced agent with multi-project support...{RESET}")
    mcp_configs, working_directories = await setup_mcp_servers()
    mcp_enhanced_agent = MCPEnhancedSingleAgent(mcp_configs, working_directories)
    await mcp_enhanced_agent.initialize_mcp_servers()
    await mcp_enhanced_agent.create_agent()
    
    # Set up shared context manager and workflow orchestrator in all agents' metadata
    code_agent.context.metadata["shared_manager"] = shared_manager
    code_agent.context.metadata["agent_name"] = "code"
    code_agent.context.metadata["workflow_orchestrator"] = workflow_orchestrator
    architect_agent.context.metadata["shared_manager"] = shared_manager
    architect_agent.context.metadata["agent_name"] = "architect"
    architect_agent.context.metadata["workflow_orchestrator"] = workflow_orchestrator
    
    print(f"{BOLD}🚀 Multi-Project MCP Agent System Initialized!{RESET}")
    print(f"{GREEN}Currently in {BOLD}Code Agent{RESET}{GREEN} mode.{RESET}")
    print(f"Use {BOLD}!code{RESET}, {BOLD}!architect{RESET}, or {BOLD}!mcp{RESET} to switch between agents.")
    print(f"Use {BOLD}!help{RESET} for all commands.")
    print(f"\n{CYAN}🌍 Multi-Project Support: {len(working_directories)} directories available{RESET}")
    
    # Get the currently active agent
    def get_current_agent():
        if current_mode == AgentMode.CODE:
            return code_agent
        elif current_mode == AgentMode.ARCHITECT:
            return architect_agent
        else:  # MCP_ENHANCED
            return mcp_enhanced_agent
    
    # Display agent mode banner
    def display_mode_banner():
        if current_mode == AgentMode.CODE:
            print(f"\n{GREEN}=== Code Agent Mode ==={RESET}")
        elif current_mode == AgentMode.ARCHITECT:
            print(f"\n{BLUE}=== Architect Agent Mode ==={RESET}")
        else:  # MCP_ENHANCED
            print(f"\n{YELLOW}=== MCP-Enhanced Agent Mode (Multi-Project) ==={RESET}")
    
    # Show initial context
    display_mode_banner()
    print(f"\n{get_current_agent().get_context_summary()}\n")
    
    # Create key bindings for better UX
    kb = KeyBindings()
    
    @kb.add('c-c')
    def _(event):
        """Handle Ctrl+C gracefully."""
        event.app.exit()
    
    @kb.add('c-d')
    def _(event):
        """Handle Ctrl+D gracefully."""
        event.app.exit()
    
    # Enhanced style with MCP mode support
    style = Style.from_dict({
        'auto-suggestion': 'fg:#888888 italic',
        'bottom-toolbar': 'bg:#444444 fg:#ffffff',
        
        # Status bar styles - match the HTML class names above
        'good': 'fg:#00ff00 bold',
        'warning': 'fg:#ffff00 bold', 
        'danger': 'fg:#ff0000 bold',
        'mode-code': 'fg:#00ff00 bold',
        'mode-arch': 'fg:#00aaff bold',
        'mode-mcp': 'fg:#ff8800 bold',  # New MCP mode color
        'path': 'fg:#cccccc',
        'collab': 'fg:#ff8800 bold',  # Orange for collaboration info
    })
    
    # Set up prompt_toolkit session with status bar
    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        style=style,
        key_bindings=kb,
        bottom_toolbar=lambda: create_status_bar_text(get_current_agent(), current_mode, shared_manager),
    )

    # enter REPL loop
    while True:
        try:
            # Use prompt_toolkit session for input with auto-suggest and status bar
            query = await session.prompt_async(HTML('<b><ansigreen>User:</ansigreen></b> '))
            logging.debug(json.dumps({"event": "user_input", "input": query, "mode": current_mode}))
            
            # Process input with spaCy for entity recognition
            # This allows the agent to have entities available before processing
            try:
                entities = await nlp_singleton.extract_entities(query)
                mapped_entities = await nlp_singleton.map_entity_types(entities)
                logging.debug(json.dumps({"event": "entity_extraction", "entities": mapped_entities}))
            except Exception as e:
                logging.error(f"Error extracting entities: {e}", exc_info=True)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break

        # Handle None or empty input safely
        if query is None or not isinstance(query, str) or not query.strip():
            continue
            
        if query.strip().lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        # Enhanced mode switching with MCP support
        query_lower = query.strip().lower()
        
        if query_lower == "!mcp" and current_mode != AgentMode.MCP_ENHANCED:
            # Switch to MCP-enhanced mode
            current_mode = AgentMode.MCP_ENHANCED
            await get_current_agent().save_context()  # Save previous context
            print(f"\n{YELLOW}Switching to MCP-Enhanced Agent mode with multi-project support.{RESET}")
            display_mode_banner()
            print(f"\n{mcp_enhanced_agent.get_context_summary()}\n")
            continue
            
        elif query_lower == "!code" and current_mode != AgentMode.CODE:
            current_mode = AgentMode.CODE
            await get_current_agent().save_context()
            # Merge relevant context for collaboration
            if current_mode == AgentMode.ARCHITECT:
                code_agent.context.merge_from(architect_agent.context, merge_chat=False)
                # Show handoff context
                handoff_context = shared_manager.get_agent_handoff_context("architect", "code")
                if handoff_context["pending_tasks"]:
                    print(f"{YELLOW}📋 You have {len(handoff_context['pending_tasks'])} pending tasks from Architect Agent{RESET}")
            print(f"\n{GREEN}Switching to Code Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{code_agent.get_context_summary()}\n")
            continue
            
        elif query_lower == "!architect" and current_mode != AgentMode.ARCHITECT:
            current_mode = AgentMode.ARCHITECT
            await get_current_agent().save_context()
            # Merge relevant context for collaboration
            if current_mode == AgentMode.CODE:
                architect_agent.context.merge_from(code_agent.context, merge_chat=False)
                # Show handoff context
                handoff_context = shared_manager.get_agent_handoff_context("code", "architect")
                if handoff_context["pending_tasks"]:
                    print(f"{YELLOW}📋 You have {len(handoff_context['pending_tasks'])} pending tasks from Code Agent{RESET}")
            print(f"\n{BLUE}Switching to Architect Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{architect_agent.get_context_summary()}\n")
            continue
            
        # Add a new command to show token details
        if query.strip().lower() == "!tokens":
            current_agent = get_current_agent()
            context = current_agent.context
            token_info = context.get_token_usage_info() if hasattr(context, 'get_token_usage_info') else {
                "current": context.token_count,
                "maximum": context.max_tokens,
                "percentage": (context.token_count / context.max_tokens) * 100,
                "remaining": context.max_tokens - context.token_count,
            }
            
            print(f"""
{BOLD}Token Usage Details:{RESET}
Current tokens: {token_info['current']:,}
Maximum tokens: {token_info['maximum']:,}
Usage percentage: {token_info['percentage']:.2f}%
Remaining tokens: {token_info['remaining']:,}
""")
            if 'manual_context_tokens' in token_info:
                print(f"Manual context tokens: {token_info['manual_context_tokens']:,}")
            if 'chat_tokens' in token_info:
                print(f"Chat history tokens: {token_info['chat_tokens']:,}")
            print()
            continue
            
        # Enhanced help command with MCP information and multi-project support
        if query_lower == "!help":
            print(f"""
{BOLD}🚀 Enhanced Multi-Project Agent Commands:{RESET}
!help       - Show this help message
!history    - Show chat history
!context    - Show full context summary 
!tokens     - Show detailed token usage information
!clear      - Clear chat history
!save       - Manually save context
!entity     - List tracked entities
!manualctx  - List all manually added context items
!delctx:label  - Remove manual context item by label

{BOLD}Agent Modes:{RESET}
!code       - Switch to Code Agent mode (original functionality)
!architect  - Switch to Architect Agent mode (architecture analysis)
!mcp        - Switch to MCP-Enhanced Agent mode (multi-project capabilities)

{BOLD}🔌 MCP-Specific Commands:{RESET}
!mcptools   - List all available MCP tools
!mcpstatus  - Show MCP server status
!mcpreload:server - Reload a specific MCP server
!mcpdirs    - List all available working directories
!mcpadddir:path - Add a new working directory
!mcprmdir:path - Remove a working directory

{BOLD}Special Commands:{RESET}
code:read:path - Add file at path to persistent context
arch:readfile:path - Read and analyze a file with Architect Agent
arch:readdir:path - Analyze directory structure with Architect Agent

{BOLD}Cross-Agent Collaboration:{RESET}
Use the agent tools to:
- request_architecture_review: Ask Architect for design advice
- request_implementation: Ask Code Agent to implement features
- share_insight: Share discoveries between agents
- record_architectural_decision: Document design decisions
- get_collaboration_status: Check pending tasks and insights
- start_feature_workflow: Start automated feature implementation workflow
- start_bugfix_workflow: Start automated bug fix workflow  
- start_refactor_workflow: Start automated refactoring workflow

exit/quit   - Exit the program

{BOLD}🌍 Multi-Project Support:{RESET}
The MCP-enhanced agent can work across multiple projects simultaneously:
- Automatically detects project directories
- Provides filesystem access to all configured directories
- Can switch between projects using change_dir or MCP filesystem tools
- Maintains context across different projects

{BOLD}🔧 MCP Capabilities:{RESET}
When in MCP mode, you have access to enhanced tools:
- **Enhanced filesystem operations** across multiple directories
- **Git repository management** with advanced features
- **Database operations** (if SQLite databases are detected)
- **GitHub API operations** (if GitHub token is configured)
- **Web search and scraping** (if configured)
- **Multi-project workflow management**

{BOLD}GitHub MCP Server Setup:{RESET}
To enable GitHub MCP server functionality:
1. Get a GitHub Personal Access Token from https://github.com/settings/tokens
2. Set one of these environment variables:
   export GITHUB_TOKEN=your_token_here
   export GITHUB_PAT=your_token_here  
   export GH_TOKEN=your_token_here
3. Restart the application to auto-detect GitHub repositories
4. Switch to MCP mode with !mcp to access GitHub tools

{BOLD}🎯 MCP Tool Priority:{RESET}
The MCP agent is designed to:
- **Prefer MCP tools** over custom tools for better capabilities
- **Explain tool choices** to help you understand the benefits
- **Work across multiple projects** seamlessly
- **Provide enhanced error handling** and structured responses

Example: Instead of using 'read_file', the MCP agent will use the MCP filesystem 
tool which provides better error handling, metadata, and cross-project support.
""")
            continue
            
        # New MCP-specific commands with multi-project support
        if query_lower == "!mcptools":
            if current_mode == AgentMode.MCP_ENHANCED:
                tools_info = await mcp_enhanced_agent.list_available_tools()
                print(f"\n{BOLD}Available Tools:{RESET}")
                print(f"{GREEN}Custom Tools ({len(tools_info['custom_tools'])}):{RESET}")
                for tool in tools_info['custom_tools']:
                    print(f"  - {tool}")
                
                print(f"\n{YELLOW}MCP Tools:{RESET}")
                mcp_tools = tools_info['mcp_tools']
                if isinstance(mcp_tools, dict):
                    for server_name, tools in mcp_tools.items():
                        print(f"  {BOLD}{server_name} ({len(tools)} tools):{RESET}")
                        for tool in tools:
                            print(f"    - {tool}")
                else:
                    print(f"  {RED}Unexpected MCP tools format: {type(mcp_tools)}{RESET}")
                
                print(f"\n{CYAN}Working Directories ({len(tools_info['working_directories'])}):{RESET}")
                for i, dir_path in enumerate(tools_info['working_directories'], 1):
                    print(f"  {i}. {dir_path}")
                print()
            else:
                print(f"{RED}MCP tools are only available in MCP-Enhanced mode. Use !mcp to switch.{RESET}")
            continue

        if query_lower == "!mcpstatus":
            if current_mode == AgentMode.MCP_ENHANCED:
                status = await mcp_enhanced_agent.get_mcp_server_status()
                print(f"\n{BOLD}MCP Server Status:{RESET}")
                for server_name, info in status.items():
                    status_color = GREEN if info['status'] == 'active' else RED
                    print(f"  {status_color}{server_name}: {info['status']}{RESET}")
                    if info['status'] == 'active':
                        print(f"    Tools: {info['tool_count']}")
                        print(f"    Type: {info['server_type']}")
                        if 'config' in info and 'args' in info['config']:
                            args = info['config']['args']
                            if server_name == 'filesystem' and len(args) > 2:
                                dirs = args[2:]  # Skip npx and package name
                                print(f"    Directories: {len(dirs)}")
                                for d in dirs[:3]:  # Show first 3
                                    print(f"      - {d}")
                                if len(dirs) > 3:
                                    print(f"      ... and {len(dirs) - 3} more")
                    else:
                        print(f"    Error: {info.get('error', 'Unknown error')}")
                print()
            else:
                print(f"{RED}MCP status is only available in MCP-Enhanced mode. Use !mcp to switch.{RESET}")
            continue

        if query_lower == "!mcpdirs":
            if current_mode == AgentMode.MCP_ENHANCED:
                dirs = await mcp_enhanced_agent.list_working_directories()
                print(f"\n{BOLD}Available Working Directories ({len(dirs)}):{RESET}")
                for i, dir_path in enumerate(dirs, 1):
                    current_marker = " (current)" if dir_path == os.getcwd() else ""
                    print(f"  {i}. {dir_path}{current_marker}")
                print()
            else:
                print(f"{RED}Working directories are only available in MCP-Enhanced mode. Use !mcp to switch.{RESET}")
            continue

        if query_lower.startswith("!mcpadddir:"):
            if current_mode == AgentMode.MCP_ENHANCED:
                dir_path = query_lower[len("!mcpadddir:"):].strip()
                if not dir_path:
                    print(f"{RED}Usage: !mcpadddir:path/to/directory{RESET}")
                    continue
                
                print(f"{YELLOW}Adding working directory: {dir_path}...{RESET}")
                success = await mcp_enhanced_agent.add_working_directory(dir_path)
                if success:
                    print(f"{GREEN}✓ Successfully added {dir_path}{RESET}")
                    dirs = await mcp_enhanced_agent.list_working_directories()
                    print(f"Total working directories: {len(dirs)}")
                else:
                    print(f"{RED}✗ Failed to add {dir_path} (check if directory exists){RESET}")
            else:
                print(f"{RED}Directory management is only available in MCP-Enhanced mode. Use !mcp to switch.{RESET}")
            continue

        if query_lower.startswith("!mcprmdir:"):
            if current_mode == AgentMode.MCP_ENHANCED:
                dir_path = query_lower[len("!mcprmdir:"):].strip()
                if not dir_path:
                    print(f"{RED}Usage: !mcprmdir:path/to/directory{RESET}")
                    continue
                
                print(f"{YELLOW}Removing working directory: {dir_path}...{RESET}")
                success = await mcp_enhanced_agent.remove_working_directory(dir_path)
                if success:
                    print(f"{GREEN}✓ Successfully removed {dir_path}{RESET}")
                    dirs = await mcp_enhanced_agent.list_working_directories()
                    print(f"Remaining working directories: {len(dirs)}")
                else:
                    print(f"{RED}✗ Failed to remove {dir_path} (not in working directories){RESET}")
            else:
                print(f"{RED}Directory management is only available in MCP-Enhanced mode. Use !mcp to switch.{RESET}")
            continue

        if query_lower.startswith("!mcpreload:"):
            if current_mode == AgentMode.MCP_ENHANCED:
                server_name = query_lower[len("!mcpreload:"):].strip()
                if not server_name:
                    print(f"{RED}Usage: !mcpreload:server_name{RESET}")
                    continue
                    
                print(f"{YELLOW}Reloading MCP server: {server_name}...{RESET}")
                success = await mcp_enhanced_agent.reload_mcp_server(server_name)
                if success:
                    print(f"{GREEN}✓ Successfully reloaded {server_name}{RESET}")
                else:
                    print(f"{RED}✗ Failed to reload {server_name}{RESET}")
            else:
                print(f"{RED}MCP reload is only available in MCP-Enhanced mode. Use !mcp to switch.{RESET}")
            continue

        # Keep all existing special commands
        elif query.strip().lower() == "!history":
            print(f"\n{get_current_agent().get_chat_history_summary()}\n")
            continue
        elif query.strip().lower() == "!context":
            print(f"\n{get_current_agent().get_context_summary()}\n")
            continue
        elif query.strip().lower() == "!clear":
            get_current_agent().clear_chat_history()
            print("\nChat history cleared.\n")
            continue
        elif query.strip().lower() == "!save":
            await get_current_agent().save_context()
            print("\nContext saved.\n")
            continue
        elif query.strip().lower() == "!collab":
            # Show collaboration status
            agent_name = "code" if current_mode == AgentMode.CODE else "architect"
            summary = shared_manager.get_collaboration_summary()
            
            print(f"\n{BOLD}=== Collaboration Status ==={RESET}")
            
            # Show pending tasks for current agent
            pending_tasks = shared_manager.get_pending_tasks(agent_name)
            if pending_tasks:
                print(f"\n{YELLOW}📋 Your Pending Tasks ({len(pending_tasks)}):{RESET}")
                for i, task in enumerate(pending_tasks, 1):
                    print(f"  {i}. [{task.priority.upper()}] {task.task}")
                    print(f"     From: {task.created_by}")
                    if task.context:
                        print(f"     Context: {json.dumps(task.context, indent=6)}")
            else:
                print(f"\n{GREEN}✅ No pending tasks for you{RESET}")
            
            # Overall statistics
            print(f"\n{BOLD}📊 Overall Statistics:{RESET}")
            print(f"  - Total tasks: {summary['total_tasks']}")
            print(f"  - Completed: {summary['completed_tasks']}")
            for agent, count in summary.get('pending_tasks_by_agent', {}).items():
                print(f"  - Pending for {agent}: {count}")
            
            # Recent insights
            if summary['recent_insights']:
                print(f"\n{BOLD}💡 Recent Insights ({summary['total_insights']} total):{RESET}")
                for insight in summary['recent_insights']:
                    print(f"  - {insight}")
            
            # Architectural decisions
            if summary['architectural_decisions'] > 0:
                print(f"\n{BOLD}🏗️  Architectural Decisions: {summary['architectural_decisions']}{RESET}")
                decisions = shared_manager.get_architectural_decisions()[:3]
                for decision in decisions:
                    print(f"  - {decision.decision}")
                    print(f"    Rationale: {decision.rationale}")
            
            print()
            continue
        elif query.strip().lower() == "!workflows":
            # Show active workflows
            workflows = workflow_orchestrator.list_active_workflows()
            
            print(f"\n{BOLD}=== Active Workflows ==={RESET}")
            
            if not workflows:
                print(f"\n{GREEN}✅ No active workflows{RESET}")
            else:
                for workflow in workflows:
                    print(f"\n🔄 {workflow['name']}")
                    print(f"   ID: {workflow['workflow_id']}")
                    print(f"   Status: {workflow['status'].upper()}")
                    print(f"   Progress: {workflow['completed_steps']}/{workflow['total_steps']} steps ({workflow['progress_percentage']:.1f}%)")
                    
                    if workflow['failed_steps'] > 0:
                        print(f"   ⚠️  Failed steps: {workflow['failed_steps']}")
                    
                    if workflow['running_steps'] > 0:
                        print(f"   🔄 Running steps: {workflow['running_steps']}")
            
            print()
            continue
        elif query.strip().lower() == "!entity":
            current_agent = get_current_agent()
            entities = current_agent.context.active_entities
            if not entities:
                print("\nNo tracked entities.\n")
                continue
                
            print(f"\n{BOLD}Tracked Entities:{RESET}")
            # Get entity types based on the current mode
            entity_types = ["file", "command", "url", "search_query"]
            if current_mode == AgentMode.ARCHITECT:
                entity_types.extend(["design_pattern", "architecture_concept"])
                
            for entity_type in entity_types:
                type_entities = [e for e in entities.values() if e.entity_type == entity_type]
                if type_entities:
                    print(f"\n{BOLD}{entity_type.capitalize()}s:{RESET}")
                    # Sort by access count (most frequent first)
                    type_entities.sort(key=lambda e: e.access_count, reverse=True)
                    for i, entity in enumerate(type_entities[:10]):  # Show top 10
                        print(f"  {i+1}. {entity.value} (accessed {entity.access_count} times)")
            print()
            continue
        elif query.strip().lower() == "!manualctx":
            current_agent = get_current_agent()
            if not hasattr(current_agent.context, 'manual_context_items') or not current_agent.context.manual_context_items:
                print("\nNo manual context items available.\n")
                continue
                
            manual_items = current_agent.context.manual_context_items
            
            print(f"\n{BOLD}Manual Context Items:{RESET}")
            print(f"\nTotal items: {len(manual_items)}")
            
            for i, item in enumerate(manual_items):
                time_str = datetime.fromtimestamp(item.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                content_preview = item.content[:50].replace('\n', ' ') + "..." if len(item.content) > 50 else item.content.replace('\n', ' ')
                print(f"\n{i+1}. {BOLD}{item.label}{RESET}")
                print(f"   Source: {item.source}")
                print(f"   Added: {time_str}")
                print(f"   Size: {item.token_count} tokens")
                print(f"   Preview: {content_preview}")
                
            print()
            continue
        
        # Check for command to delete context item
        if query.startswith("!delctx:"):
            try:
                # Extract label
                label = query[len("!delctx:"):].strip()
                
                # Get current agent
                current_agent = get_current_agent()
                
                # Check if context item exists
                if not hasattr(current_agent.context, 'manual_context_items'):
                    print(f"{RED}No manual context items exist.{RESET}")
                    continue
                
                found = False
                for item in current_agent.context.manual_context_items:
                    if item.label == label:
                        found = True
                        break
                
                if not found:
                    print(f"{RED}No context item found with label '{label}'.{RESET}")
                    print(f"{YELLOW}Use !manualctx to list available context items.{RESET}")
                    continue
                
                # Remove item
                removed = current_agent.context.remove_manual_context(label)
                
                # Save context
                await current_agent.save_context()
                
                if removed:
                    print(f"{GREEN}Successfully removed context item '{label}'.{RESET}")
                else:
                    print(f"{RED}Failed to remove context item '{label}'.{RESET}")
                
                continue
            except Exception as e:
                print(f"{RED}Error removing context item: {str(e)}{RESET}")
                continue
        
        # Check for arch:readfile command
        if query.startswith("arch:readfile:"):
            try:
                # Make sure we're in architect mode
                if current_mode != AgentMode.ARCHITECT:
                    print(f"{YELLOW}Switching to Architect Agent mode...{RESET}")
                    current_mode = AgentMode.ARCHITECT
                    
                # Extract file path
                file_path = query[len("arch:readfile:"):].strip()
                
                # Skip if path is empty
                if not file_path:
                    print(f"{RED}Error: No file path provided. Usage: arch:readfile:path/to/file{RESET}")
                    continue
                
                # Create modified query for the agent
                modified_query = f"Read and analyze the file at '{file_path}'. Provide a detailed summary of its content, structure, and purpose."
                
                # Get current agent and run 
                current_agent = get_current_agent()
                print(f"{BLUE}Processing with Architect Agent...{RESET}")
                await current_agent.run(modified_query, stream_output=True)
                
                # Save context after interaction
                await current_agent.save_context()
                continue
                
            except Exception as e:
                print(f"{RED}Error reading file: {str(e)}{RESET}")
                continue
        
        # Check for arch:readdir command
        if query.startswith("arch:readdir:"):
            try:
                # Make sure we're in architect mode
                if current_mode != AgentMode.ARCHITECT:
                    print(f"{YELLOW}Switching to Architect Agent mode...{RESET}")
                    current_mode = AgentMode.ARCHITECT
                
                # Extract directory path
                dir_path = query[len("arch:readdir:"):].strip()
                
                # Skip if path is empty
                if not dir_path:
                    print(f"{RED}Error: No directory path provided. Usage: arch:readdir:path/to/directory{RESET}")
                    continue
                
                # Create modified query for the agent
                modified_query = f"Read and analyze the directory structure at '{dir_path}'. Provide a comprehensive overview of the project structure, files, and potential architecture."
                
                # Get current agent and run
                current_agent = get_current_agent()
                print(f"{BLUE}Processing with Architect Agent...{RESET}")
                await current_agent.run(modified_query, stream_output=True)
                
                # Save context after interaction
                await current_agent.save_context()
                continue
                
            except Exception as e:
                print(f"{RED}Error reading directory: {str(e)}{RESET}")
                continue
        
        # Check for special code:read command pattern
        if query.startswith("code:read:"):
            try:
                # Extract file path
                file_path = query[len("code:read:"):].strip()
                
                # Get absolute path if relative
                if not os.path.isabs(file_path):
                    file_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
                
                # Check if file exists
                if not os.path.exists(file_path):
                    print(f"{RED}Error: File not found at {file_path}{RESET}")
                    continue
                
                # Get agent and add context
                current_agent = get_current_agent()
                
                # Generate a label based on filename
                label = f"file:{os.path.basename(file_path)}"
                
                # Add to context
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add to context using the internal method directly
                added_label = current_agent.context.add_manual_context(
                    content=content,
                    source=file_path,
                    label=label
                )
                
                # Track as file entity as well
                current_agent.context.track_entity(
                    entity_type="file",
                    value=file_path,
                    metadata={"content_preview": content[:100] if content else None}
                )
                
                # Save context
                await current_agent.save_context()
                
                # Show success message
                tokens = current_agent.context.count_tokens(content)
                print(f"{GREEN}Successfully added context from {file_path} with label '{added_label}' ({tokens} tokens){RESET}")
                continue
            
            except Exception as e:
                print(f"{RED}Error adding context: {str(e)}{RESET}")
                continue
        
        # Run the appropriate agent with the query
        try:
            current_agent = get_current_agent()
            logging.debug(json.dumps({
                "event": "agent_processing", 
                "mode": current_mode, 
                "query": query
            }))
            
            # Show agent-specific processing indicator
            if current_mode == AgentMode.CODE:
                mode_color = GREEN
                agent_name = "Code Agent"
            elif current_mode == AgentMode.ARCHITECT:
                mode_color = BLUE
                agent_name = "Architect Agent"
            else:  # MCP_ENHANCED
                mode_color = YELLOW
                agent_name = "MCP-Enhanced Agent"
            
            print(f"{mode_color}Processing with {agent_name}...{RESET}")
            
            # Run the agent with streaming output
            result = await current_agent.run(query, stream_output=True)
            
            # Save context after each interaction
            await current_agent.save_context()
            
        except Exception as e:
            logging.error(f"Error running agent: {e}", exc_info=True)
            print(f"\n{RED}Error running agent: {e}{RESET}\n")

    # Cleanup on exit
    if current_mode == AgentMode.MCP_ENHANCED:
        print(f"{YELLOW}Cleaning up MCP servers...{RESET}")
        await mcp_enhanced_agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
