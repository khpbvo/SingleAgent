"""Visualize the SingleAgent system architecture."""

import sys
import os
from pathlib import Path

# Add the SingleAgent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define output directory for visualizations
VISUALIZATION_DIR = Path(__file__).parent / "agent_visualizations"

# Check if the visualization extension is available
try:
    from agents.extensions.visualization import draw_graph
except ImportError:
    print("❌ Visualization extension not available.")
    print("Install with: pip install 'openai-agents[viz]'")
    sys.exit(1)

# Import the agent classes
from The_Agents.SingleAgent import SingleAgent
from The_Agents.ArchitectAgent import ArchitectAgent

# Import Agent class to create a combined agent
from agents import Agent


def create_combined_system():
    """Create a combined system visualization with both agents."""
    print("Creating combined SingleAgent system...")
    
    # Initialize both agents
    single_agent = SingleAgent()
    architect_agent = ArchitectAgent()
    
    # Create a master coordinator agent that can handoff to both agents
    combined_system = Agent(
        name="SingleAgent System",
        instructions="""Master coordinator for the SingleAgent system.
        Can handoff to SingleAgent for code assistance and implementation,
        or to ArchitectAgent for architecture analysis and planning.""",
        handoffs=[single_agent.agent, architect_agent.agent],
        tools=[]  # The coordinator has no tools itself, delegating to specialized agents
    )
    
    return combined_system, single_agent, architect_agent


def analyze_shared_tools(single_agent, architect_agent):
    """Analyze which tools are shared between the agents."""
    single_tools = {tool.name for tool in single_agent.agent.tools}
    architect_tools = {tool.name for tool in architect_agent.agent.tools}
    
    shared_tools = single_tools.intersection(architect_tools)
    single_only = single_tools - architect_tools
    architect_only = architect_tools - single_tools
    
    return shared_tools, single_only, architect_only


def main():
    """Create and visualize the SingleAgent system architecture."""
    print("Creating SingleAgent system visualization...")
    
    # Ensure the visualization directory exists
    VISUALIZATION_DIR.mkdir(exist_ok=True)
    print(f"📁 Visualizations will be saved to: {VISUALIZATION_DIR}")
    
    try:
        # Initialize both agents
        print("Initializing SingleAgent...")
        single_agent = SingleAgent()
        
        print("Initializing ArchitectAgent...")  
        architect_agent = ArchitectAgent()
        
        # Create individual visualizations
        print("Generating SingleAgent visualization...")
        single_graph = draw_graph(single_agent.agent, filename=str(VISUALIZATION_DIR / "singleagent_system"))
        print("✅ SingleAgent graph saved as agent_visualizations/singleagent_system.png")
        
        print("Generating ArchitectAgent visualization...")
        architect_graph = draw_graph(architect_agent.agent, filename=str(VISUALIZATION_DIR / "architectagent_system"))
        print("✅ ArchitectAgent graph saved as agent_visualizations/architectagent_system.png")
        
        # Create combined system visualization
        print("Generating combined system visualization...")
        combined_system, _, _ = create_combined_system()
        combined_graph = draw_graph(combined_system, filename=str(VISUALIZATION_DIR / "combined_singleagent_system"))
        print("✅ Combined system graph saved as agent_visualizations/combined_singleagent_system.png")
        
        # Analyze tool sharing
        shared_tools, single_only, architect_only = analyze_shared_tools(single_agent, architect_agent)
        
        # Print detailed summary
        print("\n📊 Visualization Summary:")
        print("=========================")
        print("SingleAgent System:")
        print(f"- Agent: {single_agent.agent.name}")
        print(f"- Tools: {len(single_agent.agent.tools)} tools")
        print("  • Code analysis tools (ruff, pylint, pyright)")
        print("  • File operations (read_file, create_colored_diff, apply_patch)")
        print("  • System tools (run_command, os_command, change_dir)")
        print("  • Context management (get_context, add_manual_context)")
        
        print("\nArchitectAgent System:")
        print(f"- Agent: {architect_agent.agent.name}")
        print(f"- Tools: {len(architect_agent.agent.tools)} tools")
        print("  • Code analysis (analyze_ast, analyze_project_structure)")
        print("  • Architecture tools (detect_code_patterns, analyze_dependencies)")
        print("  • Planning tools (generate_todo_list)")
        print("  • File operations (read_file, read_directory, write_file)")
        print("  • System tools (run_command)")
        print("  • Context management (get_context, add_manual_context)")
        
        print("\n🔗 Tool Sharing Analysis:")
        print(f"- Shared tools: {len(shared_tools)} tools")
        if shared_tools:
            for tool in sorted(shared_tools):
                print(f"  • {tool}")
        print(f"- SingleAgent unique tools: {len(single_only)} tools")
        if single_only:
            for tool in sorted(single_only):
                print(f"  • {tool}")
        print(f"- ArchitectAgent unique tools: {len(architect_only)} tools")
        if architect_only:
            for tool in sorted(architect_only):
                print(f"  • {tool}")
        
        print("\n📁 Generated Files:")
        print("- agent_visualizations/singleagent_system.png - Shows SingleAgent with its tools")
        print("- agent_visualizations/architectagent_system.png - Shows ArchitectAgent with its tools")
        print("- agent_visualizations/combined_singleagent_system.png - Shows both agents in one system")
        
        print("\n💡 Architecture Overview:")
        print("The SingleAgent system uses a dual-agent approach:")
        print("1. SingleAgent - Focused on code assistance and implementation")
        print("2. ArchitectAgent - Focused on architecture analysis and planning")
        print("Both agents share enhanced context management and entity tracking.")
        print("\nThe combined visualization shows how both agents work together")
        print("under a master coordinator that can delegate to the appropriate")
        print("specialized agent based on the task requirements.")
        
    except Exception as e:
        print(f"❌ Error creating visualization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
