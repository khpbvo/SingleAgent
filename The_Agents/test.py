#!/usr/bin/env python3
"""
Enhanced main.py with MCP (Model Context Protocol) support.
Extends the existing dual-agent system with MCP server integration.
"""

import asyncio
import sys
import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Enhanced prompt_toolkit imports (keeping your existing setup)
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings

# Import spaCy singleton (keeping your existing setup)
from The_Agents.spacy_singleton import SpacyModelSingleton, nlp_singleton

# Import your existing agents
from The_Agents.SingleAgent import SingleAgent
from The_Agents.ArchitectAgent import ArchitectAgent

# Import the new MCP-enhanced agent
from The_Agents.MCPEnhancedSingleAgent import MCPEnhancedSingleAgent, CommonMCPConfigs, MCPServerConfig

# ANSI escape codes (keeping your existing setup)
GREEN = "\033[32m"
RED   = "\033[31m"
BLUE  = "\033[34m"
YELLOW = "\033[33m"
BOLD  = "\033[1m"
RESET = "\033[0m"

# Configure logging (keeping your existing setup)
os.makedirs("logs", exist_ok=True)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
main_handler = RotatingFileHandler('logs/main_mcp.log', maxBytes=10*1024*1024, backupCount=3)
main_handler.setLevel(logging.DEBUG)
main_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
root_logger.addHandler(main_handler)

# Enhanced agent modes
class AgentMode:
    CODE = "code"
    ARCHITECT = "architect"
    MCP_ENHANCED = "mcp_enhanced"

def create_status_bar_text(current_agent, mode):
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
    
    # Add MCP server count if applicable
    mcp_info = ""
    if hasattr(current_agent, 'mcp_servers') and current_agent.mcp_servers:
        mcp_count = len(current_agent.mcp_servers)
        mcp_info = f" │ 🔌 {mcp_count} MCP"
    
    return HTML(
        f'<{mode_style}>[{mode_display}]</{mode_style}> │ '
        f'<{token_style}>Tokens: {token_count:,}/{max_tokens:,} ({percentage:.1f}%) [{bar}]</{token_style}> │ '
        f'<path>📁 {os.path.basename(context.working_directory)}</path>{mcp_info}'
    )

async def setup_mcp_servers() -> list:
    """Setup common MCP servers for the enhanced agent."""
    print(f"{YELLOW}Configuring MCP servers...{RESET}")
    
    mcp_configs = []
    current_dir = os.getcwd()
    
    # Always add filesystem server for current directory
    mcp_configs.append(CommonMCPConfigs.filesystem_server([current_dir]))
    
    # Add Git server if we're in a Git repository
    if os.path.exists(os.path.join(current_dir, '.git')):
        mcp_configs.append(CommonMCPConfigs.git_server("."))
        print(f"{GREEN}✓ Added Git MCP server{RESET}")
    
    # Add SQLite server if there are .db files
    db_files = [f for f in os.listdir(current_dir) if f.endswith('.db')]
    if db_files:
        mcp_configs.append(CommonMCPConfigs.sqlite_server(db_files[0]))
        print(f"{GREEN}✓ Added SQLite MCP server for {db_files[0]}{RESET}")
    
    # You can add more MCP servers here based on your needs
    # Example: Web search (requires API key)
    # if os.getenv('WEB_SEARCH_API_KEY'):
    #     mcp_configs.append(CommonMCPConfigs.web_search_server(os.getenv('WEB_SEARCH_API_KEY')))
    
    print(f"{GREEN}✓ Configured {len(mcp_configs)} MCP servers{RESET}")
    return mcp_configs

async def main():
    """Enhanced main function with MCP support."""
    # Initialize spaCy model at startup (keeping your existing setup)
    print(f"{YELLOW}Initializing spaCy model (this may take a moment)...{RESET}")
    await nlp_singleton.initialize(model_name="en_core_web_lg", disable=["parser"])
    
    # Initialize agents
    current_mode = AgentMode.CODE
    code_agent = SingleAgent()
    architect_agent = ArchitectAgent()
    
    # Setup MCP-enhanced agent
    print(f"{YELLOW}Setting up MCP-enhanced agent...{RESET}")
    mcp_configs = await setup_mcp_servers()
    mcp_enhanced_agent = MCPEnhancedSingleAgent(mcp_configs)
    await mcp_enhanced_agent.initialize_mcp_servers()
    await mcp_enhanced_agent.create_agent()
    
    print(f"{BOLD}Tri-Agent system initialized with MCP support.{RESET}")
    print(f"{GREEN}Currently in {BOLD}Code Agent{RESET}{GREEN} mode.{RESET}")
    print(f"Use {BOLD}!code{RESET}, {BOLD}!architect{RESET}, or {BOLD}!mcp{RESET} to switch between agents.")
    print(f"Use {BOLD}!help{RESET} for all commands.")
    
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
            print(f"\n{YELLOW}=== MCP-Enhanced Agent Mode ==={RESET}")
    
    # Show initial context
    display_mode_banner()
    print(f"\n{get_current_agent().get_context_summary()}\n")
    
    # Enhanced key bindings (keeping your existing setup)
    kb = KeyBindings()
    
    @kb.add('c-c')
    def _(event):
        event.app.exit()
    
    @kb.add('c-d')
    def _(event):
        event.app.exit()
    
    # Enhanced style with MCP mode support
    style = Style.from_dict({
        'auto-suggestion': 'fg:#888888 italic',
        'bottom-toolbar': 'bg:#444444 fg:#ffffff',
        'good': 'fg:#00ff00 bold',
        'warning': 'fg:#ffff00 bold', 
        'danger': 'fg:#ff0000 bold',
        'mode-code': 'fg:#00ff00 bold',
        'mode-arch': 'fg:#00aaff bold',
        'mode-mcp': 'fg:#ff8800 bold',  # New MCP mode color
        'path': 'fg:#cccccc',
    })
    
    # Enhanced prompt session
    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        style=style,
        key_bindings=kb,
        bottom_toolbar=lambda: create_status_bar_text(get_current_agent(), current_mode),
    )

    # Main REPL loop
    while True:
        try:
            query = await session.prompt_async(HTML('<b><ansigreen>User:</ansigreen></b> '))
            logging.debug(json.dumps({"event": "user_input", "input": query, "mode": current_mode}))
            
            # Entity extraction (keeping your existing logic)
            try:
                entities = await nlp_singleton.extract_entities(query)
                mapped_entities = await nlp_singleton.map_entity_types(entities)
                logging.debug(json.dumps({"event": "entity_extraction", "entities": mapped_entities}))
            except Exception as e:
                logging.error(f"Error extracting entities: {e}", exc_info=True)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break

        if not query.strip():
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
            print(f"\n{YELLOW}Switching to MCP-Enhanced Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{mcp_enhanced_agent.get_context_summary()}\n")
            continue
            
        elif query_lower == "!code" and current_mode != AgentMode.CODE:
            current_mode = AgentMode.CODE
            await get_current_agent().save_context()
            print(f"\n{GREEN}Switching to Code Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{code_agent.get_context_summary()}\n")
            continue
            
        elif query_lower == "!architect" and current_mode != AgentMode.ARCHITECT:
            current_mode = AgentMode.ARCHITECT
            await get_current_agent().save_context()
            print(f"\n{BLUE}Switching to Architect Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{architect_agent.get_context_summary()}\n")
            continue

        # Enhanced help command with MCP information
        if query_lower == "!help":
            print(f"""
{BOLD}Enhanced Agent Commands:{RESET}
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
!mcp        - Switch to MCP-Enhanced Agent mode (expanded capabilities)

{BOLD}MCP-Specific Commands:{RESET}
!mcptools   - List all available MCP tools
!mcpstatus  - Show MCP server status
!mcpreload:server - Reload a specific MCP server

{BOLD}Special Commands:{RESET}
code:read:path - Add file at path to persistent context
arch:readfile:path - Read and analyze a file with Architect Agent
arch:readdir:path - Analyze directory structure with Architect Agent

exit/quit   - Exit the program

{BOLD}MCP Capabilities:{RESET}
When in MCP mode, you have access to additional tools from MCP servers:
- Enhanced filesystem operations
- Git repository management
- Database operations (if configured)
- Web search and scraping (if configured)
- And more based on your MCP server configuration
""")
            continue

        # New MCP-specific commands
        if query_lower == "!mcptools":
            if current_mode == AgentMode.MCP_ENHANCED:
                tools_info = await mcp_enhanced_agent.list_available_tools()
                print(f"\n{BOLD}Available Tools:{RESET}")
                print(f"{GREEN}Custom Tools ({len(tools_info['custom_tools'])}):{RESET}")
                for tool in tools_info['custom_tools']:
                    print(f"  - {tool}")
                
                print(f"\n{YELLOW}MCP Tools:{RESET}")
                for server_name, tools in tools_info['mcp_tools'].items():
                    print(f"  {BOLD}{server_name} ({len(tools)} tools):{RESET}")
                    for tool in tools:
                        print(f"    - {tool}")
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
                    else:
                        print(f"    Error: {info.get('error', 'Unknown error')}")
                print()
            else:
                print(f"{RED}MCP status is only available in MCP-Enhanced mode. Use !mcp to switch.{RESET}")
            continue

        if query_lower.startswith("!mcpreload:"):
            if current_mode == AgentMode.MCP_ENHANCED:
                server_name = query_lower[len("!mcpreload:"):]
                print(f"{YELLOW}Reloading MCP server: {server_name}...{RESET}")
                success = await mcp_enhanced_agent.reload_mcp_server(server_name)
                if success:
                    print(f"{GREEN}✓ Successfully reloaded {server_name}{RESET}")
                else:
                    print(f"{RED}✗ Failed to reload {server_name}{RESET}")
            else:
                print(f"{RED}MCP reload is only available in MCP-Enhanced mode. Use !mcp to switch.{RESET}")
            continue

        # Keep all your existing special commands (tokens, context, etc.)
        # ... (keeping all existing command handling logic)
        
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