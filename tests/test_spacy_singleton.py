"""Tests for the :mod:`The_Agents.spacy_singleton` module."""

import pytest

from The_Agents.spacy_singleton import nlp_singleton


@pytest.mark.asyncio
async def test_entity_extraction_and_mapping():
    """Ensure entities are extracted and mapped to custom types.

    Based on the context management documentation, the agent keeps track of
    structured information about entities that appear in text【F:Docs/context.md†L1-L9】.
    """
    await nlp_singleton.initialize()
    text = (
        "Microsoft was founded by Bill Gates in Seattle. Python is a popular programming"
        " language."
    )

    entities = await nlp_singleton.extract_entities(text)
    mapped = await nlp_singleton.map_entity_types(entities)

    assert "organization" in mapped
    assert any(e["value"] == "Microsoft" for e in mapped["organization"])
    assert "person" in mapped
    assert any(e["value"] == "Bill Gates" for e in mapped["person"])
