"""
Tool usage display utilities for agent implementations.
Provides standardized formatting and display of tool calls and outputs.
"""

import asyncio
import logging
from typing import Any, Dict, Optional, Union, List, Callable, AsyncIterable

from agents.stream_events import RunItemStreamEvent, RawResponsesStreamEvent, AgentUpdatedStreamEvent

# Configure logger
logger = logging.getLogger(__name__)

# ANSI color codes for display
GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW = "\033[33m"
BLUE  = "\033[34m" 
CYAN  = "\033[36m"
BOLD  = "\033[1m"
RESET = "\033[0m"

def format_tool_call(tool_name: Optional[str], tool_params: Any) -> str:
    """
    Format a tool call for display.
    
    Args:
        tool_name: Name of the tool being called
        tool_params: Parameters passed to the tool
        
    Returns:
        Formatted string for display
    """
    # Tool status indicator
    tool_status = f"{YELLOW}⚙{RESET}"  # Tool execution
    
    # Format tool parameters
    params_str = ""
    if tool_params:
        if isinstance(tool_params, dict):
            params_keys = list(tool_params.keys())
            if len(params_keys) > 2:
                params_str = f"({params_keys[0]}=..., +{len(params_keys)-1} more)"
            else:
                params_str = f"({', '.join(params_keys)})"
    
    # Create the display string
    if tool_name:
        return f"\n{tool_status} {tool_name}{params_str}"
    else:
        return f"\n{tool_status} Tool was called"

def format_tool_output(output: Any) -> Optional[str]:
    """
    Format tool output for display.
    
    Args:
        output: The output from a tool call
        
    Returns:
        Formatted string for display or None if no summary
    """
    output_summary = ""
    try:
        # Build a concise summary for general display
        if isinstance(output, dict):
            if 'error' in output:
                output_summary = f"Error: {str(output['error'])[:50]}..."
            else:
                keys = list(output.keys())
                output_summary = f"{len(keys)} fields: {', '.join(keys[:3])}"
                if len(keys) > 3:
                    output_summary += f", +{len(keys)-3} more"
        elif isinstance(output, list):
            output_summary = f"{len(output)} items"
        else:
            output_str = str(output)
            output_summary = output_str[:47] + "..." if len(output_str) > 50 else output_str
    except Exception as e:
        logger.warning(f"Could not summarize tool output: {str(e)}")
        return None
    
    # Return the summary if available
    if output_summary:
        return f"⮑ {output_summary}"
    return None

def handle_entity_tracking(context, tool_name: str, tool_params: Any) -> None:
    """
    Track entities based on tool calls.
    
    Args:
        context: The agent context object
        tool_name: Name of the tool being called
        tool_params: Parameters passed to the tool
    """
    if tool_name and tool_params and hasattr(context, "track_entity"):
        if tool_name in ("os_command", "run_command"):
            if isinstance(tool_params, dict) and "command" in tool_params:
                context.track_entity("command", tool_params["command"])
        elif tool_name == "read_file":
            if isinstance(tool_params, dict) and "file_path" in tool_params:
                context.track_entity("file", tool_params["file_path"])

def track_file_from_output(context, output: Dict[str, Any]) -> None:
    """
    Track file entity from tool output.
    
    Args:
        context: The agent context object
        output: Output from a tool call
    """
    if hasattr(context, "track_entity") and isinstance(output, dict):
        if 'file_path' in output and 'content' in output:
            context.track_entity(
                "file", 
                output['file_path'], 
                {"content_preview": output['content'][:100] if output['content'] else None}
            )

def display_agent_handoff(new_agent_name: str) -> None:
    """
    Display agent handoff notification.
    
    Args:
        new_agent_name: Name of the agent being handed off to
    """
    handoff_status = f"{BLUE}→{RESET}"  # Handoff indicator
    print(f"\n{handoff_status} Handoff to {new_agent_name}", flush=True)

def display_thinking_animation(thinking_chars: list, thinking_index: int) -> int:
    """
    Display a thinking animation and return the next animation index.
    
    Args:
        thinking_chars: List of characters for the animation
        thinking_index: Current index in the animation sequence
        
    Returns:
        Next index in the animation sequence
    """
    print("\r", end="", flush=True)
    thinking_index = (thinking_index + 1) % len(thinking_chars)
    print(f"{thinking_chars[thinking_index]} ", end="", flush=True)
    return thinking_index

def clear_thinking_animation() -> None:
    """Clear the thinking animation from the terminal."""
    print("\r" + " " * 10 + "\r", end="", flush=True)

async def process_stream_event(event, context, item_helpers, output_text_buffer: str = "") -> tuple:
    """
    Process a single stream event and update the output buffer.
    
    Args:
        event: The event to process
        context: The agent context
        item_helpers: ItemHelpers from the agents module
        output_text_buffer: Current output buffer
        
    Returns:
        Tuple of (updated_buffer, processed_output, consume_event)
    """
    processed_output = ""
    consume_event = False
    
    # Handle raw response events (token-by-token streaming)
    if isinstance(event, RawResponsesStreamEvent):
        try:
            from openai.types.responses import ResponseTextDeltaEvent
            if hasattr(event, 'data') and isinstance(event.data, ResponseTextDeltaEvent):
                # Clear thinking indicator if this is first text
                if not output_text_buffer:
                    clear_thinking_animation()
                
                # Get text delta
                delta = event.data.delta
                
                # Print text deltas in real-time
                print(delta, end="", flush=True)
                output_text_buffer += delta
                consume_event = True
        except ImportError:
            # Handle case where ResponseTextDeltaEvent is not available
            pass
    
    # Handle agent handoff/update events
    elif isinstance(event, AgentUpdatedStreamEvent):
        display_agent_handoff(event.new_agent.name)
        consume_event = True
    
    # Process run item events
    elif isinstance(event, RunItemStreamEvent):
        item = event.item
        
        # Track tool calls for entity tracking
        if item.type == 'tool_call_item':
            # Extract tool name and parameters
            tool_name = getattr(item, 'name', None) or getattr(item, 'tool_name', None)
            tool_params = getattr(item, 'params', None) or getattr(item, 'input', None)
            
            # Track entities based on tool call
            handle_entity_tracking(context, tool_name, tool_params)
            
            # Format and display tool call
            tool_call_display = format_tool_call(tool_name, tool_params)
            print(tool_call_display, flush=True)
            processed_output += tool_call_display
            consume_event = True
        
        # Tool output
        elif item.type == 'tool_call_output_item':
            # Handle output from tool calls
            try:
                if hasattr(item, 'output'):
                    output = item.output
                    
                    # Track file content from read_file as metadata
                    track_file_from_output(context, output)
                    
                    # Format and display tool output
                    output_summary = format_tool_output(output)
                    if output_summary:
                        print(output_summary, flush=True)
                        processed_output += f"\n{output_summary}"
                    consume_event = True
            except Exception as e:
                logger.warning(f"Could not process tool output: {str(e)}")
        
        # Assistant message output (don't show separately if already shown via streaming)
        elif item.type == 'message_output_item' and not output_text_buffer:
            # Use the helper function to extract just the text content without duplication
            content = item_helpers.text_message_output(item)
            # Only print non-empty content if no raw streaming occurred to avoid duplicates
            if content.strip():
                print(content, end='', flush=True)
                output_text_buffer = content
                consume_event = True
    
    return output_text_buffer, processed_output, consume_event

async def handle_stream_events(stream_events, context, logger, item_helpers) -> str:
    """
    Handle streaming events from an agent run.
    
    Args:
        stream_events: Async iterator of stream events
        context: The agent context
        logger: Logger instance for logging events
        item_helpers: ItemHelpers from the agents module
        
    Returns:
        The final output buffer
    """
    # Status indicators
    thinking_chars = ["⋮", "⋰", "⋯", "⋱"]  # Rotating dots pattern
    
    # Animation variables
    thinking_index = 0
    last_animation_time = asyncio.get_event_loop().time()
    animation_interval = 0.2  # seconds between animation frames
    
    # Output buffer for collecting the response
    output_text_buffer = ""
    
    # Print initial thinking indicator
    print(f"{thinking_chars[thinking_index]} ", end="", flush=True)
    
    try:
        async for event in stream_events:
            # Animate the thinking indicator while waiting
            current_time = asyncio.get_event_loop().time()
            if current_time - last_animation_time > animation_interval:
                if not output_text_buffer:  # Only animate if no output yet
                    # Update the animation
                    thinking_index = display_thinking_animation(thinking_chars, thinking_index)
                    last_animation_time = current_time
            
            # Process this event
            output_text_buffer, processed_output, consumed = await process_stream_event(
                event, context, item_helpers, output_text_buffer
            )
            
            # If event wasn't handled by our processing, log it
            if not consumed:
                logger.debug(f"Unhandled event type: {type(event).__name__}")
            
    except Exception as e:
        logger.error(f"Error in stream event handling: {e}")
        print(f"\n{RED}Error: {e}{RESET}")
        
    # Print a newline at the end
    print()
    
    return output_text_buffer
