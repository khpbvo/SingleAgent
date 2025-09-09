"""Tests for manual context management in :mod:`The_Agents.context_data`."""

from The_Agents.context_data import EnhancedContextData


def test_add_and_remove_manual_context():
    """Adding and removing manual context updates internal state.

    The context documentation highlights that local and LLM-visible context
    should be tracked for later use【F:Docs/context.md†L1-L9】.
    """
    ctx = EnhancedContextData(working_directory=".")
    label = ctx.add_manual_context("sample content", source="file.txt", label="sample")

    assert any(item.label == label for item in ctx.manual_context_items)
    assert ctx.token_count > 0

    removed = ctx.remove_manual_context(label)
    assert removed
    assert all(item.label != label for item in ctx.manual_context_items)
