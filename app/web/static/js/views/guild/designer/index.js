// --- Core Component Imports ---
import { GridManager } from '/static/js/components/layout/gridManager.js';
import { apiRequest, showToast } from '/static/js/components/common/notifications.js'; // Keep for potential direct use?

// --- Designer Module Imports ---
import { state } from './designerState.js';
import { getGuildIdFromUrl, fetchGuildTemplate, displayErrorMessage, debounce } from './designerUtils.js';
import { 
    initializeGrid, 
    loadLayout, 
    renderDefaultWidgets, 
    saveLayout, 
    resetLayout, 
    setLockButtonAppearance, 
    toggleLayoutLockAndSave 
} from './designerLayout.js';
import { initializeDesignerEventListeners } from './designerEvents.js';
import { populateGuildDesignerWidgets, initializeCategoriesList, initializeChannelsList } from './designerWidgets.js';
import { initializeStructureTree } from './widget/structureTree.js'; // Still needed for GridManager callback

// --- Modal Imports ---
import { initializeShareModal } from './modal/shareModal.js';
import { initializeSaveAsNewModal } from './modal/saveAsNewModal.js';
import { initializeDeleteModal } from './modal/deleteModal.js';
import { initializeActivateConfirmModal } from './modal/activateConfirmModal.js';
import { initializeNewItemInputModal } from './modal/newItemInputModal.js';

// --- Panel Imports ---
import { initializePropertiesPanel } from './panel/properties.js';
import { initializeToolbox } from './panel/toolbox.js';

// --- Main Execution --- 

document.addEventListener('DOMContentLoaded', async () => {
    console.log("[Index] DOM fully loaded. Starting Guild Designer initialization...");

    const guildId = getGuildIdFromUrl();
    if (!guildId) {
        displayErrorMessage('Could not determine Guild ID. Cannot initialize designer.');
        return;
    }

    // Get main UI elements needed for initialization
    const gridContainer = document.getElementById('designer-grid');
    const lockButton = document.getElementById('toggle-lock-btn');
    const resetButton = document.getElementById('reset-layout-btn');
    const mainContainer = document.getElementById('designer-main-container'); // For data attributes

    if (!gridContainer || !lockButton || !resetButton || !mainContainer) {
        console.error('[Index] Essential UI elements missing (grid, buttons, or main container).');
        displayErrorMessage('Initialization failed: Core UI elements missing.');
        return;
    }

    try {
        // 1. Fetch Initial Data
        console.log("[Index] Fetching initial template data...");
        let initialTemplateData = null;
        try {
            initialTemplateData = await fetchGuildTemplate(guildId);
            state.setCurrentTemplateData(initialTemplateData); // Store in state
            console.log("[Index] Initial template data fetched and stored in state.");
        } catch (error) {
            console.error("[Index] Failed to fetch initial template data. Stopping initialization.", error);
            displayErrorMessage('Failed to load initial guild data. Please check the console or try again later.');
            return; 
        }

        // 2. Get Active Template ID & User ID from DOM and store in state
        const activeTemplateIdFromDOM = mainContainer.dataset.activeTemplateId;
        if (activeTemplateIdFromDOM) {
            state.setActiveTemplateId(activeTemplateIdFromDOM);
            console.log(`[Index] Found and stored active template ID from DOM: ${activeTemplateIdFromDOM} (Type: ${typeof activeTemplateIdFromDOM})`);
            console.log(`[Index] Value in state.getActiveTemplateId() right after setting: ${state.getActiveTemplateId()}`);
        } else {
             console.warn("[Index] Active template ID not found in main container's data attribute.");
        }
        // User ID is fetched within widget initializers that need it (like shared list)

        // 3. Define Widgets and Default Layout (Constants for GridManager)
        console.log("[Index] Defining widgets and default layout...");
        const pageIdentifier = `guild-designer-${guildId}`;
        const widgetDefs = {
            'structure-tree': { title: 'Guild Structure', content: '<div id="widget-content-structure-tree">Loading tree...</div>' },
            'template-info': { title: 'Template Information', content: '<div id="widget-content-template-info">Loading...</div>' },
            'categories': { title: 'Categories', content: '<div id="widget-content-categories">Loading...</div>', headerControls: [{ type: 'link', text: 'Manage', href: `/guild/${guildId}/designer/categories`, class: 'manage-link' }] },
            'channels': { title: 'Channels', content: '<div id="widget-content-channels">Loading...</div>', headerControls: [{ type: 'link', text: 'Manage', href: `/guild/${guildId}/designer/channels`, class: 'manage-link' }] },
            'template-list': { title: 'Saved Templates', content: '<div id="widget-content-template-list">Loading templates...</div>' },
            'shared-template-list': { title: 'Shared Templates', content: '<div id="widget-content-shared-template-list">Loading shared templates...</div>' },
        };
        const defaultLayout = [
            { id: 'structure-tree', x: 0, y: 0, w: 4, h: 8, minW: 3, minH: 5 },
            { id: 'template-info', x: 4, y: 0, w: 4, h: 2, minW: 3, minH: 2, maxH: 2 }, // Added maxH
            { id: 'categories', x: 4, y: 2, w: 4, h: 3, minW: 3, minH: 3 },
            { id: 'channels', x: 8, y: 0, w: 4, h: 5, minW: 3, minH: 4 },
            { id: 'template-list', x: 4, y: 5, w: 4, h: 3, minW: 3, minH: 3 },
            { id: 'shared-template-list', x: 8, y: 5, w: 4, h: 3, minW: 3, minH: 3 },
        ];
        // console.log("[Index] Widget definitions:", widgetDefs);
        // console.log("[Index] Default layout:", defaultLayout);

        // 4. Initialize GridManager
        console.log("[Index] Initializing GridManager...");
        const debouncedSaveFn = debounce((gridInstance) => saveLayout(gridInstance, pageIdentifier), 1000); 
        
        const gridManager = new GridManager({
            gridElementId: 'designer-grid',
            pageIdentifier: pageIdentifier,
            widgetDefinitions: widgetDefs,
            defaultLayout: defaultLayout,
            populateContentCallback: (dataForWidgets) => {
                // Use the widget orchestrator function
                console.log("[GridManager Callback] Populating widgets...");
                populateGuildDesignerWidgets(dataForWidgets); 
                // Tree initialization is now handled *within* populateGuildDesignerWidgets
            },
            resetRequiresDataCallback: async () => { 
                // Fetch fresh data on reset and update state
                console.log("[GridManager Callback] Reset requested. Fetching fresh data...");
                try {
                    const freshData = await fetchGuildTemplate(guildId);
                    state.setCurrentTemplateData(freshData);
                    state.setDirty(false); // Reset dirty flag on layout reset
                    return freshData;
                } catch (fetchError) {
                     console.error("[GridManager Callback] Failed to fetch fresh data on reset:", fetchError);
                     displayErrorMessage('Failed to reload data after layout reset.');
                     return null; // Prevent reset if data fetch fails
                }
            }
        });

        // Pass the initial template data fetched earlier
        const grid = await gridManager.initialize(initialTemplateData); 
        if (!grid) {
             console.error("[Index] GridManager failed to initialize. Stopping.");
             displayErrorMessage('Failed to initialize the layout manager.');
             return;
        }
        console.log("[Index] GridManager initialized successfully.");

        // 5. Setup Layout Control Button Listeners (Lock/Reset)
        lockButton.addEventListener('click', () => toggleLayoutLockAndSave(grid, lockButton, () => debouncedSaveFn(grid)));
        resetButton.addEventListener('click', async () => {
            if (confirm('Are you sure you want to reset the layout to default? Any unsaved layout changes will be lost.')) {
                // The resetRequiresDataCallback in GridManager handles fetching fresh data
                await gridManager.resetLayoutToDefault();
            }
        });
        // Set initial lock button appearance based on loaded layout state
        setLockButtonAppearance(grid, lockButton);

        // 6. Initialize Modals
        console.log("[Index] Initializing modals...");
        initializeShareModal();
        initializeSaveAsNewModal();
        initializeDeleteModal();
        initializeActivateConfirmModal();
        initializeNewItemInputModal();
        console.log("[Index] Modals initialized.");
        
        // 7. Initialize Core Designer Event Listeners (Save button, custom events, etc.)
        console.log("[Index] Initializing core designer event listeners...");
        initializeDesignerEventListeners();
        console.log("[Index] Core designer event listeners initialized.");

        // 8. Initialize Panels
        console.log("[Index] Initializing panels (Properties, Toolbox)...");
        initializePropertiesPanel();
        initializeToolbox();
        console.log("[Index] Panels initialized.");

        // Add listener for element deletion
        document.addEventListener('designerElementDeleted', handleDesignerElementDeleted);
        console.log("[Index] Added listener for 'designerElementDeleted'.");
        // --------------------------------------------

        console.log("[Index] Guild Designer initialization sequence complete.");

    } catch (error) {
        console.error("[Index] UNHANDLED error during Guild Designer initialization process:", error);
        displayErrorMessage('An critical unexpected error occurred during initialization. Please check the console.');
    }
}); 

// Handler function for element deletion
/**
 * Handles the 'designerElementDeleted' event dispatched by the delete modal.
 * Removes the corresponding node from the jsTree view.
 * @param {CustomEvent} event - The event object containing detail: { itemType, itemId }.
 */
function handleDesignerElementDeleted(event) {
    const { itemType, itemId } = event.detail;
    console.log(`[Index] Handling 'designerElementDeleted' for ${itemType} ID: ${itemId}`);

    if (!itemType || itemId === undefined || itemId === null) {
        console.error("[Index] Invalid event detail for 'designerElementDeleted':", event.detail);
        return;
    }

    // Construct the jsTree node ID (e.g., designer_category -> category_)
    const nodeTypePrefix = itemType.replace('designer_', ''); // Remove prefix
    const nodeIdString = `${nodeTypePrefix}_${itemId}`;

    // Get the jsTree instance
    const treeContainer = document.getElementById('widget-content-structure-tree');
    if (!treeContainer || typeof $.fn.jstree !== 'function') {
        console.error("[Index] Could not find tree container or jsTree function to delete node.");
        return;
    }
    const treeInstance = $(treeContainer).jstree(true);

    if (!treeInstance) {
        console.error("[Index] Could not get jsTree instance to delete node.");
        return;
    }

    // Check if node exists before attempting delete
    const node = treeInstance.get_node(nodeIdString);
    if (!node) {
        console.warn(`[Index] Node with ID ${nodeIdString} not found in jsTree. Might have been removed already.`);
        return; // Node doesn't exist, nothing to delete
    }

    // Delete the node from the tree
    try {
        treeInstance.delete_node(nodeIdString);
        console.log(`[Index] Successfully deleted node ${nodeIdString} from jsTree.`);
        // Note: state.setDirty(true) is already called by deleteModal.js
        // We might need to trigger an update for other list widgets here if needed
        // Refresh corresponding list widget
        const currentTemplateData = state.getCurrentTemplateData();
        const guildId = getGuildIdFromUrl(); // Needed for list links

        if (currentTemplateData && guildId) {
            if (itemType === 'designer_category') {
                const categoryListEl = document.getElementById('widget-content-categories');
                if (categoryListEl) {
                    console.log("[Index] Refreshing categories list after deletion.");
                    initializeCategoriesList(currentTemplateData, categoryListEl, guildId);
                } else {
                    console.warn("[Index] Could not find categories list element to refresh.");
                }
            } else if (itemType === 'designer_channel') {
                const channelListEl = document.getElementById('widget-content-channels');
                if (channelListEl) {
                    console.log("[Index] Refreshing channels list after deletion.");
                    initializeChannelsList(currentTemplateData, channelListEl, guildId);
                } else {
                    console.warn("[Index] Could not find channels list element to refresh.");
                }
            }
        } else {
            console.warn("[Index] Could not refresh list widget: Missing current template data or guild ID.");
        }
        // -----------------------------------------
    } catch (error) {
        console.error(`[Index] Error deleting node ${nodeIdString} from jsTree:`, error);
    }
}
// -------------------------------------------- 