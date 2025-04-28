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

    // console.log("[ChannelsListWidget] Populating...");

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
            // Assign -1 to uncategorized channels to bring them to the top
            const posA = parentA === null ? -1 : (catA ? catA.position : Infinity); 
            const posB = parentB === null ? -1 : (catB ? catB.position : Infinity); 
            
            // Sort by category position (uncategorized first)
            if (posA !== posB) return posA - posB;
            
            // Within the same category (or both uncategorized), sort by channel position
            const channelPosA = typeof a?.position === 'number' ? a.position : Infinity;
            const channelPosB = typeof b?.position === 'number' ? b.position : Infinity;
            return channelPosA - channelPosB;
        });

        // Create elements using DOM manipulation
        const listElement = document.createElement('ul');
        listElement.className = 'list-group list-group-flush';
        const fragment = document.createDocumentFragment();

        templateData.channels.forEach(chan => {
            if (!chan) return;

            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';

            const nameSpan = document.createElement('span');
            const icon = document.createElement('i');
            const category = categoriesById[chan.parent_category_template_id];
            const categoryName = category ? category.category_name : 'Uncategorized';
            let channelIconClass = 'fas fa-question-circle';
            const rawChannelType = chan.type;
            const channelType = rawChannelType ? rawChannelType.trim().toLowerCase() : '';
            // console.log(`[ChannelList Icon Check] ID=${chan.id}, Raw Type='${rawChannelType}', Processed Type='${channelType}'`); // ENTFERNT
            if (channelType === 'text') channelIconClass = 'fas fa-hashtag';
            else if (channelType === 'voice') channelIconClass = 'fas fa-volume-up';

            icon.className = `${channelIconClass} me-2`;
            nameSpan.appendChild(icon);
            nameSpan.appendChild(document.createTextNode(` ${chan.channel_name || 'Unnamed Channel'} `));
            const categorySmall = document.createElement('small');
            categorySmall.className = 'text-secondary';
            categorySmall.textContent = `(${categoryName})`;
            nameSpan.appendChild(categorySmall);

            const badgeSpan = document.createElement('span');
            badgeSpan.className = 'badge bg-secondary rounded-pill';
            badgeSpan.textContent = `Pos: ${chan.position !== undefined ? chan.position : 'N/A'}`;

            listItem.appendChild(nameSpan);
            listItem.appendChild(badgeSpan);
            fragment.appendChild(listItem);
        });

        listElement.appendChild(fragment);
        contentElement.innerHTML = ''; // Clear previous content
        contentElement.appendChild(listElement);

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