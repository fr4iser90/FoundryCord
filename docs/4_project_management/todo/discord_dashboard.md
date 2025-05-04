# Discord Dashboard Data Fix TODO

**Goal:** Fix dashboard data display: Get the Monitoring dashboard working with live data, then implement the missing data fetching logic for Project and GameHub dashboards.

---

## Phase 1: Fix Monitoring Dashboard (Current Focus)

- [x] **Task 1.1: Verify Service Registration & Consistency**
    - **Description:** After the latest changes to `setup_hooks.py` (registering `SystemCollector` before `DashboardDataService`), restart the bot and check the logs. Verify that:
        - `SystemCollector` is successfully registered.
        - The "Service 'system_collector' not found" error no longer appears when the dashboard attempts to fetch data.
    - **Affected Files:** Logs (`docker logs foundrycord-bot | cat` or similar)
    - **Action:** User to restart bot and provide logs if issues persist.

- [x] **Task 1.2: Test Monitoring Dashboard Display**
    - **Description:** Once the bot is running without the `system_collector` error, check the Monitoring dashboard display in Discord. It should now show actual system metrics (Hostname, CPU %, etc.) instead of placeholders (`{hostname}`, etc.).
    - **Affected Files:** Discord UI
    - **Action:** User to check the dashboard visually and confirm if data is displayed.

## Phase 2: Implement Project Dashboard Data Fetching

- [x] ~~**Task 2.1: Implement `db_repository` Fetch Logic**~~
    - ~~**Description:** Modify `DashboardDataService.fetch_data` to handle the `db_repository` source type defined in the dashboard config. This involves getting the specified repository (e.g., `ProjectRepository`) from the `ServiceFactory` and calling the specified method (e.g., `get_projects_by_guild`).~~
    - ~~**Affected Files:** `app/bot/application/services/dashboard/dashboard_data_service.py`~~
    - ~~**Requires:** Access to `guild_id` or other necessary parameters for the repository method call (needs investigation on how context is passed).~~

- [x] ~~**Task 2.2: Ensure `ProjectRepository` Registration**~~
    - ~~**Description:** Verify that `ProjectRepositoryImpl` (or the relevant service providing it) is registered with the `ServiceFactory` so `DashboardDataService` can retrieve it. If not, add registration logic (likely in `setup_hooks.py`).~~
    - ~~**Affected Files:** `app/bot/infrastructure/startup/setup_hooks.py`, `app/bot/infrastructure/factories/service_factory.py`~~

- [x] ~~**Task 2.3: Test Project Dashboard Display**~~
    - ~~**Description:** After implementing the fetch logic and ensuring repository availability, restart the bot, reset the DB/run migrations (if repository registration was added), and check the Project dashboard display.~~
    - ~~**Affected Files:** Discord UI, Logs~~
    - ~~**Action:** User to test and confirm.~~

## Phase 3: Implement GameHub Dashboard Data Fetching

- [ ] **Task 3.1: Implement `service_collector` Fetch Logic**
    - **Description:** Modify `DashboardDataService.fetch_data` to handle the `service_collector` source type. This involves getting the `ServiceCollector` instance from the `ServiceFactory` and calling its relevant method (e.g., `collect_game_services` or similar) to get game server data.
    - **Affected Files:** `app/bot/application/services/dashboard/dashboard_data_service.py`

- [ ] **Task 3.2: Ensure `ServiceCollector` Registration**
    - **Description:** Verify `ServiceCollector` is registered with the `ServiceFactory` (it likely is, but confirm) and accessible.
    - **Affected Files:** `app/bot/infrastructure/startup/setup_hooks.py`

- [ ] **Task 3.3: Test GameHub Dashboard Display**
    - **Description:** After implementing the fetch logic, restart the bot and check the GameHub dashboard display.
    - **Affected Files:** Discord UI, Logs
    - **Action:** User to test and confirm.

---

## General Notes / Future Considerations

-   The `db_repository` fetching logic needs careful consideration of how context (like `guild_id`) is passed down to the `DashboardDataService`.
-   The exact method to call on `ServiceCollector` for game data needs confirmation.