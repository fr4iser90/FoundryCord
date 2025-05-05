# Bot Structure Refactoring TODO

**Goal:** Refactor the `app/bot` directory structure to align with the organizational patterns observed in `app/web` and `app/shared` (referencing `structure.md` and `tree.md`), improving clarity and maintainability.

**Related Documentation (Optional):**
*   `docs/4_project_management/todo/structure.md`
*   `docs/4_project_management/todo/tree.md`

## Phase 1: Analyse & Initial Restructuring Plan

*   [x] **Task 1:** Analyse `app/bot` structure against `app/web` and `app/shared` (using `tree.md` and `structure.md`). Identify key deviations and list components/modules needing relocation (e.g., services in `application/services` vs. directly in `application`, infrastructure components like factories, monitoring, etc.).
    *   **Affected Files:**
        *   See Analysis: `docs/4_project_management/analysis/structure_comparison.md`
*   [x] **Task 2:** Define specific file/directory move/rename operations based on the structure analysis.
    *   **Affected Files:** (Proposed Plan)
        *   **Create `domain` Layer:**
            *   `mkdir app/bot/domain/`
        *   **Refactor `application` Layer:**
            *   `mkdir app/bot/application/services/`
            *   `mv app/bot/application/services/* app/bot/application/services/` (Excluding `__init__`, verify specific dirs: auth, category, channel, etc.)
            *   `mv app/bot/application/process app/bot/application/tasks`
            *   (Postpone Decision: `app/bot/application/decorators/`)
        *   **Refactor `core` Layer:**
            *   (Postpone Decision: `main.py`, `lifecycle_manager.py`, etc. -> `infrastructure/startup`?)
        *   **Refactor `infrastructure` Layer:**
            *   `mkdir app/bot/infrastructure/state/` (If not exists)
            *   `mv app/bot/infrastructure/state/collectors/* app/bot/infrastructure/state/collectors/` (Verify alignment with shared)
            *   `mv app/bot/infrastructure/state/bot_state_collectors.py app/bot/infrastructure/state/` (Or integrate)
            *   `mkdir app/bot/infrastructure/monitoring/` (If not exists)
            *   (Postpone Decision: Align `monitoring/*` with shared)
            *   (Postpone Decision: Consolidate/Move `component`, `data*`, `managers`, `messaging`)
            *   `mkdir app/bot/interfaces/api/` (If not exists)
            *   `mv app/bot/infrastructure/internal_api app/bot/interfaces/api/internal` (Rename to `internal`?)
            *   (Postpone Decision: Review `factories` structure)
            *   `mkdir app/bot/infrastructure/wireguard/` (Or feature module)
            *   `mv app/bot/database/wireguard app/bot/infrastructure/wireguard/`
            *   `mkdir app/bot/core/middleware/` (If not exists, or shared)
            *   `mv app/bot/infrastructure/rate_limiting app/bot/core/middleware/rate_limiting`
        *   **Refactor `interfaces` Layer:**
            *   (Postpone Decision: Major restructure needed, e.g., `api`/`views`)
        *   **Relocate Top-Level `utils`:**
            *   `mv app/bot/utils/vars.py` (Target TBD: module or shared)
            *   `rmdir app/bot/utils/` (After move)


## Phase 2: Implement Initial Moves

*   [x] **Task 2.1:** Create initial directories: `app/bot/domain/`, `app/bot/application/services/`, `app/bot/application/tasks/`, `app/bot/infrastructure/wireguard/`.
    *   **Affected Files:** (Creates new directories)
*   [x] **Task 2.2:** Move existing service folders from `app/bot/application/` to `app/bot/application/services/`. (Skipped: Source folders not found at original location)
    *   **Affected Files/Dirs:** (Move commands needed)
        *   `mv app/bot/application/auth app/bot/application/services/auth`
        *   `mv app/bot/application/category app/bot/application/services/category`
        *   `mv app/bot/application/channel app/bot/application/services/channel`
        *   `mv app/bot/application/config app/bot/application/services/config`
        *   `mv app/bot/application/dashboard app/bot/application/services/dashboard`
        *   `mv app/bot/application/discord app/bot/application/services/discord`
        *   `mv app/bot/application/monitoring app/bot/application/services/monitoring`
        *   `mv app/bot/application/project_management app/bot/application/services/project_management`
        *   `mv app/bot/application/system_metrics app/bot/application/services/system_metrics`
        *   `mv app/bot/application/wireguard app/bot/application/services/wireguard`
        *   (Note Resolved: `bot_control_service.py` is already in `app/bot/application/services/`)
*   [x] **Task 2.3:** Rename `app/bot/application/process/` to `app/bot/application/tasks/`.
    *   **Affected Files/Dirs:**
        *   `mv app/bot/application/process app/bot/application/tasks`
*   [x] **Task 2.4:** Move `app/bot/database/wireguard/` to `app/bot/infrastructure/wireguard/`. ().
    *   **Affected Files/Dirs:**
        *   `mv app/bot/database/wireguard app/bot/infrastructure/wireguard`
        *   `rmdir app/bot/database` (If empty after move)
*   [x] **Task 2.5:** Relocate `app/bot/utils/vars.py` to `app/bot/infrastructure/config/constants.py`. (Imports checked - none found)
    *   **Affected Files/Dirs:**
        *   `mkdir -p app/bot/infrastructure/config/` (Ensure target dir exists)
        *   `mv app/bot/utils/vars.py app/bot/infrastructure/config/constants.py`
        *   `rmdir app/bot/utils/`
        *   ~~Update imports from `app.bot.utils.vars` to `app.bot.infrastructure.config.constants` (Requires code search & edit)~~ (No imports found)
*   [x] **Task 2.6:** Relocate application decorators to the interfaces layer.
    *   **Affected Files/Dirs:**
        *   `mkdir -p app/bot/interfaces/commands/decorators/`
        *   `mv app/bot/application/decorators/auth.py app/bot/interfaces/commands/decorators/auth.py`
        *   `mv app/bot/application/decorators/respond.py app/bot/interfaces/commands/decorators/respond.py`
        *   `rmdir app/bot/application/decorators/`
        *   ~~Update imports from `app.bot.application.decorators` to `app.bot.interfaces.commands.decorators` (Requires code search & edit)~~ (Updated imports from `app.bot.utils.decorators`)
*   [x] **Task 2.7:** Move core startup/lifecycle files to `infrastructure/startup/`.
    *   **Affected Files/Dirs:**
        *   `mkdir -p app/bot/infrastructure/startup/`
        *   `mv app/bot/core/main.py app/bot/infrastructure/startup/main.py`
        *   `mv app/bot/core/lifecycle_manager.py app/bot/infrastructure/startup/lifecycle_manager.py`
        *   `mv app/bot/core/setup_hooks.py app/bot/infrastructure/startup/setup_hooks.py`
        *   `mv app/bot/core/shutdown_handler.py app/bot/infrastructure/startup/shutdown_handler.py`
        *   ~~Update imports referencing these files in their old `app.bot.core` location.~~ (Imports Updated)
*   [x] **Task 2.8:** Move `internal_api` from `infrastructure` to `interfaces`.
    *   **Affected Files/Dirs:**
        *   `mkdir -p app/bot/interfaces/api/internal`
        *   `mv app/bot/infrastructure/internal_api/* app/bot/interfaces/api/internal/`
        *   `rmdir app/bot/infrastructure/internal_api/`
        *   ~~Update imports from `app.bot.infrastructure.internal_api` to `app.bot.interfaces.api.internal`.~~ (Imports Updated)
*   [x] **Task 2.9:** Relocate remaining `core` components (`workflow*`, `checks`) and cleanup `core`.
    *   **Affected Files/Dirs:**
        *   `mv app/bot/core/workflow_manager.py app/bot/application/workflow_manager.py`
        *   `mv app/bot/core/workflows app/bot/application/workflows`
        *   `mkdir -p app/bot/interfaces/commands/` (Ensure parent dir exists)
        *   `mv app/bot/core/checks.py app/bot/interfaces/commands/checks.py`
        *   `rm app/bot/core/extensions.py`
        *   `rm app/bot/core/__init__.py`
        *   `rmdir app/bot/core/`
        *   ~~Update imports referencing moved files (e.g., `app.bot.core.workflow_manager`, `app.bot.core.workflows.*`, `app.bot.core.checks`).~~ (Imports Updated)
*   [x] **Task 2.10:** Refactor state collector registration.
    *   ~~Move registration logic from `BotStateCollectors` class into `setup_hooks.py` (or a dedicated setup function).~~ (Done)
    *   ~~Delete `app/bot/infrastructure/state/bot_state_collectors.py`.~~ (Done)
    *   ~~Update/remove calls to the old `setup_bot_state_collectors` function.~~ (Not needed - call site not found)
    *   **Affected Files/Dirs:**
        *   `app/bot/infrastructure/startup/setup_hooks.py` (Edit)
        *   `app/bot/infrastructure/state/bot_state_collectors.py` (Delete)
        *   (Potential call sites of `setup_bot_state_collectors` - Requires search)
*   [x] **Task 2.11:** Align monitoring & state structure.
    *   Verified existence of `app/bot/domain/monitoring` (created in 2.1).
    *   Verified placement of implementations in `app/bot/infrastructure/monitoring` and `app/bot/infrastructure/state/collectors`.
    *   No file operations needed for this step.
*   [x] **Task 2.12:** Investigate and consolidate `infrastructure` directories (`component`, `data`, `data_sources`).
        *   Identified redundant `DataSourceRegistry` in `component/registry.py` and `data/data_source_registry.py`.
        *   Removed `DataSourceRegistry` from `component/registry.py`.
        *   Renamed `component/registry.py` to `component/component_registry.py`.
        *   Deleted `component/factory.py` (potentially unused).
        *   Removed empty `data/` directory as `data_source_registry.py` is unused.
        *   Deleted redundant `data_sources/system_metrics_source.py` (functionality exists in `monitoring/collectors/system`).
        *   Removed empty `data_sources/` directory.
        *   Kept `component/` dir for `component_registry.py` (potentially unused, may relocate/delete later).
    *   **Affected Files/Dirs:**
        *   `app/bot/infrastructure/component/component_registry.py` (Renamed from `registry.py`, edited)
        *   `app/bot/infrastructure/component/factory.py` (Deleted)
        *   `app/bot/infrastructure/data/data_source_registry.py` (Deleted)
        *   `app/bot/infrastructure/data/` (Deleted)
        *   `app/bot/infrastructure/data_sources/system_metrics_source.py` (Deleted)
        *   `app/bot/infrastructure/data_sources/` (Deleted)
*   [x] **Task 2.13:** Relocate `DashboardManager` from `infrastructure/managers` to `application/services/dashboard`.
    *   Moved `dashboard_manager.py` to `app/bot/application/services/dashboard/`.
    *   Removed empty `app/bot/infrastructure/managers/` directory.
    *   No static imports found referencing the old path.
    *   **Affected Files/Dirs:**
        *   `app/bot/application/services/dashboard/dashboard_manager.py` (Moved)
        *   `app/bot/infrastructure/managers/` (Deleted)
*   [x] **Task 2.14:** Review `infrastructure/messaging` components and fix imports.
    *   Reviewed `chunk_manager.py`, `http_client.py`, `message_sender.py`, `response_mode.py`.
    *   Fixed import path for `chunk_message` in `message_sender.py`.
    *   Decided to keep `messaging` directory within `app/bot/infrastructure/` for now.
    *   **Affected Files/Dirs:**
        *   `app/bot/infrastructure/messaging/message_sender.py` (Edited)
*   [x] **Task 2.15:** Consolidate component and data source registries.
    *   Identified active `ComponentRegistry` (using DB) in `factories/`.
    *   Deleted old/unused `ComponentRegistry` from `infrastructure/component/`.
    *   Deleted empty `infrastructure/component/` directory.
    *   Identified broken/obsolete `DataSourceRegistry` in `factories/`.
    *   Deleted `factories/data_source_registry.py`.
    *   Moved active `ComponentRegistry` from `factories/` to `infrastructure/config/registries/`.
    *   Updated imports for moved `ComponentRegistry`.
    *   **Affected Files/Dirs:**
        *   `app/bot/infrastructure/component/component_registry.py` (Deleted)
        *   `app/bot/infrastructure/component/` (Deleted)
        *   `app/bot/infrastructure/factories/data_source_registry.py` (Deleted)
        *   `app/bot/infrastructure/config/registries/component_registry.py` (Moved)
        *   `app/bot/__init__.py` (Edited)
        *   `app/bot/application/services/dashboard/dashboard_builder.py` (Edited)
        *   `app/bot/infrastructure/factories/composite/workflow_factory.py` (Edited)
        *   `app/bot/infrastructure/factories/composite/bot_factory.py` (Edited)
        *   `app/bot/infrastructure/factories/component_factory.py` (Edited)
        *   `app/bot/infrastructure/startup/setup_hooks.py` (Edited)
*   [x] **Task 2.16:** Review main factory classes and subdirectories.
    *   Reviewed `ComponentFactory`, `ServiceFactory`, `TaskFactory` (top-level).
    *   Decided to keep these factories in `infrastructure/factories/` for now.
    *   Identified redundant `TaskFactory` in `factories/service/` and deleted it.
    *   Reviewed `factories/base/base_factory.py` (seems reasonable).
    *   Reviewed `factories/composite/bot_factory.py` (complex, maybe overlaps ServiceFactory, keep for now).
    *   Reviewed `factories/composite/workflow_factory.py` (placeholder, keep for now).
    *   Moved `factories/discord/channel_factory.py` and `thread_factory.py` to `infrastructure/discord/factories/`.
    *   Deleted `factories/service/service_resolver.py` (dynamic imports, likely obsolete).
    *   Deleted empty subdirectories `factories/discord/` and `factories/service/`.
    *   **(Future Refactor Note):** `ServiceFactory.create` method is complex and potentially fragile due to dynamic path guessing; consider refactoring to rely only on registered creators/instances.
    *   **Affected Files/Dirs:**
        *   `app/bot/infrastructure/factories/service/task_factory.py` (Deleted)
        *   `app/bot/infrastructure/discord/factories/channel_factory.py` (Moved)
        *   `app/bot/infrastructure/discord/factories/thread_factory.py` (Moved)
        *   `app/bot/infrastructure/factories/discord/` (Deleted)
        *   `app/bot/infrastructure/factories/service/service_resolver.py` (Deleted)
        *   `app/bot/infrastructure/factories/service/` (Deleted)
*   [x] **Task 2.17:** Relocate `rate_limiting` from `infrastructure` to `infrastructure/middleware`.
    *   Created `app/bot/infrastructure/middleware/` directory.
    *   Moved `infrastructure/rate_limiting` to `infrastructure/middleware/rate_limiting`.
    *   No static imports found referencing the old path.
    *   **Affected Files/Dirs:**
        *   `app/bot/infrastructure/middleware/rate_limiting/` (Moved)
*   [x] **Task 2.18:** Review `interfaces` layer structure.
    *   Reviewed contents of `interfaces/api/`, `interfaces/commands/`, and `interfaces/dashboards/`.
    *   Current structure (api, commands, dashboards) seems logical for the bot context.
    *   No major restructuring (like creating `views`) deemed necessary at this time.
    *   Minor internal cleanup within subdirectories can be addressed later if needed.
    *   No file operations needed for this step.
        
## General Notes / Future Considerations

*   [ ] Add any relevant notes here. 
+ *   Fixed numerous test failures related to refactoring (Imports, Mocking issues in `test_dashboard_controller.py`).
+ *   Added missing Python dependencies (`python-dotenv`, `py-cpuinfo`, `speedtest-cli`) to `shell.nix` identified during test execution.
 
## Phase 3: Verification & Refinement

*   [x] **Task 3.1:** Perform basic runtime check (e.g., attempt bot startup) to identify immediate import errors or critical failures.
    *   Fixed circular import involving `BotWorkflowManager` <-> `setup_hooks`.
    *   Fixed circular import involving `GuildWorkflow` <-> `setup_hooks` (via type hints and direct imports).
    *   Fixed circular import involving `FoundryCord` <-> `setup_hooks` (via type hints in factories/components).
    *   Fixed `ModuleNotFoundError` for `factories.service` in `factories/__init__.py`.
    *   Fixed `ImportError` for obsolete `DashboardTemplateEntity` in `dashboard_builder.py` (replaced with correct model/repo imports).
    *   Identified `DashboardBuilder` service as obsolete/redundant (logic exists in `DashboardController`); deleted the file and removed related imports/exports.
*   [x] **Task 3.2:** Conduct code review, focusing on modules heavily impacted by refactoring (startup, factories, services, interfaces) to identify potential logic errors or incorrect dependencies.
    *   Cleaned up incorrect/duplicate imports in `app/bot/application/services/__init__.py` (related to `ProjectManagementService`).
    *   Removed unused/incorrect import of `TaskRepository` in `task_workflow.py`.
    *   Corrected import path for `setup_internal_routes` in `setup_hooks.py`.
    *   Removed import and usage of deleted `DataSourceRegistry` in `setup_hooks.py`.
    *   Added missing import for `BotWorkflowManager` in `setup_hooks.py`.
    *   Added `critical` method to logging services and updated `LogEntry.is_error`.
    *   Removed `DataSourceRegistry` dependency from `DashboardDataService`.
*   [ ] **Task 3.3:** Execute tests (automated if available, otherwise manual functional tests) covering core bot functionality (commands, dashboards, monitoring, internal API) to verify behavior after structural changes.
    *   *(Note: Unit tests for `DashboardController` were run and fixed. Comprehensive functional tests still pending).* 
*   [ ] **Task 3.4:** Address issues identified in Tasks 3.1-3.3 and perform further refinement (e.g., refactor `ServiceFactory.create`, potentially simplify/remove `BotComponentFactory`).
*   [ ] **Task 3.5:** Update architecture documentation (`structure.md`, `overview.md`, etc.) to reflect the new `app/bot` structure.

## Phase 4: Specific Implementation Tasks (Added during Phase 3)

*   [x] **Task 4.1:** Refactor `FoundryCord` class out of `main.py`.
    *   Created `app/bot/infrastructure/startup/bot.py`.
    *   Moved `FoundryCord` class definition from `main.py` to `bot.py`.
    *   Updated `main.py` to import `FoundryCord` from `bot.py`.
    *   Updated imports in `component_registry.py`, `bot_factory.py`, `generic_selector.py`, `dashboard_embed.py` to use the new path.
    *   **Affected Files/Dirs:**
        *   `app/bot/infrastructure/startup/bot.py` (Created)
        *   `app/bot/infrastructure/startup/main.py` (Edited)
        *   `app/bot/infrastructure/config/registries/component_registry.py` (Edited)
        *   `app/bot/infrastructure/factories/composite/bot_factory.py` (Edited)
        *   `app/bot/interfaces/dashboards/components/common/selectors/generic_selector.py` (Edited)
        *   `app/bot/interfaces/dashboards/components/common/embeds/dashboard_embed.py` (Edited)
*   [ ] **Task 4.2:** Final documentation update (if needed) and cleanup. 