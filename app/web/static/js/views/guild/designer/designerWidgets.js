// Import specific widget initializers
import { initializeStructureTree } from './widget/structureTree.js';
import { initializeTemplateInfo } from './widget/templateInfo.js';
import { initializeCategoriesList } from './widget/categoriesList.js';
import { initializeChannelsList } from './widget/channelsList.js';
import { initializeTemplateList } from './widget/templateList.js';
import { initializeSharedTemplateList } from './widget/sharedTemplateList.js';

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

    // --- Get User ID from main container (needed for shared list) ---
    const mainContainer = document.getElementById('designer-main-container');
    const currentUserId = mainContainer?.dataset.currentUserId;
    // --- 

    // Define widgets and their initialization functions
    const widgetInitializers = {
        'template-info': (el, data) => initializeTemplateInfo(data, el),
        'categories': (el, data) => initializeCategoriesList(data, el, guildId),
        'channels': (el, data) => initializeChannelsList(data, el, guildId),
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
        }
    };

    // Iterate over known widget IDs and call their initializers
    Object.keys(widgetInitializers).forEach(widgetId => {
        const contentElement = document.getElementById(`widget-content-${widgetId}`);
        if (contentElement) {
            try {
                console.log(`[DesignerWidgets] Initializing widget: ${widgetId}`);
                widgetInitializers[widgetId](contentElement, templateData);
            } catch (error) {
                console.error(`[DesignerWidgets] Error initializing widget ${widgetId}:`, error);
                contentElement.innerHTML = `<p class="text-danger p-3">Error loading content.</p>`;
            }
        } else {
            console.warn(`[DesignerWidgets] Content container for widget ID '${widgetId}' not found.`);
        }
    });

    console.log("[DesignerWidgets] Widget content population finished.");
}

// Initial log to confirm loading
console.log("[DesignerWidgets] Widgets module loaded.");
