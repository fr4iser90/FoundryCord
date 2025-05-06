# User Guide: State Monitor (Developer & Owner Tool)

## Purpose

The State Monitor is a powerful diagnostic tool for developers and application owners. It allows you to capture, store, and analyze detailed snapshots of the internal state of both the backend (Python server) and the frontend (browser JavaScript) at specific moments. Think of it as an X-ray for your application, providing invaluable insights for debugging complex issues, understanding application behavior under various conditions, and generating comprehensive context for bug reports.

`[SCREENSHOT: Main State Monitor interface - overall view showing Collectors List, Recent Snapshots, and Main Area with a loaded snapshot]`

## Key Features

*   **Persistent Storage:** Captured snapshots are stored in the database, allowing for later retrieval and analysis.
*   **Snapshot Management:**
    *   **Automatic Deletion:** To prevent excessive storage usage, the system automatically deletes the oldest snapshots when a configurable limit is reached.
    *   **Manual Deletion:** Snapshots can be manually deleted from the "Recent Snapshots" panel.
*   **Multiple Trigger Mechanisms:**
    *   **Manual Capture:** Initiate snapshots directly from the UI.
    *   **Automatic on JS Error:** Captures frontend state automatically when a JavaScript error occurs.
    *   **Internal Backend Trigger:** Allows backend systems to capture server state programmatically.
*   **Interactive JSON Viewer:** State data (which is often deeply nested JSON) is presented in a user-friendly, collapsible/expandable tree view. `[SCREENSHOT: Interactive JSON viewer showing an expanded section with search/highlighting in use]`
    *   **Search/Highlighting:** Allows you to quickly filter the JSON tree and highlight specific keys or values.
*   **Enhanced Browser State Rendering:** Console logs (`consoleLogs`) and JavaScript errors (`javascriptErrors`) captured from the browser are displayed in structured, readable formats within the snapshot details.
*   **Contextual Information:** Snapshots include metadata about their trigger (`user_capture`, `js_error`, `internal_api`) and context.
*   **Collector Filtering:** Search bar to filter the list of available collectors.
*   **`computedStyles` Collector:** Capture computed CSS styles for specific DOM elements.
*   **UI Panels (Main Interface Components):**
    *   **Collectors List Panel (Typically Left):** Lists available server-side and browser-side state collectors. You can select which ones to include in a manual snapshot. Includes a search bar to filter this list.
        `[SCREENSHOT: Collectors List Panel, showing server/browser sections and selection checkboxes]`
    *   **Recent Snapshots Panel (Typically Right):** Displays a list of recently captured snapshots with timestamps and trigger types. From here, you can load snapshots for viewing or delete them.
        `[SCREENSHOT: Recent Snapshots Panel, with several snapshots listed, highlighting 'Load' and 'Delete' buttons for one entry]`
    *   **Main Display Area (Central, often with a configurable grid layout):**
        *   **Snapshot Summary Widget:** Displays key metadata about the currently loaded snapshot (e.g., timestamp, trigger, collectors used).
        *   **Snapshot Results Widget:** Shows the detailed snapshot data, usually in tabs (e.g., "Server State," "Browser State," "Combined View") utilizing the interactive JSON viewer.

## Usage Workflow

1.  **Navigation:** Access the State Monitor tool via the owner-specific section of the web interface, typically at a URL like `/owner/state-monitor/`.
2.  **View Recent Snapshots (Right Panel):**
    *   The "Recent Snapshots" panel lists previously captured snapshots.
    *   Click the **"Load"** button next to a snapshot entry to view its details in the Main Display Area.
    *   Click the **Trash Icon** (`<i class="fas fa-trash-alt"></i>` or similar icon) next to a snapshot to delete it. A confirmation will be required.
3.  **Capture a New Snapshot Manually:**
    *   **Optional Scope Filtering (Toolbar):** Use the filter buttons/dropdown in the toolbar (e.g., "All," "Bot-Related," "Web-Related") to narrow down the list of collectors shown in the Collectors List Panel.
        `[SCREENSHOT: Toolbar showing scope filter options for collectors]`
    *   **Select Collectors (Left Panel):** In the Collectors List Panel, check the boxes next to the server-side and browser-side collectors whose data you want to include in this snapshot.
        *   *Browser Collector Approval:* For some browser collectors (especially those accessing potentially sensitive information like DOM details or console logs), you might be prompted by a custom modal or a browser permission dialog to approve their use if it\'s the first time or approval isn\'t persistent. Grant permission if you intend to use them.
    *   **Click "Capture" Button (Toolbar):** Once collectors are selected, click the main **"Capture"** button, usually prominent in the toolbar.
        `[SCREENSHOT: Toolbar highlighting the main 'Capture' button]`
    *   This action triggers the state capture process. The new snapshot is saved to the database and will appear at the top of the "Recent Snapshots" list. *Note: The newly captured snapshot is NOT automatically loaded into the viewer; you need to click "Load" on it from the list.*
4.  **Analyze a Loaded Snapshot (Main Display Area):**
    *   **Snapshot Summary Widget:** Review the metadata: When was it captured? What triggered it (manual, JS error, internal)? Which collectors were active?
    *   **Snapshot Results Widget:** Dive into the data. Use the tabs to switch between Server, Browser, or Combined views. Utilize the interactive JSON viewer to expand/collapse sections and use its search bar to find specific keys or values relevant to your investigation.
5.  **Other Toolbar Controls:**
    *   **Refresh:** Click to reload the list of available collectors and the "Recent Snapshots" list from the server.
    *   **Download:** Saves the JSON data of the *currently loaded* snapshot to a local file (`.json`).
    *   **Copy Snapshot:** Copies the JSON data of the *currently loaded* snapshot to your clipboard.
    *   **Layout Controls (e.g., Lock/Unlock Grid, Reset Layout):** If the main display area uses a customizable grid (like Gridstack.js), these controls allow you to rearrange, lock, or reset the layout of the Summary and Results widgets.
        `[SCREENSHOT: Toolbar showing Refresh, Download, Copy, and Layout control buttons]`

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
*   **`javascriptErrors` (Scope: browser, Requires Approval):** Captures recent JavaScript errors caught by global handlers (`onerror`, `onunhandledrejection`). Data is presented in a structured way for readability.
*   **`consoleLogs` (Scope: browser, Requires Approval):** Captures recent messages logged to the browser console (`log`, `warn`, `error`, etc.), including those generated by StateBridge itself. Data is presented in a structured way.
*   **`computedStyles` (Scope: browser, Requires Approval):** Captures computed CSS styles for a specified DOM element (you may need to provide a CSS selector when enabling or configuring this collector if it doesn\'t automatically target a specific element).

## Troubleshooting / FAQ

*   **Q: I clicked "Capture" but my new snapshot didn\'t appear in the main viewer.**
    *   A: Correct. Capturing a snapshot adds it to the "Recent Snapshots" list. You need to click the "Load" button next to it in that list to view its details.
*   **Q: Why are some browser collector values (like `localStorage` values) redacted or only showing keys?**
    *   A: This is a security measure. The State Monitor aims to be a diagnostic tool without exposing highly sensitive user data. For example, `storageKeys` only lists the keys in localStorage/sessionStorage, not their actual content.
*   **Q: The `computedStyles` collector isn\'t showing any data or gives an error.**
    *   A: This collector typically requires a valid CSS selector for an element currently present on the page. Ensure the element exists and the selector is correct. Some versions might prompt for this selector or have a default target.
*   **Q: A JavaScript error occurred on a page, but I don\'t see a `js_error` snapshot.**
    *   A: Automatic snapshots on JS errors are typically only saved if an application owner is currently logged into the FoundryCord web interface. This is a security/privacy measure to prevent arbitrary client-side errors from unknown users from filling up server storage.

## Future Enhancements (Ideas)

*(Keep existing ideas, assuming custom modal for collector approval is implemented as per earlier doc notes)*
*   Add specific collectors for key features/modules as needed.
*   Implement snapshot comparison functionality.
*   Implement configurable snapshot limit (N) for storage via UI/config file.
*   Add UI for retrieving internally triggered snapshots by ID.
*   Improve auth/security for the `/log-browser-snapshot` endpoint.