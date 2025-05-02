/**
 * dashboardEditor.js
 * 
 * Logic for the Dashboard Editor widget. Allows users to build and configure
 * dashboard instances using components from the toolbox.
 */

import { apiRequest, showToast } from '/static/js/components/common/notifications.js';

// Module-level variable to store the currently edited dashboard config ID
let currentEditingDashboardId = null;
let dashboardEditorInstance = null; // To access instance methods if needed

/**
 * Represents and manages the Dashboard Editor widget.
 */
class DashboardEditor {
    constructor(element, guildId, initialContext) {
        this.element = $(element); // Ensure it's a jQuery object
        this.guildId = guildId;
        this.canvas = this.element.find('#dashboard-editor-canvas');
        // We don't store channelId here anymore
        dashboardEditorInstance = this; // Store instance for potential external access?
        console.log(`[DashboardEditor] Instantiated for Guild ID: ${guildId}.`);
        this._setupDroppable();
        
        // REMOVED event listener for node selection
        // document.addEventListener('designerNodeSelected', handleNodeSelection);
        
        // Initial state message - Encourage loading or creating a dashboard
        if (this.canvas.length > 0) {
           this.canvas.html('<p class="text-muted">Load an existing dashboard or drop "New Dashboard" here to start.</p>');
        }
    }

    _setupDroppable() {
        if (!this.canvas || this.canvas.length === 0) {
            console.error("[DashboardEditor] Canvas element not found, cannot initialize droppable.");
            return;
        }
        if (typeof $.ui === 'undefined' || typeof $.ui.droppable === 'undefined') {
            console.error("[DashboardEditor] jQuery UI Droppable is not loaded.");
            return;
        }

        console.log("[DashboardEditor] Setting up droppable on canvas:", this.canvas);

        // Use arrow function to ensure 'this' refers to the DashboardEditor instance
        this.canvas.droppable({
            accept: ".toolbox-item", 
            drop: (event, ui) => { 
                const droppedItem = ui.draggable; 
                const elementType = droppedItem.data('element-type');
                const componentKey = droppedItem.data('component-key'); 
                const componentType = droppedItem.data('component-type');

                console.log(`[DashboardEditor] Drop detected. ElementType: ${elementType}, ComponentKey: ${componentKey}, ComponentType: ${componentType}`);
                console.log(`[DashboardEditor] Current editing dashboard ID: ${currentEditingDashboardId}`);

                if (elementType === 'dashboard') {
                    console.log('[DashboardEditor] Handling drop of "New Dashboard" element.');
                    // --- REMOVED Channel check --- 
                    
                    // TODO: Call API to create a new dashboard configuration
                    // const newDashboardData = await apiRequest('/api/v1/dashboards/configurations', { method: 'POST' });
                    // if (newDashboardData && newDashboardData.dashboard_id) {
                    //     currentEditingDashboardId = newDashboardData.dashboard_id;
                    //     console.log(`[DashboardEditor] New dashboard configuration created with ID: ${currentEditingDashboardId}`);
                    //     this.canvas.html("<div>New Dashboard Ready (ID: " + currentEditingDashboardId + ")</div>"); // Clear canvas and show new state
                    //     // TODO: Potentially load initial structure or prompt user
                    // } else {
                    //     showToast('error', 'Failed to create new dashboard configuration.');
                    // }
                    this.canvas.html(`<p class="text-success">Initiated NEW dashboard configuration creation (Placeholder)</p>`);
                    currentEditingDashboardId = Date.now(); // Placeholder ID for now
                    console.log(`[DashboardEditor] Set placeholder editing ID: ${currentEditingDashboardId}`);

                } else if (componentKey) {
                    console.log(`[DashboardEditor] Handling drop of component: ${componentKey} (${componentType})`);
                    // --- REMOVED Channel check --- 

                    if (!currentEditingDashboardId) {
                         console.error("[DashboardEditor] Cannot add component: No dashboard loaded in editor.");
                         showToast('error', 'Please load or create a dashboard first before adding components.');
                         return;
                    }

                    // TODO: Fetch component definition based on componentKey
                    // TODO: Render the component onto the canvas for the currentEditingDashboardId
                    // TODO: Save the updated dashboard layout/config (API call for currentEditingDashboardId)
                    this.canvas.append(`<p class="text-info">Added component '${componentKey}' to dashboard ${currentEditingDashboardId} (Placeholder)</p>`);
                
                } else {
                    console.warn(`[DashboardEditor] Dropped item is not a dashboard or a known component. Type: ${elementType}, Key: ${componentKey}`);
                }
            }
        });
        console.log("[DashboardEditor] Droppable setup complete.");
    }

    // Placeholder for potential future methods
    // loadDashboard(dashboardId) { ... }
    // saveDashboard() { ... }
}

/**
 * Initializes the Dashboard Editor widget logic.
 * Finds the target element and instantiates the DashboardEditor class.
 * @param {string} containerSelector - CSS selector for the widget container.
 * @param {string} guildId - The current Guild ID (might not be needed directly by editor anymore).
 * @param {object} initialContext - Optional initial context data (e.g., initial dashboardId to load).
 */
export function initializeDashboardEditor(containerSelector = '#widget-content-dashboard-editor', guildId, initialContext = {}) {
    const editorElement = document.querySelector(containerSelector);

    if (!editorElement) {
        console.error(`[DashboardEditor] Container element "${containerSelector}" not found.`);
        return;
    }

    // GuildId might still be useful contextually, but not directly needed for core editing logic now.
    // if (!guildId) {
    //     console.error("[DashboardEditor] Guild ID is required for initialization.");
    //     return;
    // }

    console.log("[DashboardEditor] Initializing widget inside element:", editorElement);
    new DashboardEditor(editorElement, guildId, initialContext);
    console.log("[DashboardEditor] Initialization function complete.");
}

// Make sure the module indicates it's loaded.
console.log("dashboardEditor.js module loaded"); 