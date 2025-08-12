import os
import sys
import asyncio
from unittest.mock import patch

# Ensure repository root is on sys.path for imports
sys.path.append(os.getcwd())

from agents import RunContextWrapper
from The_Agents.context_data import EnhancedContextData
from Tools.shared_tools import read_file, _file_cache
import json


def test_read_file_uses_cache(tmp_path):
    _file_cache.clear()
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello")
    wrapper = RunContextWrapper(EnhancedContextData(working_directory=os.getcwd()))
    object.__setattr__(wrapper.context, "count_tokens", lambda text: len(text))

    # Initial read to populate cache
    asyncio.run(read_file.on_invoke_tool(wrapper, json.dumps({"params": {"file_path": str(file_path)}})))

    # Patch open to ensure cache is used
    with patch("builtins.open", side_effect=AssertionError("open called")):
        result = asyncio.run(read_file.on_invoke_tool(wrapper, json.dumps({"params": {"file_path": str(file_path)}})))

    assert result["content"] == "hello"


def test_read_file_cache_invalidation(tmp_path):
    _file_cache.clear()
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello")
    wrapper = RunContextWrapper(EnhancedContextData(working_directory=os.getcwd()))
    object.__setattr__(wrapper.context, "count_tokens", lambda text: len(text))

    # Populate cache
    asyncio.run(read_file.on_invoke_tool(wrapper, json.dumps({"params": {"file_path": str(file_path)}})))

    # Modify file to change mtime and size
    file_path.write_text("hello world")

    from builtins import open as builtin_open
    with patch("builtins.open", wraps=builtin_open) as mock_open:
        result = asyncio.run(read_file.on_invoke_tool(wrapper, json.dumps({"params": {"file_path": str(file_path)}})))

    assert result["content"] == "hello world"
    assert mock_open.call_count == 1
