# Secure Key Loading Fix TODO

**Goal:** Investigate and fix the failure in loading the `JWT_SECRET_KEY` (and potentially other keys like `AES_KEY`, `ENCRYPTION_KEY`) from the database during application startup, allowing the removal of the insecure fallback key in `AuthenticationService`.

**Related Documentation:**

*   `docs/3_developer_guides/02_architecture/database_schema.md` (Potentially relevant for key storage table)
*   `app/shared/infrastructure/database/migrations/alembic/versions/001_create_core_auth_tables.py` (Or similar migration for key table)

## Phase 1: Analyze Key Loading Failure

*   [x] **Task 1.1:** Verify Database Schema & Key Storage.
    *   Confirm the table used for storing keys (e.g., `security_keys`).
    *   Check the schema definition in the relevant migration file.
    *   Manually inspect the database (if possible) to confirm keys exist and are stored correctly after initial generation/seeding.
*   [x] **Task 1.2:** Debug Database Session in Key Loading.
    *   Analyze `KeyManagementService.initialize()`.
    *   Verify the `session` object obtained from `self.session_factory()` or `DatabaseService.get_session()` is valid and active when passed to `KeyRepositoryImpl`.
    *   Add temporary logging inside `KeyManagementService.initialize()` before and after getting the session and calling the repository to trace its state.
*   [x] **Task 1.3:** Examine Key Repository Implementation.
    *   Review the code for `KeyRepositoryImpl.get_jwt_secret_key()` (and methods for other keys if needed).
    *   Extract the exact SQL query being executed.
    *   Test this query directly against the database to ensure it returns the expected key.
*   [x] **Task 1.4:** Review Startup Sequence & Initialization Timing.
    *   Analyze `app/shared/infrastructure/startup/bootstrap.py` and related entry points (`web_entrypoint.py`, `bot_entrypoint.py`).
    *   Determine exactly when `KeyManagementService.initialize()` is called relative to database initialization, session factory setup, and migrations.
    *   Look for potential race conditions or scenarios where the database might not be fully ready when key loading is attempted.

## Phase 2: Implement Fix

*   [x] **Task 2.1:** Based on the analysis from Phase 1, implement the necessary code changes to ensure the `KeyManagementService` reliably loads keys from the database via the `KeyRepositoryImpl`.
    *   This might involve fixing the repository query, adjusting the initialization order, correcting session handling, or addressing other identified issues.

## Phase 3: Verification & Cleanup

*   [x] **Task 3.1:** Remove the temporary fallback logic for `self.jwt_secret` from `AuthenticationService.initialize()`.
*   [x] **Task 3.2:** Restart the application (both Bot and Web if applicable) multiple times to ensure keys are consistently loaded from the database without errors or warnings.
*   [ ] **Task 3.3:** Test the functionality that depends on these keys (e.g., user login/authentication for JWT key).
*   [ ] **Task 3.4:** Remove any temporary logging added during debugging.

## General Notes / Future Considerations

*   **Primary Goal Achieved:** Hardcoded fallback key in `AuthenticationService` removed.
*   **Current Workflow:** `KeyManagementService` now implements a 'load or generate' strategy for `jwt_secret` and `encryption_key`. It attempts to load keys from the database (`security_keys` table). If not found, it generates them, saves them to the database, and then uses them. This makes the system robust against an empty or initially unconfigured `security_keys` table.
*   **Remaining Fallbacks (Intended Behavior):**
    *   **Database Credentials:** `DatabaseCredentialManager` tries to load DB credentials (`POSTGRES_HOST`, `APP_DB_USER`, `APP_DB_PASSWORD`, etc.) from its repository. If that fails, it falls back to **environment variables.** This fallback is **necessary and intended** for establishing the initial DB connection. These environment variables should **not** be removed.
    *   **General Configuration:** `EnvManager` loads environment variables first, then attempts to override them with values from the database. If DB loading fails, the environment variables are used. This fallback is also **intended** for flexibility and initial setup. No specific secret fallbacks need removal here.
*   **Conclusion on Removals:** Relying on environment variables for *database connection* and potentially for *base/default application configuration* is expected. No other unintended hardcoded secret fallbacks were identified in the core key/config loading paths.
*   **Potential Improvement:** The `EncryptionService` currently creates its own instances of `KeyManagementService` and `KeyRepository`. This should be refactored to use dependency injection (e.g., from a central manager like `WebLifecycleManager`) to ensure consistency, efficiency, and clarity on which keys (`current_key`, `encryption_key`, `aes_key`) are used.
*   Consider if error handling within `KeyManagementService.initialize()` needs improvement (e.g., should it raise a more specific exception to halt startup if keys are absolutely required?).
