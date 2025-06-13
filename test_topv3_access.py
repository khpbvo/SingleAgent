#!/usr/bin/env python3
"""
Test the MCP agent with the correct TopV3 repository name and read app.py.
"""
import asyncio
import os
from The_Agents.MCPEnhancedSingleAgent_fixed import MCPEnhancedSingleAgent, CommonMCPConfigs

async def test_topv3_access():
    """Test accessing the TopV3 repository correctly."""
    
    # Get GitHub token
    github_token = (os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT') or 
                   os.getenv('GH_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN'))
    
    if not github_token:
        print("❌ No GitHub token found!")
        return
    
    print(f"✅ GitHub token found: {github_token[:10]}...")
    
    # Create MCP configs with GitHub server configured for the TopV3 repository
    mcp_configs = [
        CommonMCPConfigs.github_server(github_token, "khpbvo", "TopV3")  # Specify the correct repo
    ]
    
    try:
        # Create and initialize the enhanced agent
        agent = MCPEnhancedSingleAgent(mcp_configs)
        await agent.initialize_mcp_servers()
        await agent.create_agent()
        
        print("✅ MCP agent initialized successfully!")
        
        # Test accessing TopV3 repository and reading app.py
        print(f"\n🔍 Accessing TopV3 repository and reading app.py...")
        response = await agent.run(
            "I want to access my TopV3 repository and read the app.py file. "
            "Please use the get_file_contents tool to read the app.py file from the khpbvo/TopV3 repository. "
            "Show me the beginning of the file to understand what this application does.",
            stream_output=False
        )
        
        print(f"\n📋 Agent Response:")
        print(response)
        
        # Cleanup
        await agent.cleanup()
        
    except Exception as e:
        print(f"❌ Error accessing TopV3: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_topv3_access())
