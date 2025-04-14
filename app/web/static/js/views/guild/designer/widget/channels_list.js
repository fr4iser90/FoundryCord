/**
 * Populates the content of the Channels List widget.
 * @param {object} templateData - The structured template data.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} guildId - The current guild ID for link generation.
 */
export function initializeChannelsList(templateData, contentElement, guildId) {
     if (!contentElement) {
        console.warn("[ChannelsListWidget] Content element not provided.");
        return;
    }
    if (!templateData || !Array.isArray(templateData.channels) || !Array.isArray(templateData.categories)) {
        contentElement.innerHTML = '<p class="panel-placeholder">Channels or Categories data not available.</p>';
        return;
    }

    console.log("[ChannelsListWidget] Populating...");

    // Build categories map locally for sorting/display
    const categoriesById = {};
    templateData.categories.forEach(cat => { if (cat && cat.id) categoriesById[cat.id] = cat; });

    if (templateData.channels.length > 0) {
        // Sort using the categoriesById map 
        templateData.channels.sort((a, b) => {
            const parentA = a?.parent_category_template_id;
            const parentB = b?.parent_category_template_id;
            const catA = categoriesById[parentA];
            const catB = categoriesById[parentB];
            const posA = parentA === null ? Infinity : (catA ? catA.position : Infinity - 1);
            const posB = parentB === null ? Infinity : (catB ? catB.position : Infinity - 1);
            if (posA !== posB) return posA - posB;
            const channelPosA = typeof a?.position === 'number' ? a.position : Infinity;
            const channelPosB = typeof b?.position === 'number' ? b.position : Infinity;
            return channelPosA - channelPosB;
        });
        const listItems = templateData.channels.map(chan => {
            if (!chan) return '';
            const category = categoriesById[chan.parent_category_template_id];
            const categoryName = category ? category.category_name : 'Uncategorized';
            let channelIcon = 'fas fa-question-circle';
            if (chan.type === 'GUILD_TEXT') channelIcon = 'fas fa-hashtag';
            else if (chan.type === 'GUILD_VOICE') channelIcon = 'fas fa-volume-up';
             return `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                <span>
                    <i class="fas ${channelIcon} me-2"></i>
                        ${chan.channel_name || 'Unnamed Channel'} <small class="text-secondary">(${categoryName})</small>
                </span>
                    <span class="badge bg-secondary rounded-pill">Pos: ${chan.position !== undefined ? chan.position : 'N/A'}</span>
                </li>
            `;
        }).join('');
        contentElement.innerHTML = `<ul class="list-group list-group-flush">${listItems}</ul>`;

        // Ensure Manage link exists
        const header = contentElement.closest('.grid-stack-item-content')?.querySelector('.widget-header');
         if (header && guildId && !header.querySelector('a.manage-link')) { // Add class to check specifically
            const manageLink = document.createElement('a');
            manageLink.href = `/guild/${guildId}/designer/channels`;
            manageLink.className = 'btn btn-sm btn-outline-primary ms-auto manage-link'; // Add class
            manageLink.textContent = 'Manage';
             manageLink.style.marginLeft = 'auto';
            header.appendChild(manageLink);
        }
     } else {
        contentElement.innerHTML = '<p class="panel-placeholder">No channels defined.</p>';
     }
} 