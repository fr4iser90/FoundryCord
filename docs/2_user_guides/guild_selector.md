# User Guide: Guild Selector

## Purpose

The Guild Selector is a key navigation component in the FoundryCord web interface. It allows you, as an authenticated user, to easily switch the application's context to a specific Discord server (guild) that you have access to through FoundryCord. This is essential for managing guild-specific settings, designing server structures, viewing dashboards, or using any other feature that operates on a per-guild basis.

This guide explains how the Guild Selector works and how to use it.

## Location

The Guild Selector component is usually found in the main navigation bar of the FoundryCord web interface, often towards the top or on the left side.
`[SCREENSHOT: Main FoundryCord web interface with an arrow pointing to the Guild Selector in the navbar]`

## How the Guild Selector Works & What You See

1.  **Initial Display:** When you first load a page or log in:
    *   The selector button will prominently display the name and icon of the Discord guild you last selected in FoundryCord. This is remembered to make it convenient for you to continue where you left off.
        `[SCREENSHOT: Guild Selector button displaying a previously selected guild name and icon]`
    *   If you haven\'t selected a guild before, or if your previous selection is no longer valid, it might show a default message like "Select Guild" or similar.
        `[SCREENSHOT: Guild Selector button showing a default 'Select Guild' state]`

2.  **Opening the Selector:**
    *   Click on the Guild Selector button (the area showing the current guild name/icon or "Select Guild").
    *   A dropdown menu will open, listing all the Discord guilds that your FoundryCord account has been granted access to and that have been approved for use within the system.
        `[SCREENSHOT: Guild Selector dropdown open, listing several example guilds with their icons and names]`

3.  **Choosing a Guild:**
    *   In the dropdown list, click on the name of the guild you wish to manage or view.
    *   The system will then update its context to this newly selected guild.
    *   The page will typically refresh or dynamically update content to reflect data and options relevant to the chosen guild.
    *   The Guild Selector button in the navbar will now display the name and icon of the guild you just selected.

4.  **Persistence of Selection:**
    *   FoundryCord saves your selection. The next time you visit the web interface (even in a new browser session, after logging in), it will attempt to automatically re-select the guild you were last working with.

## Troubleshooting / FAQ

*   **Q: The Discord server I want to manage isn\'t appearing in the Guild Selector list.**
    *   A: For a server to appear, several conditions usually need to be met:
        1.  The FoundryCord bot must be a member of that Discord server.
        2.  The server must be recognized and approved within the FoundryCord system (often an administrator action).
        3.  Your FoundryCord user account must have the necessary permissions to access and manage that specific server through the platform.
        If you believe a server should be listed and it isn\'t, please contact your FoundryCord administrator.

*   **Q: I selected a guild, but the page content didn\'t change or I see an error.**
    *   A: First, try a full refresh of your browser page (Ctrl+R or Cmd+R). If the problem continues, there might be a temporary issue with loading data for that guild, or your session might have expired. Try logging out and logging back in. If problems persist, note any error messages and contact support or your administrator.

*   **Q: How do I know which guild is currently active?**
    *   A: The Guild Selector button in the navigation bar always displays the name and icon of the currently active guild context.

---

## Technical Details (For Developers/Advanced Users)

*(The following sections detail the underlying technical implementation and data flow, primarily for developers contributing to FoundryCord or those interested in its internal workings.)*

### Functionality (Detailed Steps)

1.  **Display Current Guild (On Page Load):**
    *   System checks server-side session for `selected_guild`.
    *   If not in session, checks `AppUserEntity.last_selected_guild_id` from database.
    *   If valid ID found, guild details (name, icon) are fetched and displayed.
    *   Else, default "Select Guild" is shown.
2.  **Open Dropdown:** User clicks selector button.
3.  **Fetch Guild List (Dynamic):** JavaScript calls `GET /api/v1/guilds/`.
    *   Backend (`GuildSelectorController` -> `GuildSelectionService`) determines user\'s accessible (and approved) guilds.
    *   API returns list of `GuildInfo` (ID, name, icon URL).
4.  **Populate Dropdown:** JavaScript populates the dropdown with the fetched list.
5.  **Select Guild (User Click):**
    *   JavaScript sends `POST /api/v1/guilds/select/{guild_id}`.
    *   Backend (`GuildSelectorController` -> `GuildSelectionService`) verifies access.
    *   If verified: Updates `request.session['selected_guild']` AND `AppUserEntity.last_selected_guild_id` in DB.
6.  **Context Update:** Frontend reloads or updates relevant components. The Guild Selector UI updates. Subsequent operations use the new session/DB context.

### Key Components

*   **UI (Template):** `app/web/templates/components/navigation/guild_selector.html`
*   **Backend API Controller:** `app/web/interfaces/api/rest/v1/guild/selector/guild_selector_controller.py`
*   **Backend Service Facade:** `app/web/application/services/guild/guild_service.py` (delegates)
*   **Backend Selection Service:** `app/web/application/services/guild/selection_service.py` (core logic)
*   **Database Model:** `app/shared/infrastructure/models/auth/user_entity.py` (`last_selected_guild_id`)
*   **JavaScript:** `app/web/static/js/components/guildSelector.js`
*   **CSS:** `app/web/static/css/components/guild-selector.css`, `app/web/static/css/components/navbar.css`

### Data Flow Summary (Technical)

1.  Page Load -> Backend checks session, then `user.last_selected_guild_id` -> Fetches guild details -> Template displays current guild.
2.  User clicks selector -> JS fetches guild list from `GET /api/v1/guilds/`.
3.  Backend determines accessible guilds for user -> API returns list.
4.  JS populates dropdown.
5.  User clicks a guild -> JS sends `guild_id` to `POST /api/v1/guilds/select/{guild_id}`.
6.  Backend verifies access -> Updates `selected_guild` in session -> Updates `last_selected_guild_id` in DB.
7.  Frontend might reload page or update dynamically.
8.  On next login/session, step 1 uses the stored `last_selected_guild_id` if session is empty.
