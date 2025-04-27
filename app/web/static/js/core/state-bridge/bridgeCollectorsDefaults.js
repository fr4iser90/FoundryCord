// Defines and registers the default set of browser-side state collectors.
import { registerCollector } from './bridgeCollectorsRegistry.js';

/**
 * Registers the default browser state collectors.
 * @param {Object} collectorsRegistry - The registry object (e.g., this.collectors).
 * @param {Array} jsErrorStorage - Array to store JS errors.
 * @param {Array} consoleLogStorage - Array to store console logs.
 */
export function registerDefaultCollectors(collectorsRegistry, jsErrorStorage, consoleLogStorage) {
    // Current URL and route information
    registerCollector(collectorsRegistry, 'navigation', (context) => {
        return {
            url: window.location.href,
            path: window.location.pathname,
            query: window.location.search,
            hash: window.location.hash
        };
    }, { requiresApproval: false, description: 'Current page navigation information' });
    
    // Browser viewport and device information
    registerCollector(collectorsRegistry, 'viewport', (context) => {
        return {
            width: window.innerWidth,
            height: window.innerHeight,
            devicePixelRatio: window.devicePixelRatio,
            orientation: window.screen.orientation ? window.screen.orientation.type : 'unknown'
        };
    }, { requiresApproval: false, description: 'Viewport dimensions and device information' });
    
    // Feature detection
    registerCollector(collectorsRegistry, 'features', (context) => {
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
    registerCollector(collectorsRegistry, 'domSummary', (context) => {
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
    registerCollector(collectorsRegistry, 'storageKeys', (context) => {
        try {
            return {
                localStorageKeys: '[REDACTED]', // Object.keys(localStorage), // Redacted for safety
                localStorageCount: localStorage.length,
                sessionStorageKeys: '[REDACTED]', // Object.keys(sessionStorage), // Redacted for safety
                sessionStorageCount: sessionStorage.length,
            };
        } catch (e) {
            return { error: e.message };
        }
    }, { 
        requiresApproval: true, 
        description: 'Storage key names (redacted) used by the application' 
    });

    // JavaScript Error Collector
    registerCollector(collectorsRegistry, 'javascriptErrors', (context) => {
        return [...jsErrorStorage]; // Use the passed-in error storage array
    }, {
        requiresApproval: true, 
        description: 'Captures recent JavaScript errors (onerror, unhandledrejection)',
        scope: 'browser'
    });

    // Console Log Collector
    registerCollector(collectorsRegistry, 'consoleLogs', (context) => {
        return [...consoleLogStorage]; // Use the passed-in log storage array
    }, {
        requiresApproval: true, 
        description: 'Captures recent console messages (log, warn, error, info, debug)',
        scope: 'browser'
    });

    // Computed Styles Collector (Requires Approval and context.selector)
    registerCollector(collectorsRegistry, 'computedStyles', {
        name: 'computedStyles',
        description: 'Computed CSS styles for element matching context.selector (defaults to body)',
        requiresApproval: true,
        context: { selector: 'body' }, // Default context
        source: 'browser',
        async collect(context) {
            const selector = context?.selector || 'body'; // Default to 'body' if no selector provided
            try {
                const element = document.querySelector(selector);
                if (!element) {
                    return { error: `Element not found for selector: ${selector}`, styles: null };
                }
                const styles = window.getComputedStyle(element);
                const stylesObj = {};
                for (let i = 0; i < styles.length; i++) {
                    const prop = styles[i];
                    stylesObj[prop] = styles.getPropertyValue(prop);
                }
                return { styles: stylesObj };
            } catch (error) {
                console.error(`Error collecting computed styles for selector "${selector}":`, error);
                return { error: `Error collecting styles for selector ${selector}: ${error.message}`, styles: null };
            }
        }
    });

    console.info("Default browser collectors registered.");
}
