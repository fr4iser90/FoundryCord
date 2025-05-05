# Refactor Bot Logging TODO

**Goal:** Refactor bot logging for improved clarity, usefulness, and reduced noise, focusing on critical information, errors, and key workflow steps.

---

## Phase 1: Analysis & Strategy Definition

- [x] ~~**Task 1.1: Analyze Current Logging Output & Identify Issues**~~
    - ~~**Description:** Review recent bot logs (`docker logs foundrycord-bot | cat`) to identify:~~
        - ~~Areas with excessive INFO/DEBUG noise (e.g., repetitive messages, overly verbose loops).~~
        - ~~Missing critical information (e.g., lack of context in error messages, unclear workflow transitions).~~
        - ~~Inconsistent formatting or log levels across modules.~~
    - ~~**Affected Files (Initial):**~~
        - ~~`app/shared/infrastructure/logging/services/base_logging_service.py`~~
        - ~~`app/shared/infrastructure/logging/services/bot_logging_service.py`~~
        - ~~`app/shared/application/logging/log_config.py` (To be investigated)~~
        - ~~Modules currently generating noise (e.g., `dashboard_controller`, `dashboard_registry`, `system_collector`)~~
    - ~~**Action:** Logs reviewed. Initial noise reduction implemented by changing INFO -> DEBUG for repetitive tasks.~~

- [x] ~~**Task 1.2: Define Logging Strategy & Standards**~~
    - ~~**Description:** Based on the analysis, define clear standards for log levels (when to use DEBUG, INFO, WARNING, ERROR, CRITICAL), message formatting (e.g., including relevant IDs, workflow steps), and context data. Document these standards (e.g., in `docs/3_developer_guides/01_getting_started/coding_conventions.md` or a new logging guide).~~
    - ~~**Affected Files:** Documentation files, potentially `log_config.py`.~~
    - ~~**Action:** Created `docs/3_developer_guides/01_getting_started/logging_guidelines.md` with the defined strategy.~~

---

## Phase 2: Implementation

- [x] **Task 2.1: Refactor Noisy Modules**
    - **Description:** Identify the modules producing the most DEBUG/INFO noise and refactor their logging calls according to the new standards. Reduce verbosity where appropriate, ensuring essential information remains.
    - **Affected Files:** Modules identified in Task 1.1.
    - **Action:** Initial refactoring done by changing repetitive INFO logs to DEBUG in key modules (`dashboard_controller`, `dashboard_registry`, `system_collector`). Further review can be done if needed.

- [x] ~~**Task 2.2: Enhance Error Logging Context**~~
    - ~~**Description:** Review error handling (`try...except` blocks) and `logger.error`/`logger.exception`/`logger.critical` calls. Ensure sufficient context (e.g., relevant variables, user IDs, guild IDs, operation being attempted) is included in error messages or context dictionary.~~
    - ~~**Affected Files:** Various modules, `base_logging_service.py`.~~
    - ~~**Action:** Reviewed `DashboardController` (`initialize` logs further refined), `DashboardLifecycleService`, and monitoring hardware collectors (`system/components/hardware/`). Added missing context (IDs) and ensured `exc_info=True` where appropriate. Other modules may still need review.~~

- [ ] **Task 2.3: Implement Standardized Workflow Logging (Partial)**
    - **Description:** Implement consistent logging patterns for key workflows (e.g., dashboard activation, command execution, user synchronization). Log start, key steps, success, and failure points with clear, standardized messages.
    - **Affected Files:** Workflow implementation files (`app/bot/application/workflows/`).
    - **Action:** Standardized logging for User Sync, Database, Guild Template, and Guild workflows (including sub-modules like sync, approval, template application). Other workflows (e.g., Commands, Dashboard) may need review.

- [x] ~~**Task 2.4: Review and Adjust Configuration**~~
    - ~~**Description:** Review the logging configuration (`log_config.py`?) to ensure appropriate default levels, formatters, and handler settings (e.g., memory buffer flush level).~~
    - ~~**Affected Files:** `app/shared/application/logging/log_config.py` (or equivalent), `db_handler.py`.~~
    - ~~**Action:** Reviewed `log_config.py`. Set root logger level to DEBUG, removed unused variable, and changed memory handler flush level to ERROR for better debug/error visibility.~~

---

## Phase 3: Testing & Verification

- [x] ~~**Task 3.1: Test Logging Output**~~
    - ~~**Description:** Deploy the changes and observe the bot's log output (using `docker logs foundrycord-bot | cat`). Verify:~~
        - ~~Reduced noise at INFO level.~~
        - ~~Key workflow steps logged appropriately.~~
        - ~~Errors (if any) provide sufficient context and traceback.~~
        - ~~Consistent formatting.~~
    - ~~**Action:** Deployed and verified. INFO level is much cleaner. Key events are logged. Error context improvements applied but not tested under error conditions. Formatting is consistent.~~

- [ ] **Task 3.2: Final Review & Documentation Update**
    - **Description:** Ensure any new or updated logging standards are fully documented for developers.
    - **Affected Files:** Documentation files.

---

## Related Documentation

-   `app/shared/infrastructure/logging/services/base_logging_service.py`
-   `app/shared/infrastructure/logging/services/bot_logging_service.py`
-   `app/shared/infrastructure/logging/handlers/db_handler.py`

---

## General Notes / Future Considerations

-   Focus on reducing DEBUG noise.
-   Improve error context (e.g., ensure relevant variables, IDs are included).
-   Standardize log messages, potentially on a per-workflow or per-module basis.
-   Consider log aggregation/analysis tools in the future.
-   Evaluate performance impact of DB logging, potentially adjusting sampling or queueing.
