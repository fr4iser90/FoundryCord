/**
 * snapshotResultsTabs.js: Widget for displaying snapshot results in tabs (Server, Browser, Combined).
 */

import { showToast } from '/static/js/components/common/notifications.js';

// Note: Assumes JSONViewer library is loaded globally (window.JSONViewer)

/**
 * Initializes the Snapshot Results Tabs widget.
 * @param {object} controller - The main StateMonitorController instance.
 * @param {object|null} snapshotData - The currently loaded snapshot data, or null.
 * @param {HTMLElement} contentElement - The container element for the widget's content.
 */
export function initializeSnapshotResultsTabs(controller, snapshotData, contentElement) {
    console.log("[SnapshotResultsTabs] Initializing with data:", snapshotData);
    if (!contentElement) {
        console.error("[SnapshotResultsTabs] Content element not provided.");
        return;
    }

    contentElement.innerHTML = ''; // Clear previous content
    // Remove padding if added by default, tabs usually handle their own
    contentElement.classList.remove('p-2'); 

    if (!snapshotData) {
        contentElement.innerHTML = '<p class="text-muted p-3">No snapshot data to display.</p>';
        return;
    }

    // Generate unique IDs for tabs within this widget instance
    const widgetId = `widget-${Date.now()}`;
    const serverTabId = `server-tab-${widgetId}`;
    const browserTabId = `browser-tab-${widgetId}`;
    const combinedTabId = `combined-tab-${widgetId}`;
    const serverPaneId = `server-data-${widgetId}`;
    const browserPaneId = `browser-data-${widgetId}`;
    const combinedPaneId = `combined-data-${widgetId}`;
    const serverJsonViewId = `server-json-view-${widgetId}`;
    const browserJsonViewId = `browser-json-view-${widgetId}`;
    const combinedJsonViewId = `combined-json-view-${widgetId}`;

    // Create tabs HTML structure
    const tabsContainer = document.createElement('div');
    tabsContainer.innerHTML = `
        <ul class="nav nav-tabs" id="resultTabs-${widgetId}" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="${serverTabId}" data-bs-toggle="tab" data-bs-target="#${serverPaneId}" type="button" role="tab" aria-controls="${serverPaneId}" aria-selected="true">Server State</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="${browserTabId}" data-bs-toggle="tab" data-bs-target="#${browserPaneId}" type="button" role="tab" aria-controls="${browserPaneId}" aria-selected="false">Browser State</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="${combinedTabId}" data-bs-toggle="tab" data-bs-target="#${combinedPaneId}" type="button" role="tab" aria-controls="${combinedPaneId}" aria-selected="false">Combined View</button>
            </li>
        </ul>
    `;

    const tabContent = document.createElement('div');
    tabContent.className = 'tab-content';
    tabContent.innerHTML = `
        <div class="tab-pane fade show active" id="${serverPaneId}" role="tabpanel" aria-labelledby="${serverTabId}">
            <div class="d-flex justify-content-end pt-2 pe-2">
                <button class="btn btn-sm btn-outline-secondary copy-tab-btn" data-target-view="server" title="Copy Server State JSON">
                    <i class="fas fa-copy me-1"></i>Copy Server JSON
                </button>
            </div>
            <div class="json-tree-view p-3" id="${serverJsonViewId}">Loading Server View...</div>
        </div>
        <div class="tab-pane fade" id="${browserPaneId}" role="tabpanel" aria-labelledby="${browserTabId}">
            <div class="d-flex justify-content-end pt-2 pe-2">
                <button class="btn btn-sm btn-outline-secondary copy-tab-btn" data-target-view="browser" title="Copy Browser State JSON">
                    <i class="fas fa-copy me-1"></i>Copy Browser JSON
                </button>
            </div>
            <div class="json-tree-view p-3" id="${browserJsonViewId}">Loading Browser View...</div>
        </div>
        <div class="tab-pane fade" id="${combinedPaneId}" role="tabpanel" aria-labelledby="${combinedTabId}">
             <div class="d-flex justify-content-end pt-2 pe-2">
                <button class="btn btn-sm btn-outline-secondary copy-tab-btn" data-target-view="combined" title="Copy Combined Snapshot JSON">
                    <i class="fas fa-copy me-1"></i>Copy Combined JSON
                </button>
            </div>
            <div class="json-tree-view p-3" id="${combinedJsonViewId}">Loading Combined View...</div>
        </div>
    `;

    // Add tabs and content to the widget element
    contentElement.appendChild(tabsContainer);
    contentElement.appendChild(tabContent);

    // --- JSON Rendering Logic (Adapted from stateMonitorRenderer.js) ---
    
    // TODO: Consider moving these rendering functions to a shared utility file.

    /** Renders JSON data into a container using JSONViewer or a fallback. */
    const renderJsonView = (elementId, data) => {
        const container = contentElement.querySelector(`#${elementId}`);
        if (!container) {
            console.error(`[SnapshotResultsTabs] JSON view container #${elementId} not found.`);
            return;
        }
        container.innerHTML = ''; // Clear loading message

        if (typeof data === 'undefined' || data === null) {
            container.innerHTML = '<p class="text-muted">No data available for this view.</p>';
            return;
        }
        
        // Specific handling for consoleLogs and jsErrors (example)
        if (elementId.includes('server-json-view') && data && data.consoleLogs) {
             // renderConsoleLogsView(container, data.consoleLogs);
             // For now, just show JSON
        } else if (elementId.includes('browser-json-view') && data && data.jsErrors) {
             // renderJsErrorsView(container, data.jsErrors);
             // For now, just show JSON
        }
        
        // Attempt to use JSONViewer library if available
        if (window.JSONViewer) {
            try {
                const viewer = new window.JSONViewer();
                container.appendChild(viewer.getContainer());
                viewer.showJSON(data, -1, 2); // Show JSON initially expanded
            } catch (e) {
                console.error("[SnapshotResultsTabs] Error using JSONViewer:", e);
                renderJsonFallback(container, data); // Fallback on error
            }
        } else {
            console.warn("[SnapshotResultsTabs] JSONViewer library not found. Using fallback.");
            renderJsonFallback(container, data);
        }
    }

    /** Fallback function to render JSON as a simple preformatted string. */
    const renderJsonFallback = (container, data) => {
        const pre = document.createElement('pre');
        pre.style.whiteSpace = 'pre-wrap'; // Ensure wrapping
        pre.style.wordBreak = 'break-all'; // Ensure long strings break
        pre.textContent = JSON.stringify(data, null, 2); // Pretty print
        container.appendChild(pre);
    }
    
    // --- Render JSON data into the tabs --- 
    renderJsonView(serverJsonViewId, snapshotData.server);
    renderJsonView(browserJsonViewId, snapshotData.browser);
    renderJsonView(combinedJsonViewId, snapshotData); // Combined view gets the whole object

    // --- Add event listeners for copy buttons --- 
    tabContent.querySelectorAll('.copy-tab-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            const targetView = event.currentTarget.dataset.targetView;
            let dataToCopy = null;
            let dataType = 'Data'; // For status message

            switch (targetView) {
                case 'server':
                    dataToCopy = snapshotData.server;
                    dataType = 'Server State';
                    break;
                case 'browser':
                    dataToCopy = snapshotData.browser;
                    dataType = 'Browser State';
                    break;
                case 'combined':
                    dataToCopy = snapshotData; // The whole snapshot
                    dataType = 'Combined Snapshot';
                    break;
            }

            if (dataToCopy) {
                try {
                    // Handle potential circular references during stringify (basic check)
                    let jsonString;
                     try {
                        jsonString = JSON.stringify(dataToCopy, null, 2);
                    } catch (stringifyError) {
                         console.error(`[SnapshotResultsTabs] Error stringifying ${dataType} JSON:`, stringifyError);
                         // Attempt to stringify with a replacer to handle potential circularity
                         const cache = new Set();
                         jsonString = JSON.stringify(dataToCopy, (key, value) => {
                             if (typeof value === 'object' && value !== null) {
                                 if (cache.has(value)) {
                                     // Circular reference found, discard key
                                     return '[Circular Reference]';
                                 }
                                 // Store value in our collection
                                 cache.add(value);
                             }
                             return value;
                         }, 2);
                         showToast(`Warning: ${dataType} JSON contained circular references. Check console.`, 'warning');
                     }
                     
                    await navigator.clipboard.writeText(jsonString);
                    showToast(`${dataType} JSON copied to clipboard!`, 'success');
                } catch (err) {
                    console.error(`[SnapshotResultsTabs] Failed to copy ${dataType} JSON:`, err);
                    showToast(`Failed to copy ${dataType} JSON. See console.`, 'error');
                }
            } else {
                 showToast(`No ${dataType} data available to copy.`, 'warning');
            }
        });
    });

    console.log("[SnapshotResultsTabs] Initialization complete.");
}