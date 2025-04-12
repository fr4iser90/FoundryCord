import { apiRequest, showToast } from '/static/js/components/common/notifications.js';

/**
 * Extracts the Guild ID from the current URL path.
 * Assumes URL format like /guild/{guild_id}/designer/...
 * @returns {string|null} The Guild ID or null if not found.
 */
function getGuildIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    // Example path: ['', 'guild', 'GUILD_ID', 'designer', ...]
    if (pathParts.length >= 3 && pathParts[1] === 'guild') {
        return pathParts[2];
    }
    console.error('Could not extract Guild ID from URL path:', window.location.pathname);
    return null;
}

/**
 * Fetches the guild template data from the API.
 * @param {string} guildId - The ID of the guild.
 * @returns {Promise<object|null>} A promise that resolves with the template data or null on error.
 */
async function fetchGuildTemplate(guildId) {
    const apiUrl = `/api/v1/guilds/${guildId}/template`;
    console.log(`Fetching guild template data from: ${apiUrl}`);
    try {
        const response = await apiRequest(apiUrl); // Assumes apiRequest returns parsed data on success
        console.log('Successfully fetched template data:', response);
        return response.data; // Assuming apiRequest wraps the data in a 'data' field
    } catch (error) {
        console.error('Error fetching guild template:', error);
        // The apiRequest function likely shows a toast already.
        // We might want to display a more specific error message on the page.
        displayErrorMessage('Failed to load guild template data. Please check the console.');
        return null;
    }
}

/**
 * Renders the fetched template data onto the page.
 * @param {object} templateData - The structured template data.
 */
function renderTemplate(templateData) {
    console.log("Rendering template data:", templateData);

    const infoContainer = document.getElementById('template-info-container');
    const categoriesContainer = document.getElementById('categories-container');
    const channelsContainer = document.getElementById('channels-container');

    // --- Render Template Info ---
    if (infoContainer) {
        infoContainer.innerHTML = `
            <h5>Template: ${templateData.template_name || 'Unnamed Template'}</h5>
            <p class="mb-0"><small class="text-muted">Created: ${templateData.created_at ? new Date(templateData.created_at).toLocaleString() : 'N/A'}</small></p>
        `;
    } else {
        console.warn('Template info container not found.');
    }

    // --- Render Categories ---
    if (categoriesContainer) {
        categoriesContainer.innerHTML = ''; // Clear placeholder/loading
        if (templateData.categories && templateData.categories.length > 0) {
            // Sort categories by position
            templateData.categories.sort((a, b) => a.position - b.position);

            const list = document.createElement('ul');
            list.className = 'list-group list-group-flush'; // Add some basic styling

            templateData.categories.forEach(cat => {
                const item = document.createElement('li');
                item.className = 'list-group-item d-flex justify-content-between align-items-center';
                item.innerHTML = `
                    <span>
                        <i class="fas fa-folder me-2"></i> <!-- Assuming Font Awesome -->
                        ${cat.name}
                    </span>
                    <span class="badge bg-secondary rounded-pill">Pos: ${cat.position}</span>
                `;
                // TODO: Add buttons/links to manage category later
                list.appendChild(item);
            });
            categoriesContainer.appendChild(list);
        } else {
            categoriesContainer.innerHTML = '<p class="text-muted">No categories defined in this template.</p>';
        }
    } else {
         console.warn('Categories container not found.');
    }

    // --- Render Channels ---
    if (channelsContainer) {
         channelsContainer.innerHTML = ''; // Clear placeholder/loading
         if (templateData.channels && templateData.channels.length > 0) {
            // Create a map for quick category lookup
            const categoriesById = (templateData.categories || []).reduce((acc, cat) => {
                acc[cat.id] = cat;
                return acc;
            }, {});

            // Sort channels primarily by category position, then channel position
            templateData.channels.sort((a, b) => {
                const catA = categoriesById[a.parent_category_template_id];
                const catB = categoriesById[b.parent_category_template_id];
                // Handle cases where a category might be missing (shouldn't happen ideally)
                // or if a channel has no parent (parent_category_template_id is null)
                const posA = a.parent_category_template_id === null ? Infinity : (catA ? catA.position : Infinity - 1); // Uncategorized slightly before missing category refs
                const posB = b.parent_category_template_id === null ? Infinity : (catB ? catB.position : Infinity - 1);

                if (posA !== posB) return posA - posB;
                return a.position - b.position; // Then sort by channel position within category/group
            });

            const list = document.createElement('ul');
            list.className = 'list-group list-group-flush';

            templateData.channels.forEach(chan => {
                const item = document.createElement('li');
                item.className = 'list-group-item d-flex justify-content-between align-items-center';
                const category = categoriesById[chan.parent_category_template_id];
                const categoryName = category ? category.name : 'Uncategorized';
                // Determine icon based on channel type string
                let channelIcon = 'fa-question-circle'; // Default icon
                if (chan.type === 'GUILD_TEXT') {
                    channelIcon = 'fa-hashtag';
                } else if (chan.type === 'GUILD_VOICE') {
                    channelIcon = 'fa-volume-up';
                } // Add more types as needed (e.g., GUILD_STAGE_VOICE, GUILD_FORUM)

                item.innerHTML = `
                    <span>
                        <i class="fas ${channelIcon} me-2"></i>
                        ${chan.name} <small class="text-muted">(${categoryName})</small>
                    </span>
                     <span class="badge bg-secondary rounded-pill">Pos: ${chan.position}</span>
                `;
                 // TODO: Add buttons/links to manage channel later
                list.appendChild(item);
            });
            channelsContainer.appendChild(list);
         } else {
             channelsContainer.innerHTML = '<p class="text-muted">No channels defined in this template.</p>';
         }
    } else {
        console.warn('Channels container not found.');
    }
}

/**
 * Displays an error message on the page.
 * @param {string} message - The error message to display.
 */
function displayErrorMessage(message) {
    // Try to find a dedicated error container, or fallback to replacing main content
    const errorContainer = document.getElementById('designer-error-container');
    const mainContainer = document.getElementById('designer-main-content'); // Assume a main content area

    const errorMessage = `<div class="alert alert-danger">${message}</div>`;

    if (errorContainer) {
        errorContainer.innerHTML = errorMessage;
    } else if (mainContainer) {
        mainContainer.innerHTML = errorMessage;
    } else {
        // Fallback if no specific containers are found
        document.body.insertAdjacentHTML('afterbegin', errorMessage);
    }
}

// --- Main Execution --- 
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Guild Designer page loaded.');
    const guildId = getGuildIdFromUrl();

    if (!guildId) {
        displayErrorMessage('Could not determine the Guild ID from the URL.');
        return;
    }

    const templateData = await fetchGuildTemplate(guildId);

    if (templateData) {
        renderTemplate(templateData);
    } else {
        // Error message should have been displayed by fetchGuildTemplate
        console.log('No template data received or error occurred during fetch.');
    }
}); 