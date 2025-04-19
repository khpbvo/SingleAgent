"""
SingleAgent implementation for code assistant that follows OpenAI Agents SDK patterns.
Features:
- Terminal control
- Pylint integration
- Colored diff generation
- Patch application
- Streaming responses
- Chain of thought reasoning
- Chat memory for storing up to 25 messages
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import asyncio
import os
import sys
import logging
import json
import re
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

IMPORTANT: You have access to chat history memory that stores up to 25 previous messages.
Always use the get_context tool to check the chat history before responding.
When referring to previous conversations, use this history as reference.
If asked about previous interactions or commands, check the chat history using get_context.

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

Use your run_command to execute the apply_patch.py file to apply patches to files.
python apply_patch.py <<"EOF"
*** Begin Patch
[YOUR_PATCH]
*** End Patch
EOF

Where [YOUR_PATCH] is the actual content of your patch, specified in the following V4A diff format.

*** [ACTION] File: [path/to/file] -> ACTION can be one of Add, Update, or Delete.
For each snippet of code that needs to be changed, repeat the following:
[context_before] -> See below for further instructions on context.
- [old_code] -> Precede the old code with a minus sign.
+ [new_code] -> Precede the new, replacement code with a plus sign.
[context_after] -> See below for further instructions on context.

For instructions on [context_before] and [context_after]:
- By default, show 3 lines of code immediately above and 3 lines immediately below each change. If a change is within 3 lines of a previous change, do NOT duplicate the first change's [context_after] lines in the second change's [context_before] lines.
- If 3 lines of context is insufficient to uniquely identify the snippet of code within the file, use the @@ operator to indicate the class or function to which the snippet belongs. For instance, we might have:
@@ class BaseClass
[3 lines of pre-context]
- [old_code]
+ [new_code]
[3 lines of post-context]

- If a code block is repeated so many times in a class or function such that even a single @@ statement and 3 lines of context cannot uniquely identify the snippet of code, you can use multiple `@@` statements to jump to the right context. For instance:

@@ class BaseClass
@@ 	def method():
[3 lines of pre-context]
- [old_code]
+ [new_code]
[3 lines of post-context]

Note, then, that we do not use line numbers in this diff format, as the context is enough to uniquely identify code. An example of a message that you might pass as "input" to this function, in order to apply a patch, is shown below.

python apply_patch.py <<"EOF"
*** Begin Patch
*** Update File: pygorithm/searching/binary_search.py
@@ class BaseClass
@@     def search():
-        pass
+        raise NotImplementedError()

@@ class Subclass
@@     def search():
-        pass
+        raise NotImplementedError()

*** End Patch
EOF

File references can only be relative, NEVER ABSOLUTE. After the apply_patch command is run, python will always say "Done!", regardless of whether the patch was successfully applied or not. However, you can determine if there are issue and errors by looking at any warnings or logging lines printed BEFORE the "Done!" is output.



Remember to show your reasoning at each step of the process. Consider different approaches, evaluate trade-offs,
and explain why you chose a particular solution.
"""

class SingleAgent:
    """
    A single agent implementation for code assistance with streaming capability 
    and terminal control.
    """
    
    def _apply_default_file_context(self, user_input: str) -> str:
        """
        Als de user spreekt over specifieke code-aanpassing maar geen .py noemt,
        voeg dan automatisch het meest recent bewerkte bestand toe uit de context.
        """
        if re.search(r'\b(functie|method|toevoeg|wijzig|patch)\b', user_input, re.IGNORECASE) \
           and not re.search(r'\w+\.py\b', user_input):
            recent = self.context.get_recent_files()
            if recent:
                return f"{user_input} in {recent[0]}"
        return user_input
    
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
        # Preprocess: vul default bestand toe als geen .py genoemd wordt
        user_input = self._apply_default_file_context(user_input)
        # Add (mogelijk aangevulde) user message to chat history
        self.context.add_chat_message("user", user_input)
        
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
            
        # Add assistant response to chat history
        self.context.add_chat_message("assistant", out)
        
        # log end of run
        logger.debug(json.dumps({
            "event": "run_end", 
            "output": out,
            "chat_history_length": len(self.context.chat_messages)
        }))
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
        # Preprocess ook voor streaming flow
        user_input = self._apply_default_file_context(user_input)
        print("Starting agent met streaming output...")
        
        result = Runner.run_streamed(
            starting_agent=self.agent,
            input=user_input,
            max_turns=35,  # unlimited turns
            context=self.context,
        )
        
        from agents.stream_events import RunItemStreamEvent, RawResponsesStreamEvent, AgentUpdatedStreamEvent
        try:
            async for event in result.stream_events():
                # Skip low-level raw events
                if isinstance(event, RawResponsesStreamEvent):
                    continue
                # Handle agent handoff/update events
                if isinstance(event, AgentUpdatedStreamEvent):
                    print(f"Agent updated: {event.new_agent.name}")
                    continue
                # Only process run item events
                if not isinstance(event, RunItemStreamEvent):
                    continue
                item = event.item
                # Tool invocation
                if item.type == 'tool_call_item':
                    raw = event.raw_item
                    tool = getattr(raw, 'name', 'unknown_tool')
                    params = {}
                    raw_args = getattr(raw, 'arguments', None)
                    if raw_args:
                        try:
                            params = json.loads(raw_args).get('params', {})
                        except:
                            params = {}
                    print(f"{tool}: {json.dumps(params)}")
                # Tool output
                elif item.type == 'tool_call_output_item':
                    print(f"-- Tool output: {item.output}")
                # Assistant message output
                elif item.type == 'message_output_item':
                    print(ItemHelpers.text_message_output(item), end='', flush=True)
                # ignore other event item types
                else:
                    continue
        except MaxTurnsExceeded as e:
            print(f"\n[Error] Max turns exceeded: {e}\n")
            logger.debug(json.dumps({"event": "max_turns_exceeded", "error": str(e)}))
        # final output (Agent reply)
        final = result.final_output
        logger.debug(json.dumps({"event": "_run_streamed_end", "final_output": final}))
        return final

    def get_chat_history_summary(self) -> str:
        """Return a summary of the chat history for display."""
        return self.context.get_chat_summary()
    
    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        self.context.clear_chat_history()
        logger.debug(json.dumps({"event": "chat_history_cleared"}))

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
        
        # Special commands
        if query.strip().lower() == "!history":
            print(f"\n{agent.get_chat_history_summary()}\n")
            continue
        elif query.strip().lower() == "!clear":
            agent.clear_chat_history()
            print("\nChat history cleared.\n")
            continue

        result = await agent.run(query)
        print(f"\n{BOLD}{RED}Agent:{RESET} {result}\n")

if __name__ == "__main__":
    asyncio.run(main())
