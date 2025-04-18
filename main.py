#!/usr/bin/env python3
"""
main.py
Entry point for the SingleAgent code assistant.
"""

import asyncio
import sys
from The_Agents.SingleAgent import SingleAgent

# ANSI escape codes
GREEN = "\033[32m"
RED   = "\033[31m"
BOLD  = "\033[1m"
RESET = "\033[0m"

async def main():
    agent = SingleAgent()
    # enter REPL loop
    while True:
        try:
            # prompt user in bold green
            query = input(f"{BOLD}{GREEN}User:{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break
        if not query.strip() or query.strip().lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        result = await agent.run(query)
        # print final agent output in bold red
        print(f"\n{BOLD}{RED}Agent:{RESET} {result}\n")

if __name__ == "__main__":
    asyncio.run(main())