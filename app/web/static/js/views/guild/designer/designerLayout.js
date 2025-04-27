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
    
    const currentLayout = grid.save(false); 
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
 * Renders the default widgets based on provided definitions and layout.
 * @param {GridStack} grid - The initialized Gridstack instance.
 * @param {object} widgetDefinitions - Object mapping widget IDs to { title, content, headerControls? }.
 * @param {Array} defaultLayout - Array of Gridstack layout items { id, x, y, w, h, ... }.
 */
export function renderDefaultWidgets(grid, widgetDefinitions, defaultLayout) {
    console.log("[DesignerLayout] Rendering default widgets...");
    if (!grid) {
        console.error("[DesignerLayout] Gridstack instance is not available for rendering defaults.");
        return;
    }
    if (!widgetDefinitions || !defaultLayout) {
        console.error("[DesignerLayout] Widget definitions or default layout missing.");
        return;
    }

    grid.removeAll(); // Clear existing grid items

    defaultLayout.forEach(item => {
        const definition = widgetDefinitions[item.id];
        if (definition) {
            const widgetEl = createWidgetElement(
                item.id,
                definition.title,
                definition.content, // Initial content placeholder
                item, // Pass grid options (x, y, w, h, etc.)
                definition.headerControls // Pass header controls
            );
            grid.addWidget(widgetEl);
        } else {
            console.warn(`[DesignerLayout] Definition not found for default widget ID: ${item.id}`);
        }
    });

    console.log("[DesignerLayout] Default widgets added to grid.");
}


// Initial log to confirm loading
console.log("[DesignerLayout] Layout module loaded.");
