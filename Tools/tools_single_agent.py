"""
Tools for the code assistant agent.
Contains various tools according to OpenAI Agents SDK specs with Pydantic v2 compatibility.
"""

import os
import subprocess
import tempfile
import difflib
import asyncio
import time
from datetime import datetime
from typing import List, Optional, Union, TypedDict, Dict, Any, Tuple, cast
from typing_extensions import Annotated

from pydantic import BaseModel, Field
import os
from agents import function_tool, RunContextWrapper
from The_Agents.context_data import EnhancedContextData
import json
import logging
from logging.handlers import RotatingFileHandler

# Configure logger for tools
tool_logger = logging.getLogger(__name__)
tool_logger.setLevel(logging.DEBUG)
# rotating file handler for tools.log
tools_handler = RotatingFileHandler('tools.log', maxBytes=10*1024*1024, backupCount=3)
tools_handler.setLevel(logging.DEBUG)
tools_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
tool_logger.addHandler(tools_handler)
tool_logger.propagate = False
# alias tool_logger as logger for use in function implementations
logger = tool_logger

# Integration: track entities for enhanced context
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

# Models for tool parameters (no default values as required for Pydantic v2 compatibility)

class PylintParams(BaseModel):
    """Parameters for running pylint on files."""
    file_path: str = Field(description="Path to the file to lint")
    options: List[str] = Field(description="Additional pylint options")


class PyrightParams(BaseModel):
    """Parameters for running pyright type checker."""
    targets: List[str] = Field(
        description="Files or directories to check (pass '.' for cwd)"
    )
    options: List[str] = Field(
        default_factory=list,
        description="Extra command‑line flags for pyright"
    )


class CommandParams(BaseModel):
    """Parameters for running shell commands."""
    command: str = Field(description="The command to execute")
    working_dir: Optional[str] = Field(None, description="Directory to execute the command in")


class FileParams(BaseModel):
    """Parameters for file operations."""
    file_path: str = Field(description="Path to the file")


class ColoredDiffParams(BaseModel):
    """Parameters for creating a colored diff."""
    original: str = Field(description="Original content")
    modified: str = Field(description="Modified content")
    filename: str = Field(description="Filename for the diff header")


class ApplyPatchParams(BaseModel):
    """Parameters for applying a patch."""
    patch_content: str = Field(description="Patch content in the specified format")


class ChangeDirParams(BaseModel):
    """Params for changing the working directory."""
    directory: str = Field(description="Path to the directory to switch into")

class OSCommandParams(BaseModel):
    """Parameters for OS command execution."""
    command: str = Field(description="The OS command to execute")
    args: List[str] = Field(description="Command arguments")

class RuffParams(BaseModel):
    paths: List[str]
    flags: List[str] = Field(default_factory=list)


class GetContextParams(BaseModel):
    """Parameters for getting the context information."""
    include_details: bool = Field(
        description="Whether to include detailed information"
    )

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

@function_tool
def get_context_response(wrapper: RunContextWrapper[EnhancedContextData]) -> GetContextResponse:
    ctx = wrapper.context
    return GetContextResponse(
        chat_history="\n".join(f"{m['role']}: {m['content']}" for m in ctx.get_chat_history()),
        context_summary=ctx.get_context_summary(),
        recent_files=[r.value for r in ctx.get_recent_entities("file")],
        recent_commands=[r.value for r in ctx.get_recent_entities("command")],
        token_usage=ctx.token_count,
        max_tokens=ctx.max_tokens
    )

# Tool implementations
@function_tool
async def run_ruff(wrapper: RunContextWrapper[None], params: RuffParams) -> str:
    logger.debug(json.dumps({"tool": "run_ruff", "params": params.model_dump()}))
    cmd = ["ruff", "check", *params.paths, *params.flags]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    output = stdout.decode() or stderr.decode()
    logger.debug(json.dumps({"tool": "run_ruff", "output": output}))
    return output

@function_tool
async def run_pylint(wrapper: RunContextWrapper[None], params: PylintParams) -> str:
    logger.debug(json.dumps({"tool": "run_pylint", "params": params.model_dump()}))
    cmd = ["pylint", params.file_path] + params.options
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() if stdout else stderr.decode()
        logger.debug(json.dumps({"tool": "run_pylint", "output": output}))
        return output
    except Exception as e:
        logger.debug(json.dumps({"tool": "run_pylint", "error": str(e)}))
        return f"Error running pylint: {str(e)}"


@function_tool
async def run_pyright(wrapper: RunContextWrapper[None], params: PyrightParams) -> str:
    logger.debug(json.dumps({"tool": "run_pyright", "params": params.model_dump()}))
    cmd = ["pyright", *params.targets, *params.options, "--outputjson"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() if stdout else stderr.decode()
        logger.debug(json.dumps({"tool": "run_pyright", "output": output}))
        return output
    except Exception as e:
        logger.debug(json.dumps({"tool": "run_pyright", "error": str(e)}))
        return f"Error running pyright: {str(e)}"


@function_tool
async def run_command(wrapper: RunContextWrapper[EnhancedContextData], params: CommandParams) -> str:
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
        wrapper.context.remember_command(params.command, output)
        # Track command entity in context
        track_command_entity(wrapper.context, params.command, output)
        logger.debug(json.dumps({"tool": "run_command", "output": output}))
        return output
    except Exception as e:
        logger.debug(json.dumps({"tool": "run_command", "error": str(e)}))
        return f"Error executing command: {str(e)}"


@function_tool
async def read_file(wrapper: RunContextWrapper[EnhancedContextData], params: FileParams) -> dict:
    logger.debug(json.dumps({"tool": "read_file", "params": params.model_dump()}))
    try:
        # Normalize path
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
        if file_size > 5 * 1024 * 1024:
            return {"error": f"File too large ({file_size / 1024 / 1024:.2f} MB). Maximum size is 5 MB."}
        # Read file
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
        result = {
            "content": content,
            "metadata": metadata
        }
        logger.debug(json.dumps({"tool": "read_file", "result_size": len(content)}))
        return result
    except Exception as e:
        logger.debug(json.dumps({"tool": "read_file", "error": str(e)}))
        return {"error": f"Error reading file: {str(e)}"}


@function_tool
async def create_colored_diff(wrapper: RunContextWrapper[None], params: ColoredDiffParams) -> str:
    logger.debug(json.dumps({"tool": "create_colored_diff", "params": params.model_dump()}))
    original_lines = params.original.splitlines()
    modified_lines = params.modified.splitlines()
    
    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f'a/{params.filename}',
        tofile=f'b/{params.filename}',
        lineterm=''
    )
    result = '\n'.join(diff)
    logger.debug(json.dumps({"tool": "create_colored_diff", "diff_line_count": len(result.splitlines())}))
    return result


@function_tool
async def apply_patch(wrapper: RunContextWrapper[None], params: ApplyPatchParams) -> str:
    logger.debug(json.dumps({"tool": "apply_patch", "params": {"filename": "<patch>"}}))
    try:
        # write the patch content to a temp file
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".patch") as tf:
            tf.write(params.patch_content)
            tf.flush()
            tmp = tf.name

        apply_patch_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "apply_patch.py")
        )
        # Call with the temp‐file path so input() reads your terminal
        proc = await asyncio.create_subprocess_exec(
            "python3", apply_patch_path, tmp
        )
        returncode = await proc.wait()

        # Clean up
        os.unlink(tmp)

        if returncode != 0:
            return "Patch was not applied."
        return "Patch applied."
    except Exception as e:
        logger.debug(json.dumps({"tool": "apply_patch", "error": str(e)}))
        return f"Error applying patch: {e}"


@function_tool
async def change_dir(wrapper: RunContextWrapper[EnhancedContextData], params: ChangeDirParams) -> str:
    """
    Change the agent's working directory.
    """
    try:
        os.chdir(params.directory)
        # update your context so get_context_summary stays in sync
        wrapper.context.working_directory = params.directory
        return f"✅ Working directory changed to {params.directory}"
    except Exception as e:
        return f"❌ Error changing directory: {e}"


class CommandResult(TypedDict):
    stdout: str
    stderr: str
    returncode: int


@function_tool
async def os_command(wrapper: RunContextWrapper[None], params: OSCommandParams) -> CommandResult:
    logger.debug(json.dumps({"tool": "os_command", "params": params.model_dump()}))
    try:
        proc = await asyncio.create_subprocess_exec(
            params.command, *params.args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        # ensure returncode is int, not None
        rc = proc.returncode if proc.returncode is not None else -1
        output: CommandResult = {
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": rc
        }
        # Track command entity in context (stdout preview)
        track_command_entity(wrapper.context, params.command, output["stdout"])
        logger.debug(json.dumps({"tool": "os_command", "output": output}))
        return output
    except Exception as e:
        # match CommandResult shape on error
        error_output: CommandResult = {
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "returncode": -1
        }
        return error_output


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
async def get_context(wrapper: RunContextWrapper[EnhancedContextData], params: GetContextParams) -> str:
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

