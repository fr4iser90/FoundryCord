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
import { populateGuildDesignerWidgets } from './designerWidgets.js';
import { initializeStructureTree } from './widget/structureTree.js'; // Still needed for GridManager callback

// --- Modal Imports ---
import { initializeShareModal } from './modal/shareModal.js';
import { initializeSaveAsNewModal } from './modal/saveAsNewModal.js';
import { initializeDeleteModal } from './modal/deleteModal.js';
import { initializeActivateConfirmModal } from './modal/activateConfirmModal.js';

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
            state.setCurrentTemplateIsActive(initialTemplateData?.is_active ?? false); 
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
            console.log(`[Index] Found and stored active template ID from DOM: ${activeTemplateIdFromDOM}`);
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
        console.log("[Index] Modals initialized.");
        
        // 7. Initialize Core Designer Event Listeners (Save button, custom events, etc.)
        console.log("[Index] Initializing core designer event listeners...");
        initializeDesignerEventListeners();
        console.log("[Index] Core designer event listeners initialized.");

        console.log("[Index] Guild Designer initialization sequence complete.");

    } catch (error) {
        console.error("[Index] UNHANDLED error during Guild Designer initialization process:", error);
        displayErrorMessage('An critical unexpected error occurred during initialization. Please check the console.');
    }
}); 