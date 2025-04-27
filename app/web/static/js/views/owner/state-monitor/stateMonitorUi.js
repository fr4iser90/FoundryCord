/**
 * stateMonitorUi.js: Handles UI element initialization and status updates.
 */

/**
 * Finds and returns references to the core UI elements from the DOM.
 * Corresponds to the original initElements method part that finds elements.
 * @returns {object} An object containing references to DOM elements.
 */
export function initElements() {
    const elements = {
        // Collector selection panel
        collectorPanel: document.getElementById('collector-panel'),
        // Scope selection buttons
        scopeAllBtn: document.getElementById('scope-all'),
        scopeBotBtn: document.getElementById('scope-bot'),
        scopeWebBtn: document.getElementById('scope-web'),
        // Action buttons
        captureBtn: document.getElementById('capture-snapshot'),
        refreshBtn: document.getElementById('refresh-collectors'),
        downloadBtn: document.getElementById('download-snapshot'),
        copyBtn: document.getElementById('copy-snapshot'),
        autoRefreshBtn: document.getElementById('toggle-auto-refresh'),
        // Results display
        resultsPanel: document.getElementById('results-panel'),
        summaryPanel: document.getElementById('summary-panel'),
        statusDisplay: document.getElementById('status-display'),
        snapshotTimestamp: document.getElementById('snapshot-timestamp')
    };
    
    // Basic check if essential elements are missing
    if (!elements.collectorPanel || !elements.resultsPanel || !elements.statusDisplay) {
         console.warn('State Monitor: Essential UI elements not found during initialization.');
    }
    
    return elements;
}

/**
 * Updates the status display element.
 * Corresponds to the original setStatus method.
 * @param {HTMLElement} statusDisplayElement - The status display DOM element.
 * @param {string} message - The message to display.
 * @param {string} [type='info'] - The type of status ('info', 'success', 'warning', 'error').
 */
export function setStatus(statusDisplayElement, message, type = 'info') {
    if (!statusDisplayElement) return;
    
    statusDisplayElement.textContent = message;
    statusDisplayElement.className = `status status-${type}`;
}

/**
 * Initializes any toggle switches or other complex UI components.
 * Corresponds to the original initializeToggles method.
 * Placeholder for now.
 */
export function initializeToggles() {
    // For Bootstrap toggle switches, checkboxes, etc.
    // This would be expanded based on the UI framework used
    // For example, if using Bootstrap 5 toggles, initialization might go here.
} 