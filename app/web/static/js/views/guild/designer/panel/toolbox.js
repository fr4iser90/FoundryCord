/**
 * toolbox.js
 * 
 * Handles the logic for the Toolbox Panel in the Guild Structure Designer.
 * - Makes toolbox items draggable.
 */

/**
 * Initializes the toolbox panel, making items draggable.
 */
export function initializeToolbox() {
    console.log("[Toolbox] Initializing toolbox drag functionality...");

    // Check if jQuery and jQuery UI draggable are loaded
    if (typeof jQuery === 'undefined' || typeof $.fn.draggable === 'undefined') {
        console.error("[Toolbox] jQuery or jQuery UI draggable not loaded. Cannot initialize toolbox.");
        // Optionally display an error in the toolbox panel itself
        const listElement = document.getElementById('toolbox-list');
        if (listElement) {
            listElement.innerHTML = '<p class="text-danger p-2 small">Error: Drag dependency missing.</p>';
        }
        return;
    }

    // Find all toolbox items and make them draggable
    $('.toolbox-item').draggable({
        helper: 'clone', // Create a clone of the item to drag
        appendTo: '#designer-main-container', // Append helper to main container to allow dragging outside the panel
        revert: 'invalid', // Snap back if not dropped on a valid target (jsTree)
        zIndex: 100, // Ensure helper is above other elements
        // Optional: Add classes for styling the helper or during drag
        start: function(event, ui) {
            $(ui.helper).addClass('toolbox-item-dragging');
            console.log("[Toolbox] Drag started:", $(this).data('type'));
        },
        stop: function(event, ui) {
            // No action needed on stop for now
            console.log("[Toolbox] Drag stopped.");
        }
    });

    console.log("[Toolbox] Toolbox items made draggable.");
}

// Initial log
console.log("[Toolbox] Toolbox module loaded."); 