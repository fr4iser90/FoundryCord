# State Monitor Feature

## Purpose

The State Monitor is a developer and owner-facing diagnostic tool designed to capture and display the internal state of both the backend (Python server) and the frontend (browser JavaScript) at a specific point in time. It acts like an X-ray, providing valuable insights for debugging issues, understanding application behavior, and generating context for bug reports.

## Usage

1.  **Navigation:** Access the tool via the `/owner/state-monitor/` route in the web interface.
2.  **Scope Selection (Optional):** Use the "All", "Bot", "Web" buttons at the top right to filter the list of available collectors displayed below. "All" shows collectors from all scopes.
3.  **Collector Selection:**
    *   In the "State Collectors" panel on the left, check the boxes next to the specific server-side and browser-side states you wish to include in the snapshot.
    *   **Server Collectors:** These run on the backend (e.g., `bot_status`, `system_info`). They typically do not require special permissions beyond owner access to the page.
    *   **Browser Collectors:** These run in your browser via the `StateBridge` system.
        *   Collectors marked **Auto-approved** (green badge) are considered safe and run automatically when selected.
        *   Collectors marked **Requires Approval** (yellow badge) access potentially more sensitive browser information. The first time you select one of these and click "Capture" in a browser session, a confirmation dialog will appear (batch approval for multiple). Your approval is remembered for the duration of the browser session (using localStorage).
4.  **Capture Snapshot:** Click the "Capture" button.
    *   The process involves collecting browser state, sending selected server collector names to the backend, executing server collectors, and combining the results.
5.  **Analyze Results:** The captured data will appear in the "State Snapshot" panel on the right, organized into tabs:
    *   **Server State:** Displays data collected by the selected server collectors.
    *   **Browser State:** Displays data collected by the selected *and approved* browser collectors.
        *   Data for `consoleLogs` and `javascriptErrors` is now displayed in a structured, more readable list format instead of raw JSON.
        *   Other browser data is shown in the interactive JSON viewer.
    *   **Combined View:** Shows the complete snapshot object, including timestamps and both server and browser results.
    *   The data is rendered using an interactive JSON viewer.
6.  **Export/Copy (Optional):**
    *   **Copy All:** Copies the full JSON of the combined snapshot to the clipboard.
    *   **Download:** Saves the full JSON of the combined snapshot to a `.json` file.
7.  **Other Controls:**
    *   **Refresh:** Reloads the list of available collectors from the backend.
    *   **Start/Stop Auto-Refresh:** Automatically captures a new snapshot every 10 seconds (default interval).

## Key Features

*   **Interactive JSON Viewer:** State data is presented in a collapsible/expandable tree view for easy navigation of complex objects and arrays.
    *   **Search/Highlighting:** A search bar within the JSON viewer allows filtering and highlighting of specific keys or values within the snapshot data.
*   **Enhanced Browser State Rendering:**
    *   Console logs (`consoleLogs`) are displayed as a timestamped list with log levels.
    *   JavaScript errors (`javascriptErrors`) are shown with message, source location, timestamp, and a toggleable stack trace.
*   **Error Handling & Context:**
    *   Recent JavaScript errors (`onerror`, `onunhandledrejection`) are captured and can be included in snapshots via the `javascriptErrors` collector.
    *   **Automatic Snapshots on Error:** When a JavaScript error occurs in the browser, a state snapshot is automatically triggered and captured in the background. This snapshot now includes context indicating it was triggered by an error (`{ trigger: 'js_error', error: {...} }`).
*   **Server-Side Enhancements:**
    *   **Snapshot Storage:** The backend can now store snapshots triggered internally (e.g., by system events or other backend processes). These are saved as temporary files.
    *   **Internal Trigger API:** A dedicated internal API endpoint (`POST /internal/state/trigger-snapshot`) allows triggering server-side snapshots programmatically.
    *   **Snapshot Retrieval API:** Stored snapshots can be retrieved via their unique ID using an owner-only API endpoint (`GET /owner/state/snapshot/{snapshot_id}`).
*   **Improved Styling:** The JSON viewer's CSS has been refined for better readability and clearer indentation.
*   **Collector Filtering:** A search bar allows filtering the list of available server and browser collectors.

## Debugging Use Cases

The primary goal of the State Monitor is to aid developers and owners in diagnosing issues. Here are key scenarios:

1.  **Live Debugging (Manual Trigger):**
    *   **Scenario:** An owner observes unexpected behavior in the UI or bot.
    *   **Action:** Navigate to the State Monitor, select relevant collectors (e.g., `navigation`, `consoleLogs`, `bot_status`, specific module states), and click "Capture".
    *   **Benefit:** Provides an immediate "X-ray" view of both frontend and backend state at that exact moment, helping to understand the cause of the issue.

2.  **Frontend Error Analysis (Automatic Trigger):**
    *   **Scenario:** A JavaScript error occurs in a user's browser.
    *   **Action:** The system automatically captures a state snapshot (including `javascriptErrors` and `consoleLogs`) with the trigger context set to `js_error`. This snapshot is ideally sent to the backend for storage.
    *   **Benefit:** Allows developers to retrospectively analyze the state (URL, viewport, preceding logs, server status) leading up to the error, even without being present.

3.  **Backend Error Analysis (Internal/Manual Trigger):**
    *   **Scenario:** A backend process fails (e.g., task queue error, API exception, bot disconnect).
    *   **Action:** An internal system component or an owner triggers a server-side snapshot capture (containing only server collector data) with trigger context `internal_api` or similar. This snapshot is stored server-side.
    *   **Benefit:** Captures the backend state precisely when the issue occurred, independent of any browser interaction. Snapshots can be retrieved later by ID for analysis.

4.  **Bug Report Enrichment (Manual Trigger):**
    *   **Scenario:** An owner identifies a reproducible bug.
    *   **Action:** Capture a relevant state snapshot, download the JSON, and attach it to the bug report (e.g., in GitLab/GitHub).
    *   **Benefit:** Provides developers with rich, structured context far beyond screenshots, significantly speeding up diagnosis and fixing.

## Available Collectors (Default)

This list may expand as the application grows.

### Server Collectors

*   **`bot_status` (Scope: bot, Auto-approved):** Basic status information about the Discord bot (currently placeholder data).
*   **`system_info` (Scope: web, Auto-approved):** Basic OS and Python environment details where the web server is running.

### Browser Collectors (via StateBridge)

*   **`navigation` (Scope: browser, Auto-approved):** Current page URL, path, query, and hash.
*   **`viewport` (Scope: browser, Auto-approved):** Browser window dimensions, device pixel ratio, and orientation.
*   **`features` (Scope: browser, Auto-approved):** Detection of browser features like localStorage, WebSockets, etc.
*   **`domSummary` (Scope: browser, Requires Approval):** Summary of the page structure (element counts, title, body classes). *Does not capture element content.*
*   **`storageKeys` (Scope: browser, Requires Approval):** Lists the *names* (keys) stored in localStorage and sessionStorage. *Values are redacted for security.*
*   **`javascriptErrors` (Scope: browser, Requires Approval):** Captures recent JavaScript errors caught by global handlers (`onerror`, `onunhandledrejection`).
*   **`consoleLogs` (Scope: browser, Requires Approval):** Captures recent messages logged to the browser console (`log`, `warn`, `error`, etc.), including those generated by StateBridge itself.

## Future Enhancements (Ideas)

*   Implement a custom, styled modal for browser collector approval instead of the basic `window.confirm`.
*   Add more detailed server-side collectors (e.g., specific module states, database stats, task queue status).
*   Provide functionality to compare different snapshots.
*   Refine the `bot_status` collector to fetch real data. 