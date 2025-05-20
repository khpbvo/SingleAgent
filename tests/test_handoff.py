import unittest

from agents import HandoffInputData
from agents.extensions import handoff_filters
from The_Agents.WebBrowserAgent import WebBrowserAgent
from The_Agents.SingleAgent import SingleAgent
from The_Agents.context_data import EnhancedContextData


class HandoffFilterTests(unittest.TestCase):
    def test_remove_tool_history_on_handoff(self):
        ctx = EnhancedContextData(working_directory=".", project_name="test")
        browser = WebBrowserAgent(context=ctx)
        single = SingleAgent(context=ctx, browser_agent=browser)

        self.assertEqual(len(single.agent.handoffs), 1)
        handoff_obj = single.agent.handoffs[0]
        self.assertIs(handoff_obj.input_filter, handoff_filters.remove_all_tools)

        history = [
            {"role": "user", "content": "Hi"},
            {"role": "tool", "content": "some call"},
            {"role": "assistant", "content": "Done"},
        ]
        input_data = HandoffInputData(history=history)
        filtered = handoff_obj.input_filter(input_data)
        self.assertEqual(len(filtered.history), 2)
        for msg in filtered.history:
            self.assertNotEqual(msg.get("role"), "tool")


if __name__ == "__main__":
    unittest.main()
