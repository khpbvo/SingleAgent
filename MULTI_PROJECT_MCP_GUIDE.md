# Multi-Project MCP Configuration Guide

## 🚀 What's Fixed

### 1. MCP Agent Tool Usage Issues
- **Fixed model configuration**: Changed from `gpt-4.1` to `gpt-4o`
- **Enhanced instructions**: Agent now prioritizes MCP tools over custom tools
- **Better tool visibility**: Detailed explanations of when and why to use MCP tools
- **Improved error handling**: Better debugging and logging for MCP operations

### 2. Directory Limitation Resolved
- **Multi-project support**: Agent can now work across multiple directories simultaneously
- **Auto-detection**: Automatically discovers project directories in common locations
- **Dynamic management**: Add/remove working directories during runtime
- **Cross-project operations**: Seamlessly switch between projects

## 🎯 Key Improvements

### MCP Tool Priority System
The agent now follows this decision framework:
1. **Check MCP tools first** - they provide more comprehensive capabilities
2. **Use MCP filesystem tools** instead of basic read_file
3. **Use MCP git tools** instead of run_command for git operations
4. **Use MCP database tools** for data operations
5. **Use MCP GitHub tools** for repository management
6. **Fall back to custom tools** only when MCP tools aren't suitable

### Multi-Project Architecture
```
Agent Working Directories:
├── /Users/kevinvanosch/Documents/SingleAgent (current project)
├── /Users/kevinvanosch/Documents/ProjectB
├── /Users/kevinvanosch/Development/WebApp
└── /Users/kevinvanosch/Projects/DataAnalysis
```

## 🔧 New Commands

### MCP Management Commands
- `!mcpdirs` - List all available working directories
- `!mcpadddir:path` - Add a new working directory
- `!mcprmdir:path` - Remove a working directory
- `!mcptools` - List all available MCP tools
- `!mcpstatus` - Show MCP server status
- `!mcpreload:server` - Reload a specific MCP server

### Usage Examples
```bash
# Add a new project directory
!mcpadddir:/Users/kevinvanosch/Projects/NewProject

# List all working directories
!mcpdirs

# Check MCP server status
!mcpstatus

# Remove a directory
!mcprmdir:/path/to/old/project
```

## 🌍 Multi-Project Features

### Automatic Project Detection
The system automatically detects:
- Current project directory
- Sibling projects in the same parent folder
- Common development directories (`~/Projects`, `~/Development`, etc.)
- Directories with project indicators (`.git`, `package.json`, `requirements.txt`, etc.)

### Cross-Project Operations
- Use `change_dir` tool to switch between projects
- MCP filesystem tools work across all configured directories
- Maintain separate context for each project
- Share insights between related projects

## 🔌 Enhanced MCP Capabilities

### Filesystem Server (Multi-Directory)
```python
# Before: Limited to current directory
filesystem_server(["/Users/kevinvanosch/Documents/SingleAgent"])

# After: Multiple project directories
filesystem_server([
    "/Users/kevinvanosch/Documents/SingleAgent",
    "/Users/kevinvanosch/Projects/WebApp",
    "/Users/kevinvanosch/Development/DataAnalysis"
])
```

### Git Server (Project-Aware)
- Automatically detects Git repositories
- Provides advanced Git operations beyond basic commands
- Better error handling and structured responses

### GitHub Server (Enhanced)
- Direct API access with proper authentication
- Repository management across multiple projects
- Issue and PR management
- Code search capabilities

## 🎪 Agent Behavior Changes

### Tool Selection Logic
The agent now actively explains its tool choices:
- "Using MCP filesystem tool for better error handling..."
- "MCP git tool provides more detailed repository information..."
- "MCP GitHub integration gives us direct API access..."

### Multi-Project Awareness
- Shows working directory count in status bar
- Explains multi-project capabilities to users
- Suggests cross-project operations when relevant
- Maintains context across directory switches

## 🛠 Configuration Options

### Environment Variables
```bash
# GitHub integration
export GITHUB_TOKEN=your_github_token_here

# Optional: Web search capabilities
export WEB_SEARCH_API_KEY=your_api_key_here
```

### Custom Directory Configuration
You can manually specify working directories by modifying the `get_common_project_directories()` function in `main.py`:

```python
def get_custom_project_directories():
    return [
        "/path/to/your/project1",
        "/path/to/your/project2",
        "/path/to/your/project3"
    ]
```

## 🚨 Migration Notes

### For Existing Users
1. **No breaking changes** - all existing functionality preserved
2. **Enhanced capabilities** - MCP tools provide better alternatives
3. **Automatic upgrades** - multi-project support works out of the box
4. **Backward compatibility** - can still use single directory if preferred

### Recommended Workflow
1. Start the application with `python main.py`
2. Switch to MCP mode with `!mcp`
3. Check available directories with `!mcpdirs`
4. Add new projects with `!mcpadddir:path`
5. Use MCP tools for enhanced capabilities

## 🎯 Best Practices

### For MCP Tool Usage
1. **Let the agent choose** - it will explain why it picked a specific tool
2. **Trust MCP tools** - they generally provide better capabilities
3. **Ask for explanations** - the agent will describe tool benefits
4. **Combine tools** - chain MCP and custom tools creatively

### For Multi-Project Work
1. **Start with detection** - let the system find your projects
2. **Add as needed** - use `!mcpadddir` for additional projects
3. **Switch contexts** - use `change_dir` or MCP tools to move between projects
4. **Maintain organization** - remove unused directories with `!mcprmdir`

## 🐛 Troubleshooting

### MCP Tools Not Working
1. Check server status with `!mcpstatus`
2. Reload problematic servers with `!mcpreload:server_name`
3. Verify Node.js and npm are installed for MCP servers
4. Check logs in `logs/mcp_singleagent.log`

### Directory Issues
1. Ensure directories exist and are readable
2. Use absolute paths when adding directories
3. Check permissions on project folders
4. Verify Git repositories are properly initialized

### GitHub Integration
1. Verify GitHub token is set correctly
2. Check token permissions (repo access)
3. Test with `!mcpstatus` to see GitHub server status
4. Reload GitHub server if needed: `!mcpreload:github`

## 📈 Performance Tips

### For Large Projects
- Use MCP filesystem search instead of manual file browsing
- Cache tools list is enabled by default for better performance
- Limit working directories to active projects (< 10 recommended)

### For Multiple Repositories
- Use MCP git tools for better performance than shell commands
- Leverage GitHub MCP server for API operations
- Consider separate sessions for unrelated project groups

---

## 🎉 Result

You now have a **Multi-Project MCP-Enhanced Agent** that:
- ✅ Uses MCP tools properly and explains why
- ✅ Works across multiple projects simultaneously
- ✅ Automatically detects and manages project directories
- ✅ Provides enhanced capabilities through MCP servers
- ✅ Maintains backward compatibility with existing workflows

Your agent is no longer limited to `/Users/kevinvanosch/Documents/SingleAgent` and can work intelligently across your entire development environment!
