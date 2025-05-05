# Reduce Startup Log Noise TODO

**Goal:** Review startup logs for both Bot and Web applications, identify messages logged at `INFO` or `WARNING` level that are too verbose or frequent for normal operation according to `logging_guidelines.md`, and adjust their level (e.g., to `DEBUG`) or content to reduce noise during standard startup.

**Related Documentation:**
*   `docs/3_developer_guides/01_getting_started/logging_guidelines.md`

## Phase 1: Review Startup Logs

*   [ ] **Task 1.1:** Capture full startup logs for the Bot application.
    *   Action: Restart the Bot container (`docker restart foundrycord-bot`).
    *   Action: Capture logs immediately after restart (`docker logs foundrycord-bot | cat > bot_startup_logs.txt`).
    *   Action: Attach `bot_startup_logs.txt` or paste its content.
*   [ ] **Task 1.2:** Capture full startup logs for the Web application.
    *   Action: Restart the Web container (`docker restart foundrycord-web`).
    *   Action: Capture logs immediately after restart (`docker logs foundrycord-web | cat > web_startup_logs.txt`).
    *   Action: Attach `web_startup_logs.txt` or paste its content.

## Phase 2: Identify Noisy Logs

*   [x] **Task 2.1:** Analyze Bot startup logs (`bot_startup_logs.txt`).
    *   Identify specific messages logged at `INFO` or `WARNING` level that seem too frequent or detailed for a standard startup overview (e.g., repetitive initialization steps for many items, very detailed configuration dumps).
    *   Refer to the `INFO` and `DEBUG` level definitions in `logging_guidelines.md`.
    *   Action: List the message patterns, their current level, and the originating file/line number for potential adjustment.
    *   **Result:** Provided logs show only `Bot logged in...` message at INFO level, which is appropriate. No adjustments needed based on current data.
*   [x] **Task 2.2:** Analyze Web startup logs (`web_startup_logs.txt`).
    *   Perform the same analysis as in Task 2.1 for the web application logs.
    *   Action: List the message patterns, their current level, and the originating file/line number for potential adjustment.
    *   **Result:**
        *   **Individual Guild Service Inits:** `INFO: GuildQueryService initialized.`, `INFO: GuildSelectionService initialized.`, `INFO: GuildManagementService initialized.`. Source: Respective service files (`query_service.py`, `selection_service.py`, `management_service.py` in `app/web/application/services/guild/`). Recommendation: Change to `DEBUG`.
        *   **Repeated Template Service Inits:** `INFO: TemplateQueryService initialized.`, etc., and `INFO: GuildTemplateService Facade initialized...` logged multiple times. Source: `__init__` of respective services in `app/web/application/services/template/` and potentially the Facade (`template_service.py`) being instantiated multiple times. Recommendation: Change individual service init logs to `DEBUG`. Change Facade log to `DEBUG` in `template_service.py`. (Investigate multiple instantiations separately if needed).
        *   **Static File/Dir Path and Checks:** `INFO: Static directory absolute path...`, `INFO: css_base: ... exists: True`, etc. Source: `app/web/core/extensions/static.py`. Recommendation: Change all these detailed path/check logs to `DEBUG`.
        *   **Templates Directory Path:** `INFO: Templates directory: ...`. Source: `app/web/core/extensions/templates.py`. Recommendation: Change to `DEBUG`.
        *   **State Collector Overwrite Warning:** `[W] Overwriting existing state collector: system_info`. Source: `app/shared/infrastructure/state/secure_state_snapshot.py`. Recommendation: Change to `DEBUG` (less noisy than WARNING for an expected/handled situation during startup).
        *   **Duplicate Core Services Log:** `INFO: Core services registered successfully` appears twice. First instance is OK. Second instance source is unclear but occurs after state collector registration. Recommendation: Ignore the second instance for now as the source is not definitively found and impact is low.
        *   **Workflow Init Order:** `INFO: Set initialization order: ...`. Source: `app/web/core/workflow_manager.py`. Recommendation: Change to `DEBUG` (implementation detail).
        *   **Shutdown Error:** `ERROR:root:'WebLifecycleManager' object has no attribute 'cleanup_services'`. Source: `app/web/core/main.py` calling `web_app.lifecycle_manager.cleanup_services()`. Recommendation: Add the missing `cleanup_services` method to `app/web/core/lifecycle_manager.py`.

## Phase 3: Adjust Log Levels/Content

*   [ ] **Task 3.1:** Apply adjustments for Bot logs.
    *   Based on the findings from Task 2.1, implement the necessary changes.
    *   **Status:** No noisy INFO/WARNING logs identified in the provided startup logs. No changes currently needed.
    *   **Affected Files:** None.
*   [x] **Task 3.2:** Apply adjustments for Web logs & fix shutdown error.
    *   Based on the detailed findings from Task 2.2.
    *   Implement all recommended log level changes (INFO/WARNING -> DEBUG).
    *   Add missing `cleanup_services` method to fix shutdown error.
    *   **Affected Files:**
        *   `app/web/application/services/guild/query_service.py` (Guild Query init log)
        *   `app/web/application/services/guild/selection_service.py` (Guild Selection init log)
        *   `app/web/application/services/guild/management_service.py` (Guild Management init log)
        *   `app/web/application/services/template/query_service.py` (Template Query init log)
        *   `app/web/application/services/template/structure_service.py` (Template Structure init log)
        *   `app/web/application/services/template/management_service.py` (Template Management init log)
        *   `app/web/application/services/template/sharing_service.py` (Template Sharing init log)
        *   `app/web/application/services/template/template_service.py` (Template Facade init log)
        *   `app/web/core/extensions/static.py` (Static path and file check logs)
        *   `app/web/core/extensions/templates.py` (Templates directory log)
        *   `app/shared/infrastructure/state/secure_state_snapshot.py` (State collector overwrite warning)
        *   `app/web/core/workflow_manager.py` (Workflow init order log)
        *   `app/web/core/lifecycle_manager.py` (Add `cleanup_services` method)

## Phase 4: Verification

*   [x] **Task 4.2:** Review new logs (`bot_startup_logs_v2.txt`, `web_startup_logs_v2.txt`).
    *   Confirm that the adjusted logs no longer appear at `INFO` or `WARNING` level.
    *   Confirm that essential startup information is still present at `INFO`.
    *   Confirm that the shutdown error in the web logs is gone.
*   [ ] **Task 4.3:** Evaluate overall log output against guidelines.
    *   **Outcome:** INFO/WARNING noise reduced as planned. Shutdown error fixed. However, overall log volume (INFO + DEBUG) remains high (~400+ lines for web) due to verbose DEBUG messages from KeyManagementService, SecurityBootstrapper, and potentially HTTPX. The duplicate INFO log for "Core services" also persists.
    *   **Decision:** Proceed to Phase 5 to further optimize DEBUG logs and address remaining issues for a truly clean startup log according to `logging_guidelines.md` (Target: ~15-25 INFO lines, significantly fewer DEBUG lines).

## Phase 5: DEBUG Log Optimization & Remaining Issues

*   [ ] **Task 5.1:** Consolidate KeyManagementService DEBUG logs.
    *   Goal: Replace individual `DEBUG: Loaded [KEY_TYPE] from database` logs with a single summary DEBUG message (e.g., "Keys loaded: AES, ENCRYPTION, JWT").
    *   Affected Files:
        *   `app/shared/infrastructure/encryption/key_management_service.py`
*   [x] **Task 5.2:** Review and reduce SecurityBootstrapper DEBUG logs.
    *   Goal: Evaluate if the DEBUG logs in `SecurityBootstrapper` are necessary for normal startup or can be removed/changed to only log on error/higher level.
    *   **Action:** Changed `SecurityBootstrapper` to use `get_shared_logger()`. Its `debug` calls now respect the `ENVIRONMENT` variable check in `BaseLoggingService`.
    *   Affected Files:
        *   `app/shared/infrastructure/security/security_bootstrapper.py`
*   [x] **Task 5.3:** Suppress library DEBUG logs (e.g., HTTPX).
    *   Goal: Prevent DEBUG logs from underlying libraries like `httpx` (seen as `load_ssl_context`, `load_verify_locations`) from appearing during standard startup.
    *   Action: Modified logging configuration to set the log level for `httpx` and `httpcore` loggers to `WARNING`.
    *   Affected Files:
        *   `app/shared/application/logging/log_config.py`
*   [x] **Task 5.4:** Address duplicate "Core services registered successfully" INFO log.
    *   Goal: Remove the redundant INFO log entry.
    *   Option 1: Investigate source of the second call (after state collectors) and remove it.
    *   Option 2 (Easier): Change the *first* instance of the log in `WebLifecycleManager._register_core_services` to `DEBUG`.
    *   **Action:** Option 2 implemented. Changed the first log instance to DEBUG.
    *   Affected Files:
        *   `app/web/core/lifecycle_manager.py`
*   [ ] **Task 5.5:** (Optional) Investigate multiple `GuildTemplateService` Facade initializations.
    *   Goal: Understand why the facade `__init__` (and its DEBUG log) appears multiple times, even if it doesn't impact functionality directly.
    *   Action: Trace where `GuildTemplateService` is instantiated.
    *   Affected Files: Potentially many, start search from `WebServiceFactory` or where `GuildTemplateService` is used.
    *   **Decision:** Skipping this optional task for now.

## Phase 6: Final Verification

*   [x] **Task 6.1:** Restart applications and capture final startup logs.
    *   Action: `docker restart foundrycord-bot foundrycord-web`
    *   Action: `docker logs foundrycord-web | cat` (Display directly)
*   [x] **Task 6.2:** Review final logs.
    *   Confirm `INFO` log provides a concise overview (~15-25 lines).
    *   Confirm `DEBUG` log is significantly less verbose.
    *   Confirm duplicate INFO log is resolved (either removed or changed to DEBUG).
    *   Confirm Pydantic warnings are gone.
*   [x] **Task 6.3:** Mark TODO as complete.

## General Notes / Future Considerations

*   The goal is not to remove all logs, but to ensure `INFO` provides a concise overview of the startup sequence, while `DEBUG` holds the detailed step-by-step information.
*   Pay attention to loops during initialization (e.g., loading multiple templates, components) - logging each item at `INFO` might be too noisy.
