// Sets up global window error handlers (onerror, onunhandledrejection) 
// to capture JavaScript errors and store them.

/**
 * Sets up global error handlers that store captured errors in the provided array
 * and optionally trigger a callback.
 * @param {Array} errorStorage - The array where captured errors should be stored.
 * @param {number} maxErrors - The maximum number of errors to store.
 * @param {Function} [onCaptureCallback] - Optional callback function to execute after an error is captured.
 */
export function setupGlobalErrorHandlers(errorStorage, maxErrors, onCaptureCallback) {
    const storeError = (errorData) => {
        // Add timestamp
        errorData.timestamp = new Date().toISOString();
        // Add error to the beginning of the array
        errorStorage.unshift(errorData);
        // Limit array size
        if (errorStorage.length > maxErrors) {
            errorStorage.pop();
        }
        console.warn("StateBridge captured JS Error:", errorData); // Log captured error

        // Trigger the callback if provided
        if (typeof onCaptureCallback === 'function') {
            try {
                onCaptureCallback(errorData); // Pass the captured error data to the callback
            } catch (callbackError) {
                console.error("Error executing onCaptureCallback:", callbackError);
            }
        }
    };

    // Handle synchronous errors
    window.onerror = (message, source, lineno, colno, error) => {
        storeError({
            type: 'onerror',
            message: message,
            source: source,
            lineno: lineno,
            colno: colno,
            stack: error ? error.stack : null
        });
        // Return false to allow default browser error handling
        return false; 
    };

    // Handle unhandled promise rejections
    window.onunhandledrejection = (event) => {
        let reason = event.reason;
        let errorDetails = {};

        if (reason instanceof Error) {
            errorDetails = {
                message: reason.message,
                stack: reason.stack
            };
        } else {
            // Handle cases where the rejection reason is not an Error object
            try {
                errorDetails.message = JSON.stringify(reason);
            } catch {
                errorDetails.message = String(reason);
            }
            errorDetails.stack = null;
        }
        
        storeError({
            type: 'onunhandledrejection',
            ...errorDetails
        });
        // Prevent default browser handling if needed (usually not necessary)
        // event.preventDefault(); 
    };
    
    console.info("StateBridge global error handlers initialized.");
}
