"""
Shared Context Manager for cross-agent communication and collaboration.

This module provides a centralized system for agents to share insights,
delegate tasks, and coordinate their work.
"""
import time
import json
import os
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import logging

# Configure logger
logger = logging.getLogger("SingleAgent.SharedContext")
logger.setLevel(logging.DEBUG)

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

# Add a handler for the shared context logger
handler = logging.FileHandler('logs/shared_context.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)


class TaskPriority(str, Enum):
    """Priority levels for tasks."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """Status of tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AgentTask(BaseModel):
    """A task that can be assigned to an agent."""
    id: str = Field(description="Unique task identifier")
    target_agent: str = Field(description="Target agent (architect/code)")
    task: str = Field(description="Task description")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_by: str = Field(description="Agent that created the task")
    created_at: float = Field(default_factory=time.time)
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the task")
    result: Optional[str] = Field(None, description="Result when task is completed")


class SharedInsight(BaseModel):
    """An insight shared between agents."""
    id: str = Field(description="Unique insight identifier")
    agent: str = Field(description="Agent that created the insight")
    insight: str = Field(description="The insight content")
    category: str = Field(description="Category (architecture, implementation, bug, etc.)")
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    related_files: List[str] = Field(default_factory=list)


class ArchitecturalDecision(BaseModel):
    """An architectural decision made by the architect agent."""
    id: str = Field(description="Unique decision identifier")
    decision: str = Field(description="The decision description")
    rationale: str = Field(description="Why this decision was made")
    timestamp: float = Field(default_factory=time.time)
    affected_components: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)


class SharedContextManager:
    """
    Manages shared context between architect and code agents.
    
    Features:
    - Task delegation and tracking
    - Shared insights and discoveries
    - Architectural decisions log
    - Cross-agent communication
    - Workflow coordination
    """
    
    def __init__(self, persistence_path: Optional[str] = None):
        """
        Initialize the shared context manager.
        
        Args:
            persistence_path: Optional path to persist shared context
        """
        self.tasks: Dict[str, AgentTask] = {}
        self.insights: Dict[str, SharedInsight] = {}
        self.architectural_decisions: Dict[str, ArchitecturalDecision] = {}
        self.active_workflows: List[Dict[str, Any]] = []
        self.persistence_path = persistence_path or "shared_context.json"
        self._task_counter = 0
        self._insight_counter = 0
        self._decision_counter = 0

        # Track dirty state for autosaving
        self._dirty = False
        self._last_dirty_ts = 0.0

        # Load existing data if available
        self.load_from_disk()

        # Start background autosave task if an event loop is running
        try:
            loop = asyncio.get_running_loop()
            self._autosave_task = loop.create_task(self._autosave_loop())
        except RuntimeError:
            self._autosave_task = None
            logger.warning("No running event loop; autosave disabled")

    def _mark_dirty(self) -> None:
        """Mark the context as needing persistence."""
        self._dirty = True
        self._last_dirty_ts = time.time()

    async def _autosave_loop(self) -> None:
        """Background task that periodically saves state when dirty."""
        while True:
            await asyncio.sleep(1)
            if self._dirty:
                self.save_to_disk()
                self._dirty = False
    
    def _get_next_task_id(self) -> str:
        """Generate unique task ID."""
        self._task_counter += 1
        return f"task_{self._task_counter}_{int(time.time())}"
    
    def _get_next_insight_id(self) -> str:
        """Generate unique insight ID."""
        self._insight_counter += 1
        return f"insight_{self._insight_counter}_{int(time.time())}"
    
    def _get_next_decision_id(self) -> str:
        """Generate unique decision ID."""
        self._decision_counter += 1
        return f"decision_{self._decision_counter}_{int(time.time())}"
    
    # Task Management
    def add_task(self, target_agent: str, task: str, created_by: str, 
                 priority: TaskPriority = TaskPriority.MEDIUM, 
                 context: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a task for another agent.
        
        Args:
            target_agent: Target agent name
            task: Task description
            created_by: Agent creating the task
            priority: Task priority
            context: Additional context
            
        Returns:
            Task ID
        """
        task_id = self._get_next_task_id()
        agent_task = AgentTask(
            id=task_id,
            target_agent=target_agent,
            task=task,
            priority=priority,
            created_by=created_by,
            context=context or {}
        )
        self.tasks[task_id] = agent_task
        logger.info(f"Task {task_id} created by {created_by} for {target_agent}: {task}")
        self._mark_dirty()
        return task_id
    
    def get_pending_tasks(self, agent_name: str) -> List[AgentTask]:
        """
        Get pending tasks for a specific agent.
        
        Args:
            agent_name: Agent name
            
        Returns:
            List of pending tasks
        """
        return [
            task for task in self.tasks.values()
            if task.target_agent == agent_name and task.status == TaskStatus.PENDING
        ]
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Optional[str] = None) -> bool:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status
            result: Optional result for completed tasks
            
        Returns:
            True if successful
        """
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            if result:
                self.tasks[task_id].result = result
            logger.info(f"Task {task_id} status updated to {status}")
            self._mark_dirty()
            return True
        return False
    
    # Insight Management
    def add_insight(self, agent: str, insight: str, category: str,
                    metadata: Optional[Dict[str, Any]] = None,
                    related_files: Optional[List[str]] = None) -> str:
        """
        Add a shared insight.
        
        Args:
            agent: Agent that discovered the insight
            insight: Insight description
            category: Category (architecture, bug, optimization, etc.)
            metadata: Additional metadata
            related_files: Related file paths
            
        Returns:
            Insight ID
        """
        insight_id = self._get_next_insight_id()
        shared_insight = SharedInsight(
            id=insight_id,
            agent=agent,
            insight=insight,
            category=category,
            metadata=metadata or {},
            related_files=related_files or []
        )
        self.insights[insight_id] = shared_insight
        logger.info(f"Insight {insight_id} added by {agent}: {insight[:50]}...")
        self._mark_dirty()
        return insight_id
    
    def get_insights_by_category(self, category: str) -> List[SharedInsight]:
        """Get insights by category."""
        return [
            insight for insight in self.insights.values()
            if insight.category == category
        ]
    
    def get_recent_insights(self, limit: int = 5) -> List[SharedInsight]:
        """Get most recent insights."""
        sorted_insights = sorted(
            self.insights.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_insights[:limit]
    
    # Architectural Decision Management
    def add_architectural_decision(self, decision: str, rationale: str,
                                   affected_components: Optional[List[str]] = None,
                                   constraints: Optional[List[str]] = None) -> str:
        """
        Record an architectural decision.
        
        Args:
            decision: Decision description
            rationale: Why this decision was made
            affected_components: Components affected
            constraints: Constraints considered
            
        Returns:
            Decision ID
        """
        decision_id = self._get_next_decision_id()
        arch_decision = ArchitecturalDecision(
            id=decision_id,
            decision=decision,
            rationale=rationale,
            affected_components=affected_components or [],
            constraints=constraints or []
        )
        self.architectural_decisions[decision_id] = arch_decision
        logger.info(f"Architectural decision {decision_id} recorded: {decision[:50]}...")
        self._mark_dirty()
        return decision_id
    
    def get_architectural_decisions(self) -> List[ArchitecturalDecision]:
        """Get all architectural decisions."""
        return sorted(
            self.architectural_decisions.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )
    
    # Workflow Management
    def start_workflow(self, workflow_type: str, description: str, context: Dict[str, Any]) -> str:
        """
        Start a new workflow.
        
        Args:
            workflow_type: Type of workflow
            description: Workflow description
            context: Workflow context
            
        Returns:
            Workflow ID
        """
        workflow_id = f"workflow_{len(self.active_workflows)}_{int(time.time())}"
        workflow = {
            "id": workflow_id,
            "type": workflow_type,
            "description": description,
            "context": context,
            "status": "active",
            "started_at": time.time(),
            "tasks": []
        } 
        self.active_workflows.append(workflow)
        logger.info(f"Started workflow {workflow_id}: {workflow_type}")
        self._mark_dirty()
        return workflow_id
    
    def add_task_to_workflow(self, workflow_id: str, task_id: str) -> bool:
        """Add a task to a workflow."""
        for workflow in self.active_workflows:
            if workflow["id"] == workflow_id:
                workflow["tasks"].append(task_id)
                self._mark_dirty()
                return True
        return False
    
    # Summary Methods
    def get_collaboration_summary(self) -> Dict[str, Any]:
        """Get a summary of current collaboration state."""
        pending_tasks_by_agent = {}
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                if task.target_agent not in pending_tasks_by_agent:
                    pending_tasks_by_agent[task.target_agent] = 0
                pending_tasks_by_agent[task.target_agent] += 1
        
        return {
            "total_tasks": len(self.tasks),
            "pending_tasks_by_agent": pending_tasks_by_agent,
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "total_insights": len(self.insights),
            "recent_insights": [i.insight[:50] + "..." for i in self.get_recent_insights(3)],
            "architectural_decisions": len(self.architectural_decisions),
            "active_workflows": len([w for w in self.active_workflows if w["status"] == "active"])
        }
    
    def get_agent_handoff_context(self, from_agent: str, to_agent: str) -> Dict[str, Any]:
        """
        Get context for handing off between agents.
        
        Args:
            from_agent: Agent handing off
            to_agent: Agent receiving handoff
            
        Returns:
            Handoff context
        """
        # Get pending tasks for the target agent
        pending_tasks = self.get_pending_tasks(to_agent)
        
        # Get recent insights from the source agent
        recent_insights = [
            i for i in self.insights.values()
            if i.agent == from_agent
        ][-5:]
        
        # Get recent architectural decisions
        recent_decisions = list(self.architectural_decisions.values())[-3:]
        
        return {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "pending_tasks": [{"id": t.id, "task": t.task, "priority": t.priority} for t in pending_tasks],
            "recent_insights": [{"insight": i.insight, "category": i.category} for i in recent_insights],
            "architectural_decisions": [{"decision": d.decision, "rationale": d.rationale} for d in recent_decisions],
            "timestamp": time.time()
        }
    
    # Persistence
    def save_to_disk(self) -> None:
        """Save shared context to disk."""
        data = {
            "tasks": {k: v.model_dump() for k, v in self.tasks.items()},
            "insights": {k: v.model_dump() for k, v in self.insights.items()},
            "architectural_decisions": {k: v.model_dump() for k, v in self.architectural_decisions.items()},
            "active_workflows": self.active_workflows,
            "counters": {
                "task": self._task_counter,
                "insight": self._insight_counter,
                "decision": self._decision_counter
            }
        }
        
        with open(self.persistence_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.debug(f"Saved shared context to {self.persistence_path}")
    
    def load_from_disk(self) -> None:
        """Load shared context from disk."""
        if not os.path.exists(self.persistence_path):
            logger.info("No existing shared context found, starting fresh")
            return
        
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)
            
            # Load tasks
            self.tasks = {
                k: AgentTask(**v) for k, v in data.get("tasks", {}).items()
            }
            
            # Load insights
            self.insights = {
                k: SharedInsight(**v) for k, v in data.get("insights", {}).items()
            }
            
            # Load architectural decisions
            self.architectural_decisions = {
                k: ArchitecturalDecision(**v) for k, v in data.get("architectural_decisions", {}).items()
            }
            
            # Load workflows
            self.active_workflows = data.get("active_workflows", [])
            
            # Load counters
            counters = data.get("counters", {})
            self._task_counter = counters.get("task", 0)
            self._insight_counter = counters.get("insight", 0)
            self._decision_counter = counters.get("decision", 0)
            
            logger.info(f"Loaded shared context from {self.persistence_path}")
            logger.info(f"Loaded {len(self.tasks)} tasks, {len(self.insights)} insights, "
                       f"{len(self.architectural_decisions)} decisions")
        except Exception as e:
            logger.error(f"Error loading shared context: {e}")