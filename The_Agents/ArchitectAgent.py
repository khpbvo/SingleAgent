"""
Enhanced ArchitectAgent implementation with AST-based project insights:
- Python AST module for code structure analysis
- Project architecture planning
- Generating TODO lists for the CodeAgent
- Dependency mapping and visualization
- Code pattern recognition
- Shared context with SingleAgent
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
import ast

# Configure logger for ArchitectAgent
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
os.makedirs("logs", exist_ok=True)
arch_handler = RotatingFileHandler('logs/architectagent.log', maxBytes=10*1024*1024, backupCount=3)
arch_handler.setLevel(logging.DEBUG)
arch_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(arch_handler)
logger.propagate = False

# ANSI color codes for REPL
GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW = "\033[33m"
BLUE  = "\033[34m" 
CYAN  = "\033[36m"
BOLD  = "\033[1m"
RESET = "\033[0m"

# Import OpenAI ResponseTextDeltaEvent for streaming
try:
    from openai.types.responses import ResponseTextDeltaEvent
except ImportError:
    # Define a placeholder class for older OpenAI versions
    class ResponseTextDeltaEvent:
        def __init__(self, delta=""):
            self.delta = delta

from agents import (
    Agent, 
    Runner, 
    ItemHelpers, 
    function_tool,
    RunContextWrapper,
    StreamEvent
)
from agents.stream_events import RunItemStreamEvent, RawResponsesStreamEvent, AgentUpdatedStreamEvent
from pydantic import BaseModel, Field

# Import OpenAI for summarization
from openai import OpenAI, AsyncOpenAI

# Import architect tools
from Tools.architect_tools import (
    analyze_ast,
    analyze_project_structure,
    generate_todo_list,
    analyze_dependencies,
    detect_code_patterns,
    get_context,
    get_context_response
)
from utils.project_info import discover_project_info
from agents.exceptions import MaxTurnsExceeded

# Import our enhanced context
from The_Agents.context_data import EnhancedContextData

# Path for persistent context storage
CONTEXT_FILE_PATH = os.path.join(os.path.expanduser("~"), ".architectagent_context.json")

# Constants
AGENT_INSTRUCTIONS = """
You are an AI software architect assistant, specialized in analyzing codebases and planning software projects.
You excel at understanding existing code structures through AST analysis, detecting code patterns, mapping dependencies,
and creating comprehensive TODO lists for implementation.

You can analyze Python projects to reveal their structure, dependencies, and architectural patterns.
You have a deep understanding of software design principles, patterns, anti-patterns, and best practices.
You can provide strategic guidance on software architecture decisions.

IMPORTANT: You have access to chat history and context information.
Always use the get_context tool to check the current context before responding.
When referring to previous conversations, use this history as reference.
If asked about previous interactions or commands, check the context using get_context.

# Analysis Capabilities
- AST Analysis: Analyze Python code structure at the abstract syntax tree level
- Project Structure: Map out directories and files to understand project organization
- Dependency Analysis: Identify module dependencies and potential issues
- Code Pattern Detection: Recognize design patterns and anti-patterns
- Task Planning: Generate structured TODO lists for implementation

# Software Architecture Skills
- Design Pattern Recognition and Application
- Modular Design Principles
- Component Coupling Analysis
- Cohesion Optimization
- Technical Debt Identification
- Scalability Planning
- Maintainability Assessment

# Context Management
You will have access to:
- Recent files the user has worked with
- Recent commands that have been executed
- Current project information
- Chat history with the user

# Working with the Code Agent
When creating TODO lists, structure them in a way that's clear for the Code Agent to implement:
1. Break down large features into specific, manageable tasks
2. Specify dependencies between tasks
3. Prioritize tasks by importance and implementation order
4. Include clear acceptance criteria for each task
5. Tag tasks with appropriate categories (setup, core, testing, etc.)

# Planning Guidelines
When creating plans:
1. Start with high-level architecture decisions
2. Identify core components and their relationships
3. Consider proper abstractions and separation of concerns
4. Factor in error handling, logging, and diagnostics
5. Think about future extensibility and maintenance

# Code Analysis Guidelines
When analyzing code:
1. Look for design patterns and anti-patterns
2. Assess module cohesion and coupling
3. Identify opportunities for refactoring
4. Evaluate naming conventions and code clarity
5. Check for potential performance issues

You should always approach problems systematically, breaking them down into architectural components
and implementation steps. Provide clear rationales for your design decisions and recommendations.
"""

class ArchitectAgent:
    """
    An enhanced architect agent implementation for code analysis and project planning with:
    - Python AST module for code structure analysis
    - Project architecture planning
    - Generating TODO lists for the CodeAgent
    - Dependency mapping and visualization
    - Code pattern recognition
    - Shared context with SingleAgent
    """
    
    def _apply_default_file_context(self, user_input: str) -> str:
        """
        If user mentions code analysis but doesn't specify a file,
        automatically add the most recently edited file from context.
        """
        # 1. Skip if the input already mentions a file
        if re.search(r'\w+\.(py|js|ts|html|css|java|cpp|h|c|rb|go|rs|php)\b', user_input):
            return user_input
    
        # 2. Skip for common commands that aren't file operations
        command_patterns = [
            r'\b(cd|chdir|change\s+dir|change\s+directory|directory|switch\s+dir|mkdir)\b',
            r'\b(ls|dir|list)\b',
            r'\b(install|todo)\b',
            r'\b(!|help|clear|exit|quit|context|history|save|entity)\b',
        ]
    
        for pattern in command_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return user_input
    
        # 3. Only apply for specific architecture analysis contexts
        if re.search(
            r'\b(analyze|understand|review|examine|explain|check|diagram|visualize|map|structure)\b.{0,15}'
            r'(code|architecture|project|module|class|inheritance|function|method|pattern|dependency)\b',
            user_input, 
            re.IGNORECASE
        ):
            # Prefer the actively tracked file ⇢ fall back to recents
            target = self.context.current_file or next(iter(self.context.get_recent_files()), None)
            if target:
                return f"{user_input} in {target}"
        return user_input
    
    def __init__(self):
        """Initialize the architect agent with all required tools and shared context."""
        # Attempt to load existing context or create new one
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # no loop running → safe to run synchronously
            asyncio.run(self._load_context())
        else:
            # loop already running → schedule as background task
            loop.create_task(self._load_context())
    
        # Safety measure: Reset current_file if user explicitly starts a new session
        # (This helps avoid file fixation issues even if context was loaded)
        if hasattr(self, 'context') and self.context.current_file:
            logger.info(f"Safely clearing current_file ({self.context.current_file}) for new session")
            self.context.current_file = None
        
        # Create the enhanced agent with all tools
        self.agent = Agent[EnhancedContextData](
            name="ArchitectAssistant",
            model="gpt-4.1",
            instructions=AGENT_INSTRUCTIONS,
            tools=[
                analyze_ast,
                analyze_project_structure,
                generate_todo_list,
                analyze_dependencies,
                detect_code_patterns,
                get_context,
                get_context_response
            ]
        )
        
        # Initialize the OpenAI client for summarization
        try:
            self.openai_client = AsyncOpenAI()
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")
            self.openai_client = None
    
    async def _load_context(self):
        """Load context from persistent storage or create new if not found."""
        try:
            # Attempt to load existing context - Use the same context file as SingleAgent
            self.context = await EnhancedContextData.load_from_json(CONTEXT_FILE_PATH)
            logger.info(f"Loaded context from {CONTEXT_FILE_PATH}")
        
            # Update working directory to current directory
            if self.context.working_directory != os.getcwd():
                logger.info(f"Updating working directory from {self.context.working_directory} to {os.getcwd()}")
                self.context.working_directory = os.getcwd()
            
                # Reset current_file when working directory changes to prevent file fixation
                if self.context.current_file:
                    logger.info(f"Resetting current_file from {self.context.current_file} to None due to directory change")
                    self.context.current_file = None
            
                # Refresh project info
                self.context.project_info = discover_project_info(os.getcwd())
        
        except Exception as e:
            # If loading fails, create new context
            logger.warning(f"Failed to load context: {e}, creating new context")
            cwd = os.getcwd()
            self.context = EnhancedContextData(
                working_directory=cwd,
                project_name=os.path.basename(cwd),
                project_info=discover_project_info(cwd),
                current_file=None,
            )
    
    async def save_context(self):
        """Save context to persistent storage."""
        try:
            await self.context.save_to_json(CONTEXT_FILE_PATH)
            logger.info(f"Saved context to {CONTEXT_FILE_PATH}")
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
    
    async def run(self, user_input: str, stream_output: bool = True) -> str:
        """
        Run the architect agent with the given user input.
        
        Args:
            user_input: The user's query or request
            stream_output: Whether to stream the output or wait for completion
            
        Returns:
            The agent's response
        """
        # Ensure context is loaded before running
        if not hasattr(self, 'context'):
            await self._load_context()
            
        # Preprocess: add default file context if needed
        user_input = self._apply_default_file_context(user_input)
        
        # Log start of run
        logger.debug(json.dumps({"event": "run_start", "user_input": user_input}))
        
        # Process input for potential entities
        self._extract_entities_from_input(user_input)
        
        # Add user message to chat history
        self.context.add_chat_message("user", user_input)
        
        # Check if context should be summarized
        if self.context.should_summarize() and self.openai_client:
            print(f"{YELLOW}Context is large, summarizing...{RESET}")
            was_summarized = await self.context.summarize_if_needed(self.openai_client)
            if was_summarized:
                print(f"{GREEN}Context summarized successfully{RESET}")
        
        # Run the agent
        if stream_output:
            out = await self._run_streamed(user_input)
        else:
            res = await Runner.run(
                starting_agent=self.agent,
                input=user_input,
                context=self.context,
            )
            out = res.final_output
        
        # Add assistant response to chat history
        self.context.add_chat_message("assistant", out)
        
        # Save context after each run
        await self.save_context()
        
        # Log end of run
        logger.debug(json.dumps({
            "event": "run_end", 
            "output": out,
            "chat_history_length": len(self.context.chat_messages),
            "token_count": self.context.token_count
        }))
        
        return out
    
    def _extract_entities_from_input(self, user_input: str):
        """
        Extract and track potential entities from user input.
        
        Args:
            user_input: The user's query or request
        """
        # Extract potential file references
        file_matches = re.findall(r'([\w\/\.-]+\.(?:py|js|ts|html|css|java|cpp|h|c|rb|go|rs|php))', user_input, re.IGNORECASE)
        for file_path in file_matches:
            self.context.track_entity("file", file_path)
            # **Promote first explicit mention this turn to current file**
            if not self.context.current_file:
                self.context.current_file = file_path
        
        # Extract potential URLs
        url_matches = re.findall(r'https?://[^\s]+', user_input)
        for match in url_matches:
            self.context.track_entity("url", match)
        
        # Extract potential command references
        if user_input.startswith('!') or user_input.startswith('$'):
            command = user_input[1:].strip()
            self.context.track_entity("command", command)
        
        # Extract potential search queries
        if re.match(r'^(search|find|look for)\s+', user_input, re.IGNORECASE):
            query = re.sub(r'^(search|find|look for)\s+', '', user_input, flags=re.IGNORECASE)
            self.context.track_entity("search_query", query)
            
        # Set active task if detected
        task_match = re.search(r'(analyze|design|architect|plan|review|refactor)\s+([^\.]+)', user_input, re.IGNORECASE)
        if task_match:
            task = task_match.group(0)
            self.context.set_state("active_task", task)
        
        # Look for specific architecture-related entities
        pattern_match = re.search(r'(pattern|singleton|factory|observer|decorator)\b', user_input, re.IGNORECASE)
        if pattern_match:
            pattern = pattern_match.group(0)
            self.context.track_entity("design_pattern", pattern)
            
        # Track architecture concepts
        arch_concepts = ['module', 'component', 'service', 'architecture', 'dependency', 'coupling', 'cohesion']
        for concept in arch_concepts:
            if re.search(fr'\b{concept}\b', user_input, re.IGNORECASE):
                self.context.track_entity("architecture_concept", concept)
    
    async def _run_streamed(self, user_input: str) -> str:
        """
        Run the agent with streamed output.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            The final output from the agent
        """
        # Log start of streamed run
        logger.debug(json.dumps({"event": "_run_streamed_start", "user_input": user_input}))
        print(f"{CYAN}Starting architect agent...{RESET}")
        
        # Run the agent with streaming
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=user_input,
            max_turns=999,  # Increased for complex tasks
            context=self.context,
        )
        
        # Status indicators
        tool_status = f"{YELLOW}⚙{RESET}"  # Tool execution
        thinking_chars = ["⋮", "⋰", "⋯", "⋱"]  # Rotating dots pattern
        handoff_status = f"{BLUE}→{RESET}"  # Handoff to another agent
        
        # Animation variables
        thinking_index = 0
        last_animation_time = asyncio.get_event_loop().time()
        animation_interval = 0.2  # seconds between animation frames
        
        # Output buffer for collecting the response
        output_text_buffer = ""
        
        # Print initial thinking indicator
        print(f"{thinking_chars[thinking_index]} ", end="", flush=True)
        
        try:
            async for event in result.stream_events():
                # Animate the thinking indicator while waiting
                current_time = asyncio.get_event_loop().time()
                if current_time - last_animation_time > animation_interval:
                    if not output_text_buffer:  # Only animate if no output yet
                        # Clear the current indicator
                        print("\r", end="", flush=True)
                        # Update the animation
                        thinking_index = (thinking_index + 1) % len(thinking_chars)
                        print(f"{thinking_chars[thinking_index]} ", end="", flush=True)
                        last_animation_time = current_time
                
                # Process raw response events for token-by-token streaming
                if isinstance(event, RawResponsesStreamEvent):
                    if hasattr(event, 'data') and isinstance(event.data, ResponseTextDeltaEvent):
                        # Clear thinking indicator if this is first text
                        if not output_text_buffer:
                            print("\r" + " " * 10 + "\r", end="", flush=True)  # Clear indicator
                        
                        # Print text deltas in real-time
                        delta = event.data.delta
                        print(delta, end="", flush=True)
                        output_text_buffer += delta
                    continue  # Continue to next event after processing
                
                # Handle agent handoff/update events
                if isinstance(event, AgentUpdatedStreamEvent):
                    print(f"\n{handoff_status} Handoff to {event.new_agent.name}", flush=True)
                    continue
                    
                # Only process run item events
                if not isinstance(event, RunItemStreamEvent):
                    continue
                    
                item = event.item
                
                # Track tool calls for entity tracking
                if item.type == 'tool_call_item':
                    # Extract tool name and parameters
                    tool_name = getattr(item, 'name', None) or getattr(item, 'tool_name', None)
                    tool_params = getattr(item, 'params', None) or getattr(item, 'input', None)
                    
                    # Format tool parameters for display
                    params_str = ""
                    if tool_params:
                        if isinstance(tool_params, dict):
                            params_keys = list(tool_params.keys())
                            if len(params_keys) > 2:
                                params_str = f"({params_keys[0]}=..., +{len(params_keys)-1} more)"
                            else:
                                params_str = f"({', '.join(params_keys)})"
                    
                    if tool_name:
                        print(f"\n{tool_status} {tool_name}{params_str}", flush=True)
                    else:
                        print(f"\n{tool_status} Tool was called", flush=True)
                
                # Tool output
                elif item.type == 'tool_call_output_item':
                    # Handle output from tool calls
                    output_summary = ""
                    try:
                        if hasattr(item, 'output'):
                            output = item.output
                            
                            # Build a concise summary for general display
                            if isinstance(output, dict):
                                if 'error' in output:
                                    output_summary = f"Error: {str(output['error'])[:50]}..."
                                else:
                                    keys = list(output.keys())
                                    output_summary = f"{len(keys)} fields: {', '.join(keys[:3])}"
                                    if len(keys) > 3:
                                        output_summary += f", +{len(keys)-3} more"
                            elif isinstance(output, list):
                                output_summary = f"{len(output)} items"
                            else:
                                output_str = str(output)
                                output_summary = output_str[:47] + "..." if len(output_str) > 50 else output_str
                    except Exception as e:
                        logger.warning(f"Could not summarize tool output: {str(e)}")
                    
                    # Show output summary if available
                    if output_summary:
                        print(f"⮑ {output_summary}", flush=True)
                
                # Assistant message output (don't show separately if already shown via streaming)
                elif item.type == 'message_output_item':
                    # Use the helper function to extract just the text content without duplication
                    content = ItemHelpers.text_message_output(item)
                    # Only print non-empty content if no raw streaming occurred to avoid duplicates
                    if content.strip() and not output_text_buffer:
                        print(content, end='', flush=True)
                        output_text_buffer = content
                
                # Handle other event types if needed
                else:
                    continue
            
        except MaxTurnsExceeded as e:
            print(f"\n[Error] Max turns exceeded: {e}\n")
            logger.debug(json.dumps({"event": "max_turns_exceeded", "error": str(e)}))
        except Exception as e:
            logger.error(f"Error handling streamed response: {str(e)}", exc_info=True)
            print(f"\nError handling response: {str(e)}")
            
        # Print a newline at the end to ensure clean formatting
        print("")
        
        # Final output (Agent reply)
        final = result.final_output
        
        # Count tokens for the agent's response
        response_tokens = self.context.count_tokens(final)
        logger.info(f"Response size: ~{response_tokens} tokens")
        
        # Update context with token count from response
        self.context.update_token_count(response_tokens)
        
        logger.debug(json.dumps({
            "event": "_run_streamed_end", 
            "final_output": final,
            "token_count": self.context.token_count
        }))
        
        return final

    def get_chat_history_summary(self) -> str:
        """Return a summary of the chat history for display."""
        return self.context.get_chat_summary()
    
    def get_context_summary(self) -> str:
        """Return a full summary of the current context."""
        return self.context.get_context_summary()
    
    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        self.context.clear_chat_history()
        logger.debug(json.dumps({"event": "chat_history_cleared"}))

async def main():
    """Main function to run the ArchitectAgent REPL."""
    print(f"{GREEN}Initializing ArchitectAgent...{RESET}")
    agent = ArchitectAgent()
    print(f"{GREEN}ArchitectAgent ready.{RESET}")
    print(f"Type {BOLD}!help{RESET} for command list or enter a query.")
    
    # Display context summary on startup
    print(f"\n{CYAN}Current context:{RESET}")
    print(agent.get_context_summary())
    print()
    
    # Enter REPL loop
    while True:
        try:
            query = input(f"{BOLD}{GREEN}User:{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            # Save context before exit
            await agent.save_context()
            break
            
        if not query.strip():
            continue
            
        if query.strip().lower() in ("exit", "quit"):
            print("Goodbye.")
            # Save context before exit
            await agent.save_context()
            break
        
        # Special commands
        if query.strip().lower() == "!help":
            print(f"""
{BOLD}ArchitectAgent Commands:{RESET}
!help       - Show this help message
!history    - Show chat history
!context    - Show full context summary
!clear      - Clear chat history
!save       - Manually save context
!entity     - List tracked entities
!code       - Switch to Code Agent mode
exit/quit   - Exit the program
""")
            continue
        elif query.strip().lower() == "!history":
            print(f"\n{agent.get_chat_history_summary()}\n")
            continue
        elif query.strip().lower() == "!context":
            print(f"\n{agent.get_context_summary()}\n")
            continue
        elif query.strip().lower() == "!clear":
            agent.clear_chat_history()
            print("\nChat history cleared.\n")
            continue
        elif query.strip().lower() == "!save":
            await agent.save_context()
            print("\nContext saved.\n")
            continue
        elif query.strip().lower() == "!entity":
            entities = agent.context.active_entities
            if not entities:
                print("\nNo tracked entities.\n")
                continue
                
            print(f"\n{BOLD}Tracked Entities:{RESET}")
            for entity_type in ["file", "command", "url", "search_query", "design_pattern", "architecture_concept"]:
                type_entities = [e for e in entities.values() if e.entity_type == entity_type]
                if type_entities:
                    print(f"\n{BOLD}{entity_type.capitalize()}s:{RESET}")
                    # Sort by access count (most frequent first)
                    type_entities.sort(key=lambda e: e.access_count, reverse=True)
                    for i, entity in enumerate(type_entities[:10]):  # Show top 10
                        print(f"  {i+1}. {entity.value} (accessed {entity.access_count} times)")
            print()
            continue
        elif query.strip().lower() == "!code":
            print("\nSwitching to Code Agent mode. Please use main.py to continue.\n")
            # Save context before switching
            await agent.save_context()
            break

        # Run the agent with the query
        try:
            result = await agent.run(query)
            print(f"\n{BOLD}{RED}Agent:{RESET} {result}\n")
        except Exception as e:
            logger.error(f"Error running agent: {e}", exc_info=True)
            print(f"\n{RED}Error running agent: {e}{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())