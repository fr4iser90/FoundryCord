# HomeLab Discord Bot Architecture

_Last Updated: [Current Date]_

## System Architecture Overview

The HomeLab Discord Bot uses a layered architecture based on Domain-Driven Design principles, with clear separation of concerns:
┌─────────────────────────────────────────────────────────────────┐
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
from app.bot.domain.monitoring.services.metric_service import MetricService
from app.bot.infrastructure.factories.service.service_factory import ServiceFactory
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

## Related Documentation
- [Design Patterns](../patterns/DESIGN_PATTERN.md) - Implementation patterns
- [Data Flow Patterns](./DATA_FLOW.md) - Component interaction patterns
- [Project Structure](../../ai/context/CORE.md) - Overall project organization
- [Coding Conventions](../guidelines/CONVENTIONS.md) - Implementation standards

## Updated Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  Interface Layer                                │
│  (Dynamic Dashboard Views/Components)           │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│  Application Layer                              │
│  (Dashboard Builder, Dashboard Services)        │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│  Domain Layer                                   │
│  (Dashboard Definition Models, Business Logic)  │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│  Infrastructure Layer                           │
│  (Dashboard Repository, Component Registry)     │
└─────────────────────────────────────────────────┘
```

## Key Components for Database-Driven Dashboards

### 1. Dashboard Definition Model

```python
class DashboardDefinition:
    """Domain model representing a dashboard definition from the database"""
    def __init__(self, id, name, description, layout, components, refresh_rate):
        self.id = id
        self.name = name
        self.description = description
        self.layout = layout  # JSON/dict defining component positioning
        self.components = components  # List of component references
        self.refresh_rate = refresh_rate
        
class DashboardComponent:
    """Domain model representing a dashboard component from the database"""
    def __init__(self, id, type, title, data_source, properties):
        self.id = id
        self.type = type  # "chart", "status", "button", etc.
        self.title = title
        self.data_source = data_source  # Service/method to fetch data
        self.properties = properties  # Component-specific properties
```

### 2. Dashboard Repository

```python
class DashboardRepository:
    """Repository for fetching dashboard definitions from database"""
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    async def get_dashboard_by_id(self, dashboard_id):
        """Fetch a dashboard definition by ID"""
        # DB query implementation
        
    async def get_component_by_id(self, component_id):
        """Fetch a component definition by ID"""
        # DB query implementation
        
    async def save_dashboard(self, dashboard_definition):
        """Save a dashboard definition"""
        # DB save implementation
```

### 3. Dashboard Builder

```python
class DashboardBuilder:
    """Builds runtime dashboard views from definitions"""
    def __init__(self, bot, component_registry):
        self.bot = bot
        self.component_registry = component_registry
        
    async def build_dashboard(self, dashboard_definition):
        """Build a complete dashboard from its definition"""
        embed = await self.create_embed(dashboard_definition)
        view = await self.create_view(dashboard_definition)
        return embed, view
        
    async def create_embed(self, dashboard_definition):
        """Create embed from dashboard definition"""
        # Implementation
        
    async def create_view(self, dashboard_definition):
        """Create view with components from definition"""
        # Implementation
```

### 4. Component Registry

```python
class ComponentRegistry:
    """Registry of available dashboard components"""
    def __init__(self):
        self.components = {}
        
    def register_component(self, component_type, component_class):
        """Register a component type with its implementation class"""
        self.components[component_type] = component_class
        
    def get_component(self, component_type):
        """Get component implementation for a type"""
        return self.components.get(component_type)
```

### 5. Updated Dashboard Controller

```markdown:docs/development/patterns/DASHBOARD_CONTROLLER_STRUCTURE.md
class DatabaseDrivenDashboardController(BaseDashboardController):
    """Controller for database-driven dashboards"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.dashboard_repository = bot.get_service('dashboard_repository')
        self.dashboard_builder = bot.get_service('dashboard_builder')
        self.dashboard_definition = None
        
    async def load_dashboard(self, dashboard_id):
        """Load dashboard definition from database"""
        self.dashboard_definition = await self.dashboard_repository.get_dashboard_by_id(dashboard_id)
        return self.dashboard_definition
        
    async def create_embed(self):
        """Create embed using dashboard builder"""
        if not self.dashboard_definition:
            raise ValueError("Dashboard not loaded")
        embed, _ = await self.dashboard_builder.build_dashboard(self.dashboard_definition)
        return embed
        
    def create_view(self):
        """Create view using dashboard builder"""
        if not self.dashboard_definition:
            raise ValueError("Dashboard not loaded")
        _, view = await self.dashboard_builder.build_dashboard(self.dashboard_definition)
        return view
        
    async def refresh_data(self):
        """Refresh all data sources for this dashboard"""
        # Implementation to refresh all data sources defined in components
```

## Updated Data Flow for Database-Driven Dashboards

```
1. User requests dashboard or clicks action button
   │
   ▼
2. Controller loads dashboard definition from repository
   │
   ▼
3. Dashboard Builder fetches component definitions 
   │
   ▼
4. For each component, Builder fetches data from appropriate services
   │
   ▼
5. Builder assembles components into complete dashboard
   │
   ▼
6. Controller displays assembled dashboard
   │
   ▼
7. User interactions trigger component-specific callbacks
```

## Refined Dashboard Creation Workflow

1. **Create Dashboard Definition**
   - Define dashboard metadata (name, description)
   - Select dashboard layout template
   - Configure refresh settings

2. **Add Components to Dashboard**
   - Select component types from registry
   - Configure data sources for components
   - Set component properties and display settings

3. **Configure Component Layout**
   - Position components within dashboard layout
   - Set size and visibility properties

4. **Configure Interactivity**
   - Define button actions and callbacks
   - Set up component interactions and state changes

5. **Save Dashboard Definition**
   - Store complete definition in database
   - Generate access permissions

## Implementation Example

```python
# Example database-driven dashboard implementation
async def setup_database_driven_dashboards(bot):
    # Register component types
    component_registry = ComponentRegistry()
    component_registry.register_component("status_panel", StatusPanelComponent)
    component_registry.register_component("chart", ChartComponent)
    component_registry.register_component("button_group", ButtonGroupComponent)
    
    # Create dashboard builder
    dashboard_builder = DashboardBuilder(bot, component_registry)
    bot.service_factory.register_service("dashboard_builder", dashboard_builder)
    
    # Set up dashboard controller
    dashboard_controller = DatabaseDrivenDashboardController(bot)
    
    # Load dashboard by ID
    system_dashboard_id = "system-dashboard-001"
    await dashboard_controller.load_dashboard(system_dashboard_id)
    
    # Display dashboard
    await dashboard_controller.display_dashboard()
```

## Benefits of Database-Driven Approach

1. **Customization**: Users can create and modify dashboards without code changes
2. **Flexibility**: Components can be reused across multiple dashboards
3. **Runtime Updates**: Dashboards can be updated without restarting the bot
4. **Dynamic Configuration**: Dashboards can adapt based on user permissions and preferences

This database-driven architecture maintains the same layer separation as before but shifts dashboard creation from compile-time to runtime, making your bot much more flexible and extensible.
