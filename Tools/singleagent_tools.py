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
from agents import RunContextWrapper
from . import function_tool
from The_Agents.context_data import EnhancedContextData
import logging

# Import shared tools and utilities
from .shared_tools import (
    track_file_entity, track_command_entity,
    get_context_response, add_manual_context, run_command, read_file, get_context,
    GetContextParams, GetContextResponse, AddManualContextParams, RunCommandParams, FileReadParams
)

from utilities.logging_setup import setup_logging

setup_logging(__name__)
logger = logging.getLogger(__name__)

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
@function_tool(name="run_ruff", description="Run the ruff linter on the given paths.")
async def run_ruff(wrapper: RunContextWrapper[None], params: RuffParams) -> str:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("run_ruff params=%s", params.model_dump())
    cmd = ["ruff", "check", *params.paths, *params.flags]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    output = stdout.decode() or stderr.decode()
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("run_ruff output=%s", output)
    return output

@function_tool(name="run_pylint", description="Execute pylint on a file with optional arguments.")
async def run_pylint(wrapper: RunContextWrapper[None], params: PylintParams) -> str:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("run_pylint params=%s", params.model_dump())
    cmd = ["pylint", params.file_path] + params.options
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() if stdout else stderr.decode()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("run_pylint output=%s", output)
        return output
    except Exception as e:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("run_pylint error=%s", e)
        return f"Error running pylint: {str(e)}"


@function_tool(name="run_pyright", description="Run the pyright type checker on targets.")
async def run_pyright(wrapper: RunContextWrapper[None], params: PyrightParams) -> str:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("run_pyright params=%s", params.model_dump())
    cmd = ["pyright", *params.targets, *params.options, "--outputjson"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() if stdout else stderr.decode()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("run_pyright output=%s", output)
        return output
    except Exception as e:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("run_pyright error=%s", e)
        return f"Error running pyright: {str(e)}"


# Parameter model aliases for compatibility
CommandParams = RunCommandParams
FileParams = FileReadParams

@function_tool(name="create_colored_diff", description="Generate a unified diff between two text versions.")
async def create_colored_diff(wrapper: RunContextWrapper[None], params: ColoredDiffParams) -> str:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("create_colored_diff params=%s", params.model_dump())
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
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("create_colored_diff diff_line_count=%d", len(result.splitlines()))
    return result


@function_tool(name="apply_patch", description="Apply a patch to files with a colored preview.")
async def apply_patch(wrapper: RunContextWrapper[None], params: ApplyPatchParams) -> str:
    """Apply a patch to files using the apply_patch.py script with enhanced colored diff preview."""
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("apply_patch params=%s", params.model_dump())
    
    # Resolve path to apply_patch.py: prefer root shim, fallback to scripts/apply_patch.py
    project_root = os.path.dirname(os.path.dirname(__file__))
    root_shim = os.path.join(project_root, "apply_patch.py")
    scripts_impl = os.path.join(project_root, "scripts", "apply_patch.py")
    apply_patch_path = root_shim if os.path.isfile(root_shim) else scripts_impl
    if not os.path.isfile(apply_patch_path):
        err = f"apply_patch.py not found. Expected at {root_shim} or {scripts_impl}"
        logger.error(err)
        return f"Error applying patch: {err}"

    # Determine the command args based on auto_confirm
    cmd_args = [sys.executable, apply_patch_path]
    if params.auto_confirm:
        cmd_args.append("--no-preview")  # Skip preview and apply directly
    else:
        # Use default behavior (show preview + ask for confirmation)
        # But since we're in a non-interactive subprocess, we need to handle this
        try:
            is_tty = sys.stdin.isatty() and sys.stdout.isatty()
        except Exception:
            is_tty = False

        if not is_tty:
            # In non-interactive mode, show preview only
            cmd_args.append("--preview")
            preview_only = True
        else:
            preview_only = False

    # Create subprocess with PIPE for stdin/stdout/stderr
    proc = await asyncio.create_subprocess_exec(
        *cmd_args,
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
    
    # Print the colored output from the enhanced apply_patch script
    print(output)
    
    if params.auto_confirm:
        logger.debug(f"Apply patch output: {output}")
        track_command_entity(wrapper.context, f"apply_patch", output) if hasattr(wrapper.context, 'track_entity') else None
        return f"{GREEN}✓ Patch applied successfully!{RESET}"
    else:
        if hasattr(wrapper.context, 'track_entity'):
            track_command_entity(wrapper.context, f"apply_patch_preview", output)
        
        if "Preview complete" in output:
            return f"{YELLOW}📋 Patch preview shown above. To apply, set auto_confirm=True or run manually.{RESET}"
        else:
            return f"{GREEN}✓ Patch applied successfully!{RESET}"

@function_tool(name="change_dir", description="Change the agent's current working directory.")
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


@function_tool(name="os_command", description="Execute an operating system command.")
async def os_command(wrapper: RunContextWrapper[None], params: OSCommandParams) -> CommandResult:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("os_command params=%s", params.model_dump())
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
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("os_command output=%s", output)
        return output
    except Exception as e:
        # match CommandResult shape on error
        error_output: CommandResult = {
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "returncode": -1
        }
        return error_output




