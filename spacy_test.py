import asyncio
from The_Agents.spacy_singleton import nlp_singleton
import json
async def test_spacy():
    await nlp_singleton.initialize()
    text = "Microsoft was founded by Bill Gates in Seattle. Python is a popular programming language."
    entities = await nlp_singleton.extract_entities(text)
    mapped = await nlp_singleton.map_entity_types(entities)
    print(json.dumps(mapped, indent=2))

asyncio.run(test_spacy())