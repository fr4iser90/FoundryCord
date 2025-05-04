# Bot Logging Guidelines

**Goal:** Ensure consistent, useful, and appropriately detailed logging across the bot application.

---

## Logging Levels

Use the standard Python logging levels with the following semantics:

-   **`DEBUG`:** Detailed information for diagnosing specific problems during development or troubleshooting. Suitable for high-volume, low-level details.
    -   *Examples:* Repetitive loop iterations (dashboard refresh, collector steps), detailed diagnostic messages (`[DIAGNOSTIC ...]`), function entry/exit points for complex flows, intermediate calculation results, data structures being passed between components (use sparingly).
    -   *Goal:* Provide fine-grained tracing when needed, but expect these to be filtered out in production by default.

-   **`INFO`:** High-level information about the bot's normal operation and key lifecycle events. Should be relatively low volume in production.
    -   *Examples:* Bot started/stopped/reconnected, workflow started/completed successfully (e.g., "Dashboard activation complete for ID: 1", "User sync started for Guild 123", "User sync finished for Guild 123"), significant configuration changes loaded, user actions successfully processed (e.g., "Command /xyz executed successfully by User 123"), service initialization/startup messages.
    -   *Goal:* Provide a general overview of the bot's state and major activities.

-   **`WARNING`:** Indicates potential issues or unexpected situations that don't necessarily prevent the current operation from completing but might require attention or indicate a potential future problem.
    -   *Examples:* Component/service not found but handled gracefully (e.g., fallback used), rate limiting triggered, optional configuration missing, deprecated function usage, failed operations that are recoverable or have defined fallbacks (e.g., failed to fetch optional external data).
    -   *Goal:* Alert developers/administrators to non-critical problems or deviations from the norm.

-   **`ERROR`:** An error occurred that prevented a specific operation/task from completing, but the bot can likely continue running other tasks.
    -   *Examples:* Failed to process a command due to an internal error, failed database operation (that doesn't halt the bot), failed API call to an external service, unexpected exception caught during a specific workflow step.
    -   *Goal:* Indicate specific functional failures that need investigation.

-   **`CRITICAL`:** A severe error occurred that might prevent the bot from continuing stable operation or indicates a major failure requiring immediate attention.
    -   *Examples:* Failure during critical startup/initialization, unrecoverable database connection loss, critical component failure, uncaught exceptions in main loops.
    -   *Goal:* Indicate serious problems that threaten the bot's stability or core functionality.

---

## Message Formatting & Context

-   **Standard Prefix:** Where applicable, include relevant context IDs in the log message prefix for easier filtering and correlation. Use a consistent format like `[Scope:ID]` or `[Type:ID]`.
    -   *Examples:* `[Dashboard:1]`, `[Guild:12345]`, `[User:67890]`, `[Command:/status]`
    -   *Implementation:* This might require helper functions or passing context to the logger.

-   **Clarity:** Messages should be concise and clearly state what happened. Use English. Avoid overly technical jargon unless necessary (especially for INFO/WARNING levels).

-   **Error Context:** `ERROR` and `CRITICAL` level logs **MUST** include sufficient context to diagnose the problem.
    -   Use `logger.exception(...)` or pass `exc_info=True` to `logger.error(...)`/`logger.critical(...)` when logging caught exceptions to automatically include the traceback.
    -   Include relevant variables in the message or as extra data if using structured logging (e.g., relevant IDs, input data snippets, current state variables). **AVOID LOGGING SENSITIVE DATA (tokens, passwords, raw user messages).**

-   **Workflow Logging:** For key workflows (e.g., dashboard activation, guild sync, command execution), log the start and successful/failed end points at `INFO` level. Log key intermediate steps at `DEBUG` level if needed for tracing.
    -   *Example:* `INFO: [Guild:123] Starting user synchronization...` -> `DEBUG: [Guild:123] Fetched 50 members.` -> `INFO: [Guild:123] User synchronization complete.`

---

## Implementation Notes

-   Leverage the shared logging service (`app.shared.interface.logging.api.get_bot_logger`).
-   Consider adding context automatically via LogRecord attributes or Filters if feasible.
-   Review `app/shared/application/logging/log_config.py` (or equivalent) to set appropriate default levels for handlers (e.g., StreamHandler at INFO, FileHandler/DBHandler potentially at DEBUG initially, adjustable via config). 