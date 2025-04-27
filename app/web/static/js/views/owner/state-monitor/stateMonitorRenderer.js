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
    
    // Create and prepend the search input
    const searchInput = document.createElement('div');
    searchInput.className = 'mb-3'; // Add some margin below the input
    searchInput.innerHTML = `
        <input type="search" 
               id="collector-search-input" 
               class="form-control form-control-sm" 
               placeholder="Filter collectors...">
    `;
    // Prepend the search input to the collector panel, if it's empty, otherwise insert after potential existing header
    if (instance.ui.collectorPanel.firstChild) {
        instance.ui.collectorPanel.insertBefore(searchInput, instance.ui.collectorPanel.firstChild.nextSibling); // Attempt to place after a header, if one exists
    } else {
         instance.ui.collectorPanel.prepend(searchInput);
    }
    
    // Add event listener for the search input
    const searchInputElement = document.getElementById('collector-search-input');
    if (searchInputElement) {
        searchInputElement.addEventListener('input', (event) => {
            const searchTerm = event.target.value.toLowerCase();
            const collectorItems = instance.ui.collectorPanel.querySelectorAll('li'); // Assuming collectors are list items

            collectorItems.forEach(item => {
                const collectorName = item.textContent.toLowerCase();
                if (collectorName.includes(searchTerm)) {
                    item.style.display = ''; // Show item
                } else {
                    item.style.display = 'none'; // Hide item
                }
            });
        });
    }
    
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
    
    // Clear previous content (important if called multiple times on same ID)
    container.innerHTML = ''; 

    if (typeof JSONViewer !== 'undefined') {
        try {
            // Check if data might be the full snapshot structure {timestamp, results}
            const dataToRender = (data && typeof data === 'object' && 'results' in data && 'timestamp' in data) 
                                 ? data.results // Render only the results part if it's the full structure
                                 : data;       // Otherwise, render the data as is

            if (dataToRender === null || typeof dataToRender !== 'object' || Object.keys(dataToRender).length === 0) {
                 container.innerHTML = '<span class=\"text-muted\">No data available or data is empty.</span>';
                 return;
            }

            const viewer = new JSONViewer();
            viewer.showJSON(dataToRender);
            container.appendChild(viewer.getContainer());
        } catch (e) {
            console.error('Error using JSONViewer:', e);
            renderJsonFallback(container, data); // Fallback to simple rendering
        }
    } else {
        console.warn('JSONViewer class not found. Using fallback renderer.');
        renderJsonFallback(container, data);
    }
}

/**
 * Fallback function to render JSON data as a simple preformatted text block.
 * Corresponds to the original renderJsonFallback method.
 * @param {HTMLElement} container - The container element.
 * @param {object} data - The JSON data to render.
 */
function renderJsonFallback(container, data) {
    const pre = document.createElement('pre');
    pre.className = 'json-fallback';
    try {
        pre.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        pre.textContent = 'Error displaying data.';
        console.error('Error stringifying data for fallback:', e);
    }
    container.appendChild(pre);
}

/**
 * Renders console log entries in a structured list.
 * @param {HTMLElement} container - The DOM element to render into.
 * @param {Array<object>} logs - Array of console log objects.
 */
function renderConsoleLogsView(container, logs) {
    container.innerHTML = ''; // Clear container

    if (!logs || !Array.isArray(logs) || logs.length === 0) {
        container.innerHTML = '<small class=\"text-muted\">No console logs captured.</small>';
        return;
    }

    const list = document.createElement('ul');
    list.className = 'list-unstyled console-log-list'; // Use Bootstrap class + custom

    logs.forEach(log => {
        const item = document.createElement('li');
        item.className = `log-entry log-${log.level || 'log'}`; // Class based on level

        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'log-timestamp';
        timestampSpan.textContent = new Date(log.timestamp).toLocaleTimeString();

        const levelSpan = document.createElement('span');
        levelSpan.className = 'log-level';
        levelSpan.textContent = (log.level || 'log').toUpperCase();

        const messageSpan = document.createElement('span');
        messageSpan.className = 'log-message';
        // Attempt to format arguments nicely
        messageSpan.textContent = log.args.map(arg => {
            try {
                return typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
            } catch {
                return '[unserializable]';
            }
        }).join(' ');

        item.appendChild(timestampSpan);
        item.appendChild(levelSpan);
        item.appendChild(messageSpan);
        list.appendChild(item);
    });

    container.appendChild(list);
}

/**
 * Renders JavaScript error entries in a structured list.
 * @param {HTMLElement} container - The DOM element to render into.
 * @param {Array<object>} errors - Array of JavaScript error objects.
 */
function renderJsErrorsView(container, errors) {
    container.innerHTML = ''; // Clear container

    if (!errors || !Array.isArray(errors) || errors.length === 0) {
        container.innerHTML = '<small class=\"text-muted\">No JavaScript errors captured.</small>';
        return;
    }

    const list = document.createElement('div'); // Use divs for better structure than ul
    list.className = 'js-error-list';

    errors.forEach((error, index) => {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-entry mb-3 p-2 border rounded'; // Add some styling

        const header = document.createElement('div');
        header.className = 'error-header fw-bold';
        header.textContent = `Error #${index + 1}: ${error.type || 'Unknown Type'} (${new Date(error.timestamp).toLocaleString()})`;
        
        const message = document.createElement('div');
        message.className = 'error-message';
        message.textContent = `Message: ${error.message || 'N/A'}`;

        const source = document.createElement('div');
        source.className = 'error-source text-muted small';
        if (error.source) {
            source.textContent = `Source: ${error.source} (Line: ${error.lineno || '?'}, Col: ${error.colno || '?'})`;
        } else {
             source.textContent = 'Source: N/A';
        }

        errorDiv.appendChild(header);
        errorDiv.appendChild(message);
        errorDiv.appendChild(source);

        if (error.stack) {
            const stackToggle = document.createElement('a');
            stackToggle.href = '#';
            stackToggle.className = 'error-stack-toggle small d-block mt-1';
            stackToggle.textContent = 'Show Stack Trace';
            
            const stackPre = document.createElement('pre');
            stackPre.className = 'error-stack pre-scrollable bg-light p-2 border rounded'; // Style stack trace
            stackPre.textContent = error.stack;
            stackPre.style.display = 'none'; // Initially hidden
            
            stackToggle.onclick = (e) => {
                e.preventDefault();
                const isHidden = stackPre.style.display === 'none';
                stackPre.style.display = isHidden ? 'block' : 'none';
                stackToggle.textContent = isHidden ? 'Hide Stack Trace' : 'Show Stack Trace';
            };
            
            errorDiv.appendChild(stackToggle);
            errorDiv.appendChild(stackPre);
        }

        list.appendChild(errorDiv);
    });

    container.appendChild(list);
}

// --- Helper function to render data using JSONViewer (or fallback) ---
// This is needed because renderJsonView expects an element ID, 
// but here we have the container element directly.
function renderDataInContainer(container, data) {
     if (!container) return;
     container.innerHTML = ''; // Clear previous content

     if (typeof JSONViewer !== 'undefined') {
         try {
              const dataToRender = (data && typeof data === 'object' && 'results' in data && 'timestamp' in data) 
                                  ? data.results 
                                  : data;

             if (dataToRender === null || typeof dataToRender !== 'object' || Object.keys(dataToRender).length === 0) {
                 container.innerHTML = '<span class=\"text-muted\">No data available or data is empty.</span>';
                 return;
             }
             
             const viewer = new JSONViewer();
             viewer.showJSON(dataToRender); // Use the JSONViewer instance
             container.appendChild(viewer.getContainer()); // Append its element
         } catch (e) {
             console.error('Error using JSONViewer:', e);
             renderJsonFallback(container, data); 
         }
     } else {
         console.warn('JSONViewer class not found. Using fallback renderer.');
         renderJsonFallback(container, data);
     }
}

/**
 * Renders the summary panel with key information from the snapshot.
 * @param {object} instance - The StateMonitorDashboard instance.
 */
export function renderSummaryPanel(instance) {
    const panel = instance.ui.summaryPanel;
    if (!panel) return;
    if (!instance.currentSnapshot) {
        panel.innerHTML = '<p class="text-muted">Capture a snapshot to see the summary.</p>';
        return;
    }

    const snap = instance.currentSnapshot;
    const browserResults = snap.browser?.results || {};
    const serverResults = snap.server?.results || {};
    const browserContext = snap.browser?.context || {}; // Assumes context is passed here eventually
    const serverContext = snap.server?.context || {};   // Context from server API call

    // Determine trigger (try server context first, then browser)
    let trigger = serverContext.trigger || browserContext.trigger || 'Unknown';
    if (trigger === 'user_capture') trigger = 'User Capture';
    else if (trigger === 'js_error') trigger = 'JS Error';
    else if (trigger === 'internal_api') trigger = 'Internal API';

    // Helper to get nested data safely
    const getData = (obj, path, defaultValue = 'N/A') => {
        const keys = path.split('.');
        let current = obj;
        for (const key of keys) {
            if (current && typeof current === 'object' && key in current) {
                current = current[key];
            } else {
                return defaultValue;
            }
        }
        // Handle cases where value might be empty string or null
        return (current === null || current === '') ? defaultValue : current;
    };

    const errors = browserResults.javascriptErrors || [];
    const logs = browserResults.consoleLogs || [];

    panel.innerHTML = `
        <div class="summary-grid">
            <div class="summary-item">
                <strong>Timestamp:</strong>
                <span>${new Date(snap.timestamp).toLocaleString()}</span>
            </div>
            <div class="summary-item">
                <strong>Trigger:</strong>
                <span>${trigger}</span>
            </div>
            <div class="summary-item">
                <strong>URL:</strong>
                <span>${getData(browserResults, 'navigation.href', 'N/A')}</span>
            </div>
            <div class="summary-item">
                <strong>Viewport:</strong>
                <span>${getData(browserResults, 'viewport.width')}x${getData(browserResults, 'viewport.height')}</span>
            </div>
            <div class="summary-item">
                <strong>JS Errors:</strong>
                <span class="badge bg-${errors.length > 0 ? 'danger' : 'secondary'}">${errors.length}</span>
            </div>
             <div class="summary-item">
                <strong>Console Logs:</strong>
                <span class="badge bg-secondary">${logs.length}</span>
            </div>
            <div class="summary-item">
                <strong>Bot Status:</strong>
                <span>${getData(serverResults, 'bot_status.status', 'N/A')}</span>
            </div>
            <div class="summary-item">
                <strong>Platform:</strong>
                <span>${getData(serverResults, 'system_info.platform', 'N/A')}</span>
            </div>
        </div>
    `;
}
