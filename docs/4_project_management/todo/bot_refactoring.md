# Bot Refactoring Plan: Phase 1 - Dynamic Structure & Constant Removal

**Goal:** Transition from hardcoded constants to a dynamic, database-driven configuration for core components (channels, categories, dashboards), based on Guild Templates and Dashboard Templates.

## 1. Channel & Category Management (Focus: Guild Templates)

*   `[x]` **Remove Old Constants:** Logic using `CHANNELS`, `CATEGORIES`, `CATEGORY_CHANNEL_MAPPINGS` must be removed or replaced.
*   `[x]` **Source of Truth:** Guild structure (channels, categories, permissions) is exclusively defined by `active_template_id` in the `guild_configs` table and associated template tables.
*   **Refactoring Targets:**
    *   `[x]` **Workflows (`ChannelWorkflow`, `CategoryWorkflow`, `GuildWorkflow`):** Must contain logic to sync Discord structure with the active template from the DB. (`GuildWorkflow.apply_template` handles sync; Trigger exists).
    *   `[x]` **Setup Services/Builders (`ChannelSetupService`, `CategorySetupService`, `ChannelBuilder`, `CategoryBuilder`):** Must be revised to process template data instead of static configs. (`Setup` services deleted/obsolete. `Builder` classes seem OK).
    *   `[x]` **`ChannelConfig` Functions:** Methods like `get_channel_factory_config`, `repair_channel_mapping`, `validate_channels` must be removed or fundamentally revised.
    *   `[ ]` **`GameServerChannelService`:** Must be revised to create channels based on dynamic configs (specific templates?) instead of `GameServerChannelConfig`. (**Deferred**).

## 2. Dashboard Management (Focus: Decoupling)

*   `[x]` **Remove Old Constants:** Logic using `DASHBOARD_MAPPINGS` and `DASHBOARD_SERVICES` must be removed or replaced.
*   `[ ]` **Source of Truth:** Available dashboard *types/components* defined by `dashboard_component_definitions`. **Saved Configurations** (independent blueprints) stored in `dashboard_templates`. Active instances tracked in `active_dashboards` (referencing a specific Saved Configuration ID).
*   `[ ]` **Role of `DashboardCategory`:** Enum is solely for categorization/filtering.
*   **Refactoring Targets:**
    *   `[ ]` **`DashboardFactory` / Controller Creation:** No explicit factory needed. Instantiation via Lifecycle/Registry based on DB entities (`active_dashboards`).
    *   `[x]` **Consolidate Controller Logic:** Logic to manage **Saved Configurations** exists in `DashboardConfigurationController`.
    *   `[x]` **Review Service Responsibilities:** Service `DashboardConfigurationService` manages **Saved Configurations**.
    *   `[x]` **Data/Config-Driven Services:** `DashboardConfigurationService` uses DB.
    *   `[ ]` **`DashboardLifecycleService` / `DashboardSetupService`:** Activation must use `active_dashboards` table, referencing the specific **Saved Configuration ID** from `dashboard_templates`. (`Setup` deleted. `Lifecycle` currently uses old repo - **NEEDS REWORK** to use `active_dashboards`).
    *   `[x]` **`DashboardWorkflow`:** Manages state.
    *   `[ ]` **API (Web):** CRUD for **Saved Configurations** exists. Live instance management TBD.
    *   `[ ]` **`DashboardService.sync_dashboard_from_snapshot`:** This concept is likely obsolete. Sync/Update of live instances needs a new mechanism based on `active_dashboards`. (**Review/Remove needed**).

## 3. Specific Checklist (Actions Taken in Phase 1)

*   **Code Logic Fixed/Marked:**
    *   `[x]` ~~`app/bot/infrastructure/discord/category_setup_service.py`: Uses `CATEGORIES`.~~ (File deleted)
    *   `[x]` ~~`app/bot/infrastructure/discord/dashboard_setup_service.py`: Uses `DASHBOARD_MAPPINGS`.~~ (File deleted)
    *   `[x]` ~~`app/bot/infrastructure/config/services/dashboard_config.py`: Uses `dashboard_services`. Check if file/logic is obsolete.~~ (File deleted)
*   **Comments Removed/Updated:**
    *   `[x]` ~~`app/bot/infrastructure/config/channel_config.py`: Comments re `CATEGORY_CHANNEL_MAPPINGS`.~~ (File deleted)
    *   `[x]` ~~`app/web/interfaces/api/rest/v1/dashboards/dashboard_controller.py`: Comments re `DASHBOARD_MAPPINGS`.~~
    *   `[x]` ~~`app/bot/application/services/channel/game_server_channel_service.py`: Comments re `GameServerChannelConfig`.~~
    *   `[x]` ~~`app/bot/application/services/bot_control_service.py`: Comments re `BotConnector`.~~
    *   `[x]` ~~`app/web/interfaces/web/views/owner/control_view.py`: Comments re `BotConnector`.~~
    *   `[x]` ~~`app/web/interfaces/web/views/owner/bot_control_view.py`: Comments re `BotConnector`.~~

## 4. General TODOs

*   `[ ]` Minor TODOs added during refactoring (e.g., error handling, specific implementation details like data fetching in `DashboardController`) should be reviewed and prioritized separately.
