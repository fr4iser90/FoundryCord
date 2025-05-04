# Guild Selector Feature TODO

**Goal:** Ensure consistent naming convention ("guild" instead of "server") throughout the codebase and UI related to the guild selector, and implement persistence for the user's last selected guild across sessions.

**Related Documentation (Optional):**
*   `docs/development/features/guild_selector/guild_selector.md` (Needs update after refactoring)

## Phase 1: Consistency & Persistence

*   [x] **Task 1: Rename "server" to "guild"**: Ensure consistency across files and directories.
    *   ~~**Affected Files:** (Checked/Renamed)~~ *(Original detailed list removed for brevity)*
*   [ ] **Task 2: Implement Selection Persistence**: Persist the user's last selected guild beyond the current session.
    *   [ ] **Sub-Task 2.1:** Add `last_selected_guild_id` field to user model/DB.
        *   **Affected Files:**
            *   `app/shared/infrastructure/models/auth/user.py` (Verify path)
            *   (New Alembic migration file)
    *   [ ] **Sub-Task 2.2:** Update guild selection logic to store ID in session AND DB.
        *   **Affected Files:**
            *   `app/web/interfaces/api/rest/v1/guild/selector/guild_selector_controller.py` (Logic for `POST /select/{guild_id}` or similar)
            *   `app/web/application/services/guild/guild_service.py` (Or relevant service handling selection)
    *   [ ] **Sub-Task 2.3:** Update logic for determining initial guild display (prioritize DB > Session > Default).
        *   **Affected Files:**
            *   (Logic related to user login or initial page load, potentially in auth service or main view controller)
*   [ ] **Task 3: Update Documentation**: Update relevant documentation to reflect renaming and persistence changes.
    *   **Affected Files:**
        *   `docs/development/features/guild_selector/guild_selector.md`

## General Notes / Future Considerations

*   [ ] Consider potential impact of renaming on existing database entries or configurations if applicable.
*   [ ] Ensure thorough testing after renaming and persistence implementation.
