#!/usr/bin/env python3
"""
Fix for SingleAgent streaming issues - comprehensive solution
"""

import os
import sys

def fix_model_name():
    """Fix the incorrect model name in MCPEnhancedSingleAgent_fixed.py"""
    file_path = "The_Agents/MCPEnhancedSingleAgent_fixed.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix model name - use gpt-4-turbo or gpt-4o
    content = content.replace('model="gpt-5"', 'model="gpt-4o"')
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed model name in {file_path}")

def fix_tool_usage():
    """Fix the stream event handling in tool_usage.py"""
    file_path = "utilities/tool_usage.py"
    
    # Read the current file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find and replace the problematic section
    new_content = []
    in_raw_response_section = False
    
    for i, line in enumerate(lines):
        if "if isinstance(event, RawResponsesStreamEvent):" in line:
            in_raw_response_section = True
            # Replace the entire RawResponsesStreamEvent handling section
            new_content.append(line)
            new_content.append("""        # Handle raw streaming events with proper fallback
        if hasattr(event, 'data'):
            data = event.data
            
            # Check for text delta events by attributes rather than type
            if hasattr(data, 'delta'):
                if not output_text_buffer:
                    clear_thinking_animation()
                
                delta = data.delta
                print_buffer.append(delta)
                output_text_buffer.append(delta)
                consume_event = True
                
                flush_output = ""
                joined_buffer = "".join(print_buffer)
                
                # Flush when newline present
                if "\\n" in joined_buffer:
                    newline_index = joined_buffer.rfind("\\n") + 1
                    flush_output = joined_buffer[:newline_index]
                    remainder = joined_buffer[newline_index:]
                    print_buffer.clear()
                    if remainder:
                        print_buffer.append(remainder)
                elif len(joined_buffer) >= STREAMING_FLUSH_THRESHOLD:
                    flush_output = joined_buffer
                    print_buffer.clear()
                
                if flush_output:
                    print(flush_output, end="", flush=True)
            
            # Check for completion events
            elif hasattr(data, 'type') and 'done' in str(data.type).lower():
                if print_buffer:
                    print("".join(print_buffer), end="", flush=True)
                    print_buffer.clear()
                consume_event = True
        else:
            # Log raw response for debugging but mark as consumed
            logger.debug(f"Raw response event without data: {type(event)}")
            consume_event = True
""")
            # Skip the original implementation
            skip_until_outdent = True
            continue
        elif in_raw_response_section and not line.startswith('    '):
            in_raw_response_section = False
            new_content.append(line)
        elif not in_raw_response_section:
            new_content.append(line)
    
    # Write the fixed content
    with open(file_path, 'w') as f:
        f.writelines(new_content)
    
    print(f"✅ Fixed stream event handling in {file_path}")

def create_improved_handler():
    """Create an improved stream handler as a separate module"""
    
    improved_handler = '''"""
Improved stream event handler for SingleAgent
Handles all types of streaming events robustly
"""

import asyncio
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)

# ANSI color codes
GREEN = "\\033[32m"
RED   = "\\033[31m"
YELLOW = "\\033[33m"
BLUE  = "\\033[34m"
CYAN  = "\\033[36m"
BOLD  = "\\033[1m"
RESET = "\\033[0m"

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
                            print("\\r" + " " * 20 + "\\r", end="", flush=True)  # Clear thinking indicator
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
                        
                        print(f"\\n{YELLOW}⚙{RESET} Calling: {tool_name}", flush=True)
                        
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
                    print(f"\\n{BLUE}→{RESET} Switching to {event.new_agent.name}", flush=True)
                continue
            
            # For any unhandled events, just log them but don't block
            logger.debug(f"Processing event type: {event_type}")
        
    except Exception as e:
        logger.error(f"Error in stream handler: {e}")
        print(f"\\n{RED}Stream error: {e}{RESET}")
    
    # Final cleanup
    if print_buffer:
        print("".join(print_buffer), flush=True)
    
    print()  # Final newline
    return "".join(output_buffer)
'''
    
    with open('utilities/improved_stream_handler.py', 'w') as f:
        f.write(improved_handler)
    
    print("✅ Created improved stream handler at utilities/improved_stream_handler.py")

def update_usage_imports():
    """Update the imports to use the improved handler"""
    
    files_to_update = [
        "The_Agents/SingleAgent.py",
        "The_Agents/MCPEnhancedSingleAgent_fixed.py"
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add fallback import
            if "from utilities.tool_usage import handle_stream_events" in content:
                content = content.replace(
                    "from utilities.tool_usage import handle_stream_events",
                    """try:
    from utilities.improved_stream_handler import handle_stream_events_improved as handle_stream_events
except ImportError:
    from utilities.tool_usage import handle_stream_events"""
                )
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ Updated imports in {file_path}")

def main():
    """Apply all fixes"""
    print("🔧 Fixing SingleAgent streaming issues...")
    print("-" * 50)
    
    # Change to the SingleAgent directory
    os.chdir('/Users/kevinvanosch/Documents/SingleAgent')
    
    try:
        # Apply all fixes
        fix_model_name()
        create_improved_handler()
        update_usage_imports()
        
        print("-" * 50)
        print("✅ All fixes applied successfully!")
        print("\n📝 Summary of changes:")
        print("1. Fixed model name from 'gpt-5' to 'gpt-4o'")
        print("2. Created improved stream event handler")
        print("3. Updated imports to use improved handler with fallback")
        print("\n🚀 To test the fixes:")
        print("1. Restart your SingleAgent program")
        print("2. Switch to MCP mode with !mcp")
        print("3. Try calling tools - they should no longer get stuck")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        print("Please check the error and try again")

if __name__ == "__main__":
    main()
