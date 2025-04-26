/**
 * State Bridge - Secure state collection and sharing with backend
 * Allows capturing targeted browser state with user approval
 */

class StateBridge {
    constructor() {
        this.collectors = {};
        this.approvedCollectors = new Set();
        this.pendingApprovals = {};
        this.lastSnapshot = null;
        this.apiEndpoint = '/api/v1/state/snapshot';
        
        // Security token for API requests
        this.securityToken = null;
        
        // Initialize on creation
        this._initialize();
    }
    
    /**
     * Initialize the state bridge
     * @private
     */
    async _initialize() {
        console.log('Initializing StateBridge');
        
        try {
            // Fetch security token from session
            const response = await fetch('/api/v1/auth/state-token');
            if (response.ok) {
                const data = await response.json();
                this.securityToken = data.token;
                console.log('Security token retrieved for state bridge');
            } else {
                console.warn('Failed to get security token for state bridge');
            }
            
            // Register default collectors
            this._registerDefaultCollectors();
            
            // Load pre-approved collectors from localStorage
            this._loadApprovedCollectors();
        } catch (error) {
            console.error('Error initializing StateBridge:', error);
        }
    }
    
    /**
     * Register a state collector function
     * @param {string} name - Unique name for the collector
     * @param {Function} collectorFn - Function that captures state
     * @param {Object} options - Configuration options
     */
    registerCollector(name, collectorFn, options = {}) {
        if (this.collectors[name] && !options.force) {
            console.warn(`Collector "${name}" already registered. Use force: true to override.`);
            return false;
        }
        
        const defaultOptions = {
            requiresApproval: true,
            description: `State collector for ${name}`,
            scope: 'browser',
            secure: true,
            sanitize: true
        };
        
        this.collectors[name] = {
            function: collectorFn,
            options: {...defaultOptions, ...options},
            registeredAt: new Date()
        };
        
        console.log(`Registered state collector: ${name}`);
        return true;
    }
    
    /**
     * Request user approval for a collector
     * @param {string} name - Name of the collector
     * @returns {Promise<boolean>} - Whether approval was granted
     */
    async requestApproval(name) {
        if (!this.collectors[name]) {
            console.warn(`Cannot request approval for unknown collector: ${name}`);
            return false;
        }
        
        const collector = this.collectors[name];
        
        if (!collector.options.requiresApproval) {
            return true; // No approval needed
        }
        
        if (this.approvedCollectors.has(name)) {
            return true; // Already approved
        }
        
        // Check if we're in a pending state
        if (this.pendingApprovals[name]) {
            if (Date.now() - this.pendingApprovals[name].requestedAt < 30000) {
                return false; // Still waiting for approval (30 sec timeout)
            }
        }
        
        // Mark as pending
        this.pendingApprovals[name] = {
            requestedAt: Date.now(),
            status: 'pending'
        };
        
        // Show approval dialog to user
        const approved = await this._showApprovalDialog(name, collector.options.description);
        
        if (approved) {
            this.approvedCollectors.add(name);
            this._saveApprovedCollectors();
            
            // Update pending status
            this.pendingApprovals[name] = {
                requestedAt: Date.now(),
                status: 'approved'
            };
            
            return true;
        } else {
            // Update pending status
            this.pendingApprovals[name] = {
                requestedAt: Date.now(),
                status: 'rejected'
            };
            
            return false;
        }
    }
    
    /**
     * Collect state from specified collectors
     * @param {Array<string>} collectorNames - Collector names to execute
     * @param {Object} context - Optional context data
     * @returns {Promise<Object>} - Collected state data
     */
    async collectState(collectorNames = [], context = {}) {
        const results = {};
        const timestamp = Date.now();
        
        // If no collectors specified, use all registered ones
        const collectorsToRun = collectorNames.length > 0 
            ? collectorNames 
            : Object.keys(this.collectors);
            
        for (const name of collectorsToRun) {
            if (!this.collectors[name]) {
                console.warn(`Unknown state collector: ${name}`);
                continue;
            }
            
            const collector = this.collectors[name];
            
            // Check approval status
            if (collector.options.requiresApproval && !this.approvedCollectors.has(name)) {
                const approved = await this.requestApproval(name);
                if (!approved) {
                    results[name] = { error: 'not_approved', requiresApproval: true };
                    continue;
                }
            }
            
            try {
                const collectorFn = collector.function;
                const result = await Promise.resolve(collectorFn(context));
                
                // Sanitize result if needed
                const processedResult = collector.options.sanitize 
                    ? this._sanitizeStateData(result)
                    : result;
                    
                results[name] = processedResult;
                console.debug(`Successfully collected state with: ${name}`);
            } catch (error) {
                console.error(`Error executing state collector ${name}:`, error);
                results[name] = { error: error.message || 'Unknown error' };
            }
        }
        
        const snapshot = {
            timestamp,
            results
        };
        
        this.lastSnapshot = snapshot;
        return snapshot;
    }
    
    /**
     * Send collected state to the backend
     * @param {Object} stateData - State data to send (or use last snapshot)
     * @returns {Promise<Object>} - API response
     */
    async sendStateToBackend(stateData = null) {
        const dataToSend = stateData || this.lastSnapshot;
        
        if (!dataToSend) {
            console.error('No state data to send to backend');
            return { error: 'no_data', success: false };
        }
        
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-State-Security-Token': this.securityToken || ''
                },
                body: JSON.stringify(dataToSend)
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error sending state to backend:', error);
            return { error: error.message, success: false };
        }
    }
    
    /**
     * Register default state collectors
     * @private
     */
    _registerDefaultCollectors() {
        // Current URL and route information
        this.registerCollector('navigation', (context) => {
            return {
                url: window.location.href,
                path: window.location.pathname,
                query: window.location.search,
                hash: window.location.hash
            };
        }, { requiresApproval: false, description: 'Current page navigation information' });
        
        // Browser viewport and device information
        this.registerCollector('viewport', (context) => {
            return {
                width: window.innerWidth,
                height: window.innerHeight,
                devicePixelRatio: window.devicePixelRatio,
                orientation: window.screen.orientation ? window.screen.orientation.type : 'unknown'
            };
        }, { requiresApproval: false, description: 'Viewport dimensions and device information' });
        
        // Feature detection
        this.registerCollector('features', (context) => {
            return {
                localStorage: !!window.localStorage,
                sessionStorage: !!window.sessionStorage,
                webSockets: !!window.WebSocket,
                webWorkers: !!window.Worker,
                geolocation: !!navigator.geolocation,
                serviceWorker: !!navigator.serviceWorker
            };
        }, { requiresApproval: false, description: 'Browser feature detection' });
        
        // DOM structure summary (safe version)
        this.registerCollector('domSummary', (context) => {
            // Only count elements, don't include content
            const counts = {};
            document.querySelectorAll('*').forEach(el => {
                const tag = el.tagName.toLowerCase();
                counts[tag] = (counts[tag] || 0) + 1;
            });
            
            return {
                title: document.title,
                elementCounts: counts,
                totalElements: document.querySelectorAll('*').length,
                bodyClasses: Array.from(document.body.classList)
            };
        }, { 
            requiresApproval: true, 
            description: 'Summary of page structure (element counts, no content)' 
        });
        
        // LocalStorage keys (but not values)
        this.registerCollector('storageKeys', (context) => {
            try {
                return {
                    localStorageKeys: Object.keys(localStorage),
                    localStorageCount: localStorage.length,
                    sessionStorageKeys: Object.keys(sessionStorage),
                    sessionStorageCount: sessionStorage.length,
                };
            } catch (e) {
                return { error: e.message };
            }
        }, { 
            requiresApproval: true, 
            description: 'Storage key names (not values) used by the application' 
        });
    }
    
    /**
     * Display an approval dialog to the user
     * @param {string} collectorName - Name of the collector
     * @param {string} description - Description of what will be collected
     * @returns {Promise<boolean>} - Whether approval was granted
     * @private
     */
    async _showApprovalDialog(collectorName, description) {
        return new Promise(resolve => {
            // Check if we have a custom modal component
            if (window.UIComponents && window.UIComponents.showConfirmModal) {
                window.UIComponents.showConfirmModal({
                    title: 'Allow State Collection',
                    message: `The application is requesting permission to collect state information: ${description}`,
                    confirmText: 'Approve',
                    cancelText: 'Deny',
                    onConfirm: () => resolve(true),
                    onCancel: () => resolve(false)
                });
                return;
            }
            
            // Fallback to browser confirm
            const approved = window.confirm(
                `The application is requesting permission to collect the following state information:\n\n` +
                `${description}\n\n` +
                `Do you approve?`
            );
            
            resolve(approved);
        });
    }
    
    /**
     * Sanitize state data to remove sensitive information
     * @param {*} data - Data to sanitize
     * @returns {*} - Sanitized data
     * @private
     */
    _sanitizeStateData(data) {
        // Simple implementation - could be expanded
        if (!data) return data;
        
        if (typeof data === 'object') {
            const sanitized = Array.isArray(data) ? [] : {};
            
            for (const [key, value] of Object.entries(data)) {
                // Skip keys that suggest sensitive data
                if (/password|token|key|secret|auth|credential/i.test(key)) {
                    sanitized[key] = '[REDACTED]';
                } else if (typeof value === 'object' && value !== null) {
                    sanitized[key] = this._sanitizeStateData(value);
                } else {
                    sanitized[key] = value;
                }
            }
            
            return sanitized;
        }
        
        return data;
    }
    
    /**
     * Save approved collectors to localStorage
     * @private
     */
    _saveApprovedCollectors() {
        try {
            localStorage.setItem('state_bridge_approved', 
                JSON.stringify(Array.from(this.approvedCollectors)));
        } catch (e) {
            console.warn('Failed to save approved collectors to localStorage:', e);
        }
    }
    
    /**
     * Load approved collectors from localStorage
     * @private
     */
    _loadApprovedCollectors() {
        try {
            const saved = localStorage.getItem('state_bridge_approved');
            if (saved) {
                const approvedList = JSON.parse(saved);
                approvedList.forEach(name => {
                    this.approvedCollectors.add(name);
                });
                console.log(`Loaded ${this.approvedCollectors.size} previously approved collectors`);
            }
        } catch (e) {
            console.warn('Failed to load approved collectors from localStorage:', e);
        }
    }
}

// Create global instance
window.stateBridge = window.stateBridge || new StateBridge();

export default window.stateBridge; 