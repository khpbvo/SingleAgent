#!/usr/bin/env python3
"""
main.py
Entry point for the SingleAgent code assistant.
"""

import asyncio
import sys
import logging
import json
from The_Agents.SingleAgent import SingleAgent

# ANSI escape codes
GREEN = "\033[32m"
RED   = "\033[31m"
BOLD  = "\033[1m"
RESET = "\033[0m"

async def main():
    # configure root logger for JSON logging
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    agent = SingleAgent()
    # enter REPL loop
    while True:
        try:
            # read user input and log it
            query = input(f"{BOLD}{GREEN}User:{RESET} ")
            logging.debug(json.dumps({"event": "user_input", "input": query}))
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break
        if not query.strip() or query.strip().lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        # run agent and log response
        result = await agent.run(query)
        logging.debug(json.dumps({"event": "agent_response", "response": result}))
        # print final agent output in bold red
        print(f"\n{BOLD}{RED}Agent:{RESET} {result}\n")

if __name__ == "__main__":
    asyncio.run(main())