#!/usr/bin/env python3
"""
Search for Topv3 repository specifically.
"""
import asyncio
import os
from The_Agents.MCPEnhancedSingleAgent_fixed import MCPEnhancedSingleAgent, CommonMCPConfigs

async def search_topv3():
    """Search specifically for Topv3 repository."""
    
    # Get GitHub token
    github_token = (os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT') or 
                   os.getenv('GH_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN'))
    
    if not github_token:
        print("❌ No GitHub token found!")
        return
    
    print(f"✅ GitHub token found: {github_token[:10]}...")
    
    # Create MCP configs with GitHub server
    mcp_configs = [
        CommonMCPConfigs.github_server(github_token)  # General access
    ]
    
    try:
        # Create and initialize the enhanced agent
        agent = MCPEnhancedSingleAgent(mcp_configs)
        await agent.initialize_mcp_servers()
        await agent.create_agent()
        
        print("✅ MCP agent initialized successfully!")
        
        # Search for Topv3 specifically
        print(f"\n🔍 Searching for 'Topv3' repository...")
        response = await agent.run(
            "Please search for a repository named 'Topv3' using the search_repositories tool. "
            "Search for 'Topv3' in my repositories. If you find it, please access it and "
            "read the contents of app.py file from that repository.",
            stream_output=False
        )
        
        print(f"\n📋 Search Result:")
        print(response)
        
        # Also try alternative searches
        print(f"\n🔍 Trying alternative searches...")
        response2 = await agent.run(
            "Please also search for repositories containing 'top' or 'v3' in the name, "
            "and list all my repositories (not just the first 10) to make sure we don't miss Topv3.",
            stream_output=False
        )
        
        print(f"\n📋 Alternative Search Result:")
        print(response2)
        
        # Cleanup
        await agent.cleanup()
        
    except Exception as e:
        print(f"❌ Error searching for Topv3: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(search_topv3())
