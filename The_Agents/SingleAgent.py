"""
SingleAgent implementation for code assistant that follows OpenAI Agents SDK patterns.
Features:
- Terminal control
- Pylint integration
- Colored diff generation
- Patch application
- Streaming responses
- Chain of thought reasoning
"""

import asyncio
import os
from typing import List, Optional, Dict, Any

from agents import (
    Agent, 
    Runner, 
    ItemHelpers, 
    function_tool,
    RunContextWrapper,
    StreamEvent
)
from pydantic import BaseModel, Field

# Import tools
from ..Tools.tools_single_agent import (
    run_ruff,
    run_pylint,
    run_pyright,
    run_command,
    read_file,
    create_colored_diff,
    apply_patch,
    change_dir,
    os_command
)
from ..utils.project_info import discover_project_info

# Constants
AGENT_INSTRUCTIONS = """
You are a code assistant capable of helping users write, edit, and patch code.
You have full control of the terminal and can run commands like sed, grep, ls, dir, cd, tail, python, and bash.
You can analyze code with pylint, generate colored diffs, and apply patches to files.

When suggesting code changes, follow this workflow:
1. Read and understand the code using the read_file tool
2. If needed, analyze the code using pylint
3. Generate improved or fixed code
4. Create a colored diff to show the changes
5. Format the patch in the expected format
6. Apply the patch using the apply_patch tool

Always clearly explain your thought process before taking actions.
For complex tasks, break down your approach into specific steps and explain each step.

When applying patches, use this format:
*** Begin Patch
*** Update File: <filename>
[context lines before change]
- [old line]
+ [new line]
[context lines after change]
*** End Patch

Remember to show your reasoning at each step of the process. Consider different approaches, evaluate trade-offs,
and explain why you chose a particular solution.
"""

class CodeAssistantContextData(BaseModel):
    """Context data for the code assistant agent"""
    working_directory: str = Field(description="Current working directory")
    project_info: Optional[Dict[str, Any]] = Field(None, description="Information about the project")


class SingleAgent:
    """
    A single agent implementation for code assistance with streaming capability 
    and terminal control.
    """
    
    def __init__(self):
        """Initialize the code assistant agent with all required tools."""
        self.agent = Agent[CodeAssistantContextData](
            name="CodeAssistant",
            instructions=AGENT_INSTRUCTIONS,
            tools=[
                run_ruff,
                run_pylint,
                run_pyright,
                run_command,
                read_file,
                create_colored_diff,
                apply_patch,
                change_dir,
                os_command
            ]
        )
        
        cwd = os.getcwd()
        self.context = CodeAssistantContextData(
            working_directory=cwd,
            project_info=discover_project_info(cwd)
        )
    
    async def run(self, user_input: str, stream_output: bool = True) -> Any:
        """
        Run the agent with the given user input.
        
        Args:
            user_input: The user's query or request
            stream_output: Whether to stream the output or wait for completion
            
        Returns:
            The agent's response
        """
        if stream_output:
            return await self._run_streamed(user_input)
        else:
            result = await Runner.run(
                starting_agent=self.agent,
                input=user_input,
                context=self.context,
            )
            return result.final_output
    
    async def _run_streamed(self, user_input: str) -> str:
        """
        Run the agent with streamed output.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            The final output from the agent
        """
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=user_input,
            max_turns=50,
            context=self.context,
        )
        
        print("Starting agent with streaming output...")
        
        # Process stream events
        async for event in result.stream_events():
            if event.type == "raw_response_event":
                # Stream the raw response events for real-time output
                from openai.types.responses import ResponseTextDeltaEvent
                if hasattr(event, 'data') and isinstance(event.data, ResponseTextDeltaEvent):
                    print(event.data.delta, end="", flush=True)
            
            elif event.type == "run_item_stream_event":
                # Process different types of items
                if event.item.type == "tool_call_item":
                    item_any: Any = event.item
                    print(f"\n\n[Tool Call] {item_any.name}\n")
                
                elif event.item.type == "tool_call_output_item":
                    tool_output = event.item.output
                    print(f"\n[Tool Output] {tool_output[:100]}{'...' if len(tool_output) > 100 else ''}\n")
                
                elif event.item.type == "message_output_item":
                    message = ItemHelpers.text_message_output(event.item)
                    print(f"\n[Message] {message[:100]}{'...' if len(message) > 100 else ''}\n")
        
        # Return the final result
        return result.final_output


async def main():
    """Example usage of SingleAgent."""
    agent = SingleAgent()
    
    # Example query to test the agent
    query = "Please analyze the apply_patch.py file and suggest any improvements."
    
    result = await agent.run(query)
    print("\n\nFinal Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
