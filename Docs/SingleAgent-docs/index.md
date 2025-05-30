# SingleAgent Documentation

SingleAgent is een geavanceerd dual-agent systeem gebouwd op de OpenAI Agents SDK. Het biedt twee gespecialiseerde AI agents - een Code Agent voor programmeer-gerelateerde taken en een Architect Agent voor software architectuur en project analyse.

## Overzicht

SingleAgent maakt gebruik van de krachtige OpenAI Agents SDK om twee complementaire AI assistenten te bieden:

- **Code Agent (SingleAgent)**: Gespecialiseerd in code analyse, debugging, testing, en directe programmeer hulp
- **Architect Agent**: Gefocust op software architectuur, project structuur analyse, en high-level design beslissingen

Het systeem ondersteunt naadloos wisselen tussen agents en biedt geavanceerde context management, entity tracking, en streaming output.

## Inhoud

1. [Snelstart Gids](quickstart.md) - Begin direct met SingleAgent
2. [Installatie](installation.md) - Volledige installatie instructies
3. [Architectuur Overview](architecture.md) - Hoe het systeem in elkaar zit
4. [Code Agent](code-agent.md) - Gedetailleerde documentatie voor de Code Agent
5. [Architect Agent](architect-agent.md) - Gedetailleerde documentatie voor de Architect Agent
6. [Tools](tools.md) - Overzicht van alle beschikbare tools
7. [Context Management](context-management.md) - Hoe context en entity tracking werkt
8. [Configuration](configuration.md) - Configuratie opties en aanpassingen
9. [Gebruik Voorbeelden](examples.md) - Praktische voorbeelden en use cases
10. [API Referentie](api-reference.md) - Technische API documentatie
11. [Troubleshooting](troubleshooting.md) - Veelvoorkomende problemen en oplossingen

## Vereisten

- Python 3.8+
- OpenAI API key
- Enkele Python packages (zie [installatie](installation.md))

## Snel Beginnen

```bash
# Installeer dependencies
pip install -r requirements.txt

# Set je OpenAI API key
export OPENAI_API_KEY=sk-...

# Start het systeem
python main.py
```

Voor meer details, zie de [Snelstart Gids](quickstart.md).

## Key Features

### Dual Agent Systeem
- **!code** - Schakel naar Code Agent mode voor programmeer taken
- **!architect** - Schakel naar Architect Agent mode voor architectuur analyse

### Geavanceerd Context Management
- Automatische entity tracking (bestanden, commando's, taken)
- Slimme context samenvattingen om token limits te beheren
- Persistente context opslag tussen sessies

### Uitgebreide Tool Sets
- **Code Agent Tools**: Ruff, Pylint, Pyright, file operations, patch management
- **Architect Agent Tools**: AST analyse, project structuur analyse, dependency grafieken, design pattern detectie

### Interactive CLI
- Prompt_toolkit powered interface met history en auto-suggest
- Real-time streaming output
- Kleur-gecodeerde output voor betere leesbaarheid

## Voor Wie?

Deze documentatie is geschreven voor:

- **Ontwikkelaars** die SingleAgent willen gebruiken voor code analyse en debugging
- **Software Architects** die het systeem willen gebruiken voor project analyse
- **Contributors** die de codebase willen begrijpen en bijdragen
- **DevOps Engineers** die het systeem willen integreren in workflows

We gaan er vanuit dat je bekend bent met:
- Basis Python programmering
- De [OpenAI Agents SDK](../openai-agents-sdk-docs_copy/index.md) concepten
- Commando-regel interfaces

## Support

Voor vragen, bugs, of feature requests, zie de [Troubleshooting](troubleshooting.md) sectie of raadpleeg de bron code in de repository.
