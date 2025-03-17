# Homelab Discord Bot Implementation Action Plan

## 1. Overview

This action plan outlines our strategy for implementing data-driven architecture in the Homelab Discord Bot. We're migrating from hardcoded configuration to a database-driven approach, where all configuration is stored in PostgreSQL and managed through the web frontend.

## 2. Implementation Sequence

We will implement the data-driven architecture in the following sequence:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. Category    │───▶│  2. Channel     │───▶│  3. Dashboard   │
│     Service     │    │     Service     │    │     Service     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

This sequence is designed to build a strong foundation first (categories), then add complexity (channels), and finally implement the most complex and user-facing components (dashboards).

## 3. Phase 1: Category Service (Week 1)

Categories form the foundation of our Discord server structure.

### Tasks:
1. **Domain Layer (Days 1-2)**
   - Create `CategoryModel` and `CategoryTemplate` in `app/bot/domain/categories/models/`
   - Define repository interface in `app/bot/domain/categories/repositories/`
   - Implement validation rules in domain services

2. **Infrastructure Layer (Days 3-4)**
   - Implement `CategoryRepositoryImpl` in `app/bot/infrastructure/repositories/`
   - Create database seed migration for category data from `category_constants.py`
   - Set up category-channel mappings in database

3. **Application Layer (Days 4-5)**
   - Refactor `CategorySetupService` to use the repository
   - Create `CategoryBuilder` to build from templates
   - Implement backward compatibility with constants

### Success Criteria:
- Categories can be created from database definitions
- All existing hardcoded categories are available in the database
- The system falls back to constants if database is unavailable

## 4. Phase 2: Channel Service (Week 2)

Channels depend on categories and form the structure for user interaction.

### Tasks:
1. **Domain Layer (Days 1-2)**
   - Create `ChannelModel` and `ChannelTemplate` in `app/bot/domain/channels/models/`
   - Define repository interface in `app/bot/domain/channels/repositories/`
   - Implement channel type and thread models

2. **Infrastructure Layer (Days 3-4)**
   - Implement `ChannelRepositoryImpl` in `app/bot/infrastructure/repositories/`
   - Create database seed migration for channel data from `channel_constants.py`
   - Set up thread template data in database

3. **Application Layer (Days 4-5)**
   - Refactor `ChannelSetupService` to use the repository
   - Create `ChannelBuilder` to build from templates
   - Ensure proper sequencing with category creation

### Success Criteria:
- Channels can be created from database definitions
- Thread configurations are properly handled
- Channel-to-category relationships are maintained
- Game server channels are correctly configured

## 5. Phase 3: Dashboard Service (Weeks 3-4)

Dashboards are the most complex and visible component of our system.

### Tasks:
1. **Domain Layer (Days 1-3)**
   - Create dashboard and component models in `app/bot/domain/dashboards/models/`
   - Define repository interfaces for dashboards and components
   - Implement data source abstractions

2. **Component Registry (Days 4-6)**
   - Create component registry system in infrastructure
   - Implement factory pattern for component creation
   - Set up data source providers

3. **Dashboard Builder (Days 7-9)**
   - Create dashboard builder to assemble dashboards from database
   - Implement view model generation for components
   - Set up refresh/lifecycle management

4. **Migration & Testing (Days 10-14)**
   - Use existing migration data from `app/shared/infrastructure/database/migrations/dashboards/`
   - Run existing `dashboard_components_migration.py`
   - Test all dashboard types: welcome, monitoring, gamehub, project

### Success Criteria:
- All dashboard types can be created from database definitions
- Components are dynamically loaded based on database configuration
- Data sources correctly provide information to components
- Dashboards maintain state and can be refreshed

## 6. Dashboard Controller Structure

```
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│  DashboardManager │────│ DynamicDashboard  │────│  ComponentRegistry│
│   (Coordinator)   │    │   Controller      │    │  (Factory)        │
└───────────────────┘    └───────────────────┘    └───────────────────┘
         │                        │                        │
         │                        │                        │
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│    Dashboard      │    │    Dashboard      │    │    Component      │
│    Repository     │────│     Builder       │────│    Instances      │
│  (Data Storage)   │    │ (Assembler)       │    │  (UI Elements)    │
└───────────────────┘    └───────────────────┘    └───────────────────┘
         │                        │                        │
         │                        │                        │
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│   Data Source     │    │    View Model     │    │    Interaction    │
│    Registry       │────│     Builder       │────│     Handlers      │
│ (Data Providers)  │    │ (Data Formatter)  │    │   (Callbacks)     │
└───────────────────┘    └───────────────────┘    └───────────────────┘
```

## 7. Directory Structure

```
app/bot/
├── domain/
│   └── dashboards/
│       ├── models/
│       │   ├── dashboard_model.py           # Core dashboard domain models
│       │   ├── component_model.py           # Component domain models
│       │   └── data_source_model.py         # Data source domain models
│       ├── repositories/                    # Repository interfaces
│       │   └── dashboard_repository.py      # Dashboard repository interface
│       └── services/                        # Domain services
│           ├── data_processor_service.py    # Processing data for display
│           └── component_service.py         # Component business logic
│
├── application/
│   └── services/
│       └── dashboard/
│           ├── dashboard_service.py         # Dashboard orchestration
│           ├── dashboard_builder.py         # Dashboard assembly 
│           ├── data_source_service.py       # Data retrieval coordination
│           └── component_service.py         # Component service (uses domain)
│
├── infrastructure/
│   ├── repositories/
│   │   └── dashboard_repository_impl.py     # Repository implementation
│   ├── discord/
│   │   ├── message_tracker.py              # Discord message tracking
│   │   └── dashboard_channel.py            # Dashboard channel management
│   ├── factories/
│   │   ├── component_registry.py           # Component registration
│   │   └── data_source_registry.py         # Data source registration
│   ├── data_sources/                       # Data source implementations
│   │   ├── system_data_source.py           # System metrics source
│   │   └── minecraft_data_source.py        # Game server metrics source
│   └── persistence/                        # Database entities/schemas
│       └── dashboard_entity.py             # DB entity for dashboard
│
└── interfaces/
    └── dashboards/
        ├── controller/
        │   ├── base_dashboard.py           # Base controller
        │   ├── dynamic_dashboard.py        # Dynamic controller
        │   └── system_dashboard.py         # Specialized controller
        └── components/
            ├── common/
            │   ├── buttons/
            │   │   ├── refresh_button.py   # Shared refresh button
            │   │   └── navigation_button.py # Navigation buttons
            │   ├── embeds/
            │   │   ├── dashboard_embed.py  # Dashboard embed template
            │   │   └── error_embed.py      # Error embed template
            │   └── views/
            │       └── base_view.py        # Base Discord view
            └── specific/
                ├── status_indicator.py     # Status indicator component
                ├── metric_display.py       # Metric display component
                └── chart_component.py      # Chart component
```

## 8. Implementation Timeline

```
Week 1: Category Service
┌───────────────┐
│ Domain Models │──────┐
└───────────────┘      │
                       ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Repositories  │───▶│ Setup Service │───▶│ Database Seed │
└───────────────┘    └───────────────┘    └───────────────┘

Week 2: Channel Service
┌───────────────┐
│ Domain Models │──────┐
└───────────────┘      │
                       ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Repositories  │───▶│ Channel       │───▶│ Database Seed │
└───────────────┘    │ Builder       │    └───────────────┘
                     └───────────────┘

Week 3-4: Dashboard Service
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Domain Models │───▶│ Component     │───▶│ Dashboard     │
└───────────────┘    │ Registry      │    │ Builder       │
                     └───────────────┘    └───────────────┘
                                               │
┌───────────────┐    ┌───────────────┐         │
│ Use Existing  │◀───┤ Dashboard     │◀────────┘
│ Migration Data│    │ Service       │
└───────────────┘    └───────────────┘
```

## 9. Resources and References

- Category Service Plan: `docs/planning/services/category-service-plan.md`
- Channel Service Plan: `docs/planning/services/channel-service-plan.md`
- Dashboard Service Plan: `docs/planning/services/dashboard-service-plan.md`
- General Service Plan: `docs/planning/services/general-service-plan.md`
- Existing Dashboard Components: `app/shared/infrastructure/database/migrations/dashboards/`