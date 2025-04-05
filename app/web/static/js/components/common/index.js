/**
 * Index page JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Index page loaded');
    
    // Add any index page specific JavaScript here
    
    // Example: Initialize dashboard cards to have equal height
    const cards = document.querySelectorAll('.card');
    let maxHeight = 0;
    
    cards.forEach(card => {
        const height = card.offsetHeight;
        if (height > maxHeight) {
            maxHeight = height;
        }
    });
    
    cards.forEach(card => {
        card.style.height = `${maxHeight}px`;
    });
});
