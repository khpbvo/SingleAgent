from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import os
from pydantic import BaseModel, Field

class MemoryItem(BaseModel):
    """A memory item with timestamp and metadata"""
    content: str = Field(description="The main content of the memory item")
    item_type: str = Field(description="Type of item ('file', 'person', 'command', etc.)")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this item was added")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional information")

class CodeAssistantContextData(BaseModel):
    """Context data for the code assistant agent"""
    working_directory: str = Field(description="Current working directory")
    project_info: Optional[Dict[str, Any]] = Field(None, description="Information about the project")

class EnhancedContextData(BaseModel):
    """Enhanced context data with memory capabilities"""
    working_directory: str = Field(description="Current working directory")
    project_info: Optional[Dict[str, Any]] = Field(None, description="Information about the project")
    current_file: Optional[str] = Field(None, description="Currently active file")
    memory_items: List[MemoryItem] = Field(default_factory=list, description="Remembered items")
    chat_messages: List[Tuple[str, str]] = Field(default_factory=list, description="Chat message history as (role, content) tuples")
    max_chat_messages: int = Field(default=25, description="Maximum number of chat messages to remember")

    def remember_file(self, file_path: str, content: Optional[str] = None) -> None:
        file_path = os.path.normpath(os.path.join(self.working_directory, file_path))
        self.memory_items.append(MemoryItem(
            content=file_path,
            item_type="file",
            metadata={"content_preview": content[:100] if content else None}
        ))
        self.current_file = file_path

    def remember_person(self, name: str) -> None:
        self.memory_items.append(MemoryItem(content=name, item_type="person"))

    def remember_command(self, command: str, output: Optional[str] = None) -> None:
        self.memory_items.append(MemoryItem(
            content=command,
            item_type="command",
            metadata={"output_preview": output[:100] if output else None}
        ))

    def add_chat_message(self, role: str, content: str) -> None:
        """
        Add a chat message to the history, maintaining the maximum chat history size.
        
        Args:
            role: The role of the message sender ('user' or 'assistant')
            content: The message content
        """
        self.chat_messages.append((role, content))
        # Trim chat history if it exceeds max size
        if len(self.chat_messages) > self.max_chat_messages:
            self.chat_messages = self.chat_messages[-self.max_chat_messages:]
    
    def get_chat_history(self) -> List[Tuple[str, str]]:
        """
        Get the full chat history.
        
        Returns:
            List of (role, content) tuples representing the chat history
        """
        return self.chat_messages
    
    def clear_chat_history(self) -> None:
        """Clear all chat history."""
        self.chat_messages = []

    def get_chat_summary(self) -> str:
        """
        Get a formatted summary of the chat history.
        
        Returns:
            String representation of the chat history
        """
        if not self.chat_messages:
            return "No chat history available."
        
        result = ["Chat History:"]
        for i, (role, content) in enumerate(self.chat_messages):
            # Truncate long messages in the summary
            if len(content) > 100:
                content = content[:97] + "..."
            result.append(f"{i+1}. {role.capitalize()}: {content}")
        
        return "\n".join(result)

    def get_recent_files(self, limit: int = 25) -> List[str]:
        files = [item.content for item in reversed(self.memory_items) if item.item_type == "file"]
        seen = set()
        return [x for x in files if not (x in seen or seen.add(x)) and len(seen) < limit]

    def get_recent_persons(self, limit: int = 10) -> List[str]:
        persons = [item.content for item in reversed(self.memory_items) if item.item_type == "person"]
        seen = set()
        return [x for x in persons if not (x in seen or seen.add(x)) and len(seen) < limit]

    def get_recent_commands(self, limit: int = 40) -> List[str]:
        commands = [item.content for item in reversed(self.memory_items) if item.item_type == "command"]
        seen = set()
        return [x for x in commands if not (x in seen or seen.add(x)) and len(seen) < limit]

    def get_memory_summary(self) -> str:
        parts = []
        if self.current_file:
            parts.append(f"Current file: {self.current_file}")
        files = self.get_recent_files()
        if files:
            parts.append("\nRecent files:")
            parts += [f"  {i+1}. {f}" for i, f in enumerate(files)]
        cmds = self.get_recent_commands()
        if cmds:
            parts.append("\nRecent commands:")
            parts += [f"  {i+1}. {c}" for i, c in enumerate(cmds)]
        prs = self.get_recent_persons()
        if prs:
            parts.append("\nMentioned persons/entities:")
            parts += [f"  {i+1}. {p}" for i, p in enumerate(prs)]
            
        # Add chat history summary to memory summary
        if self.chat_messages:
            parts.append("\nRecent conversations:")
            # Only show last few messages in summary
            for i, (role, content) in enumerate(self.chat_messages[-3:]):
                if len(content) > 50:
                    content = content[:47] + "..."
                parts.append(f"  {role.capitalize()}: {content}")
        
        return "\n".join(parts)