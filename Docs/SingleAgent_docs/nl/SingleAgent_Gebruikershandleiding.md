# SingleAgent - Gebruikershandleiding

## Wat is SingleAgent?

SingleAgent is een intelligente AI-assistent die je helpt met programmeren, systeemontwerp en documentatie. Het systeem beschikt over twee gespecialiseerde modi die samenwerken om je productiviteit te verhogen:

- **Code Agent**: Gespecialiseerd in programmeren, debugging en code-gerelateerde taken
- **Architect Agent**: Gericht op systeemontwerp, architectuur en documentatie

## Installatie en Setup

### Vereisten
- Python 3.8 of hoger
- OpenAI API key

### Installatie Stappen

1. **Clone en installeer dependencies:**
```bash
cd SingleAgent
pip install -r requirements.txt
```

2. **Download het spaCy taalmodel:**
```bash
python -m spacy download en_core_web_lg
```

3. **Stel je OpenAI API key in:**
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

4. **Start het programma:**
```bash
python main.py
```

## Basisfunctionaliteiten

### Agent Modi

#### Code Agent Mode (Standaard)
De Code Agent helpt je met:
- ✅ Code schrijven en debuggen
- ✅ Bestanden lezen en schrijven  
- ✅ Commands uitvoeren
- ✅ Code reviews en optimalisaties
- ✅ Error troubleshooting

#### Architect Agent Mode
De Architect Agent helpt je met:
- 🏗️ Systeemarchitectuur ontwerpen
- 📋 Documentatie genereren
- 🔍 Code base analyse
- 📊 Project planning
- 🎯 Best practices advies

### Tussen Modi Wisselen

```
!code       # Schakel naar Code Agent
!architect  # Schakel naar Architect Agent
```

## Belangrijke Commando's

### Basis Commando's
```
!help       # Toon alle beschikbare commando's
!history    # Bekijk chat geschiedenis
!context    # Toon context samenvatting
!clear      # Wis chat geschiedenis
!save       # Sla context handmatig op
exit/quit   # Sluit het programma af
```

### Context Management
```
!entity     # Bekijk bijgehouden entiteiten
!manualctx  # Toon handmatig toegevoegde context
!delctx:label # Verwijder context item op label
```

### Speciale Functies
```
code:read:path          # Voeg bestand toe aan persistente context
arch:readfile:path      # Analyseer bestand met Architect Agent
arch:readdir:path       # Analyseer mapstructuur
```

## Praktische Voorbeelden

### Voorbeeld 1: Code Generatie
```
User: Schrijf een Python functie om een REST API te maken met FastAPI

Code Agent: Ik ga een FastAPI applicatie voor je maken...
[Agent genereert code met uitleg]
```

### Voorbeeld 2: Bestand Analyse
```
arch:readfile:src/main.py

[Architect Agent analyseert het bestand en geeft gedetailleerde feedback over structuur en verbeteringen]
```

### Voorbeeld 3: Project Structuur Analyse
```
arch:readdir:src

[Architect Agent scant de directory en geeft een overzicht van de project architectuur]
```

### Voorbeeld 4: Context Toevoegen
```
code:read:config/settings.py

[Voegt het bestand toe aan de persistente context zodat de agent er in toekomstige gesprekken naar kan verwijzen]
```

## Geavanceerde Features

### Intelligente Context Management
- **Automatische Entity Tracking**: Het systeem herkent automatisch bestanden, commands en concepten
- **Persistente Context**: Belangrijke informatie blijft bewaard tussen sessies
- **Token Management**: Efficiënt beheer van context om binnen API limieten te blijven

### Real-time Streaming
- **Live Response**: Zie antwoorden real-time verschijnen
- **Tool Feedback**: Krijg direct feedback wanneer tools gebruikt worden
- **Progress Indicators**: Zie wanneer het systeem bezig is met complexe taken

### Smart File Operations
- **Veilig Schrijven**: Automatische backups en validatie
- **Directory Scanning**: Intelligente analyse van project structuren
- **Content Summarization**: Automatische samenvattingen van grote bestanden

## Tips voor Effectief Gebruik

### 1. Kies de Juiste Mode
- **Code problemen?** → Gebruik Code Agent
- **Architectuur vragen?** → Gebruik Architect Agent

### 2. Gebruik Context Slim
```
# Voeg relevante bestanden toe aan context
code:read:src/models.py
code:read:config.py

# Vraag dan om hulp
"Kun je deze models optimaliseren voor betere performance?"
```

### 3. Bouw Context Op
```
# Start met overzicht
arch:readdir:src

# Zoom in op specifieke onderdelen  
arch:readfile:src/main.py

# Vraag om verbeteringen
"Hoe kan ik deze architectuur beter structureren?"
```

### 4. Gebruik Historische Context
Het systeem onthoudt:
- Eerder geschreven code
- Besproken architectuur beslissingen
- Geïdentificeerde problemen
- Toegepaste oplossingen

## Workflow Voorbeelden

### Nieuwe Feature Ontwikkeling
1. **Analyseer huidige code:**
   ```
   arch:readdir:src
   ```

2. **Wissel naar Code Agent:**
   ```
   !code
   ```

3. **Implementeer feature:**
   ```
   "Voeg een user authentication systeem toe aan mijn FastAPI app"
   ```

4. **Test en verfijn:**
   ```
   "Run de tests en fix eventuele errors"
   ```

### Code Review Workflow
1. **Voeg code toe aan context:**
   ```
   code:read:src/new_feature.py
   ```

2. **Wissel naar Architect:**
   ```
   !architect
   ```

3. **Vraag om review:**
   ```
   "Review deze code voor best practices en potentiële verbeteringen"
   ```

### Debugging Workflow
1. **Deel error informatie:**
   ```
   "Ik krijg deze error: [error message]"
   ```

2. **Voeg relevante bestanden toe:**
   ```
   code:read:src/problematic_file.py
   ```

3. **Vraag om debugging hulp:**
   ```
   "Help me deze error te debuggen"
   ```

## Troubleshooting

### Veelvoorkomende Problemen

#### "API Key Error"
```bash
# Controleer je API key
echo $OPENAI_API_KEY

# Stel opnieuw in als leeg
export OPENAI_API_KEY=sk-your-key
```

#### "spaCy Model Not Found"
```bash
# Download het model opnieuw
python -m spacy download en_core_web_lg
```

#### "Context Te Groot"
```
!clear          # Wis geschiedenis
!delctx:label   # Verwijder specifieke context items
```

#### Agent Reageert Langzaam
- Wis onnodige context met `!clear`
- Verwijder oude bestanden uit context
- Check je internet verbinding

### Debug Informatie
Het systeem slaat logs op in:
```
logs/main.log           # Algemene logs
logs/singleagent.log    # Code Agent logs
logs/architectagent.log # Architect Agent logs
```

## Best Practices

### 1. Context Hygiene
- **Wis regelmatig** oude gesprekken met `!clear`
- **Verwijder irrelevante** context items
- **Voeg alleen relevante** bestanden toe aan context

### 2. Effectieve Vragen
- **Wees specifiek** in je vragen
- **Geef context** over wat je probeert te bereiken
- **Gebruik voorbeelden** waar mogelijk

### 3. Tool Gebruik
- **Gebruik arch:readdir** voor project overzichten
- **Gebruik code:read** voor specifieke bestanden
- **Wissel tussen modi** afhankelijk van je taak

### 4. Workflow Organisatie
- **Begin breed** (architectuur overzicht)
- **Zoom in** op specifieke componenten
- **Test iteratief** tijdens ontwikkeling

## Veelgestelde Vragen

**Q: Hoe weet ik welke mode ik moet gebruiken?**
A: Code Agent voor implementatie, Architect Agent voor design en planning.

**Q: Wordt mijn context automatisch opgeslagen?**
A: Ja, bij elke interactie. Je kunt ook handmatig opslaan met `!save`.

**Q: Kan ik meerdere bestanden tegelijk analyseren?**
A: Ja, gebruik `arch:readdir` voor directory analyse of voeg meerdere bestanden toe met `code:read`.

**Q: Hoe verwijder ik oude context?**
A: Gebruik `!clear` voor alles of `!delctx:label` voor specifieke items.

**Q: Kan het systeem code uitvoeren?**
A: Ja, via de run_command tool, maar dit wordt veilig gedaan in containers waar mogelijk.

## Support en Feedback

Voor technische problemen:
1. Check de logs in de `logs/` directory
2. Restart het programma
3. Verificeer je API key en internet verbinding

Het SingleAgent systeem leert van je gebruik en wordt effectiever naarmate je er meer mee werkt. Begin met eenvoudige taken en bouw geleidelijk op naar complexere workflows.
