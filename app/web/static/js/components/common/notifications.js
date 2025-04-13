// Notification Utilities
// Custom Error for API Requests
class ApiError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data; // Store the parsed error data if available
    }
}

const showToast = (type, message) => {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    const container = document.getElementById('toast-container');
    if (!container) {
        const newContainer = document.createElement('div');
        newContainer.id = 'toast-container';
        newContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(newContainer);
    }
    
    const toastContainer = document.getElementById('toast-container');
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
};

// API Request Utilities
const apiRequest = async (endpoint, options = {}) => {
    let response; // Define response outside try block to access in catch
    try {
        response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            credentials: 'same-origin'
        });

        if (response.status === 204) {
            console.log(`apiRequest: Received status ${response.status}, returning null.`);
            return null;
        }

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/auth/login';
                return;
            }

            let errorData = null; // Initialize errorData
            let errorMessage = `API request failed with status ${response.status}`;
            try {
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.indexOf("application/json") !== -1) {
                    errorData = await response.json(); // Store parsed data
                    if (errorData && errorData.detail) {
                        if (typeof errorData.detail === 'string') {
                            errorMessage = errorData.detail;
                        } else {
                            errorMessage = JSON.stringify(errorData.detail);
                        }
                    } else if (errorData && errorData.message) {
                        errorMessage = errorData.message;
                    }
                } else {
                    const textData = await response.text(); // Store text data
                    errorData = textData; // Assign text data to errorData
                    if (textData) {
                        errorMessage = textData;
                    }
                }
            } catch (parseError) {
                console.warn("Could not parse error response body:", parseError);
                try {
                    // Try to get raw text as fallback message
                    const rawText = await response.text(); 
                    errorData = rawText; // Assign raw text to errorData
                    if (rawText) errorMessage = rawText.substring(0, 500); 
                } catch (textError) { 
                    console.warn("Could not get raw text from error response:", textError);
                    // Keep the default status message if text fails
                 }
            }
            
            // Throw the custom ApiError with status and data
            throw new ApiError(errorMessage, response.status, errorData);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error in apiRequest:", error);
        
        // Use ApiError properties if available for the toast
        const displayMessage = (error instanceof ApiError) 
            ? `${error.message} (Status: ${error.status})`
            : (error instanceof Error ? error.message : String(error));
            
        showToast('error', displayMessage.substring(0, 500));
        throw error; // Re-throw the original error (could be ApiError or other)
    }
};

// Date/Time Utilities
const formatDateTime = (date) => {
    return new Date(date).toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

const formatDuration = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    const parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (remainingSeconds > 0 || parts.length === 0) parts.push(`${remainingSeconds}s`);
    
    return parts.join(' ');
};

// Export utilities for use in other modules
export {
    showToast,
    apiRequest,
    formatDateTime,
    formatDuration,
    ApiError // Export the custom error class too
}; 