# Channel Service Organization Plan

## 1. Domain Layer Refinement
- Create proper channel domain models in `app/bot/domain/channels/models/`
- Define repository interfaces in `app/bot/domain/channels/repositories/`
- Define channel types and validation rules
- Create channel template value objects

## 2. Application Layer Consolidation
- Keep `ChannelSetupService` as the main orchestrator
- Ensure `GameServerChannelService` delegates to main channel service
- Add channel-specific operations in dedicated services
- Create channel builder for database-driven channel creation

## 3. Infrastructure Layer Organization
- Create `app/bot/infrastructure/repositories/channel_repository_impl.py` using PostgreSQL
- Create Discord API adapter for channel operations
- Implement proper caching mechanisms for channel data
- Use shared database models from `app/shared/database/models/`

## 4. Interface Layer Setup
- Create commands and controllers for channel management
- Add proper error handling and user feedback
- Implement permission checking for commands
- Develop channel template selection UI

## 5. Service Structure Cleanup

### Application Layer (app/bot/application/)

```
app/bot/application/services/
├── channel/
│   ├── channel_service.py # Main orchestration service
│   ├── channel_setup_service.py # Channel setup workflows
│   ├── channel_builder.py # Channel builder from database
│   ├── channel_permission_service.py # Channel permissions
│   └── game_server_channel_service.py # Game server channels
```

**Key Principles:**
- Coordinates domain objects
- Implements use cases and workflows
- Doesn't have direct Discord API or database dependencies
- Uses repository interfaces, not implementations

### Domain Layer (app/bot/domain/)

```
app/bot/domain/channels/
├── models/
│   ├── channel_model.py # Core channel entity
│   ├── channel_type.py # Channel type definitions
│   └── channel_template.py # Channel template value object
├── repositories/
│   └── channel_repository.py # Repository interface
├── services/
│   └── channel_validator.py # Channel validation rules
└── events/
    └── channel_events.py # Domain events
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
│   └── channel_repository_impl.py # PostgreSQL repository implementation
├── discord/
│   └── channel_client.py # Discord API interactions
└── config/
    └── channel_config.py # Channel configuration
```

**Key Principles:**
- Implements interfaces defined in domain layer
- Contains Discord API and PostgreSQL interactions
- Framework-specific code
- Separates external concerns from business logic

### Interface Layer (app/bot/interfaces/)

```
app/bot/interfaces/channels/
├── commands/
│   ├── channel_commands.py # Channel slash commands
│   └── channel_context_menu.py # Context menu commands
├── controllers/
│   └── channel_controller.py # Channel workflow controller
└── components/
    ├── views/
    │   └── channel_template_selector.py # Template selection UI
    └── embeds/
        └── channel_config_embed.py # Channel configuration display
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
    │   ├── channel.py  # Channel database entity
    │   └── channel_template.py  # Channel template database entity
    └── core/
        └── connection.py  # Database connection manager
```

## 6. Database Schema Reference

The bot will read from these tables, which are managed by the web frontend:

```sql
-- Channel templates (replacing hardcoded channel definitions)
CREATE TABLE channels (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    channel_type VARCHAR(50) NOT NULL, -- TEXT, VOICE, FORUM, etc.
    default_permissions JSONB,
    topic TEXT,
    slowmode INTEGER,
    nsfw BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    position_strategy VARCHAR(50), -- TOP, BOTTOM, AFTER_PARENT
    icon VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Channel configurations (runtime instances)
CREATE TABLE channels (
    id VARCHAR(50) PRIMARY KEY,
    guild_id VARCHAR(50) NOT NULL,
    category_id VARCHAR(50) REFERENCES categories(id),
    template_id VARCHAR(50) REFERENCES channels(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    channel_type VARCHAR(50) NOT NULL,
    position INTEGER,
    topic TEXT,
    is_private BOOLEAN DEFAULT FALSE,
    permissions JSONB,
    custom_properties JSONB,
    discord_id VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Thread templates (replacing thread configurations in constants)
CREATE TABLE thread_templates (
    id VARCHAR(50) PRIMARY KEY,
    channel_template_id VARCHAR(50) REFERENCES channels(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    auto_archive_duration INTEGER DEFAULT 1440, -- minutes (1 day)
    slowmode INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Thread configurations (runtime instances)
CREATE TABLE threads (
    id VARCHAR(50) PRIMARY KEY,
    channel_id VARCHAR(50) REFERENCES channels(id) ON DELETE CASCADE,
    template_id VARCHAR(50) REFERENCES thread_templates(id),
    name VARCHAR(100) NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    auto_archive_duration INTEGER,
    discord_id VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Game server channel configurations (replacing GameServerChannelConfig)
CREATE TABLE game_server_channels (
    id VARCHAR(50) PRIMARY KEY,
    channel_id VARCHAR(50) REFERENCES channels(id) ON DELETE CASCADE,
    game_server_id VARCHAR(50) NOT NULL,
    server_type VARCHAR(50) NOT NULL, -- minecraft, factorio, valheim, etc.
    update_interval INTEGER NOT NULL DEFAULT 60,
    display_format JSONB, -- How to format game server info
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 7. Implementation Steps

1. **Create Domain Models**:
   - Define `ChannelModel` with properties and validation
   - Create channel type enumerations and templates
   - Define repository interface

2. **Reference Database Schema**:
   - Create domain models that map to existing database tables
   - Import shared database models from `app/shared`

3. **Implement Repository**:
   - Create PostgreSQL implementation of repository
   - Map between database records and domain models
   - Implement caching for frequently accessed channels

4. **Refactor Services**:
   - Migrate logic from current `ChannelSetupService` to new architecture
   - Extract Discord-specific code to infrastructure layer
   - Create proper domain services
   - Implement channel builder from database

5. **Create Commands and Controllers**:
   - Implement slash commands for channel management
   - Create controllers to handle command requests
   - Ensure proper permission checking
   - Build template selection interface

6. **Integration Testing**:
   - Test channel creation, update, and deletion workflows
   - Ensure proper error handling
   - Verify permissions are enforced correctly
   - Test database-driven channel creation

## 8. Migration from Hardcoded to Database

1. **Seed Initial Data**:
   - Create database entries for all channels in `channel_constants.py`
   - Populate channels with default channels
   - Create thread_templates based on thread definitions

2. **Update ChannelSetupService**:
   - Modify to load channel definitions from database
   - Create ChannelBuilder to construct channels from templates
   - Keep backward compatibility during transition

3. **Replace Constants Usage**:
   - Update all references to `channel_constants.py` to use repository
   - Create domain models for runtime use
   - Maintain fallback to constants if database unavailable