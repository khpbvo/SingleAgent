"""
Improved stream event handler for SingleAgent
Handles all types of streaming events robustly
"""

import asyncio
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)

# ANSI color codes
GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW = "\033[33m"
BLUE  = "\033[34m"
CYAN  = "\033[36m"
BOLD  = "\033[1m"
RESET = "\033[0m"

async def handle_stream_events_improved(stream_events, context, item_helpers):
    """
    Improved stream event handler that doesn't get stuck
    """
    output_buffer = []
    print_buffer = []
    thinking_shown = False
    
    try:
        async for event in stream_events:
            event_type = type(event).__name__
            
            # Handle different event types
            if "RawResponse" in event_type:
                # Process raw streaming responses
                if hasattr(event, 'data'):
                    data = event.data
                    
                    # Text streaming
                    if hasattr(data, 'delta'):
                        if not thinking_shown:
                            print("\r" + " " * 20 + "\r", end="", flush=True)  # Clear thinking indicator
                            thinking_shown = True
                        
                        delta = str(data.delta) if not isinstance(data.delta, str) else data.delta
                        output_buffer.append(delta)
                        print(delta, end="", flush=True)
                    
                    # Completion event
                    elif hasattr(data, 'type'):
                        if 'done' in str(data.type).lower() or 'complete' in str(data.type).lower():
                            if print_buffer:
                                print("".join(print_buffer), flush=True)
                                print_buffer.clear()
                continue
            
            elif "RunItemStreamEvent" in event_type:
                item = event.item if hasattr(event, 'item') else None
                if item:
                    # Tool call
                    if hasattr(item, 'type') and 'tool_call' in item.type:
                        tool_name = getattr(item, 'name', None) or getattr(item, 'tool_name', 'Unknown tool')
                        params = getattr(item, 'params', None) or getattr(item, 'input', {})
                        
                        print(f"\n{YELLOW}⚙{RESET} Calling: {tool_name}", flush=True)
                        
                        # Show parameters summary
                        if params and isinstance(params, dict):
                            param_keys = list(params.keys())[:3]
                            if param_keys:
                                print(f"   Parameters: {', '.join(param_keys)}", flush=True)
                    
                    # Tool output
                    elif hasattr(item, 'type') and 'output' in item.type:
                        if hasattr(item, 'output'):
                            output = item.output
                            # Summarize output
                            if isinstance(output, dict):
                                if 'error' in output:
                                    print(f"   {RED}✗ Error: {str(output['error'])[:100]}{RESET}", flush=True)
                                else:
                                    print(f"   {GREEN}✓ Success{RESET}", flush=True)
                            else:
                                print(f"   {GREEN}✓ Complete{RESET}", flush=True)
                    
                    # Message output
                    elif hasattr(item, 'type') and 'message' in item.type:
                        if hasattr(item_helpers, 'text_message_output'):
                            content = item_helpers.text_message_output(item)
                            if content and content.strip():
                                output_buffer.append(content)
                                print(content, end='', flush=True)
                continue
            
            elif "AgentUpdatedStreamEvent" in event_type:
                if hasattr(event, 'new_agent'):
                    print(f"\n{BLUE}→{RESET} Switching to {event.new_agent.name}", flush=True)
                continue
            
            # For any unhandled events, just log them but don't block
            logger.debug(f"Processing event type: {event_type}")
        
    except Exception as e:
        logger.error(f"Error in stream handler: {e}")
        print(f"\n{RED}Stream error: {e}{RESET}")
    
    # Final cleanup
    if print_buffer:
        print("".join(print_buffer), flush=True)
    
    print()  # Final newline
    return "".join(output_buffer)
