# Troubleshooting Guide

Common issues, solutions, and debugging tips for SingleAgent. This guide helps you resolve problems quickly and effectively.

## Quick Diagnosis

### System Health Check

Run this diagnostic script to check your SingleAgent installation:

```python
#!/usr/bin/env python3
"""
SingleAgent Health Check Script
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        return False, f"Python {version.major}.{version.minor} found, requires Python 3.8+"
    return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"

def check_dependencies():
    """Check required dependencies"""
    required_packages = [
        'openai',
        'spacy',
        'prompt_toolkit',
        'rich',
        'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        return False, f"Missing packages: {', '.join(missing)}"
    return True, "All required packages installed ✓"

def check_spacy_model():
    """Check SpaCy model availability"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        return True, "SpaCy model 'en_core_web_sm' loaded ✓"
    except OSError:
        return False, "SpaCy model 'en_core_web_sm' not found"
    except Exception as e:
        return False, f"SpaCy error: {str(e)}"

def check_openai_config():
    """Check OpenAI API configuration"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return False, "OPENAI_API_KEY environment variable not set"
    
    if len(api_key) < 20:
        return False, "OPENAI_API_KEY appears invalid (too short)"
    
    return True, "OpenAI API key configured ✓"

def run_health_check():
    """Run complete health check"""
    print("SingleAgent Health Check")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("SpaCy Model", check_spacy_model),
        ("OpenAI Config", check_openai_config)
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✓" if passed else "✗"
            print(f"{name:<15} {status} {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"{name:<15} ✗ Error: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All checks passed! SingleAgent should work correctly.")
    else:
        print("✗ Some checks failed. See individual errors above.")
    
    return all_passed

if __name__ == "__main__":
    run_health_check()
```

Save this as `health_check.py` and run it to diagnose issues quickly.

## Installation Issues

### Python Version Problems

**Problem**: SingleAgent requires Python 3.8+ but older version is installed

**Solutions**:
```bash
# Check Python version
python --version

# Install Python 3.8+ using pyenv (recommended)
curl https://pyenv.run | bash
pyenv install 3.9.16
pyenv global 3.9.16

# Or use system package manager
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv

# macOS with Homebrew
brew install python@3.9

# Windows - download from python.org
```

### Dependency Installation Failures

**Problem**: `pip install` fails for required packages

**Solutions**:

1. **Upgrade pip first**:
```bash
python -m pip install --upgrade pip
```

2. **Install with specific requirements**:
```bash
# Create requirements.txt
cat > requirements.txt << EOF
openai>=1.0.0
spacy>=3.4.0
prompt-toolkit>=3.0.0
rich>=12.0.0
python-dotenv>=0.19.0
EOF

# Install with requirements file
pip install -r requirements.txt
```

3. **Use virtual environment**:
```bash
python -m venv singleagent_env
source singleagent_env/bin/activate  # Linux/macOS
# or
singleagent_env\Scripts\activate  # Windows

pip install -r requirements.txt
```

4. **Compilation issues (Linux)**:
```bash
# Install build dependencies
sudo apt install build-essential python3-dev

# For SpaCy compilation
sudo apt install gcc g++ make
```

### SpaCy Model Issues

**Problem**: SpaCy language model not found

**Error Messages**:
- `OSError: [E050] Can't find model 'en_core_web_sm'`
- `ModuleNotFoundError: No module named 'en_core_web_sm'`

**Solutions**:

1. **Install SpaCy model**:
```bash
# Method 1: Using spacy download
python -m spacy download en_core_web_sm

# Method 2: Direct pip install
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.4.1/en_core_web_sm-3.4.1-py3-none-any.whl

# Method 3: Using specific version
pip install en_core_web_sm==3.4.1 \
    --find-links https://github.com/explosion/spacy-models/releases/
```

2. **Verify installation**:
```python
import spacy
nlp = spacy.load("en_core_web_sm")
print("SpaCy model loaded successfully!")
```

3. **Alternative models** (if default fails):
```bash
# Smaller model (less accurate but faster)
python -m spacy download en_core_web_sm

# Larger model (more accurate but slower)
python -m spacy download en_core_web_lg
```

## Configuration Issues

### OpenAI API Key Problems

**Problem**: API key not working or not found

**Error Messages**:
- `openai.AuthenticationError: Incorrect API key provided`
- `openai.RateLimitError: You exceeded your current quota`
- `OPENAI_API_KEY environment variable not set`

**Solutions**:

1. **Set environment variable correctly**:
```bash
# Linux/macOS - add to ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-your-actual-api-key-here"

# Windows - Command Prompt
set OPENAI_API_KEY=sk-your-actual-api-key-here

# Windows - PowerShell
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"

# Or create .env file in project directory
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > .env
```

2. **Verify API key format**:
```python
import os
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key length: {len(api_key) if api_key else 'Not set'}")
print(f"Starts with 'sk-': {api_key.startswith('sk-') if api_key else False}")
```

3. **Test API connectivity**:
```python
from openai import OpenAI
client = OpenAI()

try:
    response = client.models.list()
    print("API connection successful!")
except Exception as e:
    print(f"API error: {e}")
```

### Configuration File Issues

**Problem**: Config file not found or invalid format

**Solutions**:

1. **Create default config**:
```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    MODEL_NAME: str = 'gpt-4'
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    SPACY_MODEL: str = 'en_core_web_sm'
    LOG_LEVEL: str = 'INFO'
    LOG_FILE: str = 'singleagent.log'
    
    def validate(self):
        """Validate configuration"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not self.OPENAI_API_KEY.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format")

# Usage
config = Config()
config.validate()
```

2. **JSON configuration file**:
```json
{
    "openai": {
        "model": "gpt-4",
        "max_tokens": 2000,
        "temperature": 0.7
    },
    "spacy": {
        "model": "en_core_web_sm"
    },
    "logging": {
        "level": "INFO",
        "file": "singleagent.log"
    }
}
```

## Runtime Issues

### Memory Problems

**Problem**: High memory usage or out-of-memory errors

**Error Messages**:
- `MemoryError: Unable to allocate memory`
- System becomes slow or unresponsive

**Solutions**:

1. **Reduce SpaCy model size**:
```python
# Use smaller model
import spacy
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

# Or load specific components only
nlp = spacy.load("en_core_web_sm", disable=["textcat", "entity_ruler"])
```

2. **Limit conversation history**:
```python
class ContextData:
    def __init__(self, max_messages=50):
        self.max_messages = max_messages
        self.conversation_history = []
    
    def add_message(self, message):
        self.conversation_history.append(message)
        if len(self.conversation_history) > self.max_messages:
            self.conversation_history.pop(0)
```

3. **Process text in chunks**:
```python
def process_large_text(text, chunk_size=1000):
    """Process large text in smaller chunks"""
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    results = []
    for chunk in chunks:
        result = process_chunk(chunk)
        results.append(result)
    return combine_results(results)
```

### OpenAI API Errors

**Problem**: API calls failing or rate limits

**Error Messages**:
- `openai.RateLimitError: Rate limit reached`
- `openai.APITimeoutError: Request timed out`
- `openai.APIError: The server had an error`

**Solutions**:

1. **Implement retry logic**:
```python
import time
import random
from openai import OpenAI

def api_call_with_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello"}],
                timeout=30
            )
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s...")
            time.sleep(delay)
```

2. **Handle rate limits**:
```python
from openai import RateLimitError
import time

def handle_rate_limit(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except RateLimitError:
            print("Rate limit reached, waiting 60 seconds...")
            time.sleep(60)
```

3. **Use token limits wisely**:
```python
def calculate_tokens(text):
    """Rough token estimation"""
    return len(text) // 4  # Approximate: 1 token ≈ 4 characters

def trim_context(messages, max_tokens=3000):
    """Trim conversation to fit token limit"""
    total_tokens = sum(calculate_tokens(msg['content']) for msg in messages)
    
    while total_tokens > max_tokens and len(messages) > 1:
        # Remove oldest message (keep system message if present)
        if messages[0]['role'] == 'system':
            messages.pop(1)
        else:
            messages.pop(0)
        total_tokens = sum(calculate_tokens(msg['content']) for msg in messages)
    
    return messages
```

### Context Management Issues

**Problem**: Context becomes corrupted or inconsistent

**Solutions**:

1. **Context validation**:
```python
def validate_context(context):
    """Validate context data integrity"""
    errors = []
    
    # Check entity integrity
    for entity_id, entity in context.entities.items():
        if not entity.text or not entity.label:
            errors.append(f"Invalid entity: {entity_id}")
    
    # Check relationship integrity
    for rel in context.relationships:
        if rel.source not in context.entities or rel.target not in context.entities:
            errors.append(f"Invalid relationship: {rel}")
    
    return errors

def repair_context(context):
    """Attempt to repair corrupted context"""
    # Remove invalid entities
    valid_entities = {
        eid: entity for eid, entity in context.entities.items()
        if entity.text and entity.label
    }
    context.entities = valid_entities
    
    # Remove invalid relationships
    valid_relationships = [
        rel for rel in context.relationships
        if rel.source in context.entities and rel.target in context.entities
    ]
    context.relationships = valid_relationships
```

2. **Context backup and recovery**:
```python
import json
from datetime import datetime

class ContextManager:
    def __init__(self):
        self.backup_dir = "context_backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_context(self, context):
        """Create context backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.backup_dir}/context_backup_{timestamp}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(context.to_dict(), f, indent=2)
        
        return backup_file
    
    def restore_context(self, backup_file):
        """Restore context from backup"""
        with open(backup_file, 'r') as f:
            data = json.load(f)
        return ContextData.from_dict(data)
```

## Performance Issues

### Slow Response Times

**Problem**: SingleAgent responds slowly

**Solutions**:

1. **Profile performance**:
```python
import time
import cProfile
import pstats

def profile_function(func):
    """Profile function performance"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 slowest functions
    
    return result
```

2. **Optimize SpaCy processing**:
```python
# Use smaller pipeline
nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger"])

# Process in batches
def process_texts_batch(texts):
    return list(nlp.pipe(texts, batch_size=100, n_process=2))

# Cache results
from functools import lru_cache

@lru_cache(maxsize=1000)
def extract_entities_cached(text):
    return extract_entities(text)
```

3. **Optimize OpenAI calls**:
```python
# Use streaming for long responses
def stream_response(client, messages):
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

# Batch similar requests
def batch_similar_requests(requests):
    # Group similar requests together
    # Process in single API call
    pass
```

### High CPU Usage

**Problem**: SingleAgent consumes too much CPU

**Solutions**:

1. **Limit concurrent processing**:
```python
import threading
from concurrent.futures import ThreadPoolExecutor

class ResourceManager:
    def __init__(self, max_workers=2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.rate_limiter = threading.Semaphore(max_workers)
    
    def process_with_limit(self, func, *args):
        with self.rate_limiter:
            return self.executor.submit(func, *args)
```

2. **Optimize text processing**:
```python
# Use regex for simple patterns instead of SpaCy
import re

def quick_entity_extraction(text):
    """Fast entity extraction for simple cases"""
    # Email pattern
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    
    # Phone pattern
    phones = re.findall(r'\b\d{3}-\d{3}-\d{4}\b', text)
    
    return {'emails': emails, 'phones': phones}
```

## Logging and Debugging

### Enable Debug Logging

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Agent-specific logging
agent_logger = logging.getLogger('singleagent.agents')
agent_logger.setLevel(logging.DEBUG)

# Tool execution logging
tool_logger = logging.getLogger('singleagent.tools')
tool_logger.setLevel(logging.DEBUG)
```

### Debug Tools

1. **Context inspector**:
```python
def inspect_context(context):
    """Print detailed context information"""
    print(f"Entities: {len(context.entities)}")
    for eid, entity in list(context.entities.items())[:5]:
        print(f"  {eid}: {entity.text} ({entity.label})")
    
    print(f"Messages: {len(context.conversation_history)}")
    for msg in context.conversation_history[-3:]:
        print(f"  {msg.role}: {msg.content[:50]}...")
    
    print(f"Relationships: {len(context.relationships)}")
    for rel in context.relationships[:3]:
        print(f"  {rel.source} -> {rel.relation} -> {rel.target}")
```

2. **API call tracer**:
```python
class APITracer:
    def __init__(self):
        self.calls = []
    
    def trace_call(self, method, params, response_time):
        self.calls.append({
            'method': method,
            'params': params,
            'response_time': response_time,
            'timestamp': datetime.now()
        })
    
    def print_stats(self):
        print(f"Total API calls: {len(self.calls)}")
        avg_time = sum(call['response_time'] for call in self.calls) / len(self.calls)
        print(f"Average response time: {avg_time:.2f}s")
```

## Getting Help

### Community Resources

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share experiences
- **Wiki**: Community-maintained documentation and tips

### Creating Bug Reports

When reporting issues, include:

1. **System Information**:
```bash
python --version
pip list | grep -E "(openai|spacy|prompt-toolkit|rich)"
uname -a  # Linux/macOS
systeminfo  # Windows
```

2. **Error Details**:
```python
import traceback
try:
    # Your failing code here
    pass
except Exception as e:
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")
    traceback.print_exc()
```

3. **Minimal Reproduction**:
```python
#!/usr/bin/env python3
"""
Minimal reproduction of the issue
"""
from singleagent import SingleAgent

# Minimal code that reproduces the problem
agent = SingleAgent()
result = agent.process_message("test message")  # This fails
```

### Performance Optimization Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] SpaCy model downloaded
- [ ] OpenAI API key configured
- [ ] Sufficient system memory (4GB+ recommended)
- [ ] Network connectivity for API calls
- [ ] Proper file permissions for logs and data
- [ ] Debug logging enabled for troubleshooting

---

*For additional support, see [Configuration](configuration.md) and [API Reference](api-reference.md).*
