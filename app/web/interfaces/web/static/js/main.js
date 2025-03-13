/**
 * Main JavaScript file for the HomeLab Discord Bot web interface
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('HomeLab Discord Bot web interface loaded');
    
    // Check if the user is logged in
    const userElement = document.getElementById('user-info');
    if (userElement) {
        console.log('User is logged in');
    } else {
        console.log('User is not logged in');
    }
    
    // Initialize any components that need initialization
    initializeComponents();
});

function initializeComponents() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Add other component initializations here
} 