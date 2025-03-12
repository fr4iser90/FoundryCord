# HomeLab Discord Bot Project Structure

This document provides a structured overview of the HomeLab Discord Bot project organization, highlighting the key architectural components and their relationships.

## Architectural Layers

The project follows a clean Domain-Driven Design architecture with clear separation of concerns:

1. **Domain Layer**: Core business logic, models, and domain services
2. **Application Layer**: Orchestration of use cases, application services
3. **Interface Layer**: User interfaces, command handling, dashboards
4. **Infrastructure Layer**: Technical concerns, external systems integration

For more detailed information about layer implementation, see [Layer Definitions](../../development/architecture/LAYERS.md).

For data flow patterns between components, see [Data Flow Patterns](../../development/architecture/DATA_FLOW.md).

## Project Organization

### Core Components
- **Domain Models**: Business entities and value objects
- **Domain Services**: Core business logic
- **Repositories**: Data access interfaces
- **Events**: Domain events for state changes

## Core Application Structure

### Bot Application (app/bot/)

#### 1. Core Layer

```
app/bot/core/
├── extensions.py # Bot extensions management
├── lifecycle/    # Bot lifecycle management
├── main.py       # Entry point and initialization
└── workflows/    # Core workflow orchestration
```

#### 2. Domain Layer
```
app/bot/domain/
├── auth/                  # Authentication and authorization
│   ├── models/            # User, role and permission models
│   ├── policies/          # Authorization policies
│   ├── repositories/      # Auth data access
│   └── services/          # Auth domain services
├── channels/              # Channel domain models
├── gameservers/           # Game server monitoring
│   ├── collectors/        # Game data collection
│   ├── models/            # Game server domain models
│   └── repositories/      # Game server data access
├── monitoring/            # Monitoring domain
│   ├── collectors/        # Data collectors
│   ├── models/            # Monitoring models
│   ├── repositories/      # Monitoring data access
│   └── services/          # Monitoring services
├── security/              # Security domain
│   └── services/          # Security services
└── tracker/               # Project tracking
    └── services/          # Project services
```

#### 3. Application Layer
```
app/bot/application/
├── services/              # Application services
│   ├── channel/           # Channel services
│   ├── dashboard/         # Dashboard services
│   ├── monitoring/        # Monitoring services
│   └── wireguard/         # Wireguard VPN services
└── tasks/                 # Scheduled tasks
    ├── cleanup_task.py    # Cleanup tasks
    └── security_tasks.py  # Security tasks
```

#### 4. Infrastructure Layer
```
app/bot/infrastructure/
├── config/                # Configuration
│   ├── constants/         # System constants
│   └── services/          # Service configuration
├── database/              # Database infrastructure
│   ├── connection.py      # Database connection
│   ├── management/        # Credential management
│   ├── migrations/        # Database migrations
│   ├── models/            # Database models
│   └── repositories/      # Repository implementations
├── discord/               # Discord integration
├── encryption/            # Encryption services
├── factories/             # Factory implementations
│   ├── base/              # Base factories
│   ├── composite/         # Composite factories
│   ├── discord/           # Discord-related factories
│   ├── discord_ui/        # UI component factories
│   ├── monitoring/        # Monitoring factories
│   └── service/           # Service factories
├── logging/               # Logging infrastructure
├── managers/              # System managers
├── monitoring/            # Monitoring infrastructure
│   ├── checkers/          # Service checkers
│   └── collectors/        # Metric collectors
├── rate_limiting/         # Rate limiting
├── security/              # Security infrastructure
└── web/                   # Web server infrastructure
```

#### 5. Interface Layer
```
app/bot/interfaces/
├── commands/              # Command interfaces
│   ├── admin/             # Admin commands
│   ├── auth/              # Auth commands
│   ├── gameserver/        # Game server commands
│   ├── monitoring/        # Monitoring commands
│   ├── tracker/           # Project tracker commands
│   ├── utils/             # Utility commands
│   └── wireguard/         # VPN commands
├── dashboards/            # Dashboard interfaces
│   ├── components/        # UI components
│   │   ├── channels/      # Channel-specific components
│   │   ├── common/        # Common UI components
│   │   ├── factories/     # UI factories
│   │   └── ui/            # UI utilities
│   └── controller/        # Dashboard controllers
├── homelab_commands.py    # Main command registration
└── web/                   # Web interface
    ├── models/            # Web models
    ├── routes/            # Web routes
    ├── services/          # Web services
    └── templates/         # HTML templates
```

### Web Application (app/bot/interfaces/web)
```
app/bot/interfaces/web/
├── config.py              # Web config
├── database.py            # Web database
├── models/                # Web data models
├── routes/                # API routes
│   ├── auth.py            # Auth endpoints
│   ├── dashboard.py       # Dashboard endpoints
│   └── user.py            # User endpoints
├── server.py              # Web server
├── services/              # Web services
│   ├── auth_service.py    # Auth service
│   ├── dashboard_service.py # Dashboard service
│   └── user_service.py    # User service
└── templates/             # HTML templates
    ├── base.html          # Base template
    ├── dashboard_.html    # Dashboard templates
    ├── error.html         # Error page
    ├── login.html         # Login page
    ├── profile.html       # User profile
    └── settings.html      # Settings page
```

## Documentation Structure
```
docs/
├── ai/                    # AI documentation
│   ├── CAPABILITIES.md    # AI capabilities
│   ├── INTEGRATION.md     # AI role integration
│   ├── context/           # Context information
│   ├── roles/             # AI role definitions
│   │   ├── application/   # Application layer roles
│   │   ├── core/          # Core layer roles
│   │   ├── infrastructure/ # Infrastructure layer roles
│   │   ├── system/        # System roles
│   │   ├── ui/            # UI roles
│   │   └── web/           # Web interface roles
│   └── subjects/          # Domain knowledge
├── core/                  # Core documentation
│   ├── ARCHITECTURE.md    # Architecture overview
│   ├── CONVENTIONS.md     # Coding conventions
│   ├── DATA_FLOW.md       # Data flow diagrams
│   ├── KEYMANAGER.md      # Key management
│   └── SECURITY_POLICY.md # Security documentation
├── development/           # Development guides
│   └── patterns/          # Design patterns
├── planning/              # Project planning
│   ├── ACTION_PLAN.md     # Current action plan
│   ├── MILESTONES.md      # Project milestones
│   └── ROADMAP.md         # Development roadmap
├── reference/             # Reference documentation
│   ├── api/               # API documentation
│   └── config/            # Configuration reference
└── user/                  # User documentation
    ├── features/          # Feature documentation
    ├── getting-started/   # Getting started guides
    └── guides/            # User guides
```

## Deployment & Testing Structure

```
docker/                   # Docker deployment
├── docker-compose.yml     # Docker composition
├── Dockerfile.bot         # Main Dockerfile
├── Dockerfile.web         # Main Dockerfile
├── .env                   # Environment variables
└── entrypoint.sh          # Container entrypoint
tests/                     # Test suite
├── integration/           # Integration tests
└── unit/                  # Unit tests
utils/                     # Utility scripts
├── config/                # Configuration scripts
├── database/              # Database scripts
├── deployment/            # Deployment scripts
├── development/           # Development utilities
├── lib/                   # Shared libraries
└── testing/               # Testing utilities
```

## Professional Documentation Template

Below is a recommended template for how professional documentation should look in your project:

```markdown
# [Document Title]

## Overview
A concise introduction to the document purpose and scope (2-3 sentences).

## Key Concepts
Brief explanation of the important concepts covered in this document:

- **Concept One**: Definition and explanation
- **Concept Two**: Definition and explanation
- **Concept Three**: Definition and explanation

## Architecture / Structure
┌─────────────┐      ┌─────────────┐
│ Component A │─────▶│ Component B │
└─────────────┘      └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│ Component C │◀─────│ Component D │
└─────────────┘      └─────────────┘

## Implementation Details

### Component A
```python
def example_function():
    """
    Documentation for function purpose
    """
    # Implementation details
    pass
```

### Component B
Description of component B functionality, including:
- Initialization process
- Key methods and properties
- Error handling approach

## Usage Examples
```python
# Example code showing how to use the described components
from module import Component

component = Component()
result = component.process_data(input_data)
```

## Best Practices
- **Do**: Follow these recommendations
- **Don't**: Avoid these common pitfalls
- **Consider**: Things to keep in mind

## Related Documentation
- Link to related document 1
- Link to related document 2

## Changelog
| Date | Version | Changes |
|------|---------|---------|
| YYYY-MM-DD | 1.0 | Initial document |
| YYYY-MM-DD | 1.1 | Updated section X |