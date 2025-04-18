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
    const categoriesById = {};

    // Root node for the template
    treeData.push({
        id: `template_${templateData.id || 'root'}`,
        parent: '#', // # denotes the root
        text: templateData.template_name || 'Guild Structure',
        icon: 'fas fa-server', // Example icon
        type: 'template' // Custom type for styling/behavior
    });

    // Process categories
    if (Array.isArray(templateData.categories)) {
        templateData.categories.sort((a, b) => a.position - b.position);
        templateData.categories.forEach(cat => {
            if (cat && cat.id) {
                categoriesById[cat.id] = cat; // Store for channel lookup
                treeData.push({
                    id: `category_${cat.id}`,
                    parent: `template_${templateData.id || 'root'}`,
                    text: `${cat.category_name || 'Unnamed Category'} (Pos: ${cat.position})`,
                    icon: 'fas fa-folder', // Example icon
                    type: 'category',
                    data: { type: 'category', dbId: cat.id } // Store original data if needed
                });
            }
        });
    }

    // Process channels
    if (Array.isArray(templateData.channels)) {
        templateData.channels.sort((a, b) => a.position - b.position);
        templateData.channels.forEach(chan => {
             if (chan && chan.id) {
                const iconElement = document.createElement('i');
                let icon = 'fas fa-question-circle'; // Default icon
                const rawChannelType = chan.type;
                const channelType = rawChannelType ? rawChannelType.trim().toLowerCase() : '';
                // --- TEMPORARY DEBUG LOG REMOVED ---
                // console.log(`[TreeWidget Icon Check] ID=${chan.id}, Raw Type='${rawChannelType}', Processed Type='${channelType}'`);
                // -----------------------------------
                if (channelType === 'text') icon = 'fas fa-hashtag';
                else if (channelType === 'voice') icon = 'fas fa-volume-up';
                // iconElement.className = icon + ' me-2'; // Nicht mehr nötig, da wir den String übergeben
                
                const parentId = chan.parent_category_template_id 
                    ? `category_${chan.parent_category_template_id}` 
                    : `template_${templateData.id || 'root'}`; // Assign to root if no category

                treeData.push({
                    id: `channel_${chan.id}`,
                    parent: parentId,
                    text: `${chan.channel_name || 'Unnamed Channel'} (Pos: ${chan.position})`,
                    icon: icon, // <-- KORREKTUR: Gib den String mit der Klasse weiter, nicht das Element
                    type: 'channel',
                    data: { type: 'channel', dbId: chan.id, channelType: chan.type } // Store original data
                });
            }
        });
    }

    // console.log("[TreeWidget] Formatted data for jsTree:", treeData); // AUSKOMMENTIERT
    return treeData;
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
            // console.log("[TreeWidget] Node moved:", data); // AUSKOMMENTIERT
            showToast('info', `Moved ${data.node.text}. Saving structure not implemented yet.`);
            // TODO: Implement save logic here or trigger a save action
        });
        // console.log("[TreeWidget] jsTree initialized successfully."); // AUSKOMMENTIERT
    } catch (error) {
        console.error("[TreeWidget] Error initializing jsTree:", error); // BLEIBT (Fehlerlog)
        treeContainer.innerHTML = '<p class="text-danger p-3">Error initializing tree view.</p>';
    }
} 