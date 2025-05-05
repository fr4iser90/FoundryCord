# Fix DB Init Script & Update Logging Guidelines TODO

**Goal:** Correct the syntax error observed in the `init-db.sh` script during database initialization and enhance the `logging_guidelines.md` to cover infrastructure component logging (like database, cache).

**Related Documentation:**
*   `docs/3_developer_guides/01_getting_started/logging_guidelines.md`

## Phase 1: Fix Database Initialization Script

*   [x] **Task 1.1:** Analyze `init-db.sh` script.
    *   Action: Read `docker/postgres/init-db.sh`.
    *   Action: Identify the line causing the `ERROR: syntax error at or near "1"`.
    *   **Result:** The error message `DO 1` does not originate from the script itself, but likely an artifact from previous failed initializations. The script syntax appears correct regarding this error.
    *   **Affected Files:**
        *   `docker/postgres/init-db.sh`
*   [x] **Task 1.2:** Correct the syntax error.
    *   Action: Propose an edit to `docker/postgres/init-db.sh` to fix the identified error.
    *   **Result:** No correction needed in the script for the `DO 1` error.
    *   **Affected Files:**
        *   `docker/postgres/init-db.sh`
*   [x] **Task 1.3:** Verify the fix.
    *   Action: Recreate and restart the database container (`docker-compose down foundrycord-db` followed by `docker-compose up -d postgres`).
    *   Action: Check the database logs (`docker logs foundrycord-db | cat`) for the absence of the syntax error.
    *   **Result:** Error did not reappear after clean restart. Confirmed as artifact.

## Phase 2: Update Logging Guidelines

*   [ ] **Task 2.1:** Add Infrastructure Logging section to Guidelines.
    *   Action: Propose an edit to `docs/3_developer_guides/01_getting_started/logging_guidelines.md`.
    *   Action: Add a new section explaining where to find logs for components like Postgres, Redis, etc., and their typical logging levels/purpose (often standard vendor defaults unless specific issues arise). Mention that they are configured separately from the application logging.
    *   **Affected Files:**
        *   `docs/3_developer_guides/01_getting_started/logging_guidelines.md`

## Phase 3: Final Review & Cleanup

*   [ ] **Task 3.1:** Review changes and mark TODO as complete.

## General Notes / Future Considerations

*   Consider if default Postgres/Redis logging levels need adjustment based on future needs (e.g., for performance tuning). 