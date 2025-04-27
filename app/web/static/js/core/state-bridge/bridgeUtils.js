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

/**
 * Collects computed CSS styles for a selected element.
 * @param {string} selector - The CSS selector for the target element.
 * @returns {Promise<{error: string|null, styles: object|null}>} - Object containing styles or error.
 */
export async function getComputedStylesForElement(selector) {
    if (!selector || typeof selector !== 'string') {
        console.warn('[StateBridge Util] getComputedStylesForElement: Invalid or missing selector.');
        return { error: 'Invalid or missing selector argument', styles: null };
    }

    const element = document.querySelector(selector);
    if (!element) {
        console.warn(`[StateBridge Util] getComputedStylesForElement: Element not found for selector: ${selector}`);
        return { error: `Element not found for selector: ${selector}`, styles: null };
    }

    try {
        const computedStyles = window.getComputedStyle(element);
        const stylesObject = {};
        // Iterate over all CSS properties
        // Using a simple loop as computedStyles is a CSSStyleDeclaration, not a plain object/array
        for (let i = 0; i < computedStyles.length; i++) {
            const propName = computedStyles[i];
            stylesObject[propName] = computedStyles.getPropertyValue(propName);
        }
        console.log(`[StateBridge Util] getComputedStylesForElement: Collected ${Object.keys(stylesObject).length} styles for ${selector}.`);
        return { error: null, styles: stylesObject }; // Return styles directly
    } catch (error) {
        console.error(`[StateBridge Util] getComputedStylesForElement: Error getting styles for ${selector}:`, error);
        return { error: `Error getting computed styles: ${error.message}`, styles: null };
    }
}
