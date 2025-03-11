# HomeLab Discord Bot Architecture

_Last Updated: [Current Date]_

## System Architecture Overview

The HomeLab Discord Bot uses a layered architecture based on Domain-Driven Design principles, with clear separation of concerns:
┌─────────────────────────────────────────────────────┐
│ Interface Layer                                     │
│ (Discord Commands, Dashboards, User Interactions)   │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│ Application Layer                                   │
│ (Application Services, Command Handlers)            │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│ Domain Layer                                        │
│ (Domain Models, Services, Business Logic)           │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│ Infrastructure Layer                                │
│ (Discord API, Database, External Services)          │
└─────────────────────────────────────────────────────┘

 WEBUI TOO:

┌─────────────────────────────────────────────────────┐
│ Interface Layer                                     │
│ (Web UI Components, API Endpoints)                  │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│ Application Layer                                   │
│ (Web Application Services, Request Handlers)        │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│ Domain Layer                                        │
│ (Shared Domain Models, Services, Business Logic)    │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│ Infrastructure Layer                                │
│ (Web Server, Authentication Middleware)             │
└─────────────────────────────────────────────────────┘

## Key Architectural Components

### Discord Integration
- **Bot Client**: Built on nextcord
- **Event Handling**: Async event processing
- **Command Management**: Slash commands and prefix commands

### Domain Services
- **Authentication Service**: User authorization
- **Channel Service**: Channel management
- **Monitoring Service**: System monitoring
- **Dashboard Service**: Dashboard creation and management

### Infrastructure Components
- **Service Factory**: Creates and provides access to services
- **Repository Pattern**: Data access abstraction
- **Configuration System**: Environment-based configuration

## Data Flow

1. **Commands & Events**: User interactions trigger commands or events
2. **Application Services**: Orchestrate domain operations
3. **Domain Logic**: Execute business rules
4. **Persistence**: Store and retrieve data through repositories
5. **Response**: Format and present results to users

## Dependencies
- nextcord: Discord API library
- psutil: System monitoring
- aiohttp: Async HTTP client/server
- python-dotenv: Environment variable management

## Deployment Architecture
The bot is designed to run as a standalone Python application with minimal external dependencies, making it suitable for small homelab environments.

## Architectural Decision Records

### ADR-001: Domain-Driven Design
**Decision**: Use DDD for overall architecture
**Rationale**: Clear separation of concerns, maintainability
**Consequences**: More initial structure, better long-term scalability

### ADR-002: Service Factory Pattern
**Decision**: Use factory pattern for service creation
**Rationale**: Centralized service management, dependency injection
**Consequences**: Simplified service access, controlled lifecycle

## Code Map

This section maps the architectural layers to specific directories in the codebase.

### Directory Structure Overview
```python
app/bot/
├── core/ # Bootstrap and lifecycle management
├── domain/ # Domain Layer
│ ├── auth/ # Authentication domain
│ ├── monitoring/ # System monitoring domain
│ ├── tracker/ # Project tracking domain
│ └── wireguard/ # Wireguard VPN domain
├── application/ # Application Layer
│ ├── services/ # Application services by domain
│ └── tasks/ # Background and scheduled tasks
├── infrastructure/ # Infrastructure Layer
│ ├── config/ # Configuration management
│ ├── database/ # Database access and models
│ ├── discord/ # Discord API integration
│ ├── encryption/ # Security services
│ ├── factories/ # Component factories
│ ├── logging/ # Logging infrastructure
│ ├── managers/ # Resource managers
│ ├── rate_limiting/ # Rate limiting services
│ └── security/ # Security infrastructure
└── interfaces/ # Interface Layer
├── commands/ # Discord slash commands by domain
└── dashboards/ # Interactive UI components
├── components/ # Reusable dashboard components
└── ui/ # Complete dashboard implementations
```

### Layer-to-Directory Mapping

1. **Interface Layer** (`app/bot/interfaces/`)
   - Commands: `interfaces/commands/{domain}/`
   - Dashboards: `interfaces/dashboards/ui/`
   - UI Components: `interfaces/dashboards/components/`

2. **Application Layer** (`app/bot/application/`)
   - Application Services: `application/services/{domain}/`
   - Tasks: `application/tasks/`

3. **Domain Layer** (`app/bot/domain/`)
   - Models: `domain/{domain}/models/`
   - Domain Services: `domain/{domain}/services/`
   - Repositories (interfaces): `domain/{domain}/repositories/`

4. **Infrastructure Layer** (`app/bot/infrastructure/`)
   - Repository Implementations: `infrastructure/database/repositories/`
   - Factories: `infrastructure/factories/`
   - External Integrations: `infrastructure/discord/`, etc.

### Import Conventions

All imports should use absolute paths from the project root:
```python
# Recommended
from domain.monitoring.services.metric_service import MetricService
from infrastructure.factories.service.service_factory import ServiceFactory
```

```python
# NOT recommended (inconsistent)
from app.domain.monitoring.services.metric_service import MetricService
from app.bot.application.services.monitoring.system_monitoring import setup
```

### Domain Organization

Each domain follows this structure:
```python
domain/{domain_name}/
├── models/ # Domain entities and value objects
├── services/ # Domain services with business logic
├── repositories/ # Repository interfaces
└── collectors/ # (If applicable) Data collectors
```

### Interface Organization

UI components follow this structure:
```python
interfaces/dashboards/components/{domain}/
├── buttons/ # Interactive buttons
├── embeds/ # Embed message templates
├── views/ # Discord views
```
This structure ensures consistency across the codebase and helps developers quickly locate components based on their architectural responsibilities.

## Component Type Placement

### Domain Layer Components
Components in this layer focus on business logic and domain concepts:

- **Models**: Core business entities and value objects
- **Domain Services**: Business logic specific to a domain
- **Repositories (interfaces)**: Data access contracts
- **Policies**: Business rules and authorization logic
- **Validators**: Domain-specific validation rules
- **Strategies**: Business logic algorithms that may vary
- **Domain Events**: Business significant events

### Infrastructure Layer Components
Components in this layer implement technical concerns:

- **Managers**: Lifecycle and state coordination components
- **Repository Implementations**: Concrete data access
- **Adapters**: External system integration
- **Factories**: Object creation
- **Middleware**: Request/operation interception
- **Providers**: Resource provisioning
- **Security**: Authentication, encryption, key management
- **Caching**: Performance optimization
- **Logging**: System observability
- **Configuration**: System settings and parameters
- **Mappers**: Data transformation between layers

### Application Layer Components
Components in this layer orchestrate use cases:

- **Application Services**: Coordinate domain objects
- **Tasks**: Scheduled background operations
- **Command Handlers**: Process user commands
- **Workflows**: Multi-step business processes
- **Event Handlers**: React to system events

### Interface Layer Components
Components in this layer interact with users:

- **Commands**: Discord slash commands
- **UI Components**: Dashboard elements and views
- **Converters**: Transform between UI and application formats
- **Presenters**: Format data for display
