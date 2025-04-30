import { showToast } from '/static/js/components/common/notifications.js';

// Store modal elements
let modalElement = null;
let modalTitleSpan = null;
let formElement = null;
let nameInputElement = null;
let typeInputElement = null;
let parentIdInputElement = null;
let positionInputElement = null;
let confirmButton = null;

// --- NEW: Variables for Rename context ---
let isRenameMode = false;
let renameTemplateId = null;
// --- END NEW ---

/**
 * Initializes the new item input modal elements and event listeners.
 */
export function initializeNewItemInputModal() {
    modalElement = document.getElementById('newItemInputModal');
    if (!modalElement) {
        console.warn("[NewItemModal] Modal element '#newItemInputModal' not found during init.");
        return;
    }

    modalTitleSpan = modalElement.querySelector('#newItemTypeSpan');
    formElement = modalElement.querySelector('#newItemForm');
    nameInputElement = modalElement.querySelector('#newItemNameInput');
    typeInputElement = modalElement.querySelector('#newItemTypeInput');
    parentIdInputElement = modalElement.querySelector('#newItemParentIdInput');
    positionInputElement = modalElement.querySelector('#newItemPositionInput');
    confirmButton = modalElement.querySelector('#confirmNewItemButton');

    if (!modalTitleSpan || !formElement || !nameInputElement || !typeInputElement || 
        !parentIdInputElement || !positionInputElement || !confirmButton) {
        console.error("[NewItemModal] Could not find essential elements within the modal during init.");
        modalElement = null; // Mark as invalid
        return;
    }

    // Add listener for form submission
    formElement.addEventListener('submit', handleFormSubmit);

    // Optional: Clear validation state when modal is hidden
    modalElement.addEventListener('hidden.bs.modal', () => {
        formElement.classList.remove('was-validated');
        nameInputElement.classList.remove('is-invalid');
        nameInputElement.value = ''; // Clear input
    });

    console.log("[NewItemModal] New item input modal initialized.");
}

/**
 * Opens the new item input modal and sets context.
 * @param {string} itemType - The type of item being added (e.g., 'category', 'text_channel').
 * @param {string|null} parentNodeId - The jsTree ID of the parent node ('category_123', 'template_root') or null.
 * @param {number} position - The desired position among siblings.
 */
export function openNewItemInputModal(itemType, parentNodeId, position) {
    if (!modalElement) {
        console.error("[NewItemModal] Cannot open modal: elements not found or init failed.");
        showToast('error', 'Could not open item input form.');
        return;
    }

    // Clean up type string for display
    let displayType = itemType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()); 
    if (displayType.endsWith('Channel')) displayType = displayType.replace(' Channel', ''); // Shorten 'Text Channel' to 'Text'

    // Set modal content
    modalTitleSpan.textContent = displayType;
    typeInputElement.value = itemType;
    parentIdInputElement.value = parentNodeId || ''; // Store parent jsTree ID
    positionInputElement.value = position;
    nameInputElement.value = ''; // Clear previous input
    nameInputElement.focus(); // Focus the name input

    // Show the modal
    const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
    modalInstance.show();
    console.log(`[NewItemModal] Opened for type: ${itemType}, parent: ${parentNodeId}, position: ${position}`);
}

// --- NEW: Function to open the modal specifically for renaming a template ---
export function openRenameTemplateModal(templateId, currentName) {
    if (!modalElement) {
        console.error("[NewItemModal] Cannot open modal for rename: elements not found or init failed.");
        showToast('error', 'Could not open rename form.');
        return;
    }

    // Set rename context
    isRenameMode = true;
    renameTemplateId = templateId;

    // Set modal content for renaming
    modalTitleSpan.textContent = 'Template'; // Keep it simple
    modalElement.querySelector('.modal-title').childNodes[0].nodeValue = 'Rename '; // Change main title
    nameInputElement.value = currentName; // Pre-fill with current name
    
    // Clear/hide fields not needed for renaming
    typeInputElement.value = 'template_rename'; // Special type to identify in submit handler
    parentIdInputElement.value = '';
    positionInputElement.value = '';
    // Optionally hide parent/position fields visually if desired
    
    nameInputElement.focus(); // Focus the name input

    // --- NEW: Change button text for rename mode ---
    if (confirmButton) confirmButton.textContent = 'Rename Template';
    // --- END NEW ---

    // Show the modal
    const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
    modalInstance.show();
    console.log(`[NewItemModal] Opened in RENAME mode for template ID: ${templateId}, Current Name: ${currentName}`);
}
// --- END NEW ---

/**
 * Handles the form submission within the modal.
 * Validates input and dispatches an event with the new item details.
 * @param {Event} event - The form submission event.
 */
function handleFormSubmit(event) {
    event.preventDefault();
    event.stopPropagation();

    formElement.classList.add('was-validated');

    if (!formElement.checkValidity()) {
        console.warn("[NewItemModal] Form validation failed.");
        nameInputElement.classList.add('is-invalid'); // Ensure invalid style is shown
        return;
    }

    // Validation passed, gather data
    const newName = nameInputElement.value.trim();

    // --- MODIFIED: Check if in rename mode --- 
    if (isRenameMode && renameTemplateId !== null) {
        console.log("[NewItemModal] Form submitted in RENAME mode.");
        // Dispatch rename event
        document.dispatchEvent(new CustomEvent('renameTemplateConfirmed', {
            detail: {
                templateId: renameTemplateId,
                newName: newName
            }
        }));
        console.log(`[NewItemModal] Dispatched 'renameTemplateConfirmed' for ID: ${renameTemplateId}, New Name: ${newName}`);
    } else {
        console.log("[NewItemModal] Form submitted in NEW ITEM mode.");
        // Original logic for adding new items
        const newItemData = {
            itemType: typeInputElement.value,
            itemName: newName, // Use already trimmed name
            parentNodeId: parentIdInputElement.value || null, // Send null if empty string
            position: parseInt(positionInputElement.value, 10)
        };
        console.log("[NewItemModal] Dispatching 'newItemConfirmed':", newItemData);
        document.dispatchEvent(new CustomEvent('newItemConfirmed', { detail: newItemData }));
    }
    // --- END MODIFICATION ---

    // Close the modal
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
        modalInstance.hide();
    }
    
    // --- Reset rename mode flag after closing --- 
    isRenameMode = false;
    renameTemplateId = null;
    // Reset title back to default?
    modalElement.querySelector('.modal-title').childNodes[0].nodeValue = 'Add New ';
    // --- NEW: Reset button text --- 
    if (confirmButton) confirmButton.textContent = 'Add Item';
    // --- END NEW ---
}

// Initial log
console.log("[NewItemInputModal] Modal module loaded."); 