import { apiRequest, showToast } from '/static/js/components/common/notifications.js';
// Potentially needed imports if list refresh is desired:
// import { getGuildIdFromUrl } from '../index.js'; // Adjust path if needed
// import { initializeTemplateList } from '../widget/templateList.js';

/**
 * Initializes the event listeners and logic for the Share Template modal.
 */
export function initializeShareModal() {
    const confirmShareBtn = document.getElementById('confirmShareTemplateBtn');
    const shareModalElement = document.getElementById('shareTemplateModal');
    const shareTemplateNameInput = document.getElementById('shareTemplateNameInput');
    const shareTemplateDescInput = document.getElementById('shareTemplateDescriptionInput');
    const shareTemplateIdInput = document.getElementById('shareTemplateIdInput'); // Hidden input

    if (confirmShareBtn && shareModalElement && shareTemplateNameInput && shareTemplateDescInput && shareTemplateIdInput) {
        // Ensure Bootstrap Modal class is available (usually global)
        if (typeof bootstrap === 'undefined' || !bootstrap.Modal) {
            console.error('[ShareModal] Bootstrap Modal component not found.');
            return;
        }
        const shareModal = bootstrap.Modal.getInstance(shareModalElement) || new bootstrap.Modal(shareModalElement);

        confirmShareBtn.addEventListener('click', async () => {
            const originalTemplateId = shareTemplateIdInput.value;
            const newTemplateName = shareTemplateNameInput.value.trim();
            const newTemplateDescription = shareTemplateDescInput.value.trim();

            // Basic Validation
            shareTemplateNameInput.classList.remove('is-invalid'); // Reset validation state
            if (!newTemplateName || newTemplateName.length < 3 || newTemplateName.length > 100) {
                shareTemplateNameInput.classList.add('is-invalid');
                console.warn("[ShareModal] Validation failed: Template name is required (3-100 chars).");
                return; // Stop submission
            }

            // API Call
            const shareApiUrl = '/api/v1/templates/guilds/share'; 
            const payload = {
                original_template_id: originalTemplateId,
                new_template_name: newTemplateName,
                new_template_description: newTemplateDescription,
            };

            console.log(`[ShareModal] Attempting to share template. Payload:`, payload);

            try {
                confirmShareBtn.disabled = true;
                confirmShareBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Sharing...
                `;

                // Assuming the API returns the new template info or just success
                const response = await apiRequest(shareApiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                console.log('[ShareModal] Share request successful:', response);
                showToast('success', `Template "${newTemplateName}" shared successfully!`);
                
                // TODO: Optionally refresh the template list widget if needed
                // const templateListWidgetContent = document.getElementById('widget-content-template-list');
                // if (templateListWidgetContent) {
                //     const currentGuildId = getGuildIdFromUrl(); // Needs import
                //     initializeTemplateList(templateListWidgetContent, currentGuildId); // Needs import
                // }

                shareModal.hide(); // Close modal on success

            } catch (error) {
                console.error('[ShareModal] Error sharing template:', error);
                // apiRequest handles toast
            } finally {
                confirmShareBtn.disabled = false;
                confirmShareBtn.innerHTML = 'Share Template';
                shareTemplateNameInput.classList.remove('is-invalid'); 
            }
        });

        // Optional: Clear validation state when modal is hidden
        shareModalElement.addEventListener('hidden.bs.modal', () => {
            shareTemplateNameInput.classList.remove('is-invalid');
        });

        console.log('[ShareModal] Initialization complete.');

    } else {
        console.warn('[ShareModal] Could not find all required elements for the Share Template modal logic.');
    }
}

// Function to be called from index.js to open the modal with pre-filled data
// This is called by the share button in the templateList widget.
export function openShareModal(templateId, templateName) {
     const shareModalElement = document.getElementById('shareTemplateModal');
    if (!shareModalElement) {
        console.error("[ShareModal] Share modal element (#shareTemplateModal) not found in the DOM.");
        showToast('error', 'Could not open the share dialog.');
        return;
    }

    // Ensure Bootstrap Modal class is available
    if (typeof bootstrap === 'undefined' || !bootstrap.Modal) {
        console.error('[ShareModal] Bootstrap Modal component not found.');
        showToast('error', 'Modal component failed to load.');
        return;
    }
    const bootstrapModal = bootstrap.Modal.getInstance(shareModalElement) || new bootstrap.Modal(shareModalElement);

    // Populate the modal fields
    const templateIdInput = shareModalElement.querySelector('#shareTemplateIdInput');
    const templateNameInput = shareModalElement.querySelector('#shareTemplateNameInput');
    const templateDescriptionInput = shareModalElement.querySelector('#shareTemplateDescriptionInput');

    if (templateIdInput) templateIdInput.value = templateId;
    else console.warn("[ShareModal] Share modal is missing the template ID input.");
    
    if (templateNameInput) templateNameInput.value = templateName; // Pre-fill with the original name
    else console.warn("[ShareModal] Share modal is missing the template name input.");

    if (templateDescriptionInput) templateDescriptionInput.value = ''; // Clear description on open
    else console.warn("[ShareModal] Share modal is missing the template description input.");

    // Show the modal
    bootstrapModal.show();
} 