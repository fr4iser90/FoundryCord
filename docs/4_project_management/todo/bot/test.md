# Bot Functionality Test Plan (Post-Refactoring)

**Goal:** Verify core bot functionality after the major `app/bot` structure refactoring (Task 3.3 of `bot_structure_refactoring.md`). Ensure key components interact correctly and critical features remain operational.

**Test Runner:** `pytest`

## Phase 1: Unit Tests

*(Focus: Isolate and test individual classes/functions, mocking dependencies)*

*   [ ] **Application Services:**
    *   [ ] `DashboardManager`: Test registration, activation, deactivation logic (mocking bot, channel, db).
    *   [ ] `DashboardBuilder`: Test component construction logic (mocking registry, components).
    *   [ ] `DashboardDataService`: Test data retrieval logic (mocking data sources/collectors).
    *   [ ] `BotControlService`: Test control commands (mocking bot methods).
    *   [ ] ... (Add other critical services)
*   [ ] **Infrastructure Components:**
    *   [ ] `ServiceFactory`: Test service registration, retrieval, initialization sequence.
    *   [ ] `TaskFactory`: Test task creation, cancellation, state management.
    *   [ ] `ComponentRegistry`: Test DB definition loading, class registration, retrieval.
    *   [ ] `ComponentFactory`: Test component instantiation logic.
    *   [ ] `MessageSender`: Test different response modes (mocking `ctx`).
    *   [ ] ... (Add other critical infrastructure)
*   [ ] **Domain Logic (If applicable):**
    *   [ ] Test any complex domain entities or services defined in `app/bot/domain`.

## Phase 2: Integration Tests

*(Focus: Test interactions between components, potentially using fixtures for database or mocked Discord API)*

*   [ ] **Startup Sequence:**
    *   [ ] Verify successful bot initialization, including service factory setup, registry loading, workflow registration, and hook execution.
*   [ ] **Commands:**
    *   [ ] Test basic execution of key commands (e.g., a monitoring command, an auth command). Requires mocking `discord.Context` and potentially dependent services or Discord API responses.
*   [ ] **Dashboards:**
    *   [ ] Test the lifecycle: activation -> refresh -> deactivation. Requires mocking Discord channel/message interactions and potentially database state.
    *   [ ] Test component interaction (e.g., button click leading to expected action).
*   [ ] **Internal API:**
    *   [ ] Test key endpoints of the internal WebSocket API (e.g., connection, state request). Requires setting up a test client.
*   [ ] **Monitoring/State Collectors:**
    *   [ ] Test registration and basic execution of state collectors via the snapshot service.

## Test Setup Notes

*   Consider using `pytest-asyncio` for async tests.
*   Utilize `unittest.mock` or libraries like `pytest-mock` for mocking dependencies.
*   Fixtures (`pytest.fixture`) will be useful for setting up reusable test resources (e.g., mock bot instance, database session, test configurations).
*   Integration tests might require a test database or carefully mocked external APIs (Discord).
