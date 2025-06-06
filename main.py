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
from The_Agents.shared_context_manager import SharedContextManager
from The_Agents.workflows import WorkflowOrchestrator

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

def create_status_bar_text(current_agent, mode, shared_manager=None):
    """Create status bar text for the bottom toolbar."""
    context = current_agent.context
    token_count = context.token_count
    max_tokens = context.max_tokens
    percentage = (token_count / max_tokens) * 100 if max_tokens > 0 else 0
    
    # Create progress bar
    bar_width = 20
    filled = int((percentage / 100) * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    # Color coding based on percentage - use valid HTML class names
    if percentage < 50:
        token_style = "good"
    elif percentage < 80:
        token_style = "warning"
    else:
        token_style = "danger"
    
    mode_style = "mode-code" if mode == AgentMode.CODE else "mode-arch"
    
    # Get collaboration info
    collab_info = ""
    if shared_manager:
        agent_name = "code" if mode == AgentMode.CODE else "architect"
        pending_tasks = shared_manager.get_pending_tasks(agent_name)
        if pending_tasks:
            task_count = len(pending_tasks)
            collab_info = f' │ <collab>📋 {task_count} tasks</collab>'
    
    # Use simpler HTML formatting that doesn't break XML parsing
    return HTML(
        f'<{mode_style}>[{mode.upper()}]</{mode_style}> │ '
        f'<{token_style}>Tokens: {token_count:,}/{max_tokens:,} ({percentage:.1f}%) [{bar}]</{token_style}> │ '
        f'<path>📁 {os.path.basename(context.working_directory)}</path>'
        f'{collab_info}'
    )

async def main():
    """Main function to run the dual-agent system with mode switching support."""
    # Initialize spaCy model at startup
    print(f"{YELLOW}Initializing spaCy model (this may take a moment)...{RESET}")
    await nlp_singleton.initialize(model_name="en_core_web_lg", disable=["parser"])
    
    # Initialize shared context manager and workflow orchestrator
    shared_manager = SharedContextManager()
    workflow_orchestrator = WorkflowOrchestrator(shared_manager)
    
    # Start in code agent mode by default
    current_mode = AgentMode.CODE
    code_agent = SingleAgent()
    architect_agent = ArchitectAgent()
    
    # Set up shared context manager and workflow orchestrator in both agents' metadata
    code_agent.context.metadata["shared_manager"] = shared_manager
    code_agent.context.metadata["agent_name"] = "code"
    code_agent.context.metadata["workflow_orchestrator"] = workflow_orchestrator
    architect_agent.context.metadata["shared_manager"] = shared_manager
    architect_agent.context.metadata["agent_name"] = "architect"
    architect_agent.context.metadata["workflow_orchestrator"] = workflow_orchestrator
    
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
    
    # Set up enhanced style with status bar colors
    style = Style.from_dict({
        'auto-suggestion': 'fg:#888888 italic',
        'bottom-toolbar': 'bg:#444444 fg:#ffffff',
        
        # Status bar styles - match the HTML class names above
        'good': 'fg:#00ff00 bold',
        'warning': 'fg:#ffff00 bold', 
        'danger': 'fg:#ff0000 bold',
        'mode-code': 'fg:#00ff00 bold',
        'mode-arch': 'fg:#00aaff bold',
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
            # Merge relevant context from code agent to architect
            architect_agent.context.merge_from(code_agent.context, merge_chat=False)
            print(f"\n{BLUE}Switching to Architect Agent mode.{RESET}")
            # Show handoff context
            handoff_context = shared_manager.get_agent_handoff_context("code", "architect")
            if handoff_context["pending_tasks"]:
                print(f"{YELLOW}📋 You have {len(handoff_context['pending_tasks'])} pending tasks from Code Agent{RESET}")
            display_mode_banner()
            print(f"\n{architect_agent.get_context_summary()}\n")
            continue
        elif query.strip().lower() == "!code" and current_mode == AgentMode.ARCHITECT:
            # Switch to code mode
            current_mode = AgentMode.CODE
            # Save context before switching
            await architect_agent.save_context()
            # Merge relevant context from architect agent to code agent
            code_agent.context.merge_from(architect_agent.context, merge_chat=False)
            print(f"\n{GREEN}Switching to Code Agent mode.{RESET}")
            # Show handoff context
            handoff_context = shared_manager.get_agent_handoff_context("architect", "code")
            if handoff_context["pending_tasks"]:
                print(f"{YELLOW}📋 You have {len(handoff_context['pending_tasks'])} pending tasks from Architect Agent{RESET}")
            display_mode_banner()
            print(f"\n{code_agent.get_context_summary()}\n")
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
            
        # Common special commands for both modes
        if query.strip().lower() == "!help":
            print(f"""
{BOLD}Agent Commands:{RESET}
!help       - Show this help message
!history    - Show chat history
!context    - Show full context summary 
!tokens     - Show detailed token usage information
!clear      - Clear chat history
!save       - Manually save context
!entity     - List tracked entities
!manualctx  - List all manually added context items
!delctx:label  - Remove manual context item by label
!code       - Switch to Code Agent mode
!architect  - Switch to Architect Agent mode
!collab     - Show collaboration status and pending tasks
!workflows  - Show active workflows and their status

{BOLD}Special Commands:{RESET}
code:read:path - Add file at path to persistent context
arch:readfile:path - Read and analyze a file with Architect Agent
arch:readdir:path - Analyze directory structure with Architect Agent
  Parameters for arch:readdir:
   - directory_path: Directory to analyze (required)
   - max_depth: How deep to scan (default: 3)
   - include: File patterns to include (default: ['*.py', '*.md', etc.])
   - exclude: File patterns to exclude (default: ['__pycache__', '*.pyc', etc.])

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
- get_workflow_status: Check status of a specific workflow
- list_active_workflows: List all active workflows

exit/quit   - Exit the program

{BOLD}Status Bar:{RESET}
The bottom toolbar shows:
- Current agent mode ([CODE] or [ARCHITECT])
- Token usage with visual progress bar and percentage
- Current working directory
- Pending collaboration tasks (📋 N tasks)
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