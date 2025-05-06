# Web Application Structure (`app/web`, `static/`, `templates/`)

This document details the internal structure of the FoundryCord Web Application, which primarily resides within `app/web/` but also utilizes `static/` and `templates/` from the project root. It provides developers with an understanding of its organization, architectural layers, key components, and entry points.

## Architectural Overview

The web application follows a **Layered Architecture** and an **MVC-like (Model-View-Controller)** pattern, leveraging FastAPI for the backend API and Jinja2 for server-side HTML templating.

*   **Layered Architecture:**
    *   **Interfaces:** Defines how the web application interacts with users (via browser) and potentially other systems. This includes REST API controllers and HTML view handlers.
    *   **Application:** Orchestrates use cases, containing application-specific business logic. It utilizes services to perform tasks and interact with the domain and shared core.
    *   **Infrastructure:** Implements adapters for external concerns like configuration, FastAPI extensions (e.g., static files, templates), middleware, security integrations (OAuth), and application startup/lifecycle.
    *   **(Domain):** Core domain logic largely resides in `app/shared/domain/` to be accessible by both the web and bot applications.

*   **MVC-like Pattern with FastAPI & Jinja2:**
    *   **Controller:** FastAPI path operation functions (found in `app/web/interfaces/api/rest/v1/..._controller.py` and `app/web/interfaces/web/views/..._view.py`) handle incoming HTTP requests, process input, interact with application services, and return responses (JSON for API, HTML for web views).
    *   **Model/Service:** Application services (`app/web/application/services/`) and shared services/repositories (`app/shared/`) encapsulate business logic and data access.
    *   **View:** Jinja2 templates (`templates/`) render HTML pages dynamically, receiving data from the view/controller functions.
    *   **Static Assets:** Frontend JavaScript (`static/js/`), CSS (`static/css/`), and images are served directly.

## Key Directory Breakdown

Below is a description of the primary directories related to the web application:

*   **`app/web/interfaces/`**: This layer serves as the primary entry point for HTTP requests.
    *   `api/rest/v1/`: Contains FastAPI routers and controllers that define the RESTful API endpoints. Subdirectories often group controllers by domain (e.g., `auth/`, `dashboards/`, `guild/`). Includes Pydantic schemas (`schemas/`) for request/response validation and serialization, and dependencies (`dependencies/`) for shared logic like authentication checks.
    *   `web/views/`: Contains FastAPI routers/handlers that render HTML pages using Jinja2 templates. These often correspond to user-facing sections of the website (e.g., `auth/`, `guild/designer/`, `home/`).

*   **`app/web/application/`**: Houses the core application logic for web-specific functionalities.
    *   `services/`: Contains services that implement business logic specific to web application use cases (e.g., `DashboardConfigurationService`, `GuildService`, `TemplateService`). These services often interact with shared repositories and domain models.
    *   `dtos/`: Data Transfer Objects, if used specifically within the web application layer for passing data between services and controllers (distinct from API Pydantic schemas).
    *   `tasks/`: Defines any background tasks or scheduled jobs specific to or triggered by the web application.
    *   `workflows/`: Implements more complex, multi-step processes or use cases initiated via the web interface.

*   **`app/web/infrastructure/`**: Provides concrete implementations for web-specific infrastructure concerns.
    *   `config/`: Manages web application-specific configuration loading.
    *   `extensions/`: Custom FastAPI extensions or configurations (e.g., setting up static file serving, Jinja2 template engine, session management).
    *   `factories/`: Implements factory patterns for creating web-specific objects (e.g., `WebServiceFactory`).
    *   `middleware/`: Custom FastAPI middleware (e.g., for authentication, request tracking, error handling).
    *   `security/`: Handles security aspects like OAuth integration.
    *   `startup/`: Manages the FastAPI application\'s startup sequence, including creating the `FastAPI` app instance (`main_app.py`), registering routers, middleware, exception handlers, and lifecycle events (`init_web.py`, `lifecycle_manager.py`).

*   **`static/` (Project Root)**: Contains all static frontend assets served directly to the browser.
    *   `css/`: Stylesheets, organized into components, core styles, themes, and view-specific styles.
    *   `js/`: JavaScript files, often organized by components, core utilities, and view-specific logic. This includes client-side interactions, API calls to the backend, and UI manipulations.
    *   *(May also contain images, fonts, etc.)*

*   **`templates/` (Project Root)**: Contains Jinja2 HTML templates used for server-side rendering of web pages.
    *   Organized by layouts, components (reusable UI snippets), and views (page-specific templates).

## Entry Point

The primary entry point for initializing and configuring the FastAPI web application is likely within **`app/web/infrastructure/startup/`**, specifically files like `main_app.py` (where `FastAPI()` is instantiated) and `init_web.py` or `lifecycle_manager.py` (where routers, middleware, and event handlers are attached to the app instance).

## Configuration Loading

Web application configuration is loaded via:

1.  Environment variables (defined in `docker/.env` and loaded via `python-dotenv`).
2.  Configuration files/modules within `app/web/infrastructure/config/` (e.g., `env_loader.py`).
3.  Shared configuration mechanisms from `app/shared/infrastructure/config/`.

FastAPI settings management (potentially using Pydantic\'s `BaseSettings`) might also be employed.

## Directory Tree (Visual Aid)

(The existing tree diagram from the file will be preserved below this section)

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
│   │     ├── init.py
│   │     ├── init_web.py
│   │     ├── lifecycle_manager.py
│   │     ├── main_app.py
│   │     ├── main_check.py
│   │     ├── middleware_registry.py
│   │     └── router_registry.py
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
│   │          └── owner
│   │              ├── bot_control_view.py
│   │              ├── bot_logger_view.py
│   │              ├── control_view.py
│   │              ├── features_view.py
│   │              ├── guild_management_view.py
│   │              ├── __init__.py
│   │              └── state_monitor_view.py
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
