"""
Tools for the code assistant agent.
Contains various tools according to OpenAI Agents SDK specs with Pydantic v2 compatibility.
"""

import os
import subprocess
import tempfile
import difflib
import asyncio
from typing import List, Optional, Union, TypedDict
from typing_extensions import Annotated

from pydantic import BaseModel, Field

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
    """Parameters for changing the working directory."""
    directory: str = Field(description="Directory to change to")


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


# Tool implementations
@function_tool
async def run_ruff(wrapper: RunContextWrapper[None], params: RuffParams) -> str:
    logger.debug(json.dumps({"tool": "run_ruff", "params": params.dict()}))
    cmd = ["ruff", "check", *params.paths, *params.flags, "--format=json"]
    result = subprocess.run(cmd, text=True, capture_output=True)
    logger.debug(json.dumps({"tool": "run_ruff", "output": result.stdout or result.stderr}))
    return result.stdout or result.stderr

@function_tool
async def run_pylint(wrapper: RunContextWrapper[None], params: PylintParams) -> str:
    logger.debug(json.dumps({"tool": "run_pylint", "params": params.dict()}))
    cmd = ["pylint", params.file_path] + params.options
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        output = result.stdout if result.stdout else result.stderr
        logger.debug(json.dumps({"tool": "run_pylint", "output": output}))
        return output
    except Exception as e:
        logger.debug(json.dumps({"tool": "run_pylint", "error": str(e)}))
        return f"Error running pylint: {str(e)}"


@function_tool
async def run_pyright(wrapper: RunContextWrapper[None], params: PyrightParams) -> str:
    logger.debug(json.dumps({"tool": "run_pyright", "params": params.dict()}))
    cmd = ["pyright", *params.targets, *params.options, "--outputjson"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        output = result.stdout if result.stdout else result.stderr
        logger.debug(json.dumps({"tool": "run_pyright", "output": output}))
        return output
    except Exception as e:
        logger.debug(json.dumps({"tool": "run_pyright", "error": str(e)}))
        return f"Error running pyright: {str(e)}"


@function_tool
async def run_command(wrapper: RunContextWrapper[EnhancedContextData], params: CommandParams) -> str:
    logger.debug(json.dumps({"tool": "run_command", "params": params.dict()}))
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
        logger.debug(json.dumps({"tool": "run_command", "output": output}))
        return output
    except Exception as e:
        logger.debug(json.dumps({"tool": "run_command", "error": str(e)}))
        return f"Error executing command: {str(e)}"


@function_tool
async def read_file(wrapper: RunContextWrapper[EnhancedContextData], params: FileParams) -> str:
    logger.debug(json.dumps({"tool": "read_file", "params": params.dict()}))
    try:
        content = await asyncio.to_thread(lambda: open(params.file_path, 'r', encoding='utf-8').read())
        wrapper.context.remember_file(params.file_path, content)
        logger.debug(json.dumps({"tool": "read_file", "output_length": len(content)}))
        return content
    except Exception as e:
        logger.debug(json.dumps({"tool": "read_file", "error": str(e)}))
        return f"Error reading file: {str(e)}"


@function_tool
async def create_colored_diff(wrapper: RunContextWrapper[None], params: ColoredDiffParams) -> str:
    logger.debug(json.dumps({"tool": "create_colored_diff", "params": params.dict()}))
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
        result = subprocess.run(
            ["python3", apply_patch_path, tmp],
            text=True,
            stdout=None,  # inherit, so you see the prompt and messages
            stderr=None
        )

        # Clean up
        os.unlink(tmp)

        # if user aborted or error, return nonzero → raise
        if result.returncode != 0:
            return "Patch was not applied."

        # success
        return "Patch applied."
    except Exception as e:
        logger.debug(json.dumps({"tool": "apply_patch", "error": str(e)}))
        return f"Error applying patch: {e}"


@function_tool
async def change_dir(wrapper: RunContextWrapper[EnhancedContextData], params: ChangeDirParams) -> str:
    logger.debug(json.dumps({"tool": "change_dir", "params": params.dict()}))
    try:
        os.chdir(params.directory)
        new_dir = os.getcwd()
        wrapper.context.working_directory = new_dir
        wrapper.context.remember_command(f"cd {params.directory}")
        logger.debug(json.dumps({"tool": "change_dir", "output": new_dir}))
        return f"Changed directory to: {new_dir}"
    except Exception as e:
        logger.debug(json.dumps({"tool": "change_dir", "error": str(e)}))
        return f"Error changing directory: {str(e)}"


class CommandResult(TypedDict):
    stdout: str
    stderr: str
    returncode: int


@function_tool
async def os_command(wrapper: RunContextWrapper[None], params: OSCommandParams) -> CommandResult:
    logger.debug(json.dumps({"tool": "os_command", "params": params.dict()}))
    try:
        result = subprocess.run(
            [params.command] + params.args,
            capture_output=True,
            text=True,
            check=False
        )
        # explicitly type as CommandResult for Pylance
        output: CommandResult = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
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
async def get_context(wrapper: RunContextWrapper[EnhancedContextData], params: GetContextParams) -> str:
    logger.debug(json.dumps({"tool": "get_context", "params": params.dict()}))
    context = wrapper.context
    info = [
        f"Working directory: {context.working_directory}",
    ]
    if context.current_file:
        info.append(f"Current file: {context.current_file}")
    
    # Add chat history to context information
    if hasattr(context, 'chat_messages') and context.chat_messages:
        info.append("\nRecent Chat History:")
        # Show the last 5 messages or all if there are fewer
        history_to_show = context.chat_messages[-5:] if len(context.chat_messages) > 5 else context.chat_messages
        for i, (role, content) in enumerate(history_to_show):
            # Truncate long messages in the summary
            if len(content) > 100:
                content = content[:97] + "..."
            info.append(f"- {role.capitalize()}: {content}")
    
    if params.include_details:
        info.append("\nMemory items:")
        for item in context.memory_items:
            ts = item.timestamp.strftime("%H:%M:%S")
            info.append(f"- {item.item_type}: {item.content} (at {ts})")
    else:
        summary = context.get_memory_summary()
        if (summary):
            info.append(summary)
    result = "\n".join(info)
    logger.debug(json.dumps({"tool": "get_context", "output_length": len(result)}))
    return result

