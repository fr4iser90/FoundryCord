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

*   [ ] **Task 2.1:** Analyze Bot startup logs (`bot_startup_logs.txt`).
    *   Identify specific messages logged at `INFO` or `WARNING` level that seem too frequent or detailed for a standard startup overview (e.g., repetitive initialization steps for many items, very detailed configuration dumps).
    *   Refer to the `INFO` and `DEBUG` level definitions in `logging_guidelines.md`.
    *   Action: List the message patterns, their current level, and the originating file/line number for potential adjustment.
*   [ ] **Task 2.2:** Analyze Web startup logs (`web_startup_logs.txt`).
    *   Perform the same analysis as in Task 2.1 for the web application logs.
    *   Action: List the message patterns, their current level, and the originating file/line number for potential adjustment.

## Phase 3: Adjust Log Levels/Content

*   [ ] **Task 3.1:** Apply adjustments for Bot logs.
    *   Based on the findings from Task 2.1, implement the necessary changes.
    *   Action: Use `edit_file` to change log levels (e.g., `logger.info` to `logger.debug`) or rephrase messages in the identified files.
*   [ ] **Task 3.2:** Apply adjustments for Web logs.
    *   Based on the findings from Task 2.2, implement the necessary changes.
    *   Action: Use `edit_file` to change log levels or rephrase messages in the identified files.

## Phase 4: Verification

*   [ ] **Task 4.1:** Restart both Bot and Web applications.
    *   Action: `docker restart foundrycord-bot foundrycord-web`
*   [ ] **Task 4.2:** Capture new startup logs.
    *   Action: `docker logs foundrycord-bot | cat > bot_startup_logs_after.txt`
    *   Action: `docker logs foundrycord-web | cat > web_startup_logs_after.txt`
*   [ ] **Task 4.3:** Verify noise reduction.
    *   Review the new logs (`*_after.txt`).
    *   Confirm that the previously identified noisy logs no longer appear at `INFO`/`WARNING` level (unless deemed appropriate after review) and the overall startup sequence is clearer.

## General Notes / Future Considerations

*   The goal is not to remove all logs, but to ensure `INFO` provides a concise overview of the startup sequence, while `DEBUG` holds the detailed step-by-step information.
*   Pay attention to loops during initialization (e.g., loading multiple templates, components) - logging each item at `INFO` might be too noisy.
