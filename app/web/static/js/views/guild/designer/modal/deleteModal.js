import { apiRequest, showToast } from '/static/js/components/common/notifications.js';
import { getGuildIdFromUrl } from '../designerUtils.js'; // Needed for list refresh
import { initializeTemplateList } from '../widget/templateList.js'; // Needed for saved list refresh
import { initializeSharedTemplateList } from '../widget/sharedTemplateList.js'; // Needed for shared list refresh
import { state } from '../designerState.js'; // <-- Import state

// Variables to store modal elements found during initialization
let modalElement = null;
let modalTitleElement = null;
let modalBodyTextElement = null;
let confirmButton = null;
let itemNameElement = null;
let itemIdInputElement = null;
let currentItemType = 'template'; // Default to template, updated on open
let currentItemId = null; // Store ID separately
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

    modalTitleElement = modalElement.querySelector('#deleteConfirmationModalLabel');
    modalBodyTextElement = modalElement.querySelector('.modal-body p:first-of-type');
    confirmButton = modalElement.querySelector('#confirmDeleteButton');
    itemNameElement = modalElement.querySelector('#deleteItemName');
    itemIdInputElement = modalElement.querySelector('#deleteItemIdInput');
    
    if (!confirmButton || !itemNameElement || !itemIdInputElement || !modalTitleElement || !modalBodyTextElement) {
        console.error("[DeleteModal] Could not find essential elements within the delete modal during init.", {
             confirmButton, itemNameElement, itemIdInputElement, modalTitleElement, modalBodyTextElement
        });
        modalElement = null; // Mark as invalid
        return;
    }

    console.log("[DeleteModal] Delete confirmation modal elements found. Adding confirm listener...");

    // --- Add the confirm listener ONCE during initialization --- 
    confirmButton.addEventListener('click', async () => {
        const itemId = currentItemId;
        const itemType = currentItemType;
        const itemName = itemNameElement.textContent;
        const guildId = getGuildIdFromUrl();

        if (itemId === null || itemId === undefined) {
            console.error("[DeleteModal] Item ID is missing!");
            showToast('error', 'Cannot delete: Item ID unknown.');
            return;
        }

        // Check if guildId is available (needed for most deletes now)
        if (!guildId) {
            console.error("[DeleteModal] Guild ID is missing! Cannot construct URL.");
            showToast('error', 'Cannot delete: Guild context unknown.');
            return;
        }

        console.log(`[DeleteModal] Confirm delete clicked for Item Type: ${itemType}, ID: ${itemId}, Guild ID: ${guildId}`);
        confirmButton.disabled = true;
        confirmButton.querySelector('.spinner-border').classList.remove('d-none');
        confirmButton.childNodes[confirmButton.childNodes.length - 1].textContent = ' Deleting...';

        // --- Determine API URL based on itemType ---
        let deleteApiUrl = '';
        let itemTypeNameForMsg = 'Item';

        if (itemType === 'template' || itemType === 'saved' || itemType === 'shared') {
             deleteApiUrl = `/api/v1/guilds/${guildId}/template/${itemId}`;
             itemTypeNameForMsg = 'Template';
        } else if (itemType === 'designer_category') {
             deleteApiUrl = `/api/v1/guilds/${guildId}/template/categories/${itemId}`;
             itemTypeNameForMsg = 'Category';
        } else if (itemType === 'designer_channel') {
             deleteApiUrl = `/api/v1/guilds/${guildId}/template/channels/${itemId}`;
             itemTypeNameForMsg = 'Channel';
        } else {
            console.error(`[DeleteModal] Unknown item type for deletion: ${itemType}`);
            showToast('error', `Cannot delete: Unknown item type '${itemType}'.`);
            // Reset button state
            confirmButton.disabled = false; 
            confirmButton.querySelector('.spinner-border').classList.add('d-none');
            confirmButton.childNodes[confirmButton.childNodes.length - 1].textContent = ' Confirm Delete';
            return; // Stop execution
        }
        console.log(`[DeleteModal] Determined API URL: ${deleteApiUrl}`);
        // --------------------------------------------

        try {
            await apiRequest(deleteApiUrl, { method: 'DELETE' });
            showToast('success', `${itemTypeNameForMsg} "${itemName}" deleted successfully.`);
            
            // --- Handle Post-Deletion Action ---
            handleSuccessfulDeletion(itemType, itemId);
            // -----------------------------------

            // Close the modal
            closeModal();
        } catch (error) {
            console.error(`[DeleteModal] Error deleting ${itemType} ID ${itemId}:`, error);
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
 * @param {number|string} itemId - The ID of the item to delete.
 * @param {string} itemName - The name of the item to display.
 * @param {string} itemType - 'template', 'saved', 'shared', 'designer_category', 'designer_channel'.
 */
export function openDeleteModal(itemId, itemName, itemType = 'template') {
    // Check if initialization was successful
    if (!modalElement || !confirmButton || !itemNameElement || !itemIdInputElement || !modalTitleElement || !modalBodyTextElement) {
        console.error("[DeleteModal] Cannot open modal: elements not found or init failed.");
        showToast('error', 'Could not open delete confirmation.');
        return;
    }

    // Store item details for the confirm handler
    currentItemId = itemId;
    currentItemType = itemType;

    // Update modal content
    itemNameElement.textContent = itemName;
    itemIdInputElement.value = itemId; // Still set the hidden input, though we use stored value now

    // --- Update Title and Body Text Dynamically ---
    let titleText = 'Confirm Deletion';
    let bodyText = 'Are you sure you want to permanently delete:';
    if (itemType === 'designer_category') {
        titleText = 'Confirm Category Deletion';
        bodyText = 'Are you sure you want to permanently delete the category:';
    } else if (itemType === 'designer_channel') {
        titleText = 'Confirm Channel Deletion';
        bodyText = 'Are you sure you want to permanently delete the channel:';
    } else if (itemType === 'saved' || itemType === 'shared' || itemType === 'template') {
         titleText = 'Confirm Template Deletion';
         bodyText = 'Are you sure you want to permanently delete the template:';
    }
    modalTitleElement.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i>${titleText}`; // Keep icon
    modalBodyTextElement.textContent = bodyText;
    // ---------------------------------------------

    // Reset button state explicitly on open as well
    confirmButton.disabled = false;
    confirmButton.querySelector('.spinner-border').classList.add('d-none');
    confirmButton.childNodes[confirmButton.childNodes.length - 1].textContent = ' Confirm Delete'; 

    // Show the modal
    const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
    modalInstance.show();
    console.log(`[DeleteModal] Opened modal for Item Type: ${itemType}, ID: ${itemId}, Name: ${itemName}`);
}

// Helper: Close Modal
function closeModal() {
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
        modalInstance.hide(); 
    }
}

// Helper: Handle successful deletion
function handleSuccessfulDeletion(itemType, itemId) {
    console.log(`[DeleteModal] Handling successful deletion of ${itemType} ID: ${itemId}`);
    if (itemType === 'saved' || itemType === 'shared' || itemType === 'template') {
        // Refresh the appropriate template list
        refreshTemplateList(itemType); 
    } else if (itemType === 'designer_category' || itemType === 'designer_channel') {
        // Dispatch event for the designer UI to handle (remove node from tree/lists)
        document.dispatchEvent(new CustomEvent('designerElementDeleted', {
            detail: { itemType: itemType, itemId: itemId }
        }));
        // Also mark state as dirty since the structure changed
        state.setDirty(true);
        console.log(`[DeleteModal] Dispatched 'designerElementDeleted' for ${itemType} ${itemId}`);
    }
}

// refreshTemplateList function remains the same
function refreshTemplateList(listType) {
    const guildId = getGuildIdFromUrl();
    if (!guildId) {
        console.warn("[DeleteModal] Cannot refresh list: Guild ID not found.");
        return;
    }

    let listElementId;
    let refreshFunction;
    let actualListType = listType; // Use a separate var in case we adjusted itemType

    if (actualListType === 'saved' || actualListType === 'template') { // Treat template as saved
        listElementId = 'widget-content-template-list';
        refreshFunction = initializeTemplateList;
    } else if (actualListType === 'shared') {
        listElementId = 'widget-content-shared-template-list';
        refreshFunction = initializeSharedTemplateList;
    } else {
        console.error(`[DeleteModal] Unknown list type for refresh: ${actualListType}`);
        return;
    }

    const listElement = document.getElementById(listElementId);
    if (listElement) {
        console.log(`[DeleteModal] Refreshing ${actualListType} template list...`);
        if(refreshFunction === initializeSharedTemplateList) {
            refreshFunction(listElement, guildId);
        } else {
            // Pass current active ID? Let's get it from state.
            const activeId = state.getActiveTemplateId(); // Use state
            refreshFunction(listElement, guildId, activeId); 
        }
    } else {
        console.warn(`[DeleteModal] Could not find list element #${listElementId} to refresh.`);
    }
}
