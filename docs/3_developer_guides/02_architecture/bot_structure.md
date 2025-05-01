```tree
bot
├── application
│   ├── decorators
│   │   ├── auth.py
│   │   └── respond.py
│   ├── process
│   │   ├── cleanup_dm_task.py
│   │   ├── cleanup_task.py
│   │   └── security_tasks.py
│   └── services
│       ├── auth
│       │   ├── __init__.py
│       │   └── OLD.py
│       ├── bot_control_service.py
│       ├── category
│       │   ├── category_builder.py
│       │   ├── category_setup_service.py
│       │   └── __init__.py
│       ├── channel
│       │   ├── channel_builder.py
│       │   ├── channel_factory.py
│       │   ├── channel_setup_service.py
│       │   ├── game_server_channel_service.py
│       │   └── __init__.py
│       ├── config
│       │   ├── config_service.py
│       │   └── __init__.py
│       ├── dashboard
│       │   ├── component_loader_service.py
│       │   ├── dashboard_builder.py
│       │   ├── dashboard_builder_service.py
│       │   ├── dashboard_lifecycle_service.py
│       │   ├── dashboard_repository.py
│       │   ├── dashboard_service.py
│       │   └── __init__.py
│       ├── discord
│       │   ├── discord_query_service.py
│       │   └── __init__.py
│       ├── __init__.py
│       ├── monitoring
│       │   └── system_monitoring.py
│       ├── project_management
│       │   ├── __init__.py
│       │   ├── project_service.py
│       │   └── task_service.py
│       ├── system_metrics
│       │   ├── __init__.py
│       │   └── system_metrics_service.py
│       └── wireguard
│           ├── __init__.py
│           └── wireguard_service.py
├── config
├── core
│   ├── checks.py
│   ├── extensions.py
│   ├── __init__.py
│   ├── lifecycle_manager.py
│   ├── main.py
│   ├── shutdown_handler.py
│   ├── workflow_manager.py
│   └── workflows
│       ├── base_workflow.py
│       ├── bot_permission_workflow.py
│       ├── category_workflow.py
│       ├── channel_workflow.py
│       ├── dashboard_workflow.py
│       ├── database_workflow.py
│       ├── guild
│       │   ├── approval.py
│       │   ├── check_structure.py
│       │   ├── initialization.py
│       │   ├── __init__.py
│       │   ├── state.py
│       │   ├── sync.py
│       │   └── template_application.py
│       ├── guild_template_workflow.py
│       ├── __init__.py
│       ├── overview_workflow.py
│       ├── service_manager.py
│       ├── service_workflow.py
│       ├── slash_commands_workflow.py
│       ├── task_workflow.py
│       ├── user_workflow.py
│       └── webinterface_workflow.py
├── database
│   └── wireguard
├── infrastructure
│   ├── component
│   │   ├── factory.py
│   │   ├── __init__.py
│   │   └── registry.py
│   ├── config
│   │   ├── category_config.py
│   │   ├── channel_config.py
│   │   ├── command_config.py
│   │   ├── constants
│   │   │   ├── category_constants.py
│   │   │   ├── channel_constants.py
│   │   │   ├── dashboard_constants.py
│   │   │   ├── role_constants.py
│   │   │   └── user_config.py
│   │   ├── dashboard_config.py
│   │   ├── feature_flags.py
│   │   ├── __init__.py
│   │   ├── service_config.py
│   │   ├── services
│   │   │   └── dashboard_config.py
│   │   └── task_config.py
│   ├── dashboards
│   │   ├── dashboard_registry.py
│   │   └── __init__.py
│   ├── data
│   │   ├── data_source_registry.py
│   │   └── __init__.py
│   ├── data_sources
│   │   └── system_metrics_source.py
│   ├── discord
│   │   ├── category_setup_service.py
│   │   ├── command_sync_service.py
│   │   ├── dashboard_setup_service.py
│   │   ├── game_server_channels.py
│   │   ├── role_mapper.py
│   │   └── setup_discord_channels.py
│   ├── factories
│   │   ├── base
│   │   │   ├── base_factory.py
│   │   │   └── __init__.py
│   │   ├── component_factory.py
│   │   ├── component_registry_factory.py
│   │   ├── component_registry.py
│   │   ├── composite
│   │   │   ├── bot_factory.py
│   │   │   ├── __init__.py
│   │   │   ├── service_factory.py
│   │   │   └── workflow_factory.py
│   │   ├── data_source_registry_factory.py
│   │   ├── data_source_registry.py
│   │   ├── discord
│   │   │   ├── channel_factory.py
│   │   │   ├── __init__.py
│   │   │   └── thread_factory.py
│   │   ├── __init__.py
│   │   ├── service
│   │   │   ├── __init__.py
│   │   │   ├── service_factory.py
│   │   │   ├── service_resolver.py
│   │   │   └── task_factory.py
│   │   ├── service_factory.py
│   │   └── task_factory.py
│   ├── __init__.py
│   ├── internal_api
│   │   ├── routes.py
│   │   └── server.py
│   ├── managers
│   │   └── dashboard_manager.py
│   ├── messaging
│   │   ├── chunk_manager.py
│   │   ├── http_client.py
│   │   ├── message_sender.py
│   │   └── response_mode.py
│   ├── monitoring
│   │   ├── checkers
│   │   │   ├── docker_utils.py
│   │   │   ├── game_service_checker.py
│   │   │   ├── __init__.py
│   │   │   ├── port_checker.py
│   │   │   └── web_service_checker.py
│   │   ├── collectors
│   │   │   ├── game_servers
│   │   │   │   ├── __init__.py
│   │   │   │   └── minecraft_server_collector_impl.py
│   │   │   ├── service
│   │   │   │   ├── components
│   │   │   │   │   ├── base.py
│   │   │   │   │   ├── docker.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── security.py
│   │   │   │   │   └── services.py
│   │   │   │   ├── config
│   │   │   │   │   ├── game_services.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── web_services.py
│   │   │   │   ├── impl.py
│   │   │   │   └── __init__.py
│   │   │   └── system
│   │   │       ├── components
│   │   │       │   ├── base.py
│   │   │       │   ├── hardware
│   │   │       │   │   ├── cpu.py
│   │   │       │   │   ├── gpu.py
│   │   │       │   │   ├── __init__.py
│   │   │       │   │   ├── memory.py
│   │   │       │   │   ├── network.py
│   │   │       │   │   ├── power.py
│   │   │       │   │   ├── sensors.py
│   │   │       │   │   ├── speed_test.py
│   │   │       │   │   └── system.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── network.py
│   │   │       │   ├── storage.py
│   │   │       │   └── system.py
│   │   │       ├── impl.py
│   │   │       └── __init__.py
│   │   └── __init__.py
│   ├── rate_limiting
│   │   ├── __init__.py
│   │   ├── rate_limiting_middleware.py
│   │   └── rate_limiting_service.py
│   └── state
│       ├── bot_state_collectors.py
│       └── collectors
│           ├── basic_info.py
│           ├── cog_status.py
│           ├── database_status.py
│           ├── discord_api.py
│           ├── listeners.py
│           └── performance.py
├── __init__.py
├── interfaces
│   ├── bot.py
│   ├── commands
│   │   ├── auth
│   │   │   ├── auth_commands.py
│   │   │   └── __init__.py
│   │   ├── dashboard
│   │   │   └── dashboard_command.py
│   │   ├── monitoring
│   │   │   ├── __init__.py
│   │   │   └── system_monitoring_commands.py
│   │   ├── tracker
│   │   │   └── project_commands.py
│   │   ├── utils
│   │   │   └── clean
│   │   │       └── cleanup_commands.py
│   │   └── wireguard
│   │       ├── config_commands.py
│   │       ├── __init__.py
│   │       ├── qr_commands.py
│   │       ├── README.md
│   │       └── utils.py
│   └── dashboards
│       ├── components
│       │   ├── base_component.py
│       │   ├── channels.py
│       │   ├── common
│       │   │   ├── buttons
│       │   │   │   ├── __init__.py
│       │   │   │   └── refresh_button.py
│       │   │   └── embeds
│       │   │       ├── dashboard_embed.py
│       │   │       ├── error_embed.py
│       │   │       └── __init__.py
│       │   ├── factories
│       │   │   ├── base_dashboard_factory.py
│       │   │   ├── base_factory.py
│       │   │   ├── button_factory.py
│       │   │   ├── dashboard_factory.py
│       │   │   ├── embed_factory.py
│       │   │   ├── __init__.py
│       │   │   ├── menu_factory.py
│       │   │   ├── message_factory.py
│       │   │   ├── modal_factory.py
│       │   │   ├── new_factory.py
│       │   │   ├── ui_component_factory.py
│       │   │   └── view_factory.py
│       │   ├── __init__.py
│       │   └── ui
│       │       ├── __init__.py
│       │       ├── mini_graph.py
│       │       └── table_builder.py
│       ├── controller
│       │   ├── base_dashboard.py
│       │   ├── dynamic_dashboard.py
│       │   ├── __init__.py
│       │   ├── template_dashboard.py
│       │   └── universal_dashboard.py
│       └── __init__.py
├── requirements.txt
├── state_collectors.py
└── utils
    └── vars.py
```