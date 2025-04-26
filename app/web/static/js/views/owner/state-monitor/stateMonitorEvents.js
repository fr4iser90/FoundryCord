/**
 * stateMonitorEvents.js: Sets up event listeners for the State Monitor UI.
 */

/**
 * Attaches event listeners to the UI elements.
 * @param {object} instance - The instance of the StateMonitorDashboard class.
 */
export function setupEventListeners(instance) {
    const ui = instance.ui; // Get UI elements from the instance

    // Scope selection
    if (ui.scopeAllBtn) {
        ui.scopeAllBtn.addEventListener('click', () => instance.setScope('all'));
    }
    if (ui.scopeBotBtn) {
        ui.scopeBotBtn.addEventListener('click', () => instance.setScope('bot'));
    }
    if (ui.scopeWebBtn) {
        ui.scopeWebBtn.addEventListener('click', () => instance.setScope('web'));
    }
    
    // Action buttons
    if (ui.captureBtn) {
        ui.captureBtn.addEventListener('click', () => instance.captureSnapshot());
    }
    if (ui.refreshBtn) {
        ui.refreshBtn.addEventListener('click', () => instance.loadAvailableCollectors());
    }
    if (ui.downloadBtn) {
        ui.downloadBtn.addEventListener('click', () => instance.downloadSnapshot());
    }
    if (ui.copyBtn) {
        ui.copyBtn.addEventListener('click', () => instance.copySnapshot()); 
    }
    if (ui.autoRefreshBtn) {
        ui.autoRefreshBtn.addEventListener('click', () => instance.toggleAutoRefresh());
    }
    
    console.log("State Monitor event listeners initialized.");
} 