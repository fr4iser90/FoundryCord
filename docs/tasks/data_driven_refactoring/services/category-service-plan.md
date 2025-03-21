# Category Service Organization Plan

## 1. Domain Layer Refinement
- Create proper category domain models in `app/bot/domain/categories/models/`
- Define repository interfaces in `app/bot/domain/categories/repositories/`
- Define category validation rules and domain services
- Design value objects for category configurations

## 2. Application Layer Consolidation
- Keep `CategorySetupService` as the main orchestration service
- Add category-specific operations in dedicated services
- Implement proper event handling for category operations
- Create category builder for constructing from database definitions

## 3. Infrastructure Layer Organization
- Create `app/bot/infrastructure/repositories/category_repository_impl.py` using PostgreSQL
- Create Discord API adapter for category operations
- Implement caching for category data to reduce API calls
- Use shared database models from `app/shared/database/models/`

## 4. Interface Layer Setup
- Create commands and controllers for category management
- Implement user-friendly error handling and feedback
- Add permission checking for category operations
- Create category template selection interfaces

## 5. Service Structure Cleanup

### Application Layer (app/bot/application/)

```
app/bot/application/services/
├── category/
│   ├── category_service.py # Main orchestration service
│   ├── category_setup_service.py # Category setup workflows
│   ├── category_builder.py # Category assembly from database
│   └── category_permission_service.py # Permission handling
```

**Key Principles:**
- Coordinates domain objects
- Implements use cases and workflows
- Doesn't have direct Discord API or database dependencies
- Uses repository interfaces, not implementations

### Domain Layer (app/bot/domain/)

```
app/bot/domain/categories/
├── models/
│   ├── category_model.py # Core category entity
│   └── category_template.py # Category template value object
├── repositories/
│   └── category_repository.py # Repository interface
├── services/
│   └── category_validator.py # Category validation rules
└── events/
    └── category_events.py # Domain events
```

**Key Principles:**
- Contains pure business logic with no external dependencies
- Defines interfaces that will be implemented in infrastructure
- Holds rich domain models with behavior, not just data
- Uses value objects and entities with proper validation

### Infrastructure Layer (app/bot/infrastructure/)

```
app/bot/infrastructure/
├── repositories/
│   └── category_repository_impl.py # PostgreSQL repository implementation
├── discord/
│   └── category_client.py # Discord API interactions
└── config/
    └── category_config.py # Category configuration
```

**Key Principles:**
- Implements interfaces defined in domain layer
- Contains Discord API and PostgreSQL interactions
- Framework-specific code
- Separates external concerns from business logic

### Interface Layer (app/bot/interfaces/)

```
app/bot/interfaces/categories/
├── commands/
│   └── category_command.py # Category slash commands
├── controllers/
│   └── category_controller.py # Category workflow controller
└── components/
    ├── views/
    │   └── category_template_selector.py # Template selection UI
    └── embeds/
        └── category_config_embed.py # Category configuration display
```

**Key Principles:**
- Handles user interaction (Discord commands/UI)
- Light controllers that delegate to application services
- Presentation logic only
- No business rules

### Shared Layer (app/shared/)

```
app/shared/
└── database/
    ├── models/
    │   ├── category.py  # Category database entity
    │   └── category_template.py  # Category template database entity
    └── core/
        └── connection.py  # Database connection manager
```

## 6. Database Schema Reference

The bot will read from these tables, which are managed by the web frontend:

```sql
-- Category templates (replacing hardcoded default categories)
CREATE TABLE categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    default_permissions JSONB,
    icon VARCHAR(100),
    color INTEGER,
    is_private BOOLEAN DEFAULT FALSE,
    position_group VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Category configurations (runtime instances)
CREATE TABLE categories (
    id VARCHAR(50) PRIMARY KEY,
    guild_id VARCHAR(50) NOT NULL,
    template_id VARCHAR(50) REFERENCES categories(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    position INTEGER,
    is_private BOOLEAN DEFAULT FALSE,
    permissions JSONB,
    custom_properties JSONB,
    discord_id VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Channel to category mappings (replacing CATEGORY_CHANNEL_MAPPINGS)
CREATE TABLE category_channel_mappings (
    id VARCHAR(50) PRIMARY KEY,
    category_template_id VARCHAR(50) REFERENCES categories(id) ON DELETE CASCADE,
    channel_template_id VARCHAR(50) REFERENCES channels(id) ON DELETE CASCADE,
    position INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(category_template_id, channel_template_id)
);
```

## 7. Implementation Steps

1. **Create Domain Models**:
   - Define `CategoryModel` with properties and validation
   - Create repository interface with CRUD operations
   - Define domain events for category lifecycle

2. **Reference Database Schema**:
   - Create domain models that map to existing database tables
   - Import shared database models from `app/shared`

3. **Implement Repository**:
   - Create PostgreSQL implementation of repository
   - Map between database records and domain models
   - Implement caching for frequently accessed categories

4. **Refactor Services**:
   - Migrate logic from current `CategorySetupService` to new architecture
   - Extract Discord-specific code to infrastructure layer
   - Create dedicated permission service

5. **Create Infrastructure**:
   - Implement repository with Discord API integration
   - Create caching layer to optimize API calls
   - Implement event handlers

6. **Add User Interface**:
   - Create slash commands for category management
   - Implement controller to handle command requests
   - Add proper error handling and user feedback
   - Create template selection interface

## 8. Migration from Hardcoded to Database

1. **Seed Initial Data**:
   - Create database entries for all categories in `category_constants.py`
   - Populate categories with default categories
   - Set up category_channel_mappings based on CATEGORY_CHANNEL_MAPPINGS

2. **Update CategorySetupService**:
   - Modify to load category definitions from database
   - Create CategoryBuilder to construct categories from templates
   - Keep backward compatibility during transition

3. **Replace Constants Usage**:
   - Update all references to `category_constants.py` to use repository
   - Create domain models for runtime use
   - Maintain fallback to constants if database unavailable
