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
    // We might not need to clear tabNav if we pre-defined the buttons in HTML, but good practice
    // tabNav.innerHTML = ''; // Assuming tabs are now static in HTML

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
        showToast("Error loading dynamic components. Using defaults.", "error");
    }

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

    // --- Render Dashboards Tab (with internal grouping) --- 
    
    // Clear placeholder first
    dashboardsList.innerHTML = '';

    // Render the "New Dashboard" draggable item (which now includes the inline button via renderComponentItem)
    if (dashboardStructureElements.length > 0) {
        dashboardStructureElements.forEach(comp => {
            renderComponentItem(dashboardsList, comp); 
        });
    } else {
        console.warn("[Toolbox] dashboardStructureElements array is empty!");
    }
    
    // Optional: Add a visual separator if there are API components below
    if (dashboardItems.length > 0) {
        const separator = document.createElement('hr');
        separator.classList.add('my-2'); 
        dashboardsList.appendChild(separator);
    }
    
    // Now, handle the API components (dashboard widgets)
    if (dashboardItems.length === 0) {
        // Append message only if New Dashboard wasn't added either
        if (dashboardStructureElements.length === 0) {
            dashboardsList.innerHTML = '<li class="list-group-item text-muted small">No dashboard components available.</li>';
        }
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

        // Sort dashboard categories (e.g., Common first, then alphabetical)
        const sortedDashboardCategories = Object.keys(groupedDashboards).sort((a, b) => {
            if (a === 'Common') return -1;
            if (b === 'Common') return 1;
            if (a === 'Other') return 1; // Push Other to the end
            if (b === 'Other') return -1;
            return a.localeCompare(b);
        });

        let totalDashboardsRendered = 0;
        sortedDashboardCategories.forEach(category => {
            // Add category header within the dashboard list
            const headerLi = document.createElement('li');
            headerLi.className = 'list-group-item list-group-item-light text-uppercase small fw-bold'; // Slightly different styling for subgroup
            headerLi.textContent = category;
            dashboardsList.appendChild(headerLi);

            // Render components within this category
            groupedDashboards[category].forEach(comp => {
                renderComponentItem(dashboardsList, comp);
                totalDashboardsRendered++;
            });
        });
         console.log(`[Toolbox] Rendered ${totalDashboardsRendered} dashboard items across ${sortedDashboardCategories.length} groups.`);
    }

    makeItemsDraggable(); // Apply draggable to items in both tabs
    console.log("[Toolbox] Finished rendering components into tabs.");
}

// Helper function to render a single component item
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


// Function to make list items draggable (Updated Selector)
function makeItemsDraggable() {
    // Select items within the tab content area
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
    console.log("[Toolbox] Initialized/Re-initialized draggable for toolbox items in tabs.");
}

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
        // Simplified error display within the content area
        const tabContent = document.getElementById('toolbox-tab-content');
        if(tabContent) {
            tabContent.innerHTML = '<div class="p-3 text-danger">Critical toolbox initialization error. Cannot load components.</div>';
        } else {
            showToast("Critical toolbox initialization error.", "error");
        }
    });

    // Remove previous listener
    // const addButton = document.getElementById('toolbox-add-btn'); 
    // if (addButton) { addButton.removeEventListener(...) } // Need to store listener to remove properly

    // Add event listener for the new add button *inside* the dashboard tab
    // Use event delegation on the container in case the button is re-rendered
    const dashboardsListContainer = document.querySelector('#tab-pane-dashboards .toolbox-list-group');
    if (dashboardsListContainer) {
        dashboardsListContainer.addEventListener('click', async (event) => {
            const clickedButton = event.target.closest('#toolbox-add-dashboard-btn');
            if (clickedButton) {
                console.log("[Toolbox] Add New Dashboard Configuration button clicked. Triggering API call...");
                // --- Direct API call to create new config --- 
                const defaultName = `New Dashboard ${Date.now()}`;
                // Use a default type or leave it to backend? Let's assume a default is needed.
                const defaultType = 'custom'; 
                const apiUrl = '/api/v1/dashboards/configurations';
                const payload = { 
                    name: defaultName,
                    dashboard_type: defaultType 
                    // description and config will be empty/null by default in backend
                };

                clickedButton.disabled = true; // Disable button during API call
                showToast('info', 'Creating new dashboard configuration...');

                try {
                    const newConfig = await apiRequest(apiUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    if (newConfig && newConfig.id) {
                        console.log("[Toolbox] New dashboard config created successfully:", newConfig);
                        showToast('success', `Created: ${newConfig.name}`);
                        
                        // Dispatch event to load the new config into editor/config widgets
                        console.log("[Toolbox] Dispatching 'dashboardConfigLoaded' for new config.");
                        document.dispatchEvent(new CustomEvent('dashboardConfigLoaded', { 
                            detail: { 
                                configData: newConfig, 
                                isNew: true
                            } 
                        }));

                    } else {
                         throw new Error("Invalid response received after creating dashboard config.");
                    }

                } catch (error) {
                    console.error("[Toolbox] Error creating dashboard configuration:", error);
                    // showToast handled by apiRequest usually, but maybe add a specific one?
                    showToast('error', 'Failed to create new dashboard configuration.');
                } finally {
                    clickedButton.disabled = false; // Re-enable button
                }
                // -------------------------------------------
            }
        });
        console.log("[Toolbox] Event listener added for #toolbox-add-dashboard-btn.");
    } else {
        console.warn("[Toolbox] Dashboards list container not found for event delegation.");
    }

    // Optional: Initialize Bootstrap Tabs if needed (often handled automatically via data-bs-toggle)
    // const triggerTabList = [].slice.call(document.querySelectorAll('#toolbox-tabs button'))
    // triggerTabList.forEach(function (triggerEl) {
    //   const tabTrigger = new bootstrap.Tab(triggerEl)
    //   // Optional: Add listeners if needed
    // })

    console.log("[Toolbox] Toolbox module with tabs loaded successfully.");
}

// Initial log
console.log("[Toolbox] Toolbox module loaded."); 