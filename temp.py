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
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Add these imports for prompt_toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

# Import spaCy singleton
from spacy_singleton import SpacyModelSingleton, nlp_singleton

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
    # Initialize spaCy model at startup
    print(f"{YELLOW}Initializing spaCy model (this may take a moment)...{RESET}")
    await nlp_singleton.initialize(model_name="en_core_web_lg", disable=["parser"])
    
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
    
    # Set up prompt_toolkit session for CLI with history auto-suggest
    style = Style.from_dict({
        'auto-suggestion': 'fg:#888888 italic'
    })
    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        style=style
    )

    # enter REPL loop
    while True:
        try:
            # Use prompt_toolkit session for input with auto-suggest
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

        if not query.strip():
            continue
            
        if query.strip().lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        # Continue with rest of your existing main function...
        # Mode switching commands, command handling, agent processing, etc.

if __name__ == "__main__":
    asyncio.run(main())