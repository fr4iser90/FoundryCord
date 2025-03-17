# Dashboard Controller Structure

## Overview

This document outlines the standardized structure for dashboard controllers in the HomeLab Discord Bot. By following these patterns, we ensure consistency across all dashboard implementations and facilitate maintenance and new feature development.
We got all data from the database and display it in the dashboard.
## Related Documentation
- [Dashboard Pattern](./DASHBOARD_PATTERN.md) - Overall dashboard implementation workflow
- [UI Designer Role](../../ai/roles/ui/BOT_UI_DESIGNER.md) - Role responsible for dashboard design
- [Data Flow Patterns](../architecture/DATA_FLOW.md) - Understanding data flow in dashboards

## Controller Hierarchy

```
BaseDashboardController
├── WelcomeDashboardController
├── MonitoringDashboardController
├── ProjectDashboardController
├── GameHubDashboardController
├── MinecraftServerDashboardController
└── [Other Specialized Controllers]
```

## System Architecture

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

## Directory Structure

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

