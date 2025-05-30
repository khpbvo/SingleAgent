import os
import asyncio
import logging
import json
from agents import Agent, Runner
from utilities.tool_usage import handle_stream_events
from The_Agents.context_data import EnhancedContextData
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from Tools.web_browser_tools import fetch_url, search_web
from Tools.tools_single_agent import get_context, get_context_response, add_manual_context
from utils.project_info import discover_project_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BROWSER_INSTRUCTIONS = f"""{RECOMMENDED_PROMPT_PREFIX}
You are a web browsing assistant. Use your tools to fetch webpages and search the internet.
Always prefer using tools to gather information rather than guessing.
When exposed as a tool to other agents, use the name `web_browser_agent`.
"""

CONTEXT_FILE_PATH = os.path.join(os.path.expanduser("~"), ".webbrowser_context.json")

class WebBrowserAgent:
    def __init__(
        self,
        context: EnhancedContextData | None = None,
        context_path: str = CONTEXT_FILE_PATH,
        mcp_servers: list | None = None,
    ):
        cwd = os.getcwd()
        self.context_path = context_path
        self.mcp_servers = mcp_servers
        self.context = context or EnhancedContextData(
            working_directory=cwd,
            project_name=os.path.basename(cwd),
            project_info=discover_project_info(cwd),
            current_file=None,
        )
        self.agent = Agent[
            EnhancedContextData
        ](
            name="WebBrowserAgent",
            model="gpt-4.1",
            instructions=BROWSER_INSTRUCTIONS,
            tools=[fetch_url, search_web, get_context, get_context_response, add_manual_context],
            mcp_servers=self.mcp_servers,
        )

    def to_tool(self):
        """Return this agent as a callable tool."""
        return self.agent.as_tool(
            tool_name="web_browser_agent",
            tool_description="Browse the web and fetch URLs using WebBrowserAgent",
        )

    async def _load_context(self):
        if self.context:
            return
        try:
            self.context = await EnhancedContextData.load_from_json(self.context_path)
        except Exception:
            pass

    async def save_context(self):
        try:
            await self.context.save_to_json(self.context_path)
        except Exception as e:
            logger.error(f"Failed to save context: {e}")

    def _prepare_context_for_agent(self):
        summary = self.context.get_context_summary()
        instr = (
            BROWSER_INSTRUCTIONS
            + "\n\n--- CONTEXT ---\n"
            + summary
            + "\n----------------\n"
        )
        self.agent = Agent[
            EnhancedContextData
        ](
            name="WebBrowserAgent",
            model="gpt-4.1",
            instructions=instr,
            tools=self.agent.tools,
            mcp_servers=self.mcp_servers,
        )

    async def _run_streamed(
        self,
        user_input: str,
        *,
        enable_tracing: bool = False,
        trace_dir: str | None = None,
    ) -> str:
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=user_input,
            max_turns=50,
            context=self.context,
            enable_tracing=enable_tracing,
            trace_dir=trace_dir,
        )
        output = await handle_stream_events(result.stream_events())
        return output

    async def run(
        self,
        user_input: str,
        stream_output: bool = True,
        *,
        enable_tracing: bool = False,
        trace_dir: str | None = None,
    ) -> str:
        self._prepare_context_for_agent()
        self.context.add_chat_message("user", user_input)
        if stream_output:
            final = await self._run_streamed(
                user_input,
                enable_tracing=enable_tracing,
                trace_dir=trace_dir,
            )
        else:
            res = await Runner.run(
                starting_agent=self.agent,
                input=user_input,
                context=self.context,
                enable_tracing=enable_tracing,
                trace_dir=trace_dir,
            )
            final = res.final_output
        self.context.add_chat_message("assistant", final)
        await self.save_context()
        return final

    def get_context_summary(self) -> str:
        return self.context.get_context_summary()

    def get_chat_history_summary(self) -> str:
        return self.context.get_chat_summary()

    def clear_chat_history(self) -> None:
        self.context.clear_chat_history()
