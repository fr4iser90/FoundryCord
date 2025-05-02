import { apiRequest, showToast } from '/static/js/components/common/notifications.js';
// GridStack is assumed to be globally available via CDN in the base template

/**
 * Saves the current grid layout to the backend.
 * @param {GridStack} grid - The GridStack instance.
 * @param {string} pageIdentifier - The unique identifier for the page layout.
 */
export async function saveLayout(grid, pageIdentifier) {
    if (!grid) {
        console.error("[DesignerLayout] Cannot save layout: Grid instance is not available.");
        return;
    }
    console.log(`[DesignerLayout] Saving layout for ${pageIdentifier}`);
    
    // Manually collect layout data including height (h)
    const currentLayout = grid.engine.nodes.map(node => ({
        id: node.id, 
        x: node.x,
        y: node.y,
        w: node.w,
        h: node.h // Ensure height is included
        // Include other necessary properties if backend expects them (minW, minH etc.)
        // Example: minW: node.minW, minH: node.minH 
    }));

    const isLocked = grid.opts.disableDrag; // Assuming disableDrag reflects the locked state
    
    const payload = {
        layout: currentLayout,
        is_locked: isLocked
    };

    const apiUrl = `/api/v1/layouts/${pageIdentifier}`;
    console.log(`[DesignerLayout] Saving layout to: ${apiUrl}`);

    try {
        await apiRequest(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        // Success toast is optional here, could be annoying
        // showToast('success', 'Layout saved.'); 
        console.log("[DesignerLayout] Layout save request successful.");
    } catch (error) {
        console.error("[DesignerLayout] Failed to save layout:", error.message);
        // apiRequest handles error toast
    }
}

/**
 * Resets the layout by deleting the saved state and potentially reloading defaults.
 * @param {GridStack} grid - The GridStack instance.
 * @param {string} pageIdentifier - The unique identifier for the page layout.
 * @param {Function} renderDefaultsCallback - A function to call to re-render the default widgets.
 */
export async function resetLayout(grid, pageIdentifier, renderDefaultsCallback) {
    console.log(`[DesignerLayout] Resetting layout for ${pageIdentifier}`);
    const apiUrl = `/api/v1/layouts/${pageIdentifier}`;
    try {
        await apiRequest(apiUrl, { method: 'DELETE' });
        showToast('success', 'Layout reset successfully! Reloading default widgets...');
        
        // Call the provided callback to render defaults
        if (renderDefaultsCallback && typeof renderDefaultsCallback === 'function') {
             // Potentially needs to refetch data before rendering, handled by caller
             renderDefaultsCallback(); 
        } else {
             console.error("[DesignerLayout] Cannot render default layout after reset: renderDefaultsCallback missing or invalid.")
             // Maybe force a page reload as fallback?
             // window.location.reload(); 
        }
    } catch (error) {
        console.error("[DesignerLayout] Failed to reset layout:", error);
        // apiRequest should have shown an error toast
    }
}

/**
 * Updates the lock button appearance based on the grid lock state.
 * @param {GridStack} grid - The GridStack instance.
 * @param {HTMLButtonElement} lockButton - The button element used to toggle lock state.
 */
export function setLockButtonAppearance(grid, lockButton) {
    if (!grid || !lockButton) return;

    const icon = lockButton.querySelector('i');
    const textSpan = lockButton.querySelector('.btn-text'); // Assuming text is in a span
    
    if (!icon || !textSpan) {
        console.warn("[DesignerLayout] Lock button icon or text span not found.");
        return;
    }

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
 * @param {function} saveCallback - The function to call to save the layout (debounced or immediate).
 */
export function toggleLayoutLockAndSave(grid, lockButton, saveCallback) {
    if (!grid || !lockButton || !saveCallback) return;

    const isCurrentlyLocked = grid.opts.disableDrag;

    if (isCurrentlyLocked) { // Unlock it
        grid.enableMove(true);
        grid.enableResize(true);
        grid.opts.disableDrag = false;
        grid.opts.disableResize = false;
        showToast('info', 'Layout unlocked for editing.');
    } else { // Lock it
        grid.enableMove(false);
        grid.enableResize(false);
        grid.opts.disableDrag = true;
        grid.opts.disableResize = true;
        showToast('info', 'Layout locked.');
    }

    setLockButtonAppearance(grid, lockButton);
    saveCallback(); // Trigger the save
}

/**
 * Creates a standard widget structure for Gridstack.
 * @param {string} id - Unique ID for the widget.
 * @param {string} title - Title for the widget header.
 * @param {string} contentHtml - Initial HTML content for the widget body.
 * @param {object} gridOptions - Gridstack options (x, y, w, h, etc.).
 * @param {Array} [headerControls=[]] - Optional array of header control definitions.
 * @returns {HTMLElement} The widget element to be added to the grid.
 */
function createWidgetElement(id, title, contentHtml, gridOptions, headerControls = []) {
    const widget = document.createElement('div');
    widget.className = 'grid-stack-item';
    widget.setAttribute('gs-id', id);
    for (const key in gridOptions) {
        widget.setAttribute(`gs-${key}`, gridOptions[key]);
    }

    // Basic structure
    const itemContent = document.createElement('div');
    itemContent.className = 'grid-stack-item-content';
    
    const header = document.createElement('div');
    header.className = 'widget-header d-flex align-items-center'; // Use flex for alignment
    
    const titleSpan = document.createElement('span');
    titleSpan.textContent = title;
    header.appendChild(titleSpan);
    
    // Add header controls
    if (headerControls.length > 0) {
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'ms-auto'; // Push controls to the right
        headerControls.forEach(control => {
            if (control.type === 'link') {
                const link = document.createElement('a');
                link.href = control.href || '#';
                link.className = `btn btn-sm btn-outline-primary ${control.class || ''}`;
                link.textContent = control.text || 'Manage';
                if (control.title) link.title = control.title;
                controlsDiv.appendChild(link);
            }
            // Add other control types (buttons, etc.) here if needed
        });
        header.appendChild(controlsDiv);
    }

    const contentArea = document.createElement('div');
    contentArea.className = 'widget-content widget-content-area';
    contentArea.id = `widget-content-${id}`;
    contentArea.innerHTML = contentHtml;

    itemContent.appendChild(header);
    itemContent.appendChild(contentArea);
    widget.appendChild(itemContent);

    return widget;
}

/**
 * Initializes the Gridstack instance.
 * Checks if GridStack is loaded.
 * @param {string} gridElementId - The ID of the container element.
 * @returns {GridStack|null} The initialized GridStack object or null if GridStack or element not found.
 */
export function initializeGrid(gridElementId = 'designer-grid') {
    if (typeof GridStack === 'undefined') {
        console.error('[DesignerLayout] GridStack library is not loaded.');
        return null;
    }
    const gridElement = document.getElementById(gridElementId);
    if (!gridElement) {
        console.error(`[DesignerLayout] Gridstack container #${gridElementId} not found.`);
        return null;
    }
    try {
        const grid = GridStack.init({
            cellHeight: 70,
            margin: 10,
            float: true,
            disableResize: false,
            disableDrag: false
        });
        console.log("[DesignerLayout] GridStack initialized.");
        return grid;
    } catch (error) {
        console.error("[DesignerLayout] Error initializing GridStack:", error);
        return null;
    }
}

/**
 * Loads the saved layout for a given page identifier from the API.
 * @param {string} pageIdentifier - The unique identifier for the page layout.
 * @returns {Promise<object|null>} Layout data { layout: [...], is_locked: ... } if found, otherwise null.
 */
export async function loadLayout(pageIdentifier) {
    const apiUrl = `/api/v1/layouts/${pageIdentifier}`;
    console.log(`[DesignerLayout] Attempting to load layout from: ${apiUrl}`);
    try {
        const rawResponse = await apiRequest(apiUrl);
        if (rawResponse && typeof rawResponse === 'object' && Array.isArray(rawResponse.layout)) {
            console.log("[DesignerLayout] Saved layout data loaded:", rawResponse);
            return rawResponse; 
        } else {
            console.log("[DesignerLayout] No saved layout found or response format invalid.");
            return null;
        }
    } catch (error) {
        // Treat 404 as "no layout found", other errors might be more serious
        if (error.status === 404) {
             console.log(`[DesignerLayout] No saved layout found for ${pageIdentifier} (404).`);
        } else {
             console.error(`[DesignerLayout] Error loading layout for ${pageIdentifier}:`, error);
        }        
        return null;
    }
}

/**
 * Contains the definitions (title, initial content) for all available widgets.
 */
export const widgetDefinitions = {
    'structure-tree': { title: 'Guild Structure', content: '<div id="widget-content-structure-tree">Loading tree...</div>' },
    'template-info': { title: 'Template Information', content: '<div id="widget-content-template-info">Loading...</div>' },
    'categories': { title: 'Categories', content: '<div id="widget-content-categories">Loading...</div>', headerControls: [{ type: 'link', text: 'Manage', href: '', class: 'manage-link', id: 'manage-categories-link' }] }, // Placeholder href
    'channels': { title: 'Channels', content: '<div id="widget-content-channels">Loading...</div>', headerControls: [{ type: 'link', text: 'Manage', href: '', class: 'manage-link', id: 'manage-channels-link' }] }, // Placeholder href
    'template-list': { title: 'Saved Templates', content: '<div id="widget-content-template-list">Loading templates...</div>' },
    'shared-template-list': { title: 'Shared Templates', content: '<div id="widget-content-shared-template-list">Loading shared templates...</div>' },
    // --- Add the new Dashboard Editor widget definition ---
    'dashboard-editor': {
        title: 'Dashboard Editor',
        content: '<div id="widget-content-dashboard-editor"><p class="text-muted p-2">Loading editor...</p></div>'
    },
    // ----------------------------------------------------
    // --- Add the new Dashboard Preview widget definition ---
    'dashboard-preview': {
        title: 'Dashboard Preview',
        content: '<div id="widget-content-dashboard-preview">Loading preview...</div>'
        // Add initialization logic later
    },
    // --- Add the Dashboard Configuration List widget definition --- 
    'dashboard-configuration': { 
        title: 'Dashboard Configuration', 
        content: '<div id="widget-content-dashboard-configuration">Loading configuration...</div>' 
        // Add initialization logic later
    },
};

/**
 * Defines the default layout (positions and sizes) for the widgets.
 */
export const defaultLayout = [
    { id: 'structure-tree', x: 0, y: 0, w: 4, h: 8, minW: 3, minH: 5 },
    { id: 'template-info', x: 4, y: 0, w: 4, h: 2, minW: 3, minH: 2, maxH: 2 }, // Added maxH
    { id: 'categories', x: 4, y: 2, w: 4, h: 3, minW: 3, minH: 3 },
    { id: 'channels', x: 8, y: 0, w: 4, h: 5, minW: 3, minH: 4 },
    { id: 'template-list', x: 4, y: 5, w: 4, h: 3, minW: 3, minH: 3 }, // Adjusted y to make space
    { id: 'shared-template-list', x: 8, y: 5, w: 4, h: 3, minW: 3, minH: 3 }, // Adjusted y to make space
    // Add dashboard widgets
    { id: 'dashboard-editor', x: 0, y: 8, w: 6, h: 5, minW: 4, minH: 4 }, // Place below structure tree
    { id: 'dashboard-preview', x: 6, y: 8, w: 6, h: 5, minW: 4, minH: 4 }, // Place next to editor
    { id: 'dashboard-configuration', x: 4, y: 8, w: 8, h: 3, minW: 4, minH: 3 }
];

/**
 * Renders the default set of widgets into the grid based on the defaultLayout.
 * @param {GridStack} grid - The GridStack instance.
 * @param {object} widgetDefs - The definitions for all widgets.
 * @param {Array} defaultLayoutConf - The default layout configuration.
 */
export function renderDefaultWidgets(grid, widgetDefs = widgetDefinitions, defaultLayoutConf = defaultLayout) {
    if (!grid) {
        console.error("[DesignerLayout] Cannot render default widgets: Grid instance is missing.");
        return;
    }
    console.log("[DesignerLayout] Rendering default widgets...");
    grid.removeAll(); // Clear existing widgets first
    
    defaultLayoutConf.forEach(item => {
        const def = widgetDefs[item.id];
        if (def) {
            const widgetEl = createWidgetElement(item.id, def.title, def.content, item, def.headerControls);
            grid.addWidget(widgetEl);
        } else {
            console.warn(`[DesignerLayout] Widget definition not found for default layout item ID: ${item.id}`);
        }
    });
    console.log("[DesignerLayout] Default widgets rendered.");
}

// Initial log to confirm loading
console.log("[DesignerLayout] Layout module loaded.");
