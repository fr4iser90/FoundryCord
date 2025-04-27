/**
 * snapshotSummary.js: Widget for displaying summary information about the loaded snapshot.
 */

// TODO: Import helper functions if needed

/**
 * Initializes the Snapshot Summary widget.
 * @param {object} controller - The main StateMonitorController instance.
 * @param {object|null} snapshotData - The currently loaded snapshot data, or null.
 * @param {HTMLElement} contentElement - The container element for the widget's content.
 */
export function initializeSnapshotSummaryWidget(controller, snapshotData, contentElement) {
    console.log("[SnapshotSummary] Initializing with data:", snapshotData);
    if (!contentElement) {
        console.error("[SnapshotSummary] Content element not provided.");
        return;
    }

    contentElement.innerHTML = ''; // Clear previous content
    contentElement.classList.add('p-2'); // Add some padding

    // Helper function for safe data access (from original renderer)
    const getData = (obj, path, defaultValue = 'N/A') => {
        if (!obj) return defaultValue;
        const value = path.split('.').reduce((o, p) => (o && o.hasOwnProperty(p)) ? o[p] : undefined, obj);
        // Handle cases where value might be an empty object/array but we want a specific string
        if (value === undefined || value === null || (typeof value === 'object' && Object.keys(value).length === 0) || (Array.isArray(value) && value.length === 0)) {
            return defaultValue;
        }
        // If it's an array, join elements
        if (Array.isArray(value)) {
             return value.join(', ') || defaultValue; 
        }
        return value;
    };

    if (!snapshotData) {
        contentElement.innerHTML = '<p class="text-muted">No snapshot loaded.</p>';
        return;
    }

    // Format timestamp
    let timestampStr = 'Invalid Date';
    try {
        const date = new Date(snapshotData.timestamp || snapshotData.created_at);
        if (!isNaN(date)) {
            timestampStr = date.toLocaleString();
        }
    } catch (e) {
        console.warn("Error parsing snapshot timestamp:", snapshotData.timestamp || snapshotData.created_at);
    }
    
    // Determine source (if available)
    const source = getData(snapshotData, 'metadata.source', 'Unknown'); // Assuming metadata structure
    
    // Get collector lists
    const serverCollectors = Object.keys(getData(snapshotData, 'server', {})).join(', ') || 'None';
    const browserCollectors = Object.keys(getData(snapshotData, 'browser', {})).join(', ') || 'None';

    // Create summary content
    const summaryContent = document.createElement('div');
    summaryContent.innerHTML = `
        <dl class="row mb-0">
            <dt class="col-sm-4">Timestamp</dt>
            <dd class="col-sm-8">${timestampStr}</dd>

            <dt class="col-sm-4">Source</dt>
            <dd class="col-sm-8">${escapeHtml(source)}</dd>

            <dt class="col-sm-4">Server Collectors</dt>
            <dd class="col-sm-8"><small>${escapeHtml(serverCollectors)}</small></dd>

            <dt class="col-sm-4">Browser Collectors</dt>
            <dd class="col-sm-8"><small>${escapeHtml(browserCollectors)}</small></dd>
        </dl>
    `;

    contentElement.appendChild(summaryContent);
    
    // Basic HTML escaping function
    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
     }

    console.log("[SnapshotSummary] Initialization complete.");
} 