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
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Union, Set, cast
from typing_extensions import Annotated

from pydantic import BaseModel, Field
from logging.handlers import RotatingFileHandler

from agents import function_tool, RunContextWrapper
from The_Agents.context_data import EnhancedContextData
# Import shared tools and utilities
from .shared_tools import (
    track_file_entity, track_command_entity,
    get_context_response, add_manual_context, run_command, read_file, get_context,
    GetContextParams, GetContextResponse, AddManualContextParams, RunCommandParams, FileReadParams
)

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
    
class DirectoryReadParams(BaseModel):
    """Parameters for reading a directory structure."""
    directory_path: str = Field(description="Path to the directory to read")
    max_depth: int = Field(description="Maximum depth to traverse")
    include_patterns: List[str] = Field(description="File patterns to include (e.g., ['*.py', '*.md'])")
    exclude_patterns: List[str] = Field(description="File patterns to exclude (e.g., ['__pycache__', '*.pyc'])")

class WriteFileParams(BaseModel):
    """Parameters for writing to a file."""
    file_path: str = Field(description="Path to the file to write")
    content: str = Field(description="Content to write to the file")
    mode: Optional[str] = Field(None, description="Write mode: 'w' for write, 'a' for append")

@function_tool
async def write_file(wrapper: RunContextWrapper[EnhancedContextData], params: WriteFileParams) -> str:
    """
    Write content to a file on disk.
    """
    # Compute write mode, defaulting to 'w' if not provided
    mode = params.mode if params.mode is not None else "w"
    logger.debug(json.dumps({"tool": "write_file", "params": {"file_path": params.file_path, "mode": mode}}))
    
    try:
        # Ensure the directory exists
        directory = os.path.dirname(params.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        # Write the file
        with open(params.file_path, mode, encoding='utf-8') as f:
            f.write(params.content)
        
        # Track file entity in context
        track_file_entity(wrapper.context, params.file_path, params.content)
        
        file_size = os.path.getsize(params.file_path)
        logger.debug(json.dumps({"tool": "write_file", "output": f"File written: {params.file_path}, size: {file_size} bytes"}))
        
        return f"Successfully wrote {file_size} bytes to {params.file_path}"
    except Exception as e:
        logger.debug(json.dumps({"tool": "write_file", "error": str(e)}))
        return f"Error writing to file: {str(e)}"

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
                # Check if this is a top-level function (not a method in a class)
                if isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.iter_child_nodes(tree) if hasattr(parent, 'body') and node in parent.body):
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
            # Create structure parameters
            structure_params = ProjectStructureParams(
                directory=params.directory,
                max_depth=3,
                include_patterns=["*.py", "*.md", "*.txt", "*.json"],
                exclude_patterns=["__pycache__", "*.pyc", "*.pyo", ".git", ".venv", "venv"]
            )
            
            # Use analyze_project_structure directly
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
        # We'll modify this section to avoid the parent attribute issue
        magic_numbers = []
        for node in ast.walk(tree):
            # Check for magic numbers in the code (Python 3.8+ compatible)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Exclude common numbers like 0, 1, -1, 2
                if node.value not in [0, 1, -1, 2, 10, 100]:
                    magic_numbers.append({
                        "value": node.value,
                        "line": getattr(node, "lineno", "unknown")
                    })
        
        if magic_numbers:
            anti_patterns["magic_numbers"]["instances"] = magic_numbers
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
async def read_directory(wrapper: RunContextWrapper[EnhancedContextData], params: DirectoryReadParams) -> Dict[str, Any]:
    """
    Read a directory structure and return organized information about its contents.
    
    This tool scans a directory and its subdirectories up to a specified depth,
    applying include and exclude patterns to filter the files. It returns a structured
    representation of the directory contents along with statistics.
    
    Args:
        directory_path: Path to the directory to read
        max_depth: Maximum depth to traverse (1 = just the specified directory, no subdirectories)
        include_patterns: File patterns to include (e.g., ['*.py', '*.md'])
        exclude_patterns: File patterns to exclude (e.g., ['__pycache__', '*.pyc'])
        
    Returns:
        Dictionary containing directory structure and statistics
    """
    logger.debug(json.dumps({"tool": "read_directory", "params": params.model_dump()}))
    
    try:
        import fnmatch
        
        # Normalize path - handle relative paths automatically
        directory_path = params.directory_path
        if not os.path.isabs(directory_path):
            directory_path = os.path.abspath(os.path.join(os.getcwd(), directory_path))
            logger.info(f"Converted relative path to absolute: {directory_path}")
            
        directory_path = os.path.normpath(directory_path)
        
        # Check if the path exists
        if not os.path.exists(directory_path):
            return {"error": f"Path not found: {directory_path}"}
            
        # Check if it's a directory
        if not os.path.isdir(directory_path):
            return {"error": f"Not a directory: {directory_path}. Use read_file instead."}
        
        # Function to check if a file should be included based on patterns
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
        
        # Function to build directory tree recursively
        def build_tree(path, current_depth=0):
            if current_depth > params.max_depth:
                return {"truncated": True, "message": f"Reached maximum depth of {params.max_depth}"}
            
            result = {"files": [], "directories": {}}
            
            try:
                entries = list(os.scandir(path))
                
                # Process files first
                for entry in sorted([e for e in entries if e.is_file()], key=lambda e: e.name):
                    if should_include(entry.name):
                        rel_path = os.path.relpath(entry.path, directory_path)
                        try:
                            file_stats = entry.stat()
                            
                            # Get file extension
                            _, file_extension = os.path.splitext(entry.name)
                            
                            file_info = {
                                "name": entry.name,
                                "path": rel_path,
                                "extension": file_extension.lower(),
                                "size": file_stats.st_size,
                                "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                            }
                            
                            result["files"].append(file_info)
                        except PermissionError:
                            # Handle inaccessible files
                            result["files"].append({
                                "name": entry.name,
                                "path": rel_path,
                                "error": "Permission denied"
                            })
                
                # Process directories
                for entry in sorted([e for e in entries if e.is_dir()], key=lambda e: e.name):
                    # Skip directories that match exclude patterns
                    if not any(fnmatch.fnmatch(entry.name, pattern) for pattern in params.exclude_patterns):
                        try:
                            subdir_result = build_tree(entry.path, current_depth + 1)
                            result["directories"][entry.name] = subdir_result
                        except PermissionError:
                            result["directories"][entry.name] = {"error": "Permission denied"}
            
            except PermissionError:
                result["error"] = "Permission denied"
            
            return result
        
        # Build the directory tree
        tree = build_tree(directory_path)
        
        # Collect statistics
        file_count = 0
        dir_count = 0
        file_types = {}
        error_count = 0
        
        def count_items(tree_node):
            nonlocal file_count, dir_count, error_count
            
            # Check for errors in the current node
            if "error" in tree_node:
                error_count += 1
            
            # Count files and categorize by extension
            for file_info in tree_node.get("files", []):
                file_count += 1
                if "error" in file_info:
                    error_count += 1
                    continue
                    
                ext = file_info.get("extension", "").lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            
            # Count directories and process recursively
            directories = tree_node.get("directories", {})
            dir_count += len(directories)
            
            for dir_name, dir_tree in directories.items():
                count_items(dir_tree)
        
        count_items(tree)
        
        # Track this as a project entity
        wrapper.context.track_entity(
            entity_type="project",
            value=directory_path,
            metadata={"file_count": file_count, "dir_count": dir_count}
        )
        
        # Create result
        result = {
            "structure": tree,
            "statistics": {
                "file_count": file_count,
                "directory_count": dir_count,
                "file_types": file_types,
                "largest_extension": max(file_types.items(), key=lambda x: x[1])[0] if file_types else None,
                "errors_encountered": error_count
            },
            "base_directory": directory_path
        }
        
        logger.debug(json.dumps({"tool": "read_directory", "result_size": len(json.dumps(result))}))
        return result
    
    except Exception as e:
        logger.error(f"Error in read_directory: {str(e)}", exc_info=True)
        return {"error": f"Error reading directory: {str(e)}"}
