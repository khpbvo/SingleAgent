# API Reference

This document provides comprehensive technical API documentation for the SingleAgent system, including classes, methods, and integration interfaces.

## Core API Overview

The SingleAgent system exposes several APIs for different use cases:
- **Agent API**: Core agent interaction and orchestration
- **Tools API**: Tool registration and execution
- **Context API**: Context management and persistence
- **Configuration API**: Runtime configuration management

## Agent API

### SingleAgent Class

The main Code Agent implementation.

```python
class SingleAgent:
    """
    Primary agent for code analysis, quality checking, and file operations.
    
    Inherits from OpenAI's Agent class and adds specialized tools for
    software development tasks.
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        max_tokens: int = 8000,
        tools: List[str] = None,
        context_manager: ContextManager = None
    ):
        """
        Initialize the Code Agent.
        
        Args:
            model: OpenAI model to use (default: "gpt-4")
            max_tokens: Maximum context window size
            tools: List of tools to enable (default: all code tools)
            context_manager: Context management instance
        """
        
    async def process_request(
        self,
        message: str,
        file_paths: List[str] = None,
        context: Dict[str, Any] = None
    ) -> AgentResponse:
        """
        Process a user request with the Code Agent.
        
        Args:
            message: User's request message
            file_paths: Optional list of files to analyze
            context: Additional context information
            
        Returns:
            AgentResponse with results and any file modifications
        """
        
    def add_tool(self, tool_name: str, tool_function: Callable) -> None:
        """
        Register a new tool with the agent.
        
        Args:
            tool_name: Name of the tool
            tool_function: Tool implementation function
        """
        
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tools.
        
        Returns:
            List of tool names available to this agent
        """
```

### ArchitectAgent Class

The specialized Architect Agent for project analysis.

```python
class ArchitectAgent:
    """
    Specialized agent for architectural analysis and project understanding.
    
    Provides tools for project structure analysis, design pattern detection,
    and architectural recommendations.
    """
    
    def __init__(
        self,
        model: str = "gpt-4", 
        max_tokens: int = 8000,
        analysis_depth: str = "standard",
        context_manager: ContextManager = None
    ):
        """
        Initialize the Architect Agent.
        
        Args:
            model: OpenAI model to use
            max_tokens: Maximum context window size
            analysis_depth: Analysis depth ("basic", "standard", "deep")
            context_manager: Context management instance
        """
        
    async def analyze_project(
        self,
        project_path: str,
        analysis_type: str = "full"
    ) -> ProjectAnalysis:
        """
        Perform comprehensive project analysis.
        
        Args:
            project_path: Path to project root
            analysis_type: Type of analysis ("structure", "patterns", "full")
            
        Returns:
            ProjectAnalysis object with findings and recommendations
        """
        
    async def detect_patterns(
        self,
        file_paths: List[str]
    ) -> List[DesignPattern]:
        """
        Detect design patterns in specified files.
        
        Args:
            file_paths: List of Python files to analyze
            
        Returns:
            List of detected design patterns with confidence scores
        """
```

### AgentOrchestrator Class

Manages dual-agent interaction and switching.

```python
class AgentOrchestrator:
    """
    Orchestrates interaction between Code and Architect agents.
    """
    
    def __init__(
        self,
        config: AgentConfig = None,
        context_manager: ContextManager = None
    ):
        """
        Initialize the agent orchestrator.
        
        Args:
            config: Configuration for both agents
            context_manager: Shared context manager
        """
        
    async def process_message(
        self,
        message: str,
        current_agent: str = "code"
    ) -> AgentResponse:
        """
        Process message with appropriate agent.
        
        Args:
            message: User message
            current_agent: Currently active agent ("code" or "architect")
            
        Returns:
            Response from the appropriate agent
        """
        
    def switch_agent(self, target_agent: str) -> str:
        """
        Switch to specified agent.
        
        Args:
            target_agent: Agent to switch to ("code" or "architect")
            
        Returns:
            Confirmation message
        """
```

## Tools API

### Tool Registration

```python
class ToolRegistry:
    """
    Registry for managing and executing tools.
    """
    
    @staticmethod
    def register_tool(
        name: str,
        function: Callable,
        agent_types: List[str] = None,
        schema: Dict[str, Any] = None
    ) -> None:
        """
        Register a new tool.
        
        Args:
            name: Tool name
            function: Tool implementation
            agent_types: Compatible agent types
            schema: JSON schema for parameters
        """
        
    @staticmethod
    def get_tool(name: str) -> Optional[Callable]:
        """
        Retrieve a registered tool.
        
        Args:
            name: Tool name
            
        Returns:
            Tool function or None if not found
        """
        
    @staticmethod
    async def execute_tool(
        name: str,
        parameters: Dict[str, Any],
        context: ToolContext = None
    ) -> ToolResult:
        """
        Execute a tool with given parameters.
        
        Args:
            name: Tool name
            parameters: Tool parameters
            context: Execution context
            
        Returns:
            Tool execution result
        """
```

### Code Quality Tools

#### Ruff Tool

```python
async def run_ruff(
    file_path: str,
    fix: bool = False,
    config_file: str = None
) -> ToolResult:
    """
    Run Ruff linter/formatter on Python file.
    
    Args:
        file_path: Path to Python file
        fix: Whether to apply automatic fixes
        config_file: Custom config file path
        
    Returns:
        ToolResult with linting results and any fixes applied
    """
```

#### Pylint Tool

```python
async def run_pylint(
    file_path: str,
    config_file: str = None,
    score_threshold: float = None
) -> ToolResult:
    """
    Run Pylint analysis on Python file.
    
    Args:
        file_path: Path to Python file
        config_file: Custom config file path
        score_threshold: Minimum acceptable score
        
    Returns:
        ToolResult with detailed analysis results
    """
```

#### Pyright Tool

```python
async def run_pyright(
    file_path: str,
    config_file: str = None,
    strict_mode: bool = False
) -> ToolResult:
    """
    Run Pyright type checker on Python file.
    
    Args:
        file_path: Path to Python file
        config_file: Custom config file path
        strict_mode: Enable strict type checking
        
    Returns:
        ToolResult with type checking results
    """
```

### File Operations Tools

```python
async def read_file(file_path: str) -> str:
    """
    Read file contents.
    
    Args:
        file_path: Path to file
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file not readable
    """

async def write_file(file_path: str, content: str, backup: bool = True) -> bool:
    """
    Write content to file.
    
    Args:
        file_path: Path to file
        content: Content to write
        backup: Create backup before writing
        
    Returns:
        True if successful
        
    Raises:
        PermissionError: If file not writable
    """

async def list_files(
    directory_path: str,
    pattern: str = "*",
    recursive: bool = False
) -> List[str]:
    """
    List files in directory.
    
    Args:
        directory_path: Directory to list
        pattern: File pattern to match
        recursive: Include subdirectories
        
    Returns:
        List of file paths
    """
```

### Analysis Tools

#### AST Analysis

```python
async def analyze_ast(file_path: str) -> ASTAnalysis:
    """
    Perform AST analysis on Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        ASTAnalysis object with structural information
    """

class ASTAnalysis:
    """Result of AST analysis."""
    
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    imports: List[ImportInfo]
    complexity_metrics: Dict[str, float]
    dependencies: List[str]
```

#### Project Structure Analysis

```python
async def analyze_project_structure(project_path: str) -> ProjectStructure:
    """
    Analyze project structure and organization.
    
    Args:
        project_path: Path to project root
        
    Returns:
        ProjectStructure with hierarchy and organization info
    """

class ProjectStructure:
    """Project structure analysis result."""
    
    directory_tree: Dict[str, Any]
    file_types: Dict[str, int]
    module_relationships: List[Tuple[str, str]]
    configuration_files: List[str]
    test_organization: Dict[str, Any]
```

## Context API

### ContextManager Class

```python
class ContextManager:
    """
    Manages conversation context, entity tracking, and memory.
    """
    
    def __init__(
        self,
        max_tokens: int = 8000,
        entity_cache_size: int = 1000,
        session_cache_size: int = 500
    ):
        """
        Initialize context manager.
        
        Args:
            max_tokens: Maximum context window size
            entity_cache_size: Maximum entities to cache
            session_cache_size: Maximum session items to cache
        """
        
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Add message to conversation history.
        
        Args:
            role: Message role ("user", "assistant", "system")
            content: Message content
            metadata: Additional metadata
        """
        
    def add_entity(
        self,
        entity_type: str,
        entity_name: str,
        entity_info: Dict[str, Any]
    ) -> None:
        """
        Add or update entity information.
        
        Args:
            entity_type: Type of entity ("class", "function", "variable")
            entity_name: Entity identifier
            entity_info: Entity details and metadata
        """
        
    def get_relevant_context(
        self,
        query: str,
        max_items: int = 10
    ) -> List[ContextItem]:
        """
        Retrieve context relevant to query.
        
        Args:
            query: Search query
            max_items: Maximum items to return
            
        Returns:
            List of relevant context items
        """
        
    def optimize_context(self) -> None:
        """
        Optimize context for token limits and relevance.
        """
```

### Entity Tracking

```python
class EntityTracker:
    """
    Tracks code entities and their relationships.
    """
    
    def track_file(self, file_path: str) -> None:
        """
        Extract and track entities from file.
        
        Args:
            file_path: Path to file to analyze
        """
        
    def get_entity_relationships(
        self,
        entity_name: str
    ) -> List[EntityRelationship]:
        """
        Get relationships for specified entity.
        
        Args:
            entity_name: Name of entity
            
        Returns:
            List of relationships
        """
        
    def find_related_entities(
        self,
        entity_name: str,
        relationship_types: List[str] = None
    ) -> List[str]:
        """
        Find entities related to specified entity.
        
        Args:
            entity_name: Source entity name
            relationship_types: Types of relationships to consider
            
        Returns:
            List of related entity names
        """
```

## Configuration API

### ConfigManager Class

```python
class ConfigManager:
    """
    Manages runtime configuration for agents and tools.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (dot-separated)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        
    def set_config(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (dot-separated)
            value: Value to set
        """
        
    def reload_config(self) -> None:
        """
        Reload configuration from file.
        """
        
    def validate_config(self) -> List[str]:
        """
        Validate current configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
```

## Data Models

### Core Response Types

```python
@dataclass
class AgentResponse:
    """Response from agent processing."""
    
    success: bool
    message: str
    files_modified: List[str] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolResult:
    """Result from tool execution."""
    
    tool_name: str
    success: bool
    output: str
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0

@dataclass
class DesignPattern:
    """Detected design pattern information."""
    
    pattern_name: str
    confidence: float
    location: str
    description: str
    examples: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
```

### Configuration Models

```python
@dataclass
class AgentConfig:
    """Configuration for agents."""
    
    model: str = "gpt-4"
    max_tokens: int = 8000
    enabled_tools: List[str] = field(default_factory=list)
    tool_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
@dataclass
class ToolConfig:
    """Configuration for individual tools."""
    
    enabled: bool = True
    timeout: int = 30
    parameters: Dict[str, Any] = field(default_factory=dict)
```

## Error Handling

### Exception Classes

```python
class SingleAgentError(Exception):
    """Base exception for SingleAgent system."""
    pass

class ToolExecutionError(SingleAgentError):
    """Error during tool execution."""
    
    def __init__(self, tool_name: str, message: str, details: Dict[str, Any] = None):
        self.tool_name = tool_name
        self.details = details or {}
        super().__init__(message)

class ConfigurationError(SingleAgentError):
    """Error in configuration."""
    
    def __init__(self, key: str, message: str):
        self.key = key
        super().__init__(message)

class ContextError(SingleAgentError):
    """Error in context management."""
    pass
```

## Integration Interfaces

### CLI Interface

```python
class CLIInterface:
    """Command-line interface for SingleAgent."""
    
    def __init__(self, config: AgentConfig = None):
        """Initialize CLI interface."""
        
    async def run_interactive(self) -> None:
        """Run interactive CLI session."""
        
    async def run_batch(self, commands: List[str]) -> List[AgentResponse]:
        """Run batch commands."""
        
    def parse_command(self, command: str) -> Tuple[str, Dict[str, Any]]:
        """Parse CLI command."""
```

### API Server Interface

```python
class APIServer:
    """REST API server for SingleAgent."""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize API server."""
        
    async def start(self) -> None:
        """Start the API server."""
        
    async def process_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process API request."""
```

### Plugin Interface

```python
class Plugin:
    """Base class for SingleAgent plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name."""
        
    @abstractmethod
    def get_tools(self) -> List[Tuple[str, Callable]]:
        """Get tools provided by this plugin."""
        
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
```

## Usage Examples

### Basic Agent Usage

```python
from singleagent import SingleAgent, ArchitectAgent

# Initialize Code Agent
code_agent = SingleAgent(model="gpt-4", max_tokens=8000)

# Process request
response = await code_agent.process_request(
    "Please analyze and fix code quality issues in src/main.py",
    file_paths=["src/main.py"]
)

print(f"Success: {response.success}")
print(f"Modified files: {response.files_modified}")
```

### Tool Registration

```python
from singleagent import ToolRegistry

async def custom_tool(file_path: str, option: str = "default") -> ToolResult:
    """Custom tool implementation."""
    # Tool logic here
    return ToolResult(
        tool_name="custom_tool",
        success=True,
        output="Tool completed successfully"
    )

# Register tool
ToolRegistry.register_tool(
    "custom_tool",
    custom_tool,
    agent_types=["code"],
    schema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "option": {"type": "string", "default": "default"}
        },
        "required": ["file_path"]
    }
)
```

### Context Management

```python
from singleagent import ContextManager

# Initialize context manager
context_mgr = ContextManager(max_tokens=8000)

# Add entity information
context_mgr.add_entity(
    "class",
    "UserManager", 
    {
        "file": "src/models.py",
        "methods": ["create_user", "delete_user"],
        "dependencies": ["Database"]
    }
)

# Get relevant context for query
relevant_context = context_mgr.get_relevant_context(
    "How do I modify user creation?",
    max_items=5
)
```

This API reference provides complete technical documentation for integrating with and extending the SingleAgent system.
