import { initializeStructureTree } from './widget/structureTree.js';
import { initializeTemplateInfo } from './widget/templateInfo.js';

import { initializeCategoriesList as _initializeCategoriesList } from './widget/categoriesList.js';
import { initializeChannelsList as _initializeChannelsList } from './widget/channelsList.js';
import { initializeTemplateList } from './widget/templateList.js';
import { initializeSharedTemplateList } from './widget/sharedTemplateList.js';

import { initializeDashboardEditor } from './widget/dashboardEditor.js';
import { initializeDashboardConfiguration } from './widget/dashboardConfiguration.js';
import { initializeDashboardPreview } from './widget/dashboardPreview.js';

// Import necessary utils and state
import { getGuildIdFromUrl } from './designerUtils.js';
import { state } from './designerState.js';

/**
 * Populates the content areas of already existing widgets based on their ID.
 * Called when a layout is loaded or widgets need refreshing with new data.
 * @param {object} templateData - The structured template data (categories, channels etc.).
 */
export function populateGuildDesignerWidgets(templateData) {
    console.log("[DesignerWidgets] Populating all widget contents...");
    if (!templateData) {
        console.error("[DesignerWidgets] Template data is missing, cannot populate widgets.");
        return;
    }
    
    const guildId = getGuildIdFromUrl(); // Needed for manage links

    // Get User ID from main container
    const mainContainer = document.getElementById('designer-main-container');
    const currentUserId = mainContainer?.dataset.currentUserId;
    // --- 

    // Define widgets and their initialization functions
    // NOTE: The functions here are called when the *default* layout is loaded
    // or when data needs refreshing. Dynamic widgets like dashboard-editor
    // might need separate initialization logic when they are added to the grid.
    const widgetInitializers = {
        'template-info': (el, data) => initializeTemplateInfo(data, el),
        'categories': (el, data) => _initializeCategoriesList(data, el, guildId),
        'channels': (el, data) => _initializeChannelsList(data, el, guildId),
        'template-list': (el, data) => {
            // Use the active template ID from the state module
            const activeId = state.getActiveTemplateId();
            console.log(`[DesignerWidgets] Populating template-list, using active ID from state: ${activeId}`);
            initializeTemplateList(el, guildId, activeId); 
        },
        'shared-template-list': (el, data) => {
            // Pass user ID to the widget element before initializing
            if (el && currentUserId) {
                 el.dataset.currentUserId = currentUserId;
                 initializeSharedTemplateList(el, guildId);
             } else if (!currentUserId) {
                  console.error("[DesignerWidgets] Could not find currentUserId for shared list.");
                  el.innerHTML = '<p class="text-danger p-3">Error: User ID missing.</p>';
             }
        },
        'structure-tree': (el, data) => {
            // Structure tree initializer doesn't need the element passed directly
            // It finds its container by ID internally. But we call it here.
            initializeStructureTree(data);
        },
        // Register the dashboard editor - pass its *content container selector* ID
        'dashboard-editor': (el, data) => {
             const instance = initializeDashboardEditor(`#${el.id}`, guildId /* pass necessary context */);
             if (instance) {
                 instance.initUI(); // Call initUI immediately after creation
                 console.log(`[DesignerWidgets] DashboardEditor instance created and initUI called for ${el.id}.`);
             } else {
                 console.error(`[DesignerWidgets] Failed to create DashboardEditor instance for ${el.id}.`);
             }
        },
        // --- NEW: Register the dashboard configuration widget --- 
        'dashboard-configuration': (el, data) => {
            // Initially called with templateData, but we need specific dashboard config data.
            // For now, just call it with null data. It will display "No dashboard loaded".
            // The actual config data will be passed later via event or direct call.
            initializeDashboardConfiguration(el, null);
            console.log(`[DesignerWidgets] DashboardConfiguration widget initialized for ${el.id}.`);
        },
        // --- NEW: Register the dashboard preview widget --- 
        'dashboard-preview': (el, data) => {
            initializeDashboardPreview(el);
            console.log(`[DesignerWidgets] DashboardPreview widget initialized for ${el.id}.`);
        }
        // ------------------------------------------------
    };

    // Iterate over known widget IDs and call their initializers if the element exists
    // This primarily populates the *default* widgets. 
    Object.keys(widgetInitializers).forEach(widgetId => {
        // Check if the widget element currently exists in the DOM (it might not if it's dynamic)
        const contentElement = document.getElementById(`widget-content-${widgetId}`);
        if (contentElement) {
            try {
                console.log(`[DesignerWidgets] Initializing/Populating widget: ${widgetId}`);
                widgetInitializers[widgetId](contentElement, templateData);
            } catch (error) {
                console.error(`[DesignerWidgets] Error initializing/populating widget ${widgetId}:`, error);
                contentElement.innerHTML = `<p class="text-danger p-3">Error loading content.</p>`;
            }
        } else {
            // It's normal for dynamic widgets like dashboard-editor not to be found initially
            if (widgetId !== 'dashboard-editor' && widgetId !== 'dashboard-configuration' && widgetId !== 'dashboard-preview') { // Only warn for non-dynamic widgets
                 console.warn(`[DesignerWidgets] Content container for widget ID '${widgetId}' not found.`);
            }
        }
    });

    console.log("[DesignerWidgets] Widget content population finished.");
}

// Initial log
console.log("[DesignerWidgets] Widgets module loaded.");

// Export individual list initializers
export const initializeCategoriesList = _initializeCategoriesList;
export const initializeChannelsList = _initializeChannelsList;
// -------------------------------------------
