# SingleAgent: Technische Documentatie

## Overzicht

SingleAgent is een geavanceerde implementatie van een multi-agent systeem gebouwd bovenop de [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). Het project demonstreert hoe je de SDK kernprimitieven kunt gebruiken om een productiewaardige agent applicatie te bouwen met rijke context management, tool integratie en dual-agent orchestratie.

Voor achtergrond informatie over de onderliggende OpenAI Agents SDK, zie de [officiële documentatie](./openai_agents_sdk_docs/index.md).

## Architectuur

### Kern Componenten

Het SingleAgent systeem is georganiseerd rond drie hoofdcomponenten:

1. **The_Agents/**: Agent implementaties
2. **Tools/**: Tool definities en functionaliteiten 
3. **utilities/**: Hulpfuncties en shared utilities

### Agent Hiërarchie

```
SingleAgent System
├── SingleAgent (Code Agent)
│   ├── Context Management
│   ├── Entity Recognition
│   └── Code Tools
└── ArchitectAgent (Architecture Agent)
    ├── System Design Tools
    ├── Documentation Tools
    └── Planning Tools
```

## Agent Implementaties

### SingleAgent (Code Agent)

**Locatie**: `The_Agents/SingleAgent.py`

De `SingleAgent` klasse implementeert een gespecialiseerde code assistent die gebruik maakt van de OpenAI Agents SDK principes:

#### Kernfunctionaliteiten

1. **Enhanced Context Management**: 
   - Tiktoken-gebaseerde token counting
   - Entity tracking via spaCy NLP
   - Context summarization
   - Persistent storage tussen sessies

2. **Agent Loop Integration**:
   - Gebruikt de SDK's ingebouwde agent loop zoals beschreven in [agents.md](./openai_agents_sdk_docs/agents.md)
   - Handelt tool calls automatisch af
   - Loopt tot de LLM klaar is

3. **Tools Integration**:
   - Function tools voor code operaties (zie [tools.md](./openai_agents_sdk_docs/tools.md))
   - Custom tools voor file operations, command execution
   - Automatische schema generatie via Pydantic

#### Code Voorbeeld

```python
from The_Agents.SingleAgent import SingleAgent
from utilities.tool_usage import handle_stream_events

# Initialiseer de agent
agent = SingleAgent()

# Voer een query uit
response = await agent.run_query_streaming(
    "Write a Python function to calculate fibonacci numbers",
    handle_stream_events
)
```

### ArchitectAgent

**Locatie**: `The_Agents/ArchitectAgent.py`

Een gespecialiseerde agent voor system design en architectuur taken, volgt hetzelfde patroon als SingleAgent maar met focus op:
- System design tools
- Documentation generation
- High-level planning

## Tools Systeem

Het tools systeem volgt de OpenAI Agents SDK [tools specificaties](./openai_agents_sdk_docs/tools.md):

### Tool Categorieën

#### 1. Shared Tools (`Tools/shared_tools.py`)

Basis functionaliteiten gedeeld tussen agents:

```python
@function_tool
async def read_file(ctx: RunContextWrapper[Any], params: FileReadParams) -> str:
    """Read the contents of a file."""
    # Implementatie volgt SDK function tool patroon
```

#### 2. SingleAgent Tools (`Tools/singleagent_tools.py`)

Code-specifieke tools:

```python
@function_tool
async def write_file(ctx: RunContextWrapper[Any], params: WriteFileParams) -> str:
    """Write content to a file with safety checks."""
    # Gebruikt SDK's automatische schema generatie
```

#### 3. Architect Tools (`Tools/architect_tools.py`)

Architecture-specifieke tools voor system design.

### Tool Implementation Pattern

Alle tools volgen het SDK patroon:

1. **Pydantic Models** voor parameter validatie
2. **@function_tool decorator** voor automatische registratie
3. **RunContextWrapper** voor context toegang
4. **Automatische schema generatie** van function signatures

```python
from agents import function_tool, RunContextWrapper
from pydantic import BaseModel, Field

class ToolParams(BaseModel):
    param1: str = Field(description="Description for param1")
    param2: Optional[int] = Field(default=None, description="Optional parameter")

@function_tool
async def my_tool(ctx: RunContextWrapper[Any], params: ToolParams) -> str:
    """Tool description extracted from docstring."""
    # Tool implementatie
    return "result"
```

## Context Management

### Enhanced Context Data

**Locatie**: `The_Agents/context_data.py`

Implementeert geavanceerd context management bovenop de SDK basis:

#### Features

1. **Token Counting**: Gebruik van tiktoken voor accurate token tracking
2. **Entity Recognition**: spaCy NLP voor entity extraction
3. **Context Summarization**: Automatische context compression
4. **Persistent Storage**: Context opslag tussen sessies

#### Code Voorbeeld

```python
from The_Agents.context_data import EnhancedContextData

context = EnhancedContextData()
context.add_entry("user", "Implement a REST API", {"entities": ["API", "REST"]})
summary = context.get_context_summary()
```

### SpaCy Integration

**Locatie**: `The_Agents/spacy_singleton.py`

Singleton pattern voor efficiënte NLP model initialisatie:

```python
from The_Agents.spacy_singleton import nlp_singleton

# Async initialisatie
await nlp_singleton.initialize(model_name="en_core_web_lg")

# Gebruik in tools
entities = nlp_singleton.extract_entities(text)
```

## Multi-Agent Orchestratie

### Mode Switching

**Locatie**: `main.py`

Het systeem ondersteunt dynamische switching tussen agents:

```python
# Switch naar Code Agent
current_mode = AgentMode.CODE
agent = code_agent

# Switch naar Architect Agent  
current_mode = AgentMode.ARCHITECT
agent = architect_agent
```

### Handoffs

Hoewel handoffs een kernfeature zijn van de SDK (zie [handoffs.md](./openai_agents_sdk_docs/handoffs.md)), gebruikt SingleAgent momenteel mode switching in plaats van echte handoffs. Een toekomstige verbetering zou zijn:

```python
# Potentiële handoff implementatie
from agents import Agent, handoff_to

architect_agent = Agent(
    name="Architect",
    instructions="You are a system architect...",
)

code_agent = Agent(
    name="Coder", 
    instructions="You are a coding assistant...",
    tools=[handoff_to(architect_agent)]
)
```

## Streaming en Event Handling

### Stream Events

**Locatie**: `utilities/tool_usage.py`

Implementeert event handling voor streaming responses:

```python
async def handle_stream_events(event):
    """Handle streaming events from the agent."""
    if event.type == "text_delta":
        print(event.text, end="", flush=True)
    elif event.type == "tool_call_start":
        print(f"\n[Using tool: {event.tool_name}]")
```

## Configuratie en Setup

### Dependencies

Het project vereist:
- `openai-agents`: Core SDK
- `spacy`: NLP processing
- `tiktoken`: Token counting
- `prompt_toolkit`: Enhanced CLI interface
- `pydantic`: Data validation

### Environment Setup

```bash
# Installeer dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg

# Set OpenAI API key
export OPENAI_API_KEY=sk-your-key-here
```

## Best Practices & Patterns

### 1. Tool Design

Volg de SDK patterns:
- Gebruik Pydantic models voor type safety
- Documenteer tools via docstrings
- Implement async functions voor I/O operaties

### 2. Context Management

- Track entities voor betere context awareness
- Gebruik token counting voor efficiency
- Implement context compression voor lange sessies

### 3. Error Handling

```python
try:
    result = await agent.run_query(query)
except Exception as e:
    logger.error(f"Agent error: {e}")
    # Graceful fallback
```

### 4. Logging

Gebruik structured logging voor debugging:

```python
import logging
logger = logging.getLogger(__name__)
logger.info(json.dumps({
    "event": "tool_execution",
    "tool": tool_name,
    "params": params
}))
```

## Tracing en Monitoring

Het project is voorbereid voor de SDK's ingebouwde tracing capabilities (zie [tracing documentatie](./openai_agents_sdk_docs/tracing.md)):

```python
# Toekomstige tracing integratie
from agents import Runner

result = await Runner.run(
    agent=agent,
    messages=messages,
    trace=True  # Enable tracing
)
```

## Testing

### Test Structuur

```
tests/
├── test_agents.py        # Agent behavior tests
├── test_tools.py         # Tool functionality tests
└── test_context.py       # Context management tests
```

### Example Test

```python
import pytest
from The_Agents.SingleAgent import SingleAgent

@pytest.mark.asyncio
async def test_agent_code_generation():
    agent = SingleAgent()
    response = await agent.run_query("Write a hello world function")
    assert "def" in response.lower()
```

## Extensies en Uitbreidingen

### Nieuwe Tools Toevoegen

1. Definieer Pydantic model voor parameters
2. Implementeer async function met @function_tool decorator
3. Voeg toe aan agent's tools lijst

### Nieuwe Agents Toevoegen

1. Extend base agent pattern
2. Definieer specifieke tools set
3. Implement in main.py orchestratie

### Guardrails Integration

Voor toekomstige uitbreiding met SDK guardrails:

```python
from agents import Agent, Guardrail

input_guardrail = Guardrail(
    name="input_validator",
    # Guardrail implementation
)

agent = Agent(
    name="SafeAgent",
    guardrails=[input_guardrail]
)
```

## Conclusie

SingleAgent demonstreert een robuuste implementatie van de OpenAI Agents SDK principes met:

- **Agent Loop**: Automatische tool calling en iteration
- **Function Tools**: Python functions als tools met automatische schema generatie  
- **Context Management**: Geavanceerde context tracking en persistence
- **Multi-Agent Orchestration**: Mode switching tussen gespecialiseerde agents
- **Streaming**: Real-time response handling

Het project toont hoe de SDK's minimale abstractions gebruikt kunnen worden om complexe, productie-waardige agent applicaties te bouwen terwijl de Python-first filosofie behouden blijft.

Voor verdere details over de onderliggende SDK capabilities, raadpleeg de [OpenAI Agents SDK documentatie](./openai_agents_sdk_docs/).
