```tree
app/web
├── application
│   ├── dtos
│   ├── __init__.py
│   ├── services
│   │   ├── api
│   │   │   ├── api_service.py
│   │   │   └── __init__.py
│   │   ├── auth
│   │   │   └── __init__.py
│   │   ├── dashboards
│   │   │   ├── dashboard_component_service.py
│   │   │   ├── dashboard_configuration_service.py
│   │   │   └── __init__.py
│   │   ├── guild
│   │   │   ├── guild_service.py
│   │   │   ├── __init__.py
│   │   │   ├── management_service.py
│   │   │   ├── query_service.py
│   │   │   └── selection_service.py
│   │   ├── __init__.py
│   │   ├── monitoring
│   │   │   └── __init__.py
│   │   ├── security
│   │   │   └── __init__.py
│   │   ├── template
│   │   │   ├── __init__.py
│   │   │   ├── management_service.py
│   │   │   ├── OLD.py
│   │   │   ├── query_service.py
│   │   │   ├── sharing_service.py
│   │   │   ├── structure_service.py
│   │   │   └── template_service.py
│   │   └── ui
│   │       └── layout_service.py
│   ├── tasks
│   │   └── __init__.py
│   ├── workflow_manager.py
│   └── workflows
│       ├── base_workflow.py
│       ├── __init__.py
│       └── service_workflow.py
├── infrastructure
│   ├── config
│   │   ├── env_loader.py
│   │   └── __init__.py
│   ├── extensions
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── static.py
│   │   ├── templates.py
│   │   └── time.py
│   ├── factories
│   │   ├── base
│   │   │   └── base_factory.py
│   │   ├── composite
│   │   │   └── web_factory.py
│   │   └── service
│   │       └── web_service_factory.py
│   ├── __init__.py
│   ├── middleware
│   │   ├── authentication.py
│   │   ├── __init__.py
│   │   └── request_tracking.py
│   ├── security
│   │   ├── __init__.py
│   │   └── oauth.py
│   └── startup
│       ├── bot_imports.py
│       ├── exception_handlers.py
│       ├── __init__.py
│       ├── init.py
│       ├── init_web.py
│       ├── lifecycle_manager.py
│       ├── main_app.py
│       ├── main_check.py
│       ├── middleware_registry.py
│       └── router_registry.py
├── __init__.py
├── interfaces
│   ├── api
│   │   ├── __init__.py
│   │   └── rest
│   │       ├── dependencies
│   │       │   ├── auth_dependencies.py
│   │       │   └── ui_dependencies.py
│   │       ├── README.md
│   │       ├── routes.py
│   │       └── v1
│   │           ├── auth
│   │           │   ├── auth_controller.py
│   │           │   └── __init__.py
│   │           ├── base_controller.py
│   │           ├── dashboards
│   │           │   ├── dashboard_component_controller.py
│   │           │   ├── dashboard_configuration_controller.py
│   │           │   ├── dashboard_controller.py
│   │           │   └── __init__.py
│   │           ├── debug
│   │           │   ├── debug_controller.py
│   │           │   └── __init__.py
│   │           ├── guild
│   │           │   ├── admin
│   │           │   │   ├── guild_config_controller.py
│   │           │   │   └── guild_user_management_controller.py
│   │           │   ├── designer
│   │           │   │   ├── guild_template_controller.py
│   │           │   │   ├── __init__.py
│   │           │   │   ├── lifecycle_controller.py
│   │           │   │   ├── metadata_controller.py
│   │           │   │   ├── OLD.py
│   │           │   │   └── structure_controller.py
│   │           │   ├── __init__.py
│   │           │   └── selector
│   │           │       └── guild_selector_controller.py
│   │           ├── home
│   │           │   ├── __init__.py
│   │           │   └── overview_controller.py
│   │           ├── __init__.py
│   │           ├── owner
│   │           │   ├── bot_control_controller.py
│   │           │   ├── bot_logger_controller.py
│   │           │   ├── guild_management_controller.py
│   │           │   ├── __init__.py
│   │           │   ├── owner_controller.py
│   │           │   └── state_snapshot_controller.py
│   │           ├── schemas
│   │           │   ├── dashboard_component_schemas.py
│   │           │   ├── dashboard_schemas.py
│   │           │   ├── guild_schemas.py
│   │           │   ├── guild_template_schemas.py
│   │           │   ├── state_monitor_schemas.py
│   │           │   └── ui_layout_schemas.py
│   │           ├── system
│   │           │   ├── health_controller.py
│   │           │   └── __init__.py
│   │           └── ui
│   │               ├── __init__.py
│   │               └── layout_controller.py
│   ├── __init__.py
│   └── web
│       ├── __init__.py
│       ├── routes.py
│       └── views
│           ├── auth
│           │   ├── auth_view.py
│           │   └── __init__.py
│           ├── base_view.py
│           ├── debug
│           │   ├── debug_view.py
│           │   └── __init__.py
│           ├── guild
│           │   ├── admin
│           │   │   ├── index_view.py
│           │   │   ├── __init__.py
│           │   │   ├── logs_view.py
│           │   │   ├── settings_view.py
│           │   │   └── users_view.py
│           │   ├── designer
│           │   │   ├── categories_view.py
│           │   │   ├── channels_view.py
│           │   │   ├── commands_view.py
│           │   │   ├── embeds_view.py
│           │   │   ├── index_view.py
│           │   │   └── __init__.py
│           │   └── __init__.py
│           ├── home
│           │   ├── __init__.py
│           │   └── overview.py
│           ├── __init__.py
│           ├── main
│           │   ├── __init__.py
│           │   └── main_view.py
│           ├── navbar
│           │   ├── guild_selector_view.py
│           │   └── __init__.py
│           └── owner
│               ├── bot_control_view.py
│               ├── bot_logger_view.py
│               ├── control_view.py
│               ├── features_view.py
│               ├── guild_management_view.py
│               ├── __init__.py
│               └── state_monitor_view.py
├── requirements.txt
├── static
│   ├── css
│   │   ├── components
│   │   │   ├── alerts.css
│   │   │   ├── badges.css
│   │   │   ├── buttons.css
│   │   │   ├── cards.css
│   │   │   ├── forms.css
│   │   │   ├── guild-selector.css
│   │   │   ├── index.css
│   │   │   ├── json-viewer.css
│   │   │   ├── modal.css
│   │   │   ├── navbar.css
│   │   │   ├── panels.css
│   │   │   ├── stats.css
│   │   │   ├── table.css
│   │   │   └── widgets.css
│   │   ├── core
│   │   │   ├── base.css
│   │   │   ├── layout.css
│   │   │   ├── reset.css
│   │   │   └── utilities.css
│   │   ├── themes
│   │   │   ├── dark.css
│   │   │   ├── dark_green.css
│   │   │   ├── light.css
│   │   │   ├── light_green.css
│   │   │   └── light_red.css
│   │   └── views
│   │       ├── admin
│   │       │   └── system_status.css
│   │       ├── auth
│   │       │   └── login.css
│   │       ├── dashboard
│   │       │   └── overview.css
│   │       ├── guild
│   │       │   └── designer.css
│   │       └── owner
│   │           ├── bot_logger.css
│   │           ├── control.css
│   │           └── state-monitor.css
│   └── js
│       ├── components
│       │   ├── common
│       │   │   ├── dateTimeUtils.js
│       │   │   ├── index.js
│       │   │   ├── navbar.js
│       │   │   ├── notifications.js
│       │   │   ├── serversWidget.js
│       │   │   └── status_widget.js
│       │   ├── forms
│       │   ├── guildSelector.js
│       │   ├── jsonViewer.js
│       │   ├── layout
│       │   │   └── gridManager.js
│       │   ├── modalComponent.js
│       │   └── navigation
│       ├── core
│       │   ├── main.js
│       │   ├── state-bridge
│       │   │   ├── bridgeApproval.js
│       │   │   ├── bridgeCollectionLogic.js
│       │   │   ├── bridgeCollectorsDefaults.js
│       │   │   ├── bridgeCollectorsRegistry.js
│       │   │   ├── bridgeConsoleWrapper.js
│       │   │   ├── bridgeErrorHandler.js
│       │   │   ├── bridgeMain.js
│       │   │   ├── bridgeStorage.js
│       │   │   └── bridgeUtils.js
│       │   ├── theme.js
│       │   └── utils
│       └── views
│           ├── auth
│           │   └── login.js
│           ├── guild
│           │   ├── admin
│           │   │   └── userManagement.js
│           │   └── designer
│           │       ├── designerEvents.js
│           │       ├── designerLayout.js
│           │       ├── designerState.js
│           │       ├── designerUtils.js
│           │       ├── designerWidgets.js
│           │       ├── index.js
│           │       ├── modal
│           │       │   ├── activateConfirmModal.js
│           │       │   ├── deleteModal.js
│           │       │   ├── newItemInputModal.js
│           │       │   ├── saveAsNewModal.js
│           │       │   └── shareModal.js
│           │       ├── panel
│           │       │   ├── properties.js
│           │       │   └── toolbox.js
│           │       ├── toolbox
│           │       │   ├── category.js
│           │       │   ├── text_channel.js
│           │       │   └── voice_channel.js
│           │       └── widget
│           │           ├── categoriesList.js
│           │           ├── channelsList.js
│           │           ├── dashboardConfiguration.js
│           │           ├── dashboardEditor.js
│           │           ├── dashboardPreview.js
│           │           ├── sharedTemplateList.js
│           │           ├── structureTree.js
│           │           ├── templateInfo.js
│           │           └── templateList.js
│           ├── home
│           │   └── index.js
│           └── owner
│               ├── control
│               │   ├── botControls.js
│               │   ├── botLogger.js
│               │   ├── configManagement.js
│               │   └── guildManagement.js
│               └── state-monitor
│                   ├── index.js
│                   ├── panel
│                   │   ├── collectorsList.js
│                   │   └── recentSnapshotsList.js
│                   └── widget
│                       ├── snapshotResultsTabs.js
│                       └── snapshotSummary.js
└── templates
    ├── components
    │   ├── common
    │   │   ├── footer.html
    │   │   └── header.html
    │   ├── forms
    │   ├── guild
    │   │   └── designer
    │   │       └── panel
    │   │           ├── properties.html
    │   │           └── toolbox.html
    │   └── navigation
    │       ├── guild_selector.html
    │       ├── nav_links.html
    │       └── user_menu.html
    ├── debug
    │   ├── add_test_guild.html
    │   └── debug_home.html
    ├── layouts
    │   ├── base_layout.html
    │   ├── error_layout.html
    │   └── three_column_layout.html
    └── views
        ├── admin
        │   ├── guild_config.html
        │   ├── index.html
        │   ├── logs.html
        │   ├── settings.html
        │   ├── system_status.html
        │   └── users.html
        ├── auth
        │   └── login.html
        ├── errors
        │   ├── 400.html
        │   ├── 401.html
        │   ├── 403.html
        │   ├── 404.html
        │   ├── 500.html
        │   └── 503.html
        ├── guild
        │   ├── admin
        │   │   ├── index.html
        │   │   ├── settings.html
        │   │   └── users.html
        │   └── designer
        │       ├── activate_confirm_modal.html
        │       ├── category.html
        │       ├── channel.html
        │       ├── command.html
        │       ├── delete_modal.html
        │       ├── index.html
        │       ├── new_item_input_modal.html
        │       ├── no_template.html
        │       ├── save_as_new_modal.html
        │       └── share_modal.html
        ├── home
        │   └── index.html
        ├── main
        │   └── index.html
        └── owner
            ├── control
            │   ├── add-guild-modal.html
            │   ├── bot-controls.html
            │   ├── config-panel.html
            │   ├── guild-actions.html
            │   ├── guild-details.html
            │   ├── guild-list.html
            │   ├── index.html
            │   └── logger
            │       └── bot.html
            ├── features
            │   └── index.html
            ├── index.html
            ├── monitor
            ├── permissions
            └── state-monitor.html

112 directories, 272 files
```
