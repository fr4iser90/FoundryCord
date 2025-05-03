/**
 * toolbox.js
 * 
 * Handles the logic for the Toolbox Panel in the Guild Structure Designer.
 * - Fetches component definitions from API.
 * - Renders components dynamically.
 * - Makes toolbox items draggable using jQuery UI.
 */

import { apiRequest, showToast } from '/static/js/components/common/notifications.js';

// Define hardcoded structure elements
const structureElements = [
    { component_key: 'category', component_type: 'structure', metadata: { display_name: 'New Category', icon: 'fas fa-folder text-warning' } },
    { component_key: 'text_channel', component_type: 'structure', metadata: { display_name: 'New Text Channel', icon: 'fas fa-hashtag text-info' } },
    { component_key: 'voice_channel', component_type: 'structure', metadata: { display_name: 'New Voice Channel', icon: 'fas fa-volume-up text-info' } },
];

// Define element to create a new dashboard configuration
const dashboardStructureElements = [
    { component_key: 'new_dashboard_config', component_type: 'dashboard-config-structure', metadata: { display_name: 'New Dashboard', icon: 'bi bi-layout-wtf text-success' } }
];

// Helper to sanitize category names for use in IDs
function sanitizeForId(name) {
    return name.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-');
}

// Function to render components into the tab structure
async function renderToolboxComponents() {
    console.log("[Toolbox] Fetching and rendering toolbox components into tabs...");
    
    // Get references to the tab content panes' UL elements
    const structureList = document.querySelector('#tab-pane-structure .toolbox-list-group');
    const dashboardsList = document.querySelector('#tab-pane-dashboards .toolbox-list-group');
    // Get references to the tab navigation and content containers (optional, for clearing)
    const tabNav = document.getElementById('toolbox-tabs'); 
    const tabContent = document.getElementById('toolbox-tab-content');

    if (!structureList || !dashboardsList || !tabNav || !tabContent) {
        console.error("[Toolbox] Required tab elements (#tab-pane-structure, #tab-pane-dashboards, #toolbox-tabs, #toolbox-tab-content) not found!");
        return;
    }

    // Clear existing content and set loading placeholders
    structureList.innerHTML = '<li class="list-group-item text-muted small">Loading structure...</li>';
    dashboardsList.innerHTML = '<li class="list-group-item text-muted small">Loading dashboards...</li>';

    // --- Fetch API Components ---
    let apiComponents = [];
    try {
        console.log("[Toolbox] Fetching components from API: /api/v1/dashboards/components");
        const response = await apiRequest('/api/v1/dashboards/components', { method: 'GET' });
        if (response && Array.isArray(response.components)) {
            apiComponents = response.components;
            console.log(`[Toolbox] Received ${apiComponents.length} components from API.`);
        } else {
            console.warn("[Toolbox] API response format unexpected or empty:", response);
        }
    } catch (error) {
        console.error("[Toolbox] Error fetching components from API:", error);
        showToast("Error loading dynamic components.", "error"); // Simplified message
    }

    // --- Fetch Saved Dashboard Configurations ---
    let savedConfigs = [];
    try {
        console.log("[Toolbox] Fetching saved configurations from API: /api/v1/dashboards/configurations");
        // Assuming the list endpoint returns an array directly or similar to components { configurations: [] }
        // Adjust based on actual API response structure
        const configResponse = await apiRequest('/api/v1/dashboards/configurations', { method: 'GET' });
        // Check if the response itself is the array or if it's nested
        if (Array.isArray(configResponse)) {
             savedConfigs = configResponse;
        } else if (configResponse && Array.isArray(configResponse.configurations)) { // Example nested structure
            savedConfigs = configResponse.configurations;
        } else {
             console.warn("[Toolbox] Saved configurations API response format unexpected or empty:", configResponse);
        }
         console.log(`[Toolbox] Received ${savedConfigs.length} saved configurations from API.`);
    } catch (error) {
         console.error("[Toolbox] Error fetching saved configurations from API:", error);
         showToast("Error loading saved dashboards.", "error");
    }
    // --------------------------------------------

    // --- Separate items into Structure and Dashboards --- 
    const dashboardItems = apiComponents.filter(comp => comp.component_type !== 'structure');
    
    // Clear placeholders before rendering actual items
    structureList.innerHTML = '';
    dashboardsList.innerHTML = '';

    // --- Render Structure Tab --- 
    if (structureElements.length === 0) {
        structureList.innerHTML = '<li class="list-group-item text-muted small">No structure elements defined.</li>';
    } else {
        structureElements.forEach(comp => {
            renderComponentItem(structureList, comp);
        });
    }
    console.log(`[Toolbox] Rendered ${structureElements.length} structure items.`);

    // --- Render Dashboards Tab --- 
    
    // Clear placeholder first
    dashboardsList.innerHTML = '';

    // Render the \"New Dashboard\" draggable item
    if (dashboardStructureElements.length > 0) {
        dashboardStructureElements.forEach(comp => {
            renderComponentItem(dashboardsList, comp); 
        });
    } else {
        console.warn("[Toolbox] dashboardStructureElements array is empty!");
    }
    
    // --- Render Saved Configurations ---
    const savedConfigsHeader = document.createElement('li');
    savedConfigsHeader.className = 'list-group-item list-group-item-secondary text-uppercase small fw-bold mt-3'; // Header styling
    savedConfigsHeader.textContent = 'Saved Configurations';
    dashboardsList.appendChild(savedConfigsHeader);

    if (savedConfigs.length === 0) {
        const noConfigsLi = document.createElement('li');
        noConfigsLi.className = 'list-group-item text-muted small';
        noConfigsLi.textContent = 'No saved configurations found.';
        dashboardsList.appendChild(noConfigsLi);
    } else {
        savedConfigs.forEach(config => {
            const li = document.createElement('li');
            // Make these clickable, not draggable
            li.className = 'list-group-item list-group-item-action toolbox-load-config-item'; // Use distinct class
            li.setAttribute('data-config-id', config.id);
            li.innerHTML = `<i class="bi bi-file-earmark-text me-2"></i> ${config.name} <span class="text-muted small">(${config.dashboard_type})</span>`;
            li.style.cursor = 'pointer'; // Indicate clickability
            dashboardsList.appendChild(li);
        });
        console.log(`[Toolbox] Rendered ${savedConfigs.length} saved configurations.`);
    }
    // ------------------------------------

    // Add a visual separator before API components if there are any
    if (dashboardItems.length > 0) {
        const separator = document.createElement('hr');
        separator.classList.add('my-2'); 
        dashboardsList.appendChild(separator);
    }
    
    // Now, handle the API components (dashboard widgets)
    if (dashboardItems.length === 0) {
        // Don't add "No components" if we added saved configs
        // const noComponentsLi = document.createElement('li');
        // noComponentsLi.className = 'list-group-item text-muted small';
        // noComponentsLi.textContent = 'No dashboard components available.';
        // dashboardsList.appendChild(noComponentsLi);
    } else {
        // Group dashboard components by dashboard_type
        const groupedDashboards = dashboardItems.reduce((groups, comp) => {
            if (!comp || !comp.component_key || !comp.metadata || !comp.metadata.display_name) {
                 console.warn("[Toolbox Grouping - Dashboards] Skipping invalid component data:", comp);
                 return groups;
            }
            let categoryKey = (comp.dashboard_type && typeof comp.dashboard_type === 'string') ? comp.dashboard_type.trim() : 'Other';
            const displayCategory = categoryKey.charAt(0).toUpperCase() + categoryKey.slice(1);
            if (!groups[displayCategory]) {
                groups[displayCategory] = [];
            }
            groups[displayCategory].push(comp);
            return groups;
        }, {});

        // Sort dashboard categories 
        const sortedDashboardCategories = Object.keys(groupedDashboards).sort((a, b) => {
            if (a === 'Common') return -1;
            if (b === 'Common') return 1;
            if (a === 'Other') return 1; // Push Other to the end
            if (b === 'Other') return -1;
            return a.localeCompare(b);
        });

        // Render category headers and items
        let totalDashboardsRendered = 0;
        sortedDashboardCategories.forEach(category => {
            // Add category header within the dashboard list
            const headerLi = document.createElement('li');
            headerLi.className = 'list-group-item list-group-item-light text-uppercase small fw-bold'; // Slightly different styling for subgroup
            headerLi.textContent = category;
            dashboardsList.appendChild(headerLi);

            // Render components within this category
            groupedDashboards[category].forEach(comp => {
                renderComponentItem(dashboardsList, comp); // This makes them draggable
                totalDashboardsRendered++;
            });
        });
         console.log(`[Toolbox] Rendered ${totalDashboardsRendered} dashboard items across ${sortedDashboardCategories.length} groups.`);
    }

    makeItemsDraggable(); // Apply draggable only to component items
    console.log("[Toolbox] Finished rendering components and configurations into tabs.");
}

// Helper function to render a single component item (Draggable or Static for New Dashboard)
function renderComponentItem(listElement, comp) {
    // Validation
    if (!comp.metadata || !comp.metadata.display_name) {
        console.warn("[Toolbox RenderItem] Skipping component due to missing metadata/display_name:", comp);
        return;
    }

    const li = document.createElement('li');
    // Apply base list-group-item style
    li.classList.add('list-group-item'); 

    const iconClass = comp.metadata.icon || 'fas fa-puzzle-piece'; // Default icon

    // Special handling for New Dashboard to add the button inline
    if (comp.component_type === 'dashboard-config-structure') {
        // Make the LI draggable for the "New Dashboard" part
        li.classList.add('toolbox-item'); 
        li.setAttribute('data-component-key', comp.component_key);
        li.setAttribute('data-component-type', comp.component_type || 'unknown');
        
        // Use innerHTML to create the flex structure with the button
        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>
                    <i class="${iconClass} me-2"></i> 
                    ${comp.metadata.display_name}
                </span>
                <button class="btn btn-sm btn-outline-success ms-2" id="toolbox-add-dashboard-btn" type="button" title="Add new dashboard configuration">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        `;
    } else {
        // Default rendering and draggable behavior for other items
        li.classList.add('toolbox-item'); 
        li.setAttribute('data-component-key', comp.component_key);
        li.setAttribute('data-component-type', comp.component_type || 'unknown');
        li.innerHTML = `<i class="${iconClass} me-2"></i> ${comp.metadata.display_name}`;
    }

    listElement.appendChild(li);
}


// Function to make list items draggable (Updated Selector for specific items)
function makeItemsDraggable() {
    // Select only items intended to be draggable components
    $("#toolbox-tab-content .toolbox-item").draggable({
        helper: "clone",
        revert: "invalid",
        containment: "document",
        cursor: "move",
        opacity: 0.7,
        zIndex: 1000,
        start: function(event, ui) {
            console.log("[Draggable] Start dragging:", $(this).data('component-key'));
            ui.helper.addClass("toolbox-item-dragging");
        },
        stop: function(event, ui) {
            console.log("[Draggable] Stop dragging:", $(this).data('component-key'));
        }
    });
    // Do NOT make .toolbox-load-config-item draggable here
    console.log("[Toolbox] Initialized/Re-initialized draggable for toolbox component items in tabs.");
}

// --- NEW: Handler for clicking a saved configuration ---
async function handleLoadConfigurationClick(event) {
    // Find the list item element that was clicked
    const targetElement = event.target.closest('.toolbox-load-config-item');
    if (!targetElement) return; // Click wasn't on a loadable item

    const configId = targetElement.dataset.configId;
    if (!configId) {
        console.error("[Toolbox] Clicked config item missing data-config-id attribute.");
        return;
    }

    console.log(`[Toolbox] Requesting load for configuration ID: ${configId}`);
    showToast(`Loading dashboard config ${configId}...`, 'info', 2000); // Short duration toast

    try {
        const apiUrl = `/api/v1/dashboards/configurations/${configId}`;
        const configData = await apiRequest(apiUrl, { method: 'GET' });

        if (!configData || !configData.id) {
             console.error(`[Toolbox] Failed to load configuration ${configId} or response invalid.`, configData);
             showToast(`Error: Could not load configuration ${configId}.`, 'error');
             return;
        }
        
        console.log(`[Toolbox] Configuration ${configId} loaded successfully. Dispatching event.`, configData);
        
        // Dispatch the custom event with the loaded data
        document.dispatchEvent(new CustomEvent('dashboardConfigLoaded', {
            detail: { configData: configData } 
        }));
        
        showToast(`Dashboard '${configData.name}' loaded.`, 'success');

    } catch (error) {
        console.error(`[Toolbox] Error fetching configuration details for ID ${configId}:`, error);
        // apiRequest usually shows a toast on error, but we can add a specific one
        showToast(`Failed to fetch dashboard ${configId}.`, 'error');
    }
}
// ----------------------------------------------------


// Main initialization function for the toolbox
export function initializeToolbox() {
    console.log("[Toolbox] Initializing toolbox with tabs...");
    
    if (typeof $.ui === 'undefined' || typeof $.ui.draggable === 'undefined') {
        console.error("[Toolbox] jQuery UI or Draggable not loaded!");
        showToast("Toolbox functionality might be limited: jQuery UI missing.", "warning");
    }

    // Fetch and render components into the new tab structure
    renderToolboxComponents().catch(error => {
        console.error("[Toolbox] Unexpected error during initial tab render:", error);
        const tabContent = document.getElementById('toolbox-tab-content');
        if(tabContent) {
            tabContent.innerHTML = '<div class="p-3 text-danger">Critical toolbox initialization error. Cannot load components.</div>';
        } else {
            showToast("Critical toolbox initialization error.", "error");
        }
    });

    // Add event listener for the new add button *inside* the dashboard tab
    // Use event delegation on the container in case the button is re-rendered
    const dashboardsListContainer = document.querySelector('#tab-pane-dashboards .toolbox-list-group');
    if (dashboardsListContainer) {
        // Listener for the "+" button next to "New Dashboard"
        dashboardsListContainer.addEventListener('click', async (event) => {
            if (event.target.closest('#toolbox-add-dashboard-btn')) {
                console.log("[Toolbox] 'Add new dashboard' button clicked.");
                event.preventDefault();
                event.stopPropagation(); // Prevent other listeners if needed

                // Prompt user for a name
                const newDashboardName = prompt("Enter a name for the new dashboard configuration:");

                // Validate the input
                if (!newDashboardName || newDashboardName.trim() === "") {
                    showToast("Dashboard name cannot be empty.", "warning");
                    console.log("[Toolbox] New dashboard creation cancelled: Empty name provided.");
                    return; // Stop execution if name is invalid
                }
                const trimmedName = newDashboardName.trim();

                // Disable button temporarily
                const addButton = event.target.closest('#toolbox-add-dashboard-btn');
                if (addButton) addButton.disabled = true;

                showToast("Creating new dashboard configuration...", "info");
                try {
                    const response = await apiRequest('/api/v1/dashboards/configurations', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        // Send minimal required data for creation
                        body: JSON.stringify({
                            name: trimmedName,
                            dashboard_type: "custom", // Default type remains custom
                            description: "A newly created dashboard."
                        })
                    });

                    if (response && response.id) {
                        console.log(`[Toolbox] New dashboard created successfully. ID: ${response.id}, Name: ${trimmedName}. Dispatching event.`);
                        showToast(`New dashboard '${trimmedName}' created.`, 'success');

                        // Dispatch event for other widgets to know a new config was made
                        document.dispatchEvent(new CustomEvent('dashboardConfigCreated', {
                            detail: { newConfigData: response } // Send the full response
                        }));

                        // Optionally, re-render the toolbox to show the new item in the list
                        await renderToolboxComponents();

                    } else {
                        console.error("[Toolbox] Failed to create new dashboard configuration. Invalid response:", response);
                        showToast("Error: Could not create new dashboard.", 'error');
                    }
                } catch (error) {
                    console.error("[Toolbox] Error creating new dashboard configuration:", error);
                    // apiRequest should show an error toast, possibly add detail?
                    // Example: showToast(`Error creating dashboard: ${error.message || 'Unknown error'}`, 'error');
                } finally {
                     // Re-enable button
                     if (addButton) addButton.disabled = false;
                }
            }

            // --- NEW: Listener for loading saved configurations ---
            if (event.target.closest('.toolbox-load-config-item')) {
                handleLoadConfigurationClick(event);
            }
            // -----------------------------------------------------
        });
    } else {
        console.warn("[Toolbox] Could not find dashboards list container (#tab-pane-dashboards .toolbox-list-group) to attach listeners.");
    }
}

console.log("[Toolbox] Toolbox module loaded.");