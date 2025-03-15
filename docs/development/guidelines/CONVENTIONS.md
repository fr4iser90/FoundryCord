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

## Architecture Patterns

### Component Types

- **Managers**: Handle lifecycle, state management and coordination between components
  - Example: `KeyManagementService` manages encryption key lifecycle
  - Naming: `{Component}Manager` or `{Function}Manager`
  - Location: `infrastructure/{domain}/management/` or `domain/{domain}/management/`

- **Services**: Provide specific business functionality and operations
  - Example: `EncryptionService` provides encryption/decryption operations
  - Naming: `{Function}Service`
  - Location: `application/services/{domain}/` or `domain/{domain}/services/`

- **Repositories**: Handle data persistence and retrieval
  - Example: `UserRepository` provides access to user data
  - Naming: `{Entity}Repository`
  - Location: `infrastructure/database/repositories/`

- **Factories**: Create complex objects
  - Example: `EmbedFactory` creates Discord embed objects
  - Naming: `{Product}Factory`
  - Location: `infrastructure/factories/{type}/`

- **Collectors**: Fetch data from external sources
  - Example: `UserCollector` fetches user data from an API
  - Naming: `{Function}Collector`
  - Location: `infrastructure/collectors/{type}/`

- **Workflows**: Orchestrate complex processes and business logic sequences
  - Example: `CategoryWorkflow` handles the setup and lifecycle of Discord categories
  - Naming: `{Domain}Workflow` or `{Process}Workflow`
  - Location: `core/workflows/`

- **Middleware**: Intercept and process requests or operations
  - Example: `RateLimitingMiddleware` enforces request rate limits
  - Naming: `{Function}Middleware`
  - Location: `infrastructure/{domain}/middleware/`

- **Config**: Define and manage configuration settings
  - Example: `EnvConfig` loads and manages environment variables
  - Naming: `{Domain}Config` or `{Type}Config`
  - Location: `infrastructure/config/` or `domain/{domain}/config/`

- **Models**: Define domain entities and data structures
  - Example: `User` represents a user entity
  - Naming: Singular noun, `CamelCase`
  - Location: `domain/{domain}/models/`

- **Commands**: Implement Discord slash commands
  - Example: `SystemMonitoringCommands` implements monitoring commands
  - Naming: `{Domain}Commands` or `{Function}Commands`
  - Location: `interfaces/commands/{domain}/`

- **UI Components**: Create and manage Discord UI elements
  - Example: `DashboardView` manages interactive dashboard views
  - Naming: `{Purpose}Button`, `{Purpose}View`, `{Purpose}Modal`, etc.
  - Location: `interfaces/dashboards/components/{type}/`

- **Tasks**: Perform scheduled or background operations
  - Example: `CleanupTask` removes stale data periodically
  - Naming: `{Function}Task`
  - Location: `application/tasks/` or `domain/{domain}/tasks/`

- **Policies**: Enforce business rules and authorization logic
  - Example: `AuthorizationPolicies` defines access control rules
  - Naming: `{Domain}Policies` or `{Function}Policies`
  - Location: `domain/{domain}/policies/`

- **Utilities**: Provide helper functions and common operations
  - Example: `HttpClient` manages HTTP requests
  - Naming: Descriptive of functionality
  - Location: `utils/` or domain-specific utility folders

- **Decorators**: Add cross-cutting functionality to methods
  - Example: `@authorized` checks permissions before execution
  - Naming: Verb or adjective describing the modification
  - Location: `utils/decorators/`

- **Handlers**: Process specific events or triggers
  - Example: `ErrorHandler` processes exceptions
  - Naming: `{Event}Handler`
  - Location: `infrastructure/handlers/` or domain-specific handler folders

- **Adapters**: Bridge between the application and external systems or APIs
  - Example: `DiscordAdapter` provides a unified interface to Discord API
  - Naming: `{ExternalSystem}Adapter`
  - Location: `infrastructure/adapters/` or `infrastructure/{domain}/adapters/`

- **Converters**: Transform data between different formats or types
  - Example: `MessageConverter` converts between different message representations
  - Naming: `{DataType}Converter`
  - Location: `infrastructure/converters/` or `domain/{domain}/converters/`

- **Validators**: Ensure data meets specific requirements or constraints
  - Example: `InputValidator` checks user input for correctness
  - Naming: `{Domain}Validator` or `{Input}Validator`
  - Location: `domain/{domain}/validators/` or `infrastructure/validators/`

- **Strategies**: Implement interchangeable algorithms or approaches
  - Example: `NotificationStrategy` defines how notifications are sent
  - Naming: `{Function}Strategy`
  - Location: `domain/{domain}/strategies/`

- **Providers**: Supply data or services to components
  - Example: `ConfigProvider` provides configuration values
  - Naming: `{Resource}Provider`
  - Location: `infrastructure/providers/` or `domain/{domain}/providers/`

- **Extensions**: Add functionality to the core system
  - Example: `LoggingExtension` adds enhanced logging capabilities
  - Naming: `{Function}Extension`
  - Location: `core/extensions/`

- **Builders**: Create complex objects step by step
  - Example: `CommandBuilder` constructs command objects incrementally
  - Naming: `{Product}Builder`
  - Location: `infrastructure/builders/` or `domain/{domain}/builders/`

- **Dispatchers**: Route events or requests to appropriate handlers
  - Example: `EventDispatcher` routes events to registered handlers
  - Naming: `{Type}Dispatcher`
  - Location: `infrastructure/dispatchers/` or `domain/{domain}/dispatchers/`

- **Mappers**: Transform objects between different representations
  - Example: `UserMapper` converts between User entity and DTO
  - Naming: `{Entity}Mapper`
  - Location: `infrastructure/mappers/` or `domain/{domain}/mappers/`

- **Caches**: Store and manage temporary data
  - Example: `ResponseCache` stores recent responses for quick retrieval
  - Naming: `{Data}Cache`
  - Location: `infrastructure/caches/` or `domain/{domain}/caches/`

- **Guards**: Protect access to resources or operations
  - Example: `RateGuard` prevents excessive operation frequency
  - Naming: `{Resource}Guard` or `{Function}Guard`
  - Location: `infrastructure/guards/` or `domain/{domain}/guards/`

- **Resolvers**: Determine how to fulfill a request or find a resource
  - Example: `DependencyResolver` locates and provides required dependencies
  - Naming: `{Resource}Resolver`
  - Location: `infrastructure/resolvers/` or `domain/{domain}/resolvers/`

- **Listeners**: React to events or state changes
  - Example: `StateChangeListener` responds to application state changes
  - Naming: `{Event}Listener`
  - Location: `infrastructure/listeners/` or `domain/{domain}/listeners/`

- **Hooks**: Provide extension points for customizing behavior
  - Example: `CommandHook` allows customizing command behavior
  - Naming: `{Process}Hook`
  - Location: `infrastructure/hooks/` or `domain/{domain}/hooks/`

## Component Placement Guidelines

### Domain Layer vs. Infrastructure Layer

Use these guidelines to determine where components belong:

#### Place in Domain Layer when:
- The component implements core business rules or concepts
- The functionality is specific to a particular domain area
- The component defines "what" the system does, not "how"
- The component would make sense even if the technical implementation changes
- The component represents a real-world concept in your problem space

**Examples**: User model, permission rules, service eligibility calculations

#### Place in Infrastructure Layer when:
- The component deals with technical concerns
- The functionality is about "how" something is done, not "what"
- The component interacts with external systems, frameworks or libraries
- The component implements interfaces defined in the domain layer
- The component provides cross-cutting technical capabilities

**Examples**: Database access, caching implementation, Discord API integration

### Component Type Placement Reference

| Component Type     | Typical Layer     | Primary Location                       | Secondary Location (if applicable)  |
|--------------------|-------------------|----------------------------------------|-------------------------------------|
| Models             | Domain            | `domain/{domain}/models/`              | -                                   |
| Domain Services    | Domain            | `domain/{domain}/services/`            | -                                   |
| Repositories (I)   | Domain            | `domain/{domain}/repositories/`        | -                                   |
| Repositories (Impl)| Infrastructure    | `infrastructure/database/repositories/`| -                                   |
| Factories          | Infrastructure    | `infrastructure/factories/{type}/`     | -                                   |
| Managers           | Infrastructure    | `infrastructure/{domain}/management/`  | `domain/{domain}/management/`       |
| Collectors         | Domain            | `domain/{domain}/collectors/`          | `infrastructure/collectors/{type}/` |
| Validators         | Domain            | `domain/{domain}/validators/`          | `infrastructure/validators/`        |
| Services (App)     | Application       | `application/services/{domain}/`       | -                                   |
| Commands           | Interface         | `interfaces/commands/{domain}/`        | -                                   |
| UI Components      | Interface         | `interfaces/dashboards/components/`    | -                                   |

### Example Component Organization by Domain

For a "monitoring" domain:

```
domain/monitoring/
├── models/              # Domain entities like Alert, Metric, System
├── services/            # Domain services like AlertService, MetricService
├── collectors/          # Mechanisms to collect monitoring data
├── repositories/        # Repository interfaces for data access
├── policies/            # Rules governing monitoring behavior
└── validators/          # Validation for monitoring inputs/thresholds

infrastructure/
├── database/repositories/
│   └── monitoring_repository.py  # Implementation of repository interfaces
├── collectors/
│   └── system_collector.py       # Technical implementation of collection
├── adapters/
│   └── prometheus_adapter.py     # Integration with external monitoring tools
```

## Related Documentation
- [Design Patterns](../patterns/DESIGN_PATTERN.md) - Architectural patterns
- [Layer Definitions](../architecture/LAYERS.md) - System layer organization
- [Security Policy](../modules/SECURITY_POLICY.md) - Security implementation requirements
- [Communication Guidelines](../../ai/context/COMMUNICATION.md) - Language and documentation standards
