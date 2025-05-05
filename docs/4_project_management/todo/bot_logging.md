# Reduce Startup Log Noise TODO (Revised - Phase 2)

**Goal:** **MINIMIEREN** der Anzahl von `INFO`-Log-Meldungen während des Bot-Starts, um eine saubere Konsolenausgabe zu erreichen (gemäß `@logging_guidelines.md`). Ändern fast aller detaillierten Startup-Schritte auf `DEBUG`, sodass `INFO` nur noch **absolute Top-Level-Meilensteine** (z.B. "Bot logged in", kritische Fehler) anzeigt.

---

## Phase 1: Core Infrastructure Initialization

- [x] ~~**Task 1.1: Refactor Core Component Setup Logs**~~
    - ~~**Description:** Change INFO logs for *individual* core component initializations (`Component registry initialized`, `Component factory initialized`, `Shutdown handler initialized`, `BotControlService initialized`, `Core components setup complete`) to DEBUG in `app/bot/infrastructure/startup/setup_hooks.py` (`setup_core_components`). Consider changing the initial "Setting up..." log to DEBUG as well.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/startup/setup_hooks.py`~~
    - ~~**Action:** Modify code to change log levels.~~ Done.

- [x] ~~**Task 1.2: Refactor Service Factory & Core Service Registration Logs**~~
    - ~~**Description:** Change INFO logs for Service Factory setup (`Setting up Service Factory...`, `Registering core services...`, `Service Factory setup... complete`) and individual service registration logs (if any) to DEBUG in `app/bot/infrastructure/startup/setup_hooks.py` (`setup_service_factory_and_register_core_services`). Consider changing the final "complete" log to DEBUG.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/startup/setup_hooks.py`~~
    - ~~**Action:** Modify code to change log levels.~~ Done.

- [x] ~~**Task 1.3: Refactor Default/Generic Component Registration Logs**~~
    - ~~**Description:** Change INFO logs for registering *individual* default components (`Registered component implementation class for type: ...`) to DEBUG in `app/bot/infrastructure/startup/setup_hooks.py` (`register_default_components`). Consider changing the initial "Registering default..." log to DEBUG.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/startup/setup_hooks.py`~~
    - ~~**Action:** Modify code to change log levels.~~ Done.

- [x] **Task 1.4: Refactor Bot State Collector Registration Logs**
    - **Description:** Change INFO logs for registering *individual* collectors (`Registered state collector: ...`) and the "Bot state collectors registered successfully." log to DEBUG in `app/bot/infrastructure/startup/setup_hooks.py` (`register_state_collectors`). Consider changing the initial "Registering bot state collectors..." log to DEBUG.
    - **Affected Files:**
        - `app/bot/infrastructure/startup/setup_hooks.py`
    - **Action:** Modify code to change log levels. Done.

## Phase 2: Workflow Initialization

- [x] ~~**Task 2.1: Refactor Workflow Registration Logs**~~
    - ~~**Description:** Change INFO logs for workflow registration setup (`Setting up and registering workflows...`, `Set initialization order...`, `Workflows registered and order set.`) to DEBUG in `app/bot/infrastructure/startup/setup_hooks.py` (`register_workflows`).~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/startup/setup_hooks.py`~~
    - ~~**Action:** Modify code to change log levels.~~ Done.

- [x] **Task 2.2: Refactor Workflow Manager Initialization Logs**
    - **Description:** Change INFO logs for individual workflow initialization steps (`Initializing workflow: X`, `Workflow X initialized successfully`) to DEBUG in `app/bot/application/workflow_manager.py` (`initialize_all`).
    - **Affected Files:**
        - `app/bot/application/workflow_manager.py`
    - **Action:** Modify code to change log levels. Done.

- [x] ~~**Task 2.3: Refactor Individual Workflow Initialization Logs**~~
    - ~~**Description:** Change *all* INFO logs within the `initialize` methods of individual workflow classes (e.g., `[DatabaseWorkflow] Starting initialization...`, `[DatabaseWorkflow] Initialized successfully.`, `[GuildTemplateWorkflow] Initialized successfully.`, `[DashboardWorkflow] Starting initialization...`, `[DashboardWorkflow] Instantiating...`, `Task workflow initialized successfully`) to DEBUG.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/application/workflows/database_workflow.py`~~
        - ~~`app/bot/application/workflows/guild_template_workflow.py`~~
        - ~~`app/bot/application/workflows/dashboard_workflow.py`~~
        - ~~`app/bot/application/workflows/task_workflow.py`~~
        - ~~(Potentially others like `guild`, `category`, `channel`, `user`)~~
    - ~~**Action:** Modify code to change log levels in each workflow file.~~ Done.

## Phase 3: `on_ready` and Final Startup Logs

- [x] ~~**Task 3.1: Refactor `on_ready` Core Logs**~~
    - ~~**Description:** Change INFO logs within `on_ready` (in `bot.py`) like `"Core initialization (...) completed successfully."` and `"on_ready: Triggering activation..."` to DEBUG. *KEEP* `"Logged in as..."` at INFO.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/startup/bot.py`~~
    - ~~**Action:** Modify code to change log levels.~~ Done.

- [x] ~~**Task 3.2: Refactor Top-Level Startup Sequence Logs**~~
    - ~~**Description:** Change other high-level INFO logs during startup sequence (e.g., `"Starting the bot..."` in `bot.py`, `"Database service initialized successfully"`, `"Waiting for PostgreSQL..."`) to DEBUG.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/startup/bot.py`~~
        - ~~`app/shared/infrastructure/database/core/setup.py` (or wherever DB init logs originate)~~ -> Found in `database/service.py`
        - ~~`app/shared/application/logging/log_config.py` (for the initial "Logging configured..." if desired)~~ -> Found in `log_config.py`
    - ~~**Action:** Modify code to change log levels.~~ Done.

- [x] ~~**Task 3.3: Refactor Dashboard Registry Initialization Logs**~~
    - ~~**Description:** Change INFO logs like `"Dashboard registry initialized..."` and `"DashboardRegistry refresh loop..."` to DEBUG in `app/bot/infrastructure/dashboards/dashboard_registry.py`.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/dashboards/dashboard_registry.py`~~
    - ~~**Action:** Modify code to change log levels.~~ Done.

- [x] ~~**Task 3.4: Refactor Miscellaneous Identified Logs**~~
    - ~~**Description:** Change previously identified INFO logs like `"Successfully loaded ... component definitions"`, `"Speed test skipped..."`, `"Repository: Successfully updated message_id..."` to DEBUG.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/config/registries/component_registry.py`~~
        - ~~`app/bot/infrastructure/monitoring/checkers/speed_test.py`~~ -> Found in `monitoring/collectors/system/components/hardware/speed_test.py`
        - ~~`app/shared/infrastructure/repositories/dashboards/active_dashboard_repository_impl.py`~~
    - ~~**Action:** Modify code to change log levels.~~ Done.

## Phase 4: Verification

- [ ] **Task 4.1: Deploy and Verify Minimal Log Output**
    - **Description:** After completing Phases 1-3, ensure `console_level: INFO` is set. Deploy and verify `docker logs foundrycord-bot` shows *minimal* output (ideally just "Logged in as...", maybe "Logging configured...", and warnings/errors).
    - **Affected Files:**
        - `app/shared/application/logging/log_config.py`
    - **Action:** Configure, Deploy, Verify Logs. **FAILED** (Several unexpected INFO logs remain).

---

## Phase 5: Final INFO Reduction (Post-Verification 2)

- [x] ~~**Task 5.1: Refactor Bootstrap Logs**~~
    - ~~**Description:** Change INFO logs for "Starting bot application initialization", "Application bootstrap completed successfully", "Bot application bootstrap completed successfully" to DEBUG.~~
    - ~~**Affected Files:**~~
        - ~~`app/shared/infrastructure/startup/bootstrap.py`~~ ~~(likely)~~ (Found "Application bootstrap completed...")
        - ~~`app/bot/infrastructure/startup/main.py` (or bot bootstrap)~~ -> `app/shared/infrastructure/startup/bot_entrypoint.py` (Found others)
    - ~~**Action:**~~ Done.

- [x] ~~**Task 5.2: Refactor Database Session Factory Logs**~~
    - ~~**Description:** Change INFO logs for "Database initialization completed", "Attempting to initialize SessionFactory...", "Session factory initialized successfully" to DEBUG.~~ ("Database initialization completed" handled in Task 5.1 via `bootstrap.py`)
    - ~~**Affected Files:**~~
        - ~~`app/shared/infrastructure/database/session/factory.py`~~ ~~(likely)~~ (Found others)
    - ~~**Action:**~~ Done.

- [x] ~~**Task 5.3: Refactor Security Component Logs**~~
    - ~~**Description:** Change INFO log for "Security components initialized successfully" to DEBUG.~~ (Handled in Task 5.1 via `bootstrap.py`)
    - ~~**Affected Files:**~~
        - ~~`app/shared/infrastructure/security/setup.py`~~ ~~(likely, or bootstrap)~~ -> `bootstrap.py`
    - ~~**Action:**~~ Done.

- [x] ~~**Task 5.4: Refactor Core Bot Component Init Logs**~~
    - ~~**Description:** Change INFO logs in the `__init__` methods for "Component registry initialized", "Component factory initialized with registry", "Shutdown handler initialized", "BotControlService initialized." to DEBUG.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/infrastructure/config/registries/component_registry.py`~~
        - ~~`app/bot/infrastructure/factories/component_factory.py`~~
        - ~~`app/bot/infrastructure/startup/shutdown_handler.py`~~
        - ~~`app/bot/application/services/bot_control_service.py`~~
    - ~~**Action:**~~ Done.

- [x] ~~**Task 5.5: Refactor Workflow Manager Order Log**~~
    - ~~**Description:** Change INFO log for "Set initialization order: [...]" to DEBUG.~~
    - ~~**Affected Files:**~~
        - ~~`app/bot/application/workflow_manager.py` (`set_initialization_order` method)~~
    - ~~**Action:**~~ Done.

---

## Phase 6: Final Verification (Round 2)

- [x] ~~**Task 6.1: Deploy and Verify Minimal Log Output (Again)**~~
    - ~~**Description:** After completing Phase 5, ensure `console_level: INFO` is set. Deploy and verify `docker logs foundrycord-bot` shows *minimal* output (ONLY "Logged in as..." and warnings/errors).~~
    - ~~**Affected Files:**~~
        - ~~`app/shared/application/logging/log_config.py`~~
    - ~~**Action:** Configure, Deploy, Verify Logs.~~ PASSED.

---

## Related Documentation

- `@docs/3_developer_guides/01_getting_started/logging_guidelines.md`

---

## General Notes / Future Considerations

- Focus is on reducing `INFO` noise during startup. `DEBUG` logs should remain available for troubleshooting when needed.
- Only change `logger.info` calls to `logger.debug`. Do not change log messages themselves unless necessary for clarity after level change.
