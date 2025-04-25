import { GridManager } from '/static/js/components/layout/grid_manager.js';
// Keep showToast and apiRequest available if needed directly, though GridManager uses them
import { apiRequest, showToast } from '/static/js/components/common/notifications.js';
// Import the specific widget initializer
import { initializeStructureTree } from './widget/structure_tree.js';
import { initializeTemplateInfo } from './widget/template_info.js';
import { initializeCategoriesList } from './widget/categories_list.js';
import { initializeChannelsList } from './widget/channels_list.js';
// Import the new template list initializer
import { initializeTemplateList } from './widget/template_list.js';
// Import the shared template list initializer
import { initializeSharedTemplateList } from './widget/shared_template_list.js';

/**
 * Extracts the Guild ID from the current URL path.
 * Assumes URL format like /guild/{guild_id}/designer/...
 * @returns {string|null} The Guild ID or null if not found.
 */
function getGuildIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    // Example path: ['', 'guild', 'GUILD_ID', 'designer', ...]
    if (pathParts.length >= 3 && pathParts[1] === 'guild') {
        return pathParts[2];
    }
    console.error('Could not extract Guild ID from URL path:', window.location.pathname);
    return null;
}

/**
 * Fetches the guild template data from the API (Specific to this page).
 * Used for initial data and reset data.
 * @param {string} guildId - The ID of the guild.
 * @returns {Promise<object|null>} Template data or null.
 */
async function fetchGuildTemplate(guildId) {
    if (!guildId) return null; // Guard against missing guildId
    const apiUrl = `/api/v1/guilds/${guildId}/template`;
    console.log(`Fetching guild template data from: ${apiUrl}`);
    try {
        const response = await apiRequest(apiUrl);
        console.log('Successfully fetched template data:', response);
        // Return the response directly, as FastAPI now sends the data object
        return response ? response : null;
    } catch (error) {
        console.error('Error fetching guild template:', error);
        displayErrorMessage('Failed to load guild template data. Please check the console.');
        return null;
    }
}

/**
 * Main population function called by GridManager after widgets are added/loaded.
 * Delegates to specific widget initializers.
 * @param {object} templateData - The structured template data.
 * @param {string|null} targetWidgetId - ID of the specific widget to populate, or null for all.
 * @param {HTMLElement|null} targetElement - The content element of the specific widget, or null.
 */
function populateGuildDesignerWidgets(templateData, targetWidgetId = null, targetElement = null) {
    console.log(`[Index] Populating widget content. Target: ${targetWidgetId || 'all'}`);
    const guildId = getGuildIdFromUrl(); // Needed for links

    const widgetsToPopulate = targetWidgetId ? [targetWidgetId] : [
        'template-info', 
        'categories', // Categories List Widget
        'channels',   // Channels List Widget
        'structure-tree', // Structure Tree Widget
        'template-list', // Saved Templates List Widget
        'shared-template-list' // Shared Templates List Widget
    ];

    widgetsToPopulate.forEach(widgetId => {
        const contentElement = targetElement && targetWidgetId === widgetId 
            ? targetElement 
            : document.getElementById(`widget-content-${widgetId}`);
        
        if (!contentElement) {
            console.warn(`[Index] Content container for widget ID '${widgetId}' not found.`);
            return;
        }

        try {
            switch (widgetId) {
                case 'template-info':
                    initializeTemplateInfo(templateData, contentElement);
                    break;
                case 'categories':
                    initializeCategoriesList(templateData, contentElement, guildId);
                    break;
                case 'channels':
                    initializeChannelsList(templateData, contentElement, guildId);
                    break;
                case 'structure-tree':
                    contentElement.innerHTML = 'Tree is initializing...'; // Placeholder
                    break;
                case 'template-list':
                    // Call the actual initializer function
                    initializeTemplateList(contentElement, guildId);
                    break;
                case 'shared-template-list':
                    // Call the shared template list initializer
                    initializeSharedTemplateList(contentElement, guildId);
                    break;
                default:
                    console.warn(`[Index] Unknown widget ID for population: ${widgetId}`);
            }
        } catch (error) {
             console.error(`[Index] Error populating widget ${widgetId}:`, error);
             if(contentElement) contentElement.innerHTML = `<p class="text-danger p-3">Error loading content.</p>`;
        }
    });
}

/**
 * Displays an error message on the page.
 * (Could be moved to a shared utility later)
 */
function displayErrorMessage(message) {
    const errorContainer = document.getElementById('designer-error-container');
    // Also create a generic container for GridManager errors if it doesn't exist
    let gridManagerErrorContainer = document.getElementById('grid-manager-error-container');
    if (!gridManagerErrorContainer && document.getElementById('designer-main-container')) {
        gridManagerErrorContainer = document.createElement('div');
        gridManagerErrorContainer.id = 'grid-manager-error-container';
        gridManagerErrorContainer.style.display = 'none'; // Initially hidden
        document.getElementById('designer-main-container').prepend(gridManagerErrorContainer);
    }

    if (errorContainer) {
        errorContainer.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        errorContainer.style.display = 'block'; // Make sure it's visible
    } else {
        console.error("Error container '#designer-error-container' not found for page-specific error.");
        showToast('error', `UI Error: ${message}`); // Fallback toast
    }
}

/**
 * Debounce function to limit the rate at which a function can fire.
 * @param {function} func The function to debounce.
 * @param {number} wait The number of milliseconds to delay.
 * @returns {function} The debounced function.
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Saves the current grid layout to the backend.
 * @param {GridStack} grid - The GridStack instance.
 * @param {string} pageIdentifier - The unique identifier for the page layout.
 */
async function saveLayout(grid, pageIdentifier) {
    if (!grid) {
        console.error("[Index] Cannot save layout: Grid instance is not available.");
        return;
    }
    console.log(`[Index] Debounced save triggered for ${pageIdentifier}`);
    
    // Get the current layout structure from Gridstack
    // grid.save(false) saves only layout structure (x, y, w, h, id), not content
    const currentLayout = grid.save(false); 
    
    // Get the current lock state
    const isLocked = grid.opts.disableDrag;
    
    // Format the payload according to UILayoutSaveSchema
    const payload = {
        layout: currentLayout,
        is_locked: isLocked // Include lock state
    };

    const apiUrl = `/api/v1/layouts/${pageIdentifier}`;
    console.log(`[Index] Saving layout to: ${apiUrl}`);

    try {
        // Use apiRequest (which should handle errors and toasts implicitly)
        await apiRequest(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        // If we reach here, the request was successful (status 2xx)
        showToast('success', 'Layout saved successfully!');
        console.log("[Index] Layout save request successful.");
    } catch (error) {
        // Generic error handling here, as apiRequest now handles 204 and logs/toasts other errors.
        // The error is already logged by apiRequest's catch block.
        console.error("[Index] Failed to save layout:", error.message);
        // Optionally display a user-facing error message on the page if apiRequest's toast isn't enough.
        // displayErrorMessage("Failed to save the layout. Please try again.");
    }
}

/**
 * Resets the layout by deleting the saved state and rendering defaults.
 * @param {GridStack} grid - The GridStack instance.
 * @param {string} pageIdentifier - The unique identifier for the page layout.
 * @param {object} templateData - The template data needed to render defaults.
 */
async function resetLayout(grid, pageIdentifier, templateData) {
    console.log(`Resetting layout for ${pageIdentifier}`);
    const apiUrl = `/api/v1/layouts/${pageIdentifier}`;
    try {
        await apiRequest(apiUrl, { method: 'DELETE' });
        showToast('success', 'Layout reset successfully!');
        // Re-render the default layout
        if (grid && templateData) {
            renderDefaultWidgets(templateData, grid); // Render defaults after reset
        } else {
            console.error("Cannot render default layout after reset: grid or templateData missing.")
            // Maybe force a page reload as fallback?
            // window.location.reload(); 
        }
    } catch (error) {
        console.error("Failed to reset layout:", error);
        // apiRequest should have shown an error toast
        displayErrorMessage("Could not reset layout. Please try again.");
    }
}

/**
 * Updates the button appearance based on the grid lock state.
 * @param {GridStack} grid - The GridStack instance.
 * @param {HTMLButtonElement} lockButton - The button element used to toggle lock state.
 */
function setLockButtonAppearance(grid, lockButton) {
    if (!grid || !lockButton) return;

    const icon = lockButton.querySelector('i');
    const textSpan = lockButton.querySelector('.btn-text');
    
    const isCurrentlyLocked = grid.opts.disableDrag;

    if (isCurrentlyLocked) {
        icon.classList.remove('bi-unlock-fill');
        icon.classList.add('bi-lock-fill');
        textSpan.textContent = 'Unlock Layout';
        lockButton.title = 'Unlock Layout Editing';
    } else {
        icon.classList.remove('bi-lock-fill');
        icon.classList.add('bi-unlock-fill');
        textSpan.textContent = 'Lock Layout';
        lockButton.title = 'Lock Layout Editing';
    }
}

/**
 * Toggles the editability (drag/resize) of the grid layout and saves the state.
 * @param {GridStack} grid - The GridStack instance.
 * @param {HTMLButtonElement} lockButton - The button element used to toggle lock state.
 * @param {function} saveCallback - The debounced save function.
 */
function toggleLayoutLockAndSave(grid, lockButton, saveCallback) {
    if (!grid || !lockButton) return;

    const isCurrentlyLocked = grid.opts.disableDrag;

    if (isCurrentlyLocked) { // Unlock it
        grid.enableMove(true);
        grid.enableResize(true);
        grid.opts.disableDrag = false; // Update internal option state if needed
        grid.opts.disableResize = false;
        showToast('info', 'Layout unlocked for editing.');
    } else { // Lock it
        grid.enableMove(false);
        grid.enableResize(false);
        grid.opts.disableDrag = true;
        grid.opts.disableResize = true;
        showToast('info', 'Layout locked.');
    }

    // Update button appearance to reflect the new state
    setLockButtonAppearance(grid, lockButton);

    // Trigger save immediately (or debounced if preferred)
    console.log("Lock state changed, triggering save...");
    saveCallback(); // Call the passed save function
}

/**
 * Creates a standard widget structure for Gridstack.
 * @param {string} id - Unique ID for the widget.
 * @param {string} title - Title for the widget header.
 * @param {string} contentHtml - Initial HTML content for the widget body.
 * @param {object} gridOptions - Gridstack options (x, y, w, h, etc.).
 * @returns {HTMLElement} The widget element to be added to the grid.
 */
function createWidgetElement(id, title, contentHtml, gridOptions) {
    const widget = document.createElement('div');
    widget.className = 'grid-stack-item';
    widget.setAttribute('gs-id', id);
    // Apply grid options (x, y, w, h) dynamically
    for (const key in gridOptions) {
        widget.setAttribute(`gs-${key}`, gridOptions[key]);
    }

    widget.innerHTML = `
        <div class="grid-stack-item-content">
            <div class="widget-header">
                <span>${title}</span>
                <!-- Add optional controls here -->
            </div>
            <div class="widget-content widget-content-area" id="widget-content-${id}">
                ${contentHtml}
            </div>
        </div>
    `;
    return widget;
}

/**
 * Initializes the Gridstack instance.
 * @returns {GridStack|null} The initialized GridStack object or null if grid element not found.
 */
function initializeGrid() {
    const gridElement = document.getElementById('designer-grid');
    if (!gridElement) {
        console.error('Gridstack container #designer-grid not found.');
        return null;
    }
    const grid = GridStack.init({
        cellHeight: 70, // Adjust as needed
        margin: 10,     // Adjust as needed
        float: true,    // Allows widgets to float up
        disableResize: false, // Start unlocked by default
        disableDrag: false    // Start unlocked by default
        // Add other Gridstack options if needed
    });
    return grid;
}

/**
 * Loads the saved layout for a given page identifier from the API.
 * @param {string} pageIdentifier - The unique identifier for the page layout.
 * @returns {Promise<object|null>} Layout data if found, otherwise null.
 */
async function loadLayout(pageIdentifier) {
    const apiUrl = `/api/v1/layouts/${pageIdentifier}`;
    console.log(`Attempting to load layout from: ${apiUrl}`);
    try {
        // Assuming apiRequest handles non-200 responses gracefully (e.g., returns null or throws)
        // If 404 specifically means "no layout saved", apiRequest should ideally reflect that.
        // For now, we assume null/error means no usable layout.
        const rawResponse = await apiRequest(apiUrl);
        console.log("Raw response from loadLayout:", rawResponse); // Log the response

        // Check if the response is an object and has a 'layout' array property
        // The API should return the layout_data directly: { layout: [...], is_locked: ... }
        if (rawResponse && typeof rawResponse === 'object' && Array.isArray(rawResponse.layout)) {
            console.log("Saved layout data looks valid:", rawResponse);
            return rawResponse; // Return the object { layout: [...], is_locked: ... }
        } else {
            console.log("No saved layout found or response format invalid.");
            return null;
        }
    } catch (error) {
        // Log error, but treat as "no layout found" for flow control
        console.error(`Error loading layout for ${pageIdentifier}:`, error);
        // Don't show a generic error toast here, as it might just be a 404 (no layout)
        // displayErrorMessage("Failed to load saved layout."); // Avoid this unless it's a 500
        return null;
    }
}

/**
 * Renders the fetched template data as widgets in the Gridstack grid.
 * @param {object} templateData - The structured template data.
 * @param {GridStack} grid - The initialized Gridstack instance.
 */
function renderDefaultWidgets(templateData, grid) {
    console.log("Rendering default widgets:", templateData);
    if (!grid) {
        console.error("Gridstack instance is not available for rendering defaults.");
        displayErrorMessage("Failed to initialize the designer layout.");
        return;
    }
    if (!templateData) {
        console.error("Template data is missing, cannot render default widgets.");
        displayErrorMessage("Failed to load template data.");
        return;
    }

    // Clear existing widgets before adding new ones for default layout
    grid.removeAll();

    // Define widget configurations
    const guildId = getGuildIdFromUrl();
    const widgetConfigs = [
        {
            id: 'structure-tree',
            title: 'Guild Structure',
            content: '<p class="panel-placeholder">Loading structure...</p>', // Just the inner placeholder
            options: { x: 0, y: 0, w: 4, h: 8, minH: 4, minW: 3 }
        },
        {
            id: 'template-info',
            title: 'Template Information',
            content: '', // Content will be populated by JS
            options: { x: 4, y: 0, w: 4, h: 2, minH: 2, minW: 3, maxH: 2 }
        },
        {
            id: 'categories',
            title: 'Categories (List View)',
            content: '', // Content will be populated by JS
            options: { x: 4, y: 2, w: 4, h: 3, minH: 3, minW: 3 },
            manageLink: `/guild/${guildId}/designer/categories`
        },
         {
            id: 'channels',
            title: 'Channels (List View)',
            content: '', // Content will be populated by JS
            options: { x: 8, y: 0, w: 4, h: 5, minH: 3, minW: 3 },
            manageLink: `/guild/${guildId}/designer/channels`
        },
        {
            id: 'template-list', // Saved Templates
            title: 'Saved Templates',
            content: '', // Content will be populated by JS
            options: { x: 4, y: 5, w: 4, h: 3, minH: 3, minW: 3 }
        },
        {
            id: 'shared-template-list', // Shared Templates
            title: 'Shared Templates',
            content: '', // Content will be populated by JS
            options: { x: 8, y: 5, w: 4, h: 3, minH: 3, minW: 3 }
        }
        // Add more default widgets here as needed
    ];

    // Add widgets to the grid
    widgetConfigs.forEach(config => {
        const widgetEl = createWidgetElement(config.id, config.title, config.content, config.options);
        
        // Add manage link if specified
        if (config.manageLink) {
            const header = widgetEl.querySelector('.widget-header');
            if (header) {
                const manageLink = document.createElement('a');
                manageLink.href = config.manageLink;
                manageLink.className = 'btn btn-sm btn-outline-primary ms-auto'; // Use ms-auto to push right
                manageLink.textContent = 'Manage';
                manageLink.style.marginLeft = 'auto'; // Ensure it aligns right
                header.appendChild(manageLink);
            }
        }
        
        grid.addWidget(widgetEl);
    });

    console.log("Default widgets added to grid.");
    
    // Initial population after adding default widgets
    // This is now handled by the populateWidgetContents call in the main initialization logic
    // populateGuildDesignerWidgets(templateData); // REMOVED - Avoid double population
}

/**
 * Populates the content areas of already existing widgets.
 * Assumes grid.load() has already run and created the widget items.
 * @param {object} templateData - The structured template data (categories, channels etc.).
 */
function populateWidgetContents(templateData) {
    console.log("Populating content of existing widgets:", templateData);
    if (!templateData) {
        console.error("Template data is missing, cannot populate widget contents.");
        // Potentially display an error, though the widgets might just stay empty
        return;
    }
    
    const guildId = getGuildIdFromUrl(); // Needed for manage links

    // --- Populate Template Info ---    
    const infoContentEl = document.getElementById('widget-content-template-info');
    if (infoContentEl) {
         // Now we just set innerHTML directly, assuming the container exists
         initializeTemplateInfo(templateData, infoContentEl);
    } else {
        console.warn("Content area for template-info widget not found.");
    }

    // --- Populate Categories --- 
    const categoriesContentEl = document.getElementById('widget-content-categories');
    if (categoriesContentEl) {
        // Call the initializer function directly
        initializeCategoriesList(templateData, categoriesContentEl, guildId);
        // Remove manual population logic here, initializer handles it
    } else {
         console.warn("Content area for categories widget not found.");
    }

    // --- Populate Channels --- 
    const channelsContentEl = document.getElementById('widget-content-channels');
    if (channelsContentEl) {
         // Call the initializer function directly
         initializeChannelsList(templateData, channelsContentEl, guildId);
         // Remove manual population logic here, initializer handles it
    } else {
        console.warn("Content area for channels widget not found.");
    }

    // --- Populate Saved Templates List ---
    const templateListContentEl = document.getElementById('widget-content-template-list');
    if (templateListContentEl) {
        initializeTemplateList(templateListContentEl, guildId);
    } else {
        console.warn("Content area for template-list widget not found.");
    }

    // --- Populate Shared Templates List ---
    const sharedTemplateListContentEl = document.getElementById('widget-content-shared-template-list');
    if (sharedTemplateListContentEl) {
        initializeSharedTemplateList(sharedTemplateListContentEl, guildId);
    } else {
        console.warn("Content area for shared-template-list widget not found.");
    }

    // --- Initialize Structure Tree (After other data might be ready) ---
    // We need the template data which should include categories/channels by now
    initializeStructureTree(templateData); 

    console.log("Widget content population finished.");
}

/**
 * Sets up the event listeners for the panel toggle buttons.
 */
function setupPanelToggles() {
    console.log("[Index] Setting up panel toggles...");
    const leftPanelBtn = document.getElementById('toggle-left-panel-btn');
    const rightPanelBtn = document.getElementById('toggle-right-panel-btn');
    const leftPanel = document.querySelector('.editor-panel-left');
    const rightPanel = document.querySelector('.editor-panel-right');

    if (leftPanelBtn && leftPanel) {
        leftPanelBtn.addEventListener('click', () => {
            leftPanel.classList.toggle('collapsed');
            const icon = leftPanelBtn.querySelector('i');
            if (icon) icon.className = leftPanel.classList.contains('collapsed') ? 'bi bi-layout-sidebar' : 'bi bi-layout-sidebar-inset';
            // TODO: Maybe notify grid to resize? grid?.onParentResize();
        });
    }
    if (rightPanelBtn && rightPanel) {
        rightPanelBtn.addEventListener('click', () => {
            rightPanel.classList.toggle('collapsed');
            const icon = rightPanelBtn.querySelector('i');
            if (icon) icon.className = rightPanel.classList.contains('collapsed') ? 'bi bi-layout-sidebar-reverse' : 'bi bi-layout-sidebar-inset-reverse';
            // TODO: Maybe notify grid to resize? grid?.onParentResize();
        });
    }
    console.log("[Index] Panel toggles set up.");
}

// --- NEW: Event Listener for loading template data ---
function setupTemplateLoadListener() {
    console.log("[Index] Setting up listener for 'loadTemplateData' event...");
    document.addEventListener('loadTemplateData', (event) => {
        console.log("[Index] Received 'loadTemplateData' event.", event.detail);
        if (event.detail && event.detail.templateData) {
            const templateData = event.detail.templateData;
            showToast('info', `Loading structure from template: ${templateData.template_name || 'Unnamed Template'}`);
            
            // Re-populate widgets with the new data
            populateGuildDesignerWidgets(templateData);
            // Re-initialize the structure tree with the new data
            initializeStructureTree(templateData);
        } else {
            console.error("[Index] 'loadTemplateData' event received without valid template data in detail.");
            showToast('error', 'Failed to load template data from event.');
        }
    });
    console.log("[Index] 'loadTemplateData' event listener is active.");
}
// --- END NEW LISTENER ---

// --- Main Execution ---
document.addEventListener('DOMContentLoaded', async () => {
    console.log("[Index] DOM fully loaded.");

    const guildId = getGuildIdFromUrl();
    if (!guildId) {
        displayErrorMessage('Could not determine Guild ID. Cannot initialize designer.');
        return;
    }

    const gridContainer = document.getElementById('designer-grid');
    const lockButton = document.getElementById('toggle-lock-btn');
    const resetButton = document.getElementById('reset-layout-btn');

    if (!gridContainer || !lockButton || !resetButton) {
        console.error('[Index] Essential UI elements missing.');
        displayErrorMessage('Initialization failed: Core UI elements missing.');
        return;
    }

    try {
        // 1. Fetch Initial Data (Template for content)
        console.log("[Index] Fetching initial template data...");
        const templateData = await fetchGuildTemplate(guildId);
        if (!templateData) {
             console.error("[Index] Failed to fetch initial template data. Stopping initialization.");
            // Error message already shown by fetchGuildTemplate
            return; 
        }
        console.log("[Index] Initial template data fetched.");

        // 2. Define Widgets and Default Layout
        console.log("[Index] Defining widgets and default layout...");
        const pageIdentifier = `guild-designer-${guildId}`;
        const widgetDefs = {
            'structure-tree': { title: 'Guild Structure', content: '<div id="widget-content-structure-tree">Loading tree...</div>' },
            'template-info': { title: 'Template Information', content: '<div id="widget-content-template-info">Loading...</div>' },
            'categories': { title: 'Categories (List View)', content: '<div id="widget-content-categories">Loading...</div>', headerControls: [{ type: 'link', text: 'Manage', href: `/guild/${guildId}/designer/categories`, class: 'manage-link' }] },
            'channels': { title: 'Channels (List View)', content: '<div id="widget-content-channels">Loading...</div>', headerControls: [{ type: 'link', text: 'Manage', href: `/guild/${guildId}/designer/channels`, class: 'manage-link' }] },
            'template-list': { title: 'Saved Templates', content: '<div id="widget-content-template-list">Loading templates...</div>' },
            'shared-template-list': { title: 'Shared Templates', content: '<div id="widget-content-shared-template-list">Loading shared templates...</div>' },
        };
        const defaultLayout = [
            { id: 'structure-tree', x: 0, y: 0, w: 4, h: 8, minW: 3, minH: 5 },
            { id: 'template-info', x: 4, y: 0, w: 4, h: 2, minW: 3, minH: 2 },
            { id: 'categories', x: 4, y: 2, w: 4, h: 3, minW: 3, minH: 3 },
            { id: 'channels', x: 8, y: 0, w: 4, h: 5, minW: 3, minH: 4 },
            { id: 'template-list', x: 4, y: 5, w: 4, h: 3, minW: 3, minH: 3 },
            { id: 'shared-template-list', x: 8, y: 5, w: 4, h: 3, minW: 3, minH: 3 },
        ];
        console.log("[Index] Widget definitions:", widgetDefs);
        console.log("[Index] Default layout:", defaultLayout);

        // 3. Initialize GridManager
        console.log("[Index] Initializing GridManager...");
        const debouncedSaveLayout = debounce((grid) => saveLayout(grid, pageIdentifier), 1000); 
        const gridManager = new GridManager({
            gridElementId: 'designer-grid', // Specify the correct container ID
            pageIdentifier: pageIdentifier,
            widgetDefinitions: widgetDefs, // Pass definitions here
            defaultLayout: defaultLayout, // Pass default layout here
            // Modified callback to include tree initialization
            populateContentCallback: (initialData) => { 
                console.log("[GridManager Callback] Populating widget content.");
                console.log("[GridManager Callback] Received initialData:", initialData);
                // Use the data passed by GridManager (which should be the templateData we provided)
                populateGuildDesignerWidgets(initialData, null, null); 
                console.log("[GridManager Callback] Initializing structure tree.");
                initializeStructureTree(initialData);
            },
            resetRequiresDataCallback: () => fetchGuildTemplate(guildId), // Fetch fresh data on reset
        });

        const grid = await gridManager.initialize(templateData); // Initialize (loads/renders layout)
        console.log("[Index] GridManager initialized.");

        // --- Setup Listeners --- 
        setupPanelToggles();
        setupTemplateLoadListener(); // Activate the new listener

        console.log("[Index] Guild Designer initialization sequence complete.");

    } catch (error) {
        console.error("[Index] Error during Guild Designer initialization process:", error);
        displayErrorMessage('An unexpected error occurred during initialization. Please check the console.');
    }

    // --- Share Template Modal Logic ---
    const confirmShareBtn = document.getElementById('confirmShareTemplateBtn');
    const shareModalElement = document.getElementById('shareTemplateModal');
    const shareTemplateNameInput = document.getElementById('shareTemplateNameInput');
    const shareTemplateDescInput = document.getElementById('shareTemplateDescriptionInput');
    const shareTemplateIdInput = document.getElementById('shareTemplateIdInput'); // Hidden input

    if (confirmShareBtn && shareModalElement && shareTemplateNameInput && shareTemplateDescInput && shareTemplateIdInput) {
        // Get the Bootstrap modal instance
        const shareModal = bootstrap.Modal.getInstance(shareModalElement) || new bootstrap.Modal(shareModalElement);

        confirmShareBtn.addEventListener('click', async () => {
            const originalTemplateId = shareTemplateIdInput.value;
            const newTemplateName = shareTemplateNameInput.value.trim();
            const newTemplateDescription = shareTemplateDescInput.value.trim();

            // --- Basic Validation ---
            shareTemplateNameInput.classList.remove('is-invalid'); // Reset validation state
            if (!newTemplateName || newTemplateName.length < 3 || newTemplateName.length > 100) {
                shareTemplateNameInput.classList.add('is-invalid');
                // Optionally show a small message near the input or rely on the default invalid-feedback div
                console.warn("[ShareModal] Validation failed: Template name is required (3-100 chars).");
                return; // Stop submission
            }
            // --- End Validation ---


            // --- API Call ---
            // TODO: Confirm the correct API endpoint and method for sharing/saving as new
            const shareApiUrl = `/api/v1/templates/guilds/share`; 
            const payload = {
                original_template_id: originalTemplateId,
                new_template_name: newTemplateName,
                new_template_description: newTemplateDescription,
                // Add any other required fields for the API
            };

            console.log(`[ShareModal] Attempting to share template. Payload:`, payload);

            try {
                // Disable button during request
                confirmShareBtn.disabled = true;
                confirmShareBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Sharing...
                `;

                const response = await apiRequest(shareApiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });

                // Assuming the API returns the new template info or just success
                console.log('[ShareModal] Share request successful:', response);
                showToast('success', `Template "${newTemplateName}" shared successfully!`);
                
                // TODO: Optionally refresh the template list widget if needed
                // const templateListWidgetContent = document.getElementById('widget-content-template-list');
                // if (templateListWidgetContent) {
                //     const currentGuildId = getGuildIdFromUrl(); 
                //     initializeTemplateList(templateListWidgetContent, currentGuildId);
                // }

                shareModal.hide(); // Close modal on success

            } catch (error) {
                console.error('[ShareModal] Error sharing template:', error);
                // apiRequest should handle showing an error toast, but we can add more specific feedback if needed
                // Maybe display error within the modal? For now, rely on toast.
            } finally {
                 // Re-enable button and restore text
                confirmShareBtn.disabled = false;
                confirmShareBtn.innerHTML = 'Share Template';
                // Clear inputs *after* potential failure might be better UX depending on requirements
                // shareTemplateNameInput.value = ''; 
                // shareTemplateDescInput.value = '';
                // shareTemplateIdInput.value = ''; // Clear hidden ID too
                shareTemplateNameInput.classList.remove('is-invalid'); // Clear validation state on close/finish
            }
            // --- End API Call ---
        });

         // Optional: Clear validation state when modal is hidden
        shareModalElement.addEventListener('hidden.bs.modal', () => {
            shareTemplateNameInput.classList.remove('is-invalid');
        });

    } else {
        console.warn('[Index] Could not find all required elements for the Share Template modal logic.');
    }
    // --- End Share Template Modal Logic ---
}); 