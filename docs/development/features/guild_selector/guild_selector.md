# Guild Selector Feature

## Purpose

The Guild Selector is a navigation component that allows authenticated users (especially owners and potentially admins/moderators) to switch the application's context to a specific Discord server (guild) they have access to. This is crucial for features that operate on a per-guild basis, such as configuration, moderation tools, or viewing guild-specific data.

## Location

The Guild Selector component is located in the main navigation bar, typically on the left side.

## Functionality

1.  **Display Current Guild:** The selector button prominently displays the name and icon of the currently selected guild. This information is retrieved from the user's server-side session.
    *   If no guild is currently selected in the session, a default "Select Server" text and icon are shown.
2.  **Open Dropdown:** Clicking the selector button opens a dropdown menu.
3.  **Fetch Guild List (Dynamic):** Upon opening the dropdown, JavaScript initiates an asynchronous request to the backend API endpoint `GET /api/v1/servers/`.
    *   The backend controller (`GuildSelectorController`) calls a service (`ServerService`) which determines the list of guilds the currently logged-in user has appropriate access to (e.g., based on shared guilds and permissions).
    *   The API returns a list of guilds, typically containing their ID, name, and icon URL (`GuildInfo` schema).
4.  **Populate Dropdown:** The JavaScript receives the list of guilds and dynamically populates the dropdown menu, showing each available guild (usually with icon and name).
5.  **Select Guild:** When the user clicks on a guild in the dropdown:
    *   JavaScript sends the selected `guild_id` via a `POST` request to the backend API endpoint `POST /api/v1/servers/select/{guild_id}`.
    *   The backend controller (`GuildSelectorController` / `ServerService`) verifies if the user has access to the requested `guild_id`.
    *   If access is verified, the backend updates the user's server-side **session**, storing the details (ID, name, icon URL) of the newly selected guild (e.g., in `request.session['selected_guild']`).
6.  **Context Update (Reload):** After the session is updated, the frontend likely performs a full page reload. This ensures that:
    *   The Guild Selector UI in the navbar updates to show the newly selected guild (read from the updated session).
    *   Other parts of the application (backend and frontend) can now read the selected guild from the session and adjust their context or data accordingly.

## Key Components

*   **UI (Template):** `app/web/templates/components/navigation/guild_selector.html` - Defines the HTML structure of the button and dropdown.
*   **Backend API Controller:** `app/web/interfaces/api/rest/v1/guild/selector/guild_selector_controller.py` - Handles API requests for listing available guilds and selecting a guild.
*   **Backend Service:** `ServerService` (obtained via `WebServiceFactory`) - Contains the business logic for fetching accessible guilds for a user and updating the session upon selection.
*   **JavaScript:** (Likely within navbar initialization or a dedicated component script) - Handles dropdown toggling, fetching the guild list via API, populating the dropdown, and triggering the guild selection API call on user interaction.
*   **Session Management:** Server-side sessions are used to persist the user's current guild selection across requests.
*   **CSS:** (Likely `navbar.css` or a specific `guild-selector.css`) - Styles the appearance of the selector button, icon, name, and dropdown.

## Data Flow Summary

1.  Page Load -> Template reads `selected_guild` from session -> Displays current guild.
2.  User clicks selector -> JS fetches guild list from `GET /api/v1/servers/`.
3.  Backend determines accessible guilds for user -> API returns list.
4.  JS populates dropdown.
5.  User clicks a guild -> JS sends `guild_id` to `POST /api/v1/servers/select/{guild_id}`.
6.  Backend verifies access -> Updates `selected_guild` in session.
7.  Frontend reloads page.
