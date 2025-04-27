/**
 * collectorsList.js: Widget for displaying available server and browser state collectors.
 */

// TODO: Import any necessary helper functions (e.g., for event handling)

/**
 * Initializes the Collectors List widget.
 * @param {object} collectorsData - The collector data ({ server: [], browser: [] }).
 * @param {HTMLElement} contentElement - The container element for the widget's content.
 * @param {object} controller - The main StateMonitorController instance.
 */
export function initializeCollectorsList(collectorsData, contentElement, controller) {
    console.log("[CollectorsList] Initializing with data:", collectorsData);
    if (!contentElement) {
        console.error("[CollectorsList] Content element not provided.");
        return;
    }
    // Add check for controller if needed by event listeners later
    if (!controller) {
         console.warn("[CollectorsList] Controller instance not provided (needed for event handling).");
         // Proceeding without controller for display, but interactions might fail
    }

    // Clear any existing content (e.g., "Loading...")
    contentElement.innerHTML = '';

    // 1. Add Search Input
    const searchInputContainer = document.createElement('div');
    searchInputContainer.className = 'mb-3 px-2'; // Add padding
    searchInputContainer.innerHTML = `
        <input type="search" 
               id="collector-search-input" 
               class="form-control form-control-sm" 
               placeholder="Filter collectors...">
    `;
    contentElement.appendChild(searchInputContainer);

    // 2. Create Containers for Lists
    const listsContainer = document.createElement('div');
    listsContainer.className = 'collector-lists-container px-2'; // Container for scrolling/styling if needed

    const serverListContainer = document.createElement('div');
    serverListContainer.innerHTML = '<h6>Server Collectors</h6>';
    const serverList = document.createElement('div');
    serverList.id = 'server-collectors-list'; // Use a unique ID within the widget
    serverListContainer.appendChild(serverList);
    listsContainer.appendChild(serverListContainer);

    const browserListContainer = document.createElement('div');
    browserListContainer.innerHTML = '<h6 class="mt-3">Browser Collectors</h6>';
    const browserList = document.createElement('div');
    browserList.id = 'browser-collectors-list'; // Use a unique ID
    browserListContainer.appendChild(browserList);
    listsContainer.appendChild(browserListContainer);

    contentElement.appendChild(listsContainer);

    // 3. Populate Lists
    const populateList = (listElement, collectors, source, currentScope) => {
        listElement.innerHTML = ''; // Clear previous items
        let count = 0;
        // Check if collectors array exists before iterating
        if (!collectors || !Array.isArray(collectors)) {
             listElement.innerHTML = '<small class="text-muted">No data provided for this list.</small>';
             return;
        }
        collectors.forEach(collector => {
            // --- Apply Scope Filtering --- 
            // Scope filtering logic moved here
            if (currentScope !== 'all' && collector.scope !== currentScope && collector.scope !== 'global') {
                 return; // Skip this collector if it doesn't match the scope
            }
            // --- End Scope Filtering ---
            count++;

            const item = document.createElement('div');
            item.className = 'collector-item mb-2'; // Added margin-bottom
            item.dataset.collectorName = collector.name; // For filtering

            const checkboxId = `collector-${source}-${collector.name}`.replace(/\s+/g, '-'); // Ensure valid ID
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input me-2'; // Bootstrap styling
            checkbox.id = checkboxId;
            checkbox.dataset.name = collector.name;
            checkbox.dataset.source = source;
            checkbox.checked = collector.is_approved || !collector.requires_approval; // Assuming these properties exist
            
            // Check if controller exists before adding listener
            if (controller) {
                checkbox.addEventListener('change', (event) => {
                    // Call the controller method to handle the logic
                    controller.handleCollectorApprovalChange(event);
                });
            } else {
                checkbox.disabled = true; // Disable if no controller to handle changes
            }

            const label = document.createElement('label');
            label.className = 'form-check-label'; // Bootstrap styling
            label.htmlFor = checkboxId;
            // Use textContent for safety, construct HTML carefully
            label.innerHTML = `
                <span class="collector-name fw-bold">${escapeHtml(collector.name)}</span>
                <small class="collector-description d-block text-muted">${escapeHtml(collector.description || 'No description')}</small>
                ${collector.requires_approval ? '<span class="badge bg-warning text-dark me-1">Requires Approval</span>' : '<span class="badge bg-success me-1">Auto-approved</span>'}
                ${collector.scope ? `<span class="badge bg-info">${escapeHtml(collector.scope)}</span>` : ''}
            `;

            item.appendChild(checkbox);
            item.appendChild(label);
            listElement.appendChild(item);
        });

        if (count === 0) {
            // Display a more informative message if filtering resulted in empty list
            if (currentScope === 'all') {
                listElement.innerHTML = '<small class="text-muted">No collectors available.</small>';
            } else {
                listElement.innerHTML = `<small class="text-muted">No ${source} collectors available for scope '${currentScope}'.</small>`;
            }
        }
    };

    // Initial population - Pass the controller's current scope
    const currentScope = controller?.currentScope || 'all'; 
    populateList(serverList, collectorsData?.server || [], 'server', currentScope);
    populateList(browserList, collectorsData?.browser || [], 'browser', currentScope);

    // 4. Setup Search Filter
    const searchInputElement = contentElement.querySelector('#collector-search-input');
    if (searchInputElement) {
        searchInputElement.addEventListener('input', (event) => {
            const searchTerm = event.target.value.toLowerCase().trim();
            listsContainer.querySelectorAll('.collector-item').forEach(item => {
                const collectorName = item.dataset.collectorName?.toLowerCase() || '';
                const collectorDescription = item.querySelector('.collector-description')?.textContent.toLowerCase() || '';
                // Show if search term is in name or description
                if (collectorName.includes(searchTerm) || collectorDescription.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
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

    console.log("[CollectorsList] Initialization complete.");
    // Remove TODOs as scope filtering is now implemented
    // TODO: Add logic for handling collector selection/approval changes.
    // TODO: Connect scope filtering (if needed within the widget) to controller state.
}