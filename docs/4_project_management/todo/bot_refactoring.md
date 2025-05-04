# Bot Refactoring Plan: Phase 1 - Dynamic Structure & Constant Removal

**Goal:** Transition from hardcoded constants to a dynamic, database-driven configuration for core components (channels, categories, dashboards), based on Guild Templates and Dashboard Templates.

**Related Documentation (Optional):**
*   [Link to relevant ADRs, design docs, etc.]

## Phase 1: Channel & Category Management (Focus: Guild Templates)

*   [x] **Remove Old Constants:** Logic using `CHANNELS`, `CATEGORIES`, `CATEGORY_CHANNEL_MAPPINGS` must be removed or replaced.
    *   **Affected Files:** (Files using these constants were targeted, many now deleted/refactored).
*   [x] **Ensure Source of Truth:** Verify guild structure (channels, categories, permissions) is exclusively defined by `active_template_id` in the `guild_configs` table and associated template tables.
*   [x] **Refactor Workflows:** Ensure workflows contain logic to sync Discord structure with the active template from the DB.
    *   **Affected Files:**
        *   `app/bot/core/workflows/channel/channel_workflow.py` (Verify path)
        *   `app/bot/core/workflows/category/category_workflow.py` (Verify path)
        *   `app/bot/core/workflows/guild/guild_workflow.py` (`apply_template` handles sync; Trigger exists).
*   [x] **Revise Setup Services/Builders:** Ensure builders process template data; Setup services deleted/obsolete.
    *   **Affected Files:**
        *   `app/bot/infrastructure/discord/channel_builder.py` (Verify path/status)
        *   `app/bot/infrastructure/discord/category_builder.py` (Verify path/status)
        *   ~~`app/bot/infrastructure/discord/channel_setup_service.py`~~ (Deleted)
        *   ~~`app/bot/infrastructure/discord/category_setup_service.py`~~ (Deleted)
*   [x] **Revise/Remove `ChannelConfig` Functions:** Methods like `get_channel_factory_config`, `repair_channel_mapping`, `validate_channels` using old constants must be removed or fundamentally revised.
    *   **Affected Files:**
        *   ~~`app/bot/infrastructure/config/channel_config.py`~~ (Deleted)
*   [ ] **Revise `GameServerChannelService` (Deferred):** Must be revised to create channels based on dynamic configs instead of `GameServerChannelConfig`.
    *   **Affected Files:**
        *   `app/bot/application/services/channel/game_server_channel_service.py`

## Phase 2: Dashboard Management (Focus: Decoupling)

*   [x] **Remove Old Constants:** Logic using `DASHBOARD_MAPPINGS` and `DASHBOARD_SERVICES` must be removed or replaced.
    *   **Affected Files:**
        *   ~~`app/bot/infrastructure/discord/dashboard_setup_service.py`~~ (Deleted)
        *   ~~`app/bot/infrastructure/config/services/dashboard_config.py`~~ (Deleted)
*   [ ] **Ensure Source of Truth:** Available dashboard *types/components* defined by `dashboard_component_definitions`. **Saved Configurations** stored in `dashboard_templates`. Active instances tracked in `active_dashboards`.
*   [ ] **Clarify Role of `DashboardCategory`:** Enum is solely for categorization/filtering.
*   [ ] **Refactor Dashboard Instantiation:** No explicit factory needed. Instantiation via Lifecycle/Registry based on DB entities (`active_dashboards`).
    *   **Affected Files:** (Previously involved `DashboardFactory`)
*   [x] **Consolidate Saved Config Logic:** Logic to manage **Saved Configurations** exists in `DashboardConfigurationController`.
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/dashboards/dashboard_controller.py`
*   [x] **Review Service Responsibilities:** Service `DashboardConfigurationService` manages **Saved Configurations**.
    *   **Affected Files:**
        *   `app/web/application/services/dashboards/dashboard_configuration_service.py`
*   [x] **Verify Data/Config-Driven Services:** `DashboardConfigurationService` uses DB.
*   [ ] **Rework `DashboardLifecycleService`:** Activation must use `active_dashboards` table, referencing the specific **Saved Configuration ID** from `dashboard_templates`. (`Setup` deleted. `Lifecycle` currently uses old repo - **NEEDS REWORK**).
    *   **Affected Files:**
        *   `app/bot/application/services/dashboard/dashboard_lifecycle_service.py` (Verify path)
*   [x] **Review `DashboardWorkflow`:** Manages state.
    *   **Affected Files:**
        *   `app/bot/core/workflows/dashboard/dashboard_workflow.py` (Verify path)
*   [ ] **API (Web):** CRUD for **Saved Configurations** exists. Live instance management TBD.
*   [ ] **Review/Remove `DashboardService.sync_dashboard_from_snapshot`:** This concept is likely obsolete. Sync/Update of live instances needs a new mechanism based on `active_dashboards`.
    *   **Affected Files:**
        *   (Find relevant `DashboardService` file)

## Phase 3: Specific Checklist Review (Actions Taken Previously)

*   **Note:** The items previously listed under "Specific Checklist" and "Comments Removed/Updated" have been integrated into the tasks in Phase 1 and Phase 2 or marked as complete/deleted there. This section is kept for reference but ideally, these specific file checks should be part of the main task verification.

## General Notes / Future Considerations

*   [ ] Minor TODOs added during refactoring (e.g., error handling, specific implementation details like data fetching in `DashboardController`) should be reviewed and prioritized separately.
