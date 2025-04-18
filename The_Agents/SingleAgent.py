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
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import asyncio
import os
import sys
import logging
import json
from logging.handlers import RotatingFileHandler

# Configure logger for SingleAgent
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
single_handler = RotatingFileHandler('singleagent.log', maxBytes=10*1024*1024, backupCount=3)
single_handler.setLevel(logging.DEBUG)
single_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(single_handler)
logger.propagate = False

# ANSI color codes for REPL
GREEN = "\033[32m"
RED   = "\033[31m"
BOLD  = "\033[1m"
RESET = "\033[0m"

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
from Tools.tools_single_agent import (
    run_ruff,
    run_pylint,
    run_pyright,
    run_command,
    read_file,
    create_colored_diff,
    apply_patch,
    change_dir,
    os_command,
    get_context
)
from utils.project_info import discover_project_info
from agents.exceptions import MaxTurnsExceeded
from The_Agents.context_data import EnhancedContextData

# Constants
AGENT_INSTRUCTIONS = """
You are a code assistant capable of helping users write, edit, and patch code.
You have full control of the terminal and can run commands like sed, grep, ls, dir, cd, tail, python, and bash.
You can analyze code with pylint, ruff and pyright, generate colored diffs, and apply patches to files.
Your thinking should be thorough and so it's fine if it's very long. You can think step by step before and after each action you decide to take.
You MUST iterate and keep going until the problem is solved.
You already have everything you need to solve this problem in your tools, fully solve this autonomously before coming back to me.
Only terminate your turn when you are sure that the problem is solved. Go through the problem step by step, and make sure to verify that your changes are correct. NEVER end your turn without having solved the problem, and when you say you are going to make a tool call, make sure you ACTUALLY make the tool call, instead of ending your turn.
Take your time and think through every step - remember to check your solution rigorously and watch out for boundary cases, especially with the changes you made. Your solution must be perfect. If not, continue working on it. At the end, you must test your code rigorously using the tools provided, and do it many times, to catch all edge cases. If it is not robust, iterate more and make it perfect. Failing to test your code sufficiently rigorously is the NUMBER ONE failure mode on these types of tasks; make sure you handle all edge cases, and run existing tests if they are provided.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.
# Workflow
## High-Level Problem Solving Strategy
1. Understand the problem deeply. Carefully read the issue and think critically about what is required.
2. Investigate the codebase. Explore relevant files, search for key functions, and gather context.
3. Develop a clear, step-by-step plan. Break down the fix into manageable, incremental steps.
4. Implement the fix incrementally. Make small, testable code changes.
5. Debug as needed. Use debugging techniques to isolate and resolve issues.
6. Test frequently. Run tests after each change to verify correctness.
7. Iterate until the root cause is fixed and all tests pass.
8. Reflect and validate comprehensively. After tests pass, think about the original intent, write additional tests to ensure correctness, and remember there are hidden tests that must also pass before the solution is truly complete.

## 1. Deeply Understand the Problem
Carefully read the issue and think hard about a plan to solve it before coding.

## 2. Codebase Investigation
- Explore relevant files and directories.
- Search for key functions, classes, or variables related to the issue.
- Read and understand relevant code snippets.
- Identify the root cause of the problem.
- Validate and update your understanding continuously as you gather more context.

## 3. Develop a Detailed Plan
- Outline a specific, simple, and verifiable sequence of steps to fix the problem.
- Break down the fix into small, incremental changes.

## 4. Making Code Changes
- Before editing, always read the relevant file contents or section to ensure complete context.
- If a patch is not applied correctly, attempt to reapply it.
- Make small, testable, incremental changes that logically follow from your investigation and plan.

## 5. Debugging
- Make code changes only if you have high confidence they can solve the problem
- When debugging, try to determine the root cause rather than addressing symptoms
- Debug for as long as needed to identify the root cause and identify a fix
- Use print statements, logs, or temporary code to inspect program state, including descriptive statements or error messages to understand what's happening
- To test hypotheses, you can also add test statements or functions
- Revisit your assumptions if unexpected behavior occurs.

## 6. Testing
- Run tests frequently using `!python3 run_tests.py` (or equivalent).
- After each change, verify correctness by running relevant tests.
- If tests fail, analyze failures and revise your patch.
- Write additional tests if needed to capture important behaviors or edge cases.
- Ensure all tests pass before finalizing.

## 7. Final Verification
- Confirm the root cause is fixed.
- Review your solution for logic correctness and robustness.
- Iterate until you are extremely confident the fix is complete and all tests pass.

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

class SingleAgent:
    """
    A single agent implementation for code assistance with streaming capability 
    and terminal control.
    """
    
    def __init__(self):
        """Initialize the code assistant agent with all required tools and enhanced context."""
        # Use EnhancedContextData so tools can store memory
        self.agent = Agent[EnhancedContextData](
            name="CodeAssistant",
            model="gpt-4.1",
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
                os_command,
                get_context  # include context inspection tool
            ]
        )
        
        cwd = os.getcwd()
        self.context = EnhancedContextData(
            working_directory=cwd,
            project_info=discover_project_info(cwd),
            current_file=None,
            memory_items=[],
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
        # log start of run
        logger.debug(json.dumps({"event": "run_start", "user_input": user_input}))
        if stream_output:
            out = await self._run_streamed(user_input)
        else:
            res = await Runner.run(
                starting_agent=self.agent,
                input=user_input,
                context=self.context,
            )
            out = res.final_output
        # log end of run
        logger.debug(json.dumps({"event": "run_end", "output": out}))
        return out
    
    async def _run_streamed(self, user_input: str) -> str:
        """
        Run the agent with streamed output.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            The final output from the agent
        """
        # log start of streamed
        logger.debug(json.dumps({"event": "_run_streamed_start", "user_input": user_input}))
        print("Starting agent with streaming output...")
        
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=user_input,
            max_turns=35,  # unlimited turns
            context=self.context,
        )
        
        from agents.stream_events import RunItemStreamEvent
        try:
            async for event in result.stream_events():
                # Only handle RunItemStreamEvent which has 'item'
                if not isinstance(event, RunItemStreamEvent):
                    continue
                item = event.item
                # Detect tool call start
                if item.type == 'tool_call_item':
                    raw = item.raw_item
                    # get tool name from raw function call metadata
                    tool = getattr(raw, 'name', 'unknown_tool')
                    # extract params safely
                    params = {}
                    raw_args = getattr(raw, 'arguments', None)
                    if raw_args:
                        try:
                            params = json.loads(raw_args).get('params', {})
                        except Exception:
                            params = {}
                    # Removed printing of tool call details to console
                elif item.type == 'tool_call_output_item':
                    output = item.output
                    # Removed printing of tool output details to console
        except MaxTurnsExceeded as e:
            print(f"\n[Error] Max turns exceeded: {e}\n")
            logger.debug(json.dumps({"event": "max_turns_exceeded", "error": str(e)}))
        # final output (Agent reply)
        final = result.final_output
        logger.debug(json.dumps({"event": "_run_streamed_end", "final_output": final}))
        return final


async def main():
    agent = SingleAgent()
    # enter REPL loop
    while True:
        try:
            query = input(f"{BOLD}{GREEN}User:{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break
        if not query.strip() or query.strip().lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        result = await agent.run(query)
        print(f"\n{BOLD}{RED}Agent:{RESET} {result}\n")

if __name__ == "__main__":
    asyncio.run(main())
