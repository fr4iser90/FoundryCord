# Guild Selector Feature TODO

**Goal:** Ensure consistent naming convention ("guild" instead of "server") throughout the codebase and UI related to the guild selector, and implement persistence for the user's last selected guild across sessions.

**Related Documentation (Optional):**
*   `docs/development/features/guild_selector/guild_selector.md` (Needs update after refactoring)

## Phase 1: Consistency & Persistence

*   [ ] **Task 1: Rename "server" to "guild"**: Ensure consistency across files and directories.
    *   **Affected Files:** (Check context carefully during rename)
        *   **Python (Backend):**
            *   `app/web/application/services/server/server_service.py` -> `GuildService`?
            *   `app/web/interfaces/api/rest/v1/guild/selector/guild_selector_controller.py` (API route `/servers/` -> `/guilds/`)
            *   `app/web/infrastructure/factories/service/web_service_factory.py`
            *   `app/web/interfaces/api/rest/v1/schemas/guild_schemas.py` (Check schema names)
            *   `app/web/interfaces/api/rest/v1/owner/server_management_controller.py` -> `guild_management_controller.py`? (route `/owner/servers` -> `/owner/guilds`)
            *   `app/web/interfaces/web/views/owner/server_management_view.py` -> `guild_management_view.py`?
        *   **HTML (Templates):**
            *   `app/web/templates/components/navigation/guild_selector.html` (CSS classes)
            *   `app/web/templates/views/owner/control/` (Directory rename?) -> `guild_control`?
                *   `add-server-modal.html` -> `add-guild-modal.html`?
                *   `server-actions.html` -> `guild-actions.html`?
                *   `server-details.html` -> `guild-details.html`?
                *   `server-list.html` -> `guild-list.html`?
            *   `app/web/templates/views/owner/control/index.html` (Template includes)
            *   `app/web/templates/views/owner/state-monitor.html` (Check usage)
        *   **JavaScript (Frontend):**
            *   `app/web/static/js/components/guildSelector.js` (API calls, CSS selectors, variables)
            *   `app/web/static/js/views/owner/control/serverManagement.js` -> `guildManagement.js`? (API calls)
        *   **CSS:**
            *   `app/web/static/css/components/guild-selector.css` (Selectors, CSS Vars?)
            *   `app/web/static/css/components/navbar.css` (Selectors)
            *   `app/web/static/css/themes/*.css` (CSS Variables)
            *   `app/web/static/css/views/owner/bot_control.css` -> `guild_control.css`? (Selectors)
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
