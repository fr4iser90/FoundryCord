// Handles the registration of state collector functions.

/**
 * Register a state collector function.
 * @param {Object} collectorsRegistry - The object where collectors are stored (e.g., this.collectors).
 * @param {string} name - Unique name for the collector.
 * @param {Function} collectorFn - Function that captures state.
 * @param {Object} options - Configuration options for the collector.
 * @returns {boolean} - True if registration was successful, false otherwise.
 */
export function registerCollector(collectorsRegistry, name, collectorFn, options = {}) {
    if (collectorsRegistry[name] && !options.force) {
        console.warn(`Collector "${name}" already registered. Use force: true to override.`);
        return false;
    }
    
    const defaultOptions = {
        requiresApproval: true,
        description: `State collector for ${name}`,
        scope: 'browser', // Default scope
        secure: true,     // Placeholder for potential future security checks
        sanitize: true    // Placeholder for potential future sanitization options
    };
    
    collectorsRegistry[name] = {
        function: collectorFn,
        options: {...defaultOptions, ...options},
        registeredAt: new Date()
    };
    
    console.log(`Registered state collector: ${name}`);
    return true;
}
