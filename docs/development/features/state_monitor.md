# State Monitor Feature

## Purpose

The State Monitor is a developer and owner-facing diagnostic tool designed to capture and display the internal state of both the backend (Python server) and the frontend (browser JavaScript) at a specific point in time. It acts like an X-ray, providing valuable insights for debugging issues, understanding application behavior, and generating context for bug reports. Snapshots can be triggered manually, automatically on frontend errors, or internally by backend processes, and are stored persistently in the database.

## Key Features

*   **Persistent Storage:** Captured snapshots are stored in the database, allowing for later retrieval and analysis.
*   **Snapshot Management:**
    *   **Automatic Deletion:** To prevent excessive storage usage, the system automatically deletes the oldest snapshots when a configurable limit is reached.
    *   **Manual Deletion:** Snapshots can be manually deleted from the "Recent Snapshots" panel.
*   **Multiple Trigger Mechanisms:**
    *   **Manual Capture:** Initiate snapshots directly from the UI.
    *   **Automatic on JS Error:** Captures frontend state automatically when a JavaScript error occurs.
    *   **Internal Backend Trigger:** Allows backend systems to capture server state programmatically.
*   **Interactive JSON Viewer:** State data is presented in a collapsible/expandable tree view.
    *   **Search/Highlighting:** Filter and highlight specific keys or values.
*   **Enhanced Browser State Rendering:** Console logs (`consoleLogs`) and JavaScript errors (`javascriptErrors`) are displayed in structured, readable formats.
*   **Contextual Information:** Snapshots include metadata about their trigger (`user_capture`, `js_error`, `internal_api`) and context.
*   **Collector Filtering:** Search bar to filter the list of available collectors.
*   **`computedStyles` Collector:** Capture computed CSS styles for specific DOM elements.
*   **UI Panels:**
    *   **Collectors List (Left):** Select server and browser collectors.
    *   **Recent Snapshots (Right):** View a list of recently captured snapshots, load them for analysis, or delete them.
    *   **Main Area (Grid Layout):**
        *   **Snapshot Summary:** Displays key metadata about the currently loaded snapshot.
        *   **Snapshot Results:** Shows the detailed snapshot data in tabs (Server, Browser, Combined).

## Usage Workflow

1.  **Navigation:** Access the tool via `/owner/state-monitor/`.
2.  **View Recent Snapshots (Right Panel):**
    *   A list of recently captured snapshots is displayed with timestamps and IDs.
    *   Click **"Load"** to view a specific snapshot's details in the main area (Summary and Results panels).
    *   Click the **Trash Icon** <i class="fas fa-trash-alt"></i> to delete a snapshot (confirmation required).
3.  **Capture a New Snapshot (Manual):**
    *   **Scope Selection (Toolbar):** Optionally filter collectors by "All", "Bot", or "Web".
    *   **Collector Selection (Left Panel):** Check the desired server and browser collectors. Handle browser collector approval prompts if necessary (using the custom modal).
    *   **Click "Capture" (Toolbar):** This triggers the capture process, stores the snapshot in the database, and updates the "Recent Snapshots" list. The new snapshot is *not* automatically loaded for viewing.
4.  **Analyze Loaded Snapshot (Main Area):**
    *   **Summary Panel:** View timestamp, trigger source, and basic collector info.
    *   **Results Panel:** Explore the detailed data using the tabs and the interactive JSON viewer (including search).
5.  **Other Controls (Toolbar):**
    *   **Refresh:** Reloads collector and recent snapshot lists.
    *   **Download:** Saves the *currently loaded* snapshot as a JSON file.
    *   **Copy Snapshot:** Copies the *currently loaded* snapshot JSON to the clipboard.
    *   **(Layout Controls):** Lock/Unlock and Reset the grid layout of the main area panels.

## Trigger Scenarios & Data Flow

1.  **Manual Capture (`user_capture`):**
    *   Triggered by: Owner clicking "Capture" button.
    *   Process: Browser collects selected/approved state -> Sends collector names + browser state to `POST /api/v1/owner/state/snapshot` -> Backend runs server collectors -> Backend combines data -> Backend saves to DB via `save_snapshot` (checks limit, deletes oldest if needed) -> Backend returns snapshot ID -> UI refreshes "Recent Snapshots" list.
2.  **JS Error Capture (`js_error`):**
    *   Triggered by: Global JavaScript error handler (`bridgeErrorHandler.js`).
    *   Process: Browser automatically collects state (incl. `javascriptErrors`, `consoleLogs`) -> Sends snapshot data to `POST /api/v1/owner/state/log-browser-snapshot` -> Backend **verifies owner authentication** -> Backend saves to DB via `save_snapshot`. *(Note: Snapshots are only saved if the error occurs while the owner is logged in)*.
3.  **Internal Backend Capture (`internal_api`, etc.):**
    *   Triggered by: Backend code calling `POST /internal/state/trigger-snapshot` with collector list and context.
    *   Process: Backend runs specified server collectors -> Backend saves to DB via `save_snapshot`.

## Snapshot Retrieval & Management APIs

*   `GET /api/v1/owner/state/snapshots/list?limit=N`: Retrieves metadata for the N most recent snapshots. (Owner-only)
*   `GET /api/v1/owner/state/snapshot/{snapshot_id}`: Retrieves the full data for a specific snapshot by its ID. (Owner-only)
*   `DELETE /api/v1/owner/state/snapshot/{snapshot_id}`: Deletes a specific snapshot by its ID. (Owner-only)
*   `POST /api/v1/owner/state/log-browser-snapshot`: Endpoint for browser to send automatically triggered snapshots. (Owner-only)

## Debugging Use Cases

*(This section remains largely the same but benefits from the context of persistent storage and multiple triggers)*

1.  **Live Debugging (Manual Trigger):** Capture state instantly when observing issues. Load the snapshot immediately or later via the "Recent Snapshots" panel.
2.  **Frontend Error Analysis (Automatic Trigger):** Retrospectively analyze the state leading up to a JS error by finding the corresponding `js_error` snapshot in the list and loading it.
3.  **Backend Error Analysis (Internal Trigger):** Retrieve server-side snapshots (triggered by `internal_api`) by their known ID (e.g., logged during the backend event) using the retrieval API or potentially a future UI element.
4.  **Bug Report Enrichment (Manual/Automatic):** Capture or find a relevant snapshot, download the JSON, and attach it to bug reports for comprehensive context.

## Available Collectors (Default)

*(List remains the same as previous version)*

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
*   **`computedStyles` (Scope: browser, Requires Approval):** Captures computed CSS styles for a specified element.

## Future Enhancements (Ideas)

*(Keep existing ideas, remove custom modal as it's done)*
*   Add specific collectors for key features/modules as needed.
*   Implement snapshot comparison functionality.
*   Implement configurable snapshot limit (N) for storage via UI/config file.
*   Add UI for retrieving internally triggered snapshots by ID.
*   Improve auth/security for the `/log-browser-snapshot` endpoint.