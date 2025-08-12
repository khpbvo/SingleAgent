"""
Shared tools for both the SingleAgent and ArchitectAgent.
Contains common tools used by both agents to avoid duplication.
"""

import os
import json
import logging
import asyncio
import shlex
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, cast
from typing_extensions import Annotated

from pydantic import BaseModel, Field
from logging.handlers import RotatingFileHandler

from agents import function_tool, RunContextWrapper
from The_Agents.context_data import EnhancedContextData
from The_Agents.shared_context_manager import SharedContextManager, TaskPriority
from The_Agents.workflows import WorkflowOrchestrator

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

# Simple module-level cache for file reads keyed by absolute path
# Each entry stores mtime, size, content, and metadata
_file_cache: Dict[str, Dict[str, Any]] = {}

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
    stream_output: bool = Field(False, description="Stream output to caller in real time")

class FileReadParams(BaseModel):
    """Parameters for reading a file."""
    file_path: str = Field(description="Path to the file to read")

# Cross-agent communication parameter models
class RequestArchitectureReviewParams(BaseModel):
    """Parameters for requesting an architecture review."""
    component: str = Field(description="Component or feature to review")
    description: str = Field(description="Detailed description of what needs review")
    priority: str = Field("medium", description="Priority level (high, medium, low)")
    
    class Config:
        extra = "forbid"

class RequestImplementationParams(BaseModel):
    """Parameters for requesting implementation from code agent."""
    feature: str = Field(description="Feature or component to implement")
    specification: str = Field(description="Detailed specification for implementation")
    priority: str = Field("medium", description="Priority level (high, medium, low)")
    
    class Config:
        extra = "forbid"

class ShareInsightParams(BaseModel):
    """Parameters for sharing an insight with the other agent."""
    insight: str = Field(description="The insight to share")
    category: str = Field(description="Category (architecture, bug, optimization, security, etc.)")
    
    class Config:
        extra = "forbid"

class RecordArchitecturalDecisionParams(BaseModel):
    """Parameters for recording an architectural decision."""
    decision: str = Field(description="The architectural decision")
    rationale: str = Field(description="Why this decision was made")
    
    class Config:
        extra = "forbid"

class GetCollaborationStatusParams(BaseModel):
    """Parameters for getting collaboration status."""
    verbose: bool = Field(False, description="Whether to include detailed information")
    
    class Config:
        extra = "forbid"

# Workflow parameter models
class StartFeatureWorkflowParams(BaseModel):
    """Parameters for starting a feature implementation workflow."""
    feature_name: str = Field(description="Name of the feature to implement")
    requirements: str = Field(description="Detailed requirements for the feature")
    
    class Config:
        extra = "forbid"

class StartBugfixWorkflowParams(BaseModel):
    """Parameters for starting a bug fix workflow."""
    bug_description: str = Field(description="Description of the bug to fix")
    
    class Config:
        extra = "forbid"

class StartRefactorWorkflowParams(BaseModel):
    """Parameters for starting a refactoring workflow."""
    component: str = Field(description="Component or module to refactor")
    refactoring_goals: str = Field(description="Goals and objectives for the refactoring")
    
    class Config:
        extra = "forbid"

class GetWorkflowStatusParams(BaseModel):
    """Parameters for getting workflow status."""
    workflow_id: str = Field(description="ID of the workflow to check")
    
    class Config:
        extra = "forbid"

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
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("add_manual_context params=%s", params.model_dump())
    
    try:
        # Use read_file to leverage caching and tracking
        result = await read_file(wrapper, FileReadParams(file_path=params.file_path))
        if "error" in result:
            return f"Error: {result['error']}"

        content = result["content"]
        if not content:
            return f"Error: Empty file at {params.file_path}"

        # Add to context
        label = wrapper.context.add_manual_context(
            content=content,
            source=params.file_path,
            label=params.label
        )

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
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("run_command params=%s", params.model_dump())
    working_dir = params.working_dir if params.working_dir is not None else os.getcwd()
    try:
        proc = await asyncio.create_subprocess_exec(
            *shlex.split(params.command),
            cwd=working_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_lines: List[str] = []
        stderr_lines: List[str] = []

        async def _read_stream(stream: asyncio.StreamReader, collector: List[str]):
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode()
                collector.append(text)
                if params.stream_output:
                    # Stream output incrementally to caller
                    print(text, end="", flush=True)

        stdout_task = asyncio.create_task(_read_stream(proc.stdout, stdout_lines))
        stderr_task = asyncio.create_task(_read_stream(proc.stderr, stderr_lines))

        await asyncio.gather(stdout_task, stderr_task)
        await proc.wait()

        output = "".join(stdout_lines)
        if stderr_lines:
            output += f"\nSTDERR:\n{''.join(stderr_lines)}"
        if not output:
            output = "Command executed successfully with no output."

        # Track command entity in context
        track_command_entity(wrapper.context, params.command, output)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("run_command output=%s", output)
        return output
    except Exception as e:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("run_command error=%s", e)
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
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("read_file params=%s", params.model_dump())
    
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

        # Check cache: reuse content and metadata if unchanged
        cached = False
        cache_entry = _file_cache.get(file_path)
        if cache_entry and cache_entry["mtime"] == file_stats.st_mtime and cache_entry["size"] == file_size:
            content = cache_entry["content"]
            metadata = cache_entry["metadata"]
            cached = True
        else:
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

            metadata = {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": file_size,
                "file_extension": file_extension,
                "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "token_count": wrapper.context.count_tokens(content),
                "line_count": content.count('\n') + 1
            }

            _file_cache[file_path] = {
                "mtime": file_stats.st_mtime,
                "size": file_size,
                "content": content,
                "metadata": metadata,
            }

        # Track file in context using content (cached or new)
        track_file_entity(wrapper.context, file_path, content)
        codex/add-lru-cache-for-read_file

        result = {"content": content, "metadata": metadata}

        logger.debug(json.dumps({"tool": "read_file", "result_size": len(content), "cached": cached}))
        
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

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("read_file result_size=%d", len(content))
        main
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
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("get_context params=%s", params.model_dump())
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
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("get_context output_length=%d", len(result))
    return result

# Cross-agent communication tools
@function_tool
async def request_architecture_review(wrapper: RunContextWrapper[EnhancedContextData], params: RequestArchitectureReviewParams) -> str:
    """
    Request an architecture review from the Architect Agent.
    
    Use this when you need architectural guidance or validation for your implementation.
    The Architect Agent will analyze the component and provide design recommendations.
    
    Args:
        component: Component or feature to review
        description: Detailed description of what needs review
        context: Additional context for the review
        priority: Priority level (high, medium, low)
        
    Returns:
        Confirmation message with task ID
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("request_architecture_review params=%s", params.model_dump())
    
    # Get the shared context manager from metadata
    shared_manager = wrapper.context.metadata.get("shared_manager")
    if not shared_manager:
        return "Error: Shared context manager not available. Please ensure the system is properly initialized."
    
    # Get current agent name from context
    current_agent = wrapper.context.metadata.get("agent_name", "code")
    
    # Create task for architect
    task_id = shared_manager.add_task(
        target_agent="architect",
        task=f"Architecture review requested for {params.component}: {params.description}",
        created_by=current_agent,
        priority=TaskPriority(params.priority),
        context={}
    )
    
    return f"Architecture review requested successfully. Task ID: {task_id}. Switch to Architect Agent (!architect) to process this request."

@function_tool
async def request_implementation(wrapper: RunContextWrapper[EnhancedContextData], params: RequestImplementationParams) -> str:
    """
    Request implementation from the Code Agent.
    
    Use this when architectural design is complete and you need the Code Agent
    to implement a specific feature or component.
    
    Args:
        feature: Feature or component to implement
        specification: Detailed specification for implementation
        architectural_constraints: Architectural constraints to follow
        priority: Priority level (high, medium, low)
        
    Returns:
        Confirmation message with task ID
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("request_implementation params=%s", params.model_dump())
    
    # Get the shared context manager from metadata
    shared_manager = wrapper.context.metadata.get("shared_manager")
    if not shared_manager:
        return "Error: Shared context manager not available. Please ensure the system is properly initialized."
    
    # Get current agent name from context
    current_agent = wrapper.context.metadata.get("agent_name", "architect")
    
    # Create task for code agent
    context = {
        "specification": params.specification
    }
    
    task_id = shared_manager.add_task(
        target_agent="code",
        task=f"Implement {params.feature}",
        created_by=current_agent,
        priority=TaskPriority(params.priority),
        context=context
    )
    
    return f"Implementation task created successfully. Task ID: {task_id}. Switch to Code Agent (!code) to implement this feature."

@function_tool
async def share_insight(wrapper: RunContextWrapper[EnhancedContextData], params: ShareInsightParams) -> str:
    """
    Share an insight or discovery with the other agent.
    
    Use this to communicate important findings, bugs, optimizations, or design
    patterns that the other agent should be aware of.
    
    Args:
        insight: The insight to share
        category: Category (architecture, bug, optimization, security, etc.)
        related_files: Related file paths
        metadata: Additional metadata
        
    Returns:
        Confirmation message with insight ID
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("share_insight params=%s", params.model_dump())
    
    # Get the shared context manager from metadata
    shared_manager = wrapper.context.metadata.get("shared_manager")
    if not shared_manager:
        return "Error: Shared context manager not available. Please ensure the system is properly initialized."
    
    # Get current agent name from context
    current_agent = wrapper.context.metadata.get("agent_name", "unknown")
    
    # Add insight
    insight_id = shared_manager.add_insight(
        agent=current_agent,
        insight=params.insight,
        category=params.category,
        metadata={},
        related_files=[]
    )
    
    return f"Insight shared successfully. ID: {insight_id}. The other agent will see this insight when they check collaboration status."

@function_tool
async def record_architectural_decision(wrapper: RunContextWrapper[EnhancedContextData], params: RecordArchitecturalDecisionParams) -> str:
    """
    Record an important architectural decision.
    
    Use this to document architectural decisions that will affect the implementation.
    These decisions will be available to both agents and help maintain consistency.
    
    Args:
        decision: The architectural decision
        rationale: Why this decision was made
        affected_components: Components affected by this decision
        constraints: Constraints considered
        
    Returns:
        Confirmation message with decision ID
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("record_architectural_decision params=%s", params.model_dump())
    
    # Get the shared context manager from metadata
    shared_manager = wrapper.context.metadata.get("shared_manager")
    if not shared_manager:
        return "Error: Shared context manager not available. Please ensure the system is properly initialized."
    
    # Record decision
    decision_id = shared_manager.add_architectural_decision(
        decision=params.decision,
        rationale=params.rationale,
        affected_components=[],
        constraints=[]
    )
    
    return f"Architectural decision recorded successfully. ID: {decision_id}. This decision will guide future implementations."

@function_tool
async def get_collaboration_status(wrapper: RunContextWrapper[EnhancedContextData], params: GetCollaborationStatusParams) -> str:
    """
    Get the current collaboration status between agents.
    
    Shows pending tasks, recent insights, architectural decisions, and active workflows.
    Use this to understand what work is pending and what the other agent has discovered.
    
    Args:
        verbose: Whether to include detailed information
        
    Returns:
        Collaboration status summary
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("get_collaboration_status params=%s", params.model_dump())
    
    # Get the shared context manager from metadata
    shared_manager = wrapper.context.metadata.get("shared_manager")
    if not shared_manager:
        return "Error: Shared context manager not available. Please ensure the system is properly initialized."
    
    # Get current agent name
    current_agent = wrapper.context.metadata.get("agent_name", "unknown")
    
    # Get summary
    summary = shared_manager.get_collaboration_summary()
    
    # Build response
    lines = ["=== Collaboration Status ==="]
    
    # Pending tasks for current agent
    pending_tasks = shared_manager.get_pending_tasks(current_agent)
    if pending_tasks:
        lines.append(f"\n📋 Pending Tasks for You ({len(pending_tasks)}):")
        for task in pending_tasks[:5]:  # Show first 5
            lines.append(f"  - [{task.priority.upper()}] {task.task} (from {task.created_by})")
            if params.verbose and task.context:
                lines.append(f"    Context: {json.dumps(task.context, indent=4)}")
    else:
        lines.append("\n✅ No pending tasks for you")
    
    # Overall task statistics
    lines.append(f"\n📊 Task Statistics:")
    lines.append(f"  - Total tasks: {summary['total_tasks']}")
    lines.append(f"  - Completed: {summary['completed_tasks']}")
    for agent, count in summary.get('pending_tasks_by_agent', {}).items():
        lines.append(f"  - Pending for {agent}: {count}")
    
    # Recent insights
    if summary['recent_insights']:
        lines.append(f"\n💡 Recent Insights ({summary['total_insights']} total):")
        for insight in summary['recent_insights']:
            lines.append(f"  - {insight}")
    
    # Architectural decisions
    if summary['architectural_decisions'] > 0:
        lines.append(f"\n🏗️  Architectural Decisions: {summary['architectural_decisions']}")
        if params.verbose:
            decisions = shared_manager.get_architectural_decisions()[:3]
            for decision in decisions:
                lines.append(f"  - {decision.decision}")
                lines.append(f"    Rationale: {decision.rationale}")
    
    # Active workflows
    if summary['active_workflows'] > 0:
        lines.append(f"\n🔄 Active Workflows: {summary['active_workflows']}")
    
    return "\n".join(lines)

# Workflow orchestration tools
@function_tool
async def start_feature_workflow(wrapper: RunContextWrapper[EnhancedContextData], params: StartFeatureWorkflowParams) -> str:
    """
    Start a feature implementation workflow.
    
    This creates a multi-step workflow that coordinates between Architect and Code agents
    to implement a new feature from design to completion.
    
    Args:
        feature_name: Name of the feature to implement
        requirements: Detailed requirements for the feature
        
    Returns:
        Workflow ID and confirmation message
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("start_feature_workflow params=%s", params.model_dump())
    
    # Get the workflow orchestrator from metadata
    orchestrator = wrapper.context.metadata.get("workflow_orchestrator")
    if not orchestrator:
        return "Error: Workflow orchestrator not available. Please ensure the system is properly initialized."
    
    # Create workflow
    workflow_id = orchestrator.create_workflow(
        workflow_type="feature",
        feature_name=params.feature_name,
        requirements=params.requirements
    )
    
    return f"Feature implementation workflow started successfully. Workflow ID: {workflow_id}. Check !collab or get_collaboration_status to see progress."

@function_tool
async def start_bugfix_workflow(wrapper: RunContextWrapper[EnhancedContextData], params: StartBugfixWorkflowParams) -> str:
    """
    Start a bug fix workflow.
    
    This creates a multi-step workflow that coordinates analysis and fixing of bugs
    with architectural guidance.
    
    Args:
        bug_description: Description of the bug to fix
        
    Returns:
        Workflow ID and confirmation message
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("start_bugfix_workflow params=%s", params.model_dump())
    
    # Get the workflow orchestrator from metadata
    orchestrator = wrapper.context.metadata.get("workflow_orchestrator")
    if not orchestrator:
        return "Error: Workflow orchestrator not available. Please ensure the system is properly initialized."
    
    # Create workflow
    workflow_id = orchestrator.create_workflow(
        workflow_type="bugfix",
        bug_description=params.bug_description
    )
    
    return f"Bug fix workflow started successfully. Workflow ID: {workflow_id}. Check !collab or get_collaboration_status to see progress."

@function_tool
async def start_refactor_workflow(wrapper: RunContextWrapper[EnhancedContextData], params: StartRefactorWorkflowParams) -> str:
    """
    Start a code refactoring workflow.
    
    This creates a multi-step workflow that coordinates code refactoring
    with architectural guidance and planning.
    
    Args:
        component: Component or module to refactor
        refactoring_goals: Goals and objectives for the refactoring
        
    Returns:
        Workflow ID and confirmation message
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("start_refactor_workflow params=%s", params.model_dump())
    
    # Get the workflow orchestrator from metadata
    orchestrator = wrapper.context.metadata.get("workflow_orchestrator")
    if not orchestrator:
        return "Error: Workflow orchestrator not available. Please ensure the system is properly initialized."
    
    # Create workflow
    workflow_id = orchestrator.create_workflow(
        workflow_type="refactor",
        component=params.component,
        refactoring_goals=params.refactoring_goals
    )
    
    return f"Refactoring workflow started successfully. Workflow ID: {workflow_id}. Check !collab or get_collaboration_status to see progress."

@function_tool
async def get_workflow_status(wrapper: RunContextWrapper[EnhancedContextData], params: GetWorkflowStatusParams) -> str:
    """
    Get the status of a specific workflow.
    
    Shows detailed progress including completed steps, current steps, and remaining work.
    
    Args:
        workflow_id: ID of the workflow to check
        
    Returns:
        Detailed workflow status
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("get_workflow_status params=%s", params.model_dump())
    
    # Get the workflow orchestrator from metadata
    orchestrator = wrapper.context.metadata.get("workflow_orchestrator")
    if not orchestrator:
        return "Error: Workflow orchestrator not available. Please ensure the system is properly initialized."
    
    # Get workflow status
    status = orchestrator.get_workflow_status(params.workflow_id)
    
    if "error" in status:
        return f"Error: {status['error']}"
    
    # Format status
    lines = [f"=== Workflow Status: {status['name']} ==="]
    lines.append(f"ID: {status['workflow_id']}")
    lines.append(f"Status: {status['status'].upper()}")
    lines.append(f"Progress: {status['completed_steps']}/{status['total_steps']} steps ({status['progress_percentage']:.1f}%)")
    
    if status['failed_steps'] > 0:
        lines.append(f"⚠️  Failed steps: {status['failed_steps']}")
    
    if status['running_steps'] > 0:
        lines.append(f"🔄 Running steps: {status['running_steps']}")
    
    # Show step details
    lines.append("\n📋 Steps:")
    for step in status['steps']:
        status_icon = {
            "pending": "⏸️",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌"
        }.get(step['status'], "❓")
        
        lines.append(f"  {status_icon} {step['description']} ({step['agent']})")
        if step['status'] == "running" and step['started_at']:
            runtime = time.time() - step['started_at']
            lines.append(f"    ⏱️  Running for {runtime:.1f} seconds")
    
    return "\n".join(lines)

@function_tool
async def list_active_workflows(wrapper: RunContextWrapper[EnhancedContextData]) -> str:
    """
    List all active workflows.
    
    Shows a summary of all currently running or pending workflows.
    
    Returns:
        List of active workflows with their status
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("list_active_workflows")
    
    # Get the workflow orchestrator from metadata
    orchestrator = wrapper.context.metadata.get("workflow_orchestrator")
    if not orchestrator:
        return "Error: Workflow orchestrator not available. Please ensure the system is properly initialized."
    
    # Get active workflows
    workflows = orchestrator.list_active_workflows()
    
    if not workflows:
        return "No active workflows."
    
    lines = ["=== Active Workflows ==="]
    for workflow in workflows:
        lines.append(f"\n🔄 {workflow['name']}")
        lines.append(f"   ID: {workflow['workflow_id']}")
        lines.append(f"   Status: {workflow['status'].upper()}")
        lines.append(f"   Progress: {workflow['completed_steps']}/{workflow['total_steps']} steps ({workflow['progress_percentage']:.1f}%)")
    
    return "\n".join(lines)
