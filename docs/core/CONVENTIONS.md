# HomeLab Discord Bot Coding Conventions

_Last Updated: [Current Date]_

This document outlines the coding conventions and standards for the HomeLab Discord Bot project. Following these conventions ensures consistency, readability, and maintainability across the codebase.

## Python Coding Style

### General Guidelines
- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters (compatible with Black formatter)
- Use UTF-8 encoding for all Python files

### Naming Conventions
- **Classes**: `CamelCase`
- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private attributes/methods**: Prefix with underscore `_private_method`
- **Module names**: Short, lowercase, no underscores if possible

### Type Annotations
- Use type hints for all function parameters and return values
- Use Union/Optional for variables that can be None or another type
- Import types from typing module
```python
from typing import List, Dict, Optional, Union
def process_data(data: List[Dict[str, str]]) -> Optional[Dict[str, any]]:
# Implementation
```

## Documentation

### Docstrings
- Use Google-style docstrings for all public functions, classes, and methods
- Include parameters, return values, and exceptions raised 
```python
def fetch_data(user_id: str, limit: int = 10) -> List[Dict[str, any]]:
"""Fetches user data from the database.
Args:
user_id: The ID of the user to fetch data for.
limit: Maximum number of records to return.
Returns:
A list of dictionaries containing user data.
Raises:
ValueError: If user_id is empty or invalid.
DatabaseError: If connection to database fails.
"""
# Implementation
```


### Comments
- Use comments sparingly and focus on **why**, not **what**
- Comment complex logic or non-obvious decisions
- Keep comments updated when code changes

## Project Organization

### Module Structure
- Group related functionality in modules
- Follow the project's domain-driven design structure
- Maintain separation of concerns between layers

### Import Conventions
- Sort imports in three groups: standard library, third-party, local
- Sort each group alphabetically
- Use absolute imports for project modules 
```python
Standard library
import os
import sys
from datetime import datetime
Third-party
import discord
import nextcord
from dotenv import load_dotenv
Local application imports
from bot.domain.models import User
from bot.infrastructure.repositories import UserRepository
```

## Discord-Specific Conventions

### Command Naming
- Use kebab-case for slash command names: `system-status`
- Group related commands into command groups
- Follow Discord's command naming guidelines

### Error Handling
- Always handle exceptions in command handlers
- Provide user-friendly error messages
- Log detailed error information for debugging

### Asynchronous Code
- Always use async/await for Discord API calls
- Avoid blocking operations in event handlers
- Use asyncio.gather for parallel operations

## Testing

### Test Naming
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassBeingTested>`
- Test methods: `test_<method_name>_<scenario>`

### Test Structure
- Arrange-Act-Assert pattern
- Use pytest fixtures for test setup
- Mock external dependencies

## Version Control

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- First line is a summary (max 50 characters)
- Followed by blank line and detailed description if needed
- Reference issue numbers where applicable

### Branch Naming
- Feature branches: `feature/short-description`
- Bugfix branches: `fix/issue-description`
- Refactor branches: `refactor/component-name`