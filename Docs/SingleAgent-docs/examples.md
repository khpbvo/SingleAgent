# Examples and Use Cases

This document provides practical examples and real-world use cases for the SingleAgent system, demonstrating how to effectively use both agents for different development scenarios.

## Overview

The SingleAgent system excels at various development tasks through its dual-agent architecture:
- **Code Agent**: Focused on code quality, formatting, and direct code operations
- **Architect Agent**: Specialized in project analysis, design patterns, and architectural insights

## Getting Started Examples

### Basic Code Quality Check

**Scenario**: You want to check and fix code quality issues in a Python file.

```bash
# Start SingleAgent (defaults to Code Agent)
python -m singleagent

# Check and fix a file
User: Please analyze and fix any issues in src/user_manager.py

Code Agent: I'll analyze the file for code quality issues and apply fixes.

# The agent will:
# 1. Run Ruff linter with auto-fix
# 2. Run Pylint for detailed analysis  
# 3. Run Pyright for type checking
# 4. Provide a summary of changes made
```

### Project Architecture Analysis

**Scenario**: You want to understand the architecture of an existing project.

```bash
# Switch to Architect Agent
!architect

# Analyze project structure
User: Can you analyze the overall architecture of this project and identify any design patterns?

Architect Agent: I'll perform a comprehensive architectural analysis.

# The agent will:
# 1. Analyze project structure and organization
# 2. Identify design patterns in use
# 3. Generate entity relationship mappings
# 4. Provide architectural recommendations
```

## Code Quality Workflows

### Complete Code Quality Pipeline

**Use Case**: Establish a comprehensive code quality workflow for a Python project.

```python
# File: src/models/user.py (before)
class user:
    def __init__(self,name,email):
        self.name=name
        self.email=email
    def validate_email(self,email):
        if "@" in email:return True
        else:return False
```

**Workflow**:
```bash
# 1. Start with Code Agent
python -m singleagent

# 2. Request comprehensive analysis
User: Please perform a complete code quality analysis on src/models/user.py and fix all issues

# 3. Code Agent performs:
# - Ruff formatting (PEP 8 compliance)
# - Pylint analysis (code quality)  
# - Pyright type checking
# - Applies automatic fixes
```

**Result**:
```python
# File: src/models/user.py (after)
"""User model with email validation."""
import re
from typing import Optional


class User:
    """User class for managing user data."""
    
    def __init__(self, name: str, email: str) -> None:
        """Initialize user with name and email.
        
        Args:
            name: User's full name
            email: User's email address
        """
        self.name = name
        self.email = email
    
    def validate_email(self, email: Optional[str] = None) -> bool:
        """Validate email address format.
        
        Args:
            email: Email address to validate (uses self.email if None)
            
        Returns:
            True if email is valid, False otherwise
        """
        email_to_check = email or self.email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email_to_check))
```

### Pre-commit Hook Integration

**Use Case**: Integrate SingleAgent into pre-commit hooks for automatic code quality checks.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: singleagent-quality
        name: SingleAgent Code Quality
        entry: python -m singleagent --batch-mode --agent code
        language: system
        files: \.py$
        pass_filenames: true
```

## Architectural Analysis Workflows

### Legacy Code Understanding

**Use Case**: Understanding and documenting a legacy codebase.

```bash
# Switch to Architect Agent
!architect

# Comprehensive legacy analysis
User: This is a legacy Django project. Can you help me understand its architecture and identify areas for improvement?

# Architect Agent workflow:
# 1. Analyze project structure
# 2. Identify Django patterns and anti-patterns
# 3. Map model relationships
# 4. Identify technical debt
# 5. Generate improvement recommendations
```

**Example Output**:
```markdown
# Legacy Django Project Analysis

## Project Structure
```
myproject/
├── apps/
│   ├── users/          # User management (follows Django patterns)
│   ├── orders/         # Order processing (needs refactoring)
│   └── legacy_utils/   # Contains deprecated code
├── config/             # Django settings (well organized)
└── static/            # Static files (needs optimization)
```

## Design Patterns Identified
- **Model-View-Template**: Standard Django pattern
- **Factory Pattern**: Used in `order_factory.py`
- **Singleton**: Database connection manager (anti-pattern - use Django's built-in)

## Recommendations
1. Refactor `legacy_utils` module
2. Replace Singleton pattern with Django connection pooling
3. Add type hints to model fields
4. Implement proper error handling in views
```

### Microservices Architecture Planning

**Use Case**: Planning the decomposition of a monolith into microservices.

```bash
# Use Architect Agent for analysis
!architect

User: I have a large monolithic e-commerce application. Can you help me identify potential microservice boundaries?

# Analysis workflow:
# 1. Identify domain boundaries
# 2. Analyze coupling between modules
# 3. Identify shared dependencies
# 4. Recommend service boundaries
```

**Example Analysis**:
```markdown
# Microservices Decomposition Analysis

## Identified Domain Boundaries

### User Service
- Files: `users/models.py`, `users/views.py`, `authentication/`
- Responsibilities: User management, authentication, profiles
- Dependencies: Minimal external dependencies
- **Recommendation**: Strong candidate for separate service

### Product Catalog Service  
- Files: `products/`, `inventory/`, `categories/`
- Responsibilities: Product information, inventory management
- Dependencies: Media storage, search indexing
- **Recommendation**: Can be extracted with careful dependency management

### Order Processing Service
- Files: `orders/`, `payments/`, `shipping/`
- Responsibilities: Order lifecycle, payment processing
- Dependencies: User Service, Product Service, external payment APIs
- **Recommendation**: Extract after User and Product services
```

## Refactoring Workflows

### Design Pattern Implementation

**Use Case**: Implementing the Strategy pattern to replace conditional logic.

**Before**:
```python
# File: src/payment_processor.py
class PaymentProcessor:
    def process_payment(self, amount, method):
        if method == "credit_card":
            # Credit card processing logic
            return self._process_credit_card(amount)
        elif method == "paypal":
            # PayPal processing logic  
            return self._process_paypal(amount)
        elif method == "bank_transfer":
            # Bank transfer logic
            return self._process_bank_transfer(amount)
        else:
            raise ValueError(f"Unsupported payment method: {method}")
```

**Agent-Assisted Refactoring**:
```bash
# Start with Architect Agent
!architect

User: The payment processor class has too many conditionals. Can you help me refactor it using the Strategy pattern?

# Architect Agent identifies the pattern opportunity and suggests refactoring
# Then switch to Code Agent for implementation
!code

User: Please implement the Strategy pattern refactoring suggested by the Architect Agent
```

**After**:
```python
# File: src/payment_strategies.py
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    """Abstract base class for payment strategies."""
    
    @abstractmethod
    def process_payment(self, amount: float) -> dict:
        """Process payment with specific strategy."""
        pass

class CreditCardStrategy(PaymentStrategy):
    """Credit card payment strategy."""
    
    def process_payment(self, amount: float) -> dict:
        # Credit card processing logic
        return {"status": "success", "method": "credit_card", "amount": amount}

class PayPalStrategy(PaymentStrategy):
    """PayPal payment strategy."""
    
    def process_payment(self, amount: float) -> dict:
        # PayPal processing logic
        return {"status": "success", "method": "paypal", "amount": amount}

# File: src/payment_processor.py
from .payment_strategies import PaymentStrategy, CreditCardStrategy, PayPalStrategy

class PaymentProcessor:
    """Payment processor using Strategy pattern."""
    
    def __init__(self):
        self._strategies = {
            "credit_card": CreditCardStrategy(),
            "paypal": PayPalStrategy(),
        }
    
    def process_payment(self, amount: float, method: str) -> dict:
        """Process payment using appropriate strategy."""
        strategy = self._strategies.get(method)
        if not strategy:
            raise ValueError(f"Unsupported payment method: {method}")
        return strategy.process_payment(amount)
```

## Testing and Quality Assurance

### Test Coverage Analysis

**Use Case**: Identifying untested code and improving test coverage.

```bash
# Use Code Agent for test analysis
!code

User: Can you analyze test coverage and identify areas that need more tests?

# Agent performs:
# 1. Runs coverage analysis
# 2. Identifies untested functions/classes
# 3. Suggests test cases
# 4. Generates test templates
```

### Automated Test Generation

**Use Case**: Generating unit tests for existing code.

```python
# File: src/calculator.py
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price."""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
```

**Agent-Generated Tests**:
```python
# File: tests/test_calculator.py
import pytest
from src.calculator import calculate_discount

class TestCalculateDiscount:
    """Test cases for calculate_discount function."""
    
    def test_calculate_discount_valid_input(self):
        """Test discount calculation with valid inputs."""
        assert calculate_discount(100.0, 10.0) == 90.0
        assert calculate_discount(50.0, 20.0) == 40.0
    
    def test_calculate_discount_zero_discount(self):
        """Test with zero discount."""
        assert calculate_discount(100.0, 0.0) == 100.0
    
    def test_calculate_discount_full_discount(self):
        """Test with 100% discount."""
        assert calculate_discount(100.0, 100.0) == 0.0
    
    def test_calculate_discount_invalid_negative(self):
        """Test with negative discount percentage."""
        with pytest.raises(ValueError, match="Discount must be between 0 and 100"):
            calculate_discount(100.0, -10.0)
    
    def test_calculate_discount_invalid_over_100(self):
        """Test with discount over 100%."""
        with pytest.raises(ValueError, match="Discount must be between 0 and 100"):
            calculate_discount(100.0, 150.0)
```

## Documentation Workflows

### API Documentation Generation

**Use Case**: Generating comprehensive API documentation from code.

```bash
# Use Architect Agent for documentation
!architect

User: Please generate comprehensive API documentation for the user management module

# Agent analyzes code and generates:
# 1. Class and method documentation
# 2. Parameter descriptions
# 3. Return value specifications
# 4. Usage examples
# 5. Error handling documentation
```

### Code Review Assistance

**Use Case**: Automated code review for pull requests.

```bash
# Review specific changes
!code

User: Please review the changes in this pull request and provide feedback

# Agent performs:
# 1. Analyzes changed files
# 2. Checks code quality standards
# 3. Identifies potential issues
# 4. Suggests improvements
# 5. Validates test coverage
```

## Performance Optimization

### Performance Analysis

**Use Case**: Identifying performance bottlenecks in code.

```bash
# Use Architect Agent for performance analysis
!architect

User: Can you identify potential performance issues in this Django application?

# Agent analyzes:
# 1. Database query patterns
# 2. N+1 query problems
# 3. Inefficient algorithms
# 4. Memory usage patterns
# 5. Caching opportunities
```

### Optimization Implementation

**Use Case**: Implementing performance improvements.

**Before** (N+1 Query Problem):
```python
# Inefficient - causes N+1 queries
def get_user_orders():
    users = User.objects.all()
    for user in users:
        orders = user.orders.all()  # N additional queries
        print(f"{user.name}: {len(orders)} orders")
```

**After** (Optimized):
```python
# Efficient - uses prefetch_related
def get_user_orders():
    users = User.objects.prefetch_related('orders').all()
    for user in users:
        orders = user.orders.all()  # No additional queries
        print(f"{user.name}: {len(orders)} orders")
```

## CI/CD Integration

### Automated Quality Gates

**Use Case**: Implementing quality gates in CI/CD pipeline.

```yaml
# .github/workflows/quality.yml
name: Code Quality Check

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          
      - name: Run SingleAgent Quality Check
        run: |
          python -m singleagent --batch-mode --agent code --strict
          
      - name: Run Architecture Analysis
        run: |
          python -m singleagent --batch-mode --agent architect --generate-report
```

## Advanced Use Cases

### Custom Tool Integration

**Use Case**: Integrating domain-specific analysis tools.

```toml
# pyproject.toml
[tool.singleagent.custom_tools]

[tool.singleagent.custom_tools.security_scanner]
command = "bandit -r {project_path} -f json"
enabled = true
agent = "code"
output_format = "json"

[tool.singleagent.custom_tools.complexity_analyzer]
command = "radon cc {file_path} --json"
enabled = true
agent = "architect"
threshold = 10
```

### Multi-Project Analysis

**Use Case**: Analyzing multiple related projects for consistency.

```bash
# Analyze multiple projects
!architect

User: I have three microservices in different directories. Can you analyze them for consistency in patterns and standards?

# Agent performs cross-project analysis:
# 1. Compares project structures
# 2. Identifies pattern inconsistencies
# 3. Suggests standardization opportunities
# 4. Generates unified documentation
```

## Best Practices from Examples

### Effective Agent Usage

1. **Start with the right agent**:
   - Use Code Agent for immediate code quality issues
   - Use Architect Agent for understanding and planning

2. **Leverage agent switching**:
   - Switch between agents for different perspectives
   - Use `!code` and `!architect` commands strategically

3. **Provide context**:
   - Describe your goals clearly
   - Mention specific technologies and frameworks
   - Provide relevant background information

### Workflow Optimization

1. **Batch similar operations**:
   - Group related code quality checks
   - Perform architectural analysis in focused sessions

2. **Use configuration profiles**:
   - Set up different profiles for different project types
   - Customize tool selection based on needs

3. **Integrate with existing tools**:
   - Combine with IDEs, CI/CD, and other development tools
   - Use as part of larger development workflows

These examples demonstrate the versatility and power of the SingleAgent system across various development scenarios, from basic code quality checks to complex architectural analysis and refactoring tasks.
