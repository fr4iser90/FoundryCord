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
// --- Module-level flag to prevent multiple listeners ---
let isConfigLoadedListenerAdded_Editor = false; 
// -----------------------------------------------------

/**
 * Represents and manages the Dashboard Editor widget.
 */
class DashboardEditor {
    // Constructor now only stores basic info and the *selector*
    constructor(contentAreaSelector, guildId, initialContext) {
        console.log(`[DashboardEditor Constructor] Initializing with selector: ${contentAreaSelector}`);
        this.contentAreaSelector = contentAreaSelector;
        this.guildId = guildId;
        this.initialContext = initialContext;
        this.element = null; // Will be set in initUI
        this.canvas = null;  // Will be set in initUI
        
        // We don't store channelId here anymore
        dashboardEditorInstance = this; // Store instance for potential external access?
        // --- Make instance accessible globally for debugging --- 
        //window.dashboardEditorInstance = this;
        // -----------------------------------------------------
        console.log(`[DashboardEditor Constructor] Instantiated for Guild ID: ${guildId}. UI setup deferred.`);
    }

    // Separate method to initialize UI elements after constructor
    initUI() {
        console.log(`[DashboardEditor initUI] Setting up UI for selector: ${this.contentAreaSelector}`);
        const contentAreaElement = document.querySelector(this.contentAreaSelector);
        if (!contentAreaElement) {
             console.error(`[DashboardEditor initUI] CRITICAL: Content area element "${this.contentAreaSelector}" not found!`);
             return false; // Indicate failure
        }
        this.element = $(contentAreaElement); // Set the element property (jQuery object)
        console.log(`[DashboardEditor initUI] Content area element found: ${!!contentAreaElement}`);

        // --- Create the canvas element dynamically --- 
        console.log(`[DashboardEditor initUI] Creating canvas element dynamically.`);
        const canvasDiv = document.createElement('div');
        canvasDiv.id = 'dashboard-editor-canvas';
        canvasDiv.style.minHeight = '150px'; // Apply necessary styles
        canvasDiv.style.border = '1px dashed #ccc';
        canvasDiv.style.padding = '10px';
        canvasDiv.innerHTML = '<p class="text-muted text-center small">Select or create a dashboard instance to edit.</p>'; // Initial placeholder text

        // Clear the container (which might have "Loading...") and append the canvas
        this.element.empty().append(canvasDiv);
        
        this.canvas = $(canvasDiv); // Set this.canvas to the new jQuery object
        console.log(`[DashboardEditor initUI] Canvas element created and appended. Found: ${this.canvas.length > 0}`);
        // --- End dynamic canvas creation ---

        if (this.canvas.length === 0) {
            // This check should theoretically never fail now, but keep for safety
            console.error("[DashboardEditor initUI] CRITICAL: Failed to create or find dynamically created canvas element!");
            this.element.html('<p class="text-danger p-2">Error: Failed to initialize editor canvas.</p>');
            return false; // Indicate failure
        } 
        
        // Setup droppable now that canvas is created and guaranteed to exist
        this._setupDroppable(); 
        
        console.log("[DashboardEditor initUI] UI setup complete." );

        // --- Add event listener ONCE --- 
        if (!isConfigLoadedListenerAdded_Editor) {
            document.addEventListener('dashboardConfigLoaded', (event) => {
                console.log("[DashboardEditor] Received 'dashboardConfigLoaded' event:", event.detail);
                const receivedConfigData = event.detail?.configData;
                if (receivedConfigData && receivedConfigData.id) {
                    currentEditingDashboardId = receivedConfigData.id;
                    console.log(`[DashboardEditor] Set currentEditingDashboardId via event: ${currentEditingDashboardId}`);
                    // Update the editor display
                    if (this.canvas) {
                        this.canvas.html(`<p class="text-success p-2">Loaded: ${receivedConfigData.name} (ID: ${receivedConfigData.id})</p>`);
                        // TODO: Add logic here later to parse receivedConfigData.config and render components
                    }
                } else {
                     console.warn("[DashboardEditor] 'dashboardConfigLoaded' event received without valid configData.");
                     // Optionally reset the editor view?
                     // currentEditingDashboardId = null;
                     // if (this.canvas) { this.canvas.html("<p class=\"text-muted p-2\">No dashboard loaded.</p>"); }
                }
            });
            isConfigLoadedListenerAdded_Editor = true;
            console.log("[DashboardEditor] 'dashboardConfigLoaded' listener added.");
        }
        // -----------------------------

        return true; // Indicate success
    }

    // --- Placeholder to simulate loading and dispatching --- 
    async _loadAndDispatchConfig(configIdToLoad) {
        console.log(`[DashboardEditor] Placeholder: Simulating load for config ID: ${configIdToLoad}`);
        // TODO: Replace this with actual API call to GET /api/v1/dashboards/configurations/{configIdToLoad}
        
        // Simulate fetching data
        await new Promise(resolve => setTimeout(resolve, 100)); // Simulate network delay

        // Hardcoded example data 
        const fakeConfigData = {
            id: configIdToLoad || 1, // Use passed ID or default
            name: `Fake Dashboard ${configIdToLoad || 1}`,
            description: "This is a simulated dashboard configuration.",
            dashboard_type: "system_monitor", 
            config: { 
                title: "System Overview (Simulated)", 
                color: "0xAA55FF", 
                components: [
                    { id: "cpu_load", type: "gauge", config: { label: "CPU Load", data_key: "cpu.load" } },
                    { id: "mem_usage", type: "gauge", config: { label: "Memory Usage", data_key: "memory.usage_percent" } }
                ]
            },
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };
        
        // --- Store the ID internally (important!) ---
        currentEditingDashboardId = fakeConfigData.id;
        console.log(`[DashboardEditor] Set currentEditingDashboardId to: ${currentEditingDashboardId}`);
        // ---------------------------------------------

        // --- Dispatch the event --- 
        console.log("[DashboardEditor] Dispatching 'dashboardConfigLoaded' event with data:", fakeConfigData);
        document.dispatchEvent(new CustomEvent('dashboardConfigLoaded', { 
            detail: { configData: fakeConfigData } 
        }));
        // ------------------------

        // Update the editor display (optional placeholder)
        if (this.canvas) {
            this.canvas.html(`<p class="text-success p-2">Loaded: ${fakeConfigData.name} (ID: ${fakeConfigData.id})</p>`);
        }
    }
    // --- End Placeholder ---

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
 * @param {string} containerSelector - CSS selector for the widget *content area*.
 * @param {string} guildId - The current Guild ID.
 * @param {object} initialContext - Optional initial context data.
 */
export function initializeDashboardEditor(containerSelector = '#widget-content-dashboard-editor', guildId, initialContext = {}) {
    console.log(`[InitializeDashboardEditor] Initializing for container selector: ${containerSelector}`);
    // The selector now directly points to the content area
    const editorContentElement = document.querySelector(containerSelector); 

    if (!editorContentElement) {
        console.error(`[InitializeDashboardEditor] Content element "${containerSelector}" not found.`);
        return null; // Return null to indicate failure
    }

    console.log("[InitializeDashboardEditor] Creating DashboardEditor instance ONLY...");
    try {
        // Create the instance
        const editorInstance = new DashboardEditor(containerSelector, guildId, initialContext);
        // --- DO NOT CALL initUI() here anymore --- 
        // It will be called via Gridstack's 'added' event
        
        console.log("[InitializeDashboardEditor] Instance created. UI Initialization deferred.");
        return editorInstance; // Return the instance 
    } catch (error) {
         console.error("[InitializeDashboardEditor] Error during DashboardEditor instantiation:", error);
         if (editorContentElement) {
             editorContentElement.innerHTML = '<p class="text-danger p-2">Error initializing editor logic.</p>';
         }
         return null; // Return null on error
    }
}

// Make sure the module indicates it's loaded.
console.log("dashboardEditor.js module loaded"); 