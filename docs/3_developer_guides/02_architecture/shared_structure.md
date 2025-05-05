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
