"""
Enhanced context system for SingleAgent with features from AgentSmith:
- Entity tracking (files, commands, URLs)
- Accurate token counting with tiktoken
- Session state management
- Conversation summarization
- Persistent storage between sessions
"""
from datetime import datetime
import os, time
import json
from typing import List, Optional, Dict, Any
import tiktoken 
# Configure logger
import logging
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


class ManualContextItem(BaseModel):
    """Model for manually added context items."""
    content: str = Field(description="The content of the context item")
    label: str = Field(description="Label or identifier for this context item")
    source: str = Field(description="Source of the context item (e.g., file path)")
    timestamp: float = Field(default_factory=time.time, description="When this item was added")
    token_count: int = Field(default=0, description="Number of tokens in this context item")


class EnhancedContextData(BaseModel):
    """
    Enhanced context data with:
    - Token tracking
    - Entity tracking
    - Session state
    - Conversation history with roles
    - Summarization capabilities
    - Persistence through JSON
    - Manual context additions
    """
    # Basic project info
    working_directory: str = Field(description="Current working directory")
    project_info: Optional[Dict[str, Any]] = Field(None, description="Information about the project")
    project_name: str = Field(default="DefaultProject", description="Name of the current project")
    
    # Token management
    token_count: int = Field(default=0, description="Current token count")
    max_tokens: int = Field(default=400_000, description="Maximum tokens before summarization")
    summarization_threshold: float = Field(default=0.8, description="Threshold ratio for summarization")
    summaries: List[ContextSummary] = Field(default_factory=list, description="History of context summaries")
    
    # Chat history
    chat_messages: List[Dict[str, Any]] = Field(default_factory=list, description="Chat message history with metadata")
    max_chat_messages: int = Field(default=25, description="Maximum number of chat messages to keep")
    
    # Entity tracking
    active_entities: Dict[str, EntityReference] = Field(default_factory=dict, description="Currently tracked entities")
    current_file: Optional[str] = Field(None, description="Currently active file")
    
    # Manual context items that persist across sessions
    manual_context_items: List[ManualContextItem] = Field(default_factory=list, description="Manually added context items")
    
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
        # ensure chat history exists
        if self.chat_messages is None:
            self.chat_messages = []
        # ensure token_count exists
        if not hasattr(self, "token_count"):
            self.token_count = 0

    def get_tokenizer(self):
        if self._tokenizer is None:
            # pick an encoder for your model
            self._tokenizer = tiktoken.encoding_for_model("gpt-4o")
        return self._tokenizer

    def count_tokens(self, text: str) -> int:
        enc = self.get_tokenizer()
        return len(enc.encode(text))

    def update_token_count(self, new_tokens: int) -> None:
        self.token_count += new_tokens
        self.last_updated = time.time()

    # Chat message management
    def add_chat_message(self, role: str, content: str, extra_metadata: Optional[Dict[str, Any]] = None) -> None:
        msg_tokens = self.count_tokens(content)
        msg = {"role": role, "content": content, "token_count": msg_tokens}
        if extra_metadata:
            msg.update(extra_metadata)
        self.chat_messages.append(msg)
        # track tokens used for this message
        self.update_token_count(msg_tokens)
        # trim old messages if we exceed the max
        while len(self.chat_messages) > self.max_chat_messages:
            removed = self.chat_messages.pop(0)
            removed_tokens = removed.get("token_count", self.count_tokens(removed.get("content", "")))
            self.token_count = max(0, self.token_count - removed_tokens)
            logger.debug(
                "Trimmed chat history, removed %s tokens; %s messages remaining",
                removed_tokens,
                len(self.chat_messages),
            )

    def get_chat_history(self) -> List[Dict[str, Any]]:
        return list(self.chat_messages)

    def clear_chat_history(self) -> None:
        self.chat_messages = []
        self.token_count = 0
        self.last_updated = time.time()

    def get_chat_summary(self) -> str:
        # show last N messages as a quick summary
        recent = self.chat_messages[-5:]
        lines = []
        for m in recent:
            lines.append(f"{m['role'].upper()}: {m['content'][:100]}")
        return "\n".join(lines)

    # Context summary to inject into system prompt
    def get_context_summary(self) -> str:
        parts = []
        parts.append(f"👥 Chat messages: {len(self.chat_messages)} total")
        if self.chat_messages:
            parts.append(self.get_chat_summary())
        # optionally list manual context items
        if self.manual_context_items:
            parts.append(f"📚 Manual items: {len(self.manual_context_items)}")
            for it in self.manual_context_items[-3:]:
                preview = it.content[:50].replace("\n"," ") + ("…" if len(it.content)>50 else "")
                parts.append(f"  - {it.label}: {preview}")
        return "\n".join(parts)

    def should_summarize(self) -> bool:
        """
        Returns True if our token_count has exceeded the
        max_tokens * summarization_threshold.
        """
        return self.token_count >= self.max_tokens * self.summarization_threshold

    async def summarize_if_needed(self, openai_client) -> bool:
        """
        If should_summarize() is True, call the LLM to
        compress the context down into a single summary
        and reset chat_messages to just that summary.
        Returns True if a summarization was performed.
        """
        if not self.should_summarize():
            return False

        # Build a simple summarization prompt
        prompt = (
            "Please summarize the following context to reduce token usage:\n\n"
            + self.get_context_summary()
        )

        # Call the LLM
        resp = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        summary = resp.choices[0].message.content

        # Record old/new token counts
        old_tokens = self.token_count
        new_tokens = self.count_tokens(summary)
        self.summaries.append(
            ContextSummary(
                summary=summary,
                timestamp=time.time(),
                tokens_before=old_tokens,
                tokens_after=new_tokens
            )
        )

        # Reset history and replace with the summary
        self.clear_chat_history()
        self.chat_messages.append({
            "role": "system",
            "content": f"—CONTEXT SUMMARY—\n{summary}"
        })
        self.token_count = new_tokens
        self.last_updated = time.time()
        return True

    # ----- ENTITY TRACKING -----
    def track_entity(self, entity_type: str, value: str, metadata: Dict[str, Any]):
        """
        Create or update an EntityReference in active_entities.
        """
        key = f"{entity_type}:{value}"
        now = time.time()
        if key in self.active_entities:
            ref = self.active_entities[key]
            ref.access_count += 1
            ref.last_access = now
            ref.metadata.update(metadata or {})
        else:
            ref = EntityReference(
                entity_type=entity_type,
                entity_id=key,
                value=value,
                metadata=metadata or {},
                last_access=now,
                access_count=1
            )
            self.active_entities[key] = ref
        self.last_updated = now

    def get_recent_entities(self, entity_type: str, limit: int = 5) -> List[EntityReference]:
        """
        Return up to `limit` most‐recently accessed entities of the given type.
        """
        all_refs = [r for r in self.active_entities.values() if r.entity_type == entity_type]
        all_refs.sort(key=lambda r: r.last_access, reverse=True)
        return all_refs[:limit]

    # ----- REMEMBER FILE/COMMAND -----
    def remember_file(self, file_path: str, content: str) -> None:
        """
        Called after read_file: update token count, track entity, add to memory_items.
        """
        tokens = self.count_tokens(content)
        self.update_token_count(tokens)
        # track as entity
        self.track_entity("file", file_path, {"content_preview": content[:100]})
        # add to memory for backward‐compat
        self.memory_items.append(MemoryItem(content=f"FILE {file_path} read"))
        self.last_updated = time.time()

    def remember_command(self, command: str, output: str) -> None:
        """
        Called after run_command: update token count, track entity, add to memory_items.
        """
        tokens = self.count_tokens(output)
        self.update_token_count(tokens)
        # track as entity
        self.track_entity("command", command, {"output_preview": output[:100]})
        # add to memory
        self.memory_items.append(MemoryItem(content=f"CMD `{command}` → {output[:50]}"))
        self.last_updated = time.time()

    # ----- MANUAL CONTEXT -----
    def add_manual_context(self, content: str, source: str, label: Optional[str] = None) -> str:
        """
        Tool calls this to persist a ManualContextItem.
        Returns the label used.
        """
        lbl = label or os.path.basename(source)
        tokens = self.count_tokens(content)
        item = ManualContextItem(
            content=content,
            label=lbl,
            source=source,
            timestamp=time.time(),
            token_count=tokens
        )
        self.manual_context_items.append(item)
        self.update_token_count(tokens)
        self.last_updated = time.time()
        return lbl

    # ----- MEMORY SUMMARY -----
    def get_memory_summary(self) -> str:
        """
        Return a short summary of the last few memory_items.
        """
        if not self.memory_items:
            return ""
        recent = self.memory_items[-3:]
        lines = [f"- {m.content}" for m in recent]
        return "Recent memory items:\n" + "\n".join(lines)

    # Add these methods
    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in the session state dictionary.
        
        Args:
            key: State key to set
            value: Value to store
        """
        self.session_state[key] = value
        self.last_updated = time.time()

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the session state dictionary.
        
        Args:
            key: State key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The stored value or default if not found
        """
        return self.session_state.get(key, default)

    def get_token_usage_info(self) -> Dict[str, Any]:
        """
        Get detailed token usage information for display.
        
        Returns:
            Dictionary with token usage details
        """
        percentage = (self.token_count / self.max_tokens) * 100 if self.max_tokens > 0 else 0
        
        # Calculate manual context tokens
        manual_context_tokens = sum(item.token_count for item in self.manual_context_items)
        
        # Calculate chat tokens
        chat_tokens = sum(self.count_tokens(msg.get("content", "")) for msg in self.chat_messages)
        
        return {
            "current": self.token_count,
            "maximum": self.max_tokens,
            "percentage": percentage,
            "remaining": self.max_tokens - self.token_count,
            "status": "good" if percentage < 50 else "warning" if percentage < 80 else "danger",
            "manual_context_tokens": manual_context_tokens,
            "chat_tokens": chat_tokens,
            "manual_context_items_count": len(self.manual_context_items),
            "chat_messages_count": len(self.chat_messages),
            "active_entities_count": len(self.active_entities),
            "memory_items_count": len(self.memory_items),
            "summarization_threshold": self.max_tokens * self.summarization_threshold,
            "needs_summarization": self.should_summarize(),
        }

    def format_token_bar(self, width: int = 20) -> str:
        """
        Create a visual progress bar for token usage.
        
        Args:
            width: Width of the progress bar in characters
            
        Returns:
            String representation of the progress bar
        """
        percentage = (self.token_count / self.max_tokens) * 100 if self.max_tokens > 0 else 0
        filled = int((percentage / 100) * width)
        return "█" * filled + "░" * (width - filled)

    def get_detailed_token_breakdown(self) -> str:
        """
        Get a formatted string with detailed token usage breakdown.
        
        Returns:
            Formatted string with token breakdown
        """
        info = self.get_token_usage_info()
        
        return f"""Token Usage Breakdown:
├─ Total Used: {info['current']:,} / {info['maximum']:,} ({info['percentage']:.1f}%)
├─ Chat Messages: {info['chat_tokens']:,} tokens ({info['chat_messages_count']} messages)
├─ Manual Context: {info['manual_context_tokens']:,} tokens ({info['manual_context_items_count']} items)
├─ Remaining: {info['remaining']:,} tokens
├─ Summarization Threshold: {info['summarization_threshold']:,} tokens
└─ Status: {info['status'].upper()} {'⚠️  NEEDS SUMMARIZATION' if info['needs_summarization'] else '✅'}

Progress: {self.format_token_bar(30)}

Tracked Entities: {info['active_entities_count']}
Memory Items: {info['memory_items_count']}"""

    def remove_manual_context(self, label: str) -> bool:
        """
        Remove a manual context item by its label.
        
        Args:
            label: Label of the context item to remove
            
        Returns:
            True if item was found and removed, False otherwise
        """
        for i, item in enumerate(self.manual_context_items):
            if item.label == label:
                removed_item = self.manual_context_items.pop(i)
                # Subtract the tokens from our count
                self.token_count -= removed_item.token_count
                self.last_updated = time.time()
                return True
        return False
    
    # Serialization methods
    async def save_to_json(self, filepath: str) -> None:
        """Save context to JSON file."""
        data = self.model_dump(exclude={'_tokenizer'})
        # Convert datetime objects to strings
        for item in data.get('memory_items', []):
            if 'timestamp' in item and hasattr(item['timestamp'], 'isoformat'):
                item['timestamp'] = item['timestamp'].isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved context to {filepath}")
    
    @classmethod
    async def load_from_json(cls, filepath: str) -> 'EnhancedContextData':
        """Load context from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Convert timestamp strings back to datetime objects
        for item in data.get('memory_items', []):
            if 'timestamp' in item and isinstance(item['timestamp'], str):
                item['timestamp'] = datetime.fromisoformat(item['timestamp'])

        # Ensure max_tokens is at least the default
        default_max = 400_000
        if data.get('max_tokens', default_max) < default_max:
            data['max_tokens'] = default_max

        logger.info(f"Loaded context from {filepath}")
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = self.model_dump(exclude={'_tokenizer'})
        # Handle datetime serialization
        for item in data.get('memory_items', []):
            if 'timestamp' in item and hasattr(item['timestamp'], 'isoformat'):
                item['timestamp'] = item['timestamp'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedContextData':
        """Create from dictionary."""
        # Convert timestamp strings back to datetime objects
        for item in data.get('memory_items', []):
            if 'timestamp' in item and isinstance(item['timestamp'], str):
                item['timestamp'] = datetime.fromisoformat(item['timestamp'])

        # Ensure max_tokens respects minimum default
        default_max = 400_000
        if data.get('max_tokens', default_max) < default_max:
            data['max_tokens'] = default_max

        return cls(**data)
    
    def merge_from(self, other_context: 'EnhancedContextData', merge_chat: bool = False) -> None:
        """
        Merge relevant information from another context.
        
        Args:
            other_context: The context to merge from
            merge_chat: Whether to merge recent chat messages
        """
        # Merge entities with higher access counts
        for key, entity in other_context.active_entities.items():
            if key not in self.active_entities or entity.access_count > self.active_entities[key].access_count:
                self.active_entities[key] = entity
        
        # Optionally merge recent chat history
        if merge_chat:
            # Take last N messages from other context
            recent_messages = other_context.chat_messages[-5:]
            self.chat_messages.extend(recent_messages)
            # Update token count
            for msg in recent_messages:
                self.update_token_count(self.count_tokens(msg.get('content', '')))
        
        # Merge manual context items (avoid duplicates)
        existing_labels = {item.label for item in self.manual_context_items}
        for item in other_context.manual_context_items:
            if item.label not in existing_labels:
                self.manual_context_items.append(item)
                self.update_token_count(item.token_count)
        
        # Merge session state
        self.session_state.update(other_context.session_state)
        
        # Update metadata
        self.last_updated = time.time()
        logger.info("Merged context from another instance")