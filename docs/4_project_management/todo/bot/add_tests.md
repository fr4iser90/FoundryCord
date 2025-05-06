# Add Bot Tests TODO

**Goal:** Increase unit test coverage for critical services, factories, workflows, commands, and infrastructure components within the `app/bot` directory. Ensure core logic is tested in isolation, improving maintainability and confidence in future changes.

**Related Documentation (Optional):**
*   `docs/4_project_management/todo/shared/test-plan.md`
*   `docs/3_developer_guides/01_getting_started/testing_guidelines.md` (To be created/updated alongside this)

## Phase 1: Core Factories & Services (Unit Tests)

*   [x] **Task 1.1:** Write unit tests for `app/bot/infrastructure/factories/service_factory.py`.
    *   Focus: Registration (creator/instance), retrieval, overwrite handling, `get_all_services`. Mock `bot`.
    *   Test File: `app/tests/unit/bot/infrastructure/factories/test_service_factory.py` (Create)
    *   Affected Files:
        *   `app/bot/infrastructure/factories/service_factory.py`
        *   `app/tests/unit/bot/infrastructure/factories/test_service_factory.py`
*   [x] **Task 1.2:** Write unit tests for `app/bot/infrastructure/factories/component_factory.py`.
    *   Focus: `create` method logic based on registry data. Mock `ComponentRegistryInterface`.
    *   Test File: `app/tests/unit/bot/infrastructure/factories/test_component_factory.py` (Create)
    *   Affected Files:
        *   `app/bot/infrastructure/factories/component_factory.py`
        *   `app/tests/unit/bot/infrastructure/factories/test_component_factory.py`
*   [x] **Task 1.3:** Write unit tests for `app/bot/application/services/dashboard/dashboard_data_service.py`.
    *   Focus: `initialize` and `fetch_data` logic. Mock `bot`, `service_factory`, collectors, repositories.
    *   Test File: `app/tests/unit/bot/application/services/dashboard/test_dashboard_data_service.py` (Create)
    *   Affected Files:
        *   `app/bot/application/services/dashboard/dashboard_data_service.py`
        *   `app/tests/unit/bot/application/services/dashboard/test_dashboard_data_service.py`
*   [x] **Task 1.4:** Write unit tests for `app/bot/infrastructure/config/registries/component_registry.py`.
    *   Focus: Registration, retrieval of definitions, `get_all_component_types`, `has_component`. Mock DB interactions (`load_definitions_from_db`).
    *   Test File: `app/tests/unit/bot/infrastructure/config/registries/test_component_registry.py` (Verify/Extend)
    *   Affected Files:
        *   `app/bot/infrastructure/config/registries/component_registry.py`
        *   `app/tests/unit/bot/infrastructure/config/registries/test_component_registry.py`

## Phase 2: Workflows (Unit Tests)

*   [x] **Task 2.1:** Write unit tests for `app/bot/application/workflows/guild_template_workflow.py`.
    *   Focus: `initialize`, `create_template_for_guild` (structure processing). Mock `DatabaseWorkflow`, `GuildWorkflow`, `bot`, Discord objects, Repositories.
    *   Test File: `app/tests/unit/bot/application/workflows/test_guild_template_workflow.py` (Create)
    *   Affected Files:
        *   `app/bot/application/workflows/guild_template_workflow.py`
        *   `app/tests/unit/bot/application/workflows/test_guild_template_workflow.py`
*   [x] **Task 2.2:** Write unit tests for `app/bot/application/workflows/dashboard_workflow.py`.
    *   Focus: `initialize`, interaction with `DashboardLifecycleService`, `load_dashboards`, `cleanup_guild`. Mock `DatabaseWorkflow`, `DashboardLifecycleService`, DB Repos.
    *   Test File: `app/tests/unit/bot/application/workflows/test_dashboard_workflow.py` (Create)
    *   Affected Files:
        *   `app/bot/application/workflows/dashboard_workflow.py`
        *   `app/tests/unit/bot/application/workflows/test_dashboard_workflow.py`
*   [x] **Task 2.3:** Write unit tests for `app/bot/application/workflows/user_workflow.py`.
    *   Focus: Initialization, user data synchronization (`sync_guild_members`, `sync_guild_to_database`). Mock `DatabaseWorkflow`, `bot`, DB Repos, session.
    *   Test File: `app/tests/unit/bot/application/workflows/test_user_workflow.py` (Create)
    *   Affected Files:
        *   `app/bot/application/workflows/user_workflow.py`
        *   `app/tests/unit/bot/application/workflows/test_user_workflow.py`
*   [ ] **Task 2.4:** Add unit tests for `CategoryWorkflow`, `ChannelWorkflow`, `TaskWorkflow`.
    *   Note: `GuildWorkflow` was renamed/refactored to `GuildTemplateWorkflow` (Task 2.1). 
    *   Create separate test files for each, focusing on their core logic.
    *   Status:
        *   `CategoryWorkflow` tests: Done.
        *   `ChannelWorkflow` tests: Done.
        *   `TaskWorkflow` tests: Up next.

## Phase 3: Commands & Checks (Unit Tests)

*   [ ] **Task 3.1:** Identify key commands in `app/bot/interfaces/commands/`.
*   [ ] **Task 3.2:** Write unit tests for a representative monitoring command (e.g., system status).
    *   Focus: Correct output formatting, argument parsing, service interaction. Mock `Context`, relevant services.
    *   Test File: e.g., `app/tests/unit/bot/interfaces/commands/monitoring/test_monitoring_commands.py` (Create)
*   [ ] **Task 3.3:** Write unit tests for a representative authentication/authorization command.
    *   Focus: Logic based on user auth status, permission checks. Mock `Context`, auth services, user roles/permissions.
    *   Test File: e.g., `app/tests/unit/bot/interfaces/commands/auth/test_auth_commands.py` (Create)
*   [ ] **Task 3.4:** Write unit tests specifically for command checks (e.g., `check_guild_approval`).
    *   Focus: Verify check passes/fails correctly based on mock context/state.
    *   Test File: e.g., `app/tests/unit/bot/interfaces/commands/test_checks.py` (Create)
*   [ ] **Task 3.5:** Add unit tests for other important command groups (`dashboard`, `tracker`, `utils`, `wireguard`).

## Phase 4: Infrastructure Components (Unit Tests)

*   [ ] **Task 4.1:** Write unit tests for `app/bot/infrastructure/monitoring/collectors/system/impl.py`.
    *   Focus: Data collection logic. Mock `psutil` calls and file reads (`/etc/hostname`).
    *   Test File: `app/tests/unit/bot/infrastructure/monitoring/collectors/system/test_system_collector.py` (Create)
*   [ ] **Task 4.2:** Write unit tests for `app/bot/infrastructure/monitoring/collectors/service/impl.py`.
    *   Focus: Data collection logic for game/docker services. Mock external checks or APIs.
    *   Test File: `app/tests/unit/bot/infrastructure/monitoring/collectors/service/test_service_collector.py` (Create)
*   [ ] **Task 4.3:** Write unit tests for `app/bot/infrastructure/dashboards/dashboard_registry.py`.
    *   Focus: Dashboard registration, activation/update logic, cleanup. Mock `bot`, `DashboardController`, `ServiceFactory`, `ComponentRegistry`.
    *   Test File: `app/tests/unit/bot/infrastructure/dashboards/test_dashboard_registry.py` (Create)
*   [ ] **Task 4.4:** Add tests for other relevant infrastructure (`startup/setup_hooks.py` helpers, `api/internal/websocket_manager.py`, etc.).

## General Notes / Future Considerations

*   Focus on unit tests first for broad coverage of isolated logic.
*   Integration tests (Phase 2 in `test-plan.md`) should be considered afterwards for testing component interactions.
*   Aim for testing behavior and outcomes rather than implementation details.
