/**
 * modalComponent.js: A simple promise-based confirmation modal.
 */
class ConfirmModal {
    constructor() {
        this.modalElement = null;
        this.resolvePromise = null;
        this._createModalDOM();
    }

    _createModalDOM() {
        // Create modal structure using Bootstrap classes for basic layout
        this.modalElement = document.createElement('div');
        this.modalElement.className = 'modal fade custom-confirm-modal'; // Base Bootstrap class + custom
        this.modalElement.tabIndex = -1;
        this.modalElement.setAttribute('aria-labelledby', 'confirmModalLabel');
        this.modalElement.setAttribute('aria-hidden', 'true');
        this.modalElement.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="confirmModalLabel">Confirmation</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p id="confirmModalMessage">Are you sure?</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="confirmModalCancel">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmModalConfirm">OK</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.modalElement);

        // Get references to dynamic parts
        this.titleElement = this.modalElement.querySelector('.modal-title');
        this.messageElement = this.modalElement.querySelector('#confirmModalMessage');
        this.confirmButton = this.modalElement.querySelector('#confirmModalConfirm');
        this.cancelButton = this.modalElement.querySelector('#confirmModalCancel');
        this.closeButton = this.modalElement.querySelector('.btn-close');

        // Add event listeners
        this.confirmButton.addEventListener('click', () => this._handleConfirm());
        this.cancelButton.addEventListener('click', () => this._handleCancel());
        this.closeButton.addEventListener('click', () => this._handleCancel());
        
        // Handle backdrop click (using Bootstrap's event system indirectly via data-bs-dismiss)
        // If not using Bootstrap JS, manual backdrop click handling would be needed.
        // For simplicity, assume Bootstrap JS handles modal dismissal.
    }

    show(options = {}) {
        return new Promise((resolve) => {
            this.resolvePromise = resolve;

            // Update modal content
            this.titleElement.textContent = options.title || 'Confirmation';
            this.messageElement.textContent = options.message || 'Are you sure?';
            this.confirmButton.textContent = options.confirmText || 'OK';
            this.cancelButton.textContent = options.cancelText || 'Cancel';

            // Show the modal using Bootstrap's JS API if available, otherwise basic show/hide
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                 // Ensure we have a Bootstrap Modal instance
                 if (!this.bootstrapModal) {
                     this.bootstrapModal = new bootstrap.Modal(this.modalElement);
                 }
                 this.bootstrapModal.show();
            } else {
                console.warn('Bootstrap Modal JS not found. Using basic show/hide.');
                this.modalElement.style.display = 'block';
                this.modalElement.classList.add('show');
                document.body.classList.add('modal-open'); // Simulate Bootstrap behavior
            }
        });
    }

    _hide() {
         if (this.bootstrapModal) {
             this.bootstrapModal.hide();
         } else {
             this.modalElement.style.display = 'none';
             this.modalElement.classList.remove('show');
             document.body.classList.remove('modal-open');
         }
    }

    _handleConfirm() {
        if (this.resolvePromise) {
            this.resolvePromise(true);
        }
        this._hide();
        this.resolvePromise = null; // Reset promise
    }

    _handleCancel() {
        if (this.resolvePromise) {
            this.resolvePromise(false);
        }
        this._hide();
        this.resolvePromise = null; // Reset promise
    }
}

// --- Global Registration ---
// Ensure UIComponents namespace exists
window.UIComponents = window.UIComponents || {};

// Create a singleton instance of the modal
const confirmModalInstance = new ConfirmModal();

// Expose the show method globally
window.UIComponents.showConfirmModal = (options) => {
    return confirmModalInstance.show(options);
};

console.info('Custom ConfirmModal registered under window.UIComponents.showConfirmModal'); 