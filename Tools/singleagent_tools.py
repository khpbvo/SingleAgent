"""
Tools for the code assistant agent.
Contains various tools according to OpenAI Agents SDK specs with Pydantic v2 compatibility.
"""

import os
import sys  # Required for stdin/stdout handling
import subprocess
import tempfile
import difflib
import asyncio
import time
from datetime import datetime
from typing import List, Optional, Union, TypedDict, Dict, Any, Tuple, cast
from typing_extensions import Annotated

from pydantic import BaseModel, Field

# ANSI color codes for colored output
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
RESET = "\033[0m"

import os
from agents import function_tool, RunContextWrapper
from The_Agents.context_data import EnhancedContextData
import json
import logging
from logging.handlers import RotatingFileHandler

# Import shared tools and utilities
from .shared_tools import (
    track_file_entity, track_command_entity,
    get_context_response, add_manual_context, run_command, read_file, get_context,
    GetContextParams, GetContextResponse, AddManualContextParams, RunCommandParams, FileReadParams
)

# Configure logger for tools
tool_logger = logging.getLogger(__name__)
tool_logger.setLevel(logging.DEBUG)
# rotating file handler for tools.log
tools_handler = RotatingFileHandler('logs/tools.log', maxBytes=10*1024*1024, backupCount=3)
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


class ColoredDiffParams(BaseModel):
    """Parameters for creating a colored diff."""
    original: str = Field(description="Original content")
    modified: str = Field(description="Modified content")
    filename: str = Field(description="Filename for the diff header")


class ApplyPatchParams(BaseModel):
    """Parameters for applying a patch."""
    patch_content: str = Field(description="Patch content in the specified format")
    auto_confirm: bool = Field(
        default=False,
        description="If true, apply the patch without interactive confirmation. Recommended for non-interactive runs."
    )


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


# Parameter model aliases for compatibility
CommandParams = RunCommandParams
FileParams = FileReadParams

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
    """Apply a patch to files using the apply_patch.py script with colored diff preview."""
    logger.debug(json.dumps({"tool": "apply_patch", "params": params.model_dump()}))
    
    # First, show the patch content for preview
    print(f"\n{BLUE}=== Patch Preview ==={RESET}")
    
    # Split the patch into sections by file
    patch_lines = params.patch_content.splitlines()
    current_file = None
    file_sections = {}
    current_section = []
    
    for line in patch_lines:
        if line.startswith("*** Add File:") or line.startswith("*** Update File:") or line.startswith("*** Delete File:"):
            if current_file and current_section:
                file_sections[current_file] = current_section
            current_file = line
            current_section = [line]
        elif current_file:
            current_section.append(line)
    
    # Add the last section
    if current_file and current_section:
        file_sections[current_file] = current_section
    
    # Print each section with colored formatting
    for file_header, section in file_sections.items():
        if "Add File" in file_header:
            print(f"\n{GREEN}{file_header}{RESET}")
            for line in section[1:]:  # Skip the header
                if line.startswith("+"):
                    print(f"{GREEN}{line}{RESET}")
                elif line == "*** End of File":
                    continue
                else:
                    print(line)
        elif "Delete File" in file_header:
            print(f"\n{RED}{file_header}{RESET}")
            for line in section[1:]:  # Skip the header
                if line.startswith("-"):
                    print(f"{RED}{line}{RESET}")
                elif line == "*** End of File":
                    continue
                else:
                    print(line)
        elif "Update File" in file_header:
            print(f"\n{YELLOW}{file_header}{RESET}")
            for line in section[1:]:  # Skip the header
                if line.startswith("+"):
                    print(f"{GREEN}{line}{RESET}")
                elif line.startswith("-"):
                    print(f"{RED}{line}{RESET}")
                elif line == "*** End of File":
                    continue
                else:
                    print(line)
    
    # Confirmation handling
    if not params.auto_confirm:
        # If in a non-interactive context, avoid blocking on input()
        try:
            is_tty = sys.stdin.isatty() and sys.stdout.isatty()
        except Exception:
            is_tty = False

        if not is_tty:
            return (
                "Non-interactive environment detected; not applying patch. "
                "Pass auto_confirm=true to apply without prompt."
            )

        # Interactive confirmation
        print(f"\n{YELLOW}Apply these changes? [y/N]{RESET} ", end="", flush=True)
        try:
            user_input = input().strip().lower()
        except EOFError:
            return (
                "Input stream closed; not applying patch. "
                "Pass auto_confirm=true to apply without prompt."
            )
        if user_input != "y":
            return "Patch application cancelled by user."
    
    # User confirmed, proceed with applying the patch
    # Resolve path to apply_patch.py: prefer root shim, fallback to scripts/apply_patch.py
    project_root = os.path.dirname(os.path.dirname(__file__))
    root_shim = os.path.join(project_root, "apply_patch.py")
    scripts_impl = os.path.join(project_root, "scripts", "apply_patch.py")
    apply_patch_path = root_shim if os.path.isfile(root_shim) else scripts_impl
    if not os.path.isfile(apply_patch_path):
        err = f"apply_patch.py not found. Expected at {root_shim} or {scripts_impl}"
        logger.error(err)
        return f"Error applying patch: {err}"

    # Create subprocess with PIPE for stdin/stdout/stderr using current interpreter
    proc = await asyncio.create_subprocess_exec(
        sys.executable, apply_patch_path,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Send the patch content to stdin of apply_patch.py
    stdout, stderr = await proc.communicate(params.patch_content.encode('utf-8'))
    
    # Handle output
    if stderr:
        error_msg = stderr.decode('utf-8').strip()
        logger.error(f"Error applying patch: {error_msg}")
        return f"Error applying patch: {error_msg}"
    
    output = stdout.decode('utf-8').strip()
    logger.debug(f"Apply patch output: {output}")
    track_command_entity(wrapper.context, f"apply_patch", output) if hasattr(wrapper.context, 'track_entity') else None
    
    return f"{GREEN}✓ Patch applied successfully!{RESET}"

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




