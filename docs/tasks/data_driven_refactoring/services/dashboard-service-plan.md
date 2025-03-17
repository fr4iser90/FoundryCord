# Dashboard Service Organization Plan

## 1. Domain Layer Refinement
- Create proper dashboard domain models in `app/bot/domain/dashboards/models/`
- Define repository interfaces in `app/bot/domain/dashboards/repositories/`
- Create data source abstraction for components

## 2. Application Layer Consolidation
- Refactor `DashboardBuilder` to build dashboards from database definitions
- Keep `DashboardService` as the main orchestrator
- Keep `DashboardLifecycleService` for lifecycle management
- Create component factory system for dynamic component creation

## 3. Infrastructure Layer Organization
- Implement `DashboardRepositoryImpl` in `app/bot/infrastructure/repositories/` using PostgreSQL
- Create component registry and data source registry services
- Use shared database models from `app/shared/database/models/`

## 4. Channel/Category Setup Fixes
- Debug category/channel creation workflow
- Ensure proper sequencing: Category creation must complete before channel creation
- Add more detailed logging for tracking creation failures

## 5. Service Structure Cleanup

### Application Layer (app/bot/application/)

```
app/bot/application/services/
├── dashboard/
│   ├── dashboard_service.py           # Orchestration service
│   ├── dashboard_builder.py           # Dashboard assembly from db definitions
│   ├── dashboard_lifecycle_service.py # Lifecycle management
│   └── component_service.py           # Component operations
├── channel/
│   └── channel_setup_service.py       # Channel orchestration
└── category_setup/
    └── category_setup_service.py      # Category orchestration
```

**Key Principles:**
- Coordinates domain objects
- Implements use cases and workflows
- Doesn't have direct database dependencies
- Uses repository interfaces to access data

### Domain Layer (app/bot/domain/)

```
app/bot/domain/dashboards/
├── models/
│   ├── dashboard_model.py         # Core dashboard entity
│   ├── component_model.py         # Component definitions
│   └── data_source_model.py       # Data source definitions
├── repositories/
│   └── dashboard_repository.py    # Repository interface
├── services/
│   ├── component_service.py       # Core component business rules
│   └── data_processor_service.py  # Data processing logic
└── events/
    └── dashboard_events.py        # Domain events
```

**Key Principles:**
- No dependencies on external frameworks
- Pure business logic and rules
- Repository interfaces (not implementations)
- Models are rich with behavior, not just data containers

### Infrastructure Layer (app/bot/infrastructure/)

```
app/bot/infrastructure/
├── repositories/
│   └── dashboard_repository_impl.py  # PostgreSQL repository
├── discord/
│   └── message_manager.py            # Discord message management
├── adapters/
│   └── data_source_adapter.py        # Data source adapters
├── services/
│   └── discord_message_tracker.py    # Track message state
└── factories/
    └── component_factory.py          # Component creation
```

**Key Principles:**
- Contains external system interactions
- Implements interfaces defined in domain layer
- Adapters for external systems
- Discord API interactions

### Interface Layer (app/bot/interfaces/)

```
app/bot/interfaces/dashboards/
├── commands/
│   └── dashboard_command.py        # Dashboard slash commands
├── controllers/
│   └── dashboard_controller.py     # Command handling
├── components/
│   ├── buttons/
│   │   └── dashboard_buttons.py    # Button components
│   ├── selectors/
│   │   └── dashboard_selectors.py  # Dropdown components
│   └── embeds/
│       └── dashboard_embeds.py     # Embed components
└── handlers/
    └── interaction_handler.py      # Handle component interactions
```

**Key Principles:**
- Contains all Discord UI components
- Delegates business logic to application services
- Handles user interaction events
- Pure presentation logic

## 6. Database Schema

```sql
-- Dashboard definitions
CREATE TABLE dashboard_templates (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    dashboard_type VARCHAR(50) NOT NULL,
    refresh_interval INTEGER NOT NULL DEFAULT 300,
    service_class VARCHAR(100),
    auto_create BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Dashboard instances (deployed to a channel)
CREATE TABLE dashboards (
    id VARCHAR(50) PRIMARY KEY,
    template_id VARCHAR(50) REFERENCES dashboard_templates(id),
    guild_id VARCHAR(50) NOT NULL,
    channel_id VARCHAR(50) NOT NULL,
    message_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Component templates (buttons, embeds, selectors, etc.)
CREATE TABLE component_templates (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    component_type VARCHAR(50) NOT NULL, -- button, embed, selector, etc.
    dashboard_type VARCHAR(50),
    properties JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Component instances
CREATE TABLE dashboard_components (
    id VARCHAR(50) PRIMARY KEY,
    dashboard_id VARCHAR(50) REFERENCES dashboards(id) ON DELETE CASCADE,
    template_id VARCHAR(50) REFERENCES component_templates(id),
    component_type VARCHAR(50) NOT NULL,
    custom_id VARCHAR(100),
    data_source_type VARCHAR(50),
    properties JSONB NOT NULL,
    position JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Data sources
CREATE TABLE data_sources (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- system, minecraft, factorio, etc.
    connection_params JSONB,
    refresh_interval INTEGER NOT NULL DEFAULT 60,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Dashboard channel mappings (replacing hardcoded mappings)
CREATE TABLE dashboard_channel_mappings (
    id VARCHAR(50) PRIMARY KEY,
    channel_template_id VARCHAR(50) REFERENCES channel_templates(id) ON DELETE CASCADE,
    dashboard_template_id VARCHAR(50) REFERENCES dashboard_templates(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(channel_template_id, dashboard_template_id)
);
```

## 7. Implementation Steps

1. **Create Domain Models**:
   - Define model classes that map to database entities
   - Define validation rules and business logic
   - Create repository interfaces

2. **Implement Repository**:
   - Create PostgreSQL repository implementations
   - Map between database records and domain models
   - Implement efficient querying patterns

3. **Develop Infrastructure**:
   - Create component registry system
   - Build data source registry and providers
   - Implement Discord message tracking

4. **Build Application Services**:
   - Refactor dashboard builder to use database definitions
   - Create services for dashboard CRUD operations
   - Implement component management services

5. **Create Interface Components**:
   - Develop controllers for dashboard operations
   - Create command handlers for user interaction
   - Build dynamic UI components

## 8. Migration from Hardcoded to Database

1. **Use Existing Migration Data**:
   - Leverage existing dashboard component definitions from `app/shared/infrastructure/database/migrations/dashboards/`
   - Run the existing `dashboard_components_migration.py` to populate database tables
   - Maintain current component organization: common, gamehub, monitoring, project, welcome

2. **Update Dashboard Services**:
   - Modify to load dashboard definitions from database
   - Create DashboardBuilder to construct dashboards from templates
   - Keep backward compatibility during transition

3. **Replace Constants Usage**:
   - Update all references to dashboard constants to use repository pattern
   - Create domain models that represent runtime dashboard instances
   - Maintain fallback to constants if database unavailable