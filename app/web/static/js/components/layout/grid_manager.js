import { apiRequest, showToast } from '/static/js/components/common/notifications.js';

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
            func.apply(this, args); // Use apply to maintain context
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Manages a Gridstack layout, including loading, saving, locking, and resetting.
 */
export class GridManager {
    constructor(options) {
        this.options = {
            gridElementId: 'grid-stack',
            lockButtonId: 'toggle-lock-btn',
            resetButtonId: 'reset-layout-btn',
            pageIdentifier: null, // Must be provided
            widgetDefinitions: {}, // { widgetId: 'Widget Title', ... }
            defaultLayout: [], // Array of { id, x, y, w, h }
            populateContentCallback: (data) => { console.warn("populateContentCallback not provided to GridManager") }, // Callback to fill widgets with page-specific data
            resetRequiresDataCallback: async () => null, // Callback to get data needed for default render after reset
            saveDebounceWait: 1500,
            ...options // Override defaults with provided options
        };

        if (!this.options.pageIdentifier) {
            throw new Error("GridManager requires a 'pageIdentifier' option.");
        }

        this.grid = null;
        this.lockButton = document.getElementById(this.options.lockButtonId);
        this.resetButton = document.getElementById(this.options.resetButtonId);
        this.currentData = null; // To store data needed for reset/populate

        // Bind methods to ensure 'this' context is correct
        this._saveLayout = this._saveLayout.bind(this);
        this._resetLayout = this._resetLayout.bind(this);
        this._toggleLayoutLockAndSave = this._toggleLayoutLockAndSave.bind(this);
        this.debouncedSave = debounce(this._saveLayout, this.options.saveDebounceWait);

        console.log("GridManager instantiated with options:", this.options);
    }

    /**
     * Initializes the GridManager: finds elements, initializes Gridstack, loads data, sets up listeners.
     * @param {object} initialData - Optional initial data needed by populateContentCallback.
     */
    async initialize(initialData = null) {
        console.log("GridManager initializing...");
        this.currentData = initialData; // Store initial data

        this.grid = this._initializeGrid();
        if (!this.grid) {
             console.error("GridManager initialization failed: Could not initialize grid.");
             return;
        }

        // Buttons are already fetched in constructor, check if found
        if (!this.lockButton) console.warn(`Lock button #${this.options.lockButtonId} not found.`);
        if (!this.resetButton) console.warn(`Reset button #${this.options.resetButtonId} not found.`);


        try {
            const savedData = await this._loadLayout();
            await this._applyInitialState(savedData);
        } catch (error) {
            console.error("Error during GridManager loading sequence:", error);
            this._displayError("An error occurred while loading the layout state.");
            // Fallback to default state on error
            try {
                 console.warn("Attempting to render default layout as fallback.");
                 // Ensure we have data for defaults, fetch if needed (might fail again)
                 if (!this.currentData && this.options.resetRequiresDataCallback) {
                     this.currentData = await this.options.resetRequiresDataCallback();
                 }
                this._renderDefaultWidgets();
                this._applyInitialLockState(true); // Default to locked on error
            } catch (fallbackError) {
                 console.error("Fallback to default layout also failed:", fallbackError);
                 this._displayError("Failed to load saved layout and could not render default layout.");
            }
        }

        this._setupEventListeners();
        if (this.lockButton) {
             this._setLockButtonAppearance(); // Set initial button appearance based on applied state
             console.log("Initial lock button appearance set.");
        }
         console.log("GridManager initialization complete.");
    }

    // --- Private Helper Methods ---

    _initializeGrid() {
        const gridElement = document.getElementById(this.options.gridElementId);
        if (!gridElement) {
            console.error(`Gridstack container #${this.options.gridElementId} not found.`);
            // No need for _displayError here, handled by the check in initialize()
            return null;
        }
         console.log(`Initializing Gridstack for element #${this.options.gridElementId}`);
        try {
            const grid = GridStack.init({
                cellHeight: 70,
                margin: 10,
                float: true,
                disableResize: false, // Initial state set after loading data
                disableDrag: false,
                // Let Gridstack handle content via `load` with the 'content' property
            });
            console.log("Gridstack initialized successfully.");
            return grid;
        } catch(error) {
             console.error("Gridstack initialization failed:", error);
             this._displayError("Failed to initialize the grid system.");
             return null;
        }
    }

    async _loadLayout() {
        const apiUrl = `/api/v1/layouts/${this.options.pageIdentifier}`;
        console.log(`Loading layout from: ${apiUrl}`);
        try {
            const rawResponse = await apiRequest(apiUrl);
            console.log(`Raw response from ${apiUrl}:`, rawResponse);
            // API expected to return { layout: [...], is_locked: ... } or null/404
            if (rawResponse && typeof rawResponse === 'object' && Array.isArray(rawResponse.layout)) {
                 console.log("Saved layout data appears valid.");
                 return rawResponse;
             } else {
                 console.log("No saved layout found or response format invalid.");
                 return null; // Treat as no saved layout
             }
        } catch (error) {
             // apiRequest should handle errors, but catch potential issues
             console.error(`Error loading layout for ${this.options.pageIdentifier}:`, error);
             // Treat error during load as "no layout found" for flow
             return null;
        }
    }

    async _saveLayout() {
        if (!this.grid) {
             console.error("Save aborted: Grid not initialized.");
             return;
        }
        console.log(`Saving layout for ${this.options.pageIdentifier}...`);

        const currentLayout = this.grid.save(false); // Get only layout structure
        const isLocked = this.grid.opts.disableDrag;
        const payload = {
            layout: currentLayout,
            is_locked: isLocked
        };

        const apiUrl = `/api/v1/layouts/${this.options.pageIdentifier}`;
        console.log(`Sending save request to: ${apiUrl}`);

        try {
            // Let apiRequest handle success/error toasts & basic errors
            await apiRequest(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            console.log(`Layout save request for ${this.options.pageIdentifier} completed.`);
         } catch (error) {
             // Catch errors not handled by apiRequest or re-thrown
             console.error(`Failed to save layout (error caught in _saveLayout for ${this.options.pageIdentifier}):`, error.message);
             // Display a manager-specific error if needed
             this._displayError("Failed to save the layout changes.");
        }
    }

    // Generates the inner HTML string for a widget, used when loading data
    _getWidgetInnerHtml(id, title) {
         const safeTitle = title || 'Widget'; // Ensure title is a string
         return `
            <div class="grid-stack-item-content">
                <div class="widget-header"><span>${safeTitle}</span></div>
                <div class="widget-content" id="widget-content-${id}"></div>
            </div>`;
    }

     _renderDefaultWidgets() {
        if (!this.grid) return;
        console.log("Rendering default widgets...");
        this.grid.removeAll();

        // Prepare widgets with content for grid.load()
        const defaultLayoutWithContent = this.options.defaultLayout.map(item => {
            const widgetId = item?.id;
            if (!widgetId) {
                 console.warn("Skipping default layout item with missing ID:", item);
                 return null;
            }
            const title = this.options.widgetDefinitions[widgetId] || 'Widget';
            const contentHTML = this._getWidgetInnerHtml(widgetId, title);
            return { ...item, content: contentHTML };
        }).filter(item => item !== null);

        if (defaultLayoutWithContent.length > 0) {
            this.grid.load(defaultLayoutWithContent);
            console.log("Default layout structure loaded.");
            // Populate content for default widgets using the callback
            if (this.currentData) {
                console.log("Populating content for default widgets...");
                try {
                    this.options.populateContentCallback(this.currentData);
                } catch (e) {
                    console.error("Error during populateContentCallback for defaults:", e);
                     this._displayError("Failed to populate default widget content.");
                }
            } else {
                console.warn("Cannot populate default widgets: missing currentData.");
            }
        } else {
            console.warn("No valid default layout items to render.");
        }
        console.log("Default widget rendering process complete.");
    }

    async _resetLayout() {
        if (!this.grid) return;
        console.log(`Resetting layout for ${this.options.pageIdentifier}`);
        const apiUrl = `/api/v1/layouts/${this.options.pageIdentifier}`;
        try {
            // Attempt to delete saved layout on server
            await apiRequest(apiUrl, { method: 'DELETE' });
            showToast('success', 'Layout reset successfully!');

            // Fetch fresh data if needed for defaults
            console.log("Fetching data required for reset...");
            if (this.options.resetRequiresDataCallback) {
                 this.currentData = await this.options.resetRequiresDataCallback();
                 if (!this.currentData) {
                     console.error("Failed to fetch data needed for reset.");
                     this._displayError("Could not load data needed to reset the layout.");
                     return; // Stop reset if data fetch fails
                 }
            } else {
                 this.currentData = null; // Reset data if no callback provided
            }

            // Render the default layout (which includes populating)
            this._renderDefaultWidgets();

             // Reset lock state to default (locked) and update button
             this._applyInitialLockState(true);
             this._setLockButtonAppearance();
             console.log("Layout reset to default and lock state applied.");

        } catch (error) {
            console.error("Failed to reset layout:", error);
            // apiRequest might have shown a toast, add specific message
            this._displayError("Could not reset layout on the server. Please try again.");
        }
    }

    _applyInitialLockState(isLocked) {
        if (!this.grid) return;
        console.log(`Applying lock state to grid: ${isLocked}`);
        this.grid.enableMove(!isLocked);
        this.grid.enableResize(!isLocked);
        // Ensure Gridstack internal options are updated
        this.grid.opts.disableDrag = isLocked;
        this.grid.opts.disableResize = isLocked;
        console.log(`Grid disableDrag set to: ${this.grid.opts.disableDrag}`);
    }

    _setLockButtonAppearance() {
        if (!this.grid || !this.lockButton) return;
        const icon = this.lockButton.querySelector('i');
        const textSpan = this.lockButton.querySelector('.btn-text'); // Make sure this class exists
        if (!icon || !textSpan) return;

        const isCurrentlyLocked = this.grid.opts.disableDrag;
        console.log(`Updating lock button appearance. Currently locked: ${isCurrentlyLocked}`);

        if (isCurrentlyLocked) {
            icon.classList.remove('bi-unlock-fill');
            icon.classList.add('bi-lock-fill');
            textSpan.textContent = 'Unlock Layout';
            this.lockButton.title = 'Unlock Layout Editing';
        } else {
            icon.classList.remove('bi-lock-fill');
            icon.classList.add('bi-unlock-fill');
            textSpan.textContent = 'Lock Layout';
            this.lockButton.title = 'Lock Layout Editing';
        }
    }

    _toggleLayoutLockAndSave() {
        if (!this.grid || !this.lockButton) return;
        const isCurrentlyLocked = this.grid.opts.disableDrag;
        console.log(`Toggling lock state. Currently locked: ${isCurrentlyLocked}`);

        if (isCurrentlyLocked) { // Unlock it
            this.grid.enableMove(true);
            this.grid.enableResize(true);
            this.grid.opts.disableDrag = false;
            this.grid.opts.disableResize = false;
            showToast('info', 'Layout unlocked for editing.');
        } else { // Lock it
            this.grid.enableMove(false);
            this.grid.enableResize(false);
            this.grid.opts.disableDrag = true;
            this.grid.opts.disableResize = true;
            showToast('info', 'Layout locked.');
        }
        // Update internal state just in case enableMove/Resize don't update opts reliably
        // this.grid.opts.disableDrag = !isCurrentlyLocked;
        // this.grid.opts.disableResize = !isCurrentlyLocked;

        this._setLockButtonAppearance();
        console.log(`Lock state changed to locked: ${this.grid.opts.disableDrag}. Triggering save...`);
        this.debouncedSave(); // Use the debounced save
    }

    _setupEventListeners() {
        if (!this.grid) return;

        // Save Listener on grid changes
        this.grid.on('change', this.debouncedSave);
        console.log("Attached grid 'change' event listener.");

        // Reset Button Listener
        if (this.resetButton) {
            this.resetButton.addEventListener('click', () => {
                if (confirm('Are you sure you want to reset the layout to default? All customizations will be lost.')) {
                    this._resetLayout();
                }
            });
            console.log(`Attached click listener to reset button #${this.options.resetButtonId}.`);
        }

        // Lock Button Listener
        if (this.lockButton) {
            this.lockButton.addEventListener('click', this._toggleLayoutLockAndSave);
            console.log(`Attached click listener to lock button #${this.options.lockButtonId}.`);
        }
    }

    // Applies the loaded state (layout structure and lock status)
    async _applyInitialState(savedData) {
         let initialIsLocked = true; // Default lock state
         let layoutToLoad = this.options.defaultLayout; // Default layout structure

         if (savedData) {
             console.log("Applying saved state:", savedData);
             // Determine lock state from saved data
             if (typeof savedData.is_locked === 'boolean') {
                 initialIsLocked = savedData.is_locked;
             } else {
                 console.warn("Saved data found, but 'is_locked' property missing or invalid. Defaulting to locked.");
             }
             // Use saved layout structure if valid
             if (Array.isArray(savedData.layout)) {
                 layoutToLoad = savedData.layout;
             } else {
                 console.warn("Saved data found, but 'layout' array missing or invalid. Using default layout structure.");
             }
         } else {
            console.log("No saved data found. Using default layout and lock state.");
         }

         console.log(`Determined initial lock state: ${initialIsLocked}`);
         this._applyInitialLockState(initialIsLocked);

         // Prepare layout items with content structure
         const layoutWithContent = layoutToLoad.map(item => {
             const widgetId = item?.id;
             if (!widgetId) {
                  console.warn("Skipping layout item with missing ID:", item);
                  return null;
             }
             const title = this.options.widgetDefinitions[widgetId] || 'Widget';
             const contentHTML = this._getWidgetInnerHtml(widgetId, title);
             // Combine original layout properties (x,y,w,h...) with generated content
             return { ...item, content: contentHTML };
         }).filter(item => item !== null);

         if (layoutWithContent.length > 0) {
             console.log(`Loading grid with ${savedData ? 'saved' : 'default'} layout structure (${layoutWithContent.length} items)...`);
             this.grid.load(layoutWithContent);
             console.log("Grid structure loaded. Populating content...");
              // Populate content using the callback AFTER loading structure
             if (this.currentData) {
                  try {
                       this.options.populateContentCallback(this.currentData);
                       console.log("Content population callback finished.");
                  } catch (e) {
                       console.error("Error during populateContentCallback:", e);
                       this._displayError("Failed to populate widget content.");
                  }
             } else {
                 console.warn("Cannot populate widgets: missing currentData (was initialize called with data?).");
                 // If resetRequiresDataCallback exists, maybe call it here? Or rely on initialize providing it.
             }
         } else {
            console.warn("No valid layout items to load into the grid.");
            // Ensure grid is empty if no layout is loaded
            this.grid.removeAll();
         }
    }

     // Helper to display errors consistently
     _displayError(message) {
        console.error("GridManager Error:", message);
        const errorContainer = document.getElementById('grid-manager-error-container') || document.getElementById('designer-error-container'); // Fallback for designer page
        if (errorContainer) {
            errorContainer.innerHTML = `<div class="alert alert-danger">${message}</div>`;
            errorContainer.style.display = 'block';
        } else {
            showToast('error', message); // Use toast as ultimate fallback
        }
    }
}
