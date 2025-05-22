import asyncio
from types import SimpleNamespace
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable

__all__ = [
    "Agent",
    "Runner",
    "function_tool",
    "RunContextWrapper",
    "WebSearchTool",
    "ItemHelpers",
    "StreamEvent",
    "RunItemStreamEvent",
    "RawResponsesStreamEvent",
    "AgentUpdatedStreamEvent",
    "HandoffInputData",
    "Handoff",
    "handoff",
]


def function_tool(func=None, *, name_override=None, description_override=None):
    def decorator(f):
        async def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(f):
                return await f(*args, **kwargs)
            return f(*args, **kwargs)
        wrapper.__name__ = name_override or f.__name__
        wrapper.__doc__ = f.__doc__
        wrapper.tool_name = name_override or f.__name__
        wrapper.tool_description = description_override or (f.__doc__ or "")
        return wrapper
    return decorator(func) if func else decorator


T = TypeVar("T")


class RunContextWrapper(Generic[T]):
    def __init__(self, context: T | None = None):
        self.context = context


@dataclass
class Agent(Generic[T]):
    name: str
    model: str | None = None
    instructions: str = ""
    tools: list | None = None
    handoffs: list | None = None
    mcp_servers: list | None = None
    model_settings: object | None = None

    @classmethod
    def __class_getitem__(cls, item):
        return cls

    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.handoffs is None:
            self.handoffs = []
        if self.mcp_servers is None:
            self.mcp_servers = []

    async def respond(self, input: str, context=None):
        """Return an LLM generated reply.

        This uses ``openai`` if it is installed. The current ``instructions``
        string is passed as the system message and any chat history stored on
        ``context`` (if provided) is included before the user message.  If the
        OpenAI client is unavailable or an error occurs, the method falls back
        to echoing the input which matches the previous placeholder
        behaviour.
        """

        messages = []

        instr = self.instructions
        if callable(instr):
            try:
                maybe = instr(context) if context is not None else instr()
                instr = await maybe if asyncio.iscoroutine(maybe) else maybe
            except Exception:
                instr = str(instr)

        if instr:
            messages.append({"role": "system", "content": str(instr)})

        if context is not None and hasattr(context, "get_chat_history"):
            try:
                messages.extend(context.get_chat_history())
            except Exception:
                pass

        messages.append({"role": "user", "content": input})

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI()
            response = await client.chat.completions.create(
                model=self.model or "gpt-3.5-turbo",
                messages=messages,
                **(self.model_settings.settings if hasattr(self.model_settings, "settings") else {})
            )
            output = response.choices[0].message.content
        except Exception:
            output = f"{self.name} response: {input}"

        if context is not None and hasattr(context, "add_chat_message"):
            try:
                context.add_chat_message("assistant", output)
            except Exception:
                pass

        return output

    def as_tool(self, tool_name: str, tool_description: str):
        @function_tool(name_override=tool_name, description_override=tool_description)
        async def _tool(wrapper: RunContextWrapper, input: str):
            res = await Runner.run(self, input=input, context=wrapper.context)
            return res.final_output
        return _tool


class Runner:
    @staticmethod
    async def run(starting_agent: Agent, input: str, context=None, **kwargs):
        output = await starting_agent.respond(input, context=context)
        return SimpleNamespace(final_output=output)

    @staticmethod
    async def run_streamed(*args, **kwargs):
        """Asynchronously run an agent and return a dummy streamed result."""
        class Dummy:
            def __init__(self, output):
                self.final_output = output

            async def stream_events(self):
                if False:
                    yield None

        result = await Runner.run(*args, **kwargs)
        return Dummy(result.final_output)


class WebSearchTool:
    def __call__(self, *args, **kwargs):
        return ""


class ItemHelpers:
    pass


class StreamEvent:
    pass


class RunItemStreamEvent(StreamEvent):
    def __init__(self, item=None):
        self.item = item


class RawResponsesStreamEvent(StreamEvent):
    def __init__(self, data=None):
        self.data = data


class AgentUpdatedStreamEvent(StreamEvent):
    def __init__(self, new_agent=None):
        self.new_agent = new_agent


@dataclass
class HandoffInputData:
    history: list


@dataclass
class Handoff:
    agent: Agent
    input_filter: Callable | None = None


def handoff(agent: Agent, *, input_filter=None, **kwargs):
    return Handoff(agent=agent, input_filter=input_filter)


# Submodules
class ModelSettings:
    def __init__(self, **kwargs):
        self.settings = kwargs


class MaxTurnsExceeded(Exception):
    pass

