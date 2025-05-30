# Context Management

SingleAgent features a sophisticated context management system that tracks entities, maintains conversation history, and provides intelligent context switching between agents.

## Overview

The context management system is built on several key components:

- **Entity Recognition**: SpaCy-powered NLP for identifying and tracking entities
- **Context Data**: Structured storage of conversation context and entity relationships
- **Intelligent Handoffs**: Context-aware agent switching
- **Memory Management**: Efficient handling of long conversations

## Entity Recognition

### SpaCy Integration

SingleAgent uses SpaCy for advanced natural language processing and entity recognition:

```python
# Entity recognition example
entities = entity_recognizer.extract_entities(user_message)
for entity in entities:
    print(f"Entity: {entity.text}, Label: {entity.label_}")
```

### Supported Entity Types

The system recognizes various entity types:

- **PERSON**: Names of people
- **ORG**: Organizations and companies
- **GPE**: Geopolitical entities (countries, cities)
- **PRODUCT**: Products and services
- **EVENT**: Named events
- **DATE**: Dates and time expressions
- **MONEY**: Monetary values
- **PERCENT**: Percentages

### Custom Entity Recognition

You can extend entity recognition for domain-specific needs:

```python
# Custom entity patterns
custom_patterns = [
    {"label": "PROJECT", "pattern": [{"LOWER": "project"}, {"IS_ALPHA": True}]},
    {"label": "API_KEY", "pattern": [{"LIKE_NUM": True, "LENGTH": 32}]}
]
```

## Context Data Structure

### Core Components

The context system maintains several data structures:

```python
class ContextData:
    def __init__(self):
        self.entities = {}          # Tracked entities
        self.relationships = {}     # Entity relationships
        self.conversation_history = []  # Message history
        self.current_focus = None   # Current conversation focus
        self.metadata = {}          # Additional context metadata
```

### Entity Tracking

Entities are tracked with rich metadata:

```python
entity_data = {
    "text": "OpenAI",
    "label": "ORG",
    "confidence": 0.95,
    "mentions": 3,
    "context": ["API integration", "model selection"],
    "relationships": ["develops GPT-4", "provides AI services"]
}
```

### Conversation History

The system maintains structured conversation history:

```python
message_entry = {
    "timestamp": datetime.now(),
    "agent": "code_agent",
    "user_message": "Implement user authentication",
    "agent_response": "I'll help you implement authentication...",
    "entities": ["authentication", "user", "security"],
    "tools_used": ["file_creator", "code_analyzer"]
}
```

## Context-Aware Handoffs

### Intelligent Agent Selection

The system determines the most appropriate agent based on context:

```python
def determine_agent(message, context):
    """
    Analyze message and context to select appropriate agent
    """
    if is_architectural_query(message, context):
        return "architect_agent"
    elif is_implementation_task(message, context):
        return "code_agent"
    else:
        return "current_agent"  # Continue with current agent
```

### Handoff Criteria

Agent handoffs are triggered by:

- **Task Type Changes**: From planning to implementation
- **Complexity Shifts**: From simple to complex tasks
- **Domain Expertise**: Specialized knowledge requirements
- **User Explicit Requests**: Direct agent specification

### Context Preservation

During handoffs, context is preserved and transferred:

```python
handoff_context = {
    "previous_agent": "architect_agent",
    "task_summary": "Designed authentication system",
    "key_decisions": ["JWT tokens", "bcrypt hashing"],
    "next_steps": ["Implement login endpoint", "Add middleware"],
    "relevant_entities": ["authentication", "JWT", "bcrypt"]
}
```

## Memory Management

### Conversation Pruning

To manage memory efficiently, the system prunes old conversations:

```python
def prune_conversation_history(max_messages=100, max_age_days=30):
    """
    Remove old messages while preserving important context
    """
    # Keep recent messages
    # Preserve messages with high entity relevance
    # Remove routine interactions
```

### Entity Relevance Scoring

Entities are scored for relevance to maintain focus:

```python
def calculate_entity_relevance(entity, context):
    """
    Score entity relevance based on:
    - Mention frequency
    - Recency of mentions
    - Relationship strength
    - Task importance
    """
    relevance_score = (
        frequency_weight * entity.mention_count +
        recency_weight * entity.last_mention_score +
        relationship_weight * entity.relationship_strength
    )
    return relevance_score
```

### Context Compression

For long conversations, context is compressed intelligently:

```python
def compress_context(conversation_history):
    """
    Compress conversation while preserving key information
    """
    # Extract key decisions and outcomes
    # Summarize repetitive interactions
    # Maintain entity relationships
    # Preserve error resolutions
```

## Context API

### Basic Usage

```python
from context_data import ContextData

# Initialize context
context = ContextData()

# Add entity
context.add_entity("user_authentication", "FEATURE", confidence=0.9)

# Track relationship
context.add_relationship("user_authentication", "implements", "JWT_tokens")

# Update conversation
context.add_message("user", "How do I secure the API?", entities=["API", "security"])
```

### Advanced Features

```python
# Query entities by type
auth_entities = context.get_entities_by_type("SECURITY")

# Find related entities
related = context.find_related_entities("authentication", max_depth=2)

# Get conversation summary
summary = context.get_conversation_summary(last_n_messages=10)

# Export context
context_export = context.export_to_dict()
```

## Configuration

### SpaCy Model Settings

Configure the SpaCy model for your use case:

```python
# config.py
SPACY_CONFIG = {
    "model": "en_core_web_sm",  # or en_core_web_md, en_core_web_lg
    "disable": [],  # Components to disable for performance
    "custom_entities": True,  # Enable custom entity recognition
    "max_length": 1000000  # Maximum text length
}
```

### Context Settings

Adjust context management parameters:

```python
CONTEXT_CONFIG = {
    "max_entities": 1000,
    "max_conversation_length": 100,
    "entity_relevance_threshold": 0.3,
    "auto_prune_enabled": True,
    "prune_interval_messages": 50
}
```

## Best Practices

### Entity Management

1. **Regular Pruning**: Remove irrelevant entities periodically
2. **Relevance Scoring**: Maintain entity relevance scores
3. **Relationship Tracking**: Monitor entity relationships
4. **Custom Entities**: Define domain-specific entity types

### Context Optimization

1. **Selective History**: Keep only relevant conversation history
2. **Compression**: Compress old context intelligently
3. **Focus Management**: Maintain clear conversation focus
4. **Handoff Timing**: Optimize agent handoff timing

### Performance Tips

1. **Model Selection**: Choose appropriate SpaCy model size
2. **Batch Processing**: Process multiple messages together
3. **Caching**: Cache entity recognition results
4. **Incremental Updates**: Update context incrementally

## Troubleshooting

### Common Issues

**High Memory Usage**
- Enable automatic pruning
- Reduce max conversation length
- Use smaller SpaCy model

**Slow Entity Recognition**
- Disable unused SpaCy components
- Reduce text length before processing
- Use batch processing for multiple texts

**Poor Context Relevance**
- Adjust relevance thresholds
- Review entity relationship rules
- Update custom entity patterns

### Debugging Tools

```python
# Debug entity recognition
def debug_entities(text):
    entities = entity_recognizer.extract_entities(text)
    for entity in entities:
        print(f"{entity.text} -> {entity.label_} ({entity.confidence})")

# Debug context state
def debug_context(context):
    print(f"Entities: {len(context.entities)}")
    print(f"Messages: {len(context.conversation_history)}")
    print(f"Focus: {context.current_focus}")
```

## Integration Examples

### With Code Agent

```python
# Code Agent using context
def code_agent_with_context(message, context):
    # Extract relevant entities
    entities = context.get_entities_by_type(["FUNCTION", "CLASS", "FILE"])
    
    # Use context for better responses
    if "refactor" in message and entities:
        return f"I'll refactor the {entities[0].text} considering the current context..."
```

### With Architect Agent

```python
# Architect Agent using context
def architect_agent_with_context(message, context):
    # Analyze architectural entities
    arch_entities = context.get_entities_by_type(["SYSTEM", "COMPONENT", "PATTERN"])
    
    # Make context-aware architectural decisions
    if arch_entities:
        return f"Based on the current architecture ({arch_entities}), I recommend..."
```

---

*For more information, see [Architecture](architecture.md) and [Tools Reference](tools.md).*
