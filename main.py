#!/usr/bin/env python3
"""
main.py
Entry point for the multi-agent system with Code, Architect and Web Browser agents.
Allows switching between SingleAgent, ArchitectAgent and WebBrowserAgent based on user commands.
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
from The_Agents.spacy_singleton import SpacyModelSingleton, nlp_singleton

# Import both agents
from The_Agents.SingleAgent import SingleAgent
from The_Agents.ArchitectAgent import ArchitectAgent
from The_Agents.WebBrowserAgent import WebBrowserAgent
from The_Agents.context_data import EnhancedContextData

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
    BROWSER = "browser"

async def main():
    """Main function to run the dual-agent system with mode switching support."""
    # Initialize spaCy model at startup
    print(f"{YELLOW}Initializing spaCy model (this may take a moment)...{RESET}")
    await nlp_singleton.initialize(model_name="en_core_web_lg", disable=["parser"])
    
    # Load or create shared context
    shared_path = os.path.join(os.path.expanduser("~"), ".agent_shared_context.json")
    shared_context = await EnhancedContextData.load_from_json(shared_path)

    # Start in code agent mode by default
    current_mode = AgentMode.CODE
    browser_agent = WebBrowserAgent(context=shared_context, context_path=shared_path)
    code_agent = SingleAgent(context=shared_context, context_path=shared_path, browser_agent=browser_agent)
    architect_agent = ArchitectAgent(context=shared_context, context_path=shared_path)
    
    print(f"{BOLD}Multi-Agent system initialized.{RESET}")
    print(f"{GREEN}Currently in {BOLD}Code Agent{RESET}{GREEN} mode.{RESET}")
    print(f"Use {BOLD}!code{RESET}, {BOLD}!architect{RESET} or {BOLD}!browser{RESET} to switch between agents.")
    print(f"Use {BOLD}!history{RESET} to view chat history or {BOLD}!clear{RESET} to clear it.")
    
    # Get the currently active agent
    def get_current_agent():
        if current_mode == AgentMode.CODE:
            return code_agent
        if current_mode == AgentMode.ARCHITECT:
            return architect_agent
        return browser_agent
    
    # Display agent mode banner
    def display_mode_banner():
        if current_mode == AgentMode.CODE:
            print(f"\n{GREEN}=== Code Agent Mode ==={RESET}")
        elif current_mode == AgentMode.ARCHITECT:
            print(f"\n{BLUE}=== Architect Agent Mode ==={RESET}")
        else:
            print(f"\n{YELLOW}=== Web Browser Agent Mode ==={RESET}")
    
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

        # Mode switching commands
        if query.strip().lower() == "!architect" and current_mode != AgentMode.ARCHITECT:
            summary = get_current_agent().get_context_summary()
            architect_agent.context.add_manual_context(
                content=summary,
                source=f"{current_mode}_agent",
                label=f"handoff_from_{current_mode}"
            )
            await get_current_agent().save_context()
            current_mode = AgentMode.ARCHITECT
            print(f"\n{BLUE}Switching to Architect Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{architect_agent.get_context_summary()}\n")
            continue
        elif query.strip().lower() == "!code" and current_mode != AgentMode.CODE:
            summary = get_current_agent().get_context_summary()
            code_agent.context.add_manual_context(
                content=summary,
                source=f"{current_mode}_agent",
                label=f"handoff_from_{current_mode}"
            )
            await get_current_agent().save_context()
            current_mode = AgentMode.CODE
            print(f"\n{GREEN}Switching to Code Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{code_agent.get_context_summary()}\n")
            continue
        elif query.strip().lower() == "!browser" and current_mode != AgentMode.BROWSER:
            summary = get_current_agent().get_context_summary()
            browser_agent.context.add_manual_context(
                content=summary,
                source=f"{current_mode}_agent",
                label=f"handoff_from_{current_mode}"
            )
            await get_current_agent().save_context()
            current_mode = AgentMode.BROWSER
            print(f"\n{YELLOW}Switching to Web Browser Agent mode.{RESET}")
            display_mode_banner()
            print(f"\n{browser_agent.get_context_summary()}\n")
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
!manualctx  - List all manually added context items
!delctx:label  - Remove manual context item by label
!code       - Switch to Code Agent mode
!architect  - Switch to Architect Agent mode
!browser    - Switch to Web Browser Agent mode

{BOLD}Special Commands:{RESET}
code:read:path - Add file at path to persistent context
arch:readfile:path - Read and analyze a file with Architect Agent
arch:readdir:path - Analyze directory structure with Architect Agent
  Parameters for arch:readdir:
   - directory_path: Directory to analyze (required)
   - max_depth: How deep to scan (default: 3)
   - include: File patterns to include (default: ['*.py', '*.md', etc.])
   - exclude: File patterns to exclude (default: ['__pycache__', '*.pyc', etc.])

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
                label = query[len("!delctx:"):]
                label = label.strip()
                
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
                file_path = query[len("arch:readfile:"):]
                file_path = file_path.strip()
                
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
                dir_path = query[len("arch:readdir:"):]
                dir_path = dir_path.strip()
                
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
                file_path = query[len("code:read:"):]
                file_path = file_path.strip()
                
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
            # Log which agent is handling the query
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
            else:
                mode_color = YELLOW
                agent_name = "Web Browser Agent"
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
