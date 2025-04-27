/**
 * stateMonitor.js: Main class for the State Monitoring Dashboard.
 * Orchestrates UI, events, API calls, and rendering based on the original monolithic script.
 */
import stateBridge from '/static/js/core/state-bridge/bridgeMain.js';

// Import functions from separated modules
import { initElements, setStatus, initializeToggles } from './stateMonitorUi.js';
import { setupEventListeners } from './stateMonitorEvents.js';
import { loadAvailableCollectors, captureSnapshot, downloadSnapshot, copySnapshot, loadRecentSnapshots } from './stateMonitorApi.js';
// Rendering functions are called by the API module in this direct split approach
// import { renderCollectorPanel, renderResults, renderJsonView } from './stateMonitorRenderer.js'; 

class StateMonitorDashboard {
    constructor() {
        // Use async init pattern to allow await
        this._asyncInit();
    }

    async _asyncInit() {
        console.log("[StateMonitorDashboard] _asyncInit started.");

        // --- Instance properties (moved here) ---
        this.collectors = { server: [], browser: [] }; 
        this.currentScope = 'all';
        this.currentSnapshot = null;
        this.refreshInterval = null;
        this.autoRefreshEnabled = false;
        this.autoRefreshIntervalMs = 10000; // 10 seconds

        // --- Initialization using imported functions ---
        this.ui = initElements();
        console.log("[StateMonitorDashboard] UI elements initialized.");
        initializeToggles();
        console.log("[StateMonitorDashboard] Toggles initialized.");

        console.log("[StateMonitorDashboard] Waiting for StateBridge.ready()...");
        try {
            await stateBridge.ready(); // Wait for the promise
            console.log("[StateMonitorDashboard] StateBridge.ready() resolved. Proceeding to load collectors."); 
            // Initial load of collectors - MUST be awaited as it's async
            await this.loadAvailableCollectors(); // Call instance method
            console.log("[StateMonitorDashboard] Initial loadAvailableCollectors finished.");
            // Also load recent snapshots
            await this.loadRecentSnapshots(); // Call instance method
            console.log("[StateMonitorDashboard] Initial loadRecentSnapshots finished.");
        } catch (error) {
            console.error("[StateMonitorDashboard] Error during async init (waiting for StateBridge or loading collectors):", error);
            // Use setStatus via the instance's UI cache
            if (this.ui && this.ui.statusDisplay) {
                setStatus(this.ui.statusDisplay, 'Error during initialization.', 'error');
            } else {
                console.error("Cannot set status, ui.statusDisplay not found.");
            }
        }

        setupEventListeners(this);
        console.log("[StateMonitorDashboard] _asyncInit finished."); 
    }
    
    // --- Methods calling the imported API functions --- 
    // These methods exist on the instance so event listeners can call them.
    // They then call the corresponding imported API function, passing the instance.
    
    async loadAvailableCollectors() {
        // This instance method now simply delegates to the imported API function
        await loadAvailableCollectors(this);
    }

    async loadRecentSnapshots(limit = 10) {
        // This instance method delegates to the imported API function
        await loadRecentSnapshots(this, limit);
    }

    async captureSnapshot() {
         // This instance method now simply delegates to the imported API function
        await captureSnapshot(this);
    }
    
    downloadSnapshot() {
        // Delegate to imported function
        downloadSnapshot(this);
    }
    
    copySnapshot() {
        // Delegate to imported function
        copySnapshot(this);
    }

    // --- State Management Logic (Remains in this class, adapted from original) ---
    setScope(scope) {
        this.currentScope = scope;
        
        // Update active button state using the stored UI elements
        [this.ui.scopeAllBtn, this.ui.scopeBotBtn, this.ui.scopeWebBtn].forEach(btn => {
            if (btn) {
                btn.classList.remove('active');
            }
        });
        switch (scope) {
            case 'all': if (this.ui.scopeAllBtn) this.ui.scopeAllBtn.classList.add('active'); break;
            case 'bot': if (this.ui.scopeBotBtn) this.ui.scopeBotBtn.classList.add('active'); break;
            case 'web': if (this.ui.scopeWebBtn) this.ui.scopeWebBtn.classList.add('active'); break;
        }
        
        // Update displayed collectors by calling the instance method (which delegates to API)
        this.loadAvailableCollectors(); 
    }
    
    toggleAutoRefresh() {
        this.autoRefreshEnabled = !this.autoRefreshEnabled;
        
        if (this.autoRefreshEnabled) {
            // Start auto-refresh - calls instance method (which delegates to API)
            this.refreshInterval = setInterval(() => { this.captureSnapshot(); }, this.autoRefreshIntervalMs);
            
            // Update button appearance
            if (this.ui.autoRefreshBtn) {
                this.ui.autoRefreshBtn.classList.add('active');
                // Original used textContent directly, replicating that
                this.ui.autoRefreshBtn.textContent = 'Stop Auto-Refresh'; 
            }
            // Call imported setStatus function
            setStatus(this.ui.statusDisplay, `Auto-refresh enabled (${this.autoRefreshIntervalMs / 1000}s interval)`);
        } else {
            // Stop auto-refresh
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
                this.refreshInterval = null;
            }
            
            // Update button appearance
            if (this.ui.autoRefreshBtn) {
                this.ui.autoRefreshBtn.classList.remove('active');
                 // Original used textContent directly, replicating that
                this.ui.autoRefreshBtn.textContent = 'Start Auto-Refresh';
            }
            // Call imported setStatus function
            setStatus(this.ui.statusDisplay, 'Auto-refresh disabled');
        }
    }
    
    // Removed methods that are now functions in other modules:
    // - initElements (now imported function)
    // - setStatus (now imported function)
    // - initializeToggles (now imported function)
    // - setupEventListeners (now imported function)
    // - renderCollectorPanel (now imported function in Renderer)
    // - renderResults (now imported function in Renderer)
    // - renderJsonView (now imported function in Renderer)
    // API methods (loadAvailableCollectors, captureSnapshot, downloadSnapshot, copySnapshot) 
    // are now wrappers calling imported API functions.

}

// Initialize the dashboard when the DOM is loaded (from original)
document.addEventListener('DOMContentLoaded', () => {
    window.stateMonitor = new StateMonitorDashboard();
});

// Export the class (from original)
export default StateMonitorDashboard;
