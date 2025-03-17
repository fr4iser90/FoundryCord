# HomeLab Discord Bot Service Organization Pattern

This document outlines the standard organization pattern for all services in the HomeLab Discord Bot. Following this pattern ensures consistency across the codebase and clear separation of concerns, with an emphasis on data-driven design where configurations are stored in PostgreSQL.

## Layer Organization

### 1. Domain Layer (`app/bot/domain/`)
The core business logic and rules independent of any external system.

```
app/bot/domain/{service_name}/
├── models/
│   └── {entity}_model.py         # Core domain entities
├── repositories/
│   └── {entity}_repository.py    # Repository interfaces
├── services/
│   └── {entity}_domain_service.py # Domain-specific business rules
└── events/
    └── {entity}_events.py        # Domain events
```

**Principles:**
- Contains pure business logic with no external dependencies
- Defines interfaces that will be implemented in infrastructure
- Holds rich domain models with behavior, not just data
- Uses value objects and entities with proper validation

### 2. Application Layer (`app/bot/application/`)
The orchestration layer that coordinates domain objects to perform use cases.

```
app/bot/application/services/{service_name}/
├── {service_name}_service.py      # Primary orchestration service
├── {entity}_manager.py            # Entity-specific operations
└── {feature}_service.py           # Feature-specific operations
```

**Principles:**
- Implements use cases by coordinating domain objects
- Uses repository interfaces from domain layer
- No direct dependencies on external frameworks, databases, or UI
- Thin services focused on workflow and coordination

### 3. Infrastructure Layer (`app/bot/infrastructure/`)
Implementations of interfaces defined in the domain layer.

```
app/bot/infrastructure/
├── repositories/
│   └── {entity}_repository_impl.py   # Repository implementations with PostgreSQL
├── discord/
│   └── {service_name}_client.py      # Discord API interactions
├── factories/
│   └── {entity}_factory.py           # Object factories
├── adapters/
│   └── {external_service}_adapter.py # External service adapters
└── registries/
    └── {entity}_registry.py          # Component/entity registries
```

**Principles:**
- Contains all external system interactions (PostgreSQL, Discord API, etc.)
- Implements repository interfaces from domain layer
- Framework-specific code isolated here
- Manages technical concerns (caching, persistence, etc.)

### 4. Interface Layer (`app/bot/interfaces/`)
User interfaces and API endpoints (Discord commands, buttons, etc.).

```
app/bot/interfaces/{service_name}/
├── commands/
│   └── {command}_command.py       # Discord slash commands
├── controllers/
│   └── {feature}_controller.py    # Feature controllers
└── components/
    ├── buttons/
    │   └── {button}_button.py     # UI buttons
    ├── embeds/
    │   └── {embed}_embed.py       # Discord embeds
    └── views/
        └── {view}_view.py         # Discord views
```

**Principles:**
- Thin controllers that delegate to application services
- Handles user input and formatting output
- No business logic, just presentation
- Translates between user interface and application layer

### 5. Shared Layer (`app/shared/`)
Cross-cutting concerns and database infrastructure used by multiple services.

```
app/shared/
├── database/
│   ├── models/                # Shared database models
│   │   └── {entity}.py        # Shared database entity
│   ├── migrations/            # Database migrations (managed by web frontend)
│   │   └── versions/          # Migration scripts
│   └── core/                  # Database core functionality
│       ├── connection.py      # Database connection management
│       └── repository.py      # Base repository patterns
├── interface/
│   └── logging/               # Shared logging utilities
└── utils/
    ├── validation.py          # Validation utilities
    └── serialization.py       # Serialization helpers
```

**Principles:**
- Utilities and helpers used across multiple modules
- Shared database models and connection management
- Migrations managed by web frontend, not the bot
- Common infrastructure used by bot and web frontend

## Data-Driven Design Approach

All services should follow these additional principles for data-driven design:

1. **Database-Driven Configuration**: Consume configurations, definitions, and templates from PostgreSQL
2. **Dynamic Component Loading**: Use registries to load and instantiate components at runtime
3. **Builder Pattern**: Use builders to construct complex objects from database definitions
4. **Repository Pattern**: Abstract database access through repositories that map to domain models
5. **Factory Pattern**: Create instances based on configuration data from the database

## Database-Bot Interaction

The bot follows these principles for database interaction:

1. **Read-Only by Default**: Most repository operations are read-only
2. **No Migration Management**: Bot doesn't manage database schema
3. **Model Mapping**: Repository implementations map database records to domain models
4. **Shared Connection**: Database connections are managed in the shared layer
5. **Loose Coupling**: Domain models are decoupled from database schema

## Implementation Guidelines

1. **Start with Domain Models**: Define your core entities and business rules first
2. **Define Repository Interfaces**: Create interfaces before implementations
3. **Implement Repository**: Create PostgreSQL implementation of repository interfaces
4. **Implement Use Cases**: Build application services that orchestrate domain objects
5. **Build User Interface**: Create commands, views, and other UI components

## Example Service Implementation

For a new "reminder" service:

1. **Domain Layer**:
   - `app/bot/domain/reminders/models/reminder_model.py`
   - `app/bot/domain/reminders/repositories/reminder_repository.py`

2. **Application Layer**:
   - `app/bot/application/services/reminder/reminder_service.py`
   - `app/bot/application/services/reminder/scheduler_service.py`

3. **Infrastructure Layer**:
   - `app/bot/infrastructure/repositories/reminder_repository_impl.py`

4. **Interface Layer**:
   - `app/bot/interfaces/reminders/commands/reminder_command.py`
   - `app/bot/interfaces/reminders/components/embeds/reminder_embed.py`

5. **Shared Layer**:
   - `app/shared/database/models/reminder.py` (Database entity model)

By following this pattern consistently, you ensure each service maintains a clean separation of concerns and remains maintainable as the codebase grows.