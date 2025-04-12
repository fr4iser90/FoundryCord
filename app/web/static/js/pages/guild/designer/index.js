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
 * (Placeholder - Implement actual DOM manipulation here)
 * @param {object} templateData - The structured template data.
 */
function renderTemplate(templateData) {
    console.log("Rendering template data (placeholder):", templateData);
    
    // TODO: Implement DOM manipulation
    // 1. Find container elements (e.g., #categories-list, #channels-list)
    // 2. Clear any existing content or loading indicators.
    // 3. Iterate through templateData.categories and create HTML elements.
    // 4. Iterate through templateData.channels and create HTML elements, potentially nesting them.
    // 5. Append the created elements to their respective containers.
    
    const infoContainer = document.getElementById('template-info-container'); // Example ID
    const categoriesContainer = document.getElementById('categories-container'); // Example ID
    const channelsContainer = document.getElementById('channels-container'); // Example ID

    if (infoContainer) {
        // Example: Display template name and creation date
        infoContainer.innerHTML = `
            <h5>Template: ${templateData.template_name || 'Unnamed Template'}</h5>
            <p>Created: ${templateData.created_at ? new Date(templateData.created_at).toLocaleString() : 'N/A'}</p>
        `;
    } else {
        console.warn('Template info container not found.');
    }

    if (categoriesContainer) {
        categoriesContainer.innerHTML = ''; // Clear placeholder/loading
        if (templateData.categories && templateData.categories.length > 0) {
            const list = document.createElement('ul');
            templateData.categories.forEach(cat => {
                const item = document.createElement('li');
                item.textContent = `${cat.name} (Pos: ${cat.position}, ID: ${cat.id})`;
                // TODO: Add buttons/links to manage category
                list.appendChild(item);
            });
            categoriesContainer.appendChild(list);
        } else {
            categoriesContainer.innerHTML = '<p>No categories defined in this template.</p>';
        }
    } else {
         console.warn('Categories container not found.');
    }
    
    // TODO: Implement channel rendering similarly, possibly grouping by category ID
    if (channelsContainer) {
         channelsContainer.innerHTML = '<p>Channel rendering not yet implemented.</p>';
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