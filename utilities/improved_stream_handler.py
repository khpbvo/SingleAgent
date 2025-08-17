"""
Improved stream event handler for SingleAgent
Handles all types of streaming events robustly
"""

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ANSI color codes
GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW = "\033[33m"
BLUE  = "\033[34m"
CYAN  = "\033[36m"
BOLD  = "\033[1m"
RESET = "\033[0m"

async def handle_stream_events_improved(stream_events, context=None, logger=None, item_helpers=None):
    """
    Improved stream event handler that doesn't get stuck
    """
    # Fallbacks for optional params
    if logger is None:
        logger = logging.getLogger(__name__)
    output_buffer = []
    print_buffer = []
    thinking_shown = False
    # Keep a rolling buffer of raw text and last seen params to infer tool names
    raw_text_accumulator = ""
    last_params_seen: Optional[Dict[str, Any]] = None
    
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
                        # Accumulate raw text and try to capture params JSON
                        try:
                            raw_text_accumulator += delta
                            # Only keep recent tail to bound memory
                            if len(raw_text_accumulator) > 4000:
                                raw_text_accumulator = raw_text_accumulator[-4000:]
                            # Heuristic: find last occurrence of '"params":'
                            anchor = raw_text_accumulator.rfind('"params"')
                            if anchor != -1:
                                # Try to find matching braces around a JSON object starting near anchor
                                start = raw_text_accumulator.rfind('{', 0, anchor)
                                end = raw_text_accumulator.find('}', anchor)
                                if start != -1 and end != -1:
                                    snippet = raw_text_accumulator[start:end+1]
                                    # Try strict JSON parse
                                    import json as _json
                                    try:
                                        obj = _json.loads(snippet)
                                        if isinstance(obj, dict) and 'params' in obj and isinstance(obj['params'], dict):
                                            last_params_seen = obj['params']
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                    
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
                        # Extract tool name and parameters; Agents SDK may nest these differently.
                        # Try multiple shapes: item.tool.name, item.name, item.tool_name, item.call.tool.name, item.call.tool_name
                        call = getattr(item, 'call', None)
                        tool_obj = (
                            getattr(item, 'tool', None)
                            or (getattr(call, 'tool', None) if call else None)
                        )
                        tool_name = (
                            getattr(tool_obj, 'name', None)
                            or getattr(tool_obj, 'tool_name', None)
                            or getattr(item, 'name', None)
                            or getattr(item, 'tool_name', None)
                            or (getattr(call, 'tool_name', None) if call else None)
                        )
                        
                        # Extract params/arguments from multiple possible fields
                        params = (
                            getattr(item, 'params', None)
                            or getattr(item, 'input', None)
                            or (getattr(call, 'arguments', None) if call else None)
                            or (getattr(call, 'params', None) if call else None)
                            or (getattr(call, 'input', None) if call else None)
                            or getattr(item, 'arguments', None)
                            or getattr(item, 'arguments_json', None)
                        ) or {}
                        
                        # Best-effort JSON parse if params look like JSON in a string
                        if isinstance(params, str):
                            try:
                                parsed = json.loads(params)
                                params = parsed
                            except Exception:
                                pass
                        
                        # Infer tool name heuristically if missing
                        inferred_name = tool_name
                        if not inferred_name and isinstance(params, dict):
                            if 'include_details' in params:
                                inferred_name = 'get_context'
                            elif 'directory' in params:
                                inferred_name = 'change_dir'
                            elif 'command' in params:
                                inferred_name = 'run_command'
                            elif 'file_path' in params:
                                inferred_name = 'read_file'
                        # Do not show a noisy fallback label; leave it unspecified if still unknown
                        label_to_show = inferred_name if inferred_name else None

                        # If we still have no params, fall back to last seen params from raw stream
                        if not params and last_params_seen:
                            params = last_params_seen
                        if label_to_show:
                            print(f"\n{YELLOW}⚙{RESET} Calling: {label_to_show}", flush=True)
                        else:
                            # Generic, friendly fallback without an "Unknown" label
                            print(f"\n{YELLOW}⚙{RESET} Calling tool", flush=True)
                        # Clear last seen params after using
                        last_params_seen = None
                        
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
                        if item_helpers is not None and hasattr(item_helpers, 'text_message_output'):
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
