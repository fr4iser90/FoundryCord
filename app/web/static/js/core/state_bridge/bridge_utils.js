// Utility functions for the State Bridge.

/**
 * Sanitize state data to remove potentially sensitive information.
 * @param {*} data - Data to sanitize.
 * @returns {*} - Sanitized data.
 */
export function sanitizeStateData(data) {
    // Simple implementation - could be expanded
    if (data === null || data === undefined) return data;

    if (typeof data === 'object') {
        // Handle DOM elements specifically to avoid large outputs
        if (data instanceof Element) {
            return `<${data.tagName.toLowerCase()} id="${data.id || ''}" class="${data.className || ''}">`;
        }
        // Handle Window object
        if (data === window) {
            return '[Window Object]';
        }
        
        const sanitized = Array.isArray(data) ? [] : {};
        
        for (const [key, value] of Object.entries(data)) {
            // Skip keys that suggest sensitive data
            if (typeof key === 'string' && /password|token|key|secret|auth|credential/i.test(key)) {
                sanitized[key] = '[REDACTED]';
            } else if (typeof value === 'object' && value !== null) {
                // Prevent infinite recursion with circular references (like window)
                if (value === window) {
                     sanitized[key] = '[Window Object]';
                } else {
                     sanitized[key] = sanitizeStateData(value);
                }
            } else {
                sanitized[key] = value;
            }
        }
        
        return sanitized;
    }
    
    // Basic types (string, number, boolean) are returned as is
    // Be cautious about returning large strings directly if needed
    return data;
}

// Add other utility functions here if needed
