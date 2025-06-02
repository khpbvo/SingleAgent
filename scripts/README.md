# Scripts

Deze map bevat utility scripts en hulpprogramma's.

## Apply Patch Systeem:
Het project gebruikt een custom patch systeem met een speciaal "V4A diff format":

- `apply_patch.py` - **Hoofdscript** voor het toepassen van patches in V4A format
- `apply_patch_prompt.py` - **Tool definitie** en beschrijving voor AI agents
- `verify_patch.py` - **Test script** voor het verifiëren van patch functionaliteit

Het V4A diff format gebruikt context-based patching in plaats van line numbers, waardoor het robuuster is voor AI agents.

## Andere Utilities:
- `count_words.py` - Utility voor het tellen van woorden in bestanden

## Documentatie:
Voor uitgebreide documentatie over het apply_patch systeem, zie:
`Docs/SingleAgent_docs/eng/apply_patch_tool_documentation.txt`
