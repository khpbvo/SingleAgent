#!/usr/bin/env python3
"""
main.py
Entry point for the dual-agent system with both Code and Architect capabilities.
Allows switching between SingleAgent and ArchitectAgent based on user commands.
"""

import asyncio
import sys
import logging
import json
import os
from logging.handlers import RotatingFileHandler

# Import both agents
from The_Agents.SingleAgent import SingleAgent
from The_Agents.ArchitectAgent import ArchitectAgent

# ANSI escape codes
GREEN = "\033[32m"
RED   = "\033[31m"
BLUE  = "\033[34m"
YELLOW = "\033[33m"
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

# Enum-like for agent modes
class AgentMode:
    CODE = "code"
    ARCHITECT = "architect"

async def main():
    """Main function to run the dual-agent system with mode switching support."""
    # Start in code agent mode by default
    current_mode = AgentMode.CODE
    code_agent = SingleAgent()
    architect_agent = ArchitectAgent()
    
    print(f"{BOLD}Dual-Agent system initialized.{RESET}")
    print(f"{GREEN}Currently in {BOLD}Code Agent{RESET}{GREEN} mode.{RESET}")
    print(f"Use {BOLD}!code{RESET} or {BOLD}!architect{RESET} to switch between agents.")
    print(f"Use {BOLD}!history{RESET} to view chat history or {BOLD}!clear{RESET} to clear it.")
    
    # Get the currently active agent
    def get_current_agent():
        return code_agent if current_mode == AgentMode.CODE else architect_agent
    
    # Display agent mode banner
    def display_mode_banner():
        if current_mode == AgentMode.CODE:
            print(f"\n{GREEN}=== Code Agent Mode ==={RESET}")
        else:
            print(f"\n{BLUE}=== Architect Agent Mode ==={RESET}")
    
    # Show initial context
    display_mode_banner()
    print(f"\n{get_current_agent().get_context_summary()}\n")
    
    # enter REPL loop
    while True:
        try:
            # read user input and log it
            query = input(f"{BOLD}{GREEN}User:{RESET} ")
            logging.debug(json.dumps({"event": "user_input", "input": query, "mode": current_mode}))
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break
        
        if not query.strip():
            continue
            
        if query.strip().lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        # Mode switching commands
        if query.strip().lower() == "!architect" and current_mode == AgentMode.CODE:
            # Switch to architect mode
            current_mode = AgentMode.ARCHITECT
            # Save context before switching
            await code_agent.save_context()
            print(f"\n{BLUE}Switching to Architect Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{architect_agent.get_context_summary()}\n")
            continue
        elif query.strip().lower() == "!code" and current_mode == AgentMode.ARCHITECT:
            # Switch to code mode
            current_mode = AgentMode.CODE
            # Save context before switching
            await architect_agent.save_context()
            print(f"\n{GREEN}Switching to Code Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{code_agent.get_context_summary()}\n")
            continue
            
        # Common special commands for both modes
        if query.strip().lower() == "!help":
            print(f"""
{BOLD}Agent Commands:{RESET}
!help       - Show this help message
!history    - Show chat history
!context    - Show full context summary 
!clear      - Clear chat history
!save       - Manually save context
!entity     - List tracked entities
!code       - Switch to Code Agent mode
!architect  - Switch to Architect Agent mode
exit/quit   - Exit the program
""")
            continue
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
        
        # Run the appropriate agent with the query
        try:
            current_agent = get_current_agent()
            # Log which agent is handling the query
            logging.debug(json.dumps({
                "event": "agent_processing", 
                "mode": current_mode, 
                "query": query
            }))
            
            # Show agent-specific processing indicator
            mode_color = GREEN if current_mode == AgentMode.CODE else BLUE
            agent_name = "Code Agent" if current_mode == AgentMode.CODE else "Architect Agent"
            print(f"{mode_color}Processing with {agent_name}...{RESET}")
            
            # Run the agent with streaming output
            result = await current_agent.run(query, stream_output=True)
            # Since output is streamed, we don't need to print the result again
            
            # Save context after each interaction
            await current_agent.save_context()
            
        except Exception as e:
            logging.error(f"Error running agent: {e}", exc_info=True)
            print(f"\n{RED}Error running agent: {e}{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())