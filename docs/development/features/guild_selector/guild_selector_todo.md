# Guild Selector Feature TODO

## Phase 1: Consistency & Persistence

- [ ] **Renaming:** Rename instances of "server"/"servers" to "guild"/"guilds" for consistency.
    - **Affected Files (Check Context Carefully, includes file/directory renames):**
        - **Python (Backend):**
            - `app/web/application/services/server/server_service.py` (Rename to `GuildService`?)
            - `app/web/interfaces/api/rest/v1/guild/selector/guild_selector_controller.py` (API route `/servers/` -> `/guilds/`)
            - `app/web/infrastructure/factories/service/web_service_factory.py`
            - `app/web/interfaces/api/rest/v1/schemas/guild_schemas.py` (Check schema names like `GuildInfo`)
            - `app/web/interfaces/api/rest/v1/owner/server_management_controller.py` (Rename to `guild_management_controller.py`?, route /owner/servers -> /owner/guilds)
            - `app/web/interfaces/web/views/owner/server_management_view.py` (Rename to `guild_management_view.py`?)
        - **HTML (Templates):**
            - `app/web/templates/components/navigation/guild_selector.html` (CSS classes: `server-icon`, `server-name`, `server-list`)
            - `app/web/templates/views/owner/control/` (Directory rename to `guild_control`?)
                - `add-server-modal.html` -> `add-guild-modal.html`?
                - `server-actions.html` -> `guild-actions.html`?
                - `server-details.html` -> `guild-details.html`?
                - `server-list.html` -> `guild-list.html`?
            - `app/web/templates/views/owner/control/index.html` (Template includes)
            - `app/web/templates/views/owner/state-monitor.html` (Check usage)
        - **JavaScript (Frontend):**
            - `app/web/static/js/components/guildSelector.js` (API calls to `/servers/`, CSS selectors, variable names)
            - `app/web/static/js/views/owner/control/serverManagement.js` (Rename to `guildManagement.js`? API calls to `/owner/servers`)
        - **CSS:**
            - `app/web/static/css/components/guild-selector.css` (Selectors: `.server-list`, `.server-list-item`, `.server-icon`, etc.; CSS Vars?)
            - `app/web/static/css/components/navbar.css` (Selectors: `.server-selector`, `.server-icon`)
            - `app/web/static/css/themes/*.css` (CSS Variables: `--server-selector-*`, `--server-icon-*`)
            - `app/web/static/css/views/owner/bot_control.css` (Rename to `guild_control.css`? Selectors: `.server-section`, `.server-list-table`, `.server-actions`, `.server-info-grid`, etc.)
        - **Documentation:**
            - `docs/development/features/guild_selector/guild_selector.md`
- [ ] **Persistence:** Implement logic to persist the user's last selected guild beyond the current session.
    - [ ] **Backend:** Add a `last_selected_guild_id` field to the user model/database.
    - [ ] **Backend:** Update the `select_server` logic (`POST /select/{guild_id}`) to store the selected ID in both the session AND the user's `last_selected_guild_id` field in the DB.
    - [ ] **Backend:** Update the logic for determining the initially displayed guild (e.g., in `get_current_server` or upon login) to prioritize the `last_selected_guild_id` from the DB over the session, falling back to the session, and only showing "Select Guild" if neither is available/valid.
- [ ] **Documentation:** Update `guild_selector.md` to reflect the renaming and persistence changes.
