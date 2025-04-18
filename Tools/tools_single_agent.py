"""
Tools for the code assistant agent.
Contains various tools according to OpenAI Agents SDK specs with Pydantic v2 compatibility.
"""

import os
import subprocess
import tempfile
import difflib
from typing import List, Optional, Union, TypedDict
from typing_extensions import Annotated

from pydantic import BaseModel, Field

from agents import function_tool, RunContextWrapper


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

# Tool implementations
@function_tool
async def run_ruff(wrapper: RunContextWrapper[None], params: RuffParams) -> str:
    cmd = ["ruff", "check", *params.paths, *params.flags, "--format=json"]
    result = subprocess.run(cmd, text=True, capture_output=True)
    return result.stdout or result.stderr

@function_tool
async def run_pylint(wrapper: RunContextWrapper[None], params: PylintParams) -> str:
    """
    Run pylint on the specified file with the given options.
    
    Args:
        params: Parameters including file path and pylint options
    """
    cmd = ["pylint", params.file_path] + params.options
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error running pylint: {str(e)}"


@function_tool
async def run_pyright(wrapper: RunContextWrapper[None], params: PyrightParams) -> str:
    """
    Run pyright on the specified targets with the provided options.

    Args:
        params: Parameters including the targets list and extra flags.
    """
    cmd = ["pyright", *params.targets, *params.options, "--outputjson"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        output = result.stdout if result.stdout else result.stderr
        return output
    except Exception as e:
        return f"Error running pyright: {str(e)}"


@function_tool
async def run_command(wrapper: RunContextWrapper[None], params: CommandParams) -> str:
    """
    Run a shell command and return the output.
    
    Args:
        params: Parameters including the command to execute and optional working directory
    """
    working_dir = params.working_dir if params.working_dir is not None else os.getcwd()
    try:
        result = subprocess.run(
            params.command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
            cwd=working_dir
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if not output:
            output = "Command executed successfully with no output."
        return output
    except Exception as e:
        return f"Error executing command: {str(e)}"


@function_tool
async def read_file(wrapper: RunContextWrapper[None], params: FileParams) -> str:
    """
    Read the contents of a file.
    
    Args:
        params: Parameters including the file path
    """
    try:
        with open(params.file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@function_tool
async def create_colored_diff(wrapper: RunContextWrapper[None], params: ColoredDiffParams) -> str:
    """
    Create a colored diff between original and modified content.
    
    Args:
        params: Parameters including original and modified content and filename
    """
    original_lines = params.original.splitlines()
    modified_lines = params.modified.splitlines()
    
    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f'a/{params.filename}',
        tofile=f'b/{params.filename}',
        lineterm=''
    )
    
    return '\n'.join(diff)


@function_tool
async def apply_patch(wrapper: RunContextWrapper[None], params: ApplyPatchParams) -> str:
    """
    Apply a patch using the apply_patch.py utility.
    
    Args:
        params: Parameters including the patch content
    """
    try:
        # Create a temporary file to store the patch
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(params.patch_content)
            temp_file_path = temp_file.name
        
        # Run the apply_patch.py script with the patch content
        result = subprocess.run(
            f"python apply_patch.py < {temp_file_path}",
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        
        return output
    except Exception as e:
        return f"Error applying patch: {str(e)}"


@function_tool
async def change_dir(wrapper: RunContextWrapper[None], params: ChangeDirParams) -> str:
    """
    Change the current working directory.
    
    Args:
        params: Parameters including the directory to change to
    """
    try:
        os.chdir(params.directory)
        return f"Changed directory to: {os.getcwd()}"
    except Exception as e:
        return f"Error changing directory: {str(e)}"


class CommandResult(TypedDict):
    stdout: str
    stderr: str
    returncode: int


@function_tool
async def os_command(wrapper: RunContextWrapper[None], params: OSCommandParams) -> CommandResult:
    """
    Execute an OS command with arguments and return structured output.
    
    Args:
        params: Parameters including the command and its arguments
    """
    try:
        result = subprocess.run(
            [params.command] + params.args,
            capture_output=True,
            text=True,
            check=False
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "returncode": -1
        }

