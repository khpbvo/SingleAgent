"""
Workflow orchestration system for coordinating tasks between agents.

This module provides predefined workflows that leverage both the Architect
and Code agents to complete complex tasks that require multiple steps.
"""
import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger("SingleAgent.Workflows")


class WorkflowStatus(str, Enum):
    """Status of a workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep:
    """A single step in a workflow."""
    
    def __init__(self, step_id: str, agent: str, description: str, 
                 task: str, depends_on: List[str] = None):
        self.step_id = step_id
        self.agent = agent  # "architect" or "code"
        self.description = description
        self.task = task
        self.depends_on = depends_on or []
        self.status = WorkflowStatus.PENDING
        self.result: Optional[str] = None
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None


class BaseWorkflow:
    """Base class for workflows."""
    
    def __init__(self, workflow_id: str, name: str, description: str):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.status = WorkflowStatus.PENDING
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.context: Dict[str, Any] = {}
    
    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow."""
        self.steps[step.step_id] = step
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to be executed (dependencies met)."""
        ready_steps = []
        for step in self.steps.values():
            if step.status == WorkflowStatus.PENDING:
                # Check if all dependencies are completed
                deps_completed = all(
                    self.steps[dep_id].status == WorkflowStatus.COMPLETED
                    for dep_id in step.depends_on
                    if dep_id in self.steps
                )
                if deps_completed:
                    ready_steps.append(step)
        return ready_steps
    
    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        return all(
            step.status == WorkflowStatus.COMPLETED
            for step in self.steps.values()
        )
    
    def has_failed_steps(self) -> bool:
        """Check if any steps have failed."""
        return any(
            step.status == WorkflowStatus.FAILED
            for step in self.steps.values()
        )
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get workflow progress summary."""
        total_steps = len(self.steps)
        completed_steps = sum(1 for s in self.steps.values() if s.status == WorkflowStatus.COMPLETED)
        failed_steps = sum(1 for s in self.steps.values() if s.status == WorkflowStatus.FAILED)
        running_steps = sum(1 for s in self.steps.values() if s.status == WorkflowStatus.RUNNING)
        
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "running_steps": running_steps,
            "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


class FeatureImplementationWorkflow(BaseWorkflow):
    """
    Architecture-first workflow for implementing a new feature.
    
    Steps:
    1. Architect analyzes requirements and creates design
    2. Architect creates implementation plan and tasks
    3. Code agent implements core functionality
    4. Code agent writes tests
    5. Architect reviews implementation
    6. Code agent addresses review feedback
    """
    
    def __init__(self, workflow_id: str, feature_name: str, requirements: str):
        super().__init__(
            workflow_id=workflow_id,
            name=f"Feature Implementation: {feature_name}",
            description=f"End-to-end implementation of {feature_name}"
        )
        
        self.context = {
            "feature_name": feature_name,
            "requirements": requirements
        }
        
        # Define workflow steps
        self.add_step(WorkflowStep(
            step_id="design",
            agent="architect",
            description="Analyze requirements and create design",
            task=f"Analyze the requirements for {feature_name} and create a detailed design: {requirements}"
        ))
        
        self.add_step(WorkflowStep(
            step_id="plan",
            agent="architect",
            description="Create implementation plan",
            task=f"Create a detailed implementation plan for {feature_name} including tasks for the code agent",
            depends_on=["design"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="implement_core",
            agent="code",
            description="Implement core functionality",
            task=f"Implement the core functionality for {feature_name} based on the architectural design",
            depends_on=["plan"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="write_tests",
            agent="code",
            description="Write comprehensive tests",
            task=f"Write comprehensive tests for the {feature_name} implementation",
            depends_on=["implement_core"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="review",
            agent="architect",
            description="Review implementation",
            task=f"Review the implementation of {feature_name} and provide feedback",
            depends_on=["write_tests"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="address_feedback",
            agent="code",
            description="Address review feedback",
            task=f"Address any feedback from the architecture review of {feature_name}",
            depends_on=["review"]
        ))


class BugFixWorkflow(BaseWorkflow):
    """
    Workflow for fixing bugs with architectural analysis.
    
    Steps:
    1. Code agent reproduces and analyzes the bug
    2. Architect analyzes root cause and suggests approach
    3. Code agent implements the fix
    4. Code agent tests the fix
    5. Architect validates the approach
    """
    
    def __init__(self, workflow_id: str, bug_description: str):
        super().__init__(
            workflow_id=workflow_id,
            name=f"Bug Fix: {bug_description[:50]}...",
            description=f"Fix bug: {bug_description}"
        )
        
        self.context = {
            "bug_description": bug_description
        }
        
        self.add_step(WorkflowStep(
            step_id="analyze_bug",
            agent="code",
            description="Reproduce and analyze the bug",
            task=f"Reproduce and analyze this bug: {bug_description}"
        ))
        
        self.add_step(WorkflowStep(
            step_id="root_cause",
            agent="architect",
            description="Analyze root cause",
            task=f"Analyze the root cause of this bug and suggest the best approach for fixing it: {bug_description}",
            depends_on=["analyze_bug"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="implement_fix",
            agent="code",
            description="Implement the bug fix",
            task=f"Implement the bug fix based on the architectural analysis",
            depends_on=["root_cause"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="test_fix",
            agent="code",
            description="Test the fix",
            task=f"Test the bug fix to ensure it works correctly and doesn't introduce regressions",
            depends_on=["implement_fix"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="validate_approach",
            agent="architect",
            description="Validate the fix approach",
            task=f"Validate that the bug fix follows good architectural principles",
            depends_on=["test_fix"]
        ))


class CodeRefactoringWorkflow(BaseWorkflow):
    """
    Workflow for refactoring code with architectural guidance.
    
    Steps:
    1. Architect analyzes current code structure
    2. Architect designs refactoring plan
    3. Code agent implements refactoring in phases
    4. Code agent updates tests
    5. Architect reviews final structure
    """
    
    def __init__(self, workflow_id: str, component: str, refactoring_goals: str):
        super().__init__(
            workflow_id=workflow_id,
            name=f"Refactoring: {component}",
            description=f"Refactor {component}: {refactoring_goals}"
        )
        
        self.context = {
            "component": component,
            "refactoring_goals": refactoring_goals
        }
        
        self.add_step(WorkflowStep(
            step_id="analyze_structure",
            agent="architect",
            description="Analyze current code structure",
            task=f"Analyze the current structure of {component} and identify refactoring opportunities"
        ))
        
        self.add_step(WorkflowStep(
            step_id="design_refactoring",
            agent="architect",
            description="Design refactoring plan",
            task=f"Design a detailed refactoring plan for {component} with goals: {refactoring_goals}",
            depends_on=["analyze_structure"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="refactor_phase1",
            agent="code",
            description="Implement refactoring (Phase 1)",
            task=f"Implement the first phase of refactoring for {component}",
            depends_on=["design_refactoring"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="refactor_phase2",
            agent="code",
            description="Implement refactoring (Phase 2)",
            task=f"Implement the second phase of refactoring for {component}",
            depends_on=["refactor_phase1"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="update_tests",
            agent="code",
            description="Update tests for refactored code",
            task=f"Update and enhance tests for the refactored {component}",
            depends_on=["refactor_phase2"]
        ))
        
        self.add_step(WorkflowStep(
            step_id="review_structure",
            agent="architect",
            description="Review final structure",
            task=f"Review the final refactored structure of {component}",
            depends_on=["update_tests"]
        ))


class WorkflowOrchestrator:
    """Orchestrates workflow execution."""
    
    def __init__(self, shared_manager):
        self.shared_manager = shared_manager
        self.active_workflows: Dict[str, BaseWorkflow] = {}
        self.workflow_counter = 0
    
    def create_workflow(self, workflow_type: str, **kwargs) -> str:
        """Create a new workflow of the specified type."""
        self.workflow_counter += 1
        workflow_id = f"workflow_{self.workflow_counter}_{int(time.time())}"
        
        if workflow_type == "feature":
            workflow = FeatureImplementationWorkflow(
                workflow_id=workflow_id,
                feature_name=kwargs.get("feature_name", "New Feature"),
                requirements=kwargs.get("requirements", "")
            )
        elif workflow_type == "bugfix":
            workflow = BugFixWorkflow(
                workflow_id=workflow_id,
                bug_description=kwargs.get("bug_description", "")
            )
        elif workflow_type == "refactor":
            workflow = CodeRefactoringWorkflow(
                workflow_id=workflow_id,
                component=kwargs.get("component", "Component"),
                refactoring_goals=kwargs.get("refactoring_goals", "")
            )
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        self.active_workflows[workflow_id] = workflow
        
        # Start the workflow by creating tasks for ready steps
        self._process_workflow(workflow)
        
        logger.info(f"Created {workflow_type} workflow: {workflow_id}")
        return workflow_id
    
    def _process_workflow(self, workflow: BaseWorkflow):
        """Process a workflow by creating tasks for ready steps."""
        ready_steps = workflow.get_ready_steps()
        
        for step in ready_steps:
            # Create task in shared context manager
            task_id = self.shared_manager.add_task(
                target_agent=step.agent,
                task=step.task,
                created_by="workflow_orchestrator",
                priority="medium",
                context={
                    "workflow_id": workflow.workflow_id,
                    "step_id": step.step_id,
                    "workflow_context": workflow.context
                }
            )
            
            step.status = WorkflowStatus.RUNNING
            step.started_at = time.time()
            
            logger.info(f"Created task {task_id} for workflow {workflow.workflow_id} step {step.step_id}")
    
    def update_workflow_progress(self, workflow_id: str, step_id: str, 
                                status: WorkflowStatus, result: str = None):
        """Update the progress of a workflow step."""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        if step_id not in workflow.steps:
            return False
        
        step = workflow.steps[step_id]
        step.status = status
        step.result = result
        
        if status == WorkflowStatus.COMPLETED:
            step.completed_at = time.time()
            
            # Check if workflow is complete
            if workflow.is_complete():
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = time.time()
                logger.info(f"Workflow {workflow_id} completed")
            else:
                # Process next ready steps
                self._process_workflow(workflow)
        
        elif status == WorkflowStatus.FAILED:
            workflow.status = WorkflowStatus.FAILED
            logger.error(f"Workflow {workflow_id} failed at step {step_id}")
        
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.active_workflows[workflow_id]
        status = workflow.get_progress_summary()
        
        # Add step details
        status["steps"] = []
        for step in workflow.steps.values():
            status["steps"].append({
                "step_id": step.step_id,
                "agent": step.agent,
                "description": step.description,
                "status": step.status,
                "started_at": step.started_at,
                "completed_at": step.completed_at
            })
        
        return status
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows."""
        return [
            workflow.get_progress_summary()
            for workflow in self.active_workflows.values()
            if workflow.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]
        ]