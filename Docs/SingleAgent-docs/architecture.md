# Architecture Overview

This document provides a comprehensive overview of SingleAgent's architecture, design principles, and system components.

## System Architecture

SingleAgent is built on a dual-agent architecture that combines specialized AI agents with advanced context management and tool integration.

```
┌─────────────────────────────────────────────────────────────┐
│                    SingleAgent System                       │
├─────────────────────────────────────────────────────────────┤
│                  Interactive CLI Interface                  │
│                  (prompt_toolkit based)                     │
├─────────────────────────────────────────────────────────────┤
│                   Agent Orchestrator                        │
│                     (main.py)                              │
├──────────────────────┬──────────────────────────────────────┤
│    Code Agent        │       Architect Agent               │
│  (SingleAgent.py)    │    (ArchitectAgent.py)             │
├──────────────────────┼──────────────────────────────────────┤
│   Code Tools         │     Architect Tools                 │
│ (tools_single_agent) │   (architect_tools)                 │
├──────────────────────┴──────────────────────────────────────┤
│                 Context Management System                   │
│                   (context_data.py)                        │
├─────────────────────────────────────────────────────────────┤
│                OpenAI Agents SDK Integration                │
│                     (agents/ directory)                     │
├─────────────────────────────────────────────────────────────┤
│              External Dependencies & Services               │
│          OpenAI GPT-4 • SpaCy NLP • File System           │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent Orchestrator (`main.py`)

The central coordinator that manages:
- Agent switching and lifecycle
- CLI interface and user interactions
- Context persistence and loading
- Error handling and recovery
- Streaming output management

**Key Features:**
- Seamless agent switching with `!code` and `!architect` commands
- Rich interactive CLI with history and auto-suggestions
- Automatic context saving and restoration
- Graceful error handling and recovery

### 2. Dual-Agent System

#### Code Agent (`SingleAgent.py`)
Specialized for implementation and code-related tasks:

**Capabilities:**
- Code analysis and review
- File operations and manipulation
- Debugging and testing
- Implementation of features
- Code optimization and refactoring

**Design Principles:**
- Direct, actionable responses
- Focus on concrete implementation
- Detailed code explanations
- Practical problem-solving

#### Architect Agent (`ArchitectAgent.py`)
Specialized for high-level design and architecture:

**Capabilities:**
- System architecture design
- Technology stack recommendations
- Design pattern suggestions
- Project structure planning
- High-level problem solving

**Design Principles:**
- Strategic thinking
- Long-term considerations
- Best practice recommendations
- Scalability and maintainability focus

### 3. Context Management System (`context_data.py`)

Advanced context handling with multiple layers:

```
Context Management Architecture:
┌─────────────────────────────────────┐
│           Context Manager           │
├─────────────────────────────────────┤
│  Entity Tracker (SpaCy NLP)        │
│  - Named Entity Recognition         │
│  - Relationship Mapping             │
│  - Semantic Understanding           │
├─────────────────────────────────────┤
│  Persistent Storage                 │
│  - JSON-based storage               │
│  - Hierarchical organization        │
│  - Version tracking                 │
├─────────────────────────────────────┤
│  Context Retrieval                  │
│  - Relevance scoring                │
│  - Smart filtering                  │
│  - Contextual suggestions           │
└─────────────────────────────────────┘
```

**Key Features:**
- **Entity Recognition**: SpaCy-powered NLP for identifying and tracking entities
- **Persistent Storage**: JSON-based context storage with hierarchical organization
- **Smart Retrieval**: Relevance-based context retrieval and filtering
- **Manual Context**: Support for user-added context information

### 4. Tool Systems

#### Code Agent Tools (`tools_single_agent.py`)
Comprehensive toolset for development tasks:

- **File Operations**: Read, write, create, delete, move files
- **Code Analysis**: Syntax checking, structure analysis, dependency mapping
- **Search Capabilities**: Content search, pattern matching, grep-like functionality
- **Execution Tools**: Code execution, testing, compilation
- **Integration Tools**: Git operations, package management

#### Architect Tools (`architect_tools.py`)
Strategic planning and design tools:

- **Architecture Analysis**: System design evaluation, pattern identification
- **Documentation Tools**: Architecture documentation, diagram generation
- **Planning Tools**: Project planning, milestone setting, roadmap creation
- **Research Tools**: Technology evaluation, best practice research
- **Design Tools**: UML generation, system modeling

### 5. OpenAI Agents SDK Integration

Built on the OpenAI Agents SDK for advanced AI capabilities:

**Integration Points:**
- **Agent Configuration**: Custom agent definitions and behaviors
- **Tool Integration**: Seamless tool calling and response handling
- **Streaming**: Real-time response streaming for better UX
- **Error Handling**: Robust error handling and recovery mechanisms

**SDK Features Utilized:**
- GPT-4 model integration
- Function calling capabilities
- Conversation threading
- Response formatting

## Design Principles

### 1. Separation of Concerns

Each component has a specific responsibility:
- **Agents**: Domain-specific intelligence and reasoning
- **Tools**: Concrete action execution
- **Context**: Information persistence and retrieval
- **CLI**: User interaction and experience

### 2. Modularity

The system is designed with modular components:
- **Pluggable Tools**: Easy to add new capabilities
- **Extensible Agents**: Simple to create new specialized agents
- **Configurable Context**: Flexible context management strategies
- **Interchangeable Components**: Clean interfaces between components

### 3. Context Awareness

Every component is context-aware:
- **Agents**: Use context to inform responses
- **Tools**: Access context for enhanced functionality
- **CLI**: Provides context visibility and management
- **Storage**: Maintains context integrity across sessions

### 4. User Experience

Designed for developer productivity:
- **Intuitive Commands**: Simple, memorable command structure
- **Rich Feedback**: Detailed progress and status information
- **Error Recovery**: Graceful handling of errors and edge cases
- **Customization**: Configurable behavior and preferences

## Data Flow

### 1. User Input Processing

```
User Input → CLI Parser → Command Router → Agent Selector → Context Loader
```

### 2. Agent Processing

```
Context + Input → Agent Reasoning → Tool Selection → Tool Execution → Response Generation
```

### 3. Context Updates

```
Agent Response → Entity Extraction → Context Updates → Persistence → Context Indexing
```

### 4. Output Delivery

```
Response → Formatting → Streaming → CLI Display → History Recording
```

## Performance Considerations

### 1. Context Management

- **Lazy Loading**: Context loaded on demand
- **Intelligent Caching**: Frequently accessed context cached in memory
- **Incremental Updates**: Only changed context persisted
- **Compression**: Large context compressed for storage

### 2. Agent Switching

- **State Preservation**: Agent state maintained during switches
- **Fast Initialization**: Agents initialized lazily
- **Context Transfer**: Seamless context transfer between agents
- **Memory Management**: Efficient memory usage across agents

### 3. Tool Execution

- **Parallel Execution**: Independent tools run in parallel
- **Resource Management**: Tool resource usage monitored
- **Caching**: Tool results cached when appropriate
- **Error Isolation**: Tool failures don't affect system stability

## Security Considerations

### 1. API Key Management

- **Environment Variables**: Secure API key storage
- **No Logging**: API keys never logged or persisted
- **Validation**: API key format validation
- **Rotation Support**: Easy API key rotation

### 2. File System Access

- **Sandboxing**: Tool file access limited to project directories
- **Permission Checks**: File operation permissions validated
- **Path Validation**: File paths sanitized and validated
- **Backup Protection**: Critical files protected from accidental deletion

### 3. Code Execution

- **Controlled Environment**: Code execution in controlled context
- **Resource Limits**: Execution time and resource limits
- **Isolation**: Execution isolated from main system
- **Validation**: Code validated before execution

## Extensibility

### 1. Adding New Tools

Tools can be easily added by:
1. Creating tool functions with proper signatures
2. Adding tool descriptions and metadata
3. Registering tools with appropriate agents
4. Testing tool integration

### 2. Creating New Agents

New agents can be created by:
1. Inheriting from base agent classes
2. Defining agent-specific tools and behaviors
3. Implementing context handling
4. Integrating with the agent orchestrator

### 3. Customizing Context

Context behavior can be customized through:
1. Custom entity recognition patterns
2. Context storage backends
3. Retrieval and ranking algorithms
4. Context lifecycle management

## Integration Points

### 1. External Services

- **OpenAI API**: Core AI capabilities
- **File System**: Project file access
- **Git**: Version control integration
- **Package Managers**: Dependency management

### 2. Development Tools

- **IDEs**: Integration possibilities with popular IDEs
- **CI/CD**: Potential CI/CD pipeline integration
- **Testing Frameworks**: Test execution and analysis
- **Documentation Tools**: Documentation generation and maintenance

### 3. Monitoring and Logging

- **Usage Analytics**: Usage pattern tracking
- **Performance Metrics**: Response time and resource usage
- **Error Tracking**: Error frequency and patterns
- **Context Analytics**: Context effectiveness measurement

## Future Architecture Considerations

### 1. Scalability

- **Multi-user Support**: Supporting multiple concurrent users
- **Distributed Architecture**: Scaling across multiple machines
- **Cloud Integration**: Cloud-native deployment options
- **Load Balancing**: Request distribution and management

### 2. Advanced Features

- **Multi-modal Input**: Support for images, audio, and other inputs
- **Real-time Collaboration**: Multiple users working on same project
- **Advanced Analytics**: Deep insights into development patterns
- **Machine Learning**: Custom model training on user data

### 3. Integration Ecosystem

- **Plugin Architecture**: Third-party plugin support
- **API Exposure**: RESTful API for external integrations
- **Webhook Support**: Event-driven integrations
- **Marketplace**: Community-driven tool and agent sharing

This architecture provides a solid foundation for intelligent development assistance while maintaining flexibility for future enhancements and customizations.
