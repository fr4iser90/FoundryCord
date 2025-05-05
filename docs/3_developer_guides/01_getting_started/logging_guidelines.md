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

---

# Web Application Logging Guidelines

**Goal:** Ensure consistent, useful, and appropriately detailed logging across the web application (`app/web`), complementing the bot guidelines.

---

## Logging Levels (Web Context)

Use the standard Python logging levels with the following semantics specific to the web application:

-   **`DEBUG`:** Detailed information for diagnosing specific web requests or internal processes.
    -   *Web Examples:* Request received with headers (sanitized), response details (status code, key headers), entering/exiting specific middleware steps, detailed database query parameters/results (sanitized), arguments passed to service methods called by API endpoints, intermediate results in complex endpoint logic.
    -   *Goal:* Provide fine-grained tracing for web request handling and background tasks triggered via web, filtered out in production by default.

-   **`INFO`:** High-level information about the web server's operation and key events.
    -   *Web Examples:* Web server started/stopped, successful user authentication/login/logout, significant user actions completed via API (e.g., "Dashboard config saved by User 123 for Guild 456", "Template X applied by User 123"), critical service initialization (e.g., LifecycleManager stages), successful completion of background tasks initiated via web (if applicable). *Maybe* log successful request completion (e.g., `Request completed: GET /path -> 200`) but consider sampling or using DEBUG for high-volume endpoints in production.
    -   *Goal:* Provide an overview of server state, user activity, and major API interactions.

-   **`WARNING`:** Indicates potential issues or expected client-side errors that don't indicate a server failure.
    -   *Web Examples:* Authentication required/failed (401/403 responses), resource not found (404 responses triggered by client request), request validation errors (400/422 responses), rate limiting triggered for an IP/user, failed optional external API calls handled gracefully, usage of deprecated API endpoints.
    -   *Goal:* Alert to expected error conditions (often client-induced), non-critical deviations, or potential misuse.

-   **`ERROR`:** An error occurred on the server-side that prevented a specific request from completing successfully (typically leading to a 5xx response).
    -   *Web Examples:* Unhandled exception within an API endpoint handler, failed critical database operation needed for the request, failed required external API call, errors during background task processing initiated by the web.
    -   *Goal:* Indicate specific server-side failures for requests that need investigation.

-   **`CRITICAL`:** A severe error occurred threatening the web server's stability or core functionality.
    -   *Web Examples:* Failure during critical web server startup (DB connection, LifecycleManager init), unrecoverable error in core middleware affecting all requests, critical resource exhaustion (DB connections, memory), uncaught exceptions in the main web server process.
    -   *Goal:* Indicate serious problems requiring immediate attention to the web service.

---

## Message Formatting & Context (Web)

-   **Standard Prefix:** Include relevant context for web requests. If a request correlation ID mechanism is implemented (e.g., via middleware), include it. Always include User ID (if authenticated) and relevant entity IDs.
    -   *Examples:* `[Req:abc123] [User:123] GET /api/v1/guilds/456/config`, `[User:123] Authentication successful`, `[Guild:456] [Dashboard:789] Update failed`
    -   *Implementation:* Use FastAPI dependencies or middleware to access request state and user information.

-   **Clarity:** Same as bot: concise, clear English messages.

-   **Error Context (5xx):** `ERROR` and `CRITICAL` level logs for server errors **MUST** include context.
    -   Use `logger.exception(...)` or `exc_info=True` for tracebacks.
    -   Include: Request method, request path, User ID (if available), relevant entity IDs from the path/payload, potentially *sanitized* headers or query parameters.
    -   **DO NOT LOG SENSITIVE DATA:** Raw Authorization headers (Bearer tokens), passwords from request bodies, full cookies, API keys, full sensitive request bodies.

-   **Client Error Context (4xx):** `WARNING` or `INFO` logs for client errors should include enough context to understand the client's mistake (e.g., path requested for 404, validation error details for 422).

-   **Request Lifecycle Logging:** Consider logging request start (`DEBUG` or `INFO`) and finish (`DEBUG` for success, `INFO`/`WARNING` for 4xx, `ERROR`/`CRITICAL` for 5xx).

---

## Implementation Notes (Web)

-   Leverage the shared logging service (`app.shared.interface.logging.api.get_web_logger`).
-   Implement FastAPI middleware to inject request IDs and potentially user context into logs automatically.
-   Configure Uvicorn access logs separately if needed, focusing application logs on business logic and errors.
-   Review logging configuration to set appropriate levels (e.g., `INFO` for console in production, potentially `DEBUG` to a file/database).

---

# Infrastructure Component Logging

Beyond the Bot and Web applications, other services like the PostgreSQL database and Redis cache generate their own logs.

-   **Location:** These logs are typically viewed using `docker logs <container_name>` (e.g., `docker logs foundrycord-db`, `docker logs foundrycord-cache`).
-   **Configuration:** Their logging behavior (level, format, rotation) is configured separately, often through their own configuration files or environment variables passed via `docker-compose.yml`. They do **not** use the application's `log_config.py`.
-   **Typical Level:** Standard vendor defaults (often similar to `INFO`) are usually sufficient for production unless specific performance tuning or deep troubleshooting is required. Focus application logging efforts on the Bot and Web components first.
-   **Interpretation:** Understand the standard log messages for each component (e.g., Postgres checkpoints, Redis persistence events) to distinguish normal operation from potential issues. 