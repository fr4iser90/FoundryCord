/**
 * Main JavaScript file for the HomeLab Discord Bot web interface
 * Contains common functionality used across multiple pages
 */

// Execute when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('HomeLab Discord Bot web interface loaded');
    initializeComponents();
});

// Initialize Bootstrap components
function initializeComponents() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
}

// Common navigation function
function navigateTo(url) {
    window.location.href = url;
}

// Handle server errors
function handleError(error) {
    console.error('Error:', error);
    alert('An error occurred. Please try again or contact support if the problem persists.');
}
