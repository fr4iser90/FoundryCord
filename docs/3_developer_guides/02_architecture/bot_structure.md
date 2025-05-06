# Bot Application Structure (`app/bot`)

This document details the internal structure of the [FoundryCord](docs/1_introduction/glossary.md#foundrycord) Bot application, located within the `app/bot/` directory. It aims to provide developers with an understanding of how the bot is organized, its architectural layers, key components, and entry points.

## Architectural Overview

The bot application generally follows a **Layered Architecture**, influenced by principles similar to Clean Architecture or Hexagonal Architecture, and concepts from [DDD (Domain-Driven Design)](docs/1_introduction/glossary.md#ddd-domain-driven-design). This promotes separation of concerns, testability, and maintainability. The main layers are typically:

*   **Interfaces:** Defines how the bot interacts with the outside world (e.g., Discord commands, internal APIs, bot-driven [dashboard](../1_introduction/glossary.md#dashboard) UIs).
*   **Application:** Orchestrates use cases and workflows, containing application-specific business logic. It uses services and domain objects to perform its tasks.
*   **Domain:** Contains the core business logic and entities specific to the bot's domain. *Currently, the `app/bot/domain/` directory appears to be minimal or empty, suggesting that most core domain logic might reside in `app/shared/domain/` to be accessible by both the bot and web applications.*
*   **Infrastructure:** Implements adapters to external systems and tools, such as Discord API interaction, configuration management, database access (via shared repositories), monitoring data collection, and startup/lifecycle management.

## Key Directory Breakdown

Below is a description of the primary sub-directories within `app/bot/` and their typical responsibilities:

*   **`app/bot/interfaces/`**: This layer acts as the entry point for all interactions with the bot.
    *   `api/internal/`: Exposes an internal HTTP API (likely using FastAPI or a similar lightweight framework) for the web application (Backend) to communicate with the bot for specific actions (e.g., triggering bot tasks).
    *   `commands/`: Contains the definitions for Discord slash commands, organized by functionality (e.g., `auth/`, `dashboard/`, `monitoring/`). This is where user interactions via Discord commands are handled. Includes decorators for argument parsing, permissions, etc.
    *   `dashboards/`: Manages the components and controllers for bot-driven interactive [dashboards](../1_introduction/glossary.md#dashboard) displayed within Discord (e.g., using embeds, buttons, selectors).

*   **`app/bot/application/`**: Contains the core application logic, orchestrating actions and workflows.
    *   `services/`: Houses various services that implement specific business functionalities or coordinate tasks (e.g., `DashboardLifecycleService`, `DiscordQueryService`, `SystemMonitoringService`).
    *   `tasks/`: Defines background tasks or scheduled jobs that the bot performs periodically (e.g., `CleanupTask`, `SecurityTasks`). These are often managed by a task scheduler integrated with `nextcord`.
    *   `workflows/`: Implements more complex, multi-step processes or use cases (e.g., `GuildTemplateWorkflow` related to [Guild Designer](../1_introduction/glossary.md#guild-designer), `DashboardWorkflow`). Workflows typically coordinate multiple services and domain objects.

*   **`app/bot/domain/`**: Intended for bot-specific domain entities, value objects, and domain services that are not shared with the web application. *As noted, if this directory is empty or sparse, it implies heavy reliance on `app/shared/domain/`.*

*   **`app/bot/infrastructure/`**: Provides the concrete implementations and integrations with external systems and shared infrastructure.
    *   `config/`: Manages bot-specific configuration loading, constants, registries (e.g., `ComponentRegistry`), and feature flags. It likely works in conjunction with `app/shared/infrastructure/config/`.
    *   `dashboards/`: Contains infrastructure related to bot dashboards, like registries for discoverable dashboard types.
    *   `discord/`: Handles lower-level interactions with the Discord API, factories for Discord objects (channels, threads), and potentially mappers for roles or other Discord entities.
    *   `factories/`: Implements factory patterns for creating various objects (services, tasks, workflows, components), promoting loose coupling and easier instantiation.
    *   `messaging/`: Utilities for sending messages to Discord, potentially handling message chunking, HTTP client wrappers for bot-specific external calls.
    *   `middleware/`: Contains middleware for bot operations, such as rate limiting for commands or API calls.
    *   `monitoring/`: Includes components for monitoring external services or game servers (`checkers/`) and collecting various metrics (`collectors/`) like system stats, game server data, or internal bot state. These collectors often feed data to dashboards or logging.
    *   `startup/`: Manages the bot's startup sequence, lifecycle events (e.g., `LifecycleManager`), setup hooks, and graceful shutdown. The main entry point for the bot application (`main.py`) is typically located here.
    *   `state/`: Manages or collects information about the bot's internal state, such as cog status, listener counts, or performance metrics.
    *   `wireguard/`: Contains infrastructure related to WireGuard VPN management, if integrated into the bot.

## Entry Point

The primary entry point for the bot application is likely **`app/bot/infrastructure/startup/main.py`**. This script would typically initialize the `nextcord.Bot` instance, load configurations, set up logging, register cogs/commands, and start the bot's connection to Discord.

## Configuration Loading

Configuration for the bot is loaded through a combination of:

1.  Environment variables (defined in `docker/.env` and loaded via `python-dotenv`).
2.  Configuration files or modules within `app/bot/infrastructure/config/`.
3.  Shared configuration mechanisms from `app/shared/infrastructure/config/`.

The `ConfigService` (e.g., `app/bot/application/services/config/config_service.py`) might be responsible for consolidating and providing access to these configurations throughout the application.

## Directory Tree (Visual Aid)

(The existing tree diagram from the file will be preserved below this section)

```tree
app/bot
├── application
│   ├── services
│   │   ├── bot_control_service.py
│   │   ├── category
│   │   │   ├── category_builder.py
│   │   │   ├── category_setup_service.py
│   │   │   └── __init__.py
│   │   ├── channel
│   │   │   ├── channel_builder.py
│   │   │   ├── channel_factory.py
│   │   │   ├── channel_setup_service.py
│   │   │   ├── game_server_channel_service.py
│   │   │   └── __init__.py
│   │   ├── config
│   │   │   ├── config_service.py
│   │   │   └── __init__.py
│   │   ├── dashboard
│   │   │   ├── component_loader_service.py
│   │   │   ├── dashboard_data_service.py
│   │   │   ├── dashboard_lifecycle_service.py
│   │   │   ├── dashboard_manager.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── discord_query_service.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   └── system_monitoring.py
│   │   ├── project_management
│   │   │   ├── __init__.py
│   │   │   ├── project_service.py
│   │   │   └── task_service.py
│   │   ├── system_metrics
│   │   │   ├── __init__.py
│   │   │   └── system_metrics_service.py
│   │   └── wireguard
│   │       ├── __init__.py
│   │       └── wireguard_service.py
│   ├── tasks
│   │   ├── cleanup_dm_task.py
│   │   ├── cleanup_task.py
│   │   └── security_tasks.py
│   ├── workflow_manager.py
│   └── workflows
│       ├── base_workflow.py
│       ├── bot_permission_workflow.py
│       ├── category
│       ├── category_workflow.py
│       ├── channel
│       ├── channel_workflow.py
│       ├── dashboard
│       ├── dashboard_workflow.py
│       ├── database_workflow.py
│       ├── guild
│       │   ├── approval.py
│       │   ├── check_structure.py
│       │   ├── initialization.py
│       │   ├── __init__.py
│       │   ├── state.py
│       │   ├── sync.py
│       │   └── template_application.py
│       ├── guild_template
│       │   ├── check_structure.py
│       │   ├── initialization.py
│       │   ├── __init__.py
│       │   └── state.py
│       ├── guild_template_workflow.py
│       ├── __init__.py
│       ├── overview_workflow.py
│       ├── service_manager.py
│       ├── service_workflow.py
│       ├── slash_commands_workflow.py
│       ├── task_workflow.py
│       ├── user
│       ├── user_workflow.py
│       ├── webinterface
│       └── webinterface_workflow.py
├── domain
├── infrastructure
│   ├── config
│   │   ├── command_config.py
│   │   ├── constants
│   │   │   ├── role_constants.py
│   │   │   └── user_config.py
│   │   ├── constants.py
│   │   ├── dashboard_config.py
│   │   ├── feature_flags.py
│   │   ├── __init__.py
│   │   ├── registries
│   │   │   └── component_registry.py
│   │   ├── service_config.py
│   │   ├── services
│   │   └── task_config.py
│   ├── dashboards
│   │   ├── dashboard_registry.py
│   │   └── __init__.py
│   ├── discord
│   │   ├── command_sync_service.py
│   │   ├── factories
│   │   │   ├── channel_factory.py
│   │   │   └── thread_factory.py
│   │   ├── game_server_channels.py
│   │   └── role_mapper.py
│   ├── factories
│   │   ├── base
│   │   │   ├── base_factory.py
│   │   │   └── __init__.py
│   │   ├── component_factory.py
│   │   ├── composite
│   │   │   ├── bot_factory.py
│   │   │   ├── __init__.py
│   │   │   └── workflow_factory.py
│   │   ├── __init__.py
│   │   ├── service_factory.py
│   │   └── task_factory.py
│   ├── __init__.py
│   ├── messaging
│   │   ├── chunk_manager.py
│   │   ├── http_client.py
│   │   ├── message_sender.py
│   │   └── response_mode.py
│   ├── middleware
│   │   └── rate_limiting
│   │       ├── __init__.py
│   │       ├── rate_limiting_middleware.py
│   │       └── rate_limiting_service.py
│   ├── monitoring
│   │   ├── checkers
│   │   │   ├── docker_utils.py
│   │   │   ├── game_service_checker.py
│   │   │   ├── __init__.py
│   │   │   ├── port_checker.py
│   │   │   └── web_service_checker.py
│   │   ├── collectors
│   │   │   ├── game_servers
│   │   │   │   ├── __init__.py
│   │   │   │   └── minecraft_server_collector_impl.py
│   │   │   ├── service
│   │   │   │   ├── components
│   │   │   │   │   ├── base.py
│   │   │   │   │   ├── docker.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── security.py
│   │   │   │   │   └── services.py
│   │   │   │   ├── config
│   │   │   │   │   ├── game_services.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── web_services.py
│   │   │   │   ├── impl.py
│   │   │   │   └── __init__.py
│   │   │   └── system
│   │   │       ├── components
│   │   │       │   ├── base.py
│   │   │       │   ├── hardware
│   │   │       │   │   ├── cpu.py
│   │   │       │   │   ├── gpu.py
│   │   │       │   │   ├── __init__.py
│   │   │       │   │   ├── memory.py
│   │   │       │   │   ├── network.py
│   │   │       │   │   ├── power.py
│   │   │       │   │   ├── sensors.py
│   │   │       │   │   ├── speed_test.py
│   │   │       │   │   └── system.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── network.py
│   │   │       │   ├── storage.py
│   │   │       │   └── system.py
│   │   │       ├── impl.py
│   │   │       └── __init__.py
│   │   └── __init__.py
│   ├── startup
│   │   ├── bot.py
│   │   ├── lifecycle_manager.py
│   │   ├── main.py
│   │   ├── setup_hooks.py
│   │   └── shutdown_handler.py
│   ├── state
│   │   └── collectors
│   │       ├── basic_info.py
│   │       ├── bot_status.py
│   │       ├── cog_status.py
│   │       ├── database_status.py
│   │       ├── discord_api.py
│   │       ├── listeners.py
│   │       └── performance.py
│   └── wireguard
├── __init__.py
├── interfaces
│   ├── api
│   │   └── internal
│   │       ├── routes.py
│   │       └── server.py
│   ├── commands
│   │   ├── auth
│   │   │   ├── auth_commands.py
│   │   │   └── __init__.py
│   │   ├── checks.py
│   │   ├── dashboard
│   │   │   └── dashboard_command.py
│   │   ├── decorators
│   │   │   ├── auth.py
│   │   │   └── respond.py
│   │   ├── monitoring
│   │   │   ├── __init__.py
│   │   │   └── system_monitoring_commands.py
│   │   ├── tracker
│   │   │   └── project_commands.py
│   │   ├── utils
│   │   │   └── clean
│   │   │       └── cleanup_commands.py
│   │   └── wireguard
│   │       ├── config_commands.py
│   │       ├── __init__.py
│   │       ├── qr_commands.py
│   │       ├── README.md
│   │       └── utils.py
│   └── dashboards
│       ├── components
│       │   ├── base_component.py
│       │   ├── common
│       │   │   ├── buttons
│       │   │   │   ├── generic_button.py
│       │   │   │   ├── __init__.py
│       │   │   │   └── refresh_button.py
│       │   │   ├── embeds
│       │   │   │   ├── dashboard_embed.py
│       │   │   │   ├── error_embed.py
│       │   │   │   └── __init__.py
│       │   │   └── selectors
│       │   │       ├── generic_selector.py
│       │   │       └── __init__.py
│       │   ├── factories
│       │   │   ├── button_factory.py
│       │   │   ├── embed_factory.py
│       │   │   ├── __init__.py
│       │   │   ├── menu_factory.py
│       │   │   └── modal_factory.py
│       │   ├── __init__.py
│       │   └── ui
│       │       ├── __init__.py
│       │       ├── mini_graph.py
│       │       └── table_builder.py
│       ├── controller
│       │   ├── dashboard_controller.py
│       │   └── __init__.py
│       └── __init__.py
└── requirements.txt

71 directories, 177 files
```
