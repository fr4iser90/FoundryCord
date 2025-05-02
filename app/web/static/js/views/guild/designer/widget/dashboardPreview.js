/**
 * dashboardPreview.js
 * 
 * Logic for the Dashboard Preview widget.
 * Displays a simulated preview of the currently loaded dashboard configuration.
 */

import { showToast } from '/static/js/components/common/notifications.js';

// --- Module-level flag to prevent multiple listeners ---
let isConfigLoadedListenerAdded_Preview = false; 
// -----------------------------------------------------

/**
 * Initializes the Dashboard Preview widget.
 * @param {HTMLElement} contentElement - The container element for the widget's content 
 *                                      (e.g., #widget-content-dashboard-preview).
 * @param {object} [initialData=null] - Potentially initial data (though likely unused here).
 */
export function initializeDashboardPreview(contentElement, initialData = null) {
    console.log("[DashboardPreviewWidget] Initializing...");
    
    if (!contentElement) {
        console.error("[DashboardPreviewWidget] Content element not provided!");
        return;
    }

    // Set initial placeholder
    contentElement.innerHTML = '<p class="panel-placeholder p-3">No dashboard loaded to preview.</p>';

    // --- Add event listener ONCE --- 
    if (!isConfigLoadedListenerAdded_Preview) {
        document.addEventListener('dashboardConfigLoaded', (event) => {
            console.log("[DashboardPreviewWidget] Received 'dashboardConfigLoaded' event:", event.detail);
            const receivedConfigData = event.detail?.configData;
            if (receivedConfigData) {
                // Update the preview content (basic for now)
                contentElement.innerHTML = `
                    <div class="p-3">
                        <h6>Previewing: ${receivedConfigData.name || 'Unnamed'} (ID: ${receivedConfigData.id || 'N/A'})</h6>
                        <hr>
                        <p class="text-muted small">(Actual component rendering TBD)</p>
                        <pre class="small bg-light p-2 rounded" style="max-height: 200px; overflow-y: auto;">${JSON.stringify(receivedConfigData.config || {}, null, 2)}</pre>
                    </div>
                `;
            } else {
                 console.warn("[DashboardPreviewWidget] 'dashboardConfigLoaded' event received without valid configData.");
                 contentElement.innerHTML = '<p class="panel-placeholder p-3">No dashboard loaded to preview.</p>';
            }
        });
        isConfigLoadedListenerAdded_Preview = true;
        console.log("[DashboardPreviewWidget] 'dashboardConfigLoaded' listener added.");
    }
    // -----------------------------
}

// Make sure the module indicates it's loaded.
console.log("dashboardPreview.js module loaded"); 