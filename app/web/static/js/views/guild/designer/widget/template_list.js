import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';

/**
 * Fetches and displays the list of SAVED GUILD STRUCTURE templates for the current context
 * (including the initial snapshot and user-saved templates).
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} currentGuildId - The current guild ID (needed for context).
 * @param {string|null} activeTemplateId - The ID of the currently active template (or null).
 */
export async function initializeTemplateList(contentElement, currentGuildId, activeTemplateId) {
    if (!contentElement) {
        // console.warn("[GuildTemplateListWidget] Content element not provided.");
        return;
    }
    if (!currentGuildId) {
        console.warn("[GuildTemplateListWidget] Current Guild ID not provided, cannot load templates.");
        contentElement.innerHTML = '<p class="panel-placeholder">Guild context not available.</p>';
        return;
    }

    console.log("[GuildTemplateListWidget] Initializing saved templates list...");
    contentElement.innerHTML = '<p class="panel-placeholder">Loading saved guild structure templates...</p>';

    // API ENDPOINT fetches initial snapshot for the context guild + user-saved templates
    const listApiUrl = `/api/v1/templates/guilds/?context_guild_id=${encodeURIComponent(currentGuildId)}`; 

    try {
        // Fetch the list of templates
        const response = await apiRequest(listApiUrl); 
        
        // Expect response format: { templates: [ { template_id: ..., template_name: ..., is_initial_snapshot: boolean (optional) }, ... ] }
        const templates = response?.templates; 

        if (!Array.isArray(templates)) {
            // Handle case where response might be null or not have templates array
            if (response === null || response === undefined) {
                 // console.warn("[GuildTemplateListWidget] No response received from template list API.");
                 contentElement.innerHTML = '<p class="text-danger p-3">Error loading templates: Invalid data format.</p>';
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
        
        const fragment = document.createDocumentFragment();

        // Convert activeTemplateId to number for comparison, handle null/undefined
        const currentActiveId = activeTemplateId ? parseInt(activeTemplateId, 10) : null;

        templates.forEach(template => {
            const templateId = template.template_id; 
            const templateName = template.template_name || 'Unnamed Template';
            
            if (templateId === undefined || templateId === null) {
                // console.warn('[GuildTemplateListWidget] Template object missing template_id:', template);
                return;
            }
            
            // --- Check if this is the initial snapshot (assuming API provides a flag) --- 
            const isInitialSnapshot = template.is_initial_snapshot === true; // Example check

            // --- Create elements using DOM --- 
            const listItem = document.createElement('div');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';

            const link = document.createElement('a');
            link.href = '#';
            link.className = 'text-decoration-none text-body flex-grow-1 me-2 template-load-link';
            link.dataset.templateId = templateId;
            link.addEventListener('click', (event) => {
                event.preventDefault();
                handleTemplateLoad(templateId);
            });

            const iconElement = document.createElement('i');
            // TODO: Consider making icon dynamic based on template type (initial, user, shared) if needed
            iconElement.className = 'template-icon fas fa-server me-2'; // Default icon
            link.appendChild(iconElement);

            const nameSpan = document.createElement('span');
            nameSpan.className = 'template-name';
            nameSpan.textContent = templateName;
            link.appendChild(nameSpan);

            listItem.appendChild(link);

            // --- Action Buttons Group --- 
            const buttonGroup = document.createElement('div');
            buttonGroup.className = 'btn-group btn-group-sm';
            buttonGroup.setAttribute('role', 'group');
            buttonGroup.setAttribute('aria-label', 'Template Actions');

            // Share Button
            const shareButton = document.createElement('button');
            shareButton.type = 'button';
            shareButton.className = 'btn btn-outline-secondary btn-share-template';
            shareButton.title = `Share template '${templateName}'`;
            shareButton.dataset.templateId = templateId;
            shareButton.dataset.templateName = templateName;
            const shareIcon = document.createElement('i');
            shareIcon.className = 'fas fa-share-alt';
            shareButton.appendChild(shareIcon);
            // TODO: Disable share button for initial snapshot?
            // shareButton.disabled = isInitialSnapshot;
            shareButton.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                handleTemplateShare(templateId, templateName);
            });
            buttonGroup.appendChild(shareButton);

            // Activate Button
            const activateButton = document.createElement('button');
            activateButton.type = 'button';
            activateButton.className = 'btn btn-outline-success btn-activate-template'; // New class
            activateButton.title = `Set template '${templateName}' as active for this guild`;
            activateButton.dataset.templateId = templateId;
            activateButton.dataset.templateName = templateName;
            const activateIcon = document.createElement('i');
            // Check if this template is the active one
            const isActive = (currentActiveId !== null && templateId === currentActiveId);

            if (isActive) {
                activateButton.disabled = true;
                activateButton.title = `Template '${templateName}' is already active`;
                activateButton.classList.remove('btn-outline-success');
                activateButton.classList.add('btn-success', 'active'); // Make it look pressed/active
                activateIcon.className = 'fas fa-star'; // Change icon to star or similar
                nameSpan.insertAdjacentHTML('beforeend', ' <span class="badge bg-success ms-1">Active</span>'); // Add badge
            } else {
                activateIcon.className = 'fas fa-check-circle'; // Default checkmark icon
                activateButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    handleTemplateActivate(templateId, templateName, currentGuildId, listContentElement, currentActiveId);
                });
            }
            activateButton.appendChild(activateIcon);
            buttonGroup.appendChild(activateButton);

            // Delete Button
            const deleteButton = document.createElement('button');
            deleteButton.type = 'button';
            deleteButton.className = 'btn btn-outline-secondary btn-delete-template';
            deleteButton.title = `Delete template '${templateName}'`;
            deleteButton.dataset.templateId = templateId;
            deleteButton.dataset.templateName = templateName;
            const deleteIcon = document.createElement('i');
            deleteIcon.className = 'fas fa-trash-alt text-danger'; // Style icon red
            deleteButton.appendChild(deleteIcon);
            
            // --- Disable delete for initial snapshot --- 
            if (isInitialSnapshot) {
                deleteButton.disabled = true;
                deleteButton.title = 'Cannot delete the initial guild snapshot.';
                deleteButton.classList.add('disabled'); // Optional: visual cue
            } else {
                deleteButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    handleTemplateDelete(templateId, templateName, contentElement, currentGuildId);
                });
            }
            // -------------------------------------------
            
            buttonGroup.appendChild(deleteButton);
            // --- End Action Buttons ---

            listItem.appendChild(buttonGroup);
            fragment.appendChild(listItem);
            // --- End DOM Creation ---
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
 * Handles loading a selected SAVED or INITIAL GUILD STRUCTURE template.
 * @param {string} templateId - The ID of the template to load.
 */
function handleTemplateLoad(templateId) {
    // console.log(`[GuildTemplateListWidget] Load GUILD STRUCTURE template selected: ${templateId}`);
    // TODO: Implement logic to apply this structure template to the current guild (API call?)
    showToast('info', `Loading guild structure template ${templateId}... (Not implemented yet)`);
}

/**
 * Handles sharing a specific SAVED GUILD STRUCTURE template.
 * @param {number} templateId - The ID of the template to share.
 * @param {string} templateName - The name of the template.
 */
function handleTemplateShare(templateId, templateName) {
    // console.log(`[GuildTemplateListWidget] Share requested for template ID: ${templateId}, Name: ${templateName}`);

    // Get the modal element
    const shareModalElement = document.getElementById('shareTemplateModal');
    if (!shareModalElement) {
        console.error("[GuildTemplateListWidget] Share modal element (#shareTemplateModal) not found in the DOM.");
        showToast('error', 'Could not open the share dialog.');
        return;
    }

    // Get the Bootstrap modal instance
    // Ensure Bootstrap's Modal class is available (likely loaded globally via base template)
    const bootstrapModal = bootstrap.Modal.getInstance(shareModalElement) || new bootstrap.Modal(shareModalElement);

    // Populate the modal fields
    const templateIdInput = shareModalElement.querySelector('#shareTemplateIdInput');
    const templateNameInput = shareModalElement.querySelector('#shareTemplateNameInput');
    const templateDescriptionInput = shareModalElement.querySelector('#shareTemplateDescriptionInput');

    if (templateIdInput) {
        templateIdInput.value = templateId;
    } else {
        console.warn("[GuildTemplateListWidget] Share modal is missing the template ID input.");
    }
    
    if (templateNameInput) {
        templateNameInput.value = templateName; // Pre-fill with the original name
    } else {
        console.warn("[GuildTemplateListWidget] Share modal is missing the template name input.");
    }

    if (templateDescriptionInput) {
        templateDescriptionInput.value = ''; // Clear description on open
    } else {
        console.warn("[GuildTemplateListWidget] Share modal is missing the template description input.");
    }

    // Show the modal
    bootstrapModal.show();
}

/**
 * Handles deleting a specific SAVED GUILD STRUCTURE template.
 * (Cannot delete the initial snapshot).
 * @param {number} templateId - The ID of the template to delete.
 * @param {string} templateName - The name of the template (for confirmation).
 * @param {HTMLElement} listContentElement - The element containing the list to refresh.
 * @param {string} currentGuildId - The current guild ID for list refresh context.
 */
async function handleTemplateDelete(templateId, templateName, listContentElement, currentGuildId) {
    // console.log(`[GuildTemplateListWidget] Delete requested for saved template ID: ${templateId}, Name: ${templateName}`);

    // Confirmation dialog
    if (!confirm(`Are you sure you want to permanently delete the template "${templateName}"?`)) {
        // console.log("[GuildTemplateListWidget] Delete cancelled by user.");
        return;
    }

    const deleteApiUrl = `/api/v1/templates/guilds/${templateId}`;
    // console.log(`[GuildTemplateListWidget] Sending DELETE request to: ${deleteApiUrl}`);

    try {
        await apiRequest(deleteApiUrl, {
            method: 'DELETE'
        });
        
        showToast('success', `Template "${templateName}" deleted successfully.`);
        // console.log(`[GuildTemplateListWidget] Successfully deleted template ${templateId}.`);
        
        // Refresh the list
        if (listContentElement) {
            initializeTemplateList(listContentElement, currentGuildId);
        } else {
            // console.warn("[GuildTemplateListWidget] Could not refresh list after delete: content element missing.");
        }

    } catch (error) {
        console.error(`[GuildTemplateListWidget] Error deleting template ID ${templateId}:`, error);
    }
}

/**
 * Handles activating a specific template for the current guild.
 * @param {number} templateId - The ID of the template to activate.
 * @param {string} templateName - The name of the template (for confirmation).
 * @param {string} guildId - The ID of the current guild.
 * @param {HTMLElement} listContentElement - The element containing the list to refresh.
 * @param {string|null} initialActiveId - The active ID when the list was loaded.
 */
async function handleTemplateActivate(templateId, templateName, guildId, listContentElement, initialActiveId) {
    console.log(`[GuildTemplateListWidget] Activate requested for template ID: ${templateId}, Name: ${templateName}, Guild: ${guildId}`);

    if (!guildId) {
        console.error("[GuildTemplateListWidget] Cannot activate template: Guild ID is missing.");
        showToast('error', 'Cannot activate template: Guild context missing.');
        return;
    }

    // Confirmation dialog
    if (!confirm(`Are you sure you want to set "${templateName}" as the active template for this guild?\n(This won't apply changes immediately, but marks it for future application).`)) {
        console.log("[GuildTemplateListWidget] Activation cancelled by user.");
        return;
    }

    const activateApiUrl = `/api/v1/guilds/${guildId}/template/activate`;
    const payload = { template_id: templateId };

    console.log(`[GuildTemplateListWidget] Sending POST request to: ${activateApiUrl} with payload:`, payload);

    try {
        await apiRequest(activateApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        showToast('success', `Template "${templateName}" is now set as active.`);
        console.log(`[GuildTemplateListWidget] Successfully activated template ${templateId} for guild ${guildId}.`);
        
        // Refresh the list to show the updated active state
        if (listContentElement) {
            // Pass the NEWLY activated template ID for the refresh
            initializeTemplateList(listContentElement, guildId, String(templateId)); 
        } else {
            console.warn("[GuildTemplateListWidget] Could not refresh list after activation: content element missing.");
        }

    } catch (error) {
        // apiRequest handles basic toast, but log details here
        console.error(`[GuildTemplateListWidget] Error activating template ID ${templateId} for guild ${guildId}:`, error);
        // Optionally provide more specific feedback if needed based on error type/status
    }
}
