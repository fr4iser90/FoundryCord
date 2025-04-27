/**
 * dateTimeUtils.js: Utility functions for date and time formatting.
 */

// Date/Time Utilities
const formatDateTime = (date) => {
    // Handle potential invalid date input before creating Date object
    if (!date || isNaN(new Date(date).getTime())) {
        console.warn("[formatDateTime] Invalid date input:", date);
        return 'Invalid Date';
    }

    try {
        return new Date(date).toLocaleString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (e) {
        console.error("[formatDateTime] Error formatting date:", date, e);
        return 'Invalid Date';
    }
};

export {
    formatDateTime
}; 