/**
 * stateMonitor/index.js: Main entry point for the State Monitor page using GridManager.
 */
import { GridManager } from '/static/js/components/layout/gridManager.js';
import { apiRequest, showToast, formatDateTime } from '/static/js/components/common/notifications.js';

// Import widget initializers
import { initializeCollectorsList } from './panel/collectorsList.js';
import { initializeRecentSnapshotsList } from './panel/recentSnapshotsList.js';
import { initializeSnapshotSummaryPanel } from './widget/snapshotSummaryPanel.js';
import { initializeSnapshotResultsTabs } from './widget/snapshotResultsTabs.js';

// Import StateBridge and storage helper for browser approvals
import stateBridge from '/static/js/core/state-bridge/bridgeMain.js';
import { saveApprovedCollectors } from '/static/js/core/state-bridge/bridgeStorage.js';

// TODO: Import API functions from stateMonitorApi.js
// import { loadAvailableCollectors, captureSnapshot, downloadSnapshot, copySnapshot, loadRecentSnapshots } from './stateMonitorApi.js';

class StateMonitorController {
    constructor() {
        this.gridManager = null;
        this.collectors = { server: [], browser: [] }; // Initial state
        this.recentSnapshots = []; // Initial state
        this.currentSnapshot = null; // Holds the data of the currently loaded snapshot
        this.pageIdentifier = 'state-monitor-owner';
        this.isLoading = false;
        this.currentScope = 'all'; // TODO: Add scope selection UI later

        // Define the widgets that can be added to the grid
        // Key: Unique ID for the widget type
        // Value: Object with title and initializer function name (as string for now)
        this.widgetDefinitions = {
            snapshotSummary: {
                id: 'snapshotSummary',
                title: 'Snapshot Summary',
                initialX: 0, initialY: 0, initialW: 4, initialH: 2,
                content: '<p class="p-2 text-muted small">Loading summary...</p>'
            },
            snapshotResults: {
                id: 'snapshotResults',
                title: 'Snapshot Results',
                initialX: 4, initialY: 0, initialW: 8, initialH: 4,
                content: '<p class="p-2 text-muted small">Load or capture a snapshot to view results.</p>'
            }
        };

        // Define the default layout for Gridstack
        // See Gridstack documentation for options: https://github.com/gridstack/gridstack.js/tree/develop/doc
        this.defaultLayout = [
            // x, y, w, h, id
            { id: 'snapshotSummary', x: 0, y: 0, w: 4, h: 2 },
            { id: 'snapshotResults', x: 4, y: 0, w: 8, h: 4 }
        ];
        
        this._initializeApp();
    }
    
    /**
     * Fetches the initial data (collectors and recent snapshots) needed for the page.
     */
    async _fetchInitialData() {
        this.isLoading = true;
        this.setStatus('Fetching initial data...');
        console.log("[StateMonitorIndex] Fetching initial data...");
        try {
            const [collectorsData, snapshotsData] = await Promise.all([
                apiRequest('/api/v1/owner/state/collectors', 'GET'),
                apiRequest('/api/v1/owner/state/snapshots/list?limit=10', 'GET') // Assuming limit param
            ]);
            
            console.log("[StateMonitorIndex] Initial data received:", { collectorsData, snapshotsData });
            
             // Basic validation
            const collectors = (collectorsData && collectorsData.collectors) ? collectorsData.collectors : { server: [], browser: [] };
            const recentSnapshots = (snapshotsData && Array.isArray(snapshotsData.snapshots)) ? snapshotsData.snapshots : [];
            
            this.isLoading = false;
            this.setStatus('Ready');
            return { collectors, recentSnapshots };
        } catch (error) {
            console.error("[StateMonitorIndex] Failed to fetch initial data:", error);
            showToast('Error fetching initial data. Please check console.', 'error');
            this.setStatus('Error fetching data!', true);
            this.isLoading = false;
            // Return default empty structure on error to prevent breaking GridManager init
            return { collectors: { server: [], browser: [] }, recentSnapshots: [] }; 
        }
    }

    async _initializeApp() {
        console.log("[StateMonitorIndex] Initializing application...");
        this.setStatus('Initializing...');
        
        const initialData = await this._fetchInitialData();
        
        this.collectors = initialData.collectors;
        this.recentSnapshots = initialData.recentSnapshots;
        
        try {
            this.gridManager = new GridManager({
                gridElementId: 'state-monitor-grid',
                pageIdentifier: this.pageIdentifier,
                widgetDefinitions: this.widgetDefinitions,
                defaultLayout: this.defaultLayout,
                // Pass the actual initial data to the callback context
                populateContentCallback: (widgetElement, widgetId, data) => {
                    // This callback now ONLY handles Summary and Results
                    this._populateGridWidgetContent(widgetElement, widgetId, data);
                },
                resetRequiresDataCallback: async () => {
                     console.log("[StateMonitorIndex] Refetching initial data for layout reset...");
                     const refreshedData = await this._fetchInitialData();
                     this.collectors = refreshedData.collectors;
                     this.recentSnapshots = refreshedData.recentSnapshots;
                     // Reset current snapshot when layout resets
                     this.currentSnapshot = null; 
                     this.updateTimestamp(); // Update timestamp display
                     return refreshedData; 
                 }
            });

            // Initialize GridManager - it will call _populateGridWidgetContent internally via callback
            const grid = await this.gridManager.initialize(initialData); 
            console.log("[StateMonitorIndex] GridManager initialized.");
            
            this._setupControlBarListeners();
            this.setStatus('Ready'); // Status set after successful init

        } catch (error) {
            console.error("[StateMonitorIndex] GridManager Initialization failed:", error);
            showToast('Error initializing grid layout. Please check console.', 'error');
            this.setStatus('Layout Initialization Error!', true);
        }
    }
    
    /**
    * Sets the status display message and optionally marks it as an error.
    */
    setStatus(message, isError = false) {
        const statusDisplay = document.getElementById('status-display');
        if (statusDisplay) {
            statusDisplay.textContent = message;
            statusDisplay.classList.toggle('status-error', isError);
            statusDisplay.classList.toggle('status-info', !isError);
        }
    }
    
    /**
     * Updates the timestamp display.
     */
    updateTimestamp(timestampStr = 'No snapshot loaded') {
        const timestampDisplay = document.getElementById('snapshot-timestamp');
        if (timestampDisplay) {
            timestampDisplay.textContent = timestampStr;
        }
    }

    /**
     * Populates all widgets based on the initial data and the current layout.
     * This is called by GridManager after the grid is ready.
     * @param {Map<string, {content: HTMLElement}>} widgetElements - Map of widget IDs to their content elements.
     * @param {object} data - The initial data fetched ({ collectors, recentSnapshots }).
     */
    _populateAllWidgets(widgetElements, data) {
        console.log("[StateMonitorIndex] Populating widgets with elements:", widgetElements);
        widgetElements.forEach((widget, id) => {
            const contentElement = widget.content;
            if (!contentElement) {
                console.error(`[StateMonitorIndex] Content element missing for widget ${id}`);
                return;
            }

            console.log(`[StateMonitorIndex] Initializing widget: ${id}`);
            try {
                switch (id) {
                    case 'collectorsList':
                        initializeCollectorsList(this, data.collectors, contentElement);
                        break;
                    case 'recentSnapshots':
                        initializeRecentSnapshotsList(this, data.recentSnapshots, contentElement);
                        break;
                    case 'snapshotSummary':
                        // Summary depends on currentSnapshot, which is initially null
                        initializeSnapshotSummaryPanel(this, this.currentSnapshot, contentElement);
                        break;
                    case 'snapshotResults':
                        // Results depend on currentSnapshot, which is initially null
                        initializeSnapshotResultsTabs(this, this.currentSnapshot, contentElement);
                        break;
                    default:
                        console.warn(`[StateMonitorIndex] No initializer found for widget ID: ${id}`);
                        contentElement.innerHTML = `<p class="text-warning">Widget type '${id}' not implemented.</p>`;
                }
            } catch (error) {
                console.error(`[StateMonitorIndex] Error initializing widget ${id}:`, error);
                contentElement.innerHTML = `<p class="text-danger">Error loading widget '${id}'. Check console.</p>`;
            }
        });
        console.log("[StateMonitorIndex] Finished populating widgets.");
    }

    /**
     * Updates only the snapshot-related widgets (summary and results) with new data.
     * Called after a snapshot is loaded.
     */
    _updateSnapshotWidgets() {
        if (!this.gridManager) return; // Grid not initialized
        console.log("[StateMonitorIndex] Updating snapshot widgets with data:", this.currentSnapshot);
        
        // Update timestamp display in the header
        this.updateTimestamp(this.currentSnapshot?.timestamp ? new Date(this.currentSnapshot.timestamp).toLocaleString() : 'Snapshot Loaded (No Timestamp)');

        try {
            // Find and update Snapshot Summary widget
            const summaryWidgetElement = this.gridManager.getWidgetContentElementById('snapshotSummary');
            if (summaryWidgetElement) {
                console.log("[StateMonitorIndex] Re-initializing Snapshot Summary.");
                initializeSnapshotSummaryPanel(this, this.currentSnapshot, summaryWidgetElement);
            } else {
                console.warn("[StateMonitorIndex] Snapshot Summary widget not found in current layout.");
            }

            // Find and update Snapshot Results widget
            const resultsWidgetElement = this.gridManager.getWidgetContentElementById('snapshotResults');
            if (resultsWidgetElement) {
                console.log("[StateMonitorIndex] Re-initializing Snapshot Results.");
                initializeSnapshotResultsTabs(this, this.currentSnapshot, resultsWidgetElement);
            } else {
                 console.warn("[StateMonitorIndex] Snapshot Results widget not found in current layout.");
            }
        } catch (error) {
            console.error("[StateMonitorIndex] Error updating snapshot widgets:", error);
            showToast('Error updating snapshot display. See console.', 'error');
        }
    }
    
    /**
     * Sets up listeners for the main control bar buttons.
     */
     _setupControlBarListeners() {
         console.log("[StateMonitorIndex] Setting up control bar listeners...");

         // Panel Toggles
         document.getElementById('toggle-left-panel-btn')?.addEventListener('click', () => {
             const container = document.querySelector('.state-monitor-container.layout-editor');
             const panel = document.querySelector('.editor-panel-left');
             if (container && panel) {
                 container.classList.toggle('left-panel-collapsed'); 
                 panel.classList.toggle('collapsed');
                 if (this.gridManager && this.gridManager.grid) {
                     this.gridManager.grid.onParentResize(); 
                 }
             }
         });
         
         document.getElementById('toggle-right-panel-btn')?.addEventListener('click', () => {
             const container = document.querySelector('.state-monitor-container.layout-editor');
             const panel = document.querySelector('.editor-panel-right');
             if (container && panel) {
                 container.classList.toggle('right-panel-collapsed'); 
                 panel.classList.toggle('collapsed');
                  if (this.gridManager && this.gridManager.grid) {
                      this.gridManager.grid.onParentResize(); 
                  }
             }
         });
         
         // Scope buttons (Existing logic)
         document.querySelectorAll('.btn-group button[id^="scope-"]').forEach(button => {
            button.addEventListener('click', (event) => {
                document.querySelectorAll('.btn-group button[id^="scope-"]').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                const scope = event.target.id.split('-')[1];
                console.log(`Scope changed to: ${scope}`);
                showToast('info', `Scope set to: ${scope}. Filtering not yet implemented.`);
            });
        });
         
         // Action Buttons (Existing logic)
         document.getElementById('capture-snapshot-btn')?.addEventListener('click', () => this.captureSnapshot());
        document.getElementById('refresh-btn')?.addEventListener('click', () => this.refreshData());
        document.getElementById('download-snapshot-btn')?.addEventListener('click', () => this.downloadSnapshot());
        document.getElementById('copy-snapshot-btn')?.addEventListener('click', () => this.copySnapshot());
        document.getElementById('toggle-auto-refresh')?.addEventListener('click', () => {
            showToast('info', 'Auto-refresh toggle not implemented yet.');
        });
        
        // GridStack controls are handled by GridManager internally (lock/reset)
     }

    // --- Placeholder methods for future implementation --- 
    
    async loadSnapshot(snapshotId) {
        if (this.isLoading || !snapshotId) {
             console.warn("[StateMonitorIndex] Load snapshot request ignored (already loading or no ID).");
             return;
         }
        console.log(`[StateMonitorIndex] Loading snapshot: ${snapshotId}`);
        this.isLoading = true;
        this.setStatus(`Loading snapshot ${snapshotId}...`);
        
        try {
            // Use the correct API endpoint
            const responseData = await apiRequest(`/api/v1/owner/state/snapshot/${snapshotId}`, 'GET');

            // Validate response structure (StoredSnapshotResponse)
            if (!responseData || !responseData.snapshot || !responseData.snapshot.results) {
                console.error("[StateMonitorIndex] Invalid snapshot data received from API:", responseData);
                throw new Error("Invalid snapshot data format received from server.");
            }

            // Extract the relevant data to store and display
            // The API returns StoredSnapshotResponse model
            const snapshotData = {
                id: responseData.snapshot_id,
                timestamp: responseData.capture_timestamp ? responseData.capture_timestamp * 1000 : Date.now(), // Convert sec to ms
                metadata: responseData.trigger_context || { source: 'Loaded Snapshot' },
                server: responseData.snapshot.results?.server || { info: "No server data" },
                browser: responseData.snapshot.results?.browser || { info: "No browser data" }
            };

            this.currentSnapshot = snapshotData;
            this._updateSnapshotWidgets(); // Update relevant widgets
            this.setStatus('Snapshot loaded successfully.');
            
        } catch (error) {
            console.error(`[StateMonitorIndex] Failed to load snapshot ${snapshotId}:`, error);
            // apiRequest should show a toast, but add context here
            showToast(`Failed to load snapshot ${snapshotId}. Check console.`, 'error');
            this.setStatus(`Error loading snapshot ${snapshotId}!`, true);
            this.currentSnapshot = null; // Clear snapshot on error
            this._updateSnapshotWidgets(); // Update widgets to show empty state
        } finally {
            this.isLoading = false;
        }
    }
    
    /**
     * Handles clicks on collector approval checkboxes.
     * @param {Event} event - The checkbox change event.
     */
    async handleCollectorApprovalChange(event) { // Make async for API call
        const checkbox = event.target;
        const collectorName = checkbox.dataset.name;
        const collectorSource = checkbox.dataset.source;
        const isApproved = checkbox.checked;
        const originalCheckedState = !isApproved; // State before the click

        console.log(`[StateMonitorIndex] Approval change requested for ${collectorSource} collector '${collectorName}'. New state: ${isApproved}`);

        // Disable checkbox temporarily to prevent rapid clicking
        checkbox.disabled = true;
        this.setStatus(`Updating approval for ${collectorName}...`);

        try {
            if (collectorSource === 'server') {
                // --- Server Collector Approval --- 
                // The current backend endpoint toggles approval based on the call itself,
                // rather than taking an approve/disapprove flag. This might need adjustment.
                // For now, we just call the endpoint which *should* handle the toggle.
                // TODO: Verify backend `/approve` logic. Does it toggle or require state?
                // Assuming it handles the toggle for now.
                
                // Find the collector details to see if it actually requires approval
                 const serverCollector = this.collectors.server.find(c => c.name === collectorName);
                 if (!serverCollector) throw new Error("Server collector details not found.");
                 
                 if (!serverCollector.requires_approval) {
                     console.warn(`Server collector ${collectorName} does not require approval.`);
                     // Maybe re-enable checkbox and return? Or proceed if API handles it?
                     // Let's assume API handles it gracefully for now.
                 }
                 
                 console.log(`Calling server approval endpoint for ${collectorName}...`);
                 await apiRequest('/api/v1/owner/state/approve', {
                    method: 'POST',
                    body: JSON.stringify({ collector_name: collectorName })
                });
                showToast('success', `Server collector '${collectorName}' approval updated.`);
                // TODO: Optionally refresh the collectors list from API to ensure UI consistency?
                // For now, assume the checkbox state is correct.
                
            } else if (collectorSource === 'browser') {
                // --- Browser Collector Approval --- 
                await stateBridge.ready(); // Ensure StateBridge is initialized
                
                // Find the collector details to see if it requires approval
                const browserCollector = this.collectors.browser.find(c => c.name === collectorName);
                 if (!browserCollector) throw new Error("Browser collector details not found.");
                 
                 if (!browserCollector.requires_approval) {
                     console.warn(`Browser collector ${collectorName} does not require approval.`);
                     // Silently succeed as no action is needed
                 } else {
                     // Directly update the approved set in StateBridge
                     if (isApproved) {
                         stateBridge.approvedCollectors.add(collectorName);
                         console.log(`Browser collector '${collectorName}' added to approved set.`);
                     } else {
                         // Confirmation before removing approval?
                         // if (!confirm(`Are you sure you want to revoke approval for the browser collector '${collectorName}'?`)) {
                         //     checkbox.checked = true; // Revert UI
                         //     throw new Error("User cancelled disapproval.");
                         // }
                         stateBridge.approvedCollectors.delete(collectorName);
                         console.log(`Browser collector '${collectorName}' removed from approved set.`);
                     }
                     // Save the updated set to localStorage
                     saveApprovedCollectors(stateBridge.approvedCollectors);
                     showToast('success', `Browser collector '${collectorName}' approval updated.`);
                 }

            } else {
                throw new Error(`Unknown collector source: ${collectorSource}`);
            }

        } catch (error) {
            console.error(`Failed to update approval for ${collectorName} (${collectorSource}):`, error);
            showToast('error', `Failed to update approval for '${collectorName}'. Check console.`);
            // Revert checkbox state on error
            checkbox.checked = originalCheckedState;
        } finally {
            // Re-enable checkbox and reset status
            checkbox.disabled = false;
            this.setStatus('Ready');
        }
    }

    // TODO: Add methods for captureSnapshot, refreshData, downloadSnapshot, copySnapshot, 
    // handleCollectorApprovalChange, setScope, toggleAutoRefresh etc.
    // These methods will interact with the API module (stateMonitorApi.js) OR direct apiRequest 
    // and update state (this.collectors, this.recentSnapshots, this.currentSnapshot)
    // and call _populateAllWidgets or _updateSnapshotWidgets as needed.

    // --- Control Bar Action Methods --- 

    async captureSnapshot() {
        if (this.isLoading) {
            showToast('warning', 'Operation already in progress.');
            return;
        }
        console.log("[StateMonitorIndex] Capturing snapshot...");
        this.isLoading = true;
        this.setStatus('Capturing state snapshot...');

        try {
            // 1. Get selected collectors from the UI
            // We need to look inside the collectorsList widget content
            const collectorsWidget = this.gridManager?.getWidgetContentElementById('collectorsList');
            if (!collectorsWidget) throw new Error("Collectors list widget not found.");
            
            const serverCollectors = Array.from(collectorsWidget.querySelectorAll('input[data-source="server"]:checked'))
                .map(checkbox => checkbox.dataset.name);
            const browserCollectors = Array.from(collectorsWidget.querySelectorAll('input[data-source="browser"]:checked'))
                .map(checkbox => checkbox.dataset.name);
                
            console.log("Selected Server Collectors:", serverCollectors);
            console.log("Selected Browser Collectors:", browserCollectors);

            // 2. Collect browser state FIRST using StateBridge
            await stateBridge.ready(); 
            const baseContext = { trigger: 'user_capture' };
            const browserSnapshot = await stateBridge.collectState(browserCollectors, baseContext);
            console.log("Browser snapshot collected:", browserSnapshot);
            
            // 3. Call server snapshot endpoint, passing browser state in context
            const serverSnapshotRequest = { 
                collectors: serverCollectors,
                context: {
                    browser_snapshot: browserSnapshot,
                    source: 'state-monitor-dashboard'
                 } 
            };
            
            // Use the correct endpoint
            const serverResponse = await apiRequest('/api/v1/owner/state/snapshot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add security token if StateBridge has it (though backend might not use it for server->server calls)
                    // 'X-State-Security-Token': stateBridge.securityToken || '' 
                },
                body: JSON.stringify(serverSnapshotRequest)
            });
             console.log("Server snapshot response:", serverResponse);

            // 4. Combine results and update UI
            this.currentSnapshot = {
                id: serverResponse.snapshot_id || `temp-${Date.now()}`, // Use ID from response if available
                timestamp: serverResponse.timestamp ? serverResponse.timestamp * 1000 : Date.now(), // Server likely sends float timestamp
                metadata: serverSnapshotRequest.context, // Use the request context
                server: serverResponse.results || { info: "No server data" }, // Data is likely in response.results
                browser: browserSnapshot.results || { info: "No browser data" } // Data is in browserSnapshot.results
            };

            this._updateSnapshotWidgets(); // Update summary & results
            this.setStatus('Snapshot captured successfully.');

            // 5. Refresh recent snapshots list (optional, could be heavy)
            // TODO: Implement refreshRecentSnapshots method or integrate into _fetchInitialData?
            // For now, just log
             console.log("TODO: Refresh recent snapshots list after capture.");

        } catch (error) {
            console.error("[StateMonitorIndex] Failed to capture snapshot:", error);
            showToast('error', `Snapshot capture failed. See console.`);
            this.setStatus('Snapshot capture failed!', true);
            // Optionally clear currentSnapshot?
            // this.currentSnapshot = null;
            // this._updateSnapshotWidgets(); 
        } finally {
            this.isLoading = false;
        }
    }

    async refreshData() {
        if (this.isLoading) {
            showToast('warning', 'Operation already in progress.');
            return;
        }
        console.log("[StateMonitorIndex] Refreshing data...");
        this.isLoading = true; // Prevent overlap
        this.setStatus('Refreshing data...');

        try {
            const refreshedData = await this._fetchInitialData();
            
            // Update controller state
            this.collectors = refreshedData.collectors;
            this.recentSnapshots = refreshedData.recentSnapshots;
            
            // Re-populate relevant widgets (Collectors, Recent Snapshots)
            const collectorsWidget = this.gridManager?.getWidgetContentElementById('collectorsList');
            if (collectorsWidget) initializeCollectorsList(this, this.collectors, collectorsWidget);
            
            const recentSnapshotsWidget = this.gridManager?.getWidgetContentElementById('recentSnapshots');
            if (recentSnapshotsWidget) initializeRecentSnapshotsList(this, this.recentSnapshots, recentSnapshotsWidget);
            
            this.setStatus('Data refreshed.');
        } catch (error) {
            console.error("[StateMonitorIndex] Failed to refresh data:", error);
            // Error handled/shown by _fetchInitialData
            this.setStatus('Failed to refresh data!', true);
        } finally {
            this.isLoading = false;
        }
    }

    downloadSnapshot() {
        console.log("[StateMonitorIndex] Download snapshot requested.");
        if (!this.currentSnapshot) {
            showToast('warning', 'No snapshot loaded to download.');
            return;
        }

        try {
            const json = JSON.stringify(this.currentSnapshot, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const timestamp = new Date(this.currentSnapshot.timestamp || Date.now()).toISOString().replace(/[:.]/g, '-');
            const filename = `state-snapshot-${this.currentSnapshot.id || timestamp}.json`;
            
            // Create temporary link and click it
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href); // Clean up blob URL

            showToast('success', 'Snapshot download started.');
        } catch (error) {
            console.error("[StateMonitorIndex] Failed to prepare snapshot for download:", error);
            showToast('error', 'Could not prepare snapshot for download. See console.');
        }
    }

    async copySnapshot() {
        console.log("[StateMonitorIndex] Copy snapshot requested.");
         if (!this.currentSnapshot) {
            showToast('warning', 'No snapshot loaded to copy.');
            return;
        }

        try {
            const jsonString = JSON.stringify(this.currentSnapshot, null, 2);
            await navigator.clipboard.writeText(jsonString);
            showToast('success', 'Snapshot JSON copied to clipboard!');
        } catch (err) {
            console.error('[StateMonitorIndex] Failed to copy snapshot JSON:', err);
            showToast('error', 'Failed to copy snapshot JSON. See console.');
        }
    }

    // UPDATED: Populate static panels targeting the new content area IDs
    _populateStaticPanels(data) {
        if (!data) {
            console.warn("[StateMonitorIndex] Cannot populate static panels, data is missing.");
            return;
        }
        
        // Populate Collectors List (Left Panel)
        const collectorsContainer = document.getElementById('collectors-list-container');
        if (collectorsContainer) {
            // Target the specific content area div by its new ID
            const collectorsContent = document.getElementById('collectors-list-content-area'); 
            if (collectorsContent) {
                initializeCollectorsList(data.collectorsData || [], collectorsContent, this);
            } else {
                console.error("Could not find content area #collectors-list-content-area");
            }
        } else {
            console.error("Could not find container #collectors-list-container for Left Panel");
        }
        
        // Populate Recent Snapshots List (Right Panel)
        const snapshotsContainer = document.getElementById('recent-snapshots-container');
        if (snapshotsContainer) {
             // Target the specific content area div by its new ID
             const snapshotsContent = document.getElementById('recent-snapshots-content-area');
            if (snapshotsContent) {
                initializeRecentSnapshotsList(data.snapshotsData || [], snapshotsContent, this);
            } else {
                console.error("Could not find content area #recent-snapshots-content-area");
            }
        } else {
            console.error("Could not find container #recent-snapshots-container for Right Panel");
        }
    }
    
    // UPDATED: Renamed and now only handles widgets *within* the grid via GridManager's callback
    _populateGridWidgetContent(widgetElement, widgetId, data) {
        if (!widgetElement || !widgetId || !data) {
            console.warn("[StateMonitorIndex] Cannot populate grid widget, missing element, ID, or data.");
            return; 
        }

        // console.log(`[StateMonitorIndex] Populating grid widget: ${widgetId}`);
        const contentElement = widgetElement.querySelector('.widget-content');
        if (!contentElement) {
            console.error(`[StateMonitorIndex] Could not find .widget-content for widget ${widgetId}`);
            widgetElement.innerHTML = '<p class="p-2 text-danger small">Error: Content area not found.</p>';
            return;
        }

        switch (widgetId) {
            case 'snapshotSummary':
                initializeSnapshotSummaryPanel(this.currentSnapshot, contentElement);
                break;
            case 'snapshotResults':
                initializeSnapshotResultsTabs(this.currentSnapshot, contentElement);
                break;
            default:
                console.warn(`[StateMonitorIndex] Unknown widget ID for grid population: ${widgetId}`);
                contentElement.innerHTML = `<p class="p-2 text-muted small">Widget content for '${widgetId}' not implemented.</p>`;
        }
    }
}

// Initialize the controller when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.stateMonitorController = new StateMonitorController();
}); 