import { showToast } from '/static/js/components/common/notifications.js';

let activateModalInstance = null;
let confirmActivateButton = null;
let templateIdToActivate = null;

function handleConfirmActivation() {
    if (templateIdToActivate !== null) {
        console.log(`[ActivateModal] Confirming activation for template ID: ${templateIdToActivate}`);
        // Dispatch a custom event with the template ID
        document.dispatchEvent(new CustomEvent('activateConfirmed', {
            detail: { templateId: templateIdToActivate }
        }));
        activateModalInstance.hide();
    } else {
        console.error("[ActivateModal] Template ID to activate is null on confirmation.");
        showToast('error', 'Could not confirm activation: template ID missing.');
    }
}

export function initializeActivateConfirmModal() {
    const modalElement = document.getElementById('activateConfirmModal');
    if (!modalElement) {
        console.error("[ActivateModal] Activate confirmation modal element (#activateConfirmModal) not found.");
        return;
    }

    // Ensure Bootstrap is loaded before creating modal instance
    if (typeof bootstrap === 'undefined' || !bootstrap.Modal) {
         console.error("[ActivateModal] Bootstrap Modal component not found. Make sure Bootstrap JS is loaded.");
         return;
    }

    activateModalInstance = new bootstrap.Modal(modalElement);
    confirmActivateButton = document.getElementById('confirmActivateBtn');
    const templateNameElement = document.getElementById('activateTemplateName');

    if (!confirmActivateButton || !templateNameElement) {
        console.error("[ActivateModal] Modal confirmation button (#confirmActivateBtn) or name element (#activateTemplateName) not found.");
        activateModalInstance = null; // Prevent usage if elements are missing
        return;
    }

    confirmActivateButton.addEventListener('click', handleConfirmActivation);
    console.log("[ActivateModal] Activation confirmation modal initialized.");
}

export function openActivateConfirmModal(templateId, templateName) {
    if (!activateModalInstance) {
        console.error("[ActivateModal] Cannot open modal: it was not initialized correctly.");
        showToast('error', 'Could not open activation confirmation.');
        return;
    }
    if (templateId === undefined || templateId === null || !templateName) {
         console.error("[ActivateModal] Cannot open modal: templateId or templateName is missing.", {templateId, templateName});
         showToast('error', 'Missing template details for activation.');
         return;
    }

    templateIdToActivate = templateId;
    const templateNameElement = document.getElementById('activateTemplateName');
    templateNameElement.textContent = templateName; // Set the name in the modal body

    console.log(`[ActivateModal] Opening confirmation modal for template: ${templateName} (ID: ${templateId})`);
    activateModalInstance.show();
} 