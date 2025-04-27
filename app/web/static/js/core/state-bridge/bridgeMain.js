// Main State Bridge class - Coordinates initialization and provides the public API.
import { loadApprovedCollectors } from './bridgeStorage.js';
import { setupGlobalErrorHandlers } from './bridgeErrorHandler.js';
import { wrapConsoleMethods } from './bridgeConsoleWrapper.js';
import { registerCollector as registerCollectorFunc } from './bridgeCollectorsRegistry.js';
import { registerDefaultCollectors as registerDefaultsFunc } from './bridgeCollectorsDefaults.js';
import { collectBrowserState } from './bridgeCollectionLogic.js';
// Note: requestApproval and sanitizeStateData are primarily used internally by collectBrowserState
// and might not need to be public methods on the StateBridge instance itself.

class StateBridge {
    constructor() {
        this.collectors = {};          // Registry for collector functions and options
        this.approvedCollectors = new Set(); // Set of names of approved collectors
        this.pendingApprovals = {};      // Tracks pending approval requests (currently unused)
        this.lastSnapshot = null;        // Stores the last collected browser snapshot
        this.apiEndpoint = '/api/v1/owner/state/snapshot'; // Endpoint to send server snapshot requests
        
        // --- JS Error Tracking --- 
        this._resolveReadyPromise = null;
        this._readyPromise = new Promise(resolve => {
            this._resolveReadyPromise = resolve;
        });
        this.jsErrors = [];
        this.maxJsErrors = 20; 
        // -------------------------
        
        // --- Console Log Tracking ---
        this.consoleLogs = [];
        this.maxConsoleLogs = 50; 
        this.originalConsole = {}; 
        // --------------------------
        
        this.securityToken = null;       // Security token for backend API calls
        
        this._initialize();
    }

    /**
     * Initialize the state bridge: load approvals, setup handlers, register defaults.
     * @private
     */
    async _initialize() {
        console.log('Initializing StateBridge (Modular)');
        let success = false;
        try {
            // Fetch security token
            const response = await fetch('/api/v1/owner/state/token');
            if (response.ok) {
                const data = await response.json();
                this.securityToken = data.token;
                console.log('Security token retrieved.');
            } else {
                console.warn('Failed to get security token.');
            }

            // Load approved collectors from storage
            this.approvedCollectors = loadApprovedCollectors();

            // Setup global error handlers (pass storage array, limit, and snapshot callback)
            setupGlobalErrorHandlers(
                this.jsErrors, 
                this.maxJsErrors, 
                (errorData) => { 
                    console.log('JS error captured, triggering state snapshot...', errorData);
                    // Trigger snapshot collection (fire and forget, but catch potential errors)
                    this.collectState([], { trigger: 'js_error', error: errorData }) // Pass context
                        .catch(snapshotError => console.error('Error capturing state snapshot after JS error:', snapshotError));
                }
            );

            // Wrap console methods (pass storage array, limit, and original storage)
            wrapConsoleMethods(this.consoleLogs, this.maxConsoleLogs, this.originalConsole);

            // Register default browser collectors (pass registry and storages)
            this.registerDefaultCollectors(); 

            success = true; // Mark initialization as successful
        } catch (error) {
            console.error('Error initializing StateBridge:', error);
        } finally {
            // Resolve the ready promise regardless of success/failure, 
            // so code waiting on it doesn't hang indefinitely.
            // Calling resolve multiple times has no effect.
            if (this._resolveReadyPromise) {
                console.log(`[StateBridge] Resolving ready promise (Success: ${success}).`);
                this._resolveReadyPromise();
            } else {
                console.error("[StateBridge] Cannot resolve ready promise - resolve function missing!");
            }
            console.log('[StateBridge] _initialize finished.');
        }
    }

    /**
     * Public getter to access the ready promise.
     * Code can await this promise to ensure StateBridge is initialized.
     * @returns {Promise<void>}
     */
    ready() {
        return this._readyPromise;
    }

    /**
     * Public method to register a new collector.
     */
    registerCollector(name, collectorFn, options = {}) {
        // Uses the imported function, passing the instance's registry
        return registerCollectorFunc(this.collectors, name, collectorFn, options);
    }

    /**
     * Public method to register the default set of browser collectors.
     * This is called by _initialize, but could be called manually if needed.
     */
    registerDefaultCollectors() {
        registerDefaultsFunc(this.collectors, this.jsErrors, this.consoleLogs);
    }

    /**
     * Public method to collect state from specified browser collectors.
     */
    async collectState(collectorNames = [], context = {}) {
        // Uses the imported function, passing necessary instance state
        const snapshot = await collectBrowserState(
            this.collectors, 
            this.approvedCollectors, 
            this.pendingApprovals, 
            collectorNames, 
            context
        );
        this.lastSnapshot = snapshot; // Store the latest snapshot
        return snapshot;
    }

    // Potential future public methods:
    // - Force re-requesting approval
    // - Clearing approvals
    // - Getting specific collector info
    // - Method to send data to backend (if needed directly)
}

// Create and export the global instance
// Ensures only one StateBridge exists
if (!window.stateBridgeInstance) {
    window.stateBridgeInstance = new StateBridge();
}

export default window.stateBridgeInstance;
