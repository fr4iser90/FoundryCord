import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';

/**
 * Fetches and displays the list of saved GUILD STRUCTURE templates.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} currentGuildId - The current guild ID (needed for context, maybe for save-as).
 */
export async function initializeTemplateList(contentElement, currentGuildId) {
    if (!contentElement) {
        console.warn("[GuildTemplateListWidget] Content element not provided.");
        return;
    }
    if (!currentGuildId) {
        // Maybe still show global templates?
        console.warn("[GuildTemplateListWidget] Current Guild ID not provided.");
        // contentElement.innerHTML = '<p class="panel-placeholder">Guild ID not available.</p>';
        // return;
    }

    console.log("[GuildTemplateListWidget] Initializing...");
    contentElement.innerHTML = '<p class="panel-placeholder">Loading guild structure templates...</p>';

    // --- API ENDPOINT including current Guild ID for context --- 
    // Need to pass the current guild ID so the backend can include its initial snapshot
    const listApiUrl = `/api/v1/templates/guilds/?context_guild_id=${encodeURIComponent(currentGuildId)}`; 

    try {
        // Fetch the list of templates visible to the user, plus initial for context guild
        const response = await apiRequest(listApiUrl); 
        
        // --- CORRECTED RESPONSE HANDLING --- 
        // Expect response format: { templates: [ { template_id: ..., template_name: ... }, ... ] }
        const templates = response?.templates; // Get the array from the 'templates' key

        if (!Array.isArray(templates)) {
            // Handle case where response might be null or not have templates array
            if (response === null || response === undefined) {
                 console.warn("[GuildTemplateListWidget] No response received from template list API.");
                 contentElement.innerHTML = '<p class="panel-placeholder">Could not load templates.</p>';
            } else {
                console.error("[GuildTemplateListWidget] Invalid data received from API (expected array in response.templates):", response);
                contentElement.innerHTML = '<p class="text-danger p-3">Error loading templates: Invalid data format.</p>';
            }
            return;
        }

        if (templates.length === 0) {
            contentElement.innerHTML = '<p class="panel-placeholder">No saved guild structure templates found.</p>';
            return;
        }
        
        const itemTemplate = document.getElementById('template-list-item-template');
        if (!itemTemplate) {
             console.error("[GuildTemplateListWidget] HTML template #template-list-item-template not found!");
             contentElement.innerHTML = '<p class="text-danger p-3">Error: UI template missing.</p>';
             return;
        }
        
        const fragment = document.createDocumentFragment();

        templates.forEach(template => {
            // Use fields from the GuildTemplateListItemSchema
            const templateId = template.template_id; 
            const templateName = template.template_name || 'Unnamed Template';
            // const createdAt = template.created_at;
            // const sourceGuildId = template.guild_id; 
            
            if (templateId === undefined || templateId === null) {
                console.warn('[GuildTemplateListWidget] Template object missing template_id:', template);
                return;
            }

            let iconClass = 'fas fa-server'; 
            let nameSuffix = ''; 

            const clone = itemTemplate.content.cloneNode(true);

            const link = clone.querySelector('.template-load-link');
            const iconElement = clone.querySelector('.template-icon');
            const nameElement = clone.querySelector('.template-name');
            const shareButton = clone.querySelector('.btn-share-template');
            const deleteButton = clone.querySelector('.btn-delete-template'); 

            if (link) {
                 link.dataset.templateId = templateId; 
                 link.addEventListener('click', (event) => {
                    event.preventDefault();
                    handleTemplateLoad(templateId);
                });
            }
            if (iconElement) {
                iconElement.className = `template-icon ${iconClass} me-2`; 
            }
            if (nameElement) {
                nameElement.textContent = `${templateName}${nameSuffix}`;
            }
            // --- Configure SHARE Button --- 
            if (shareButton) {
                // Ensure icon is correct (should match HTML template)
                const shareIconSpan = shareButton.querySelector('i'); 
                if (shareIconSpan) {
                    shareIconSpan.className = 'fas fa-share-alt'; // Correct icon
                }
                shareButton.dataset.templateId = templateId; // Share needs ID
                shareButton.dataset.templateName = templateName;
                shareButton.title = `Share template '${templateName}'`; // Correct title
                shareButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    // Call the new share handler
                    handleTemplateShare(templateId, templateName);
                });
            }
            // --- Configure DELETE Button --- 
            if (deleteButton) {
                // Style the delete icon red
                const deleteIconSpan = deleteButton.querySelector('i'); 
                if (deleteIconSpan) {
                    deleteIconSpan.className = 'fas fa-trash-alt text-danger'; 
                }
                deleteButton.dataset.templateId = templateId;
                deleteButton.dataset.templateName = templateName; 
                deleteButton.title = `Delete template '${templateName}'`;
                deleteButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    handleTemplateDelete(templateId, templateName, contentElement, currentGuildId);
                });
            }
            
            fragment.appendChild(clone);
        });

        contentElement.innerHTML = ''; 
        const listGroup = document.createElement('div');
        listGroup.className = 'list-group list-group-flush';
        listGroup.appendChild(fragment);
        contentElement.appendChild(listGroup);

    } catch (error) {
        console.error("[GuildTemplateListWidget] Error fetching guild structure templates:", error);
        contentElement.innerHTML = `<p class="text-danger p-3">Error loading templates: ${error.message}</p>`;
    }
}

/**
 * Handles loading a selected GUILD STRUCTURE template.
 * @param {string} templateId - The ID of the GUILD STRUCTURE template to load.
 */
function handleTemplateLoad(templateId) {
    console.log(`[GuildTemplateListWidget] Load GUILD STRUCTURE template selected: ${templateId}`);
    // TODO: Implement logic to apply this structure template to the current guild (API call?)
    showToast('info', `Loading guild structure template ${templateId}... (Not implemented yet)`);
}

/**
 * Handles sharing a specific GUILD STRUCTURE template.
 * @param {number} templateId - The ID of the template to share.
 * @param {string} templateName - The name of the template.
 */
function handleTemplateShare(templateId, templateName) {
    console.log(`[GuildTemplateListWidget] Share requested for template ID: ${templateId}, Name: ${templateName}`);
    // TODO: Implement sharing functionality (e.g., generate link, copy to clipboard, open share modal)
    showToast('info', `Sharing template "${templateName}"... (Not implemented yet)`);
}

/**
 * Handles deleting a specific GUILD STRUCTURE template.
 * @param {number} templateId - The ID of the template to delete.
 * @param {string} templateName - The name of the template (for confirmation).
 * @param {HTMLElement} listContentElement - The element containing the list to refresh.
 * @param {string} currentGuildId - The current guild ID for list refresh context.
 */
async function handleTemplateDelete(templateId, templateName, listContentElement, currentGuildId) {
    console.log(`[GuildTemplateListWidget] Delete requested for template ID: ${templateId}, Name: ${templateName}`);

    // Confirmation dialog
    if (!confirm(`Are you sure you want to permanently delete the template "${templateName}"?`)) {
        console.log("[GuildTemplateListWidget] Delete cancelled by user.");
        return;
    }

    const deleteApiUrl = `/api/v1/templates/guilds/${templateId}`;
    console.log(`[GuildTemplateListWidget] Sending DELETE request to: ${deleteApiUrl}`);

    try {
        await apiRequest(deleteApiUrl, {
            method: 'DELETE'
        });
        
        showToast('success', `Template "${templateName}" deleted successfully.`);
        console.log(`[GuildTemplateListWidget] Successfully deleted template ${templateId}.`);
        
        // Refresh the list
        if (listContentElement) {
            initializeTemplateList(listContentElement, currentGuildId);
        } else {
            console.warn("[GuildTemplateListWidget] Could not refresh list after delete: content element missing.");
        }

    } catch (error) {
        console.error(`[GuildTemplateListWidget] Error deleting template ID ${templateId}:`, error);
    }
}
