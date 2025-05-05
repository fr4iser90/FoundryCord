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
