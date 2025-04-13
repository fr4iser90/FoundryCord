import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';

/**
 * Fetches and displays the list of saved templates for the guild.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} guildId - The current guild ID.
 */
export async function initializeTemplateList(contentElement, guildId) {
    if (!contentElement) {
        console.warn("[TemplateListWidget] Content element not provided.");
        return;
    }
    if (!guildId) {
        contentElement.innerHTML = '<p class="panel-placeholder">Guild ID not available.</p>';
        return;
    }

    console.log("[TemplateListWidget] Initializing...");
    contentElement.innerHTML = '<p class="panel-placeholder">Loading templates...</p>';

    // Define the API endpoint - THIS NEEDS TO EXIST ON THE BACKEND
    const apiUrl = `/api/v1/layouts/templates?guild_id=${guildId}`;
    // Alternatively, if the layout identifier IS the template ID:
    // const apiUrl = `/api/v1/layouts`; // And filter client-side? Less ideal.

    try {
        // Assuming the API returns an object with a 'templates' array: { templates: [...] }
        // Adjust if the API returns the array directly.
        const response = await apiRequest(apiUrl);
        const templates = response?.templates || response; // Handle both cases

        if (!Array.isArray(templates)) {
            console.error("[TemplateListWidget] Invalid data received from API:", templates);
            contentElement.innerHTML = '<p class="text-danger p-3">Error loading templates: Invalid data format.</p>';
            return;
        }

        if (templates.length === 0) {
            contentElement.innerHTML = '<p class="panel-placeholder">No saved templates found for this guild.</p>';
            return;
        }

        // Sort templates if needed (e.g., by name or date)
        // templates.sort((a, b) => a.name.localeCompare(b.name));

        const listItems = templates.map(template => {
            let icon = 'fas fa-file-alt'; // Default icon
            let nameSuffix = '';
            if (template.is_initial) {
                icon = 'fas fa-history';
                nameSuffix = ' (Initial Snapshot)';
            }
            if (template.is_shared) {
                icon = 'fas fa-share-alt'; // Or combine icons?
                nameSuffix += ' (Shared)';
            }

            // Ensure template.id exists - adjust property name based on backend model
            const templateId = template.layout_id || template.id;
            if (!templateId) return ''; // Skip templates without an ID

            // Determine if sharing should be disabled (e.g., for the initial snapshot)
            // const isInitialSnapshot = template.is_initial; // REMOVING THIS LOGIC
            // const disableShare = isInitialSnapshot; // REMOVING THIS LOGIC

            // Share button is always enabled now
            return `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <a href="#" class="text-decoration-none text-body flex-grow-1 me-2 template-load-link" data-template-id="${templateId}">
                        <i class="${icon} me-2"></i> ${template.name || 'Unnamed Template'}${nameSuffix}
                    </a>
                    <button class="btn btn-sm btn-outline-secondary btn-share-template"
                            title="Share this layout as a new template" 
                            data-template-id="${templateId}" 
                            data-template-name="${template.name || 'Unnamed Template'}">
                        <i class="fas fa-share-alt"></i>
                    </button>
                </div>
            `;
        }).join('');

        // Remove list-group-flush to restore default item backgrounds
        contentElement.innerHTML = `<div class="list-group">${listItems}</div>`;

        // Add event listener for loading templates (now targets the link)
        contentElement.querySelectorAll('.template-load-link').forEach(item => {
            item.addEventListener('click', (event) => {
                event.preventDefault();
                const selectedTemplateId = event.currentTarget.dataset.templateId;
                handleTemplateLoad(selectedTemplateId);
            });
        });

        // Add event listener for sharing templates (targets the button)
        contentElement.querySelectorAll('.btn-share-template').forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation(); // Prevent triggering the load link click
                const templateIdToShare = event.currentTarget.dataset.templateId;
                const currentTemplateName = event.currentTarget.dataset.templateName;
                handleTemplateShare(templateIdToShare, currentTemplateName);
            });
        });

    } catch (error) {
        console.error("[TemplateListWidget] Error fetching templates:", error);
        contentElement.innerHTML = `<p class="text-danger p-3">Error loading templates: ${error.message}</p>`;
    }
}

/**
 * Handles the action when a template is selected from the list.
 * @param {string} templateId - The ID of the selected template.
 */
function handleTemplateLoad(templateId) {
    console.log(`[TemplateListWidget] Template selected: ${templateId}`);
    // TODO: Implement loading logic
    showToast('info', `Loading template ${templateId}... (Not implemented yet)`);
}

// Store modal instance to avoid recreating it every time
let shareModalInstance = null;
let confirmShareBtnListener = null; // Store listener to remove later if needed

/**
 * Handles the action when the share button for a template is clicked.
 * @param {string} templateId - The ID of the template to share.
 * @param {string} currentName - The current name of the template (as default for modal).
 */
function handleTemplateShare(templateId, currentName) {
    console.log(`[TemplateListWidget] Share initiated for template ID: ${templateId}, Current Name: ${currentName}`);

    // Parse the template ID to remove the prefix if it exists
    const cleanTemplateId = templateId.replace('guild-designer-', '');
    console.log(`[TemplateListWidget] Using cleaned template ID: ${cleanTemplateId}`);

    const modalElement = document.getElementById('shareTemplateModal');
    const nameInput = document.getElementById('shareTemplateNameInput');
    const descInput = document.getElementById('shareTemplateDescriptionInput');
    const templateIdInput = document.getElementById('shareTemplateIdInput'); // Hidden input
    const confirmBtn = document.getElementById('confirmShareTemplateBtn');

    if (!modalElement || !nameInput || !descInput || !templateIdInput || !confirmBtn) {
        console.error("[TemplateListWidget] Share modal elements not found!");
        showToast('error', 'Could not open share dialog.');
        return;
    }

    // Get or create the Bootstrap Modal instance
    if (!shareModalInstance) {
        shareModalInstance = new bootstrap.Modal(modalElement);
    }

    // Set values for the modal using the cleaned ID
    templateIdInput.value = cleanTemplateId;
    nameInput.value = `Copy of ${currentName}`; // Suggest a default name
    descInput.value = ''; // Clear description
    nameInput.classList.remove('is-invalid'); // Reset validation state

    // --- API Call Logic --- 
    // Define the function to be called when confirm is clicked
    const shareApiCall = async () => {
        const newName = nameInput.value.trim();
        const newDescription = descInput.value.trim();
        const idToShare = templateIdInput.value;

        // Basic validation
        if (!newName || newName.length < 3 || newName.length > 100) {
            nameInput.classList.add('is-invalid');
            showToast('warning', 'Please enter a valid template name (3-100 characters).');
            return; // Stop processing
        } else {
            nameInput.classList.remove('is-invalid');
        }

        const apiUrl = `/api/v1/layouts/templates/share/${idToShare}`;
        const payload = {
            template_name: newName,
            template_description: newDescription || null // Send null if empty
        };

        console.log(`[TemplateListWidget] Sending share request to ${apiUrl} with payload:`, payload);

        try {
            const response = await apiRequest(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            console.log('[TemplateListWidget] Share response:', response); // Add response logging
            showToast('success', `Template '${newName}' shared successfully!`);
            shareModalInstance.hide();

            // Refresh the template list to show the new shared template
            const contentElement = document.getElementById('widget-content-template-list'); 
            const guildId = document.body.dataset.guildId;
            if (contentElement && guildId) {
                 initializeTemplateList(contentElement, guildId);
            } else {
                console.warn("[TemplateListWidget] Could not refresh list after sharing.");
            }

        } catch (error) {
            // Updated error logging for ApiError
            console.error("[TemplateListWidget] Error sharing template:", {
                error,
                templateId: idToShare,
                apiUrl,
                payload,
                // Access status and data directly from ApiError if it exists
                status: (error instanceof ApiError) ? error.status : undefined,
                responseData: (error instanceof ApiError) ? error.data : undefined
            });

            // Updated specific error handling
            if (error instanceof ApiError) {
                if (error.status === 400) {
                    // Use the specific error message from the API if available
                    showToast('error', `Failed to share: ${error.message}. The name might already be taken.`);
                    // --- Debugging --- 
                    console.log("Applying is-invalid to:", nameInput); 
                    // --- End Debugging ---
                    nameInput.classList.add('is-invalid');
                } else if (error.status === 404) {
                    showToast('error', 'Template not found. It may have been deleted.');
                } else if (error.status === 403) {
                    showToast('error', 'You do not have permission to share this template.');
                } else {
                    // General ApiError message (already includes status in the toast from apiRequest)
                    // Avoid double-toast if apiRequest already showed one.
                    // We can just rely on the console log here or the toast from apiRequest.
                    // showToast('error', `Failed to share template: ${error.message}`); 
                }
            } else {
                 // Handle non-ApiError errors (e.g., network issues before response)
                 showToast('error', `Failed to share template: ${error.message || 'An unexpected network error occurred'}`);
            }
        }
    };

    // --- Event Listener Management --- 
    // Remove previous listener if it exists to prevent multiple bindings
    if (confirmShareBtnListener) {
        confirmBtn.removeEventListener('click', confirmShareBtnListener);
    }
    // Store the new listener function reference
    confirmShareBtnListener = shareApiCall;
    // Add the event listener
    confirmBtn.addEventListener('click', confirmShareBtnListener);

    // Show the modal
    shareModalInstance.show();
}
