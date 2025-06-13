#!/usr/bin/env python3
"""
Test script to check GitHub access and find the Topv3 repository.
"""
import asyncio
import os
import sys
from The_Agents.MCPEnhancedSingleAgent_fixed import MCPEnhancedSingleAgent, CommonMCPConfigs

async def test_github_access():
    """Test GitHub MCP server access and search for Topv3 repository."""
    
    # Get GitHub token
    github_token = (os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT') or 
                   os.getenv('GH_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN'))
    
    if not github_token:
        print("❌ No GitHub token found!")
        return
    
    print(f"✅ GitHub token found: {github_token[:10]}...")
    
    # Create MCP configs with GitHub server
    mcp_configs = [
        CommonMCPConfigs.github_server(github_token)  # General access without specific repo
    ]
    
    try:
        # Create and initialize the enhanced agent
        agent = MCPEnhancedSingleAgent(mcp_configs)
        await agent.initialize_mcp_servers()
        await agent.create_agent()
        
        print("✅ MCP agent initialized successfully!")
        
        # List available tools
        tools_info = await agent.list_available_tools()
        print(f"\n🔧 Available GitHub tools:")
        github_tools = tools_info.get("mcp_tools", {}).get("github", [])
        for tool in github_tools:
            print(f"  - {tool}")
        
        # Test GitHub functionality by asking the agent to find Topv3
        print(f"\n🔍 Searching for Topv3 repository...")
        response = await agent.run(
            "Can you search for and access my repository called 'Topv3'? "
            "Please list my repositories and then try to find Topv3. "
            "If you find it, please read the app.py file from that repository.",
            stream_output=False
        )
        
        print(f"\n📋 Agent Response:")
        print(response)
        
        # Cleanup
        await agent.cleanup()
        
    except Exception as e:
        print(f"❌ Error testing GitHub access: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_github_access())
