/**
 * stateMonitorRenderer.js: Handles rendering UI updates for the State Monitor.
 */

// Note: JSONViewer is expected to be available globally via window.JSONViewer 
// as it's loaded by a separate script tag in the HTML.

/**
 * Renders the list of available collectors in the UI.
 * Corresponds to the original renderCollectorPanel method.
 * @param {object} instance - The StateMonitorDashboard instance (needed for collectors, currentScope, collectorPanel).
 */
export function renderCollectorPanel(instance) {
    // Ensure the main panel container exists on the instance's UI property
    if (!instance.ui || !instance.ui.collectorPanel) return;
    
    // Find the server collectors list container (should exist in static HTML)
    const serverList = document.getElementById('server-collectors');
    if (serverList) {
        // Clear only the list content
        serverList.innerHTML = ''; 
        // Populate server collectors
        instance.collectors.server.forEach(collector => {
            // Filtering logic from original method
            if (instance.currentScope !== 'all' && collector.scope !== instance.currentScope && collector.scope !== 'global') {
                return; 
            }
            
            const item = document.createElement('div');
            item.className = 'collector-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `collector-${collector.name}`;
            checkbox.dataset.name = collector.name;
            checkbox.dataset.source = 'server';
            checkbox.checked = collector.is_approved || !collector.requires_approval;
            
            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
            // HTML structure from original method
            label.innerHTML = `
                <span class="collector-name">${collector.name}</span>
                <span class="collector-description">${collector.description}</span>
                ${collector.requires_approval ? '<span class="badge bg-warning text-dark">Requires Approval</span>' : '<span class="badge bg-success">Auto-approved</span>'}
                <span class="badge bg-info">${collector.scope}</span>
            `;
            
            item.appendChild(checkbox);
            item.appendChild(label);
            serverList.appendChild(item);
        });
        // Add message if list is empty after filtering/loading
        if (serverList.children.length === 0) {
             serverList.innerHTML = '<small class="text-muted">No server collectors available for this scope.</small>';
        }
    } else {
        console.error("Server collector list container #server-collectors not found in HTML.");
    }
    
    // Find the browser collectors list container
    const browserList = document.getElementById('browser-collectors');
    if (browserList) {
        // Clear only the list content
        browserList.innerHTML = ''; 
        // Populate browser collectors
        instance.collectors.browser.forEach(collector => {
             // Filtering logic from original method
             if (instance.currentScope !== 'all' && collector.scope !== instance.currentScope && collector.scope !== 'global') {
                return; 
            }
            
            const item = document.createElement('div');
            item.className = 'collector-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `collector-browser-${collector.name}`;
            checkbox.dataset.name = collector.name;
            checkbox.dataset.source = 'browser';
            checkbox.checked = collector.is_approved || !collector.requires_approval;
            
            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
             // HTML structure from original method
            label.innerHTML = `
                <span class="collector-name">${collector.name}</span>
                <span class="collector-description">${collector.description}</span>
                ${collector.requires_approval ? '<span class="badge bg-warning text-dark">Requires Approval</span>' : '<span class="badge bg-success">Auto-approved</span>'}
                <span class="badge bg-info">${collector.scope}</span>
            `;
            
            item.appendChild(checkbox);
            item.appendChild(label);
            browserList.appendChild(item);
        });
         // Add message if list is empty after filtering/loading
         if (browserList.children.length === 0) {
            browserList.innerHTML = '<small class="text-muted">No browser collectors available for this scope.</small>';
       }
    } else {
        console.error("Browser collector list container #browser-collectors not found in HTML.");
    }
}

/**
 * Renders the results panel with tabs for server, browser, and combined snapshots.
 * Corresponds to the original renderResults method.
 * @param {object} instance - The StateMonitorDashboard instance (needed for resultsPanel, currentSnapshot).
 */
export function renderResults(instance) {
    // Use instance.ui.resultsPanel and instance.currentSnapshot
    if (!instance.ui || !instance.ui.resultsPanel || !instance.currentSnapshot) return;
    
    // Clear the results panel
    instance.ui.resultsPanel.innerHTML = '';
    
    // Create tabs - HTML structure from original method
    const tabsContainer = document.createElement('div');
    tabsContainer.innerHTML = `
        <ul class="nav nav-tabs" id="resultTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="server-tab" data-bs-toggle="tab" data-bs-target="#server-data" type="button" role="tab" aria-controls="server-data" aria-selected="true">Server State</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="browser-tab" data-bs-toggle="tab" data-bs-target="#browser-data" type="button" role="tab" aria-controls="browser-data" aria-selected="false">Browser State</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="combined-tab" data-bs-toggle="tab" data-bs-target="#combined-data" type="button" role="tab" aria-controls="combined-data" aria-selected="false">Combined View</button>
            </li>
        </ul>
    `;
    
    const tabContent = document.createElement('div');
    tabContent.className = 'tab-content'; // Add p-3 class? Original didn't have it here.
    tabContent.innerHTML = `
        <div class="tab-pane fade show active" id="server-data" role="tabpanel" aria-labelledby="server-tab">
            <div class="json-tree-view" id="server-json-view"></div>
        </div>
        <div class="tab-pane fade" id="browser-data" role="tabpanel" aria-labelledby="browser-tab">
            <div class="json-tree-view" id="browser-json-view"></div>
        </div>
        <div class="tab-pane fade" id="combined-data" role="tabpanel" aria-labelledby="combined-tab">
            <div class="json-tree-view" id="combined-json-view"></div>
        </div>
    `;
    
    // Add tabs and content to the panel
    instance.ui.resultsPanel.appendChild(tabsContainer);
    instance.ui.resultsPanel.appendChild(tabContent);
    
    // Now populate the JSON views - calling the exported function below
    renderJsonView('server-json-view', instance.currentSnapshot.server);
    renderJsonView('browser-json-view', instance.currentSnapshot.browser);
    renderJsonView('combined-json-view', instance.currentSnapshot);
}

/**
 * Renders JSON data into a specified container using JSONViewer or a fallback.
 * Corresponds to the original renderJsonView method.
 * @param {string} elementId - The ID of the container element.
 * @param {object} data - The JSON data to render.
 */
export function renderJsonView(elementId, data) {
    const container = document.getElementById(elementId);
    if (!container) return;
    
    // Check if JSONViewer is available (loaded separately)
    if (window.JSONViewer) {
        try {
            const viewer = new window.JSONViewer();
            container.innerHTML = ''; // Clear previous content
            container.appendChild(viewer.getContainer());
            viewer.showJSON(data, 8); // Original used maxLevel 8
        } catch (error) {
            console.error(`Error using JSONViewer for #${elementId}:`, error);
            renderJsonFallback(container, data); // Use fallback if JSONViewer fails
        }
    } else {
        console.warn("JSONViewer library not found, using fallback display.");
        renderJsonFallback(container, data);
    }
}

/**
 * Fallback function to display JSON data as preformatted text.
 * This was part of the original renderJsonView method logic.
 * @param {HTMLElement} container - The container element.
 * @param {object} data - The JSON data to render.
 */
function renderJsonFallback(container, data) {
     // Fallback logic from original renderJsonView
     const pre = document.createElement('pre');
     pre.className = 'json-display'; // Original class name
     try {
        pre.textContent = JSON.stringify(data, null, 2);
        container.appendChild(pre);
     } catch (error) {
        console.error("Error stringifying JSON for fallback display:", error);
        container.innerHTML = '<p class="text-danger">Error displaying JSON data.</p>'; // Error display
     }
}
