import { apiRequest, showToast } from '/static/js/components/common/notifications.js';
import { getGuildIdFromUrl } from '../designerUtils.js'; // Needed for list refresh
import { initializeTemplateList } from '../widget/templateList.js'; // Needed for saved list refresh
import { initializeSharedTemplateList } from '../widget/sharedTemplateList.js'; // Needed for shared list refresh
import { state } from '../designerState.js'; // <-- Import state

// Variables to store modal elements found during initialization
let modalElement = null;
let confirmButton = null;
let templateNameElement = null;
let templateIdInputElement = null;
let listTypeToRefresh = 'saved'; // Default, will be updated when modal opens

/**
 * Initializes the delete confirmation modal elements and the main confirm listener.
 */
export function initializeDeleteModal() {
    modalElement = document.getElementById('deleteConfirmationModal');
    if (!modalElement) {
        console.warn("[DeleteModal] Delete confirmation modal element not found during init.");
        return;
    }

    confirmButton = modalElement.querySelector('#confirmDeleteButton');
    templateNameElement = modalElement.querySelector('#deleteTemplateName');
    templateIdInputElement = modalElement.querySelector('#deleteTemplateIdInput');
    
    if (!confirmButton || !templateNameElement || !templateIdInputElement) {
        console.error("[DeleteModal] Could not find essential elements within the delete modal during init.");
        modalElement = null; // Mark as invalid
        return;
    }

    console.log("[DeleteModal] Delete confirmation modal elements found. Adding confirm listener...");

    // --- Add the confirm listener ONCE during initialization --- 
    confirmButton.addEventListener('click', async () => {
        const templateId = templateIdInputElement.value;
        const templateName = templateNameElement.textContent; // Get name from display

        if (!templateId) {
            console.error("[DeleteModal] Template ID is missing in hidden input!");
            showToast('error', 'Cannot delete: Template ID unknown.');
            return;
        }

        console.log(`[DeleteModal] Confirm delete clicked for template ID: ${templateId}`);
        confirmButton.disabled = true;
        confirmButton.querySelector('.spinner-border').classList.remove('d-none');
        confirmButton.childNodes[confirmButton.childNodes.length - 1].textContent = ' Deleting...';

        const deleteApiUrl = `/api/v1/templates/guilds/${templateId}`;

        try {
            await apiRequest(deleteApiUrl, { method: 'DELETE' });
            showToast('success', `Template "${templateName}" deleted successfully.`);
            
            // Refresh the list type determined when the modal was opened
            refreshTemplateList(listTypeToRefresh);

            // Close the modal
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide(); 
            }

        } catch (error) {
            console.error(`[DeleteModal] Error deleting template ID ${templateId}:`, error);
            // apiRequest handles toast
             // Re-enable button on error
             confirmButton.disabled = false; 
             confirmButton.querySelector('.spinner-border').classList.add('d-none');
             confirmButton.childNodes[confirmButton.childNodes.length - 1].textContent = ' Confirm Delete';
        }
        // No finally needed, button reset happens on error or next open
    });
    // --- End Listener --- 

    // Optional: Reset button state when modal is hidden, regardless of outcome
    modalElement.addEventListener('hidden.bs.modal', () => {
         if (confirmButton) {
             confirmButton.disabled = false; 
             confirmButton.querySelector('.spinner-border').classList.add('d-none');
             confirmButton.childNodes[confirmButton.childNodes.length - 1].textContent = ' Confirm Delete';
         }
    });

    console.log("[DeleteModal] Delete confirmation modal initialized.");
}

/**
 * Opens the delete confirmation modal and sets the necessary data.
 * @param {number|string} templateId - The ID of the template to delete.
 * @param {string} templateName - The name of the template to display.
 * @param {string} listType - 'saved' or 'shared' to know which list to refresh.
 */
export function openDeleteModal(templateId, templateName, listType = 'saved') {
    // Check if initialization was successful
    if (!modalElement || !confirmButton || !templateNameElement || !templateIdInputElement) {
        console.error("[DeleteModal] Cannot open modal: elements not found or init failed.");
        showToast('error', 'Could not open delete confirmation.');
        return;
    }

    // Store the list type needed for refresh
    listTypeToRefresh = listType;

    // Update modal content
    templateNameElement.textContent = templateName;
    templateIdInputElement.value = templateId;

    // Reset button state explicitly on open as well
    confirmButton.disabled = false;
    confirmButton.querySelector('.spinner-border').classList.add('d-none');
    confirmButton.childNodes[confirmButton.childNodes.length - 1].textContent = ' Confirm Delete'; 

    // REMOVE dynamic listener attachment logic from here

    // Show the modal
    const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
    modalInstance.show();
    console.log(`[DeleteModal] Opened modal for template ID: ${templateId}, Name: ${templateName}, ListType: ${listType}`);
}

// REMOVE cleanupModalListener as listener is not added/removed dynamically anymore

// refreshTemplateList function remains the same
function refreshTemplateList(listType) {
    const guildId = getGuildIdFromUrl();
    if (!guildId) {
        console.warn("[DeleteModal] Cannot refresh list: Guild ID not found.");
        return;
    }

    let listElementId;
    let refreshFunction;

    if (listType === 'saved') {
        listElementId = 'widget-content-template-list';
        refreshFunction = initializeTemplateList;
    } else if (listType === 'shared') {
        listElementId = 'widget-content-shared-template-list';
        refreshFunction = initializeSharedTemplateList;
    } else {
        console.error(`[DeleteModal] Unknown list type for refresh: ${listType}`);
        return;
    }

    const listElement = document.getElementById(listElementId);
    if (listElement) {
        console.log(`[DeleteModal] Refreshing ${listType} template list...`);
        if(refreshFunction === initializeSharedTemplateList) {
            refreshFunction(listElement, guildId);
        } else {
            // Pass current active ID? Let's get it from state.
            const activeId = state.getActiveTemplateId(); // Need to import state
            refreshFunction(listElement, guildId, activeId); 
        }
    } else {
        console.warn(`[DeleteModal] Could not find list element #${listElementId} to refresh.`);
    }
}
