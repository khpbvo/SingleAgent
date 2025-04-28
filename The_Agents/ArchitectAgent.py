"""
Enhanced ArchitectAgent implementation with architectural analysis capabilities:
- Analyzes project structure
- Identifies design patterns
- Suggests architectural improvements
- Provides high-level architectural insights
- Maintains architecture entities in context
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

# Import tool usage utilities
from utilities.tool_usage import handle_stream_events

# Configure logger for ArchitectAgent
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
os.makedirs("logs", exist_ok=True)
architect_handler = RotatingFileHandler('logs/architectagent.log', maxBytes=10*1024*1024, backupCount=3)
architect_handler.setLevel(logging.DEBUG)
architect_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(architect_handler)
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
    RunItemStreamEvent, 
    RawResponsesStreamEvent,
    AgentUpdatedStreamEvent,
    RunContextWrapper
)


# Import architect tools
from Tools.architect_tools import (
    analyze_ast,
    analyze_project_structure,
    generate_todo_list,
    analyze_dependencies,
    detect_code_patterns,
    get_context,
    get_context_response,
    read_file,
    read_directory,
    add_manual_context,
    run_command,  # Added run_command tool
    write_file  
)

# Import custom context data model
from The_Agents.context_data import EnhancedContextData


class ArchitectAgent:
    """
    Architecture-focused agent with specialized tools and capabilities
    for analyzing and suggesting improvements to project structure and design.
    """
    
    def __init__(self, openai_client=None):
        """
        Initialize the architect agent with default configuration.
        
        Args:
            openai_client: Optional OpenAI client for API calls
        """
        self.openai_client = openai_client
        self.instructions = self._get_default_instructions()
        
        # Create agent
        self.agent = Agent[EnhancedContextData](
            name="ArchitectAgent",
            model="gpt-4.1",
            instructions=self.instructions,
            tools=[
                analyze_ast,
                analyze_project_structure,
                generate_todo_list,
                analyze_dependencies,
                detect_code_patterns,
                get_context,
                get_context_response,
                read_file,
                read_directory,
                add_manual_context,
                run_command,  # Added run_command tool
                write_file  
            ]
        )
        
        logger.debug("ArchitectAgent initialized")
        # Initialize context with default state
        cwd = os.getcwd()
        self.context = EnhancedContextData(
            working_directory=cwd,
            project_name=os.path.basename(cwd)
        )
        
    async def _load_context(self):
        """
        Load context data from persistent storage if available.
        """
        self.context = EnhancedContextData()  # Initialize empty context
        
        # Try to load persisted context 
        context_file = "architect_context.json"
        if os.path.exists(context_file):
            try:
                with open(context_file, 'r') as f:
                    data = json.load(f)
                    # Convert raw dict to EnhancedContextData
                    self.context = EnhancedContextData.from_dict(data)
                logger.debug(f"Loaded context from {context_file}")
            except Exception as e:
                logger.error(f"Error loading context: {e}")
                # Continue with empty context on error
        else:
            logger.debug("No saved context found, starting fresh")
            
        # Ensure context has required state
        if not hasattr(self.context, 'chat_messages'):
            self.context.chat_messages = []
            
        if not hasattr(self.context, 'entities'):
            self.context.entities = {}
            
        logger.debug(f"Context initialized with {len(self.context.chat_messages)} messages")
    
    async def save_context(self):
        """
        Save context data to persistent storage.
        """
        try:
            context_file = "architect_context.json"
            # Convert context object to serializable dictionary
            data = self.context.to_dict()
            
            with open(context_file, 'w') as f:
                json.dump(data, f)
                
            logger.debug(f"Context saved to {context_file}")
        except Exception as e:
            logger.error(f"Error saving context: {e}")
    
    def _get_default_instructions(self):
        """
    Create default instructions for the architect agent.
    
    Returns:
        String with detailed instruction set
    """
        return """You are an Architecture Expert Assistant specialized in software design, architecture analysis, 
and code organization. Your purpose is to help developers understand, design, and implement 
better software architectures.

CAPABILITIES:
- Analyze project structures and suggest organizational improvements
- Identify design patterns or recommend appropriate patterns for specific problems
- Provide guidance on architecture styles (microservices, monoliths, etc.)
- Help with dependency management and code coupling issues
- Offer refactoring suggestions to improve code organization
- Teach architectural concepts and principles
- Create and manage TODO lists and project plans
- Write content to files and execute shell commands

AVAILABLE TOOLS:
- analyze_project_structure: Get a high-level view of the project organization
- analyze_ast: Analyze code at the abstract syntax tree level
- detect_code_patterns: Find common design patterns in the codebase
- analyze_dependencies: Identify dependencies between modules
- generate_todo_list: Create a prioritized list of architectural improvements
- read_file: Read the contents of specific files
- read_directory: List the contents of directories
- write_file: Write content to files (for TODO lists, documentation, etc.)
- run_command: Execute shell commands for project analysis

PRINCIPLES TO FOLLOW:
1. Focus on architectural concerns rather than implementation details
2. Explain the reasoning behind your suggestions
3. Consider trade-offs between different architectural approaches
4. Respect existing architecture when suggesting changes
5. Consider maintainability, scalability, and extensibility in your recommendations
6. When suggesting patterns, explain how they solve the specific problem

When asked about code or architecture, first use appropriate tools to analyze the current state
before making recommendations. Always explain architectural concepts in an educational way when they come up.

For TODO lists:
1. You can now create and manage TODO lists by generating them with generate_todo_list
2. Use write_file to save these TODO lists to disk (e.g., "TODO.md", "project_plan.md")
3. Structure TODO lists with clear priorities, dependencies, and estimated completion times
4. Include task categories (infrastructure, feature, documentation, testing)
5. For existing projects, analyze the codebase first to provide context-aware tasks
"""
    
    def _prepare_context_for_agent(self):
        # 1) Get a fresh summary
        summary = self.context.get_context_summary()
        # 2) Prepend it to your instructions
        instr = self._get_default_instructions()
        instr += "\n\n--- CURRENT CONTEXT ---\n" + summary + "\n-----------------------\n"
        # 3) Re-create agent with new instructions
        self.agent = Agent[EnhancedContextData](
            name="ArchitectAgent",
            model="gpt-4.1",
            instructions=instr,
            tools=self.agent.tools
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
                        
                    # Architecture-specific entity handling
                    elif entity_type == "design_pattern" and confidence > 0.75:
                        patterns = self.context.get_state("design_patterns", [])
                        if entity_value not in patterns:
                            patterns.append(entity_value)
                            self.context.set_state("design_patterns", patterns)
                            
                    elif entity_type == "architecture_concept" and confidence > 0.75:
                        concepts = self.context.get_state("architecture_concepts", [])
                        if entity_value not in concepts:
                            concepts.append(entity_value)
                            self.context.set_state("architecture_concepts", concepts)
            
            # Detailed logging for debugging
            logger.debug(f"Extracted entities summary: {json.dumps({k: len(v) for k, v in entities.items()})}")
            
        except Exception as e:
            # Fallback to regex approach if async extraction fails
            logger.error(f"Async entity extraction failed: {e}. Falling back to regex.")
            self._extract_entities_fallback(user_input)
    
    def _extract_entities_fallback(self, user_input: str):
        """
        Fallback method using basic regex for entity extraction if async method fails.
        This version focuses on architecture-related patterns.
        
        Args:
            user_input: The user's query or request
        """
        logger.debug("Using fallback entity extraction for ArchitectAgent")
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
            
        # Set active task if detected (architecture-focused)
        task_match = re.search(r'(analyze|design|architect|plan|review|refactor|model|structure)\s+([^\.]+)(?:\.|$)', user_input, re.IGNORECASE)
        if task_match:
            task = task_match.group(0)
            self.context.set_state("active_task", task)
            self.context.track_entity("task", task, {
                "confidence": 0.8,
                "detected_at": current_time,
                "method": "fallback_regex"
            })
            logger.debug(f"Fallback: Setting active task to {task}")
        
        # Look for specific architecture-related entities
        design_patterns = ['singleton', 'factory', 'observer', 'decorator', 'strategy', 'facade', 
                        'adapter', 'composite', 'command', 'iterator', 'mediator', 'template', 
                        'visitor', 'state', 'bridge', 'flyweight']
        
        for pattern in design_patterns:
            if re.search(fr'\b{pattern}\b', user_input, re.IGNORECASE):
                self.context.track_entity("design_pattern", pattern, {
                    "confidence": 0.85,
                    "detected_at": current_time,
                    "method": "fallback_regex"
                })
                patterns = self.context.get_state("design_patterns", [])
                if pattern not in patterns:
                    patterns.append(pattern)
                    self.context.set_state("design_patterns", patterns)
            
        # Track architecture concepts (expanded list)
        arch_concepts = ['module', 'component', 'service', 'microservice', 'architecture',
                        'dependency', 'coupling', 'cohesion', 'solid', 'dry', 'interface',
                        'abstraction', 'inheritance', 'composition', 'domain', 'bounded context',
                        'clean architecture', 'hexagonal', 'mvc', 'mvvm']
                        
        for concept in arch_concepts:
            if re.search(fr'\b{concept}\b', user_input, re.IGNORECASE):
                self.context.track_entity("architecture_concept", concept, {
                    "confidence": 0.85,
                    "detected_at": current_time,
                    "method": "fallback_regex"
                })
                
                concepts = self.context.get_state("architecture_concepts", [])
                if concept not in concepts:
                    concepts.append(concept)
                    self.context.set_state("architecture_concepts", concepts)
                    
        # Log fallback results
        logger.debug("Fallback architecture entity extraction complete")
    
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
        
        # Use the shared stream event handler 
        output_text_buffer = await handle_stream_events(
            result.stream_events(),
            self.context,
            logger,
            ItemHelpers
        )
        
        # Log end of streamed run
        logger.debug(json.dumps({
            "event": "_run_streamed_end",
            "output_length": len(output_text_buffer)
        }))
        
        return output_text_buffer

    def get_context_summary(self) -> str:
        """Return a summary of the current context."""
        return self.context.get_context_summary()

    def get_chat_history_summary(self) -> str:
        """Return a summary of the chat history."""
        return self.context.get_chat_summary()

    def clear_chat_history(self) -> None:
        """Clear the chat history and reset tokens."""
        self.context.clear_chat_history()