# Shared Core Library Structure (`app/shared`)

This document details the internal structure of the FoundryCord Shared Core Library, located within the `app/shared/` directory. This library is fundamental to the project, providing common functionalities, domain logic, and infrastructure components negócios by both the Bot (`app/bot/`) and Web (`app/web/`) applications. Its primary goal is to promote code reuse, maintain consistency, and establish a single source of truth for core concepts.

## Architectural Role

The `app/shared/` directory embodies the principle of a **shared kernel** or common library within a layered architecture. It provides essential components that span across different layers (Domain, Application, Infrastructure) and are consumed by the more specialized Bot and Web applications.

*   **Shared Domain:** This is the most critical part, containing the core business entities, value objects, domain services, repository interfaces (contracts for data access), and custom domain exceptions. It defines the Ubiquitous Language of the project.
*   **Shared Application Services:** Includes common application-level services like logging configuration and potentially other cross-cutting concerns usable by both applications.
*   **Shared Infrastructure:** Provides concrete implementations for common infrastructure needs, such as database access (SQLAlchemy models, session management, base repositories), environment configuration utilities, encryption services, and Alembic database migrations.

By centralizing these elements, `app/shared/` ensures that both the Bot and Web applications operate on the same understanding of the domain, use consistent data structures, and benefit from common infrastructure utilities.

## Key Directory Breakdown

Below is a description of the primary sub-directories within `app/shared/` and their typical responsibilities:

*   **`app/shared/application/`**: Contains application-level services and tasks that are common enough to be shared.
    *   `logging/`: Centralized logging configuration (e.g., `log_config.py`, shared `formatters.py`).
    *   `services/monitoring/`: Example of a shared service, like `StateSnapshotService` if it provides data for both bot and web.
    *   `tasks/`: Definitions for any background tasks that might be relevant or triggered by either application (e.g., `schedule_key_rotation.py`).

*   **`app/shared/domain/`**: This is the heart of the shared core, defining the business model.
    *   `audit/`, `auth/`, `monitoring/`, etc.: These sub-directories represent different sub-domains or Bounded Contexts within the core application. Each typically contains:
        *   `entities/`: Domain entities and value objects (e.g., `User`, `Guild`, `AuditRecord`).
        *   `repositories/`: Interfaces (abstract base classes) defining the contracts for data persistence operations related to the sub-domain (e.g., `UserRepository`, `GuildTemplateRepository`).
        *   `services/`: Domain services that encapsulate core business logic not naturally fitting within an entity.
        *   `policies/`: Authorization policies or business rules.
    *   `exceptions.py`: Common custom domain exceptions.

*   **`app/shared/infrastructure/`**: Provides concrete implementations for shared infrastructure concerns.
    *   `config/`: Utilities for loading environment variables (`env_loader.py`, `env_config.py`) and potentially shared configuration models.
    *   `constants/`: Shared constant values (e.g., `role_constants.py`).
    *   `database/`: Core database setup, including:
        *   `core/`: Connection management, base SQLAlchemy configuration.
        *   `migrations/`: Alembic configuration (`alembic.ini`, `env.py`) and version scripts for database schema evolution.
        *   `seeds/`: Scripts or data for seeding the database with initial or default data (e.g., `dashboard_templates/`).
        *   `session/`: SQLAlchemy session management (e.g., `factory.py` for creating sessions).
    *   `encryption/`: Services for data encryption and management of encryption keys.
    *   `logging/`: Shared logging infrastructure, such as custom handlers (e.g., `DBHandler`), log data models (`log_entry.py`), and concrete log repository implementations.
    *   `models/`: SQLAlchemy ORM models (database table definitions) corresponding to the domain entities. Organized by domain concern (e.g., `auth/`, `core/`, `dashboards/`, `discord/`, `guild_templates/`).
    *   `repositories/`: Concrete implementations of the repository interfaces defined in `app/shared/domain/repositories/`. These implementations use SQLAlchemy to interact with the database.
    *   `security/`: Shared security utilities, potentially related to password hashing, token validation, etc.
    *   `startup/`: Shared application startup logic or base classes that might be used by both bot and web startup processes.
    *   `state/`: Shared components related to managing or collecting application state (e.g., shared `collectors/` for system state).
    *   `system/`: Low-level system utilities shared across applications.

*   **`app/shared/interfaces/`**: Contains shared interface definitions or base classes for interfaces if applicable.
    *   `logging/`: Might contain base classes or common interfaces for logging services used by both bot and web.

*   **`app/shared/initializers/`**: If this directory exists, it would typically contain modules responsible for initializing shared resources or application context when the bot or web app starts. (This directory was not in the initial provided tree but is a common pattern).

## Consumption by Bot and Web Applications

Both `app/bot/` and `app/web/` extensively import and utilize the components defined in `app/shared/`. For instance:

*   Web API controllers and Bot command handlers might use shared Application Services or Domain Services.
*   Both applications rely on shared Repository implementations for data access.
*   Both use shared SQLAlchemy models for database interaction.
*   Both leverage shared configuration utilities and logging setups.

This shared approach is crucial for maintaining data integrity, consistent business rule enforcement, and reducing code duplication.

## Directory Tree (Visual Aid)

(The existing tree diagram from the file will be preserved below this section)

```tree
app/shared
├── application
│   ├── logging
│   │   ├── formatters.py
│   │   └── log_config.py
│   ├── services
│   │   └── monitoring
│   │       └── state_snapshot_service.py
│   └── tasks
│       └── schedule_key_rotation.py
├── domain
│   ├── audit
│   │   ├── entities
│   │   │   ├── audit_record.py
│   │   │   └── __init__.py
│   │   ├── repositories
│   │   │   ├── audit_repository.py
│   │   │   └── __init__.py
│   │   └── services
│   │       ├── audit_service.py
│   │       └── __init__.py
│   ├── auth
│   │   ├── __init__.py
│   │   ├── policies
│   │   │   ├── authorization_policies.py
│   │   │   └── __init__.py
│   │   └── services
│   │       ├── authentication_service.py
│   │       ├── authorization_service.py
│   │       ├── __init__.py
│   │       └── permission_service.py
│   ├── exceptions.py
│   ├── __init__.py
│   ├── monitoring
│   │   ├── collectors
│   │   │   ├── __init__.py
│   │   │   ├── service_collector.py
│   │   │   └── system_collector.py
│   │   ├── factories
│   │   │   ├── collector_factory.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── repositories
│   │   ├── audit
│   │   │   ├── audit_log_repository.py
│   │   │   └── __init__.py
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── key_repository.py
│   │   │   ├── session_repository.py
│   │   │   └── user_repository.py
│   │   ├── base_repository.py
│   │   ├── dashboards
│   │   │   ├── active_dashboard_repository.py
│   │   │   ├── dashboard_component_definition_repository.py
│   │   │   ├── dashboard_configuration_repository.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── category_repository.py
│   │   │   ├── channel_repository.py
│   │   │   ├── guild_config_repository.py
│   │   │   ├── guild_repository.py
│   │   │   └── __init__.py
│   │   ├── guild_templates
│   │   │   ├── guild_template_category_permission_repository.py
│   │   │   ├── guild_template_category_repository.py
│   │   │   ├── guild_template_channel_permission_repository.py
│   │   │   ├── guild_template_channel_repository.py
│   │   │   ├── guild_template_repository.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   ├── __init__.py
│   │   │   └── monitoring_repository.py
│   │   ├── projects
│   │   │   ├── __init__.py
│   │   │   ├── project_repository.py
│   │   │   └── task_repository.py
│   │   ├── templates
│   │   ├── ui
│   │   │   └── ui_layout_repository.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── ratelimit_repository.py
│   └── services
│       ├── __init__.py
│       └── wireguard
│           ├── config_manager.py
│           └── __init__.py
├── infrastructure
│   ├── config
│   │   ├── env_config.py
│   │   ├── env_loader.py
│   │   ├── env_manager.py
│   │   └── __init__.py
│   ├── constants
│   │   ├── __init__.py
│   │   ├── role_constants.py
│   │   └── user_constants.py
│   ├── database
│   │   ├── api.py
│   │   ├── config
│   │   │   └── user_config.py
│   │   ├── core
│   │   │   ├── config.py
│   │   │   ├── connection.py
│   │   │   ├── credentials.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── alembic
│   │   │   │   ├── alembic.ini
│   │   │   │   ├── env.py
│   │   │   │   └── versions
│   │   │   │       ├── 001_create_core_auth_tables.py
│   │   │   │       ├── 002_create_discord_guild_tables.py
│   │   │   │       ├── 003_create_guild_template_tables.py
│   │   │   │       ├── 004_create_guild_config_table.py
│   │   │   │       ├── 005_create_dashboard_tables.py
│   │   │   │       ├── 006_create_project_tables.py
│   │   │   │       ├── 007_create_ui_tables.py
│   │   │   │       ├── 008_seed_users.py
│   │   │   │       ├── 009_seed_dashboard_component_definitions.py
│   │   │   │       ├── 010_create_state_snapshots_table.py
│   │   │   │       ├── 011_seed_default_dashboards.py
│   │   │   │       └── 012_create_active_dashboards_table.py
│   │   │   ├── __init__.py
│   │   │   ├── migration_service.py
│   │   │   ├── README.md
│   │   │   ├── script.py.mako
│   │   │   └── wait_for_postgres.py
│   │   ├── seeds
│   │   │   └── dashboard_templates
│   │   │       ├── common
│   │   │       │   ├── buttons.py
│   │   │       │   ├── embeds.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── messages.py
│   │   │       │   ├── modals.py
│   │   │       │   ├── selectors.py
│   │   │       │   └── views.py
│   │   │       ├── gamehub
│   │   │       │   ├── buttons.py
│   │   │       │   ├── embeds.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── messages.py
│   │   │       │   ├── modals.py
│   │   │       │   ├── selectors.py
│   │   │       │   └── views.py
│   │   │       ├── monitoring
│   │   │       │   ├── buttons.py
│   │   │       │   ├── embeds.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── messages.py
│   │   │       │   ├── modals.py
│   │   │       │   ├── selectors.py
│   │   │       │   └── views.py
│   │   │       ├── project
│   │   │       │   ├── buttons.py
│   │   │       │   ├── embeds.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── messages.py
│   │   │       │   ├── modals.py
│   │   │       │   ├── selectors.py
│   │   │       │   └── views.py
│   │   │       └── welcome
│   │   │           ├── buttons.py
│   │   │           ├── embeds.py
│   │   │           ├── __init__.py
│   │   │           ├── messages.py
│   │   │           ├── modals.py
│   │   │           ├── selectors.py
│   │   │           └── views.py
│   │   ├── service.py
│   │   └── session
│   │       ├── context.py
│   │       ├── factory.py
│   │       └── __init__.py
│   ├── encryption
│   │   ├── encryption_commands.py
│   │   ├── encryption_service.py
│   │   ├── __init__.py
│   │   └── key_management_service.py
│   ├── __init__.py
│   ├── logging
│   │   ├── handlers
│   │   │   ├── db_handler.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── log_entry.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   └── log_repository_impl.py
│   │   └── services
│   │       ├── base_logging_service.py
│   │       ├── bot_logging_service.py
│   │       ├── __init__.py
│   │       ├── logging_service.py
│   │       └── web_logging_service.py
│   ├── models
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── rate_limit_entity.py
│   │   │   ├── role_entity.py
│   │   │   ├── session_entity.py
│   │   │   └── user_entity.py
│   │   ├── base.py
│   │   ├── core
│   │   │   ├── audit_log_entity.py
│   │   │   ├── config_entity.py
│   │   │   ├── __init__.py
│   │   │   └── log_entry_entity.py
│   │   ├── dashboards
│   │   │   ├── active_dashboard_entity.py
│   │   │   ├── dashboard_component_definition_entity.py
│   │   │   ├── dashboard_configuration_entity.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── entities
│   │   │   │   ├── auto_thread_channel_entity.py
│   │   │   │   ├── category_entity.py
│   │   │   │   ├── channel_entity.py
│   │   │   │   ├── guild_config_entity.py
│   │   │   │   ├── guild_entity.py
│   │   │   │   ├── guild_user_entity.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── message_entity.py
│   │   │   ├── enums
│   │   │   │   ├── category.py
│   │   │   │   ├── channels.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── guild.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── message.py
│   │   │   ├── __init__.py
│   │   │   └── mappings
│   │   │       ├── category_mapping.py
│   │   │       └── channel_mapping.py
│   │   ├── guild_templates
│   │   │   ├── guild_template_category_entity.py
│   │   │   ├── guild_template_category_permission_entity.py
│   │   │   ├── guild_template_channel_entity.py
│   │   │   ├── guild_template_channel_permission_entity.py
│   │   │   ├── guild_template_entity.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   ├── alert.py
│   │   │   ├── __init__.py
│   │   │   ├── metric.py
│   │   │   └── state_snapshot.py
│   │   ├── project
│   │   │   ├── __init__.py
│   │   │   ├── project_entity.py
│   │   │   ├── project_member.py
│   │   │   └── task_entity.py
│   │   └── ui
│   │       ├── __init__.py
│   │       └── ui_layout_entity.py
│   ├── repositories
│   │   ├── audit
│   │   │   ├── auditlog_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── key_repository_impl.py
│   │   │   ├── session_repository_impl.py
│   │   │   └── user_repository_impl.py
│   │   ├── base_repository_impl.py
│   │   ├── dashboards
│   │   │   ├── active_dashboard_repository_impl.py
│   │   │   ├── dashboard_component_definition_repository_impl.py
│   │   │   ├── dashboard_configuration_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── category_repository_impl.py
│   │   │   ├── channel_repository_impl.py
│   │   │   ├── guild_config_repository_impl.py
│   │   │   ├── guild_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── guild_templates
│   │   │   ├── guild_template_category_permission_repository_impl.py
│   │   │   ├── guild_template_category_repository_impl.py
│   │   │   ├── guild_template_channel_permission_repository_impl.py
│   │   │   ├── guild_template_channel_repository_impl.py
│   │   │   ├── guild_template_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   ├── __init__.py
│   │   │   └── monitoring_repository_impl.py
│   │   ├── projects
│   │   │   ├── __init__.py
│   │   │   ├── project_repository_impl.py
│   │   │   └── task_repository_impl.py
│   │   ├── ui
│   │   │   ├── __init__.py
│   │   │   └── ui_layout_repository_impl.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── ratelimit_repository_impl.py
│   ├── security
│   │   ├── __init__.py
│   │   ├── security_bootstrapper.py
│   │   └── security_service.py
│   ├── startup
│   │   ├── bootstrap.py
│   │   ├── bot_entrypoint.py
│   │   └── web_entrypoint.py
│   ├── state
│   │   ├── collectors
│   │   │   ├── database_status.py
│   │   │   └── system_info.py
│   │   └── secure_state_snapshot.py
│   └── system
│       └── state_collectors.py
├── initializers
│   └── state_collectors.py
├── __init__.py
├── interfaces
│   ├── __init__.py
│   └── logging
│       ├── api.py
│       ├── factories.py
│       └── __init__.py
└── test
    └── infrastructure
        └── test_entrypoint.py

85 directories, 245 files
```
