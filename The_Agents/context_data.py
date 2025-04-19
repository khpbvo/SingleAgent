"""
Enhanced context system for SingleAgent with features from AgentSmith:
- Entity tracking (files, commands, URLs)
- Accurate token counting with tiktoken
- Session state management
- Conversation summarization
- Persistent storage between sessions
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Union, Set, cast
import os
import json
import logging
import time
import hashlib
import tiktoken  # For accurate token counting

# Configure logger
logger = logging.getLogger("SingleAgent.Context")
logger.setLevel(logging.DEBUG)

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

# Add a handler for the context logger
context_handler = logging.FileHandler('logs/context.log')
context_handler.setLevel(logging.DEBUG)
context_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(context_handler)

# Import pydantic for model validation
from pydantic import BaseModel, Field


class ContextSummary(BaseModel):
    """Model for context summarization."""
    summary: str = Field(description="Summary of the context")
    timestamp: float = Field(description="Timestamp of the summarization")
    tokens_before: int = Field(description="Token count before summarization")
    tokens_after: int = Field(description="Token count after summarization")


class EntityReference(BaseModel):
    """Model for tracking entities in conversation (files, URLs, etc)."""
    entity_type: str = Field(description="Type of entity (file, url, search_query, command, etc.)")
    entity_id: str = Field(description="Unique identifier for the entity")
    value: str = Field(description="The actual entity value (path, url, command, etc.)")
    metadata: Dict[str, Any] = Field(description="Additional metadata about the entity", default_factory=dict)
    last_access: float = Field(description="Last time this entity was accessed", default_factory=time.time)
    access_count: int = Field(description="Number of times this entity was accessed", default=1)


class MemoryItem(BaseModel):
    """A memory item with timestamp and metadata - for backward compatibility"""
    content: str = Field(description="The main content of the memory item")
    item_type: str = Field(description="Type of item ('file', 'person', 'command', etc.)")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this item was added")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional information")


class EnhancedContextData(BaseModel):
    """
    Enhanced context data with:
    - Token tracking
    - Entity tracking
    - Session state
    - Conversation history with roles
    - Summarization capabilities
    - Persistence through JSON
    """
    # Basic project info
    working_directory: str = Field(description="Current working directory")
    project_info: Optional[Dict[str, Any]] = Field(None, description="Information about the project")
    project_name: str = Field(default="DefaultProject", description="Name of the current project")
    
    # Token management
    token_count: int = Field(default=0, description="Current token count")
    max_tokens: int = Field(default=180000, description="Maximum tokens before summarization")
    summarization_threshold: float = Field(default=0.8, description="Threshold ratio for summarization")
    summaries: List[ContextSummary] = Field(default_factory=list, description="History of context summaries")
    
    # Chat history
    chat_messages: List[Dict[str, Any]] = Field(default_factory=list, description="Chat message history with metadata")
    max_chat_messages: int = Field(default=25, description="Maximum number of chat messages to keep")
    
    # Entity tracking
    active_entities: Dict[str, EntityReference] = Field(default_factory=dict, description="Currently tracked entities")
    current_file: Optional[str] = Field(None, description="Currently active file")
    
    # Session state (for temporary context info)
    session_state: Dict[str, Any] = Field(default_factory=dict, description="Temporary state information")
    
    # Legacy memory items (for backward compatibility)
    memory_items: List[MemoryItem] = Field(default_factory=list, description="Legacy remembered items")
    
    # Metadata
    creation_time: float = Field(default_factory=time.time, description="When this context was created")
    last_updated: float = Field(default_factory=time.time, description="When this context was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")
    
    # Embedding cache (if needed for semantic search later)
    embedding_cache: Dict[str, List[float]] = Field(default_factory=dict, description="Cache of text embeddings")

    # Tokenizers (initialized on demand)
    _tokenizer: Any = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize metadata with basic info
        self.metadata.update({
            "os": os.name,
            "creation_time": datetime.fromtimestamp(self.creation_time).isoformat(),
            "project_id": hashlib.md5(f"{self.project_name}:{self.working_directory}".encode()).hexdigest()
        })
    
    def get_tokenizer(self):
        """Get or initialize the tokenizer."""
        if self._tokenizer is None:
            # Use cl100k_base for compatibility with most GPT models
            self._tokenizer = tiktoken.get_encoding("cl100k_base")
        return self._tokenizer
    
    def count_tokens(self, text: str) -> int:
        """
        Accurately count tokens using tiktoken.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Token count
        """
        if not text:
            return 0
            
        try:
            tokenizer = self.get_tokenizer()
            tokens = tokenizer.encode(text)
            return len(tokens)
        except Exception as e:
            logger.warning(f"Error counting tokens: {str(e)}, falling back to estimation")
            # Fallback to estimation (4 chars ≈ 1 token)
            return len(text) // 4
    
    def update_token_count(self, new_tokens: int) -> None:
        """
        Update the token count with validation.
        
        Args:
            new_tokens: Number of tokens to add
        """
        if not isinstance(new_tokens, int) or new_tokens < 0:
            logger.warning(f"Invalid token count: {new_tokens}, ignoring")
            return
            
        self.token_count += new_tokens
        self.last_updated = time.time()
        logger.debug(f"Token count updated to {self.token_count}")
    
    def should_summarize(self) -> bool:
        """
        Check if context should be summarized.
        
        Returns:
            True if summarization is needed
        """
        return self.token_count > (self.max_tokens * self.summarization_threshold)
    
    async def summarize_if_needed(self, openai_client=None) -> bool:
        """
        Summarize context if token count exceeds threshold.
        
        Args:
            openai_client: Optional OpenAI client to use for summarization
            
        Returns:
            Whether summarization was performed
        """
        if not self.should_summarize():
            return False
            
        logger.info(f"Token count ({self.token_count}) exceeds threshold, summarizing...")
        
        try:
            # Perform summarization
            tokens_before = self.token_count
            
            # Use provided OpenAI client or import a new one
            if not openai_client:
                from openai import AsyncOpenAI
                
                # Get API key from environment
                import os
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    logger.error("OPENAI_API_KEY not found in environment, cannot summarize context")
                    return False
                    
                openai_client = AsyncOpenAI(api_key=api_key)
            
            # Prepare context for summarization
            context_json = json.dumps({
                "project_name": self.project_name,
                "metadata": self.metadata,
                "summaries": [s.model_dump() for s in self.summaries],
                "entities": {k: v.model_dump() for k, v in self.active_entities.items()},
                "chat_history": self._get_recent_chat(20)  # Include recent chat for context
            })
            
            # Generate summary
            response = await openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes project context."},
                    {"role": "user", "content": f"Summarize the following project context in a concise way that retains the most important information:\n\n{context_json}"}
                ]
            )
            
            # Get the response text, ensuring it's not None
            summary_text = response.choices[0].message.content or "No summary generated"
            
            # Reset token count to 50% of max after summarization
            self.token_count = self.max_tokens // 2
            
            # Create summary object
            summary = ContextSummary(
                summary=summary_text,
                timestamp=time.time(),
                tokens_before=tokens_before,
                tokens_after=self.token_count
            )
            
            # Add to summaries
            self.summaries.append(summary)
            
            logger.info(f"Context summarized: {tokens_before} -> {self.token_count} tokens")
            return True
            
        except Exception as e:
            logger.error(f"Error summarizing context: {str(e)}", exc_info=True)
            # Fallback: just reset the token count to 50% of max
            self.token_count = self.max_tokens // 2
            logger.info(f"Fallback: reset token count to {self.token_count}")
            return False
    
    # Chat message management
    def add_chat_message(self, role: str, content: str, extra_metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a chat message to history with token counting.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            extra_metadata: Optional additional metadata
        """
        if role not in ["user", "assistant", "system", "function"]:
            logger.warning(f"Invalid role: {role}, defaulting to 'user'")
            role = "user"
        
        # Count tokens
        tokens = self.count_tokens(content)
        
        # Create message object
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "tokens": tokens
        }
        
        # Add extra metadata if provided
        if extra_metadata:
            message.update(extra_metadata)
        
        # Add to history
        self.chat_messages.append(message)
        
        # Update token count
        self.update_token_count(tokens)
        
        # Trim chat history if it exceeds max size
        if len(self.chat_messages) > self.max_chat_messages:
            # Calculate tokens to remove
            removed_tokens = sum(msg.get("tokens", 0) for msg in self.chat_messages[:(len(self.chat_messages) - self.max_chat_messages)])
            
            # Remove oldest messages
            self.chat_messages = self.chat_messages[-self.max_chat_messages:]
            
            # Adjust token count
            self.token_count = max(0, self.token_count - removed_tokens)
            logger.debug(f"Trimmed chat history, removed {removed_tokens} tokens")
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """
        Get the full chat history.
        
        Returns:
            List of chat message dictionaries
        """
        return self.chat_messages
    
    def _get_recent_chat(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent chat messages.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent chat messages
        """
        return self.chat_messages[-limit:] if self.chat_messages else []
    
    def get_chat_window(self, window_size: int = 10, include_system: bool = False) -> List[Dict[str, Any]]:
        """
        Get the most recent entries from chat history.
        
        Args:
            window_size: Number of most recent entries to return
            include_system: Whether to include system messages
            
        Returns:
            List of most recent chat entries
        """
        if not self.chat_messages:
            logger.warning("Chat history is empty when requesting window")
            return []
            
        logger.debug(f"Getting chat window: {len(self.chat_messages)} total entries, requesting {window_size} entries")
        
        if include_system:
            result = self.chat_messages[-window_size:]
            return result 
        else:
            # Filter out system messages
            filtered_history = [
                entry for entry in self.chat_messages 
                if entry.get("role") != "system"
            ]
            result = filtered_history[-window_size:]
            return result
    
    def clear_chat_history(self) -> None:
        """Clear all chat history and related token count."""
        # Track how many tokens we're removing
        removed_tokens = sum(msg.get("tokens", 0) for msg in self.chat_messages)
        
        # Clear messages
        self.chat_messages = []
        
        # Adjust token count
        self.token_count = max(0, self.token_count - removed_tokens)
        
        logger.info(f"Cleared chat history, removed {removed_tokens} tokens")
    
    def get_chat_summary(self) -> str:
        """
        Get a formatted summary of the chat history.
        
        Returns:
            String representation of the chat history
        """
        if not self.chat_messages:
            return "No chat history available."
        
        result = ["Chat History:"]
        for i, msg in enumerate(self.chat_messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", 0)
            
            # Format timestamp
            time_str = ""
            if timestamp:
                time_str = f"[{datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}] "
            
            # Truncate long messages in the summary
            if len(content) > 100:
                content = content[:97] + "..."
                
            result.append(f"{i+1}. {time_str}{role.capitalize()}: {content}")
        
        return "\n".join(result)
    
    # Entity tracking
    def track_entity(self, entity_type: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Track an entity in the conversation context.
        
        Args:
            entity_type: Type of entity (file, url, command, etc.)
            value: The entity value (file path, url, command, etc.)
            metadata: Additional info about the entity
            
        Returns:
            Entity ID that can be used for reference
        """
        # Generate a unique ID based on type and value
        entity_id = f"{entity_type}:{hashlib.md5(value.encode()).hexdigest()[:8]}"
        
        # Use a safe dictionary (empty dict if metadata is None)
        safe_metadata = metadata or {}
        
        # Check if entity already exists
        if entity_id in self.active_entities:
            # Update existing entity
            self.active_entities[entity_id].last_access = time.time()
            self.active_entities[entity_id].access_count += 1
            
            # Update metadata if provided
            if metadata:
                self.active_entities[entity_id].metadata.update(safe_metadata)
        else:
            # Create new entity reference
            self.active_entities[entity_id] = EntityReference(
                entity_type=entity_type,
                entity_id=entity_id,
                value=value,
                metadata=safe_metadata,
                last_access=time.time(),
                access_count=1
            )
            
            # Also add a system message to history about this entity
            entity_msg = f"Working with {entity_type}: {value}"
            self.add_chat_message(
                role="system",
                content=entity_msg,
                extra_metadata={
                    "entity_id": entity_id,
                    "entity_type": entity_type
                }
            )
            
            # Handle legacy memory items for backward compatibility
            if entity_type == "file":
                self.remember_file(value, safe_metadata.get("content_preview", None))
            elif entity_type == "command":
                self.remember_command(value, safe_metadata.get("output_preview", None))
            elif entity_type == "person":
                self.remember_person(value)
            
        logger.debug(f"Tracked entity {entity_id}: {entity_type} - {value}")
        return entity_id
    
    def get_entity(self, entity_id: str) -> Optional[EntityReference]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: The entity ID to retrieve
            
        Returns:
            The entity reference or None if not found
        """
        return self.active_entities.get(entity_id)
    
    def get_recent_entities(self, entity_type: Optional[str] = None, limit: int = 5) -> List[EntityReference]:
        """
        Get the most recently accessed entities.
        
        Args:
            entity_type: Optional entity type filter
            limit: Maximum number of entities to return
            
        Returns:
            List of entity references sorted by recency
        """
        entities = list(self.active_entities.values())
        
        # Filter by type if specified
        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]
            
        # Sort by last access time (most recent first)
        entities.sort(key=lambda e: e.last_access, reverse=True)
        
        return entities[:limit]
    
    def get_most_frequent_entities(self, entity_type: Optional[str] = None, limit: int = 25) -> List[EntityReference]:
        """
        Get the most frequently accessed entities.
        
        Args:
            entity_type: Optional entity type filter
            limit: Maximum number of entities to return
            
        Returns:
            List of entity references sorted by access count
        """
        entities = list(self.active_entities.values())
        
        # Filter by type if specified
        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]
            
        # Sort by access count (highest first)
        entities.sort(key=lambda e: e.access_count, reverse=True)
        
        return entities[:limit]
    
    # Session state methods
    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in the session state.
        
        Args:
            key: State key
            value: State value
        """
        self.session_state[key] = value
        logger.debug(f"Set state '{key}': {value}")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the session state.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            The state value or default if not found
        """
        return self.session_state.get(key, default)
    
    def clear_state(self, key: Optional[str] = None) -> None:
        """
        Clear session state.
        
        Args:
            key: Optional specific key to clear. If None, clears all state.
        """
        if key is None:
            self.session_state.clear()
            logger.debug("Cleared all session state")
        elif key in self.session_state:
            del self.session_state[key]
            logger.debug(f"Cleared state '{key}'")
    
    # Context summary methods
    def get_context_summary(self) -> str:
        """
        Get a summary of current context for agents.
        
        Returns:
            String summary of current context
        """
        # Get recent entities
        recent_files = self.get_recent_entities(entity_type="file", limit=3)
        recent_searches = self.get_recent_entities(entity_type="search_query", limit=3)
        recent_commands = self.get_recent_entities(entity_type="command", limit=3)
        recent_urls = self.get_recent_entities(entity_type="url", limit=3)
        
        summary_parts = []
        
        # Add project info
        if self.project_info:
            project_type = self.project_info.get("type", "Unknown project type")
            summary_parts.append(f"Project: {self.project_name} ({project_type})")
        
        # Add current file
        if self.current_file:
            summary_parts.append(f"Current file: {self.current_file}")
            
        # Add recent files
        if recent_files:
            files_str = ", ".join([f"'{e.value}'" for e in recent_files])
            summary_parts.append(f"Recent files: {files_str}")
            
        # Add recent searches
        if recent_searches:
            searches_str = ", ".join([f"'{e.value}'" for e in recent_searches])
            summary_parts.append(f"Recent searches: {searches_str}")
            
        # Add recent commands
        if recent_commands:
            cmds_str = ", ".join([f"'{e.value}'" for e in recent_commands])
            summary_parts.append(f"Recent commands: {cmds_str}")
            
        # Add recent URLs
        if recent_urls:
            urls_str = ", ".join([f"'{e.value}'" for e in recent_urls])
            summary_parts.append(f"Recent URLs: {urls_str}")
            
        # Add any relevant session state
        active_task = self.get_state("active_task")
        if active_task:
            summary_parts.append(f"Current task: {active_task}")
        
        # Add token usage info
        token_usage = f"Tokens: {self.token_count}/{self.max_tokens} ({int(self.token_count/self.max_tokens*100)}%)"
        summary_parts.append(token_usage)
        
        # Compile the final summary
        if summary_parts:
            return "Context: " + "; ".join(summary_parts)
        else:
            return "No active context"
    
    # Persistence methods
    async def save_to_json(self, path: str) -> bool:
        """
        Save context to JSON file for persistence.
        
        Args:
            path: Path to save the JSON file
            
        Returns:
            Whether the save was successful
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Log history before saving
            history_count = len(self.chat_messages) if self.chat_messages else 0
            logger.info(f"Saving context with {history_count} chat entries to {path}")
            
            # Do an extra check to ensure working directory is current
            if self.working_directory != os.getcwd():
                logger.warning(f"Working directory mismatch: {self.working_directory} vs {os.getcwd()}")
                # Update to current working directory
                self.working_directory = os.getcwd()
                logger.info(f"Updated working directory to {self.working_directory}")
            
            # Prepare data for serialization
            data = {
                "working_directory": self.working_directory,
                "project_name": self.project_name,
                "project_info": self.project_info,
                "token_count": self.token_count,
                "max_tokens": self.max_tokens,
                "creation_time": self.creation_time,
                "last_updated": self.last_updated,
                "metadata": self.metadata,
                "summaries": [s.model_dump() for s in self.summaries],
                "chat_messages": self.chat_messages,
                "active_entities": {
                    k: v.model_dump() for k, v in self.active_entities.items()
                },
                "session_state": self.session_state,
                "current_file": self.current_file
            }
            
            # Log what we're saving
            user_msgs = sum(1 for m in self.chat_messages if m.get("role") == "user")
            asst_msgs = sum(1 for m in self.chat_messages if m.get("role") == "assistant")
            system_msgs = sum(1 for m in self.chat_messages if m.get("role") == "system")
            logger.info(f"Saving context: {user_msgs} user, {asst_msgs} assistant, {system_msgs} system messages")
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Context saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving context to {path}: {str(e)}", exc_info=True)
            return False
    
    @classmethod
    async def load_from_json(cls, path: str) -> 'EnhancedContextData':
        """
        Load context from JSON file.
        
        Args:
            path: Path to the JSON file
            
        Returns:
            Loaded EnhancedContextData
        """
        try:
            if not os.path.exists(path):
                logger.info(f"Context file {path} does not exist, creating new context")
                return cls(
                    working_directory=os.getcwd(),
                    project_name="DefaultProject"
                )
            
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Extract working directory, but ensure it is set to current directory
            # This fixes potential path issues when context was created elsewhere
            saved_working_dir = data.get("working_directory", os.getcwd())
            current_dir = os.getcwd()
            
            if saved_working_dir != current_dir:
                logger.warning(f"Working directory in saved context ({saved_working_dir}) " 
                            f"doesn't match current directory ({current_dir}).")
                logger.info(f"Using current directory: {current_dir}")
                working_directory = current_dir
            else:
                working_directory = saved_working_dir
            
            # Create instance with base data
            context = cls(
                working_directory=working_directory,
                project_name=data.get("project_name", "DefaultProject"),
                project_info=data.get("project_info"),
                token_count=data.get("token_count", 0),
                creation_time=data.get("creation_time", time.time()),
                last_updated=data.get("last_updated", time.time()),
                metadata=data.get("metadata", {}),
                current_file=data.get("current_file")
            )
            
            # Load chat messages
            chat_messages = data.get("chat_messages", [])
            context.chat_messages = chat_messages
            
            # Load summaries
            if "summaries" in data:
                for summary_data in data["summaries"]:
                    context.summaries.append(ContextSummary(**summary_data))
            
            # Load entities
            entities_data = data.get("active_entities", {})
            for entity_id, entity_data in entities_data.items():
                context.active_entities[entity_id] = EntityReference(**entity_data)
                
            # Load session state
            context.session_state = data.get("session_state", {})
            
            logger.info(f"Context loaded from {path}")
            return context
            
        except Exception as e:
            logger.error(f"Error loading context from {path}: {str(e)}", exc_info=True)
            return cls(
                working_directory=os.getcwd(),
                project_name="DefaultProject"
            )
    
    # Maintain backward compatibility with the old API
    def remember_file(self, file_path: str, content: Optional[str] = None) -> None:
        """Legacy method for remembering files."""
        file_path = os.path.normpath(os.path.join(self.working_directory, file_path))
        self.memory_items.append(MemoryItem(
            content=file_path,
            item_type="file",
            metadata={"content_preview": content[:100] if content else None}
        ))
        self.current_file = file_path
        
        # Also track as entity if not already tracked
        entity_id = f"file:{hashlib.md5(file_path.encode()).hexdigest()[:8]}"
        if entity_id not in self.active_entities:
            metadata = {"content_preview": content[:100] if content else None}
            self.track_entity("file", file_path, metadata)

    def remember_person(self, name: str) -> None:
        """Legacy method for remembering persons."""
        self.memory_items.append(MemoryItem(content=name, item_type="person"))
        
        # Also track as entity
        self.track_entity("person", name)

    def remember_command(self, command: str, output: Optional[str] = None) -> None:
        """Legacy method for remembering commands."""
        self.memory_items.append(MemoryItem(
            content=command,
            item_type="command",
            metadata={"output_preview": output[:100] if output else None}
        ))
        
        # Also track as entity
        metadata = {"output_preview": output[:100] if output else None}
        self.track_entity("command", command, metadata)

    def get_recent_files(self, limit: int = 5) -> List[str]:
        """
        Legacy method for getting recent files.
        Now uses entity tracking system.
        """
        # Use entity system instead of memory items
        entities = self.get_recent_entities(entity_type="file", limit=limit)
        return [entity.value for entity in entities]

    def get_recent_persons(self, limit: int = 10) -> List[str]:
        """
        Legacy method for getting recent persons.
        Now uses entity tracking system.
        """
        entities = self.get_recent_entities(entity_type="person", limit=limit)
        return [entity.value for entity in entities]

    def get_recent_commands(self, limit: int = 5) -> List[str]:
        """
        Legacy method for getting recent commands.
        Now uses entity tracking system.
        """
        entities = self.get_recent_entities(entity_type="command", limit=limit)
        return [entity.value for entity in entities]

    def get_memory_summary(self) -> str:
        """Legacy method for getting memory summary."""
        return self.get_context_summary()