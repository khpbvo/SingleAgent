#!/usr/bin/env python3
"""
Test the MCP agent with general GitHub access to find and read TopV3/app.py.
"""
import asyncio
import os
from The_Agents.MPCEnhancedSingleAgent_fixed import MCPEnhancedSingleAgent, CommonMCPConfigs

async def test_topv3_general_access():
    """Test accessing TopV3 with general GitHub access."""
    
    # Get GitHub token
    github_token = (os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT') or 
                   os.getenv('GH_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN'))
    
    if not github_token:
        print("❌ No GitHub token found!")
        return
    
    print(f"✅ GitHub token found: {github_token[:10]}...")
    
    # Create MCP configs with general GitHub server access
    mcp_configs = [
        CommonMCPConfigs.github_server(github_token)  # General access without specifying repo
    ]
    
    try:
        # Create and initialize the enhanced agent
        agent = MCPEnhancedSingleAgent(mcp_configs)
        await agent.initialize_mcp_servers()
        await agent.create_agent()
        
        print("✅ MCP agent initialized successfully!")
        
        # Test finding and accessing TopV3 repository
        print(f"\n🔍 Finding TopV3 repository and reading app.py...")
        response = await agent.run(
            "I need to find my repository called 'TopV3' (note the capital T and V). "
            "Please search my repositories to find 'TopV3' and then read the 'app.py' file from that repository. "
            "The repository should be under the owner 'khpbvo'. "
            "Use the search_repositories tool first to find it, then get_file_contents to read app.py.",
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
    asyncio.run(test_topv3_general_access())
