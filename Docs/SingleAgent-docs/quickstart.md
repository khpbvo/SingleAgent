# Snelstart Gids

Deze gids helpt je om SingleAgent snel op te zetten en je eerste taken uit te voeren.

## Voordat je begint

Zorg ervoor dat je hebt:
- Python 3.8 of hoger geïnstalleerd
- Een OpenAI API key
- Git (optioneel, voor klonen van repository)

## Stap 1: Installatie

### Basis Setup

```bash
# Clone de repository (of download de bestanden)
cd je-project-directory

# Installeer de vereiste packages
pip install -r requirements.txt
```

### Vereiste Packages

SingleAgent vereist de volgende packages:
```
openai
prompt_toolkit
pydantic
tiktoken
spacy
networkx
typing_extensions
toml
ruff
pylint
pyright
```

### SpaCy Model Setup

Voor de beste entity recognition moet je een spaCy model downloaden:

```bash
python -m spacy download en_core_web_lg
```

## Stap 2: API Key Configuratie

Stel je OpenAI API key in als environment variable:

```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

Voor permanente setup, voeg dit toe aan je `~/.bashrc`, `~/.zshrc`, of equivalent.

## Stap 3: Eerste Start

Start het systeem:

```bash
python main.py
```

Je zou moeten zien:
```
Initializing spaCy model (this may take a moment)...
Dual-Agent system initialized.
Currently in Code Agent mode.
Use !code or !architect to switch between agents.
Use !history to view chat history or !clear to clear it.

=== Code Agent Mode ===

Context Summary: Working in /path/to/your/project
  - Project: your-project-name
  - Files tracked: 0
  - Commands tracked: 0
  - Token usage: 0/50000

User: 
```

## Stap 4: Basis Gebruik

### Code Agent Taken

Het systeem start standaard in Code Agent mode. Probeer deze commando's:

```
# File analyse
Kun je het bestand main.py analyseren?

# Code quality check
Run ruff op alle Python bestanden

# Debugging hulp
Ik krijg een error in line 45 van SingleAgent.py, kun je helpen?
```

### Architect Agent Taken

Schakel naar Architect mode en probeer:

```
!architect

# Project structuur analyse
Analyseer de project structuur van deze codebase

# Design patterns detectie
Welke design patterns zie je in de ArchitectAgent.py?

# TODO lijst genereren
Maak een TODO lijst voor het verbeteren van de code architectuur
```

### Basis Commando's

| Commando | Beschrijving |
|----------|-------------|
| `!code` | Schakel naar Code Agent mode |
| `!architect` | Schakel naar Architect Agent mode |
| `!history` | Toon chat geschiedenis |
| `!clear` | Wis chat geschiedenis |
| `!entities` | Toon getrackte entities |
| `!context` | Toon context samenvatting |
| `!manualctx` | Voeg handmatige context toe |

## Stap 5: Voorbeeld Workflow

Hier is een typische workflow voor het analyseren van een Python project:

### 1. Project Verkenning (Architect Agent)
```
!architect
Analyseer de project structuur en geef me een overzicht van de architectuur
```

### 2. Code Quality Check (Code Agent)
```
!code
Run alle linters (ruff, pylint, pyright) op de codebase
```

### 3. Specifieke File Analyse (Code Agent)
```
Lees het bestand main.py en leg uit hoe het werkt
```

### 4. Architectuur Verbeteringen (Architect Agent)
```
!architect
Welke design patterns zie je en welke verbeteringen stel je voor?
```

### 5. TODO Planning (Architect Agent)
```
Maak een gestructureerde TODO lijst met prioriteiten voor dit project
```

## Tips voor Effectief Gebruik

### 1. Context Beheer
- Het systeem onthoudt je conversatie geschiedenis
- Entities zoals bestanden en commando's worden automatisch getrackt
- Gebruik `!context` om te zien wat het systeem weet

### 2. Agent Selectie
- **Code Agent** voor: debugging, testing, file operations, patches
- **Architect Agent** voor: structuur analyse, design patterns, planning

### 3. Tool Gebruik
- De agents gebruiken automatisch de juiste tools
- Je hoeft niet te specificeren welke tool te gebruiken
- Tools worden intelligent gecombineerd voor complexe taken

### 4. Streaming Output
- Output wordt real-time gestreamed voor betere responsiviteit
- Je kunt de output zien terwijl de agent werkt

## Volgende Stappen

Nu je SingleAgent draait hebt, verken verder:

- [Code Agent Details](code-agent.md) - Diep duiken in Code Agent mogelijkheden
- [Architect Agent Details](architect-agent.md) - Leer over architectuur analyse
- [Tools Overzicht](tools.md) - Alle beschikbare tools en hun gebruik
- [Gebruik Voorbeelden](examples.md) - Meer complexe voorbeelden en use cases

## Veelvoorkomende Problemen

### "No module named 'agents'"
Zorg ervoor dat alle packages geïnstalleerd zijn met `pip install -r requirements.txt`

### SpaCy Model Fout
Download het spaCy model: `python -m spacy download en_core_web_lg`

### OpenAI API Fout
Controleer of je API key correct is ingesteld en geldig is.

Voor meer troubleshooting, zie [Troubleshooting Guide](troubleshooting.md).
