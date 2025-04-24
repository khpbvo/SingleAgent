"""
Enhanced SingleAgent implementation with improved context management:
- Tiktoken-based token counting
- Entity tracking
- Context summarization
- Persistent storage between sessions
- Rich context management like AgentSmith
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

# Configure logger for SingleAgent
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
os.makedirs("logs", exist_ok=True)
single_handler = RotatingFileHandler('logs/singleagent.log', maxBytes=10*1024*1024, backupCount=3)
single_handler.setLevel(logging.DEBUG)
single_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(single_handler)
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

# Import tools
from Tools.tools_single_agent import (
    run_ruff,
    run_pylint,
    run_pyright,
    run_command,
    read_file,
    create_colored_diff,
    apply_patch,
    change_dir,
    os_command,
    get_context,
    get_context_response,
    add_manual_context
)
from utils.project_info import discover_project_info
from agents.exceptions import MaxTurnsExceeded

# Import our enhanced context
from The_Agents.context_data import EnhancedContextData

# Path for persistent context storage
CONTEXT_FILE_PATH = os.path.join(os.path.expanduser("~"), ".singleagent_context.json")

# Constants
AGENT_INSTRUCTIONS = """
You are a code assistant capable of helping users write, edit, and patch code.
You have full control of the terminal and can run commands like sed, grep, ls, dir, cd, tail, python, and bash.
You can analyze code with pylint, ruff and pyright, generate colored diffs, and apply patches to files.
Your thinking should be thorough and so it's fine if it's very long. You can think step by step before and after each action you decide to take.

IMPORTANT: You have access to chat history and context information.
Always use the get_context tool to check the current context before responding.
When referring to previous conversations, use this history as reference.
If asked about previous interactions or commands, check the context using get_context.

# Context Management
You will have access to:
- Recent files the user has worked with
- Recent commands that have been executed
- Current project information
- Chat history with the user
- Manual context items added by the user (via 'code:read:path/to/file')

To see all context including manually added items, use the get_context tool.
You can also add new context items using the add_manual_context tool.

# Working Directory and File Handling
- Always be aware of the current working directory
- Use relative paths when referring to files
- Track which files the user is currently working with
- Remember the content and structure of important files

You MUST iterate and keep going until the problem is solved.
You already have everything you need to solve this problem in your tools, fully solve this autonomously before coming back to me.
Only terminate your turn when you are sure that the problem is solved. Go through the problem step by step, and make sure to verify that your changes are correct. NEVER end your turn without having solved the problem, and when you say you are going to make a tool call, make sure you ACTUALLY make the tool call, instead of ending your turn.
Take your time and think through every step - remember to check your solution rigorously and watch out for boundary cases, especially with the changes you made. Your solution must be perfect. If not, continue working on it. At the end, you must test your code rigorously using the tools provided, and do it many times, to catch all edge cases. If it is not robust, iterate more and make it perfect. Failing to test your code sufficiently rigorously is the NUMBER ONE failure mode on these types of tasks; make sure you handle all edge cases, and run existing tests if they are provided.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.
# Workflow
## High-Level Problem Solving Strategy
1. Understand the problem deeply. Carefully read the issue and think critically about what is required.
2. Investigate the codebase. Explore relevant files, search for key functions, and gather context.
3. Develop a clear, step-by-step plan. Break down the fix into manageable, incremental steps.
4. Implement the fix incrementally. Make small, testable code changes.
5. Debug as needed. Use debugging techniques to isolate and resolve issues.
6. Test frequently. Run tests after each change to verify correctness.
7. Iterate until the root cause is fixed and all tests pass.
8. Reflect and validate comprehensively. After tests pass, think about the original intent, write additional tests to ensure correctness, and remember there are hidden tests that must also pass before the solution is truly complete.

## 1. Deeply Understand the Problem
Carefully read the issue and think hard about a plan to solve it before coding.

## 2. Codebase Investigation
- Explore relevant files and directories.
- Search for key functions, classes, or variables related to the issue.
- Read and understand relevant code snippets.
- Identify the root cause of the problem.
- Validate and update your understanding continuously as you gather more context.

## 3. Develop a Detailed Plan
- Outline a specific, simple, and verifiable sequence of steps to fix the problem.
- Break down the fix into small, incremental changes.

## 4. Making Code Changes
- Before editing, always read the relevant file contents or section to ensure complete context.
- If a patch is not applied correctly, attempt to reapply it.
- Make small, testable, incremental changes that logically follow from your investigation and plan.

## 5. Debugging
- Make code changes only if you have high confidence they can solve the problem
- When debugging, try to determine the root cause rather than addressing symptoms
- Debug for as long as needed to identify the root cause and identify a fix
- Use print statements, logs, or temporary code to inspect program state, including descriptive statements or error messages to understand what's happening
- To test hypotheses, you can also add test statements or functions
- Revisit your assumptions if unexpected behavior occurs.

## 6. Testing
- Run tests frequently using `!python3 run_tests.py` (or equivalent).
- After each change, verify correctness by running relevant tests.
- If tests fail, analyze failures and revise your patch.
- Write additional tests if needed to capture important behaviors or edge cases.
- Ensure all tests pass before finalizing.

## 7. Final Verification
- Confirm the root cause is fixed.
- Review your solution for logic correctness and robustness.
- Iterate until you are extremely confident the fix is complete and all tests pass.

When suggesting code changes, follow this workflow:
1. Read and understand the code using the read_file tool
2. If needed, analyze the code using pylint
3. Generate improved or fixed code
4. Create a colored diff to show the changes
5. Format the patch in the expected format
6. Apply the patch using the apply_patch tool

Always clearly explain your thought process before taking actions.
For complex tasks, break down your approach into specific steps and explain each step.

Use your run_command to execute the apply_patch.py file to apply patches to files.
python apply_patch.py <<"EOF"
*** Begin Patch
[YOUR_PATCH]
*** End Patch
EOF

Where [YOUR_PATCH] is the actual content of your patch, specified in the following V4A diff format.

*** [ACTION] File: [path/to/file] -> ACTION can be one of Add, Update, or Delete.
For each snippet of code that needs to be changed, repeat the following:
[context_before] -> See below for further instructions on context.
- [old_code] -> Precede the old code with a minus sign.
+ [new_code] -> Precede the new, replacement code with a plus sign.
[context_after] -> See below for further instructions on context.

For instructions on [context_before] and [context_after]:
- By default, show 3 lines of code immediately above and 3 lines immediately below each change. If a change is within 3 lines of a previous change, do NOT duplicate the first change's [context_after] lines in the second change's [context_before] lines.
- If 3 lines of context is insufficient to uniquely identify the snippet of code within the file, use the @@ operator to indicate the class or function to which the snippet belongs. For instance, we might have:
@@ class BaseClass
[3 lines of pre-context]
- [old_code]
+ [new_code]
[3 lines of post-context]

- If a code block is repeated so many times in a class or function such that even a single @@ statement and 3 lines of context cannot uniquely identify the snippet of code, you can use multiple `@@` statements to jump to the right context. For instance:

@@ class BaseClass
@@ 	def method():
[3 lines of pre-context]
- [old_code]
+ [new_code]
[3 lines of post-context]

Note, then, that we do not use line numbers in this diff format, as the context is enough to uniquely identify code. An example of a message that you might pass as "input" to this function, in order to apply a patch, is shown below.

python apply_patch.py <<"EOF"
*** Begin Patch
*** Update File: pygorithm/searching/binary_search.py
@@ class BaseClass
@@     def search():
-        pass
+        raise NotImplementedError()

@@ class Subclass
@@     def search():
-        pass
+        raise NotImplementedError()

*** End Patch
EOF

File references can only be relative, NEVER ABSOLUTE. After the apply_patch command is run, python will always say "Done!", regardless of whether the patch was successfully applied or not. However, you can determine if there are issue and errors by looking at any warnings or logging lines printed BEFORE the "Done!" is output.



Remember to show your reasoning at each step of the process. Consider different approaches, evaluate trade-offs,
and explain why you chose a particular solution.
"""

class SingleAgent:
    """
    An enhanced single agent implementation for code assistance with:
    - Improved context management
    - Entity tracking
    - Persistent storage between sessions
    - Token management with tiktoken
    - Context summarization
    """
    
    def _apply_default_file_context(self, user_input: str) -> str:
        """
        If user mentions code changes but doesn't specify a file,
        automatically add the most recently edited file from context.
        """
        # 1. Skip if the input already mentions a file
        if re.search(r'\w+\.(py|js|ts|html|css|java|cpp|h|c|rb|go|rs|php)\b', user_input):
            return user_input
    
        # 2. Skip for common commands that aren't file operations
        command_patterns = [
            r'\b(cd|chdir|change\s+dir|change\s+directory|directory|switch\s+dir|mkdir)\b',
            r'\b(ls|dir|list)\b',
            r'\binstall\b',
            r'\b(!|help|clear|exit|quit|context|history|save|entity)\b',
        ]
    
        for pattern in command_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return user_input
    
        # 3. Only apply for specific code operation contexts
        if re.search(
            r'\b(add|append|insert|remove|delete|modify|update|refactor|rename|patch|fix|debug|implement|create)\b.{0,15}'
            r'(code|function|class|method|bug|issue|error|variable|import|module|feature)\b',
            user_input, 
            re.IGNORECASE
        ):
            # Prefer the actively tracked file ⇢ fall back to recents
            target = self.context.current_file or next(iter(self.context.get_recent_files()), None)
            if target:
                return f"{user_input} in {target}"
        return user_input
    
    def __init__(self):
        # ensure we always have a context attribute before async loading
        cwd = os.getcwd()
        self.context = EnhancedContextData(
            working_directory=cwd,
            project_name=os.path.basename(cwd),
            project_info=discover_project_info(cwd),
            current_file=None,
        )
        """Initialize the code assistant agent with all required tools and enhanced context."""
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
            name="CodeAssistant",
            model="gpt-4.1",
            instructions=AGENT_INSTRUCTIONS,
            tools=[
                run_ruff,
                run_pylint,
                run_pyright,
                run_command,
                read_file,
                create_colored_diff,
                apply_patch,
                change_dir,
                os_command,
                get_context,
                get_context_response,
                add_manual_context
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
            # Attempt to load existing context
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
    
    def _prepare_context_for_agent(self) -> None:
        """
        Prepare the agent's context by updating instructions with manual context info if needed.
        This ensures the agent is aware of all manually added context items.
        """
        # Check if we have manual context items to include
        if not hasattr(self.context, 'manual_context_items') or not self.context.manual_context_items:
            return
            
        # Create a brief summary of available manual context
        context_items = []
        for item in self.context.manual_context_items:
            context_items.append(f"- {item.label} (from: {item.source})")
            
        # Update the agent's instructions if needed
        original_instructions = AGENT_INSTRUCTIONS
        context_header = "# Available Manual Context Items:"
        context_items_str = "\n".join(context_items)
        context_footer = "\nUse get_context tool to view details and access this information."
        
        # Update agent with instructions that include context summary
        with_manual_context = f"{original_instructions}\n\n{context_header}\n{context_items_str}\n{context_footer}"
        
        # Update agent's instructions
        self.agent = Agent[EnhancedContextData](
            name="CodeAssistant",
            model="gpt-4.1",
            instructions=with_manual_context,
            tools=[
                run_ruff,
                run_pylint,
                run_pyright,
                run_command,
                read_file,
                create_colored_diff,
                apply_patch,
                change_dir,
                os_command,
                get_context,
                get_context_response,
                add_manual_context
            ]
        )
    
    async def run(self, user_input: str, stream_output: bool = True) -> str:
        """
        Run the agent with the given user input.
        
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
        await self._extract_entities_from_input(user_input)
        
        # Add user message to chat history
        self.context.add_chat_message("user", user_input)
        
        # Check if context should be summarized
        if self.context.should_summarize() and self.openai_client:
            print(f"{YELLOW}Context is large, summarizing...{RESET}")
            was_summarized = await self.context.summarize_if_needed(self.openai_client)
            if was_summarized:
                print(f"{GREEN}Context summarized successfully{RESET}")
        
        # Update agent with manual context info if available
        self._prepare_context_for_agent()
        
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
    
    async def _extract_entities_from_input(self, user_input: str):
        """
        Extract and track potential entities from user input using our enhanced async entity recognition.
        
        Args:
            user_input: The user's query or request
        """
        # Import here to avoid circular imports
        from The_Agents.entity_recognizer import extract_entities
        
        try:
            # Process the text with our async entity recognizer
            entities = await extract_entities(user_input)
            
            # Track all detected entities
            for entity_type, matches in entities.items():
                # Sort by confidence (highest first)
                matches.sort(key=lambda x: x["confidence"], reverse=True)
                
                # Log count of entities found per type
                entity_count = len(matches)
                if entity_count > 0:
                    logger.debug(f"Found {entity_count} entities of type {entity_type}")
                
                # Track each entity
                for match_data in matches:
                    entity_value = match_data["value"]
                    metadata = match_data.get("metadata", {})
                    
                    # Track in context with confidence level
                    confidence = match_data.get("confidence", 0.0)
                    if "confidence" not in metadata:
                        metadata["confidence"] = confidence
                        
                    # Add timestamp of when entity was detected
                    if "detected_at" not in metadata:
                        metadata["detected_at"] = datetime.now().isoformat()
                    
                    # Track in context
                    self.context.track_entity(entity_type, entity_value, metadata)
                    
                    # Special handling based on entity type
                    if entity_type == "file" and not self.context.current_file and confidence > 0.7:
                        # Promote high-confidence file mention to current file if it exists
                        if os.path.exists(entity_value):
                            self.context.current_file = entity_value
                            logger.debug(f"Setting current file to {entity_value}")
                    
                    elif entity_type == "task":
                        # Set active task
                        self.context.set_state("active_task", entity_value)
                        logger.debug(f"Setting active task to {entity_value}")
                    
                    elif entity_type == "programming_language" and confidence > 0.8:
                        # Track current programming language
                        self.context.set_state("current_language", entity_value)
                        logger.debug(f"Setting current language to {entity_value}")
                    
                    elif entity_type == "framework" and confidence > 0.8:
                        # Track current framework
                        self.context.set_state("current_framework", entity_value)
                        logger.debug(f"Setting current framework to {entity_value}")
                    
                    elif entity_type == "api_endpoint":
                        # Track API endpoints being discussed
                        endpoints = self.context.get_state("api_endpoints", [])
                        if entity_value not in [e["value"] for e in endpoints]:
                            endpoints.append({
                                "value": entity_value,
                                "metadata": metadata
                            })
                            self.context.set_state("api_endpoints", endpoints)
                    
                    elif entity_type == "error_message":
                        # Track error messages being addressed
                        self.context.set_state("current_error", entity_value)
                        logger.debug(f"Setting current error to {entity_value}")
            
            # Detailed logging for debugging
            logger.debug(f"Extracted entities summary: {json.dumps({k: len(v) for k, v in entities.items()})}")
            
        except Exception as e:
            # Fallback to regex approach if async extraction fails
            logger.error(f"Async entity extraction failed: {e}. Falling back to regex.")
            self._extract_entities_fallback(user_input)
    
    def _extract_entities_fallback(self, user_input: str):
        """
        Fallback method using basic regex for entity extraction if async method fails.
        This is simpler than the full async recognizer but covers essential entity types.
        
        Args:
            user_input: The user's query or request
        """
        logger.debug("Using fallback entity extraction")
        current_time = datetime.now().isoformat()
        
        # Extract potential file references (with more extensions)
        file_matches = re.findall(r'([\w\/\.-]+\.(?:py|js|ts|html|css|java|cpp|h|c|rb|go|rs|php|md|json|yaml|yml|toml|xml))', user_input, re.IGNORECASE)
        for file_path in file_matches:
            metadata = {
                "confidence": 0.7,
                "detected_at": current_time,
                "method": "fallback_regex"
            }
            
            if os.path.exists(file_path):
                metadata["exists"] = True
                metadata["confidence"] = 0.9
                
                # Promote existing file to current file
                if not self.context.current_file:
                    self.context.current_file = file_path
                    logger.debug(f"Fallback: Setting current file to {file_path}")
            
            self.context.track_entity("file", file_path, metadata)
        
        # Extract potential URLs
        url_matches = re.findall(r'https?://[^\s]+', user_input)
        for match in url_matches:
            self.context.track_entity("url", match, {
                "confidence": 0.85,
                "detected_at": current_time,
                "method": "fallback_regex"
            })
        
        # Extract potential command references
        if user_input.startswith('!') or user_input.startswith('$'):
            command = user_input[1:].strip()
            self.context.track_entity("command", command, {
                "confidence": 0.9,
                "detected_at": current_time,
                "method": "fallback_regex"
            })
        
        # Extract potential search queries
        search_match = re.match(r'^(search|find|look for)\s+(.*?)(?:\?|\.|$)', user_input, re.IGNORECASE)
        if search_match:
            query = search_match.group(2).strip()
            self.context.track_entity("search_query", query, {
                "confidence": 0.8,
                "detected_at": current_time,
                "method": "fallback_regex"
            })
            
        # Set active task if detected
        task_match = re.search(r'(implement|create|fix|debug|optimize|refactor|add|build|develop)\s+([^\.]+)(?:\.|$)', user_input, re.IGNORECASE)
        if task_match:
            task = task_match.group(0)
            self.context.set_state("active_task", task)
            self.context.track_entity("task", task, {
                "confidence": 0.8,
                "detected_at": current_time,
                "method": "fallback_regex"
            })
            logger.debug(f"Fallback: Setting active task to {task}")
            
        # Extract programming languages
        lang_matches = re.findall(r'\b(Python|JavaScript|TypeScript|Java|C\+\+|Go|Rust)\b', user_input)
        if lang_matches:
            lang = lang_matches[0]
            self.context.set_state("current_language", lang)
            self.context.track_entity("programming_language", lang, {
                "confidence": 0.85,
                "detected_at": current_time,
                "method": "fallback_regex"
            })
            logger.debug(f"Fallback: Setting current language to {lang}")
            
        # Log fallback results
        logger.debug("Fallback entity extraction complete")
    
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
        print(f"{CYAN}Starting agent...{RESET}")
        
        # Create enhanced context with current state
        context_summary = self.context.get_context_summary()
        
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
                    
                    # Track commands, file reads, etc. as entities
                    if tool_name and tool_params:
                        if tool_name == "os_command" or tool_name == "run_command":
                            if isinstance(tool_params, dict) and "command" in tool_params:
                                self.context.track_entity("command", tool_params["command"])
                        elif tool_name == "read_file":
                            if isinstance(tool_params, dict) and "file_path" in tool_params:
                                self.context.track_entity("file", tool_params["file_path"])
                    
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
                            
                            # Track file content from read_file as metadata
                            if isinstance(output, dict):
                                if 'file_path' in output and 'content' in output:
                                    self.context.track_entity(
                                        "file", 
                                        output['file_path'], 
                                        {"content_preview": output['content'][:100] if output['content'] else None}
                                    )
                            
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
    """Main function to run the SingleAgent REPL."""
    print(f"{GREEN}Initializing SingleAgent...{RESET}")
    agent = SingleAgent()
    print(f"{GREEN}SingleAgent ready.{RESET}")
    print(f"Use main.py to access the full agent system with all commands.")
    
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
        
        # Simple note about commands being in main.py
        if query.strip().startswith("!"):
            print(f"\n{YELLOW}Note: Please use main.py for full command support.{RESET}\n")
            continue

        # Run the agent with the query
        try:
            result = await agent.run(query)
            print(f"\n{BOLD}{RED}Agent:{RESET} {result}\n")
        except Exception as e:
            logger.error(f"Error running agent: {e}", exc_info=True)
            print(f"\n{RED}Error running agent: {e}{RESET}\n")