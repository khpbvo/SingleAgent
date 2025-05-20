import asyncio
import unittest
from agents import Agent, Runner, RunContextWrapper
from The_Agents.SearchAgent import SearchAgent
from The_Agents.WebBrowserAgent import WebBrowserAgent
from The_Agents.ArchitectAgent import ArchitectAgent
from The_Agents.SingleAgent import SingleAgent
from The_Agents.context_data import EnhancedContextData


class AgentToolTests(unittest.TestCase):
    def run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_runner_calls_search_agent_tool(self):
        ctx = EnhancedContextData(working_directory=".", project_name="test")
        search = SearchAgent(context=ctx)
        tool = search.to_tool()
        orch = Agent(name="orch", tools=[tool])
        async def respond(self, input, context=None):
            return await tool(RunContextWrapper(context), input)
        orch.respond = respond.__get__(orch, Agent)
        result = self.run_async(Runner.run(orch, input="hi", context=ctx))
        self.assertIn("SearchAgent", result.final_output)

    def test_runner_calls_browser_agent_tool(self):
        ctx = EnhancedContextData(working_directory=".", project_name="test")
        browser = WebBrowserAgent(context=ctx)
        tool = browser.to_tool()
        orch = Agent(name="orch", tools=[tool])
        async def respond(self, input, context=None):
            return await tool(RunContextWrapper(context), input)
        orch.respond = respond.__get__(orch, Agent)
        result = self.run_async(Runner.run(orch, input="hi", context=ctx))
        self.assertIn("WebBrowserAgent", result.final_output)

    def test_runner_calls_architect_agent_tool(self):
        ctx = EnhancedContextData(working_directory=".", project_name="test")
        arch = ArchitectAgent(context=ctx)
        tool = arch.to_tool()
        orch = Agent(name="orch", tools=[tool])
        async def respond(self, input, context=None):
            return await tool(RunContextWrapper(context), input)
        orch.respond = respond.__get__(orch, Agent)
        result = self.run_async(Runner.run(orch, input="hi", context=ctx))
        self.assertIn("ArchitectAgent", result.final_output)

    def test_single_agent_tool_list(self):
        ctx = EnhancedContextData(working_directory=".", project_name="test")
        search = SearchAgent(context=ctx)
        browser = WebBrowserAgent(context=ctx)
        arch = ArchitectAgent(context=ctx)
        single = SingleAgent(
            context=ctx,
            browser_agent=browser,
            search_agent=search,
            architect_agent=arch,
        )
        names = [t.__name__ for t in single.agent.tools]
        self.assertIn("search_agent", names)
        self.assertIn("web_browser_agent", names)
        self.assertIn("architect_agent", names)


if __name__ == "__main__":
    unittest.main()

