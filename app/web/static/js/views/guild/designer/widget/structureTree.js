// Logic specifically for the jsTree structure widget

// Import dependencies needed WITHIN this module (if any were used directly, like showToast)
// For now, formatDataForJsTree and initializeStructureTree seem self-contained
// except for jQuery which is global via CDN.
import { showToast } from '/static/js/components/common/notifications.js';

/**
 * Converts template data into the format required by jsTree.
 * @param {object} templateData - The structured template data.
 * @returns {Array} Array of nodes for jsTree.
 */
function formatDataForJsTree(templateData) {
    if (!templateData) return [];

    const treeData = [];
    const categoriesById = {}; // Keep this map needed for categorized channels

    // 1. Root node for the template
    treeData.push({
        id: `template_${templateData.id || 'root'}`,
        parent: '#', // # denotes the root
        text: 'Guild Structure', // Use a static label for the root
        icon: 'fas fa-server', // Example icon
        type: 'template' // Custom type for styling/behavior
    });

    // Process channels first to separate them
    const uncategorizedChannels = [];
    const categorizedChannels = [];
    if (Array.isArray(templateData.channels)) {
        templateData.channels.forEach(chan => {
            if (chan && chan.id) {
                if (chan.parent_category_template_id === null || chan.parent_category_template_id === undefined) {
                    uncategorizedChannels.push(chan);
                } else {
                    categorizedChannels.push(chan);
                }
            }
        });
    }

    // Sort channel groups by position
    uncategorizedChannels.sort((a, b) => (a?.position ?? Infinity) - (b?.position ?? Infinity));
    categorizedChannels.sort((a, b) => (a?.position ?? Infinity) - (b?.position ?? Infinity));

    // 2. Add uncategorized channels to treeData (parent is root)
    uncategorizedChannels.forEach(chan => {
        const icon = getChannelIcon(chan.type);
        treeData.push({
            id: `channel_${chan.id}`,
            parent: `template_${templateData.id || 'root'}`, // Assign to root
            text: `${chan.channel_name || 'Unnamed Channel'} (Pos: ${chan.position})`,
            icon: icon,
            type: 'channel',
            data: { type: 'channel', dbId: chan.id, channelType: chan.type }
        });
    });

    // 3. Process and Add categories (parent is root)
    if (Array.isArray(templateData.categories)) {
        templateData.categories.sort((a, b) => (a?.position ?? Infinity) - (b?.position ?? Infinity)); // Also sort categories
        templateData.categories.forEach(cat => {
            if (cat && cat.id) {
                categoriesById[cat.id] = cat; // Store for channel lookup
                treeData.push({
                    id: `category_${cat.id}`,
                    parent: `template_${templateData.id || 'root'}`, // Assign to root
                    text: `${cat.category_name || 'Unnamed Category'} (Pos: ${cat.position})`,
                    icon: 'fas fa-folder', // Example icon
                    type: 'category',
                    data: { type: 'category', dbId: cat.id } // Store original data if needed
                });
            }
        });
    }

    // 4. Add categorized channels to treeData (parent is category)
    categorizedChannels.forEach(chan => {
        // Check if parent category actually exists in the data we processed
        if (categoriesById[chan.parent_category_template_id]) {
             const icon = getChannelIcon(chan.type);
             const parentId = `category_${chan.parent_category_template_id}`;
             treeData.push({
                 id: `channel_${chan.id}`,
                 parent: parentId,
                 text: `${chan.channel_name || 'Unnamed Channel'} (Pos: ${chan.position})`,
                 icon: icon,
                 type: 'channel',
                 data: { type: 'channel', dbId: chan.id, channelType: chan.type }
             });
        } else {
            // Log a warning if a channel references a non-existent parent category ID
            console.warn(`[TreeWidget] Channel '${chan.channel_name}' (ID: ${chan.id}) references non-existent parent category ID: ${chan.parent_category_template_id}. Skipping.`);
        }
    });

    // Debug log for the final structure
    // console.log("[TreeWidget] Final formatted data for jsTree:", JSON.stringify(treeData, null, 2));
    return treeData;
}

// Helper function to get icon class based on channel type
function getChannelIcon(rawChannelType) {
    const channelType = rawChannelType ? String(rawChannelType).trim().toLowerCase() : '';
    if (channelType === 'text') return 'fas fa-hashtag';
    if (channelType === 'voice') return 'fas fa-volume-up';
    // Add other types as needed
    return 'fas fa-question-circle'; // Default
}

/**
 * Initializes the jsTree structure view inside its widget.
 * @param {object} templateData - The structured template data.
 */
export function initializeStructureTree(templateData) { // Export the function
    // console.log("[TreeWidget] Initializing structure tree..."); // AUSKOMMENTIERT
    const treeContainer = document.getElementById('widget-content-structure-tree');
    if (!treeContainer) {
        console.error('[TreeWidget] Tree container #widget-content-structure-tree not found!'); // BLEIBT (Fehlerlog)
        return;
    }

    const treeData = formatDataForJsTree(templateData);

    if (!treeData || treeData.length === 0) {
        treeContainer.innerHTML = '<p class="text-muted p-3">No structure data to display.</p>';
        return;
    }

    // Initialize jsTree
    if (typeof jQuery === 'undefined') {
        console.error('[TreeWidget] jQuery is not loaded. Cannot initialize jsTree.'); // BLEIBT (Fehlerlog)
        treeContainer.innerHTML = '<p class="text-danger p-3">Error: jQuery not loaded.</p>';
        return;
    }
    if (typeof $.fn.jstree === 'undefined') {
         console.error('[TreeWidget] jsTree plugin not loaded. Cannot initialize.'); // BLEIBT (Fehlerlog)
         treeContainer.innerHTML = '<p class="text-danger p-3">Error: jsTree not loaded.</p>';
        return;
    }

    // Destroy previous instance if exists
    if ($(treeContainer).jstree(true)) {
        $(treeContainer).jstree(true).destroy();
        // console.log("[TreeWidget] Destroyed existing jsTree instance."); // AUSKOMMENTIERT
    }
    treeContainer.innerHTML = ''; // Clear previous content

    try {
        $(treeContainer).jstree({
            core: {
                data: treeData,
                check_callback: true, 
                themes: { name: 'default', responsive: true, stripes: true }
            },
            plugins: ["dnd", "types", "wholerow"], 
            types: {
                "template": { "icon": "fas fa-server text-primary" },
                "category": { "icon": "fas fa-folder text-warning" },
                "channel": { /* default icon set in data */ }
            }
        })
        .on('ready.jstree', function () {
             // console.log("[TreeWidget] jsTree is ready. Opening root node."); // AUSKOMMENTIERT
             $(this).jstree('open_node', `template_${templateData.id || 'root'}`);
        })
        .on('select_node.jstree', function (e, data) {
            // console.log("[TreeWidget] Node selected:", data.node); // AUSKOMMENTIERT
            const propertiesPanel = document.querySelector('.editor-panel-right');
            if (propertiesPanel && !propertiesPanel.classList.contains('collapsed')) {
                const propsContent = propertiesPanel.querySelector('.panel-content-area') || propertiesPanel;
                // Simple display for now - Replace with actual form/fields later
                propsContent.innerHTML = `<div class="panel-content-area p-3"><h5 class="mt-0">Properties</h5><hr><p><b>${data.node.text}</b></p><p><small>ID: ${data.node.id}</small></p><pre class="small bg-light p-2 rounded">${JSON.stringify(data.node.data || {}, null, 2)}</pre></div>`;
            } else {
                 // console.log("[TreeWidget] Properties panel is collapsed or not found, skipping update."); // AUSKOMMENTIERT
            }
        })
        .on('move_node.jstree', function (e, data) {
            // console.log("[TreeWidget] Raw move_node data:", data);
            const movedNodeId = data.node.id; // e.g., "channel_123" or "category_456"
            const newParentId = data.parent; // e.g., "category_456" or "template_root"
            const newPosition = data.position; // Index among siblings (0-based)
            const oldParentId = data.old_parent;
            const oldPosition = data.old_position;

            console.log(`[TreeWidget] Node Moved: ID=${movedNodeId}`);
            console.log(`  New Parent: ID=${newParentId}, Position: ${newPosition}`);
            console.log(`  Old Parent: ID=${oldParentId}, Position: ${oldPosition}`);

            // Dispatch a custom event to notify index.js
            document.dispatchEvent(new CustomEvent('structureChanged', {
                detail: {
                    nodeId: movedNodeId,
                    newParentId: newParentId,
                    newPosition: newPosition,
                    oldParentId: oldParentId,
                    oldPosition: oldPosition
                }
            }));

            showToast('info', `Moved ${data.node.text}. Remember to save changes.`);
        });
        // console.log("[TreeWidget] jsTree initialized successfully."); // AUSKOMMENTIERT
    } catch (error) {
        console.error("[TreeWidget] Error initializing jsTree:", error); // BLEIBT (Fehlerlog)
        treeContainer.innerHTML = '<p class="text-danger p-3">Error initializing tree view.</p>';
    }
} 