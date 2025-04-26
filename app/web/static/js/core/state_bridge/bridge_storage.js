// Handles saving and loading approved collector names to/from localStorage.

const STORAGE_KEY = 'state_bridge_approved';

/**
 * Save the set of approved collectors to localStorage.
 * @param {Set<string>} approvedCollectors - The set of approved collector names.
 */
export function saveApprovedCollectors(approvedCollectors) {
    try {
        localStorage.setItem(STORAGE_KEY, 
            JSON.stringify(Array.from(approvedCollectors)));
    } catch (e) {
        console.warn('Failed to save approved collectors to localStorage:', e);
    }
}

/**
 * Load the set of approved collectors from localStorage.
 * @returns {Set<string>} The set of approved collector names.
 */
export function loadApprovedCollectors() {
    const approvedSet = new Set();
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            const approvedList = JSON.parse(saved);
            if (Array.isArray(approvedList)) { // Ensure it's an array
                approvedList.forEach(name => {
                     if (typeof name === 'string') { // Ensure names are strings
                         approvedSet.add(name);
                     }
                });
            }
            console.log(`Loaded ${approvedSet.size} previously approved collectors`);
        }
    } catch (e) {
        console.warn('Failed to load approved collectors from localStorage:', e);
        // Clear potentially corrupted data
        localStorage.removeItem(STORAGE_KEY);
    }
    return approvedSet;
}
