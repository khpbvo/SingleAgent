# API Reference

Complete technical reference for SingleAgent's APIs, classes, and methods. This documentation covers the core system components and their programmatic interfaces.

## Core System APIs

### SingleAgent Class

The main entry point for the SingleAgent system.

```python
class SingleAgent:
    """
    Main SingleAgent controller that orchestrates dual-agent interactions
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize SingleAgent with configuration
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
    
    def process_message(self, message: str, context: ContextData = None) -> AgentResponse:
        """
        Process user message and return agent response
        
        Args:
            message (str): User input message
            context (ContextData): Optional conversation context
            
        Returns:
            AgentResponse: Response from appropriate agent
        """
    
    def get_active_agent(self) -> str:
        """
        Get currently active agent name
        
        Returns:
            str: 'code_agent' or 'architect_agent'
        """
    
    def switch_agent(self, agent_name: str, context: ContextData = None) -> bool:
        """
        Manually switch to specified agent
        
        Args:
            agent_name (str): Target agent name
            context (ContextData): Context for handoff
            
        Returns:
            bool: Success status
        """
```

### Agent Base Classes

#### BaseAgent

Abstract base class for all agents.

```python
class BaseAgent(ABC):
    """
    Abstract base class for SingleAgent agents
    """
    
    def __init__(self, client: OpenAI, config: Dict[str, Any]):
        """
        Initialize agent with OpenAI client and configuration
        
        Args:
            client (OpenAI): OpenAI client instance
            config (Dict[str, Any]): Agent configuration
        """
    
    @abstractmethod
    def process_message(self, message: str, context: ContextData) -> AgentResponse:
        """
        Process user message and generate response
        
        Args:
            message (str): User input
            context (ContextData): Conversation context
            
        Returns:
            AgentResponse: Agent response
        """
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities
        
        Returns:
            List[str]: Capability descriptions
        """
    
    def can_handle_request(self, message: str, context: ContextData) -> float:
        """
        Determine if agent can handle the request
        
        Args:
            message (str): User message
            context (ContextData): Conversation context
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
```

#### CodeAgent

Implementation agent for coding tasks.

```python
class CodeAgent(BaseAgent):
    """
    Agent specialized in code implementation and technical tasks
    """
    
    def __init__(self, client: OpenAI, config: Dict[str, Any]):
        """
        Initialize Code Agent
        """
        super().__init__(client, config)
        self.tools = self._initialize_tools()
    
    def process_message(self, message: str, context: ContextData) -> AgentResponse:
        """
        Process implementation requests
        """
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a specific tool
        
        Args:
            tool_name (str): Name of tool to execute
            **kwargs: Tool parameters
            
        Returns:
            ToolResult: Tool execution result
        """
    
    def analyze_code(self, filepath: str) -> CodeAnalysis:
        """
        Analyze code file structure and complexity
        
        Args:
            filepath (str): Path to code file
            
        Returns:
            CodeAnalysis: Analysis results
        """
    
    def generate_tests(self, source_file: str, test_type: str = "unit") -> List[str]:
        """
        Generate test cases for source file
        
        Args:
            source_file (str): Source file path
            test_type (str): Type of tests to generate
            
        Returns:
            List[str]: Generated test file paths
        """
```

#### ArchitectAgent

Planning and design agent for system architecture.

```python
class ArchitectAgent(BaseAgent):
    """
    Agent specialized in system design and architectural planning
    """
    
    def __init__(self, client: OpenAI, config: Dict[str, Any]):
        """
        Initialize Architect Agent
        """
        super().__init__(client, config)
        self.design_patterns = self._load_design_patterns()
    
    def process_message(self, message: str, context: ContextData) -> AgentResponse:
        """
        Process architectural and design requests
        """
    
    def create_system_design(self, requirements: List[str]) -> SystemDesign:
        """
        Create system architecture design
        
        Args:
            requirements (List[str]): System requirements
            
        Returns:
            SystemDesign: Architecture design
        """
    
    def suggest_patterns(self, problem_domain: str) -> List[DesignPattern]:
        """
        Suggest design patterns for problem domain
        
        Args:
            problem_domain (str): Problem description
            
        Returns:
            List[DesignPattern]: Recommended patterns
        """
    
    def create_project_structure(self, project_type: str, language: str) -> ProjectStructure:
        """
        Create project directory structure
        
        Args:
            project_type (str): Type of project
            language (str): Programming language
            
        Returns:
            ProjectStructure: Project structure
        """
```

## Context Management APIs

### ContextData Class

Manages conversation context and entity tracking.

```python
class ContextData:
    """
    Container for conversation context and entity information
    """
    
    def __init__(self):
        """
        Initialize empty context
        """
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, List[Relationship]] = {}
        self.conversation_history: List[Message] = []
        self.current_focus: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def add_entity(self, text: str, label: str, confidence: float = 1.0) -> Entity:
        """
        Add entity to context
        
        Args:
            text (str): Entity text
            label (str): Entity label/type
            confidence (float): Recognition confidence
            
        Returns:
            Entity: Created entity object
        """
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """
        Get all entities of specific type
        
        Args:
            entity_type (str): Entity type to filter by
            
        Returns:
            List[Entity]: Matching entities
        """
    
    def add_relationship(self, source: str, relation: str, target: str) -> Relationship:
        """
        Add relationship between entities
        
        Args:
            source (str): Source entity
            relation (str): Relationship type
            target (str): Target entity
            
        Returns:
            Relationship: Created relationship
        """
    
    def find_related_entities(self, entity_text: str, max_depth: int = 2) -> List[Entity]:
        """
        Find entities related to given entity
        
        Args:
            entity_text (str): Source entity text
            max_depth (int): Maximum relationship depth
            
        Returns:
            List[Entity]: Related entities
        """
    
    def add_message(self, role: str, content: str, entities: List[str] = None) -> Message:
        """
        Add message to conversation history
        
        Args:
            role (str): Message role (user, assistant, system)
            content (str): Message content
            entities (List[str]): Associated entities
            
        Returns:
            Message: Created message object
        """
    
    def get_conversation_summary(self, last_n_messages: int = 10) -> str:
        """
        Get summary of recent conversation
        
        Args:
            last_n_messages (int): Number of recent messages
            
        Returns:
            str: Conversation summary
        """
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export context to dictionary
        
        Returns:
            Dict[str, Any]: Serialized context
        """
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextData':
        """
        Create context from dictionary
        
        Args:
            data (Dict[str, Any]): Serialized context data
            
        Returns:
            ContextData: Reconstructed context
        """
```

### Entity Class

Represents recognized entities in context.

```python
class Entity:
    """
    Represents a recognized entity in conversation context
    """
    
    def __init__(self, text: str, label: str, confidence: float = 1.0):
        """
        Initialize entity
        
        Args:
            text (str): Entity text
            label (str): Entity type/label
            confidence (float): Recognition confidence
        """
        self.text = text
        self.label = label
        self.confidence = confidence
        self.mentions = 1
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.context_mentions: List[str] = []
    
    def update_mention(self, context: str = None):
        """
        Update entity mention information
        
        Args:
            context (str): Context where entity was mentioned
        """
    
    def get_relevance_score(self) -> float:
        """
        Calculate entity relevance score
        
        Returns:
            float: Relevance score (0.0 to 1.0)
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to dictionary
        
        Returns:
            Dict[str, Any]: Entity data
        """
```

## Tools System APIs

### Tool Base Classes

#### BaseTool

Abstract base class for all tools.

```python
class BaseTool(ABC):
    """
    Abstract base class for SingleAgent tools
    """
    
    def __init__(self):
        """
        Initialize tool
        """
        self.name: str = ""
        self.description: str = ""
        self.parameters: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute tool with given parameters
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult: Execution result
        """
    
    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate tool parameters
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            bool: Validation result
        """
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for tool parameters
        
        Returns:
            Dict[str, Any]: Parameter schema
        """
```

#### ToolResult

Represents the result of tool execution.

```python
class ToolResult:
    """
    Represents the result of tool execution
    """
    
    def __init__(self, success: bool, data: Any = None, error: str = None):
        """
        Initialize tool result
        
        Args:
            success (bool): Execution success status
            data (Any): Result data
            error (str): Error message if failed
        """
        self.success = success
        self.data = data
        self.error = error
        self.execution_time: float = 0.0
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary
        
        Returns:
            Dict[str, Any]: Result data
        """
```

### Tool Registry

Manages available tools and their execution.

```python
class ToolRegistry:
    """
    Registry for managing and executing tools
    """
    
    def __init__(self):
        """
        Initialize tool registry
        """
        self._tools: Dict[str, BaseTool] = {}
        self._permissions: Dict[str, ToolPermissions] = {}
    
    def register_tool(self, name: str, tool: BaseTool) -> bool:
        """
        Register a tool in the registry
        
        Args:
            name (str): Tool name
            tool (BaseTool): Tool instance
            
        Returns:
            bool: Registration success
        """
    
    def unregister_tool(self, name: str) -> bool:
        """
        Remove tool from registry
        
        Args:
            name (str): Tool name
            
        Returns:
            bool: Removal success
        """
    
    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """
        Execute tool by name
        
        Args:
            name (str): Tool name
            **kwargs: Tool parameters
            
        Returns:
            ToolResult: Execution result
        """
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names
        
        Returns:
            List[str]: Tool names
        """
    
    def get_tool_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about a specific tool
        
        Args:
            name (str): Tool name
            
        Returns:
            Dict[str, Any]: Tool information
        """
```

## Response Types

### AgentResponse

Standard response format from agents.

```python
class AgentResponse:
    """
    Standard response format from SingleAgent agents
    """
    
    def __init__(self, content: str, agent_name: str, tools_used: List[str] = None):
        """
        Initialize agent response
        
        Args:
            content (str): Response content
            agent_name (str): Name of responding agent
            tools_used (List[str]): Tools used in response generation
        """
        self.content = content
        self.agent_name = agent_name
        self.tools_used = tools_used or []
        self.timestamp = datetime.now()
        self.context_updates: List[ContextUpdate] = []
        self.suggested_actions: List[str] = []
    
    def add_context_update(self, update: ContextUpdate):
        """
        Add context update to response
        
        Args:
            update (ContextUpdate): Context update
        """
    
    def add_suggested_action(self, action: str):
        """
        Add suggested action to response
        
        Args:
            action (str): Suggested action
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert response to dictionary
        
        Returns:
            Dict[str, Any]: Response data
        """
```

### CodeAnalysis

Results from code analysis operations.

```python
class CodeAnalysis:
    """
    Results from code analysis operations
    """
    
    def __init__(self, filepath: str):
        """
        Initialize code analysis
        
        Args:
            filepath (str): Analyzed file path
        """
        self.filepath = filepath
        self.language: str = ""
        self.lines_of_code: int = 0
        self.complexity_score: float = 0.0
        self.classes: List[ClassInfo] = []
        self.functions: List[FunctionInfo] = []
        self.imports: List[ImportInfo] = []
        self.dependencies: List[str] = []
        self.issues: List[CodeIssue] = []
    
    def get_complexity_rating(self) -> str:
        """
        Get human-readable complexity rating
        
        Returns:
            str: Complexity rating (low, medium, high)
        """
    
    def get_maintainability_score(self) -> float:
        """
        Calculate maintainability score
        
        Returns:
            float: Maintainability score (0.0 to 1.0)
        """
```

### SystemDesign

Architectural design representation.

```python
class SystemDesign:
    """
    Represents a system architecture design
    """
    
    def __init__(self, name: str):
        """
        Initialize system design
        
        Args:
            name (str): Design name
        """
        self.name = name
        self.description: str = ""
        self.components: List[Component] = []
        self.relationships: List[ComponentRelationship] = []
        self.patterns: List[DesignPattern] = []
        self.technologies: List[str] = []
        self.quality_attributes: Dict[str, str] = {}
    
    def add_component(self, component: Component):
        """
        Add component to design
        
        Args:
            component (Component): System component
        """
    
    def add_relationship(self, relationship: ComponentRelationship):
        """
        Add relationship between components
        
        Args:
            relationship (ComponentRelationship): Component relationship
        """
    
    def export_to_plantuml(self) -> str:
        """
        Export design as PlantUML diagram
        
        Returns:
            str: PlantUML diagram code
        """
    
    def export_to_mermaid(self) -> str:
        """
        Export design as Mermaid diagram
        
        Returns:
            str: Mermaid diagram code
        """
```

## Configuration APIs

### Configuration Classes

```python
class SingleAgentConfig:
    """
    Main configuration class for SingleAgent
    """
    
    def __init__(self):
        """
        Initialize configuration with defaults
        """
        self.openai_api_key: str = ""
        self.model_name: str = "gpt-4"
        self.max_tokens: int = 2000
        self.temperature: float = 0.7
        self.context_window: int = 1000
        self.enable_tools: bool = True
        self.log_level: str = "INFO"
        self.log_file: str = "singleagent.log"
    
    @classmethod
    def from_env(cls) -> 'SingleAgentConfig':
        """
        Create configuration from environment variables
        
        Returns:
            SingleAgentConfig: Configuration instance
        """
    
    @classmethod
    def from_file(cls, filepath: str) -> 'SingleAgentConfig':
        """
        Load configuration from file
        
        Args:
            filepath (str): Configuration file path
            
        Returns:
            SingleAgentConfig: Configuration instance
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Dict[str, Any]: Configuration data
        """
    
    def validate(self) -> List[str]:
        """
        Validate configuration
        
        Returns:
            List[str]: Validation errors
        """
```

## Exception Classes

### Custom Exceptions

```python
class SingleAgentError(Exception):
    """Base exception for SingleAgent errors"""
    pass

class AgentNotFoundError(SingleAgentError):
    """Raised when specified agent is not found"""
    pass

class ToolExecutionError(SingleAgentError):
    """Raised when tool execution fails"""
    pass

class InvalidParameterError(SingleAgentError):
    """Raised when invalid parameters are provided"""
    pass

class ContextError(SingleAgentError):
    """Raised when context operations fail"""
    pass

class ConfigurationError(SingleAgentError):
    """Raised when configuration is invalid"""
    pass

class OpenAIAPIError(SingleAgentError):
    """Raised when OpenAI API calls fail"""
    pass
```

## Utility Functions

### Helper Functions

```python
def load_spacy_model(model_name: str = "en_core_web_sm") -> spacy.Language:
    """
    Load SpaCy language model
    
    Args:
        model_name (str): SpaCy model name
        
    Returns:
        spacy.Language: Loaded model
    """

def extract_entities(text: str, nlp: spacy.Language) -> List[Entity]:
    """
    Extract entities from text using SpaCy
    
    Args:
        text (str): Input text
        nlp (spacy.Language): SpaCy model
        
    Returns:
        List[Entity]: Extracted entities
    """

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts
    
    Args:
        text1 (str): First text
        text2 (str): Second text
        
    Returns:
        float: Similarity score (0.0 to 1.0)
    """

def format_code_response(code: str, language: str = "python") -> str:
    """
    Format code response with syntax highlighting
    
    Args:
        code (str): Code content
        language (str): Programming language
        
    Returns:
        str: Formatted code
    """

def validate_file_path(filepath: str, allowed_extensions: List[str] = None) -> bool:
    """
    Validate file path for security
    
    Args:
        filepath (str): File path to validate
        allowed_extensions (List[str]): Allowed file extensions
        
    Returns:
        bool: Validation result
    """
```

## Type Definitions

### Type Aliases

```python
from typing import Dict, List, Any, Optional, Union, Callable

# Common type aliases
ConfigDict = Dict[str, Any]
ParameterDict = Dict[str, Any]
EntityDict = Dict[str, Entity]
ToolFunction = Callable[..., ToolResult]
AgentCapabilities = List[str]
MessageHistory = List[Message]
EntityRelationships = Dict[str, List[Relationship]]

# Response types
AgentResponseData = Dict[str, Any]
ToolResultData = Dict[str, Any]
AnalysisResult = Union[CodeAnalysis, SystemDesign]
```

### Enums

```python
from enum import Enum

class AgentType(Enum):
    """Agent type enumeration"""
    CODE_AGENT = "code_agent"
    ARCHITECT_AGENT = "architect_agent"

class EntityType(Enum):
    """Entity type enumeration"""
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "GPE"
    PRODUCT = "PRODUCT"
    TECHNOLOGY = "TECH"
    FEATURE = "FEATURE"
    BUG = "BUG"
    TASK = "TASK"

class ToolCategory(Enum):
    """Tool category enumeration"""
    FILE_SYSTEM = "file_system"
    CODE_ANALYSIS = "code_analysis"
    SYSTEM = "system"
    DATABASE = "database"
    WEB = "web"
    TESTING = "testing"
    DOCUMENTATION = "documentation"

class LogLevel(Enum):
    """Logging level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
```

---

*For implementation examples and usage patterns, see [Examples](examples.md) and [Tools Reference](tools.md).*
