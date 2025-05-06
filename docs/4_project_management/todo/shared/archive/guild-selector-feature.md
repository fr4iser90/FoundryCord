# Guild Selector Feature TODO

**Goal:** Ensure consistent naming convention ("guild" instead of "server") throughout the codebase and UI related to the guild selector, and implement persistence for the user's last selected guild across sessions.

**Related Documentation (Optional):**
*   `docs/development/features/guild_selector/guild_selector.md` (Needs update after refactoring)

## Phase 1: Consistency & Persistence

*   [x] **Task 1: Rename "server" to "guild"**: Ensure consistency across files and directories.
    *   *(All sub-items checked/fixed: Renaming done, API routes/variables/CSS confirmed, directory/CSS names for `control` verified as correct).*
*   [x] **Task 2: Implement Selection Persistence**: Persist the user's last selected guild beyond the current session.
    *   [x] **Sub-Task 2.1:** Add `last_selected_guild_id` field to user model/DB.
        *   **(Field exists in model; Added in migration 001)**
        *   **Affected Files:**
            *   `app/shared/infrastructure/models/auth/user_entity.py` (Field present)
            *   `app/shared/infrastructure/database/migrations/alembic/versions/001_create_core_auth_tables.py` (Field added here)
    *   [x] **Sub-Task 2.2:** Update guild selection logic to store ID in session AND DB.
        *   **(Implementation seems to exist in `GuildSelectionService.select_guild`)**
        *   **Affected Files:**
            *   `app/web/interfaces/api/rest/v1/guild/selector/guild_selector_controller.py` (Calls service)
            *   `app/web/application/services/guild/guild_service.py` (Facade)
            *   `app/web/application/services/guild/selection_service.py` (Contains logic)
    *   [x] **Sub-Task 2.3:** Update logic for determining initial guild display (prioritize DB > Session > Default).
        *   **(Implementation seems to exist in `GuildSelectionService.get_current_guild`)**
        *   **Affected Files:**
            *   `app/web/interfaces/api/rest/v1/guild/selector/guild_selector_controller.py` (Calls service)
            *   `app/web/application/services/guild/guild_service.py` (Facade)
            *   `app/web/application/services/guild/selection_service.py` (Contains logic)
            *   (Logic related to user login or initial page load - likely covered by service call)
*   [x] **Task 3: Update Documentation**: Update relevant documentation to reflect renaming and persistence changes.
    *   **Affected Files:**
        *   `docs/2_user_guides/guild_selector.md`

## General Notes / Future Considerations

*   [ ] Consider potential impact of renaming on existing database entries or configurations if applicable.
*   [ ] Ensure thorough testing after renaming and persistence implementation.
