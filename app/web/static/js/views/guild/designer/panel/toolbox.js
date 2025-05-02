/**
 * toolbox.js
 * 
 * Handles the logic for the Toolbox Panel in the Guild Structure Designer.
 * - Fetches component definitions from API.
 * - Renders components dynamically.
 * - Makes toolbox items draggable using jQuery UI.
 */

import { apiRequest, showToast } from '/static/js/components/common/notifications.js';

// Define hardcoded structure elements outside try/catch
// TODO: Remove this section once API provides structure elements reliably
const structureElements = [
    { component_key: 'category', component_type: 'structure', metadata: { display_name: 'New Category', icon: 'fas fa-folder text-warning' } },
    { component_key: 'text_channel', component_type: 'structure', metadata: { display_name: 'New Text Channel', icon: 'fas fa-hashtag text-info' } },
    { component_key: 'voice_channel', component_type: 'structure', metadata: { display_name: 'New Voice Channel', icon: 'fas fa-volume-up text-info' } },
];

// Function to render components and make them draggable
async function renderToolboxComponents() {
    console.log("[Toolbox] Fetching and rendering toolbox components...");
    const listElement = document.getElementById('toolbox-list');
    if (!listElement) {
        console.error("[Toolbox] List element #toolbox-list not found!");
        return;
    }

    listElement.innerHTML = '<li class="list-group-item text-muted small">Loading components...</li>'; // Placeholder

    let apiComponents = []; // Store components from API

    try {
        console.log("[Toolbox] Fetching components from API: /api/v1/dashboards/components");
        const response = await apiRequest('/api/v1/dashboards/components', { method: 'GET' });
        
        // Basic validation of the response structure
        if (response && Array.isArray(response.components)) {
            apiComponents = response.components;
            console.log(`[Toolbox] Received ${apiComponents.length} components from API.`);
        } else {
            console.warn("[Toolbox] API response format unexpected or empty:", response);
            // Don't throw error here, proceed with hardcoded elements
        }

    } catch (error) {
        console.error("[Toolbox] Error fetching components from API:", error);
        showToast("Error loading dynamic components. Displaying defaults.", "error");
        // API failed, we will only render structureElements below
    }

    // Always clear the list before rendering
    listElement.innerHTML = ''; 

    // Combine hardcoded structure elements and API components
    const combinedItems = [...structureElements];
    const structureKeys = new Set(structureElements.map(el => el.component_key));
    apiComponents.forEach(comp => {
        if (!structureKeys.has(comp.component_key)) {
            combinedItems.push(comp);
        }
    });

    if (combinedItems.length === 0) {
         listElement.innerHTML = '<li class="list-group-item text-muted small">No components available.</li>';
         console.log("[Toolbox] No components (API or hardcoded) to render.");
         return; // Nothing more to do
    }

    // --- Group components by category (using dashboard_type) --- 
    const groupedComponents = combinedItems.reduce((groups, comp) => {
        // Validate component structure minimally before grouping
        if (!comp || !comp.component_key || !comp.metadata || !comp.metadata.display_name) {
             console.warn("[Toolbox Grouping] Skipping invalid component data:", comp);
             return groups; // Skip invalid items
        }
        
        // Determine the category group key
        let categoryKey = 'Other'; // Default group
        if (comp.component_type === 'structure') {
             categoryKey = 'Structure Elements'; // Keep structure items separate
        } else if (comp.dashboard_type && typeof comp.dashboard_type === 'string') {
            // Use dashboard_type as the primary grouping key
             categoryKey = comp.dashboard_type.trim();
        } 
        // Capitalize category key for display
        const displayCategory = categoryKey.charAt(0).toUpperCase() + categoryKey.slice(1);

        // Initialize the category array if it doesn't exist
        if (!groups[displayCategory]) { // Use displayCategory as key for the groups object
            groups[displayCategory] = [];
        }
        // Add the component to its category group
        groups[displayCategory].push(comp);
        return groups;
    }, {});
    // ------------------------------------

    // --- Render grouped components --- 
    const sortedCategories = Object.keys(groupedComponents).sort((a, b) => {
        // Ensure 'Structure Elements' comes first, then alphabetical by dashboard type
        if (a === 'Structure Elements') return -1;
        if (b === 'Structure Elements') return 1;
        // Add other special categories if needed, e.g., 'Common' might come next
        if (a === 'Common') return -1;
        if (b === 'Common') return 1;
        return a.localeCompare(b);
    });

    let totalRendered = 0;
    sortedCategories.forEach(category => {
        // Add category header
        const headerLi = document.createElement('li');
        // Basic header styling, can be improved with CSS
        headerLi.className = 'list-group-item list-group-item-secondary text-uppercase small fw-bold'; 
        headerLi.textContent = category;
        listElement.appendChild(headerLi);

        // Render components within this category
        groupedComponents[category].forEach(comp => {
            // Validation already done in grouping stage, but double-check metadata again just in case
             if (!comp.metadata || !comp.metadata.display_name) {
                 console.warn("[Toolbox Rendering] Skipping component due to missing metadata/display_name after grouping:", comp);
                 return;
             }

            const li = document.createElement('li');
            li.classList.add('list-group-item', 'toolbox-item');
            li.setAttribute('data-component-key', comp.component_key);
            li.setAttribute('data-component-type', comp.component_type || 'unknown');

            const iconClass = comp.metadata.icon || 'fas fa-puzzle-piece';
            li.innerHTML = `<i class="${iconClass} me-2"></i> ${comp.metadata.display_name}`;
            
            listElement.appendChild(li);
            totalRendered++;
        });
    });
    // ------------------------------------

    makeItemsDraggable(); // Make all newly added items draggable
    console.log(`[Toolbox] Rendered ${totalRendered} components across ${sortedCategories.length} categories.`);
}


// Function to make list items draggable
function makeItemsDraggable() {
    $("#toolbox-list .toolbox-item").draggable({
        helper: "clone",
        revert: "invalid",
        containment: "document", // Allow dragging anywhere initially
        cursor: "move",
        opacity: 0.7,
        zIndex: 1000, // Ensure helper is above other elements
        start: function(event, ui) {
            console.log("[Draggable] Start dragging:", $(this).data('component-key'));
            // Optional: Add a class to the helper for specific styling
            ui.helper.addClass("toolbox-item-dragging"); 
        },
        stop: function(event, ui) {
            console.log("[Draggable] Stop dragging:", $(this).data('component-key'));
        }
    });
    console.log("[Toolbox] Initialized draggable for toolbox items.");
}

// Main initialization function for the toolbox
export function initializeToolbox() {
    console.log("[Toolbox] Initializing toolbox...");
    
    // Ensure jQuery UI is loaded
    if (typeof $.ui === 'undefined' || typeof $.ui.draggable === 'undefined') {
        console.error("[Toolbox] jQuery UI or Draggable not loaded!");
        showToast("Toolbox functionality might be limited: jQuery UI missing.", "warning");
        // Optionally, try to load it dynamically or just render non-draggable items
        // For now, we just proceed, renderToolboxComponents will still run
    }

    // Fetch and render components
    renderToolboxComponents().catch(error => {
        // Catch potential errors from renderToolboxComponents itself (though handled inside)
        console.error("[Toolbox] Unexpected error during initial render:", error);
        const listElement = document.getElementById('toolbox-list');
        if (listElement) {
            listElement.innerHTML = '<li class="list-group-item text-danger">Critical toolbox init error.</li>';
        }
    });

    console.log("[Toolbox] Toolbox module loaded successfully.");
}

// Initial log
console.log("[Toolbox] Toolbox module loaded."); 