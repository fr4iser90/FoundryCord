 fr4iser@WorkStation  ~/Documents/Git/NCC-DiscordBot   main ±  tree 
.
├── app
│   ├── bot
│   │   ├── application
│   │   │   ├── services
│   │   │   │   ├── channel
│   │   │   │   │   └── game_server_channel_service.py
│   │   │   │   ├── dashboard
│   │   │   │   │   ├── dynamic_minecraft_dashboard_service.py
│   │   │   │   │   ├── gamehub_dashboard_service.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── monitoring_dashboard_service.py
│   │   │   │   │   ├── project_dashboard_service.py
│   │   │   │   │   └── welcome_dashboard_service.py
│   │   │   │   ├── monitoring
│   │   │   │   │   └── system_monitoring.py
│   │   │   │   └── wireguard
│   │   │   │       ├── __init__.py
│   │   │   │       └── wireguard_service.py
│   │   │   └── tasks
│   │   │       ├── cleanup_dm_task.py
│   │   │       ├── cleanup_task.py
│   │   │       └── security_tasks.py
│   │   ├── config
│   │   ├── core
│   │   │   ├── extensions.py
│   │   │   ├── __init__.py
│   │   │   ├── lifecycle
│   │   │   │   └── lifecycle_manager.py
│   │   │   ├── main.py
│   │   │   └── workflows
│   │   │       ├── base_workflow.py
│   │   │       ├── category_workflow.py
│   │   │       ├── channel_workflow.py
│   │   │       ├── dashboard_workflow.py
│   │   │       ├── database_workflow.py
│   │   │       ├── service_workflow.py
│   │   │       ├── slash_commands_workflow.py
│   │   │       └── task_workflow.py
│   │   ├── database
│   │   │   └── credentials
│   │   │       └── db_credentials
│   │   ├── dev
│   │   │   ├── dev_server.py
│   │   │   └── reload_commands.py
│   │   ├── domain
│   │   │   ├── auth
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── permission.py
│   │   │   │   │   ├── permissions.py
│   │   │   │   │   ├── role.py
│   │   │   │   │   └── user.py
│   │   │   │   ├── policies
│   │   │   │   │   ├── authorization_policies.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── repositories
│   │   │   │   │   └── user_repository.py
│   │   │   │   └── services
│   │   │   │       ├── __init__.py
│   │   │   │       └── permission_service.py
│   │   │   ├── gameservers
│   │   │   │   ├── collectors
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── minecraft
│   │   │   │   │       └── minecraft_server_collector.py
│   │   │   │   └── models
│   │   │   │       ├── gameserver_metrics.py
│   │   │   │       └── __init__.py
│   │   │   ├── monitoring
│   │   │   │   ├── collectors
│   │   │   │   │   ├── checkers
│   │   │   │   │   │   ├── docker_utils.py
│   │   │   │   │   │   ├── game_service_checker.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── port_checker.py
│   │   │   │   │   │   └── web_service_checker.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── service_collector
│   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   ├── docker.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── security.py
│   │   │   │   │   │   └── services.py
│   │   │   │   │   ├── service_collector.py
│   │   │   │   │   ├── service_config
│   │   │   │   │   │   ├── game_services.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   └── web_services.py
│   │   │   │   │   ├── system_collector
│   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   ├── hardware
│   │   │   │   │   │   │   ├── cpu.py
│   │   │   │   │   │   │   ├── gpu.py
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── memory.py
│   │   │   │   │   │   │   ├── network.py
│   │   │   │   │   │   │   ├── power.py
│   │   │   │   │   │   │   ├── sensors.py
│   │   │   │   │   │   │   ├── speed_test.py
│   │   │   │   │   │   │   └── system.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── network.py
│   │   │   │   │   │   ├── storage.py
│   │   │   │   │   │   └── system.py
│   │   │   │   │   └── system_collector.py
│   │   │   │   ├── models
│   │   │   │   │   ├── alert.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── metric.py
│   │   │   │   ├── repositories
│   │   │   │   │   └── monitoring_repository.py
│   │   │   │   └── services
│   │   │   │       ├── alert_service.py
│   │   │   │       └── metric_service.py
│   │   │   ├── security
│   │   │   │   └── services
│   │   │   │       └── key_rotation_service.py
│   │   │   ├── tracker
│   │   │   │   └── services
│   │   │   │       └── project_service.py
│   │   │   └── wireguard
│   │   │       └── config_manager.py
│   │   ├── infrastructure
│   │   │   ├── config
│   │   │   │   ├── category_config.py
│   │   │   │   ├── channel_config.py
│   │   │   │   ├── command_config.py
│   │   │   │   ├── constants
│   │   │   │   │   ├── category_constants.py
│   │   │   │   │   ├── channel_constants.py
│   │   │   │   │   ├── dashboard_constants.py
│   │   │   │   │   ├── role_constants.py
│   │   │   │   │   └── user_groups.py
│   │   │   │   ├── dashboard_config.py
│   │   │   │   ├── env_config.py
│   │   │   │   ├── env_loader.py
│   │   │   │   ├── feature_flags.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service_config.py
│   │   │   │   ├── services
│   │   │   │   │   ├── critical_services_config.py
│   │   │   │   │   ├── dashboard_config.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── module_services_config.py
│   │   │   │   └── task_config.py
│   │   │   ├── database
│   │   │   │   ├── connection.py
│   │   │   │   ├── credentials.py
│   │   │   │   ├── migrations
│   │   │   │   │   ├── alembic.ini
│   │   │   │   │   ├── env.py
│   │   │   │   │   ├── init_db.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── init_variables.py
│   │   │   │   │   ├── README.md
│   │   │   │   │   ├── script.py.mako
│   │   │   │   │   ├── versions
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   └── v001_initial_schema.py
│   │   │   │   │   └── wait_for_postgres.py
│   │   │   │   ├── models
│   │   │   │   │   ├── audit_models.py
│   │   │   │   │   ├── auth_models.py
│   │   │   │   │   ├── base.py
│   │   │   │   │   ├── config.py
│   │   │   │   │   ├── dashboard_models.py
│   │   │   │   │   ├── discord_models.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── monitoring_models.py
│   │   │   │   │   └── project_models.py
│   │   │   │   └── repositories
│   │   │   │       ├── auditlog_repository.py
│   │   │   │       ├── category_repository.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── key_repository.py
│   │   │   │       ├── monitoring_repository_impl.py
│   │   │   │       ├── project_repository.py
│   │   │   │       ├── ratelimit_repository.py
│   │   │   │       ├── session_repository.py
│   │   │   │       ├── task_repository.py
│   │   │   │       └── user_repository.py
│   │   │   ├── discord
│   │   │   │   ├── category_setup_service.py
│   │   │   │   ├── channel_setup_service.py
│   │   │   │   ├── command_sync_service.py
│   │   │   │   ├── dashboard_setup_service.py
│   │   │   │   ├── game_server_channels.py
│   │   │   │   ├── role_mapper.py
│   │   │   │   └── setup_discord_channels.py
│   │   │   ├── encryption
│   │   │   │   ├── encryption_commands.py
│   │   │   │   ├── encryption_service.py
│   │   │   │   └── __init__.py
│   │   │   ├── factories
│   │   │   │   ├── base
│   │   │   │   │   ├── base_factory.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── composite
│   │   │   │   │   ├── bot_factory.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── discord
│   │   │   │   │   ├── channel_factory.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── thread_factory.py
│   │   │   │   ├── discord_ui
│   │   │   │   │   ├── button_factory.py
│   │   │   │   │   ├── dashboard_factory.py
│   │   │   │   │   ├── embed_factory.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── menu_factory.py
│   │   │   │   │   ├── message_factory.py
│   │   │   │   │   ├── modal_factory.py
│   │   │   │   │   └── view_factory.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── service
│   │   │   │       ├── __init__.py
│   │   │   │       ├── service_factory.py
│   │   │   │       ├── service_resolver.py
│   │   │   │       └── task_factory.py
│   │   │   ├── logging
│   │   │   │   ├── __init__.py
│   │   │   │   ├── logger.py
│   │   │   │   └── logging_service.py
│   │   │   ├── managers
│   │   │   │   └── dashboard_manager.py
│   │   │   ├── rate_limiting
│   │   │   │   ├── __init__.py
│   │   │   │   ├── rate_limiting_middleware.py
│   │   │   │   └── rate_limiting_service.py
│   │   │   └── security
│   │   │       └── key_management
│   │   │           └── key_manager.py
│   │   ├── __init__.py
│   │   ├── interfaces
│   │   │   ├── commands
│   │   │   │   ├── auth
│   │   │   │   │   ├── auth_commands.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── monitoring
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── system_monitoring_commands.py
│   │   │   │   ├── tracker
│   │   │   │   │   └── project_commands.py
│   │   │   │   ├── utils
│   │   │   │   │   └── clean
│   │   │   │   │       └── cleanup_commands.py
│   │   │   │   └── wireguard
│   │   │   │       ├── config_commands.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── qr_commands.py
│   │   │   │       ├── README.md
│   │   │   │       └── utils.py
│   │   │   ├── dashboards
│   │   │   │   ├── components
│   │   │   │   │   ├── channels
│   │   │   │   │   │   ├── gamehub
│   │   │   │   │   │   │   ├── buttons
│   │   │   │   │   │   │   │   ├── game_server_button.py
│   │   │   │   │   │   │   │   └── __init__.py
│   │   │   │   │   │   │   └── views
│   │   │   │   │   │   │       ├── gameserver_view.py
│   │   │   │   │   │   │       └── __init__.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── monitoring
│   │   │   │   │   │   │   ├── buttons
│   │   │   │   │   │   │   │   └── __init__.py
│   │   │   │   │   │   │   ├── embeds
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   └── monitoring_embed.py
│   │   │   │   │   │   │   └── views
│   │   │   │   │   │   │       ├── __init__.py
│   │   │   │   │   │   │       └── monitoring_view.py
│   │   │   │   │   │   ├── projects
│   │   │   │   │   │   │   ├── buttons
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── project_buttons.py
│   │   │   │   │   │   │   │   └── project_task_buttons.py
│   │   │   │   │   │   │   ├── embeds
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── project_embed.py
│   │   │   │   │   │   │   │   └── status_embed.py
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── modals
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── project_modal.py
│   │   │   │   │   │   │   │   └── project_task_modal.py
│   │   │   │   │   │   │   ├── selectors
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── priority_selector.py
│   │   │   │   │   │   │   │   └── status_selector.py
│   │   │   │   │   │   │   └── views
│   │   │   │   │   │   │       ├── __init__.py
│   │   │   │   │   │   │       ├── project_dashboard_view.py
│   │   │   │   │   │   │       ├── project_details_view.py
│   │   │   │   │   │   │       ├── project_task_list_view.py
│   │   │   │   │   │   │       ├── project_thread_view.py
│   │   │   │   │   │   │       └── status_select_view.py
│   │   │   │   │   │   └── welcome
│   │   │   │   │   │       ├── buttons
│   │   │   │   │   │       │   ├── bot_info_buttons.py
│   │   │   │   │   │       │   ├── __init__.py
│   │   │   │   │   │       │   └── welcome_buttons.py
│   │   │   │   │   │       ├── embeds
│   │   │   │   │   │       │   ├── __init__.py
│   │   │   │   │   │       │   └── welcome_embed.py
│   │   │   │   │   │       ├── modals
│   │   │   │   │   │       │   └── __init__.py
│   │   │   │   │   │       ├── selectors
│   │   │   │   │   │       │   ├── __init__.py
│   │   │   │   │   │       │   └── tech_selector.py
│   │   │   │   │   │       └── views
│   │   │   │   │   │           ├── bot_info_view.py
│   │   │   │   │   │           ├── __init__.py
│   │   │   │   │   │           └── welcome_view.py
│   │   │   │   │   ├── common
│   │   │   │   │   │   ├── buttons
│   │   │   │   │   │   │   ├── base_button.py
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   └── refresh_button.py
│   │   │   │   │   │   ├── embeds
│   │   │   │   │   │   │   ├── base_embed.py
│   │   │   │   │   │   │   ├── error_embed.py
│   │   │   │   │   │   │   └── __init__.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── modals
│   │   │   │   │   │   │   ├── base_modal.py
│   │   │   │   │   │   │   └── __init__.py
│   │   │   │   │   │   ├── selectors
│   │   │   │   │   │   │   ├── base_selector.py
│   │   │   │   │   │   │   └── __init__.py
│   │   │   │   │   │   ├── ui
│   │   │   │   │   │   │   ├── mini_graph.py
│   │   │   │   │   │   │   └── table_builder.py
│   │   │   │   │   │   └── views
│   │   │   │   │   │       ├── base_view.py
│   │   │   │   │   │       ├── confirmation_view.py
│   │   │   │   │   │       ├── dashboard_view.py
│   │   │   │   │   │       └── __init__.py
│   │   │   │   │   ├── factories
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   └── ui_component_factory.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── ui
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       ├── mini_graph.py
│   │   │   │   │       └── table_builder.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── ui
│   │   │   │       ├── base_dashboard.py
│   │   │   │       ├── gamehub_dashboard.py
│   │   │   │       ├── infrastructure.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── minecraft_server_dashboard.py
│   │   │   │       ├── monitoring_dashboard.py
│   │   │   │       ├── project_dashboard.py
│   │   │   │       └── welcome_dashboard.py
│   │   │   └── homelab_commands.py
│   │   ├── logs
│   │   │   └── homelab_bot.log
│   │   ├── modules
│   │   │   ├── docker
│   │   │   │   ├── commands
│   │   │   │   └── utils
│   │   │   ├── __init__.py
│   │   │   ├── monitoring
│   │   │   │   ├── commands
│   │   │   │   └── utils
│   │   │   ├── security
│   │   │   │   ├── cogs
│   │   │   │   │   └── security_cog.py
│   │   │   │   ├── commands
│   │   │   │   ├── __init__.py
│   │   │   │   └── utils
│   │   │   └── tracker
│   │   │       ├── commands
│   │   │       ├── __init__.py
│   │   │       ├── ip_management.py
│   │   │       ├── project_tracker.py
│   │   │       └── utils
│   │   ├── requirements.txt
│   │   ├── services
│   │   │   └── auth
│   │   │       ├── authentication_service.py
│   │   │       ├── authorization_service.py
│   │   │       ├── auth_service.py
│   │   │       └── __init__.py
│   │   └── utils
│   │       ├── decorators
│   │       │   ├── auth.py
│   │       │   └── respond.py
│   │       ├── formatters
│   │       │   ├── chunk_manager.py
│   │       │   └── response_mode.py
│   │       ├── http_client.py
│   │       ├── message_sender.py
│   │       └── vars.py
│   └── postgres
│       ├── pg_hba.conf
│       └── postgresql.conf
├── compose
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── init-db.sh
├── DISCLAIMER.md
├── docs
│   ├── core
│   │   ├── ARCHITECTURE.md
│   │   ├── CONVENTIONS.md
│   │   ├── KEYMANAGER.md
│   │   ├── PROTOCOL.md
│   │   ├── SECURITY_POLICY.md
│   │   └── VARIABLES.md
│   ├── development
│   │   ├── context
│   │   │   ├── COMMUNICATION.md
│   │   │   └── TREE.md
│   │   ├── patterns
│   │   │   ├── DASHBOARD_PATTERN.md
│   │   │   ├── DESIGN_PATTERN.md
│   │   │   └── SLASHCOMMAND_PATTERN.md
│   │   ├── roles
│   │   │   ├── BOT_FRAMEWORK_DEVELOPER.md
│   │   │   ├── SECURITY_SPECIALIST.md
│   │   │   ├── SLASH_COMMAND_DEVELOPER.py
│   │   │   ├── SYSTEM_MONITORING_DEVELOPER.py
│   │   │   └── UI_UX_DESIGNER.py
│   │   └── template
│   │       └── ROLE_DEFINITION.md
│   ├── planning
│   │   ├── ACTION_PLAN.md
│   │   ├── MILESTONES.md
│   │   └── ROADMAP.md
│   └── README.md
├── README.md
└── utils
    ├── database
    │   └── category_v002.sh
    ├── python-shell.nix
    ├── test_server.py
    ├── test_server.sh
    ├── update_alembic_migration.sh
    ├── update_remote_database.sh
    └── update_remote_docker.sh

136 directories, 310 files
 fr4iser@WorkStation  ~/Documents/Git/NCC-DiscordBot   main ±  