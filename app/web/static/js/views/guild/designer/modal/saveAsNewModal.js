import { showToast } from "/static/js/components/common/notifications.js";

/**
 * Initializes the "Save As New Template" modal functionality.
 * Sets up event listeners for the modal's save button.
 */
export function initializeSaveAsNewModal() {
    console.log("[SaveAsNewModal] Initializing...");

    const saveAsModalElement = document.getElementById('saveAsNewTemplateModal');
    const saveAsNewButton = document.getElementById('confirmSaveAsNewButton');
    const newNameInput = document.getElementById('newTemplateNameInput');
    const newDescriptionInput = document.getElementById('newTemplateDescriptionInput');

    // --- DEBUG: Check if button element exists at initialization time ---
    if (saveAsNewButton) {
        console.log("[SaveAsNewModal] Found 'confirmSaveAsNewButton' during initialization.");
    } else {
        console.error("[SaveAsNewModal] DID NOT FIND 'confirmSaveAsNewButton' during initialization!");
    }
    // --- END DEBUG ---

    if (!saveAsModalElement || !saveAsNewButton || !newNameInput || !newDescriptionInput) {
        console.error('[SaveAsNewModal] Critical modal elements not found. Initialization failed.');
        return;
    }

    // Listener for the CONFIRM action within the modal
    saveAsNewButton.addEventListener('click', () => {
        // --- DEBUG: Check if listener is firing --- 
        console.log("[SaveAsNewModal] \'confirmSaveAsNewButton\' CLICKED!"); 
        // -------------------------------------------
        
        const newName = newNameInput.value.trim();
        const newDescription = newDescriptionInput.value.trim();

        // --- Basic Validation --- 
        if (!newName) {
            showToast('warning', 'New template name cannot be empty.');
            newNameInput.focus();
            return;
        }
        if (newName.length > 100) {
             showToast('warning', 'Template name cannot exceed 100 characters.');
             newNameInput.focus();
             return;
        }
        // --- End Validation ---

        // Disable button temporarily
        saveAsNewButton.disabled = true;
        saveAsNewButton.innerHTML = ` 
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Processing...
        `;

        // --- Dispatch event to index.js --- 
        console.log(`[SaveAsNewModal] Dispatching saveAsNewConfirmed event with name: ${newName}`);
        document.dispatchEvent(new CustomEvent('saveAsNewConfirmed', {
            detail: {
                newName: newName,
                newDescription: newDescription
            }
        }));
        // --- End Dispatch --- 

        // Close the modal AFTER dispatching the event
        const modalInstance = bootstrap.Modal.getInstance(saveAsModalElement);
        if (modalInstance) {
            modalInstance.hide();
        }

        // Restore button state AFTER hiding or immediately after dispatch
        // Doing it here ensures it resets even if index.js fails later
        saveAsNewButton.disabled = false;
        saveAsNewButton.innerHTML = 'Save New Template';

    });

    console.log("[SaveAsNewModal] Initialization complete.");
}


// Helper function to trigger the modal display externally (e.g., from index.js catch block)
export function openSaveAsNewModal(suggestedName) {
     const saveAsNewModalElement = document.getElementById('saveAsNewTemplateModal');
     if (!saveAsNewModalElement) {
         console.error("[SaveAsNewModal] Save As New modal element (#saveAsNewTemplateModal) not found!");
         showToast('error', "Cannot open 'Save As New' dialog.");
         return;
     }
     if (typeof bootstrap === 'undefined' || !bootstrap.Modal) {
         console.error('[SaveAsNewModal] Bootstrap Modal component not found.');
         showToast('error', 'Modal component failed to load.');
         return;
     }
     const saveAsNewModalInstance = bootstrap.Modal.getInstance(saveAsNewModalElement) || new bootstrap.Modal(saveAsNewModalElement);
     
     const newNameInput = saveAsNewModalElement.querySelector('#newTemplateNameInput');
     if (newNameInput) newNameInput.value = suggestedName ? String(suggestedName).substring(0, 100) : '';
     
     const newDescInput = saveAsNewModalElement.querySelector('#newTemplateDescriptionInput');
     if (newDescInput) newDescInput.value = ''; 
      
     saveAsNewModalInstance.show();
}
