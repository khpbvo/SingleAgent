"""Web search agent using the shared context.

This agent follows the OpenAI Agents SDK specifications and is
compatible with Pydantic v2. It provides simple web search
capabilities and can hand off control to other agents by sharing
the same ``EnhancedContextData`` instance.
"""

import os
import logging
from agents import Agent, Runner
from utilities.tool_usage import handle_stream_events
from The_Agents.context_data import EnhancedContextData
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from Tools.searchagent_tools import search_internet, fetch_result
from Tools.tools_single_agent import (
    get_context,
    get_context_response,
    add_manual_context,
)
from utils.project_info import discover_project_info


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SEARCH_INSTRUCTIONS = f"""{RECOMMENDED_PROMPT_PREFIX}
You are a web search assistant. Use your tools to search the web and
fetch pages when required. Prefer using tools over guessing answers.
When exposed as a tool to other agents, use the name `search_agent`.
"""

CONTEXT_FILE_PATH = os.path.join(os.path.expanduser("~"), ".searchagent_context.json")


class SearchAgent:
    """Agent responsible for web searches."""

    def __init__(self, context: EnhancedContextData | None = None, context_path: str = CONTEXT_FILE_PATH) -> None:
        cwd = os.getcwd()
        self.context_path = context_path
        self.context = context or EnhancedContextData(
            working_directory=cwd,
            project_name=os.path.basename(cwd),
            project_info=discover_project_info(cwd),
            current_file=None,
        )
        self.agent = Agent[
            EnhancedContextData
        ](
            name="SearchAgent",
            model="gpt-4.1",
            instructions=SEARCH_INSTRUCTIONS,
            tools=[
                search_internet,
                fetch_result,
                get_context,
                get_context_response,
                add_manual_context,
            ],
        )

    def to_tool(self):
        """Return this agent as a callable tool."""
        return self.agent.as_tool(
            tool_name="search_agent",
            tool_description="Perform internet searches using SearchAgent",
        )

    async def _load_context(self) -> None:
        if self.context:
            return
        try:
            self.context = await EnhancedContextData.load_from_json(self.context_path)
        except Exception:
            pass

    async def save_context(self) -> None:
        try:
            await self.context.save_to_json(self.context_path)
        except Exception as e:
            logger.error(f"Failed to save context: {e}")

    def _prepare_context_for_agent(self) -> None:
        summary = self.context.get_context_summary()
        instr = (
            SEARCH_INSTRUCTIONS
            + "\n\n--- CONTEXT ---\n"
            + summary
            + "\n----------------\n"
        )
        self.agent = Agent[
            EnhancedContextData
        ](
            name="SearchAgent",
            model="gpt-4.1",
            instructions=instr,
            tools=self.agent.tools,
        )

    async def _run_streamed(self, user_input: str) -> str:
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=user_input,
            max_turns=50,
            context=self.context,
        )
        output = await handle_stream_events(result.stream_events())
        return output

    async def run(self, user_input: str, stream_output: bool = True) -> str:
        self._prepare_context_for_agent()
        self.context.add_chat_message("user", user_input)
        if stream_output:
            final = await self._run_streamed(user_input)
        else:
            res = await Runner.run(
                starting_agent=self.agent,
                input=user_input,
                context=self.context,
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

