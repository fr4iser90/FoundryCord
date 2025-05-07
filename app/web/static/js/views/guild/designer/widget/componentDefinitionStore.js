// componentDefinitionStore.js
// Utility for fetching and accessing dashboard component definitions

import { apiRequest } from '/static/js/components/common/notifications.js';

// Internal cache for component definitions
let _definitions = null;
let _fetchPromise = null;

/**
 * Fetches all component definitions from the API (if not already loaded).
 * Returns a promise that resolves to the definitions array.
 */
export async function fetchComponentDefinitions() {
    if (_definitions) return _definitions;
    if (_fetchPromise) return _fetchPromise;
    _fetchPromise = apiRequest('/api/v1/dashboards/components', { method: 'GET' })
        .then(response => {
            _definitions = Array.isArray(response.components) ? response.components : [];
            return _definitions;
        })
        .catch(err => {
            _definitions = [];
            throw err;
        });
    return _fetchPromise;
}

/**
 * Gets a specific component definition by dashboardType and componentKey.
 * Returns the definition object or undefined if not found.
 */
export function getDefinition(dashboardType, componentKey) {
    if (!_definitions) return undefined;
    // Some components may be global (no dashboardType), so try both
    return _definitions.find(def =>
        def.component_key === componentKey &&
        (def.dashboard_type === dashboardType || !def.dashboard_type)
    );
}

/**
 * Clears the cached definitions (for testing or reload scenarios).
 */
export function clearComponentDefinitionsCache() {
    _definitions = null;
    _fetchPromise = null;
} 