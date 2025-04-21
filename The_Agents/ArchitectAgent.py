"""
ArchitectAgent.py
Advanced architectural design agent for code projects.
Creates comprehensive system designs and task breakdowns for SingleAgent to execute.
"""

import os
import asyncio
import json
import logging
from typing import List, Dict, Optional, Any, Union, Tuple, Set
from pydantic import BaseModel, Field
from datetime import datetime

# Import OpenAI Agents SDK components
from agents import (
    Agent,
    RunContextWrapper,
    function_tool,
    Runner,
    handoff,
    ItemHelpers
)

# For context compatibility with SingleAgent
from The_Agents.context_data import EnhancedContextData

# Logging setup
logger = logging.getLogger("ArchitectAgent")
logger.setLevel(logging.DEBUG)
os.makedirs("logs", exist_ok=True)
handler = logging.FileHandler('logs/architect_agent.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.propagate = False

# Models for tool parameters (Pydantic v2 compatible - no default values)
class DesignRequirementParams(BaseModel):
    """Parameters for design requirement analysis."""
    project_description: str = Field(description="Description of the project or feature")
    constraints: List[str] = Field(description="List of constraints or requirements")

class SystemDiagramParams(BaseModel):
    """Parameters for system diagram generation."""
    components: List[str] = Field(description="Components to include in the diagram")
    diagram_type: str = Field(description="Type of diagram to generate (e.g., 'class', 'sequence', 'component')")

class TaskBreakdownParams(BaseModel):
    """Parameters for task breakdown."""
    design_doc: str = Field(description="Design document to break down into tasks")
    priority_level: str = Field(description="Priority level for task sorting")

class ArchitecturalAnalysisParams(BaseModel):
    """Parameters for architectural analysis."""
    code_path: str = Field(description="Path to code file or directory to analyze")
    analysis_depth: str = Field(description="Depth of analysis ('basic', 'detailed', 'comprehensive')")

class DesignPatternParams(BaseModel):
    """Parameters for design pattern recommendation."""
    problem_statement: str = Field(description="Statement of the problem to solve")
    current_architecture: str = Field(description="Description of current architecture if any")

class SaveDesignParams(BaseModel):
    """Parameters for saving design documents."""
    design_content: str = Field(description="Content of the design document")
    design_type: str = Field(description="Type of design document")
    filename: str = Field(description="Filename to save the design document as")

class ProjectStructureParams(BaseModel):
    """Parameters for recommending project structure."""
    project_type: str = Field(description="Type of project (e.g., 'web', 'cli', 'api', 'data')")
    technologies: List[str] = Field(description="List of technologies to be used")
    complexity: str = Field(description="Complexity level ('simple', 'medium', 'complex')")

class TaskItem(BaseModel):
    """Model for a task item in a todo list."""
    id: str = Field(description="Unique identifier for the task")
    title: str = Field(description="Short title for the task")
    description: str = Field(description="Detailed description of the task")
    priority: str = Field(description="Priority level ('high', 'medium', 'low')")
    estimated_time: str = Field(description="Estimated time to complete")
    dependencies: List[str] = Field(description="List of task IDs this task depends on")
    tags: List[str] = Field(description="List of tags for categorization")

class TodoList(BaseModel):
    """Model for a complete todo list."""
    project_name: str = Field(description="Name of the project")
    created_at: str = Field(description="Creation timestamp")
    tasks: List[TaskItem] = Field(description="List of tasks")

class DiagramResult(BaseModel):
    """Result of a diagram generation."""
    mermaid_content: str = Field(description="Mermaid diagram content")
    description: str = Field(description="Description of the diagram")
    components: List[str] = Field(description="Components in the diagram")

# Tool implementations
@function_tool
async def analyze_requirements(wrapper: RunContextWrapper[EnhancedContextData], params: DesignRequirementParams) -> Dict[str, Any]:
    """
    Analyze project requirements and extract key architectural considerations.
    
    Args:
        project_description: Description of the project or feature
        constraints: List of constraints or requirements
        
    Returns:
        A structured analysis of requirements including architectural implications
    """
    logger.info(f"Analyzing requirements for project: {params.project_description[:50]}...")
    
    # Log the analysis to context
    wrapper.context.track_entity(
        entity_type="design",
        value=f"Requirements analysis for: {params.project_description[:30]}...",
        metadata={"constraints": params.constraints}
    )
    
    # Return structured analysis
    return {
        "functional_requirements": [
            "Extracted from description - would contain actual requirements in real usage"
        ],
        "non_functional_requirements": [
            "Performance considerations",
            "Scalability considerations",
            "Security considerations"
        ],
        "architectural_implications": [
            "Key architectural decisions needed",
            "Critical components identified"
        ],
        "recommended_approach": "Initial recommendation based on requirements"
    }

@function_tool
async def create_system_diagram(wrapper: RunContextWrapper[EnhancedContextData], params: SystemDiagramParams) -> DiagramResult:
    """
    Create a system architecture diagram using Mermaid syntax.
    
    Args:
        components: Components to include in the diagram
        diagram_type: Type of diagram to generate (class, sequence, component, etc.)
        
    Returns:
        Mermaid diagram content, description, and component list
    """
    logger.info(f"Creating {params.diagram_type} diagram with {len(params.components)} components")
    
    mermaid_content = ""
    
    # Generate different diagram types based on request
    if params.diagram_type == "class":
        mermaid_content = "classDiagram\n"
        # Add classes and relationships
        for i, component in enumerate(params.components):
            mermaid_content += f"    class {component} {{\n        +methods()\n        -attributes\n    }}\n"
            
        # Add some relationships between components
        if len(params.components) > 1:
            mermaid_content += f"    {params.components[0]} <|-- {params.components[1]}: inherits\n"
            
    elif params.diagram_type == "sequence":
        mermaid_content = "sequenceDiagram\n"
        # Add sequence interactions
        for i in range(len(params.components) - 1):
            mermaid_content += f"    {params.components[i]}->>+{params.components[i+1]}: request()\n"
            mermaid_content += f"    {params.components[i+1]}-->>-{params.components[i]}: response()\n"
            
    elif params.diagram_type == "component":
        mermaid_content = "flowchart LR\n"
        # Add components and connections
        for i, component in enumerate(params.components):
            mermaid_content += f"    C{i}[{component}]\n"
            
        # Add connections between components
        for i in range(len(params.components) - 1):
            mermaid_content += f"    C{i} --> C{i+1}\n"
    
    # Log diagram to context
    wrapper.context.track_entity(
        entity_type="diagram",
        value=f"{params.diagram_type} diagram",
        metadata={"components": params.components, "preview": mermaid_content[:100]}
    )
    
    return DiagramResult(
        mermaid_content=mermaid_content,
        description=f"System {params.diagram_type} diagram showing relationships between {len(params.components)} components",
        components=params.components
    )

@function_tool
async def create_task_breakdown(wrapper: RunContextWrapper[EnhancedContextData], params: TaskBreakdownParams) -> TodoList:
    """
    Break down a design document into actionable tasks.
    
    Args:
        design_doc: Design document to break down into tasks
        priority_level: Priority level for task sorting (high, medium, low)
        
    Returns:
        Structured todo list with detailed tasks
    """
    logger.info(f"Creating task breakdown for design document (priority: {params.priority_level})")
    
    # Generate a sample todo list (in real usage, this would parse the design_doc)
    tasks = [
        TaskItem(
            id=f"TASK-{i+1}",
            title=f"Implement component {i+1}",
            description=f"Detailed description for task {i+1} implementation steps",
            priority=params.priority_level if i < 3 else "medium",
            estimated_time=f"{(i+1)*2}h",
            dependencies=[f"TASK-{i}" if i > 0 else ""],
            tags=["implementation", f"component-{i+1}"]
        )
        for i in range(5)  # Generate 5 sample tasks
    ]
    
    # Clean up empty dependencies
    for task in tasks:
        task.dependencies = [d for d in task.dependencies if d]
    
    todo_list = TodoList(
        project_name="Architecture Implementation",
        created_at=datetime.now().isoformat(),
        tasks=tasks
    )
    
    # Save the todo list to context
    wrapper.context.track_entity(
        entity_type="todo_list",
        value="Architecture implementation tasks",
        metadata={"task_count": len(tasks), "priority": params.priority_level}
    )
    
    # Set active task in context
    wrapper.context.set_state("active_todo_list", json.dumps(todo_list.model_dump()))
    
    return todo_list

@function_tool
async def analyze_codebase(wrapper: RunContextWrapper[EnhancedContextData], params: ArchitecturalAnalysisParams) -> Dict[str, Any]:
    """
    Analyze existing codebase for architectural patterns, dependencies, and structure.
    
    Args:
        code_path: Path to code file or directory to analyze
        analysis_depth: Depth of analysis ('basic', 'detailed', 'comprehensive')
        
    Returns:
        Analysis results including patterns, dependencies, and recommendations
    """
    logger.info(f"Analyzing codebase at {params.code_path} (depth: {params.analysis_depth})")
    
    try:
        # Check if file or directory exists
        if not os.path.exists(params.code_path):
            return {"error": f"Path {params.code_path} does not exist"}
        
        files_analyzed = []
        total_loc = 0
        
        # Basic file stats collection
        if os.path.isdir(params.code_path):
            for root, dirs, files in os.walk(params.code_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                loc = len(content.splitlines())
                                total_loc += loc
                                files_analyzed.append({
                                    "path": file_path,
                                    "loc": loc
                                })
                        except Exception as e:
                            logger.error(f"Error reading file {file_path}: {str(e)}")
        else:
            # Single file analysis
            try:
                with open(params.code_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    loc = len(content.splitlines())
                    total_loc += loc
                    files_analyzed.append({
                        "path": params.code_path,
                        "loc": loc
                    })
            except Exception as e:
                logger.error(f"Error reading file {params.code_path}: {str(e)}")
        
        # Save to context
        wrapper.context.track_entity(
            entity_type="code_analysis",
            value=f"Analysis of {params.code_path}",
            metadata={"files": len(files_analyzed), "loc": total_loc}
        )
        
        return {
            "files_analyzed": len(files_analyzed),
            "total_loc": total_loc,
            "top_files": sorted(files_analyzed, key=lambda x: x["loc"], reverse=True)[:5],
            "identified_patterns": [
                "Potential factory pattern in file X",
                "Observer pattern in module Y"
            ],
            "architecture_summary": "The codebase appears to follow a layered architecture with clear separation of concerns",
            "improvement_suggestions": [
                "Consider introducing dependency injection",
                "Refactor large modules X and Y for better maintainability"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in code analysis: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}

@function_tool
async def recommend_design_patterns(wrapper: RunContextWrapper[EnhancedContextData], params: DesignPatternParams) -> Dict[str, Any]:
    """
    Recommend appropriate design patterns based on problem statement.
    
    Args:
        problem_statement: Statement of the problem to solve
        current_architecture: Description of current architecture if any
        
    Returns:
        Recommended design patterns with explanations and implementation details
    """
    logger.info(f"Recommending design patterns for problem: {params.problem_statement[:50]}...")
    
    # In a real implementation, this would analyze the problem and recommend patterns
    # For now, we'll provide sample recommendations
    
    recommended_patterns = [
        {
            "name": "Factory Method",
            "applicability": "High",
            "benefits": [
                "Decouples object creation from usage",
                "Supports adding new types without modifying existing code"
            ],
            "implementation_notes": "Implement a factory class with a method that returns different object types based on parameters",
            "code_example": "class Factory:\n    def create_object(self, type):\n        if type == 'A':\n            return ObjectA()\n        elif type == 'B':\n            return ObjectB()"
        },
        {
            "name": "Strategy",
            "applicability": "Medium",
            "benefits": [
                "Encapsulates algorithms",
                "Makes algorithms interchangeable"
            ],
            "implementation_notes": "Define a strategy interface and implement concrete strategies",
            "code_example": "class Strategy:\n    def execute(self, data):\n        pass\n\nclass ConcreteStrategy(Strategy):\n    def execute(self, data):\n        # Implementation"
        }
    ]
    
    # Save recommendation to context
    wrapper.context.track_entity(
        entity_type="design_pattern",
        value=f"Pattern recommendations for: {params.problem_statement[:30]}...",
        metadata={"patterns": [p["name"] for p in recommended_patterns]}
    )
    
    return {
        "problem_analysis": "Analysis of the key aspects of the problem that influence design choices",
        "recommended_patterns": recommended_patterns,
        "implementation_strategy": "Suggested approach to implementing these patterns in the current context"
    }

@function_tool
async def save_design_document(wrapper: RunContextWrapper[EnhancedContextData], params: SaveDesignParams) -> Dict[str, Any]:
    """
    Save a design document to a file.
    
    Args:
        design_content: Content of the design document
        design_type: Type of design document
        filename: Filename to save the design document as
        
    Returns:
        Status of the save operation and file path
    """
    logger.info(f"Saving {params.design_type} design document to {params.filename}")
    
    try:
        # Ensure the design document has a markdown extension
        if not params.filename.endswith(('.md', '.markdown')):
            params.filename = f"{params.filename}.md"
        
        # Create designs directory if it doesn't exist
        os.makedirs("designs", exist_ok=True)
        
        file_path = os.path.join("designs", params.filename)
        
        # Add header with metadata
        header = f"""# {params.design_type.title()} Design Document
Generated by ArchitectAgent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        full_content = header + params.design_content
        
        # Write the content to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # Save to context
        wrapper.context.track_entity(
            entity_type="design_document",
            value=params.filename,
            metadata={"type": params.design_type, "path": file_path}
        )
        
        return {
            "status": "success",
            "file_path": file_path,
            "message": f"Design document saved successfully to {file_path}"
        }
        
    except Exception as e:
        logger.error(f"Error saving design document: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to save design document: {str(e)}"
        }

@function_tool
async def recommend_project_structure(wrapper: RunContextWrapper[EnhancedContextData], params: ProjectStructureParams) -> Dict[str, Any]:
    """
    Recommend project structure based on project type and technologies.
    
    Args:
        project_type: Type of project (web, cli, api, data, etc.)
        technologies: List of technologies to be used
        complexity: Complexity level (simple, medium, complex)
        
    Returns:
        Recommended project structure with explanations
    """
    logger.info(f"Recommending project structure for {params.project_type} project with complexity {params.complexity}")
    
    # Create basic structure based on project type
    structure = {
        "directories": [],
        "files": [],
        "explanation": "",
        "best_practices": []
    }
    
    # Base directories for all projects
    base_dirs = ["docs", "tests"]
    structure["directories"].extend(base_dirs)
    
    # Project-specific structure
    if params.project_type == "web":
        structure["directories"].extend([
            "app/static/css",
            "app/static/js",
            "app/templates",
            "app/models",
            "app/views",
            "app/controllers"
        ])
        structure["files"].extend([
            "app/__init__.py",
            "app/config.py",
            "app/main.py",
            "requirements.txt"
        ])
        structure["explanation"] = "This structure follows the MVC pattern which is ideal for web applications."
        
    elif params.project_type == "cli":
        structure["directories"].extend([
            "src/commands",
            "src/utils",
            "config"
        ])
        structure["files"].extend([
            "src/__init__.py",
            "src/cli.py",
            "src/config.py",
            "requirements.txt"
        ])
        structure["explanation"] = "This structure separates commands from utilities, making the CLI maintainable."
        
    elif params.project_type == "api":
        structure["directories"].extend([
            "api/endpoints",
            "api/models",
            "api/middleware",
            "api/services",
            "api/utils"
        ])
        structure["files"].extend([
            "api/__init__.py",
            "api/main.py",
            "api/config.py",
            "requirements.txt"
        ])
        structure["explanation"] = "This structure follows a layered architecture suitable for APIs."
        
    elif params.project_type == "data":
        structure["directories"].extend([
            "data/raw",
            "data/processed",
            "notebooks",
            "src/etl",
            "src/models",
            "src/visualization"
        ])
        structure["files"].extend([
            "src/__init__.py",
            "src/config.py",
            "requirements.txt"
        ])
        structure["explanation"] = "This structure separates data processing, modeling, and visualization."
    
    # Add complexity-based components
    if params.complexity in ["medium", "complex"]:
        structure["directories"].extend(["ci", "deployment"])
        structure["files"].extend(["Dockerfile", ".github/workflows/ci.yml"])
        
    if params.complexity == "complex":
        structure["directories"].extend(["monitoring", "microservices"])
        
    # Add best practices
    structure["best_practices"] = [
        "Use virtual environments for Python projects",
        "Include a comprehensive README.md file",
        "Implement consistent error handling",
        "Add proper logging throughout the application",
        "Implement configuration management",
        "Write tests for critical functionality"
    ]
    
    # Save to context
    wrapper.context.track_entity(
        entity_type="project_structure",
        value=f"{params.project_type} structure ({params.complexity})",
        metadata={"technologies": params.technologies}
    )
    
    return structure

# Create the actual Architect Agent
class ArchitectAgent:
    """
    Architecture design agent that creates system designs and task breakdowns.
    Integrates with SingleAgent to provide architectural guidance.
    """
    
    def __init__(self):
        """Initialize the architecture design agent with all required tools."""
        # Create the enhanced agent with architectural design tools
        self.agent = Agent[EnhancedContextData](
            name="ArchitectAgent",
            model="gpt-4.1",
            instructions=self._get_agent_instructions(),
            tools=[
                analyze_requirements,
                create_system_diagram,
                create_task_breakdown,
                analyze_codebase,
                recommend_design_patterns,
                save_design_document,
                recommend_project_structure
            ]
        )
        
        logger.info("ArchitectAgent initialized successfully")
        
    def _get_agent_instructions(self) -> str:
        """Get the detailed instructions for the architect agent."""
        return """
You are an expert software architect specializing in designing robust, scalable, and maintainable systems.
Your primary responsibility is to create comprehensive system designs and break down tasks into executable
steps that can be implemented by development teams.

# Key Responsibilities
1. Analyze requirements to extract architectural implications
2. Create system architecture diagrams (class, sequence, component)
3. Recommend appropriate design patterns for specific problems
4. Break down designs into actionable tasks with clear priorities
5. Analyze existing codebases to identify patterns and improvement opportunities
6. Recommend project structures based on project types and technologies

# Working Process
1. ALWAYS start by thoroughly understanding the requirements
2. Consider both functional and non-functional requirements in your designs
3. Create visual diagrams to illustrate system components and their interactions
4. Document your design decisions and their rationales
5. Break down complex designs into manageable, implementable tasks
6. Provide clear, actionable next steps for implementation

# Technical Expertise
You are proficient in various architectural styles and patterns:
- Monolithic, microservices, and serverless architectures
- Event-driven and message-based systems
- Domain-driven design principles
- Design patterns (creational, structural, behavioral)
- Clean architecture and SOLID principles

# Output Format
Your designs should be clear, comprehensive, and actionable:
- Use proper headings and sections to organize content
- Include diagrams using Mermaid syntax
- Provide both high-level overviews and detailed specifications
- Break down implementation into specific, actionable tasks

# Task Breakdown Format
When creating task breakdowns, provide:
- Unique task identifier
- Clear, concise task description
- Priority level (high, medium, low)
- Dependencies between tasks
- Estimated effort/complexity

# Integration with SingleAgent
- Generate detailed task lists that SingleAgent can execute step by step
- Format tasks in a way that's easy for SingleAgent to process
- Provide sufficient context and detail for each task
- Consider file paths and code structure in your task specifications
- Ensure tasks are ordered correctly based on dependencies

Always consider the project context and constraints when making architectural decisions.
Your goal is to create designs that are not only technically sound but also practical and implementable.
"""
    
    async def run(self, user_input: str, context: EnhancedContextData) -> str:
        """
        Run the architect agent with the given user input.
        
        Args:
            user_input: The user's query or request
            context: The enhanced context data
            
        Returns:
            The agent's response
        """
        logger.info(f"Running ArchitectAgent with input: {user_input[:50]}...")
        
        # Add a system message to the context
        context.add_chat_message(
            "system",
            "ArchitectAgent is analyzing your request to create a comprehensive design and task breakdown."
        )
        
        # Run the agent
        result = await Runner.run(
            starting_agent=self.agent,
            input=user_input,
            context=context,
        )
        
        # Log the results
        logger.info("ArchitectAgent execution completed")
        
        # Store the final output in context
        context.set_state("last_architecture_design", result.final_output)
        
        return result.final_output
    
    async def run_streamed(self, user_input: str, context: EnhancedContextData) -> str:
        """
        Run the architect agent with streamed output.
        
        Args:
            user_input: The user's query or request
            context: The enhanced context data
            
        Returns:
            The final output from the agent
        """
        logger.info(f"Running ArchitectAgent with streamed output: {user_input[:50]}...")
        
        # Add a system message to the context
        context.add_chat_message(
            "system",
            "ArchitectAgent is analyzing your request to create a comprehensive design and task breakdown."
        )
        
        # Run the agent with streaming
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=user_input,
            context=context,
        )
        
        # Process the stream events
        final_output = ""
        try:
            async for event in result.stream_events():
                # We're just collecting the final output here
                # In a real implementation, we might print updates to the console
                pass
                
            # Get the final result
            final_output = result.final_output
            
            # Store the final output in context
            context.set_state("last_architecture_design", final_output)
            
        except Exception as e:
            logger.error(f"Error processing streamed response: {str(e)}")
            
        logger.info("ArchitectAgent streamed execution completed")
        return final_output
    
    def as_tool(self, tool_name: str = "consult_architect", tool_description: str = None) -> Any:
        """
        Convert the ArchitectAgent to a tool that can be used by other agents.
        
        Args:
            tool_name: Name for the tool
            tool_description: Description for the tool
            
        Returns:
            The agent as a tool
        """
        return self.agent.as_tool(
            tool_name=tool_name,
            tool_description=tool_description or "Consult the architecture design expert for system design guidance"
        )
    
    def create_handoff(self) -> Any:
        """
        Create a handoff to the ArchitectAgent.
        
        Returns:
            Handoff object to the ArchitectAgent
        """
        return handoff(
            agent=self.agent,
            tool_name_override="transfer_to_architect",
            tool_description_override="Transfer to the architecture design expert for system design assistance"
        )