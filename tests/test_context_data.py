import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from The_Agents.context_data import EnhancedContextData


def test_add_chat_message_trims_history():
    ctx = EnhancedContextData(working_directory=".", max_chat_messages=3)

    class DummyTokenizer:
        def encode(self, text):
            return text.split()

    ctx._tokenizer = DummyTokenizer()
    token_counts = []
    for i in range(4):
        content = f"message {i}"
        token_counts.append(ctx.count_tokens(content))
        ctx.add_chat_message("user", content)
    assert len(ctx.chat_messages) == 3
    # Ensure the oldest message was removed
    assert ctx.chat_messages[0]["content"] == "message 1"
    # Token count should match remaining messages
    assert ctx.token_count == sum(token_counts[1:])
