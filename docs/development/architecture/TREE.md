# Project Structure

```
app
├── bot
│   ├── application
│   │   ├── services
│   │   │   ├── category
│   │   │   │   ├── category_builder.py
│   │   │   │   └── category_setup_service.py
│   │   │   ├── category_setup
│   │   │   │   └── category_setup_service.py
│   │   │   ├── channel
│   │   │   │   ├── channel_builder.py
│   │   │   │   ├── channel_factory.py
│   │   │   │   ├── channel_setup_service.py
│   │   │   │   └── game_server_channel_service.py
│   │   │   ├── channel_setup
│   │   │   │   └── channel_setup_service.py
│   │   │   ├── cleanup
│   │   │   ├── dashboard
│   │   │   │   ├── component_loader_service.py
│   │   │   │   ├── dashboard_builder.py
│   │   │   │   ├── dashboard_builder_service.py
│   │   │   │   ├── dashboard_lifecycle_service.py
│   │   │   │   ├── dashboard_repository.py
│   │   │   │   ├── dashboard_service.py
│   │   │   │   └── __init__.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── __init__.py
│   │   │   ├── monitoring
│   │   │   │   └── system_monitoring.py
│   │   │   ├── OLD
│   │   │   │   └── OLD?.py
│   │   │   ├── system_metrics
│   │   │   │   └── system_metrics_service.py
│   │   │   └── wireguard
│   │   │       ├── __init__.py
│   │   │       └── wireguard_service.py
│   │   └── tasks
│   │       ├── cleanup_dm_task.py
│   │       ├── cleanup_task.py
│   │       └── security_tasks.py
│   ├── commands
│   │   └── dashboard
│   │       └── dashboard_command.py
│   ├── config
│   ├── core
│   │   ├── bot.py
│   │   ├── extensions.py
│   │   ├── __init__.py
│   │   ├── lifecycle
│   │   │   └── lifecycle_manager.py
│   │   ├── main.py
│   │   ├── shutdown_handler.py
│   │   └── workflows
│   │       ├── base_workflow.py
│   │       ├── category_workflow.py
│   │       ├── channel_workflow.py
│   │       ├── dashboard_workflow.py
│   │       ├── database_workflow.py
│   │       ├── service_workflow.py
│   │       ├── slash_commands_workflow.py
│   │       ├── task_workflow.py
│   │       └── webinterface_workflow.py
│   ├── database
│   │   └── wireguard
│   ├── dev
│   │   ├── dev_server.py
│   │   └── reload_commands.py
│   ├── domain
│   │   ├── auth
│   │   ├── categories
│   │   │   ├── models
│   │   │   │   └── category_model.py
│   │   │   └── repositories
│   │   │       └── category_repository.py
│   │   ├── channels
│   │   │   ├── factories
│   │   │   ├── models
│   │   │   │   └── channel_model.py
│   │   │   └── repositories
│   │   │       └── channel_repository.py
│   │   ├── dashboards
│   │   │   ├── models
│   │   │   │   ├── component_model.py
│   │   │   │   ├── dashboard_model.py
│   │   │   │   ├── data_source_model.py
│   │   │   │   └── orm_models.py
│   │   │   └── repositories
│   │   │       ├── dashboard_repository_impl.py
│   │   │       └── dashboard_repository.py
│   │   ├── gameservers
│   │   │   ├── collectors
│   │   │   │   └── __init__.py
│   │   │   ├── factories
│   │   │   ├── models
│   │   │   │   ├── gameserver_metrics.py
│   │   │   │   └── __init__.py
│   │   │   ├── repositories
│   │   │   └── services
│   │   ├── monitoring
│   │   │   ├── collectors
│   │   │   │   ├── __init__.py
│   │   │   │   └── interfaces
│   │   │   │       ├── collector_interface.py
│   │   │   │       ├── __init__.py
│   │   │   │       ├── service_collector_interface.py
│   │   │   │       └── system_collector_interface.py
│   │   │   ├── factories
│   │   │   │   └── collector_factory.py
│   │   │   ├── models
│   │   │   │   ├── alert.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── metric.py
│   │   │   ├── repositories
│   │   │   │   └── monitoring_repository.py
│   │   │   └── services
│   │   │       ├── alert_service.py
│   │   │       └── metric_service.py
│   │   ├── security
│   │   │   └── services
│   │   │       └── key_rotation_service.py
│   │   ├── tracker
│   │   │   └── services
│   │   │       └── project_service.py
│   │   └── wireguard
│   │       └── config_manager.py
│   ├── infrastructure
│   │   ├── config
│   │   │   ├── category_config.py
│   │   │   ├── channel_config.py
│   │   │   ├── command_config.py
│   │   │   ├── constants
│   │   │   │   ├── category_constants.py
│   │   │   │   ├── channel_constants.py
│   │   │   │   ├── dashboard_constants.py
│   │   │   │   ├── role_constants.py
│   │   │   │   └── user_config.py
│   │   │   ├── dashboard_config.py
│   │   │   ├── feature_flags.py
│   │   │   ├── __init__.py
│   │   │   ├── service_config.py
│   │   │   ├── services
│   │   │   │   └── dashboard_config.py
│   │   │   └── task_config.py
│   │   ├── dashboards
│   │   │   ├── dashboard_registry.py
│   │   │   └── __init__.py
│   │   ├── database
│   │   │   ├── migrations
│   │   │   └── models
│   │   │       ├── category_entity.py
│   │   │       └── channel_entity.py
│   │   ├── data_sources
│   │   │   └── system_metrics_source.py
│   │   ├── discord
│   │   │   ├── category_setup_service.py
│   │   │   ├── channel_setup_service.py
│   │   │   ├── command_sync_service.py
│   │   │   ├── dashboard_setup_service.py
│   │   │   ├── game_server_channels.py
│   │   │   ├── role_mapper.py
│   │   │   └── setup_discord_channels.py
│   │   ├── factories
│   │   │   ├── base
│   │   │   │   ├── base_factory.py
│   │   │   │   └── __init__.py
│   │   │   ├── component_factory.py
│   │   │   ├── component_registry_factory.py
│   │   │   ├── component_registry.py
│   │   │   ├── composite
│   │   │   │   ├── bot_factory.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service_factory.py
│   │   │   │   └── workflow_factory.py
│   │   │   ├── data_source_registry_factory.py
│   │   │   ├── data_source_registry.py
│   │   │   ├── discord
│   │   │   │   ├── channel_factory.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── thread_factory.py
│   │   │   ├── __init__.py
│   │   │   ├── service
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service_factory.py
│   │   │   │   ├── service_resolver.py
│   │   │   │   └── task_factory.py
│   │   │   ├── service_factory.py
│   │   │   └── task_factory.py
│   │   ├── __init__.py
│   │   ├── managers
│   │   │   └── dashboard_manager.py
│   │   ├── monitoring
│   │   │   ├── checkers
│   │   │   │   ├── docker_utils.py
│   │   │   │   ├── game_service_checker.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── port_checker.py
│   │   │   │   └── web_service_checker.py
│   │   │   ├── collectors
│   │   │   │   ├── game_servers
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── minecraft_server_collector_impl.py
│   │   │   │   ├── service
│   │   │   │   │   ├── components
│   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   ├── docker.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── security.py
│   │   │   │   │   │   └── services.py
│   │   │   │   │   ├── config
│   │   │   │   │   │   ├── game_services.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   └── web_services.py
│   │   │   │   │   ├── impl.py
│   │   │   │   │   └── __init__.py
│   │   │   │   └── system
│   │   │   │       ├── components
│   │   │   │       │   ├── base.py
│   │   │   │       │   ├── hardware
│   │   │   │       │   │   ├── cpu.py
│   │   │   │       │   │   ├── gpu.py
│   │   │   │       │   │   ├── __init__.py
│   │   │   │       │   │   ├── memory.py
│   │   │   │       │   │   ├── network.py
│   │   │   │       │   │   ├── power.py
│   │   │   │       │   │   ├── sensors.py
│   │   │   │       │   │   ├── speed_test.py
│   │   │   │       │   │   └── system.py
│   │   │   │       │   ├── __init__.py
│   │   │   │       │   ├── network.py
│   │   │   │       │   ├── storage.py
│   │   │   │       │   └── system.py
│   │   │   │       ├── impl.py
│   │   │   │       └── __init__.py
│   │   │   └── __init__.py
│   │   ├── rate_limiting
│   │   │   ├── __init__.py
│   │   │   ├── rate_limiting_middleware.py
│   │   │   └── rate_limiting_service.py
│   │   ├── repositories
│   │   │   ├── category_repository_impl.py
│   │   │   ├── channel_repository_impl.py
│   │   │   └── dashboard_repository_impl.py
│   │   ├── security
│   │   │   └── encryption
│   │   └── web
│   │       ├── auth_middleware.py
│   │       ├── routes.py
│   │       └── server.py
│   ├── __init__.py
│   ├── interfaces
│   │   ├── bot.py
│   │   ├── channels
│   │   │   └── __init__.py
│   │   ├── commands
│   │   │   ├── admin
│   │   │   ├── auth
│   │   │   │   ├── auth_commands.py
│   │   │   │   └── __init__.py
│   │   │   ├── gameserver
│   │   │   ├── monitoring
│   │   │   │   ├── __init__.py
│   │   │   │   └── system_monitoring_commands.py
│   │   │   ├── tracker
│   │   │   │   └── project_commands.py
│   │   │   ├── utils
│   │   │   │   └── clean
│   │   │   │       └── cleanup_commands.py
│   │   │   └── wireguard
│   │   │       ├── config_commands.py
│   │   │       ├── __init__.py
│   │   │       ├── qr_commands.py
│   │   │       ├── README.md
│   │   │       └── utils.py
│   │   ├── dashboards
│   │   │   ├── components
│   │   │   │   ├── base_component.py
│   │   │   │   ├── channels.py
│   │   │   │   ├── common
│   │   │   │   │   ├── buttons
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   └── refresh_button.py
│   │   │   │   │   └── embeds
│   │   │   │   │       ├── dashboard_embed.py
│   │   │   │   │       ├── error_embed.py
│   │   │   │   │       └── __init__.py
│   │   │   │   ├── factories
│   │   │   │   │   ├── base_dashboard_factory.py
│   │   │   │   │   ├── base_factory.py
│   │   │   │   │   ├── button_factory.py
│   │   │   │   │   ├── dashboard_factory.py
│   │   │   │   │   ├── embed_factory.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── menu_factory.py
│   │   │   │   │   ├── message_factory.py
│   │   │   │   │   ├── modal_factory.py
│   │   │   │   │   ├── new_factory.py
│   │   │   │   │   ├── ui_component_factory.py
│   │   │   │   │   └── view_factory.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── ui
│   │   │   │       ├── __init__.py
│   │   │   │       ├── mini_graph.py
│   │   │   │       └── table_builder.py
│   │   │   ├── controller
│   │   │   │   ├── base_dashboard.py
│   │   │   │   ├── dynamic_dashboard.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── template_dashboard.py
│   │   │   │   └── universal_dashboard.py
│   │   │   └── __init__.py
│   │   └── web
│   │       ├── api.py
│   │       ├── __init__.py
│   │       ├── server.py
│   │       └── ui.py
│   ├── main.py
│   ├── modules
│   │   ├── __init__.py
│   │   ├── security
│   │   │   ├── cogs
│   │   │   │   └── security_cog.py
│   │   │   └── __init__.py
│   │   └── tracker
│   │       ├── __init__.py
│   │       ├── ip_management.py
│   │       └── project_tracker.py
│   ├── requirements.txt
│   ├── services
│   │   └── auth
│   │       ├── authentication_service.py
│   │       ├── authorization_service.py
│   │       └── __init__.py
│   └── utils
│       ├── decorators
│       │   ├── auth.py
│       │   └── respond.py
│       ├── formatters
│       │   ├── chunk_manager.py
│       │   └── response_mode.py
│       ├── http_client.py
│       ├── message_sender.py
│       ├── validators
│       └── vars.py
├── logs
├── postgres
│   ├── pg_hba.conf
│   └── postgresql.conf
├── shared
│   ├── application
│   │   ├── logging
│   │   │   ├── formatters.py
│   │   │   └── log_config.py
│   │   └── tasks
│   │       └── schedule_key_rotation.py
│   ├── config
│   │   └── default_config.py
│   ├── domain
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── permission.py
│   │   │   │   ├── role.py
│   │   │   │   └── user.py
│   │   │   ├── policies
│   │   │   │   ├── authorization_policies.py
│   │   │   │   └── __init__.py
│   │   │   ├── repositories
│   │   │   │   └── user_repository.py
│   │   │   └── services
│   │   │       ├── authentication_service.py
│   │   │       ├── authorization_service.py
│   │   │       ├── __init__.py
│   │   │       └── permission_service.py
│   │   ├── logging
│   │   │   ├── entities
│   │   │   │   ├── __init__.py
│   │   │   │   └── log_entry.py
│   │   │   ├── repositories
│   │   │   │   ├── __init__.py
│   │   │   │   └── log_repository.py
│   │   │   └── services
│   │   │       ├── __init__.py
│   │   │       └── logging_service.py
│   │   └── services
│   │       └── __init__.py
│   ├── infrastructure
│   │   ├── config
│   │   │   ├── env_config.py
│   │   │   ├── env_loader.py
│   │   │   ├── env_manager.py
│   │   │   └── __init__.py
│   │   ├── database
│   │   │   ├── api.py
│   │   │   ├── config
│   │   │   │   └── user_config.py
│   │   │   ├── constants
│   │   │   │   ├── category_constants.py
│   │   │   │   ├── channel_constants.py
│   │   │   │   ├── dashboard_constants.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── role_constants.py
│   │   │   │   └── user_constants.py
│   │   │   ├── core
│   │   │   │   ├── config.py
│   │   │   │   ├── connection.py
│   │   │   │   ├── credentials.py
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── migrations
│   │   │   │   ├── alembic.ini
│   │   │   │   ├── categories
│   │   │   │   │   └── seed_categories.py
│   │   │   │   ├── channels
│   │   │   │   │   └── seed_channels.py
│   │   │   │   ├── dashboards
│   │   │   │   │   ├── common
│   │   │   │   │   │   ├── buttons.py
│   │   │   │   │   │   ├── embeds.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── messages.py
│   │   │   │   │   │   ├── modals.py
│   │   │   │   │   │   ├── selectors.py
│   │   │   │   │   │   └── views.py
│   │   │   │   │   ├── dashboard_components_migration.py
│   │   │   │   │   ├── gamehub
│   │   │   │   │   │   ├── buttons.py
│   │   │   │   │   │   ├── embeds.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── messages.py
│   │   │   │   │   │   ├── modals.py
│   │   │   │   │   │   ├── selectors.py
│   │   │   │   │   │   └── views.py
│   │   │   │   │   ├── monitoring
│   │   │   │   │   │   ├── buttons.py
│   │   │   │   │   │   ├── embeds.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── messages.py
│   │   │   │   │   │   ├── modals.py
│   │   │   │   │   │   ├── selectors.py
│   │   │   │   │   │   └── views.py
│   │   │   │   │   ├── project
│   │   │   │   │   │   ├── buttons.py
│   │   │   │   │   │   ├── embeds.py
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── messages.py
│   │   │   │   │   │   ├── modals.py
│   │   │   │   │   │   ├── selectors.py
│   │   │   │   │   │   └── views.py
│   │   │   │   │   └── welcome
│   │   │   │   │       ├── buttons.py
│   │   │   │   │       ├── embeds.py
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       ├── messages.py
│   │   │   │   │       ├── modals.py
│   │   │   │   │       ├── selectors.py
│   │   │   │   │       └── views.py
│   │   │   │   ├── env.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── init_variables.py
│   │   │   │   ├── README.md
│   │   │   │   ├── script.py.mako
│   │   │   │   ├── versions
│   │   │   │   │   ├── 20230501_create_dashboards_table.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── v001_initial_schema.py
│   │   │   │   └── wait_for_postgres.py
│   │   │   ├── models
│   │   │   │   ├── auth
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── rate_limit.py
│   │   │   │   │   ├── session.py
│   │   │   │   │   └── user.py
│   │   │   │   ├── base.py
│   │   │   │   ├── core
│   │   │   │   │   ├── audit_log.py
│   │   │   │   │   ├── config.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── log_entry.py
│   │   │   │   ├── dashboards
│   │   │   │   │   ├── component_layout.py
│   │   │   │   │   ├── content_template.py
│   │   │   │   │   ├── dashboard_component.py
│   │   │   │   │   ├── dashboard_message.py
│   │   │   │   │   ├── dashboard.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── discord
│   │   │   │   │   ├── auto_thread_channel.py
│   │   │   │   │   ├── category_mapping.py
│   │   │   │   │   ├── channel_mapping.py
│   │   │   │   │   ├── guild.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── message.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── monitoring
│   │   │   │   │   ├── alert.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── metric.py
│   │   │   │   └── project
│   │   │   │       ├── __init__.py
│   │   │   │       ├── project.py
│   │   │   │       ├── tables.py
│   │   │   │       └── task.py
│   │   │   ├── repositories
│   │   │   │   ├── auditlog_repository_impl.py
│   │   │   │   ├── category_repository_impl.py
│   │   │   │   ├── dashboard_repository_impl.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── key_repository_impl.py
│   │   │   │   ├── monitoring_repository_impl.py
│   │   │   │   ├── new_dashboard_repository_impl.py
│   │   │   │   ├── project_repository_impl.py
│   │   │   │   ├── ratelimit_repository_impl.py
│   │   │   │   ├── session_repository_impl.py
│   │   │   │   ├── task_repository_impl.py
│   │   │   │   └── user_repository_impl.py
│   │   │   └── session
│   │   │       ├── context.py
│   │   │       ├── factory.py
│   │   │       └── __init__.py
│   │   ├── docker
│   │   │   ├── entrypoint.py
│   │   │   ├── __init__.py
│   │   │   └── test_entrypoint.py
│   │   ├── encryption
│   │   │   ├── encryption_commands.py
│   │   │   ├── encryption_service.py
│   │   │   ├── __init__.py
│   │   │   └── key_management_service.py
│   │   ├── __init__.py
│   │   ├── logging
│   │   │   ├── handlers
│   │   │   │   ├── db_handler.py
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── repositories
│   │   │   │   ├── __init__.py
│   │   │   │   └── log_repository_impl.py
│   │   │   └── services
│   │   │       ├── base_logging_service.py
│   │   │       ├── bot_logging_service.py
│   │   │       ├── __init__.py
│   │   │       └── web_logging_service.py
│   │   └── security
│   │       ├── __init__.py
│   │       └── security_bootstrapper.py
│   ├── __init__.py
│   └── interface
│       ├── __init__.py
│       └── logging
│           ├── api.py
│           ├── factories.py
│           └── __init__.py
├── tests
│   ├── conftest.py
│   ├── functional
│   │   ├── __init__.py
│   │   └── test_user_flow.py
│   ├── __init__.py
│   ├── integration
│   │   ├── caching
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── test_caching.py
│   │   └── web
│   │       └── __init__.py
│   ├── performance
│   │   ├── __init__.py
│   │   └── test_response_times.py
│   ├── pytest.ini
│   ├── README.md
│   ├── test-results
│   ├── unit
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   └── test_auth.py
│   │   ├── commands
│   │   │   ├── __init__.py
│   │   │   └── test_commands.py
│   │   ├── dashboard
│   │   │   ├── __init__.py
│   │   │   ├── test_dashboard_lifecycle.py
│   │   │   ├── test_dashboard.py
│   │   │   ├── test_dashboard_simple.py
│   │   │   └── test_dynamic_dashboard_creation.py
│   │   ├── infrastructure
│   │   │   ├── __init__.py
│   │   │   └── test_structure.py
│   │   ├── __init__.py
│   │   └── web
│   │       ├── __init__.py
│   │       └── test_web_auth.py
│   └── utils.py
└── web
    ├── api
    │   ├── dashboard.py
    │   └── __init__.py
    ├── application
    │   ├── __init__.py
    │   ├── services
    │   │   ├── auth
    │   │   │   ├── dependencies.py
    │   │   │   └── __init__.py
    │   │   ├── dashboard
    │   │   │   ├── dashboard_service.py
    │   │   │   └── __init__.py
    │   │   ├── __init__.py
    │   │   └── monitoring
    │   │       └── __init__.py
    │   └── tasks
    │       └── __init__.py
    ├── core
    │   ├── extensions.py
    │   ├── __init__.py
    │   ├── main.py
    │   ├── middleware.py
    │   └── workflows
    │       └── __init__.py
    ├── domain
    │   ├── auth
    │   │   ├── dependencies.py
    │   │   ├── __init__.py
    │   │   ├── models
    │   │   │   └── __init__.py
    │   │   ├── oauth.py
    │   │   ├── permissions.py
    │   │   ├── policies
    │   │   │   └── __init__.py
    │   │   └── repositories
    │   │       └── __init__.py
    │   ├── bot_config
    │   ├── channel_management
    │   ├── dashboard_builder
    │   │   ├── __init__.py
    │   │   ├── models
    │   │   │   ├── dashboard.py
    │   │   │   └── __init__.py
    │   │   └── repositories
    │   │       ├── dashboard_repository.py
    │   │       └── __init__.py
    │   ├── __init__.py
    │   └── monitoring_discordbot
    │       └── __init__.py
    ├── infrastructure
    │   ├── config
    │   │   ├── env_loader.py
    │   │   └── __init__.py
    │   ├── database
    │   │   ├── __init__.py
    │   │   ├── migrations
    │   │   │   └── __init__.py
    │   │   ├── models
    │   │   │   ├── dashboard.py
    │   │   │   └── __init__.py
    │   │   └── repositories
    │   │       ├── dashboard_repository.py
    │   │       └── __init__.py
    │   ├── __init__.py
    │   ├── logging
    │   │   └── __init__.py
    │   ├── security
    │   │   ├── auth.py
    │   │   └── __init__.py
    │   └── setup
    │       ├── bot_imports.py
    │       ├── __init__.py
    │       ├── init.py
    │       ├── init_web.py
    │       ├── main_check.py
    │       └── setup_app_package.py
    ├── __init__.py
    ├── interfaces
    │   ├── api
    │   │   ├── __init__.py
    │   │   ├── routes.py
    │   │   └── v1
    │   │       ├── auth.py
    │   │       ├── dashboard.py
    │   │       ├── health_routes.py
    │   │       └── __init__.py
    │   ├── __init__.py
    │   └── web
    │       ├── __init__.py
    │       ├── pages
    │       │   ├── api_endpoints.py
    │       │   ├── bot_configurator.py
    │       │   ├── channel_manager.py
    │       │   ├── dashboard_builder.py
    │       │   ├── dashboard_preview.py
    │       │   ├── footer.py
    │       │   ├── header.py
    │       │   ├── __init__.py
    │       │   ├── mainframe.py
    │       │   ├── role_management.py
    │       │   ├── sidebar.py
    │       │   ├── tools.py
    │       │   └── workflow_builder.py
    │       ├── routes.py
    │       ├── static
    │       │   ├── css
    │       │   ├── __init__.py
    │       │   └── js
    │       │       ├── bot_configurator.js
    │       │       ├── dashboard_builder.js
    │       │       ├── mainframe.js
    │       │       ├── main.js
    │       │       ├── role_manager.js
    │       │       ├── sidebar.js
    │       │       └── tools.js
    │       └── templates
    │           ├── bot_configurator
    │           ├── channel_manager
    │           ├── dashboard_builder
    │           ├── discordbot_config
    │           ├── index
    │           ├── __init__.py
    │           └── login
    ├── requirements.txt
    ├── static
    │   ├── css
    │   │   ├── base.css
    │   │   └── themes
    │   │       ├── dark
    │   │       │   └── theme.css
    │   │       └── light
    │   └── js
    │       ├── main.js
    │       └── pages
    │           └── index.js
    └── templates
        ├── auth
        │   ├── insufficient_permissions.html
        │   └── login.html
        ├── base.html
        ├── components
        │   ├── footer.html
        │   ├── header.html
        │   ├── navbar.html
        │   └── sidebars
        │       ├── builder_sidebar.html
        │       ├── dashboard_sidebar.html
        │       └── toolbox_sidebar.html
        ├── dashboard
        │   ├── builder.html
        │   └── view.html
        ├── index.html
        └── layouts
            └── dashboard_layout.html
```