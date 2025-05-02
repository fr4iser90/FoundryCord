/**
 * dashboardEditor.js
 * 
 * Logic for the Dashboard Editor widget. Allows users to build and configure
 * dashboard instances using components from the toolbox.
 */

// Import necessary modules (e.g., for API calls, state management) later

/**
 * Initializes the Dashboard Editor widget.
 * This might be called when the widget is first added to the grid or when
 * specific data needs to be loaded.
 * 
 * @param {HTMLElement} element - The container element for the widget's content.
 * @param {string} guildId - The current Guild ID.
 * @param {object} [initialContext={}] - Optional context (e.g., instanceId to load).
 */
export function initializeDashboardEditor(element, guildId, initialContext = {}) {
    console.log("[DashboardEditor] Initializing widget inside element:", element);
    console.log("[DashboardEditor] Guild ID:", guildId);
    console.log("[DashboardEditor] Initial Context:", initialContext);

    // TODO: Implement the actual editor UI and logic here.
    // - Handle dropped components
    // - Render configuration forms based on component definitions
    // - Manage the internal state of the dashboard being built
    // - Handle loading existing instances
    // - Handle saving/creating instances via API

    if (element) {
        // Set initial content
        element.innerHTML = `
            <div class="p-3">
                <h5>Dashboard Editor Placeholder</h5>
                <p class="text-muted small">Drop components here from the toolbox.</p>
                <div id="dashboard-editor-canvas" style="min-height: 200px; border: 1px dashed #ccc; background-color: #f8f9fa;" class="p-2">
                    <!-- Components will be added here -->
                </div>
                <div id="dashboard-editor-properties" class="mt-3">
                    <!-- Properties for selected component will appear here -->
                </div>
            </div>
        `;

        // --- Initialize Droppable --- 
        const canvas = $("#dashboard-editor-canvas");
        if (canvas.length > 0 && typeof $.ui !== 'undefined' && typeof $.ui.droppable !== 'undefined') {
            canvas.droppable({
                accept: ".toolbox-item", // Accept only items from the toolbox
                // greedy: true, // Prevent event bubbling if needed later
                // hoverClass: "drop-hover", // Optional: Add class on hover
                drop: function(event, ui) {
                    const droppedItem = ui.draggable; // The original toolbox item
                    const elementType = droppedItem.data('element-type'); // From toolbox.html (e.g., 'dashboard', 'category', 'text_channel')
                    const componentKey = droppedItem.data('component-key'); // From toolbox.js (for components)
                    const componentType = droppedItem.data('component-type'); // From toolbox.js (for components)

                    console.log(`[DashboardEditor] Drop detected. ElementType: ${elementType}, ComponentKey: ${componentKey}, ComponentType: ${componentType}`);

                    // TODO: Get current channel context (channelTemplateId) for which this editor is active.
                    const currentChannelId = null; // Placeholder

                    if (elementType === 'dashboard') {
                        // --- Handle Drop of 'New Dashboard' --- 
                        console.log('[DashboardEditor] Handling drop of "New Dashboard" element.');
                        if (!currentChannelId) {
                            console.error("[DashboardEditor] Cannot create dashboard: No channel context available.");
                            // showToast('error', 'Please select a channel first or ensure editor has context.');
                            return; // Abort if no channel context
                        }
                        // TODO: Open a modal here to select the actual Dashboard Type (e.g., 'welcome', 'gamehub', 'project')
                        // TODO: On modal confirm, call POST /api/v1/templates/channels/{currentChannelId}/dashboards with name and type
                        // TODO: Load the newly created (empty) instance into this editor.
                        $(this).append(`<p class="text-success">Initiated NEW dashboard creation for channel ${currentChannelId} (Placeholder)</p>`);

                    } else if (componentKey && componentType && componentType !== 'structure') {
                        // --- Handle Drop of a Dashboard Component --- 
                        console.log(`[DashboardEditor] Handling drop of component: ${componentKey} (${componentType})`);
                        // TODO: Ensure an instance is loaded/created before adding components.
                        // TODO: Get the full component definition (needs to be added to toolbox draggable data)
                        // TODO: Add component to the internal config state of the editor.
                        // TODO: Render the component visually on the canvas.
                        // TODO: Update the component properties panel within the editor.
                        $(this).append(`<p>Added Component: ${componentKey} (${componentType})</p>`);

                    } else {
                        // --- Handle other unexpected drops (e.g., structure elements like category/channel) --- 
                        console.warn(`[DashboardEditor] Ignoring drop of unexpected element type: ${elementType || componentType}`);
                        // showToast('warning', 'This element cannot be added to the dashboard editor.');
                    }
                }
            });
            console.log("[DashboardEditor] Droppable initialized for canvas.");
        } else {
             if (canvas.length === 0) {
                 console.error("[DashboardEditor] Canvas element #dashboard-editor-canvas not found for droppable.");
             } else {
                 console.error("[DashboardEditor] jQuery UI Droppable is not available.");
             }
        }
        // --------------------------

    } else {
         console.error("[DashboardEditor] Initialization failed: Target element not provided.");
    }
}

// Initial log to confirm the module is loaded
console.log("[DashboardEditor] Module loaded."); 