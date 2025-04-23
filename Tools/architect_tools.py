"""
Tools for the architect agent.
Specialized tools for code analysis, project planning, and coordination with the code agent.
Uses Python's AST module for deep code structure analysis.
"""

import os
import sys
import ast
import json
import logging
import asyncio
import networkx as nx
from typing import List, Optional, Dict, Any, Tuple, Union, Set, cast
from typing_extensions import Annotated

from pydantic import BaseModel, Field
from logging.handlers import RotatingFileHandler

from agents import function_tool, RunContextWrapper
from The_Agents.context_data import EnhancedContextData

# Configure logger for architect tools
arch_logger = logging.getLogger("ArchitectTools")
arch_logger.setLevel(logging.DEBUG)
# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)
# rotating file handler
arch_handler = RotatingFileHandler('logs/architect_tools.log', maxBytes=10*1024*1024, backupCount=3)
arch_handler.setLevel(logging.DEBUG)
arch_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
arch_logger.addHandler(arch_handler)
arch_logger.propagate = False
# alias arch_logger as logger for use in function implementations
logger = arch_logger

# Utilities for tracking entities in context
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

# Pydantic models for tool parameters
class FileParams(BaseModel):
    """Parameters for file operations."""
    file_path: str = Field(description="Path to the file")

class ProjectStructureParams(BaseModel):
    """Parameters for project structure analysis."""
    directory: str = Field(description="Directory to analyze")
    max_depth: int = Field(description="Maximum directory depth to traverse")
    include_patterns: List[str] = Field(description="File patterns to include")
    exclude_patterns: List[str] = Field(description="File patterns to exclude")

class ASTAnalysisParams(BaseModel):
    """Parameters for AST analysis."""
    file_path: str = Field(description="Path to the Python file to analyze")
    analysis_type: str = Field(description="Type of analysis to perform (imports, classes, functions, dependencies)")

class TodoGenerationParams(BaseModel):
    """Parameters for TODO list generation."""
    description: str = Field(description="Project description")
    features: List[str] = Field(description="List of features to implement")
    directory: Optional[str] = Field(description="Project directory if existing")

class CodePatternParams(BaseModel):
    """Parameters for code pattern recognition."""
    file_path: str = Field(description="Path to the file to analyze")
    pattern_type: str = Field(description="Type of pattern to look for")

class DependencyGraphParams(BaseModel):
    """Parameters for creating dependency graphs."""
    directory: str = Field(description="Project directory")
    include_external: bool = Field(description="Whether to include external dependencies")

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

# Tool implementations

@function_tool
async def analyze_ast(wrapper: RunContextWrapper[EnhancedContextData], params: ASTAnalysisParams) -> Dict[str, Any]:
    """
    Analyze a Python file using the AST module to extract code structure information.
    
    This tool can extract:
    - Imports (modules, specific imports, aliases)
    - Classes (names, inheritance, methods, class variables)
    - Functions (names, parameters, return annotations, docstrings)
    - Dependencies (modules and packages used)
    
    Args:
        file_path: Path to the Python file to analyze
        analysis_type: Type of analysis to perform (imports, classes, functions, dependencies, or all)
        
    Returns:
        Dictionary containing the requested analysis information
    """
    logger.debug(json.dumps({"tool": "analyze_ast", "params": params.model_dump()}))
    
    try:
        # Read the file and parse the AST
        with open(params.file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Track file entity in context
        track_file_entity(wrapper.context, params.file_path, code)
        
        # Parse the AST
        tree = ast.parse(code, filename=params.file_path)
        
        # Prepare the result dictionary
        result = {}
        
        # Analyze imports if requested
        if params.analysis_type in ('imports', 'all'):
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append({
                            'module': name.name,
                            'name': None,
                            'alias': name.asname,
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        imports.append({
                            'module': node.module,
                            'name': name.name,
                            'alias': name.asname,
                            'line': node.lineno
                        })
            result['imports'] = imports
        
        # Analyze classes if requested
        if params.analysis_type in ('classes', 'all'):
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'lineno': node.lineno,
                        'bases': [ast.unparse(base).strip() for base in node.bases],
                        'methods': [],
                        'class_vars': []
                    }
                    
                    # Extract docstring if available
                    docstring = ast.get_docstring(node)
                    if docstring:
                        class_info['docstring'] = docstring
                    
                    # Extract methods and class variables
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'lineno': item.lineno,
                                'args': [arg.arg for arg in item.args.args],
                            }
                            method_docstring = ast.get_docstring(item)
                            if method_docstring:
                                method_info['docstring'] = method_docstring
                            class_info['methods'].append(method_info)
                        elif isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    class_info['class_vars'].append({
                                        'name': target.id,
                                        'lineno': item.lineno
                                    })
                    
                    classes.append(class_info)
            result['classes'] = classes
        
        # Analyze functions if requested
        if params.analysis_type in ('functions', 'all'):
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.iter_child_nodes(tree) if node in ast.iter_child_nodes(parent)):
                    func_info = {
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                    }
                    
                    # Extract docstring if available
                    docstring = ast.get_docstring(node)
                    if docstring:
                        func_info['docstring'] = docstring
                    
                    # Extract return annotation if available
                    if node.returns:
                        func_info['returns'] = ast.unparse(node.returns).strip()
                    
                    functions.append(func_info)
            result['functions'] = functions
        
        # Analyze dependencies if requested
        if params.analysis_type in ('dependencies', 'all'):
            dependencies = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        dependencies.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.add(node.module.split('.')[0])
            result['dependencies'] = list(dependencies)
        
        logger.debug(json.dumps({"tool": "analyze_ast", "result_size": len(json.dumps(result))}))
        return result
    except Exception as e:
        logger.error(f"Error in analyze_ast: {str(e)}", exc_info=True)
        return {"error": str(e)}

@function_tool
async def analyze_project_structure(wrapper: RunContextWrapper[EnhancedContextData], params: ProjectStructureParams) -> Dict[str, Any]:
    """
    Analyze the structure of a project directory to generate a hierarchical representation.
    
    This tool maps out the directory structure, categorizing files by type, and provides
    a comprehensive overview of the project layout. It can filter files based on patterns
    and limit the depth of directory traversal.
    
    Args:
        directory: Directory to analyze
        max_depth: Maximum directory depth to traverse
        include_patterns: File patterns to include (e.g., ["*.py", "*.md"])
        exclude_patterns: File patterns to exclude (e.g., ["__pycache__", "*.pyc"])
        
    Returns:
        Dictionary containing project structure information
    """
    logger.debug(json.dumps({"tool": "analyze_project_structure", "params": params.model_dump()}))
    
    try:
        import fnmatch
        from pathlib import Path
        
        # Validate the directory
        if not os.path.isdir(params.directory):
            return {"error": f"Directory not found: {params.directory}"}
        
        # Function to check if a file matches include/exclude patterns
        def should_include(file_path):
            # Check exclude patterns first
            for pattern in params.exclude_patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    return False
            
            # If include patterns are specified, file must match at least one
            if params.include_patterns:
                for pattern in params.include_patterns:
                    if fnmatch.fnmatch(file_path, pattern):
                        return True
                return False
            
            # If no include patterns, include all files not excluded
            return True
        
        # Build the directory structure recursively
        def build_tree(directory, current_depth=0):
            if current_depth > params.max_depth:
                return {"truncated": True}
            
            result = {"files": [], "directories": {}}
            
            try:
                entries = list(os.scandir(directory))
                
                # Process files first
                for entry in [e for e in entries if e.is_file()]:
                    if should_include(entry.name):
                        file_info = {
                            "name": entry.name,
                            "path": os.path.relpath(entry.path, params.directory),
                            "size": entry.stat().st_size
                        }
                        
                        # Add file extension for categorization
                        file_ext = os.path.splitext(entry.name)[1].lower()
                        if file_ext:
                            file_info["extension"] = file_ext
                        
                        result["files"].append(file_info)
                
                # Then process directories
                for entry in [e for e in entries if e.is_dir()]:
                    # Skip directories that match exclude patterns
                    if not any(fnmatch.fnmatch(entry.name, pattern) for pattern in params.exclude_patterns):
                        subdir_result = build_tree(entry.path, current_depth + 1)
                        result["directories"][entry.name] = subdir_result
            
            except PermissionError:
                result["error"] = "Permission denied"
            
            return result
        
        # Analyze structure
        structure = build_tree(params.directory)
        
        # Collect statistics
        file_types = {}
        file_count = 0
        dir_count = 0
        
        def count_items(tree):
            nonlocal file_count, dir_count
            
            # Count files and categorize by extension
            for file_info in tree.get("files", []):
                file_count += 1
                ext = file_info.get("extension", "unknown")
                file_types[ext] = file_types.get(ext, 0) + 1
            
            # Count directories and process recursively
            directories = tree.get("directories", {})
            dir_count += len(directories)
            
            for dir_name, dir_tree in directories.items():
                count_items(dir_tree)
        
        count_items(structure)
        
        # Prepare result
        result = {
            "structure": structure,
            "statistics": {
                "file_count": file_count,
                "directory_count": dir_count,
                "file_types": file_types
            },
            "base_directory": os.path.abspath(params.directory)
        }
        
        # Track this activity in context
        wrapper.context.track_entity(
            entity_type="project",
            value=params.directory,
            metadata={"file_count": file_count, "dir_count": dir_count}
        )
        
        logger.debug(json.dumps({"tool": "analyze_project_structure", "result_size": len(json.dumps(result))}))
        return result
    
    except Exception as e:
        logger.error(f"Error in analyze_project_structure: {str(e)}", exc_info=True)
        return {"error": str(e)}

@function_tool
async def generate_todo_list(wrapper: RunContextWrapper[EnhancedContextData], params: TodoGenerationParams) -> Dict[str, Any]:
    """
    Generate a structured TODO list for implementing a project based on description and features.
    
    This tool creates a comprehensive, prioritized task list that can be assigned to the code agent.
    It breaks down features into manageable tasks and establishes dependencies between them.
    If a directory is provided, it will analyze the existing project structure to suggest tasks
    that integrate with the current codebase.
    
    Args:
        description: High-level project description
        features: List of features to implement
        directory: Optional project directory for existing projects
        
    Returns:
        Dictionary containing structured TODO list with tasks, priorities, and dependencies
    """
    logger.debug(json.dumps({"tool": "generate_todo_list", "params": params.model_dump()}))
    
    try:
        # Initialize the result structure
        result = {
            "project_description": params.description,
            "feature_count": len(params.features),
            "tasks": [],
            "estimated_completion_time": None,
            "suggested_approach": None
        }
        
        # Track this as a task in the context
        wrapper.context.track_entity(
            entity_type="task",
            value=f"TODO for: {params.description[:50]}...",
            metadata={"features": len(params.features)}
        )
        
        # If directory is provided, analyze existing structure
        existing_structure = None
        if params.directory and os.path.isdir(params.directory):
            # Use project structure tool to analyze
            structure_params = ProjectStructureParams(
                directory=params.directory,
                max_depth=3,
                include_patterns=["*.py", "*.md", "*.txt", "*.json"],
                exclude_patterns=["__pycache__", "*.pyc", "*.pyo", ".git", ".venv", "venv"]
            )
            existing_structure = await analyze_project_structure(wrapper, structure_params)
        
        # Process features into tasks
        task_id = 1
        for i, feature in enumerate(params.features):
            # Create a main task for the feature
            feature_task = {
                "id": task_id,
                "title": f"Implement {feature}",
                "description": f"Implement the {feature} functionality",
                "priority": "high" if i < 2 else "medium",
                "category": "feature",
                "subtasks": [],
                "dependencies": []
            }
            task_id += 1
            
            # Create subtasks for planning, implementation, and testing
            subtasks = [
                {
                    "id": task_id,
                    "title": f"Design {feature} architecture",
                    "description": f"Create detailed design for {feature} implementation",
                    "priority": "high",
                    "category": "planning",
                    "estimated_time": "1-2 hours"
                },
                {
                    "id": task_id + 1,
                    "title": f"Implement {feature} core functionality",
                    "description": f"Code the main components for {feature}",
                    "priority": "high",
                    "category": "implementation",
                    "estimated_time": "2-4 hours",
                    "dependencies": [task_id]
                },
                {
                    "id": task_id + 2,
                    "title": f"Write tests for {feature}",
                    "description": f"Create comprehensive tests for {feature}",
                    "priority": "medium",
                    "category": "testing",
                    "estimated_time": "1-2 hours",
                    "dependencies": [task_id + 1]
                },
                {
                    "id": task_id + 3,
                    "title": f"Document {feature}",
                    "description": f"Create documentation for {feature}",
                    "priority": "low",
                    "category": "documentation",
                    "estimated_time": "1 hour",
                    "dependencies": [task_id + 1]
                }
            ]
            
            feature_task["subtasks"] = subtasks
            task_id += 4
            
            # Add to main tasks list
            result["tasks"].append(feature_task)
        
        # Add infrastructure tasks if needed
        if not existing_structure:
            # This is a new project, add setup tasks
            setup_tasks = [
                {
                    "id": task_id,
                    "title": "Project setup",
                    "description": "Set up project structure and configuration",
                    "priority": "critical",
                    "category": "infrastructure",
                    "estimated_time": "1 hour",
                    "subtasks": [
                        {
                            "id": task_id + 1,
                            "title": "Create directory structure",
                            "priority": "critical",
                            "category": "setup",
                            "estimated_time": "15 minutes"
                        },
                        {
                            "id": task_id + 2,
                            "title": "Initialize version control",
                            "priority": "high",
                            "category": "setup",
                            "estimated_time": "15 minutes"
                        },
                        {
                            "id": task_id + 3,
                            "title": "Set up dependencies",
                            "priority": "high",
                            "category": "setup",
                            "estimated_time": "30 minutes"
                        }
                    ]
                }
            ]
            result["tasks"] = setup_tasks + result["tasks"]
            task_id += 4
        
        # Calculate estimated completion time
        total_min_hours = 0
        total_max_hours = 0
        
        def process_task_time(task):
            nonlocal total_min_hours, total_max_hours
            
            if "estimated_time" in task:
                time_str = task["estimated_time"]
                if "-" in time_str:
                    min_str, max_str = time_str.split("-")
                    min_val = float(min_str.strip().split()[0])
                    max_val = float(max_str.strip().split()[0])
                    total_min_hours += min_val
                    total_max_hours += max_val
                else:
                    hours = float(time_str.split()[0])
                    total_min_hours += hours
                    total_max_hours += hours
            
            if "subtasks" in task:
                for subtask in task["subtasks"]:
                    process_task_time(subtask)
        
        for task in result["tasks"]:
            process_task_time(task)
        
        result["estimated_completion_time"] = f"{total_min_hours:.1f}-{total_max_hours:.1f} hours"
        
        # Suggest approach based on project complexity
        if total_max_hours < 10:
            result["suggested_approach"] = "Sequential implementation of features"
        elif total_max_hours < 20:
            result["suggested_approach"] = "Implement core features first, then secondary features"
        else:
            result["suggested_approach"] = "Modular implementation with iterative development cycles"
        
        logger.debug(json.dumps({"tool": "generate_todo_list", "result_size": len(json.dumps(result))}))
        return result
    
    except Exception as e:
        logger.error(f"Error in generate_todo_list: {str(e)}", exc_info=True)
        return {"error": str(e)}

@function_tool
async def analyze_dependencies(wrapper: RunContextWrapper[EnhancedContextData], params: DependencyGraphParams) -> Dict[str, Any]:
    """
    Analyze Python module dependencies in a project and generate a dependency graph.
    
    This tool maps out how modules depend on each other, identifying both internal project
    dependencies and external library dependencies. It can help identify potential refactoring
    targets or architectural issues.
    
    Args:
        directory: Project directory to analyze
        include_external: Whether to include external library dependencies
        
    Returns:
        Dictionary containing dependency information and graph representation
    """
    logger.debug(json.dumps({"tool": "analyze_dependencies", "params": params.model_dump()}))
    
    try:
        import glob
        
        # Check if directory exists
        if not os.path.isdir(params.directory):
            return {"error": f"Directory not found: {params.directory}"}
        
        # Find all Python files in the directory
        python_files = glob.glob(f"{params.directory}/**/*.py", recursive=True)
        
        # Create a graph to represent dependencies
        G = nx.DiGraph()
        
        # Map to store module path to module name
        module_map = {}
        
        # Process each Python file
        for file_path in python_files:
            # Get relative path for node name
            rel_path = os.path.relpath(file_path, params.directory)
            module_name = os.path.splitext(rel_path.replace(os.path.sep, "."))[0]
            module_map[file_path] = module_name
            
            # Add node to graph
            G.add_node(module_name, type="internal", path=rel_path)
            
            # Parse the file to extract imports
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=file_path)
                except SyntaxError:
                    # Skip files with syntax errors
                    continue
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imported_module = name.name.split('.')[0]
                            if imported_module not in G:
                                G.add_node(imported_module, type="external")
                            
                            if params.include_external or imported_module in module_map.values():
                                G.add_edge(module_name, imported_module)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_module = node.module.split('.')[0]
                            if imported_module not in G:
                                G.add_node(imported_module, type="external")
                            
                            if params.include_external or imported_module in module_map.values():
                                G.add_edge(module_name, imported_module)
        
        # Analyze the graph
        # Get modules with most dependencies (highest in-degree)
        most_dependent = sorted(G.in_degree(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get modules that import the most (highest out-degree)
        most_imports = sorted(G.out_degree(), key=lambda x: x[1], reverse=True)[:5]
        
        # Identify potential circular dependencies
        try:
            cycles = list(nx.simple_cycles(G))
        except:
            cycles = []  # Handle case where cycles can't be found
        
        # Prepare result
        result = {
            "module_count": len(module_map),
            "dependency_count": G.number_of_edges(),
            "external_dependencies": [n for n in G.nodes() if G.nodes[n].get("type") == "external"],
            "most_dependent_modules": most_dependent,
            "modules_with_most_imports": most_imports,
            "circular_dependencies": cycles,
            "graph_representation": {
                "nodes": [{"id": n, "type": G.nodes[n].get("type", "unknown")} for n in G.nodes()],
                "edges": [{"source": u, "target": v} for u, v in G.edges()]
            }
        }
        
        # Track this analysis in context
        wrapper.context.track_entity(
            entity_type="analysis",
            value=f"Dependency analysis for {params.directory}",
            metadata={"module_count": len(module_map), "dependency_count": G.number_of_edges()}
        )
        
        logger.debug(json.dumps({"tool": "analyze_dependencies", "result_size": len(json.dumps(result))}))
        return result
    
    except Exception as e:
        logger.error(f"Error in analyze_dependencies: {str(e)}", exc_info=True)
        return {"error": str(e)}

@function_tool
async def detect_code_patterns(wrapper: RunContextWrapper[EnhancedContextData], params: CodePatternParams) -> Dict[str, Any]:
    """
    Detect common code patterns, anti-patterns, or architectural patterns in a Python file.
    
    This tool analyzes code to identify patterns such as Singleton, Factory, Observer,
    or anti-patterns like God Object, Shotgun Surgery, etc. It helps in understanding
    the code architecture and suggests potential refactoring opportunities.
    
    Args:
        file_path: Path to the file to analyze
        pattern_type: Type of pattern to look for (design_patterns, anti_patterns, all)
        
    Returns:
        Dictionary containing detected patterns and their instances
    """
    logger.debug(json.dumps({"tool": "detect_code_patterns", "params": params.model_dump()}))
    
    try:
        # Read and parse the file
        with open(params.file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Track file entity in context
        track_file_entity(wrapper.context, params.file_path, code)
        
        # Parse the AST
        tree = ast.parse(code, filename=params.file_path)
        
        # Define pattern detectors
        design_patterns = {
            "singleton": {
                "description": "A class that has a single instance throughout the program",
                "instances": [],
                "confidence": 0
            },
            "factory": {
                "description": "A method that creates and returns objects",
                "instances": [],
                "confidence": 0
            },
            "observer": {
                "description": "Implementation of the observer pattern (callbacks, event handlers)",
                "instances": [],
                "confidence": 0
            },
            "decorator": {
                "description": "Function or class that extends the behavior of another function/class",
                "instances": [],
                "confidence": 0
            },
            "facade": {
                "description": "Simple interface to a complex subsystem",
                "instances": [],
                "confidence": 0
            }
        }
        
        anti_patterns = {
            "god_object": {
                "description": "Class that knows or does too much",
                "instances": [],
                "confidence": 0
            },
            "shotgun_surgery": {
                "description": "Many changes needed across many classes for a single change",
                "instances": [],
                "confidence": 0
            },
            "magic_numbers": {
                "description": "Unnamed numerical constants in the code",
                "instances": [],
                "confidence": 0
            },
            "duplicate_code": {
                "description": "Repeated code blocks that could be refactored",
                "instances": [],
                "confidence": 0
            }
        }
        
        # Detect singleton pattern
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for singleton pattern
                has_instance_var = False
                has_instance_method = False
                
                for item in node.body:
                    # Check for class variable named _instance or similar
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id in ['_instance', 'instance', '__instance']:
                                has_instance_var = True
                    
                    # Check for getInstance or similar method
                    if isinstance(item, ast.FunctionDef) and item.name.lower() in ['getinstance', 'get_instance', 'instance']:
                        has_instance_method = True
                
                if has_instance_var and has_instance_method:
                    design_patterns["singleton"]["instances"].append({
                        "name": node.name,
                        "line": node.lineno
                    })
                    design_patterns["singleton"]["confidence"] = 0.9
                elif has_instance_var or has_instance_method:
                    design_patterns["singleton"]["instances"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "note": "Possible singleton, missing some characteristics"
                    })
                    design_patterns["singleton"]["confidence"] = 0.5
        
        # Detect factory pattern
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function creates and returns objects
                creates_object = False
                returns_created = False
                created_class = None
                
                for subnode in ast.walk(node):
                    # Check for instantiation
                    if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Name):
                        creates_object = True
                        created_class = subnode.func.id
                    
                    # Check for return statement returning the created object
                    if isinstance(subnode, ast.Return) and isinstance(subnode.value, ast.Name) and created_class:
                        returns_created = True
                
                if creates_object and returns_created:
                    # Function name contains 'create', 'make', 'build', 'get', or 'factory'
                    if any(kw in node.name.lower() for kw in ['create', 'make', 'build', 'get', 'factory']):
                        design_patterns["factory"]["instances"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "creates": created_class
                        })
                        design_patterns["factory"]["confidence"] = 0.8
        
        # Detect God Object anti-pattern
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
                attr_count = sum(1 for item in node.body if isinstance(item, ast.Assign))
                
                # Classes with many methods and attributes might be God Objects
                if method_count > 10 and attr_count > 10:
                    anti_patterns["god_object"]["instances"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "method_count": method_count,
                        "attribute_count": attr_count
                    })
                    anti_patterns["god_object"]["confidence"] = 0.7
        
        # Detect magic numbers
        for node in ast.walk(tree):
            if isinstance(node, ast.Num) and not isinstance(node.parent, ast.Assign):
                # Exclude common numbers like 0, 1, -1, 2
                if node.n not in [0, 1, -1, 2, 10, 100]:
                    anti_patterns["magic_numbers"]["instances"].append({
                        "value": node.n,
                        "line": getattr(node, "lineno", "unknown")
                    })
                    anti_patterns["magic_numbers"]["confidence"] = 0.6
        
        # Prepare result based on requested pattern_type
        result = {
            "file_analyzed": params.file_path,
            "pattern_type": params.pattern_type
        }
        
        if params.pattern_type in ["design_patterns", "all"]:
            result["design_patterns"] = {k: v for k, v in design_patterns.items() if v["instances"]}
        
        if params.pattern_type in ["anti_patterns", "all"]:
            result["anti_patterns"] = {k: v for k, v in anti_patterns.items() if v["instances"]}
        
        # Add summary
        result["summary"] = {
            "design_patterns_found": sum(1 for p in design_patterns.values() if p["instances"]),
            "anti_patterns_found": sum(1 for p in anti_patterns.values() if p["instances"])
        }
        
        logger.debug(json.dumps({"tool": "detect_code_patterns", "result_size": len(json.dumps(result))}))
        return result
    
    except Exception as e:
        logger.error(f"Error in detect_code_patterns: {str(e)}", exc_info=True)
        return {"error": str(e)}

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
