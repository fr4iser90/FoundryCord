# Reduce Startup Log Noise TODO (Revised)

**Goal:** **MINIMIEREN** der Anzahl von `INFO`-Log-Meldungen während des Bot-Starts, um eine saubere Konsolenausgabe zu erreichen. Ändern fast aller detaillierten Startup-Schritte auf `DEBUG`, sodass `INFO` nur noch **absolute Top-Level-Meilensteine** (z.B. "Bot gestartet", kritische Fehler) oder explizit gewünschte Betriebs-Infos anzeigt.

---

## Phase 1: Initial Analysis & Refactor (Workflow/Service Init)

- [x] ~~**Task 1.1: Locate and refactor startup logs in `app/bot/infrastructure/startup/bot.py` (or equivalent)**~~
    - ~~**Description:** Finde die Haupt-Startsequenz des Bots. Ändere detaillierte `logger.info`-Aufrufe auf `logger.debug`.~~
    - ~~**Action:** Done.~~

- [x] ~~**Task 1.2: Refactor specific Workflow initialization logs (Example: GuildWorkflow)**~~
    - ~~**Description:** Untersuche exemplarisch Workflows. Ändere interne `logger.info`-Aufrufe auf `logger.debug`.~~
    - ~~**Action:** Done (Implizit durch spätere Schritte).~~

## Phase 2: Analyze & Refactor Service Factory / Core Service Logs

- [x] ~~**Task 2.1: Refactor Service Factory logs**~~
    - ~~**Description:** Überprüfe die `ServiceFactory`. Stufe zu detaillierte `INFO`-Meldungen auf `logger.debug` herab.~~
    - ~~**Action:** Done.~~

## Phase 3: Analyze & Refactor Dashboard Startup Logs

- [x] ~~**Task 3.1: Refactor Dashboard Lifecycle / Controller logs**~~
    - ~~**Description:** Untersuche `DashboardLifecycleService` und `DashboardController`. Stufe Ablauf-Meldungen auf `logger.debug` herab.~~
    - ~~**Action:** Done.~~

## Phase 4: Verification (Intermediate - FAILED)

- [x] ~~**Task 4.1: Deploy and Verify Log Reduction**~~
    - ~~**Action:** Configure, Deploy, Verify Logs. (**Ziel noch NICHT erreicht.** Logs immer noch zu laut).~~

## Phase 5: Fine-Tune Setup & Basic Workflow Init Logs

- [x] ~~**Task 5.1: Refactor `setup_hooks.py` Logs**~~
    - ~~**Description:** Überprüfe `setup_hooks.py` auf `logger.info`-Aufrufe in Schleifen oder für jeden Registrierungsschritt. Ändere auf `logger.debug`.~~
    - ~~**Action:** Done.~~

- [x] ~~**Task 5.2: Refactor Workflow Manager / Basic Initialization Logs**~~
    - ~~**Description:** Finde `Initializing workflow: ...` und `Workflow ... initialized successfully`. Ändere auf `logger.debug`. Behalte übergeordnete `INFO`-Meldung.~~
    - ~~**Action:** Done (in `workflow_manager.py`, `category_workflow.py`, `channel_workflow.py`, `user_workflow.py`, `dashboard_workflow.py`, `guild_template_workflow.py`, `database_workflow.py`, `guild/initialization.py`).~~

- [x] ~~**Task 5.3: Final Review `bot.py` Startup Logs**~~
    - ~~**Description:** Gehe `app/bot/infrastructure/startup/bot.py` durch. Stelle sicher, dass `INFO` nur Top-Level-Phasen markiert.~~
    - ~~**Action:** Done.~~

## Phase 6: Aggressive INFO Reduction (NEW)**

- [ ] **Task 6.1: Refactor GuildWorkflow Initialization Details**
    - **Description:** Ändere die `INFO`-Logs in `app/bot/application/workflows/guild/initialization.py` für "Found X guilds", "Processing status", "Status: APPROVED/SUSPENDED", "Initialization complete" auf `DEBUG`.
    - **Affected Files:**
        - `app/bot/application/workflows/guild/initialization.py`
    - **Action:** Modify code to change log levels.

- [ ] **Task 6.2: Refactor Remaining Workflow Init Start Messages**
    - **Description:** Ändere die verbleibenden `INFO`-Logs, die nur den Start eines Workflows anzeigen (z.B. `Initializing channel workflow`, `Initializing task workflow`, `Initializing user workflow`) auf `DEBUG`. Das eigentliche "initialized successfully" ist bereits DEBUG.
    - **Affected Files:**
        - `app/bot/application/workflows/channel_workflow.py`
        - `app/bot/application/workflows/task_workflow.py`
        - `app/bot/application/workflows/user_workflow.py`
    - **Action:** Modify code to change log levels.

- [ ] **Task 6.3: Refactor User Sync Details**
    - **Description:** Ändere die `INFO`-Logs in `app/bot/application/workflows/user_workflow.py` für die User-Sync-Statistiken (`Synchronized guild...`, `Starting sync of...`, `Guild sync complete:`, `Total members processed`, `Successfully synced`, `Skipped`, `Errors`) auf `DEBUG`.
    - **Affected Files:**
        - `app/bot/application/workflows/user_workflow.py`
    - **Action:** Modify code to change log levels.

- [ ] **Task 6.4: Refactor Component Loading Logs**
    - **Description:** Ändere die `INFO`-Logs in `app/bot/infrastructure/startup/bot.py` (oder wo `load_component_definitions` aufgerufen wird) für "Loading component definitions..." und "Successfully loaded..." auf `DEBUG`.
    - **Affected Files:**
        - `app/bot/infrastructure/startup/bot.py` (vermutlich in `on_ready` oder Service Init)
        - Evtl. `app/bot/application/services/component/component_loader_service.py` oder `app/bot/infrastructure/config/registries/component_registry.py`
    - **Action:** Modify code to change log levels.

- [ ] **Task 6.5: Refactor Dashboard Data Service Init Log**
    - **Description:** Ändere das `INFO`-Log "Dashboard Data Service initialized..." auf `DEBUG`.
    - **Affected Files:**
        - `app/bot/application/services/dashboard/dashboard_data_service.py` (oder wo es initialisiert wird, z.B. `setup_hooks.py`)
    - **Action:** Modify code to change log levels.

- [ ] **Task 6.6: Refactor Internal API Setup Logs**
    - **Description:** Ändere die `INFO`-Logs für "Setting up internal API routes...", "Internal API routes added...", "Internal API server started..." auf `DEBUG`. Behalte nur `ERROR`-Logs für Fehler.
    - **Affected Files:**
        - `app/bot/infrastructure/startup/bot.py` (vermutlich in `setup_internal_api`)
        - `app/bot/interfaces/api/internal/server.py`
    - **Action:** Modify code to change log levels.

- [ ] **Task 6.7: Refactor Dashboard Activation Logs**
    - **Description:** Ändere die `INFO`-Logs in `DashboardLifecycleService` und `DashboardRegistry` für die Aktivierungsschritte (`Ensuring controller is active...`, `Activated '...' dashboard.`) auf `DEBUG`. Behalte nur die abschließende Meldung der `activate_db_configured_dashboards` auf `INFO` (oder ändere sie auch, je nach gewünschtem Detailgrad).
    - **Affected Files:**
        - `app/bot/application/services/dashboard/dashboard_lifecycle_service.py`
        - `app/bot/infrastructure/dashboards/dashboard_registry.py`
    - **Action:** Modify code to change log levels.

## Phase 7: Final Verification (NEW)**

- [ ] **Task 7.1: Deploy and Verify Minimal Log Output**
    - **Description:** Nach Abschluss von Phase 6, setze die Logging-Konfiguration (`log_config.py`) auf `console_level: INFO`. Führe ein Deployment durch und überprüfe die `docker logs foundrycord-bot`. Die Ausgabe sollte **extrem** knapp sein und fast nur noch den "Bot started" / "Logged in as" Log und eventuelle `WARNING`/`ERROR`/`CRITICAL`-Meldungen enthalten.
    - **Affected Files:**
        - `app/shared/application/logging/log_config.py`
    - **Action:** Configure, Deploy, Verify Logs.

---

## Related Documentation

- `docs/3_developer_guides/01_getting_started/logging_guidelines.md`

---

## General Notes / Future Considerations

- **NEUES ZIEL:** Startup auf `INFO`-Level soll fast lautlos sein. `DEBUG` enthält weiterhin alle Details.
- Änderungen sollten weiterhin *nur* das Loglevel betreffen (`logger.info` -> `logger.debug`).
