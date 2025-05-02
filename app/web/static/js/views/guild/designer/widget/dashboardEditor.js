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
        
        // Delay droppable setup slightly to ensure canvas is ready
        setTimeout(() => {
            this._setupDroppable();
        }, 100); // 100ms delay, adjust if needed

        // REMOVED event listener for node selection
        // document.addEventListener('designerNodeSelected', handleNodeSelection);
        
        // Initial state message - Encourage loading or creating a dashboard
        if (this.canvas.length > 0) {
           this.canvas.html('<p class="text-muted">Load an existing dashboard or drop "New Dashboard" here to start.</p>');
        }
    }

    _setupDroppable() {
        if (!this.canvas || this.canvas.length === 0) {
            console.error("[DashboardEditor] Canvas element (#dashboard-editor-canvas) not found within this.element, cannot initialize droppable.");
            return;
        }
        // --- DEBUG LOGGING ---
        const canvasElement = this.canvas[0]; // Get the raw DOM element
        console.log(`[DashboardEditor Debug] Canvas check before droppable:
           - Found: ${!!canvasElement}
           - Visible: ${this.canvas.is(':visible')}
           - Width: ${this.canvas.width()}px
           - Height: ${this.canvas.height()}px
           - OuterWidth: ${this.canvas.outerWidth()}px
           - OuterHeight: ${this.canvas.outerHeight()}px`
        );
        // --- END DEBUG LOGGING ---
        if (typeof $.ui === 'undefined' || typeof $.ui.droppable === 'undefined') {
            console.error("[DashboardEditor] jQuery UI Droppable is not loaded.");
            return;
        }

        console.log("[DashboardEditor] Setting up droppable on canvas:", this.canvas);

        // Use arrow function to ensure 'this' refers to the DashboardEditor instance
        // Make the drop handler async to use await for apiRequest
        this.canvas.droppable({
            accept: ".toolbox-item", 
            drop: async (event, ui) => { // Make handler async
                const droppedItem = ui.draggable;
                const elementType = droppedItem.data('element-type'); // Keep for potential other uses, but less relevant now
                const componentKey = droppedItem.data('component-key');
                const componentType = droppedItem.data('component-type'); // Use this for checking the drop type

                console.log(`[DashboardEditor] Drop detected on editor canvas. ComponentKey: ${componentKey}, ComponentType: ${componentType}`);
                console.log(`[DashboardEditor] Current editing dashboard ID: ${currentEditingDashboardId}`);

                // Remove the logic for handling 'dashboard-config-structure' drops here.
                // This type of drop should be handled by the structure tree, not the editor itself.
                /*
                if (componentType === 'dashboard-config-structure') {
                    console.log('[DashboardEditor] Handling drop of "New Dashboard Config" element. -> THIS LOGIC IS REMOVED/MOVED');
                    // ... removed API call logic ...
                    return; // Stop processing here if it was a new dashboard drop (shouldn't happen now)
                } 
                */

                // Handle drops of actual dashboard components (widgets) onto the canvas
                if (componentKey && componentType !== 'structure' && componentType !== 'dashboard-config-structure') { 
                    console.log(`[DashboardEditor] Handling drop of component: ${componentKey} (${componentType})`);

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
                    // Log unexpected drops onto the editor canvas
                    console.warn(`[DashboardEditor] Dropped item on canvas is not a dashboard component. Type: ${componentType}, Key: ${componentKey}`);
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