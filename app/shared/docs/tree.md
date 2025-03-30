´´´tree
.
├── application
│   ├── logging
│   │   ├── formatters.py
│   │   └── log_config.py
│   └── tasks
│       └── schedule_key_rotation.py
├── bot
│   └── infrastructure
│       └── entrypoint.py
├── config
│   └── default_config.py
├── docs
│   ├── structure_shared_infrastrcuture_models.md
│   ├── structure_shared.md
│   └── tree.md
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
│   │   ├── entities
│   │   ├── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── permission.py
│   │   │   ├── role.py
│   │   │   └── user.py
│   │   ├── policies
│   │   │   ├── authorization_policies.py
│   │   │   └── __init__.py
│   │   ├── repositories
│   │   └── services
│   │       ├── authentication_service.py
│   │       ├── authorization_service.py
│   │       ├── __init__.py
│   │       └── permission_service.py
│   ├── dashboard
│   │   ├── models
│   │   ├── repositories
│   │   └── services
│   ├── discord
│   │   ├── models
│   │   ├── repositories
│   │   └── services
│   ├── __init__.py
│   ├── models
│   │   ├── dashboard
│   │   │   ├── dashboard_model.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── category_model.py
│   │   │   ├── channel_model.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── monitoring
│   │   ├── models
│   │   ├── repositories
│   │   └── services
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
│   │   ├── discord
│   │   │   ├── category_repository.py
│   │   │   ├── channel_repository.py
│   │   │   ├── dashboard_repository.py
│   │   │   ├── guild_config_repository.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   └── __init__.py
│   │   ├── projects
│   │   │   ├── __init__.py
│   │   │   ├── project_repository.py
│   │   │   └── task_repository.py
│   │   └── utils
│   │       └── __init__.py
│   └── TREE.md
├── infrastructure
│   ├── config
│   │   ├── env_config.py
│   │   ├── env_loader.py
│   │   ├── env_manager.py
│   │   └── __init__.py
│   ├── constants
│   │   ├── category_constants.py
│   │   ├── channel_constants.py
│   │   ├── dashboard_constants.py
│   │   ├── __init__.py
│   │   ├── role_constants.py
│   │   └── user_constants.py
│   ├── database
│   │   ├── api.py
│   │   ├── bootstrapper.py
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
│   │   │   │       ├── 001_create_tables.py
│   │   │   │       ├── 002_seed_categories.py
│   │   │   │       ├── 003_seed_channels.py
│   │   │   │       ├── 004_seed_dashboards.py
│   │   │   │       └── 005_create_users.py
│   │   │   ├── create_config_table.py
│   │   │   ├── init_db.py
│   │   │   ├── __init__.py
│   │   │   ├── init_variables.py
│   │   │   ├── migration_service.py
│   │   │   ├── README.md
│   │   │   ├── script.py.mako
│   │   │   └── wait_for_postgres.py
│   │   ├── seeds
│   │   │   └── dashboard_instances
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
│   ├── integration
│   │   ├── bot_connector.py
│   │   └── __init__.py
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
│   │   │   ├── component_layout_entity.py
│   │   │   ├── content_template_entity.py
│   │   │   ├── dashboard_component_entity.py
│   │   │   ├── dashboard_entity.py
│   │   │   ├── dashboard_message_entity.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── entities
│   │   │   │   ├── auto_thread_channel_entity.py
│   │   │   │   ├── category_entity.py
│   │   │   │   ├── channel_entity.py
│   │   │   │   ├── guild_config_entity.py
│   │   │   │   ├── guild_entity.py
│   │   │   │   ├── guild_user_entity.py
│   │   │   │   └── message_entity.py
│   │   │   ├── __init__.py
│   │   │   └── mappings
│   │   │       ├── category_mapping.py
│   │   │       └── channel_mapping.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   ├── alert.py
│   │   │   ├── __init__.py
│   │   │   └── metric.py
│   │   └── project
│   │       ├── __init__.py
│   │       ├── project_member.py
│   │       ├── project.py
│   │       └── task.py
│   ├── repositories
│   │   ├── audit
│   │   │   ├── auditlog_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── key_repository_impl.py
│   │   │   ├── session_repository_impl.py
│   │   │   └── user_repository_impl.py
│   │   ├── discord
│   │   │   ├── category_repository_impl.py
│   │   │   ├── channel_repository_impl.py
│   │   │   ├── dashboard_repository_impl.py
│   │   │   ├── guild_config_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   ├── __init__.py
│   │   │   └── monitoring_repository_impl.py
│   │   ├── projects
│   │   │   ├── __init__.py
│   │   │   ├── project_repository_impl.py
│   │   │   └── task_repository_impl.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── ratelimit_repository_impl.py
│   ├── security
│   │   ├── __init__.py
│   │   ├── security_bootstrapper.py
│   │   └── security_service.py
│   └── startup
│       ├── bootstrap.py
│       └── container.py
├── __init__.py
├── interface
│   ├── __init__.py
│   └── logging
│       ├── api.py
│       ├── factories.py
│       └── __init__.py
├── test
│   └── infrastructure
│       └── test_entrypoint.py
└── web
    └── infrastructure
        └── entrypoint.py
´´´