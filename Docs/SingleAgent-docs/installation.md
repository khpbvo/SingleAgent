# Installation Guide

This guide provides detailed instructions for installing and setting up SingleAgent on your system.

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 500MB free space
- **Internet**: Required for OpenAI API access

### Recommended Requirements

- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Storage**: 1GB free space
- **Terminal**: Modern terminal with Unicode support

## Prerequisites

### 1. Python Installation

Ensure you have Python 3.8+ installed:

```bash
python --version
# or
python3 --version
```

If you need to install Python:
- **Windows**: Download from [python.org](https://python.org)
- **macOS**: Use Homebrew: `brew install python`
- **Linux**: Use your package manager: `sudo apt install python3`

### 2. OpenAI API Key

You'll need an OpenAI API key:

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Save the key securely (you'll need it later)

## Installation Steps

### Method 1: Standard Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd SingleAgent
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Development Installation

For development with editable installation:

```bash
git clone <repository-url>
cd SingleAgent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

## Configuration

### 1. Environment Variables

Set up your OpenAI API key:

**Option A: Environment Variable**
```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# Windows Command Prompt
set OPENAI_API_KEY=your-api-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"
```

**Option B: .env File**
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your-api-key-here
```

### 2. SpaCy Model Installation

SingleAgent uses SpaCy for entity recognition. Install the required model:

```bash
python -m spacy download en_core_web_sm
```

### 3. Optional Configuration

Create a configuration file if you want to customize settings:

```bash
cp config/config.example.yaml config/config.yaml
```

Edit the configuration file as needed.

## Verification

### 1. Test Installation

Run a quick test to verify everything is working:

```bash
python main.py --test
```

### 2. Check Dependencies

Verify all dependencies are installed correctly:

```bash
pip list | grep -E "(openai|spacy|prompt-toolkit)"
```

You should see the required packages listed.

### 3. Launch SingleAgent

Start the system:

```bash
python main.py
```

You should see the SingleAgent prompt:
```
SingleAgent>
```

## Troubleshooting Installation Issues

### Common Issues

#### Python Version Error
```
Error: Python 3.8+ required
```
**Solution**: Upgrade Python or use `python3` instead of `python`

#### OpenAI API Key Missing
```
Error: OpenAI API key not found
```
**Solutions**:
- Verify the API key is set correctly
- Check the environment variable name
- Ensure the `.env` file is in the correct location

#### SpaCy Model Not Found
```
OSError: [E050] Can't find model 'en_core_web_sm'
```
**Solution**: 
```bash
python -m spacy download en_core_web_sm
```

#### Permission Errors (Linux/macOS)
```
Permission denied: /usr/local/...
```
**Solution**: Use virtual environment or `--user` flag:
```bash
pip install --user -r requirements.txt
```

#### Windows Path Issues
```
'python' is not recognized...
```
**Solutions**:
- Add Python to PATH during installation
- Use `py` instead of `python`
- Reinstall Python with "Add to PATH" option

### Dependency Conflicts

If you encounter dependency conflicts:

1. **Clear pip cache**:
   ```bash
   pip cache purge
   ```

2. **Use fresh virtual environment**:
   ```bash
   deactivate
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Check for conflicting packages**:
   ```bash
   pip check
   ```

## Advanced Installation Options

### Docker Installation

If you prefer Docker:

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t singleagent .
docker run -e OPENAI_API_KEY=your-key -it singleagent
```

### Conda Installation

If you use Conda:

```bash
conda create -n singleagent python=3.9
conda activate singleagent
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Post-Installation Setup

### 1. Initialize Context Storage

On first run, SingleAgent will create necessary directories:
- Context storage: `~/.singleagent/context/`
- Configuration: `~/.singleagent/config/`
- Logs: `~/.singleagent/logs/`

### 2. Test Both Agents

Verify both agents work correctly:

```bash
# Test Code Agent (default)
SingleAgent> help

# Test Architect Agent
SingleAgent> !architect
Architect> help
```

### 3. Configure Preferences

Set up your preferences:
- Preferred output format
- Default agent
- Context retention settings

See [Configuration Guide](configuration.md) for details.

## Updating SingleAgent

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstallation

To remove SingleAgent:

1. **Deactivate virtual environment**:
   ```bash
   deactivate
   ```

2. **Remove project directory**:
   ```bash
   rm -rf /path/to/SingleAgent
   ```

3. **Remove virtual environment**:
   ```bash
   rm -rf venv
   ```

4. **Clean up user data** (optional):
   ```bash
   rm -rf ~/.singleagent
   ```

## Next Steps

After successful installation:

1. Read the [Quick Start Guide](quickstart.md)
2. Review [Configuration Options](configuration.md)
3. Explore [Architecture Overview](architecture.md)
4. Try the [Examples](examples.md)

## Getting Help

If you encounter issues during installation:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review the error messages carefully
3. Ensure all prerequisites are met
4. Try the installation in a fresh virtual environment

The SingleAgent system is now ready to use!
