"""Tests for the :mod:`The_Agents.SingleAgent` module.

These tests focus on the private ``_apply_default_file_context`` helper and
context persistence behaviour described in ``Docs/sessions.md``.
"""

from __future__ import annotations

import asyncio
from importlib import import_module
from typing import TYPE_CHECKING

sa_module = import_module("The_Agents.SingleAgent")

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from The_Agents.SingleAgent import SingleAgent


def _create_agent(tmp_path, monkeypatch) -> SingleAgent:
    """Create a ``SingleAgent`` with its context file stored in ``tmp_path``."""
    context_path = tmp_path / "context.json"
    monkeypatch.setattr(sa_module, "CONTEXT_FILE_PATH", str(context_path))
    return sa_module.SingleAgent()


def test_apply_default_file_context_uses_current_file(tmp_path, monkeypatch):
    """When no file is specified, the current file should be appended."""
    agent = _create_agent(tmp_path, monkeypatch)
    agent.context.current_file = "example.py"
    monkeypatch.setattr(
        sa_module.EnhancedContextData,
        "get_recent_files",
        lambda self: [],
        raising=False,
    )

    result = agent._apply_default_file_context("Refactor the function")
    assert result == "Refactor the function in example.py"


def test_apply_default_file_context_skips_if_filename_given(tmp_path, monkeypatch):
    """Existing filenames in the input must not be modified."""
    agent = _create_agent(tmp_path, monkeypatch)
    agent.context.current_file = "example.py"
    monkeypatch.setattr(
        sa_module.EnhancedContextData,
        "get_recent_files",
        lambda self: [],
        raising=False,
    )

    result = agent._apply_default_file_context("Refactor example.py")
    assert result == "Refactor example.py"


def test_apply_default_file_context_uses_recent_file(tmp_path, monkeypatch):
    """Recent files are used when no current file is set."""
    agent = _create_agent(tmp_path, monkeypatch)
    agent.context.current_file = None
    monkeypatch.setattr(
        sa_module.EnhancedContextData,
        "get_recent_files",
        lambda self: ["recent.py"],
        raising=False,
    )

    result = agent._apply_default_file_context("Implement new feature")
    assert result == "Implement new feature in recent.py"


def test_context_persistence(tmp_path, monkeypatch):
    """Saving and reloading the context retains chat history."""
    agent1 = _create_agent(tmp_path, monkeypatch)
    agent1.context.chat_messages.append({"role": "user", "content": "Hello"})
    asyncio.run(agent1.save_context())

    agent2 = _create_agent(tmp_path, monkeypatch)
    assert agent2.context.chat_messages[0]["content"] == "Hello"
