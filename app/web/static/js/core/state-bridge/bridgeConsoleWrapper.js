// Wraps global console methods to intercept and store log messages.

/**
 * Wraps console methods (log, warn, error, info, debug) to store logs.
 * @param {Array} logStorage - The array where captured logs should be stored.
 * @param {number} maxLogs - The maximum number of logs to store.
 * @param {Object} originalConsoleStorage - An object to store the original console methods.
 */
export function wrapConsoleMethods(logStorage, maxLogs, originalConsoleStorage) {
    const levels = ['log', 'warn', 'error', 'info', 'debug'];
    const storeLog = (level, args) => {
        let message = '';
        try {
            // Attempt to serialize arguments for better logging
            message = args.map(arg => {
                if (typeof arg === 'object' && arg !== null) {
                    // Basic handling for DOM elements to avoid excessive output
                    if (arg instanceof Element) return `<${arg.tagName.toLowerCase()}>`; 
                    try { return JSON.stringify(arg); } catch { /* Fallback below */ }
                }
                // Ensure arg is not undefined or null before calling String()
                return arg !== undefined && arg !== null ? String(arg) : '';
            }).join(' ');
        } catch (e) {
            message = '[StateBridge: Error serializing log arguments]';
        }

        logStorage.unshift({
            level: level,
            timestamp: new Date().toISOString(),
            message: message
        });
        if (logStorage.length > maxLogs) {
            logStorage.pop();
        }
    };

    levels.forEach(level => {
        if (typeof console[level] === 'function') {
            originalConsoleStorage[level] = console[level].bind(console);
            console[level] = (...args) => {
                // Store the log
                storeLog(level, args);
                // Call the original console method
                originalConsoleStorage[level](...args);
            };
        } else {
             // Fallback for browsers that might not have all levels
             originalConsoleStorage[level] = () => {}; // Assign empty function
             // Still wrap it to store log if called directly
             console[level] = (...args) => storeLog(level, args);
        }
    });
    console.info("StateBridge console methods wrapped.");
}
