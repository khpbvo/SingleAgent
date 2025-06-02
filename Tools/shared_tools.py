"""
Shared tools for both the SingleAgent and ArchitectAgent.
Contains common tools used by both agents to avoid duplication.
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, cast
from typing_extensions import Annotated

from pydantic import BaseModel, Field
from logging.handlers import RotatingFileHandler

from agents import function_tool, RunContextWrapper
from The_Agents.context_data import EnhancedContextData

# Configure logger for shared tools
shared_logger = logging.getLogger("SharedTools")
shared_logger.setLevel(logging.DEBUG)
# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)
# rotating file handler
shared_handler = RotatingFileHandler('logs/shared_tools.log', maxBytes=10*1024*1024, backupCount=3)
shared_handler.setLevel(logging.DEBUG)
shared_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
shared_logger.addHandler(shared_handler)
shared_logger.propagate = False
# alias shared_logger as logger for use in function implementations
logger = shared_logger

# Shared utility functions for tracking entities in context
def track_file_entity(ctx, file_path, content):
    """
    Track a file entity in the agent's context and set it as current file.
    """
    ctx.track_entity(
        entity_type="file",
        value=file_path,
        metadata={"content_preview": content[:100] if content else None}
    )
    ctx.current_file = file_path

def track_command_entity(ctx, command, output):
    """
    Track a command entity in the agent's context.
    """
    ctx.track_entity(
        entity_type="command",
        value=command,
        metadata={"output_preview": output[:100] if output else None}
    )

# Shared Pydantic models for tool parameters
class GetContextParams(BaseModel):
    """Parameters for getting the context information."""
    include_details: bool = Field(description="Whether to include detailed information")

class GetContextResponse(BaseModel):
    """Response model for the get_context_response tool."""
    chat_history: str = Field(description="Summary of recent chat history")
    context_summary: str = Field(description="Summary of current context")
    recent_files: list = Field(description="List of recently accessed files")
    recent_commands: list = Field(description="List of recently executed commands")
    token_usage: int = Field(description="Current token usage")
    max_tokens: int = Field(description="Maximum token limit")

class AddManualContextParams(BaseModel):
    """Parameters for manually adding content to the context."""
    file_path: str = Field(description="Path to the file to read and add to context")
    label: Optional[str] = Field(None, description="Optional label for this context item")

class RunCommandParams(BaseModel):
    """Parameters for running shell commands."""
    command: str = Field(description="The command to execute")
    working_dir: Optional[str] = Field(None, description="Directory to execute the command in")

class FileReadParams(BaseModel):
    """Parameters for reading a file."""
    file_path: str = Field(description="Path to the file to read")

# Shared tool implementations
@function_tool
async def get_context_response(wrapper: RunContextWrapper[EnhancedContextData]) -> GetContextResponse:
    """
    Get the current context information including:
    - Chat history
    - Recent files
    - Recent commands
    - Context summary
    - Token usage

    Use this to understand the conversation context and project state.
    
    Returns:
        Context information
    """
    # pull the actual context out of the wrapper
    ctx = wrapper.context

    # Get recent entities
    recent_files = [e.value for e in ctx.get_recent_entities(entity_type="file", limit=5)]
    recent_commands = [e.value for e in ctx.get_recent_entities(entity_type="command", limit=5)]
    
    # Get token usage information
    token_usage = ctx.token_count
    max_tokens = ctx.max_tokens
    
    return GetContextResponse(
        chat_history=ctx.get_chat_summary(),
        context_summary=ctx.get_context_summary(),
        recent_files=recent_files,
        recent_commands=recent_commands,
        token_usage=token_usage,
        max_tokens=max_tokens
    )

@function_tool
async def add_manual_context(wrapper: RunContextWrapper[EnhancedContextData], params: AddManualContextParams) -> str:
    """
    Add manual context from a file that will be persisted across sessions.
    
    This tool reads a file and adds its content to the agent's context. The content
    will be available to the agent in future sessions, allowing you to build up a
    persistent knowledge base.
    
    Args:
        file_path: Path to the file to read and add to context
        label: Optional label for this context item. If not provided, one will be generated from the file name
        
    Returns:
        Summary of the added context
    """
    logger.debug(json.dumps({"tool": "add_manual_context", "params": params.model_dump()}))
    
    try:
        # Verify file exists
        if not os.path.isfile(params.file_path):
            return f"Error: File not found at {params.file_path}"
            
        # Read file content
        with open(params.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content:
            return f"Error: Empty file at {params.file_path}"
            
        # Add to context
        label = wrapper.context.add_manual_context(
            content=content,
            source=params.file_path,
            label=params.label
        )
        
        # Track as file entity as well
        track_file_entity(wrapper.context, params.file_path, content)
        
        # Return success message
        tokens = wrapper.context.count_tokens(content)
        return f"Successfully added context from {params.file_path} with label '{label}' ({tokens} tokens)"
    
    except Exception as e:
        logger.error(f"Error adding manual context: {str(e)}", exc_info=True)
        return f"Error adding context: {str(e)}"

@function_tool
async def run_command(wrapper: RunContextWrapper[EnhancedContextData], params: RunCommandParams) -> str:
    """
    Run a shell command and return its output.
    
    This tool allows executing system commands from the agent.
    
    Args:
        command: The command to execute
        working_dir: Optional directory to execute the command in (defaults to current directory)
        
    Returns:
        Command output (stdout and stderr)
    """
    logger.debug(json.dumps({"tool": "run_command", "params": params.model_dump()}))
    working_dir = params.working_dir if params.working_dir is not None else os.getcwd()
    try:
        proc = await asyncio.create_subprocess_shell(
            params.command,
            cwd=working_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() or ""
        if stderr:
            output += f"\nSTDERR:\n{stderr.decode()}"
        if not output:
            output = "Command executed successfully with no output."
        
        # Track command entity in context
        track_command_entity(wrapper.context, params.command, output)
        logger.debug(json.dumps({"tool": "run_command", "output": output}))
        return output
    except Exception as e:
        logger.debug(json.dumps({"tool": "run_command", "error": str(e)}))
        return f"Error executing command: {str(e)}"

@function_tool
async def read_file(wrapper: RunContextWrapper[EnhancedContextData], params: FileReadParams) -> Dict[str, Any]:
    """
    Read a file and return its contents with metadata.
    
    This tool reads the content of a file and tracks it in the agent's context.
    It's useful for understanding code, configuration files, and documentation.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        Dictionary containing file content and metadata
    """
    logger.debug(json.dumps({"tool": "read_file", "params": params.model_dump()}))
    
    try:
        # Normalize path - handle relative paths automatically
        file_path = params.file_path
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
            logger.info(f"Converted relative path to absolute: {file_path}")
        
        file_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {"error": f"Path not found: {file_path}"}
            
        if not os.path.isfile(file_path):
            return {"error": f"Not a file (possibly a directory): {file_path}."}
        
        # Get file stats
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        
        # Check file size (limit to reasonable size to prevent resource issues)
        if file_size > 5 * 1024 * 1024:
            return {"error": f"File too large ({file_size / 1024 / 1024:.2f} MB). Maximum size is 5 MB."}
        
        # Read file with proper error handling
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except UnicodeDecodeError:
            return {"error": f"Could not decode file as text: {file_path}. This may be a binary file."}
        except PermissionError:
            return {"error": f"Permission denied when reading file: {file_path}"}
        
        # Get file extension
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        # Track file in context
        track_file_entity(wrapper.context, file_path, content)
        
        # Create metadata
        metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": file_size,
            "file_extension": file_extension,
            "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "token_count": wrapper.context.count_tokens(content),
            "line_count": content.count('\n') + 1
        }
        
        # Return result
        result = {
            "content": content,
            "metadata": metadata
        }
        
        logger.debug(json.dumps({"tool": "read_file", "result_size": len(content)}))
        return result
    
    except Exception as e:
        logger.error(f"Error in read_file: {str(e)}", exc_info=True)
        return {"error": f"Error reading file: {str(e)}"}

@function_tool
async def get_context(wrapper: RunContextWrapper[EnhancedContextData], params: GetContextParams) -> str:
    """
    Get a human-readable summary of the current context.
    
    Args:
        include_details: Whether to include detailed information
        
    Returns:
        String summary of current context
    """
    logger.debug(json.dumps({"tool": "get_context", "params": params.model_dump()}))
    context = wrapper.context
    info = [
        f"Working directory: {context.working_directory}",
    ]
    if context.current_file:
        info.append(f"Current file: {context.current_file}")
    
    # Add chat history to context information
    if hasattr(context, 'chat_messages') and context.chat_messages:
        info.append("\nRecent Chat History:")
        # Show the last 5 messages or all if fewer
        history_to_show = (
            context.chat_messages[-5:]
            if len(context.chat_messages) > 5
            else context.chat_messages
        )
        for msg in history_to_show:
            # support both simple tuples and richer objects
            if isinstance(msg, tuple) and len(msg) >= 2:
                # tell the type‐checker this is a 2‑tuple so msg[0]/msg[1] is OK
                tmsg = cast(Tuple[Any, Any], msg)
                role = tmsg[0]
                content = tmsg[1]
            else:
                role = getattr(msg, 'role', 'unknown')
                content = getattr(msg, 'content', str(msg))
            # truncate long messages
            if len(content) > 100:
                content = content[:97] + "..."
            info.append(f"- {role.capitalize()}: {content}")
    
    # Add manual context items
    if hasattr(context, 'manual_context_items') and context.manual_context_items:
        info.append("\nManual Context Items:")
        for i, item in enumerate(context.manual_context_items):
            # Format timestamp
            time_str = datetime.fromtimestamp(item.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            # Create a preview of the content
            content_preview = item.content[:50] + "..." if len(item.content) > 50 else item.content
            info.append(f"- {item.label} ({time_str}, {item.token_count} tokens): {content_preview}")
    
    if params.include_details:
        info.append("\nMemory items:")
        for item in context.memory_items:
            ts = item.timestamp.strftime("%H:%M:%S")
            info.append(f"- {item.item_type}: {item.content} (at {ts})")
    else:
        summary = context.get_memory_summary()
        if summary:
            info.append(summary)

    result = "\n".join(info)
    logger.debug(json.dumps({"tool": "get_context", "output_length": len(result)}))
    return result
