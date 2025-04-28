import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';

/**
 * Extracts the Guild ID from the current URL path.
 * Assumes URL format like /guild/{guild_id}/designer/...
 * @returns {string|null} The Guild ID or null if not found.
 */
export function getGuildIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 3 && pathParts[1] === 'guild') {
        return pathParts[2];
    }
    console.error('[DesignerUtils] Could not extract Guild ID from URL path:', window.location.pathname);
    return null;
}

/**
 * Fetches the guild template data from the API (Specific to this page).
 * Used for initial data and reset data.
 * @param {string} guildId - The ID of the guild.
 * @returns {Promise<object|null>} Template data or null.
 */
export async function fetchGuildTemplate(guildId) {
    if (!guildId) return null; 
    const apiUrl = `/api/v1/guilds/${guildId}/template`;
    console.log(`[DesignerUtils] Fetching guild template data from: ${apiUrl}`);
    try {
        const response = await apiRequest(apiUrl);
        console.log('[DesignerUtils] Successfully fetched template data:', response);
        return response ? response : null;
    } catch (error) {
        console.error('[DesignerUtils] Error fetching guild template:', error);
        // Don't display error here, let caller decide based on context
        // displayErrorMessage('Failed to load guild template data. Please check the console.');
        throw error; // Re-throw so the caller knows it failed
    }
}

/**
 * Displays an error message on the page in a dedicated container.
 * @param {string} message - The error message to display.
 */
export function displayErrorMessage(message) {
    const errorContainer = document.getElementById('designer-error-container');
    let gridManagerErrorContainer = document.getElementById('grid-manager-error-container');
    if (!gridManagerErrorContainer && document.getElementById('designer-main-container')) {
        gridManagerErrorContainer = document.createElement('div');
        gridManagerErrorContainer.id = 'grid-manager-error-container';
        gridManagerErrorContainer.style.display = 'none'; 
        document.getElementById('designer-main-container').prepend(gridManagerErrorContainer);
    }

    if (errorContainer) {
        errorContainer.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        errorContainer.style.display = 'block';
    } else {
        console.error("[DesignerUtils] Error container '#designer-error-container' not found.");
        showToast('error', `UI Error: ${message}`); // Fallback toast
    }
}

/**
 * Debounce function to limit the rate at which a function can fire.
 * @param {function} func The function to debounce.
 * @param {number} wait The number of milliseconds to delay.
 * @returns {function} The debounced function.
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Formats the current structure from jsTree into the payload for the API.
 * Requires jQuery and jsTree to be loaded globally.
 * @param {number|string} templateId - The ID of the template whose structure is being formatted (used for root node parent).
 * @returns {object|null} The payload object { nodes: [...] } or null on error.
 */
export function formatStructureForApi(templateId) {
    console.log(`[DesignerUtils] Formatting structure for template ID: ${templateId}`);
    const treeContainer = document.getElementById('widget-content-structure-tree');
    
    // Check for jQuery and jsTree
    if (typeof jQuery === 'undefined' || typeof $.fn.jstree === 'undefined') {
        console.error("[DesignerUtils] Cannot format structure: jQuery or jsTree not loaded.");
        showToast('error', 'Core component (jsTree) not available for saving.');
        return null;
    }

    const treeInstance = treeContainer ? $(treeContainer).jstree(true) : null;

    if (!treeInstance) {
        console.error("[DesignerUtils] Cannot format structure: Tree container or jsTree instance not found.");
        showToast('error', 'Failed to access structure data for saving.');
        return null;
    }

    try {
        const rootNode = treeInstance.get_json('#'); 
        if (!Array.isArray(rootNode) || rootNode.length !== 1) {
             console.error("[DesignerUtils] Unexpected tree structure format from get_json.", rootNode);
             showToast('error', 'Failed to read structure data.');
             return null;
        }

        const nodesPayload = [];
        // Recursive function to traverse the tree data and format nodes
        function traverseNodes(nodes) {
            if (!Array.isArray(nodes)) return;
            nodes.forEach((node, index) => {
                const nodeId = node.id;
                // Only include category and channel nodes in the payload
                if (nodeId && (nodeId.startsWith('category_') || nodeId.startsWith('channel_'))) {
                    // Extract name: jsTree text often includes position, clean it up
                    const name = node.text.replace(/\s*\(Pos: \d+\)$/, '').trim();
                    
                    let channelType = null;
                    if (nodeId.startsWith('channel_')) {
                        // Attempt to get type from icon or stored data
                        const iconClass = node.icon;
                        if (iconClass && iconClass.includes('fa-hashtag')) {
                            channelType = 'text';
                        } else if (iconClass && iconClass.includes('fa-volume-up')) {
                            channelType = 'voice';
                        } else if (node.data?.channelType) {
                            // Fallback to stored data if icon check fails
                            channelType = node.data.channelType;
                        } else {
                            channelType = 'text'; // Default if type cannot be determined
                            console.warn(`[DesignerUtils] Could not determine channel type for ${nodeId}. Defaulting to 'text'.`);
                        }
                    }

                    const payloadNode = {
                        id: nodeId,
                        parent_id: node.parent === '#' ? `template_${templateId || 'root'}` : node.parent, // Map '#' root to template ID
                        position: index,      // Position is the index among siblings
                        name: name            // Add extracted name
                    };
                    
                    // Add channel_type only for channel nodes
                    if (channelType) {
                         payloadNode.channel_type = channelType;
                    }

                    nodesPayload.push(payloadNode);
                }
                // Recursively process children regardless of parent type
                if (node.children && node.children.length > 0) {
                    traverseNodes(node.children);
                }
            });
        }
        
        // Start traversal from the children of the *actual* root node ('#') returned by get_json
        traverseNodes(rootNode[0].children);

        console.log(`[DesignerUtils] Formatted ${nodesPayload.length} nodes for API payload.`);
        return { nodes: nodesPayload };

    } catch (error) {
        console.error("[DesignerUtils] Error formatting tree data for API:", error);
        showToast('error', 'Failed to prepare structure data for saving.');
        return null;
    }
}

// Initial log to confirm loading
console.log("[DesignerUtils] Utils module loaded.");
