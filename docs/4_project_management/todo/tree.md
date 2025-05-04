 fr4iser@Gaming  ~/Documents/Git/FoundryCord/app  ↱ main ±  tree bot 
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
│       │   ├── dashboard_data_service.py
│       │   ├── dashboard_lifecycle_service.py
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
│   ├── setup_hooks.py
│   ├── shutdown_handler.py
│   ├── workflow_manager.py
│   └── workflows
│       ├── base_workflow.py
│       ├── bot_permission_workflow.py
│       ├── category
│       ├── category_workflow.py
│       ├── channel
│       ├── channel_workflow.py
│       ├── dashboard
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
│       ├── guild_template
│       │   ├── check_structure.py
│       │   ├── initialization.py
│       │   ├── __init__.py
│       │   └── state.py
│       ├── guild_template_workflow.py
│       ├── __init__.py
│       ├── overview_workflow.py
│       ├── service_manager.py
│       ├── service_workflow.py
│       ├── slash_commands_workflow.py
│       ├── task_workflow.py
│       ├── user
│       ├── user_workflow.py
│       ├── webinterface
│       └── webinterface_workflow.py
├── database
│   └── wireguard
├── infrastructure
│   ├── component
│   │   ├── factory.py
│   │   ├── __init__.py
│   │   └── registry.py
│   ├── config
│   │   ├── command_config.py
│   │   ├── constants
│   │   │   ├── role_constants.py
│   │   │   └── user_config.py
│   │   ├── dashboard_config.py
│   │   ├── feature_flags.py
│   │   ├── __init__.py
│   │   ├── service_config.py
│   │   ├── services
│   │   └── task_config.py
│   ├── dashboards
│   │   ├── dashboard_registry.py
│   │   └── __init__.py
│   ├── data
│   │   ├── data_source_registry.py
│   │   └── __init__.py
│   ├── data_sources
│   │   ├── __init__.py
│   │   └── system_metrics_source.py
│   ├── discord
│   │   ├── command_sync_service.py
│   │   ├── game_server_channels.py
│   │   └── role_mapper.py
│   ├── factories
│   │   ├── base
│   │   │   ├── base_factory.py
│   │   │   └── __init__.py
│   │   ├── component_factory.py
│   │   ├── component_registry.py
│   │   ├── composite
│   │   │   ├── bot_factory.py
│   │   │   ├── __init__.py
│   │   │   └── workflow_factory.py
│   │   ├── data_source_registry.py
│   │   ├── discord
│   │   │   ├── channel_factory.py
│   │   │   ├── __init__.py
│   │   │   └── thread_factory.py
│   │   ├── __init__.py
│   │   ├── service
│   │   │   ├── __init__.py
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
│       │   ├── common
│       │   │   ├── buttons
│       │   │   │   ├── generic_button.py
│       │   │   │   ├── __init__.py
│       │   │   │   └── refresh_button.py
│       │   │   ├── embeds
│       │   │   │   ├── dashboard_embed.py
│       │   │   │   ├── error_embed.py
│       │   │   │   └── __init__.py
│       │   │   └── selectors
│       │   │       ├── generic_selector.py
│       │   │       └── __init__.py
│       │   ├── factories
│       │   │   ├── button_factory.py
│       │   │   ├── embed_factory.py
│       │   │   ├── __init__.py
│       │   │   ├── menu_factory.py
│       │   │   └── modal_factory.py
│       │   ├── __init__.py
│       │   └── ui
│       │       ├── __init__.py
│       │       ├── mini_graph.py
│       │       └── table_builder.py
│       ├── controller
│       │   ├── dashboard_controller.py
│       │   └── __init__.py
│       └── __init__.py
├── requirements.txt
├── state_collectors.py
└── utils
    └── vars.py

76 directories, 194 files


web
├── application
│   ├── dtos
│   ├── __init__.py
│   ├── services
│   │   ├── api
│   │   │   ├── api_service.py
│   │   │   └── __init__.py
│   │   ├── auth
│   │   │   └── __init__.py
│   │   ├── dashboards
│   │   │   ├── dashboard_component_service.py
│   │   │   ├── dashboard_configuration_service.py
│   │   │   └── __init__.py
│   │   ├── guild
│   │   │   ├── guild_service.py
│   │   │   ├── __init__.py
│   │   │   ├── management_service.py
│   │   │   ├── OLD.py
│   │   │   ├── query_service.py
│   │   │   └── selection_service.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   └── __init__.py
│   │   ├── security
│   │   │   └── __init__.py
│   │   ├── template
│   │   │   ├── __init__.py
│   │   │   ├── management_service.py
│   │   │   ├── OLD.py
│   │   │   ├── query_service.py
│   │   │   ├── sharing_service.py
│   │   │   ├── structure_service.py
│   │   │   └── template_service.py
│   │   └── ui
│   │       └── layout_service.py
│   └── tasks
│       └── __init__.py
├── core
│   ├── exception_handlers.py
│   ├── extensions
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── static.py
│   │   ├── templates.py
│   │   └── time.py
│   ├── __init__.py
│   ├── lifecycle_manager.py
│   ├── main.py
│   ├── middleware
│   │   ├── authentication.py
│   │   ├── __init__.py
│   │   └── request_tracking.py
│   ├── middleware_registry.py
│   ├── router_registry.py
│   ├── workflow_manager.py
│   └── workflows
│       ├── base_workflow.py
│       ├── __init__.py
│       └── service_workflow.py
├── infrastructure
│   ├── config
│   │   ├── env_loader.py
│   │   └── __init__.py
│   ├── database
│   │   └── __init__.py
│   ├── factories
│   │   ├── base
│   │   │   └── base_factory.py
│   │   ├── composite
│   │   │   └── web_factory.py
│   │   └── service
│   │       └── web_service_factory.py
│   ├── __init__.py
│   ├── logging
│   │   └── __init__.py
│   ├── security
│   │   ├── __init__.py
│   │   └── oauth.py
│   └── setup
│       ├── bot_imports.py
│       ├── __init__.py
│       ├── init.py
│       ├── init_web.py
│       └── main_check.py
├── __init__.py
├── interfaces
│   ├── api
│   │   ├── __init__.py
│   │   └── rest
│   │       ├── dependencies
│   │       │   ├── auth_dependencies.py
│   │       │   └── ui_dependencies.py
│   │       ├── README.md
│   │       ├── routes.py
│   │       └── v1
│   │           ├── auth
│   │           │   ├── auth_controller.py
│   │           │   └── __init__.py
│   │           ├── base_controller.py
│   │           ├── dashboards
│   │           │   ├── dashboard_component_controller.py
│   │           │   ├── dashboard_configuration_controller.py
│   │           │   ├── dashboard_controller.py
│   │           │   └── __init__.py
│   │           ├── debug
│   │           │   ├── debug_controller.py
│   │           │   └── __init__.py
│   │           ├── guild
│   │           │   ├── admin
│   │           │   │   ├── guild_config_controller.py
│   │           │   │   └── guild_user_management_controller.py
│   │           │   ├── designer
│   │           │   │   ├── guild_template_controller.py
│   │           │   │   ├── __init__.py
│   │           │   │   ├── lifecycle_controller.py
│   │           │   │   ├── metadata_controller.py
│   │           │   │   ├── OLD.py
│   │           │   │   └── structure_controller.py
│   │           │   ├── __init__.py
│   │           │   └── selector
│   │           │       └── guild_selector_controller.py
│   │           ├── home
│   │           │   ├── __init__.py
│   │           │   └── overview_controller.py
│   │           ├── __init__.py
│   │           ├── owner
│   │           │   ├── bot_control_controller.py
│   │           │   ├── bot_logger_controller.py
│   │           │   ├── guild_management_controller.py
│   │           │   ├── __init__.py
│   │           │   ├── owner_controller.py
│   │           │   └── state_snapshot_controller.py
│   │           ├── schemas
│   │           │   ├── dashboard_component_schemas.py
│   │           │   ├── dashboard_schemas.py
│   │           │   ├── guild_schemas.py
│   │           │   ├── guild_template_schemas.py
│   │           │   ├── state_monitor_schemas.py
│   │           │   └── ui_layout_schemas.py
│   │           ├── system
│   │           │   ├── health_controller.py
│   │           │   └── __init__.py
│   │           └── ui
│   │               ├── __init__.py
│   │               └── layout_controller.py
│   ├── __init__.py
│   └── web
│       ├── __init__.py
│       ├── routes.py
│       └── views
│           ├── auth
│           │   ├── auth_view.py
│           │   └── __init__.py
│           ├── base_view.py
│           ├── debug
│           │   ├── debug_view.py
│           │   └── __init__.py
│           ├── guild
│           │   ├── admin
│           │   │   ├── index_view.py
│           │   │   ├── __init__.py
│           │   │   ├── logs_view.py
│           │   │   ├── settings_view.py
│           │   │   └── users_view.py
│           │   ├── designer
│           │   │   ├── categories_view.py
│           │   │   ├── channels_view.py
│           │   │   ├── commands_view.py
│           │   │   ├── embeds_view.py
│           │   │   ├── index_view.py
│           │   │   └── __init__.py
│           │   └── __init__.py
│           ├── home
│           │   ├── __init__.py
│           │   └── overview.py
│           ├── __init__.py
│           ├── main
│           │   ├── __init__.py
│           │   └── main_view.py
│           ├── navbar
│           │   ├── guild_selector_view.py
│           │   └── __init__.py
│           └── owner
│               ├── bot_control_view.py
│               ├── bot_logger_view.py
│               ├── control_view.py
│               ├── features_view.py
│               ├── guild_management_view.py
│               ├── __init__.py
│               └── state_monitor_view.py
├── requirements.txt
├── static
│   ├── css
│   │   ├── components
│   │   │   ├── alerts.css
│   │   │   ├── badges.css
│   │   │   ├── buttons.css
│   │   │   ├── cards.css
│   │   │   ├── forms.css
│   │   │   ├── guild-selector.css
│   │   │   ├── index.css
│   │   │   ├── json-viewer.css
│   │   │   ├── modal.css
│   │   │   ├── navbar.css
│   │   │   ├── panels.css
│   │   │   ├── stats.css
│   │   │   ├── table.css
│   │   │   └── widgets.css
│   │   ├── core
│   │   │   ├── base.css
│   │   │   ├── layout.css
│   │   │   ├── reset.css
│   │   │   └── utilities.css
│   │   ├── themes
│   │   │   ├── dark.css
│   │   │   ├── dark_green.css
│   │   │   ├── light.css
│   │   │   ├── light_green.css
│   │   │   └── light_red.css
│   │   └── views
│   │       ├── admin
│   │       │   └── system_status.css
│   │       ├── auth
│   │       │   └── login.css
│   │       ├── dashboard
│   │       │   └── overview.css
│   │       ├── guild
│   │       │   └── designer.css
│   │       └── owner
│   │           ├── bot_logger.css
│   │           ├── control.css
│   │           └── state-monitor.css
│   └── js
│       ├── components
│       │   ├── common
│       │   │   ├── dateTimeUtils.js
│       │   │   ├── index.js
│       │   │   ├── navbar.js
│       │   │   ├── notifications.js
│       │   │   ├── serversWidget.js
│       │   │   └── status_widget.js
│       │   ├── forms
│       │   ├── guildSelector.js
│       │   ├── jsonViewer.js
│       │   ├── layout
│       │   │   └── gridManager.js
│       │   ├── modalComponent.js
│       │   └── navigation
│       ├── core
│       │   ├── main.js
│       │   ├── state-bridge
│       │   │   ├── bridgeApproval.js
│       │   │   ├── bridgeCollectionLogic.js
│       │   │   ├── bridgeCollectorsDefaults.js
│       │   │   ├── bridgeCollectorsRegistry.js
│       │   │   ├── bridgeConsoleWrapper.js
│       │   │   ├── bridgeErrorHandler.js
│       │   │   ├── bridgeMain.js
│       │   │   ├── bridgeStorage.js
│       │   │   └── bridgeUtils.js
│       │   ├── theme.js
│       │   └── utils
│       └── views
│           ├── auth
│           │   └── login.js
│           ├── guild
│           │   ├── admin
│           │   │   └── userManagement.js
│           │   └── designer
│           │       ├── designerEvents.js
│           │       ├── designerLayout.js
│           │       ├── designerState.js
│           │       ├── designerUtils.js
│           │       ├── designerWidgets.js
│           │       ├── index.js
│           │       ├── modal
│           │       │   ├── activateConfirmModal.js
│           │       │   ├── deleteModal.js
│           │       │   ├── newItemInputModal.js
│           │       │   ├── saveAsNewModal.js
│           │       │   └── shareModal.js
│           │       ├── panel
│           │       │   ├── properties.js
│           │       │   └── toolbox.js
│           │       ├── toolbox
│           │       │   ├── category.js
│           │       │   ├── text_channel.js
│           │       │   └── voice_channel.js
│           │       └── widget
│           │           ├── categoriesList.js
│           │           ├── channelsList.js
│           │           ├── dashboardConfiguration.js
│           │           ├── dashboardEditor.js
│           │           ├── dashboardPreview.js
│           │           ├── sharedTemplateList.js
│           │           ├── structureTree.js
│           │           ├── templateInfo.js
│           │           └── templateList.js
│           ├── home
│           │   └── index.js
│           └── owner
│               ├── control
│               │   ├── botControls.js
│               │   ├── botLogger.js
│               │   ├── configManagement.js
│               │   └── guildManagement.js
│               └── state-monitor
│                   ├── index.js
│                   ├── panel
│                   │   ├── collectorsList.js
│                   │   └── recentSnapshotsList.js
│                   └── widget
│                       ├── snapshotResultsTabs.js
│                       └── snapshotSummary.js
└── templates
    ├── components
    │   ├── common
    │   │   ├── footer.html
    │   │   └── header.html
    │   ├── forms
    │   ├── guild
    │   │   └── designer
    │   │       └── panel
    │   │           ├── properties.html
    │   │           └── toolbox.html
    │   └── navigation
    │       ├── guild_selector.html
    │       ├── nav_links.html
    │       └── user_menu.html
    ├── debug
    │   ├── add_test_guild.html
    │   └── debug_home.html
    ├── layouts
    │   ├── base_layout.html
    │   ├── error_layout.html
    │   └── three_column_layout.html
    └── views
        ├── admin
        │   ├── guild_config.html
        │   ├── index.html
        │   ├── logs.html
        │   ├── settings.html
        │   ├── system_status.html
        │   └── users.html
        ├── auth
        │   └── login.html
        ├── errors
        │   ├── 400.html
        │   ├── 401.html
        │   ├── 403.html
        │   ├── 404.html
        │   ├── 500.html
        │   └── 503.html
        ├── guild
        │   ├── admin
        │   │   ├── index.html
        │   │   ├── settings.html
        │   │   └── users.html
        │   └── designer
        │       ├── activate_confirm_modal.html
        │       ├── category.html
        │       ├── channel.html
        │       ├── command.html
        │       ├── delete_modal.html
        │       ├── index.html
        │       ├── new_item_input_modal.html
        │       ├── no_template.html
        │       ├── save_as_new_modal.html
        │       └── share_modal.html
        ├── home
        │   └── index.html
        ├── main
        │   └── index.html
        └── owner
            ├── control
            │   ├── add-guild-modal.html
            │   ├── bot-controls.html
            │   ├── config-panel.html
            │   ├── guild-actions.html
            │   ├── guild-details.html
            │   ├── guild-list.html
            │   ├── index.html
            │   └── logger
            │       └── bot.html
            ├── features
            │   └── index.html
            ├── index.html
            ├── monitor
            ├── permissions
            └── state-monitor.html

shared
├── application
│   ├── logging
│   │   ├── formatters.py
│   │   └── log_config.py
│   ├── services
│   │   └── monitoring
│   │       └── state_snapshot_service.py
│   └── tasks
│       └── schedule_key_rotation.py
├── domain
│   ├── audit
│   │   ├── entities
│   │   │   ├── audit_record.py
│   │   │   └── __init__.py
│   │   ├── repositories
│   │   │   ├── audit_repository.py
│   │   │   └── __init__.py
│   │   └── services
│   │       ├── audit_service.py
│   │       └── __init__.py
│   ├── auth
│   │   ├── __init__.py
│   │   ├── policies
│   │   │   ├── authorization_policies.py
│   │   │   └── __init__.py
│   │   └── services
│   │       ├── authentication_service.py
│   │       ├── authorization_service.py
│   │       ├── __init__.py
│   │       └── permission_service.py
│   ├── exceptions.py
│   ├── __init__.py
│   ├── monitoring
│   │   ├── collectors
│   │   │   ├── __init__.py
│   │   │   ├── service_collector.py
│   │   │   └── system_collector.py
│   │   ├── factories
│   │   │   ├── collector_factory.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── repositories
│   │   ├── audit
│   │   │   ├── audit_log_repository.py
│   │   │   └── __init__.py
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── key_repository.py
│   │   │   ├── session_repository.py
│   │   │   └── user_repository.py
│   │   ├── base_repository.py
│   │   ├── dashboards
│   │   │   ├── active_dashboard_repository.py
│   │   │   ├── dashboard_component_definition_repository.py
│   │   │   ├── dashboard_configuration_repository.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── category_repository.py
│   │   │   ├── channel_repository.py
│   │   │   ├── guild_config_repository.py
│   │   │   ├── guild_repository.py
│   │   │   └── __init__.py
│   │   ├── guild_templates
│   │   │   ├── guild_template_category_permission_repository.py
│   │   │   ├── guild_template_category_repository.py
│   │   │   ├── guild_template_channel_permission_repository.py
│   │   │   ├── guild_template_channel_repository.py
│   │   │   ├── guild_template_repository.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   ├── __init__.py
│   │   │   └── monitoring_repository.py
│   │   ├── projects
│   │   │   ├── __init__.py
│   │   │   ├── project_repository.py
│   │   │   └── task_repository.py
│   │   ├── templates
│   │   ├── ui
│   │   │   └── ui_layout_repository.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── ratelimit_repository.py
│   └── services
│       ├── __init__.py
│       └── wireguard
│           ├── config_manager.py
│           └── __init__.py
├── infrastructure
│   ├── config
│   │   ├── env_config.py
│   │   ├── env_loader.py
│   │   ├── env_manager.py
│   │   └── __init__.py
│   ├── constants
│   │   ├── __init__.py
│   │   ├── role_constants.py
│   │   └── user_constants.py
│   ├── database
│   │   ├── api.py
│   │   ├── config
│   │   │   └── user_config.py
│   │   ├── core
│   │   │   ├── config.py
│   │   │   ├── connection.py
│   │   │   ├── credentials.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── alembic
│   │   │   │   ├── alembic.ini
│   │   │   │   ├── env.py
│   │   │   │   └── versions
│   │   │   │       ├── 001_create_core_auth_tables.py
│   │   │   │       ├── 002_create_discord_guild_tables.py
│   │   │   │       ├── 003_create_guild_template_tables.py
│   │   │   │       ├── 004_create_guild_config_table.py
│   │   │   │       ├── 005_create_dashboard_tables.py
│   │   │   │       ├── 006_create_project_tables.py
│   │   │   │       ├── 007_create_ui_tables.py
│   │   │   │       ├── 008_seed_users.py
│   │   │   │       ├── 009_seed_dashboard_component_definitions.py
│   │   │   │       ├── 010_create_state_snapshots_table.py
│   │   │   │       ├── 011_seed_default_dashboards.py
│   │   │   │       └── 012_create_active_dashboards_table.py
│   │   │   ├── __init__.py
│   │   │   ├── migration_service.py
│   │   │   ├── README.md
│   │   │   ├── script.py.mako
│   │   │   └── wait_for_postgres.py
│   │   ├── seeds
│   │   │   └── dashboard_templates
│   │   │       ├── common
│   │   │       │   ├── buttons.py
│   │   │       │   ├── embeds.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── messages.py
│   │   │       │   ├── modals.py
│   │   │       │   ├── selectors.py
│   │   │       │   └── views.py
│   │   │       ├── gamehub
│   │   │       │   ├── buttons.py
│   │   │       │   ├── embeds.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── messages.py
│   │   │       │   ├── modals.py
│   │   │       │   ├── selectors.py
│   │   │       │   └── views.py
│   │   │       ├── monitoring
│   │   │       │   ├── buttons.py
│   │   │       │   ├── embeds.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── messages.py
│   │   │       │   ├── modals.py
│   │   │       │   ├── selectors.py
│   │   │       │   └── views.py
│   │   │       ├── project
│   │   │       │   ├── buttons.py
│   │   │       │   ├── embeds.py
│   │   │       │   ├── __init__.py
│   │   │       │   ├── messages.py
│   │   │       │   ├── modals.py
│   │   │       │   ├── selectors.py
│   │   │       │   └── views.py
│   │   │       └── welcome
│   │   │           ├── buttons.py
│   │   │           ├── embeds.py
│   │   │           ├── __init__.py
│   │   │           ├── messages.py
│   │   │           ├── modals.py
│   │   │           ├── selectors.py
│   │   │           └── views.py
│   │   ├── service.py
│   │   └── session
│   │       ├── context.py
│   │       ├── factory.py
│   │       └── __init__.py
│   ├── encryption
│   │   ├── encryption_commands.py
│   │   ├── encryption_service.py
│   │   ├── __init__.py
│   │   └── key_management_service.py
│   ├── __init__.py
│   ├── logging
│   │   ├── handlers
│   │   │   ├── db_handler.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── log_entry.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   └── log_repository_impl.py
│   │   └── services
│   │       ├── base_logging_service.py
│   │       ├── bot_logging_service.py
│   │       ├── __init__.py
│   │       ├── logging_service.py
│   │       └── web_logging_service.py
│   ├── models
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── rate_limit_entity.py
│   │   │   ├── role_entity.py
│   │   │   ├── session_entity.py
│   │   │   └── user_entity.py
│   │   ├── base.py
│   │   ├── core
│   │   │   ├── audit_log_entity.py
│   │   │   ├── config_entity.py
│   │   │   ├── __init__.py
│   │   │   └── log_entry_entity.py
│   │   ├── dashboards
│   │   │   ├── active_dashboard_entity.py
│   │   │   ├── dashboard_component_definition_entity.py
│   │   │   ├── dashboard_configuration_entity.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── entities
│   │   │   │   ├── auto_thread_channel_entity.py
│   │   │   │   ├── category_entity.py
│   │   │   │   ├── channel_entity.py
│   │   │   │   ├── guild_config_entity.py
│   │   │   │   ├── guild_entity.py
│   │   │   │   ├── guild_user_entity.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── message_entity.py
│   │   │   ├── enums
│   │   │   │   ├── category.py
│   │   │   │   ├── channels.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── guild.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── message.py
│   │   │   ├── __init__.py
│   │   │   └── mappings
│   │   │       ├── category_mapping.py
│   │   │       └── channel_mapping.py
│   │   ├── guild_templates
│   │   │   ├── guild_template_category_entity.py
│   │   │   ├── guild_template_category_permission_entity.py
│   │   │   ├── guild_template_channel_entity.py
│   │   │   ├── guild_template_channel_permission_entity.py
│   │   │   ├── guild_template_entity.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   ├── alert.py
│   │   │   ├── __init__.py
│   │   │   ├── metric.py
│   │   │   └── state_snapshot.py
│   │   ├── project
│   │   │   ├── __init__.py
│   │   │   ├── project_member.py
│   │   │   ├── project.py
│   │   │   └── task.py
│   │   └── ui
│   │       ├── __init__.py
│   │       └── ui_layout_entity.py
│   ├── repositories
│   │   ├── audit
│   │   │   ├── auditlog_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── key_repository_impl.py
│   │   │   ├── session_repository_impl.py
│   │   │   └── user_repository_impl.py
│   │   ├── base_repository_impl.py
│   │   ├── dashboards
│   │   │   ├── active_dashboard_repository_impl.py
│   │   │   ├── dashboard_component_definition_repository_impl.py
│   │   │   ├── dashboard_configuration_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── discord
│   │   │   ├── category_repository_impl.py
│   │   │   ├── channel_repository_impl.py
│   │   │   ├── guild_config_repository_impl.py
│   │   │   ├── guild_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── guild_templates
│   │   │   ├── guild_template_category_permission_repository_impl.py
│   │   │   ├── guild_template_category_repository_impl.py
│   │   │   ├── guild_template_channel_permission_repository_impl.py
│   │   │   ├── guild_template_channel_repository_impl.py
│   │   │   ├── guild_template_repository_impl.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   ├── __init__.py
│   │   │   └── monitoring_repository_impl.py
│   │   ├── projects
│   │   │   ├── __init__.py
│   │   │   ├── project_repository_impl.py
│   │   │   └── task_repository_impl.py
│   │   ├── ui
│   │   │   ├── __init__.py
│   │   │   └── ui_layout_repository_impl.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── ratelimit_repository_impl.py
│   ├── security
│   │   ├── __init__.py
│   │   ├── security_bootstrapper.py
│   │   └── security_service.py
│   ├── startup
│   │   ├── bootstrap.py
│   │   ├── bot_entrypoint.py
│   │   └── web_entrypoint.py
│   ├── state
│   │   ├── collectors
│   │   │   ├── database_status.py
│   │   │   └── system_info.py
│   │   └── secure_state_snapshot.py
│   └── system
│       └── state_collectors.py
├── initializers
│   └── state_collectors.py
├── __init__.py
├── interface
│   ├── __init__.py
│   └── logging
│       ├── api.py
│       ├── factories.py
│       └── __init__.py
└── test
    └── infrastructure
        └── test_entrypoint.py