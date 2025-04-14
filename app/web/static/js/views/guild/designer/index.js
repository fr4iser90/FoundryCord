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
        'template-list', // Added new widget
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
            <div class="widget-content" id="widget-content-${id}">
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

    // --- Render Template Info Widget --- 
    const templateInfoContent = `
        <h5>${templateData.template_name || 'Unnamed Template'}</h5>
        <p class="mb-0"><small class="text-muted">Created: ${templateData.created_at ? new Date(templateData.created_at).toLocaleString() : 'N/A'}</small></p>
    `;
    const templateInfoWidget = createWidgetElement(
        'template-info', // ID used for targeting content later
        'Template Information',
        templateInfoContent,
        { x: 0, y: 0, w: 4, h: 2 } // Default position
    );
    grid.addWidget(templateInfoWidget);

    // --- Render Categories Widget --- 
    const categoriesById = {}; // Still needed for channels even in default
    let categoriesContent = '<p class="text-muted p-3">No categories defined.</p>'; 
    if (Array.isArray(templateData.categories) && templateData.categories.length > 0) {
        templateData.categories.sort((a, b) => a.position - b.position);
        const listItems = templateData.categories.map(cat => {
            if (cat && cat.id) { 
                 categoriesById[cat.id] = cat;
            }
            return `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <span><i class="fas fa-folder me-2"></i> ${cat.name || 'Unnamed Category'}</span>
                    <span class="badge bg-secondary rounded-pill">Pos: ${cat.position !== undefined ? cat.position : 'N/A'}</span>
                </li>
            `;
        }).join('');
        categoriesContent = `<ul class="list-group list-group-flush">${listItems}</ul>`;
    } else {
        console.warn("No categories data found or data is not an array for default render.");
    }
    const categoriesWidget = createWidgetElement(
        'categories', // ID used for targeting content later
        'Categories',
        categoriesContent,
        { x: 4, y: 0, w: 4, h: 4 } // Default position
    );
    const categoriesHeader = categoriesWidget.querySelector('.widget-header');
    const guildId = getGuildIdFromUrl();
    if (categoriesHeader && guildId) {
        const manageLink = document.createElement('a');
        manageLink.href = `/guild/${guildId}/designer/categories`;
        manageLink.className = 'btn btn-sm btn-outline-primary';
        manageLink.textContent = 'Manage';
        categoriesHeader.appendChild(manageLink);
    }
    grid.addWidget(categoriesWidget);

    // --- Render Channels Widget ---
    let channelsContent = '<p class="text-muted p-3">No channels defined.</p>'; 
    if (Array.isArray(templateData.channels) && templateData.channels.length > 0) {
        templateData.channels.sort((a, b) => {
            const parentA = a?.parent_category_template_id;
            const parentB = b?.parent_category_template_id;
            const catA = categoriesById[parentA];
            const catB = categoriesById[parentB];
            const posA = parentA === null ? Infinity : (catA ? catA.position : Infinity - 1);
            const posB = parentB === null ? Infinity : (catB ? catB.position : Infinity - 1);
            if (posA !== posB) return posA - posB;
            const channelPosA = typeof a?.position === 'number' ? a.position : Infinity;
            const channelPosB = typeof b?.position === 'number' ? b.position : Infinity;
            return channelPosA - channelPosB;
        });
        const listItems = templateData.channels.map(chan => {
             if (!chan) return ''; 
            const category = categoriesById[chan.parent_category_template_id];
            const categoryName = category ? category.name : 'Uncategorized';
            let channelIcon = 'fa-question-circle';
            if (chan.type === 'GUILD_TEXT') channelIcon = 'fa-hashtag';
            else if (chan.type === 'GUILD_VOICE') channelIcon = 'fa-volume-up';
            return `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <span>
                        <i class="fas ${channelIcon} me-2"></i>
                        ${chan.name || 'Unnamed Channel'} <small class="text-muted">(${categoryName})</small>
                    </span>
                    <span class="badge bg-secondary rounded-pill">Pos: ${chan.position !== undefined ? chan.position : 'N/A'}</span>
                </li>
            `;
        }).join('');
        channelsContent = `<ul class="list-group list-group-flush">${listItems}</ul>`;
    } else {
        console.warn("No channels data found or data is not an array for default render.");
    }
    const channelsWidget = createWidgetElement(
        'channels', // ID used for targeting content later
        'Channels',
        channelsContent,
        { x: 8, y: 0, w: 4, h: 4 } // Default position
    );
    const channelsHeader = channelsWidget.querySelector('.widget-header');
    if (channelsHeader && guildId) { 
        const manageLink = document.createElement('a');
        manageLink.href = `/guild/${guildId}/designer/channels`; 
        manageLink.className = 'btn btn-sm btn-outline-primary';
        manageLink.textContent = 'Manage';
        channelsHeader.appendChild(manageLink);
    }
    grid.addWidget(channelsWidget);

    console.log("Default widgets added to grid.");
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
         infoContentEl.innerHTML = `
            <h5>${templateData.template_name || 'Unnamed Template'}</h5>
            <p class="mb-0"><small class="text-muted">Created: ${templateData.created_at ? new Date(templateData.created_at).toLocaleString() : 'N/A'}</small></p>
        `;
    } else {
        console.warn("Content area for template-info widget not found.");
    }

    // --- Populate Categories --- 
    const categoriesById = {};
    const categoriesContentEl = document.getElementById('widget-content-categories');
    if (categoriesContentEl) {
        if (Array.isArray(templateData.categories) && templateData.categories.length > 0) {
             templateData.categories.sort((a, b) => a.position - b.position);
            const listItems = templateData.categories.map(cat => {
                 if (cat && cat.id) { categoriesById[cat.id] = cat; }
                 return `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span><i class="fas fa-folder me-2"></i> ${cat.name || 'Unnamed Category'}</span>
                        <span class="badge bg-secondary rounded-pill">Pos: ${cat.position !== undefined ? cat.position : 'N/A'}</span>
                    </li>
                `;
            }).join('');
            categoriesContentEl.innerHTML = `<ul class="list-group list-group-flush">${listItems}</ul>`;
            
            // Ensure Manage link exists (it might not be created by grid.load)
            const header = categoriesContentEl.closest('.grid-stack-item-content')?.querySelector('.widget-header');
            if(header && guildId && !header.querySelector('a')) {
                 const manageLink = document.createElement('a');
                manageLink.href = `/guild/${guildId}/designer/categories`;
                manageLink.className = 'btn btn-sm btn-outline-primary';
                manageLink.textContent = 'Manage';
                header.appendChild(manageLink);
            }
        } else {
            categoriesContentEl.innerHTML = '<p class="text-muted p-3">No categories defined.</p>';
        }
    } else {
         console.warn("Content area for categories widget not found.");
    }

    // --- Populate Channels --- 
    const channelsContentEl = document.getElementById('widget-content-channels');
    if (channelsContentEl) {
         if (Array.isArray(templateData.channels) && templateData.channels.length > 0) {
            // categoriesById map should be populated from the step above
            templateData.channels.sort((a, b) => {
                const parentA = a?.parent_category_template_id;
                const parentB = b?.parent_category_template_id;
                const catA = categoriesById[parentA];
                const catB = categoriesById[parentB];
                const posA = parentA === null ? Infinity : (catA ? catA.position : Infinity - 1);
                const posB = parentB === null ? Infinity : (catB ? catB.position : Infinity - 1);
                if (posA !== posB) return posA - posB;
                const channelPosA = typeof a?.position === 'number' ? a.position : Infinity;
                const channelPosB = typeof b?.position === 'number' ? b.position : Infinity;
                return channelPosA - channelPosB;
            });
            const listItems = templateData.channels.map(chan => {
                if (!chan) return ''; 
                const category = categoriesById[chan.parent_category_template_id];
                const categoryName = category ? category.name : 'Uncategorized';
                let channelIcon = 'fa-question-circle';
                if (chan.type === 'GUILD_TEXT') channelIcon = 'fa-hashtag';
                else if (chan.type === 'GUILD_VOICE') channelIcon = 'fa-volume-up';
                return `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span>
                            <i class="fas ${channelIcon} me-2"></i>
                            ${chan.name || 'Unnamed Channel'} <small class="text-muted">(${categoryName})</small>
                        </span>
                        <span class="badge bg-secondary rounded-pill">Pos: ${chan.position !== undefined ? chan.position : 'N/A'}</span>
                    </li>
                `;
            }).join('');
            channelsContentEl.innerHTML = `<ul class="list-group list-group-flush">${listItems}</ul>`;

             // Ensure Manage link exists
            const header = channelsContentEl.closest('.grid-stack-item-content')?.querySelector('.widget-header');
            if(header && guildId && !header.querySelector('a')) {
                 const manageLink = document.createElement('a');
                manageLink.href = `/guild/${guildId}/designer/channels`; 
                manageLink.className = 'btn btn-sm btn-outline-primary';
                manageLink.textContent = 'Manage';
                header.appendChild(manageLink);
            }
         } else {
             channelsContentEl.innerHTML = '<p class="text-muted p-3">No channels defined.</p>';
         }
    } else {
        console.warn("Content area for channels widget not found.");
    }

    console.log("Existing widget contents populated.");
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
        };
        const defaultLayout = [
            { id: 'structure-tree', x: 0, y: 0, w: 4, h: 8, minW: 3, minH: 5 },
            { id: 'template-info', x: 4, y: 0, w: 4, h: 2, minW: 3, minH: 2 },
            { id: 'categories', x: 4, y: 2, w: 4, h: 3, minW: 3, minH: 3 },
            { id: 'channels', x: 8, y: 0, w: 4, h: 5, minW: 3, minH: 4 },
            { id: 'template-list', x: 4, y: 5, w: 4, h: 3, minW: 3, minH: 3 },
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

        // 4. Populate Initial Content (REMOVED - Handled by GridManager callback now)
        /*
        if (grid) {
            console.log("[Index] Populating initial content for all widgets...");
            populateGuildDesignerWidgets(templateData, null, null); 
            console.log("[Index] Initializing structure tree...");
            initializeStructureTree(templateData); // Initialize the tree now
            console.log("[Index] Structure tree initialization called.");
        } else {
            console.error("[Index] Grid initialization failed. Cannot populate content.");
            displayErrorMessage('Failed to initialize the layout grid.');
        }
        */

        // 5. Setup Panel Toggles
        setupPanelToggles();

        console.log("[Index] Guild Designer initialization sequence complete.");

    } catch (error) {
        console.error("[Index] Error during Guild Designer initialization process:", error);
        displayErrorMessage('An unexpected error occurred during initialization. Please check the console.');
    }
}); 