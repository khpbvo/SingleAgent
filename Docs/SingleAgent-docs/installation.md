# Installatie

Deze pagina bevat gedetailleerde installatie instructies voor SingleAgent op verschillende platformen.

## Systeem Vereisten

### Hardware
- **RAM**: Minimaal 4GB, aanbevolen 8GB+ (voor spaCy model)
- **Disk Space**: Ongeveer 500MB voor alle dependencies
- **CPU**: Geen specifieke vereisten

### Software
- **Python**: 3.8 of hoger (3.9+ aanbevolen)
- **pip**: Voor package management
- **Internet**: Voor OpenAI API calls en package downloads

## Platform Specifieke Instructies

### macOS

```bash
# Controleer Python versie
python3 --version

# Installeer Homebrew (als je dit nog niet hebt)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update pip
python3 -m pip install --upgrade pip

# Clone/download het project
# Navigeer naar de project directory

# Installeer requirements
pip3 install -r requirements.txt

# Download spaCy model
python3 -m spacy download en_core_web_lg
```

### Linux (Ubuntu/Debian)

```bash
# Update package lijst
sudo apt update

# Installeer Python en pip (als nog niet aanwezig)
sudo apt install python3 python3-pip python3-venv

# Controleer versie
python3 --version

# Clone/download het project
# Navigeer naar de project directory

# Maak virtual environment (aanbevolen)
python3 -m venv venv
source venv/bin/activate

# Installeer requirements
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg
```

### Windows

```cmd
REM Controleer Python versie
python --version

REM Navigeer naar project directory
cd path\to\your\project

REM Maak virtual environment (aanbevolen)
python -m venv venv
venv\Scripts\activate

REM Installeer requirements
pip install -r requirements.txt

REM Download spaCy model
python -m spacy download en_core_web_lg
```

## Virtual Environment Setup (Aanbevolen)

Het wordt sterk aanbevolen om een virtual environment te gebruiken:

### Waarom Virtual Environment?
- Voorkomt conflicten met andere Python projecten
- Houdt dependencies georganiseerd
- Makkelijker om verschillende versies te beheren

### Setup

```bash
# Maak virtual environment
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
openai                  # OpenAI API client voor LLM calls
prompt_toolkit         # Geavanceerde CLI interface met history
pydantic              # Data validatie en serialisatie
tiktoken              # Token counting voor OpenAI models
```

### Advanced Features

```python
spacy                 # Natural Language Processing voor entity extraction
networkx              # Graph analysis voor dependency mapping
typing_extensions     # Extended type hints ondersteuning
toml                  # TOML configuratie file parsing
```

### Development Tools

```python
ruff                  # Python linter en formatter (vervanger voor flake8)
pylint                # Uitgebreide Python code analysis
pyright               # Static type checker van Microsoft
```

## OpenAI API Setup

### API Key verkrijgen

1. Ga naar [OpenAI Platform](https://platform.openai.com)
2. Log in of maak een account
3. Navigeer naar API keys sectie
4. Genereer een nieuwe API key
5. Bewaar deze veilig!

### API Key Configureren

#### Methode 1: Environment Variable (Aanbevolen)

```bash
# macOS/Linux - voeg toe aan ~/.bashrc of ~/.zshrc
export OPENAI_API_KEY=sk-your-api-key-here

# Windows - voeg toe aan environment variables
set OPENAI_API_KEY=sk-your-api-key-here
```

#### Methode 2: .env File

Maak een `.env` bestand in de project root:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

**Waarschuwing**: Voeg `.env` toe aan je `.gitignore`!

### API Gebruik Monitoring

- Monitor je usage op [OpenAI Platform](https://platform.openai.com/usage)
- Stel usage limits in als gewenst
- SingleAgent gebruikt standaard GPT-4.1

## SpaCy Model Setup

### Standaard Model (Aanbevolen)

```bash
# Download large English model (beste accuracy)
python -m spacy download en_core_web_lg
```

### Alternatieve Models

```bash
# Medium model (balans tussen grootte en accuracy)
python -m spacy download en_core_web_md

# Small model (snelste, minder accurate)
python -m spacy download en_core_web_sm
```

### Model Selectie Aanpassen

In `The_Agents/spacy_singleton.py` kun je het model wijzigen:

```python
# Wijzig deze regel voor een ander model
await nlp_singleton.initialize(model_name="en_core_web_md", disable=["parser"])
```

## Verificatie van Installatie

Test of alles correct geïnstalleerd is:

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
# Zorg dat je in de juiste directory bent
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
- Gebruik forward slashes `/` in plaats van backslashes `\`
- Activeer virtual environment voor elke nieuwe terminal sessie
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
- Gebruik `en_core_web_md` in plaats van `en_core_web_lg`
- Verhoog token limits in context management

## Next Steps

Na succesvolle installatie:

1. Lees de [Snelstart Gids](quickstart.md)
2. Verken de [Architectuur Overview](architecture.md)
3. Probeer enkele [Voorbeelden](examples.md)

Voor problemen die hier niet staan, zie [Troubleshooting](troubleshooting.md).
