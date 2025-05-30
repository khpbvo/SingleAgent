# Installation

This page contains detailed installation instructions for SingleAgent on different platforms.

## System Requirements

### Hardware
- **RAM**: Minimum 4GB, recommended 8GB+ (for spaCy model)
- **Disk Space**: Approximately 500MB for all dependencies
- **CPU**: No specific requirements

### Software
- **Python**: 3.8 or higher (3.9+ recommended)
- **pip**: For package management
- **Internet**: For OpenAI API calls and package downloads

## Platform-Specific Instructions

### macOS

```bash
# Check Python version
python3 --version

# Install Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update pip
python3 -m pip install --upgrade pip

# Clone/download the project
# Navigate to the project directory

# Install requirements
pip3 install -r requirements.txt

# Download spaCy model
python3 -m spacy download en_core_web_lg
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python and pip (if not present)
sudo apt install python3 python3-pip python3-venv

# Check version
python3 --version

# Clone/download the project
# Navigate to the project directory

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg
```

### Windows

```cmd
REM Check Python version
python --version

REM Navigate to project directory
cd path\to\your\project

REM Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

REM Install requirements
pip install -r requirements.txt

REM Download spaCy model
python -m spacy download en_core_web_lg
```

## Virtual Environment Setup (Recommended)

It's strongly recommended to use a virtual environment:

### Why Virtual Environment?
- Prevents conflicts with other Python projects
- Keeps dependencies organized
- Easier to manage different versions

### Setup

```bash
# Create virtual environment
python -m venv singleagent-env

# Activeer (macOS/Linux)
source singleagent-env/bin/activate

# Activeer (Windows)
singleagent-env\Scripts\activate

# Installeer dependencies
pip install -r requirements.txt

# Deactiveer wanneer klaar
deactivate
```

## Package Dependencies Uitleg

Hier is wat elke dependency doet:

### Core Dependencies

```python
openai                  # OpenAI API client for LLM calls
prompt_toolkit         # Geavanceerde CLI interface with history
pydantic              # Data validatie and serialisatie
tiktoken              # Token counting for OpenAI models
```

### Advanced Features

```python
spacy                 # Natural Language Processing for entity extraction
networkx              # Graph analysis for dependency mapping
typing_extensions     # Extended type hints ondersteuning
toml                  # TOML configuration file parsing
```

### Development Tools

```python
ruff                  # Python linter and formatter (vervanger for flake8)
pylint                # Uitgebreide Python code analysis
pyright               # Static type checker of Microsoft
```

## OpenAI API Setup

### API Key verkrijgen

1. Ga to [OpenAI Platform](https://platform.openai.com)
2. Log in or maak a account
3. Navigeer to API keys sectie
4. Genereer a nieuwe API key
5. Bewaar deze veilig!

### API Key Configureren

#### Methode 1: Environment Variable (Aanbevolen)

```bash
# macOS/Linux - voeg toe aan ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY=sk-your-api-key-here

# Windows - voeg toe aan environment variables
set OPENAI_API_KEY=sk-your-api-key-here
```

#### Methode 2: .env File

Create a `.env` bestand in the project root:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

**Waarschuwing**: Voeg `.env` toe aan je `.gitignore`!

### API Gebruik Monitoring

- Monitor je usage on [OpenAI Platform](https://platform.openai.com/usage)
- Stel usage limits in as gewenst
- SingleAgent used standaard GPT-4.1

## SpaCy Model Setup

### Standaard Model (Aanbevolen)

```bash
# Download large English model (beste accuracy)
python -m spacy download en_core_web_lg
```

### Alternatieve Models

```bash
# Medium model (balans tussen grootte and accuracy)
python -m spacy download en_core_web_md

# Small model (snelste, minder accurate)
python -m spacy download en_core_web_sm
```

### Model Selectie Aanpassen

In `The_Agents/spacy_singleton.py` kun je the model wijzigen:

```python
# Wijzig deze regel for a ander model
await nlp_singleton.initialize(model_name="en_core_web_md", disable=["parser"])
```

## Verificatie of Installatie

Test or alles correct geïnstalleerd is:

### 1. Python Environment Test

```bash
python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import openai, prompt_toolkit, pydantic, tiktoken, spacy, networkx
    print('✓ All core packages imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
"
```

### 2. SpaCy Model Test

```bash
python -c "
import spacy
try:
    nlp = spacy.load('en_core_web_lg')
    print('✓ SpaCy model loaded successfully')
except OSError:
    print('✗ SpaCy model not found - run: python -m spacy download en_core_web_lg')
"
```

### 3. OpenAI API Test

```bash
python -c "
import os
from openai import OpenAI

if 'OPENAI_API_KEY' in os.environ:
    print('✓ OpenAI API key found')
    try:
        client = OpenAI()
        print('✓ OpenAI client initialized')
    except Exception as e:
        print(f'✗ OpenAI client error: {e}')
else:
    print('✗ OPENAI_API_KEY environment variable not set')
"
```

### 4. Volledige Systeem Test

```bash
# Start SingleAgent in test mode
python -c "
from The_Agents.SingleAgent import SingleAgent
from The_Agents.ArchitectAgent import ArchitectAgent

try:
    code_agent = SingleAgent()
    arch_agent = ArchitectAgent()
    print('✓ Both agents initialized successfully')
    print('Ready to start main.py!')
except Exception as e:
    print(f'✗ Agent initialization error: {e}')
"
```

## Troubleshooting Installatie

### Veel voorkomende problemen

#### "No module named 'agents'"
```bash
# Zorg that je in the juiste directory bent
ls -la  # Moet agents/ directory bevatten

# Herinstalleer requirements
pip install -r requirements.txt --force-reinstall
```

#### SpaCy SSL Certificaat Errors
```bash
# macOS fix
/Applications/Python\ 3.x/Install\ Certificates.command

# Alternatief: download handmatig
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1-py3-none-any.whl
```

#### Windows Path Issues
- Gebruik forward slashes `/` in plaats of backslashes `\`
- Activeer virtual environment for elke nieuwe terminal sessie
- Controleer PATH environment variable

#### Permission Errors (Linux/macOS)
```bash
# Gebruik --user flag
pip install --user -r requirements.txt

# Of gebruik sudo (niet aanbevolen)
sudo pip install -r requirements.txt
```

### Performance Optimalisatie

#### Voor Snellere Startup
```python
# In spacy_singleton.py, disable meer components:
await nlp_singleton.initialize(
    model_name="en_core_web_lg", 
    disable=["parser", "tagger", "lemmatizer"]
)
```

#### Voor Minder Memory Gebruik
- Gebruik `en_core_web_md` in plaats of `en_core_web_lg`
- Verhoog token limits in context management

## Next Steps

Na succesvolle installation:

1. Lees the [Snelstart Gids](quickstart.md)
2. Verken the [Architectuur Overview](architecture.md)
3. Probeer enkele [Voorbeelden](examples.md)

Voor problemen die hier niet staan, zie [Troubleshooting](troubleshooting.md).
