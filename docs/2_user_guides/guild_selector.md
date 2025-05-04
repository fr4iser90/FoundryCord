# Guild Selector Feature

## Purpose

The Guild Selector is a navigation component that allows authenticated users (especially owners and potentially admins/moderators) to switch the application's context to a specific Discord guild they have access to. This is crucial for features that operate on a per-guild basis, such as configuration, moderation tools, or viewing guild-specific data.

## Location

The Guild Selector component is located in the main navigation bar, typically on the left side.

## Functionality

1.  **Display Current Guild:** The selector button prominently displays the name and icon of the currently selected guild. 
    *   When the page loads, the system first checks the user's server-side session for a selected guild.
    *   If no guild is found in the session, it checks the user's `last_selected_guild_id` stored in their database profile.
    *   If a valid guild ID is found in either the session or the database field, the corresponding guild's details (name, icon) are fetched and displayed.
    *   If no guild is selected in the session and no valid last selection is stored in the database, a default "Select Guild" text and icon are shown.
2.  **Open Dropdown:** Clicking the selector button opens a dropdown menu.
3.  **Fetch Guild List (Dynamic):** Upon opening the dropdown, JavaScript initiates an asynchronous request to the backend API endpoint `GET /api/v1/guilds/`.
    *   The backend controller (`GuildSelectorController`) calls a service (`GuildService` -> `GuildSelectionService`) which determines the list of guilds the currently logged-in user has appropriate access to (only approved guilds).
    *   The API returns a list of guilds, typically containing their ID, name, and icon URL (`GuildInfo` schema).
4.  **Populate Dropdown:** The JavaScript receives the list of guilds and dynamically populates the dropdown menu, showing each available guild (usually with icon and name).
5.  **Select Guild:** When the user clicks on a guild in the dropdown:
    *   JavaScript sends the selected `guild_id` via a `POST` request to the backend API endpoint `POST /api/v1/guilds/select/{guild_id}`.
    *   The backend (`GuildSelectorController` -> `GuildService` -> `GuildSelectionService`) verifies if the user has access to the requested `guild_id`.
    *   If access is verified, the backend updates the user's server-side **session**, storing the details (ID, name, icon URL) of the newly selected guild (e.g., in `request.session['selected_guild']`).
    *   Simultaneously, the backend updates the `last_selected_guild_id` field in the user's database profile (`AppUserEntity`) with the selected `guild_id`.
6.  **Context Update (Reload/Partial):** After the session and database are updated, the frontend might perform a full page reload or, depending on the page structure, update relevant components dynamically. This ensures that:
    *   The Guild Selector UI in the navbar updates to show the newly selected guild.
    *   Other parts of the application (backend and frontend) can now read the selected guild from the session (or database fallback) and adjust their context or data accordingly.
    *   The selection will persist across browser sessions due to the database update.

## Key Components

*   **UI (Template):** `app/web/templates/components/navigation/guild_selector.html` - Defines the HTML structure.
*   **Backend API Controller:** `app/web/interfaces/api/rest/v1/guild/selector/guild_selector_controller.py` - Handles API requests.
*   **Backend Service Facade:** `app/web/application/services/guild/guild_service.py` - Delegates to specific services.
*   **Backend Selection Service:** `app/web/application/services/guild/selection_service.py` - Contains the business logic for fetching accessible guilds, retrieving the current selection (from session or DB), and updating both session and `last_selected_guild_id` in the DB upon selection.
*   **Database Model:** `app/shared/infrastructure/models/auth/user_entity.py` - Contains the `last_selected_guild_id` field.
*   **JavaScript:** `app/web/static/js/components/guildSelector.js` - Handles UI interactions and API calls.
*   **Session Management:** Server-side sessions store the current selection for immediate access during a session.
*   **CSS:** `app/web/static/css/components/guild-selector.css`, `app/web/static/css/components/navbar.css` - Styles the component.

## Data Flow Summary

1.  Page Load -> Backend checks session, then `user.last_selected_guild_id` -> Fetches guild details -> Template displays current guild.
2.  User clicks selector -> JS fetches guild list from `GET /api/v1/guilds/`.
3.  Backend determines accessible guilds for user -> API returns list.
4.  JS populates dropdown.
5.  User clicks a guild -> JS sends `guild_id` to `POST /api/v1/guilds/select/{guild_id}`.
6.  Backend verifies access -> Updates `selected_guild` in session -> Updates `last_selected_guild_id` in DB.
7.  Frontend might reload page or update dynamically.
8.  On next login/session, step 1 uses the stored `last_selected_guild_id` if session is empty.
