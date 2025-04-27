// Handles the user approval workflow for state collectors.
import { saveApprovedCollectors } from './bridgeStorage.js';

/**
 * Displays an approval dialog to the user.
 * Uses window.UIComponents.showConfirmModal if available, otherwise falls back to window.confirm.
 * @param {string} collectorName - Name of the collector.
 * @param {string} description - Description of what will be collected.
 * @returns {Promise<boolean>} - Whether approval was granted.
 * @private
 */
async function showApprovalDialog(collectorName, description) {
    // Check if we have a custom modal component
    if (window.UIComponents && window.UIComponents.showConfirmModal) {
        try {
            // Directly await the promise returned by the custom modal
            // Ensure the message includes the collector name(s) for clarity
            const approved = await window.UIComponents.showConfirmModal({
                title: 'Allow State Collection',
                message: `The application requests permission for:\n${description}`,
                confirmText: 'Approve',
                cancelText: 'Deny'
            });
            return approved; // boolean true or false
        } catch (error) {
            console.error("Error showing custom confirm modal:", error);
            // Fall through to browser confirm if custom modal fails
        }
    }
    
    // Fallback to browser confirm
    console.warn("Using fallback window.confirm for approval.");
    // Ensure the message includes the collector name(s) for clarity
    const message = `The application is requesting permission for:\n\n${description}\n\nDo you approve?`;
    const approved = window.confirm(message);

    return approved;
}

/**
 * Request user approval if needed.
 * Handles single collector names or an array for batch approval.
 * @param {string|Array<string>} nameOrNames - Name of the single collector OR an array of names for batch approval.
 * @param {Object} collectorsRegistry - The registry of all collectors.
 * @param {Set<string>} approvedCollectorsSet - The current set of approved collectors.
 * @param {Object} pendingApprovalsMap - A map to track pending approval requests (currently unused after refactor).
 * @returns {Promise<boolean>} - Whether the collector(s) are now approved.
 */
export async function requestApproval(nameOrNames, collectorsRegistry, approvedCollectorsSet, pendingApprovalsMap) {
   // --- DEBUG LOG --- 
   console.debug("[requestApproval] Called with:", nameOrNames, "Approved set:", Array.from(approvedCollectorsSet));
   // --- END DEBUG LOG ---
   
   const namesToApprove = Array.isArray(nameOrNames) ? nameOrNames : [nameOrNames];
   const validNamesToRequest = [];
   const descriptions = [];

   // Validate names and collect descriptions for those needing approval
   for (const name of namesToApprove) {
       if (!collectorsRegistry[name]) {
           console.warn(`Cannot request approval for unknown collector: ${name}`);
           continue; // Skip unknown collectors
       }
       const collector = collectorsRegistry[name];
       // Only proceed if it requires approval and isn't already approved
       if (collector.options.requiresApproval && !approvedCollectorsSet.has(name)) {
           validNamesToRequest.push(name);
           descriptions.push(`- ${collector.options.description || name}`); // Collect descriptions for the dialog
       }
   }

   // If no valid collectors need approval from the list, return true (all were either auto-approved or already approved)
   if (validNamesToRequest.length === 0) {
       console.debug("No collectors in the batch require approval.");
       return true;
   }
   
   // --- Show ONE Dialog for Batch Approval --- 
   const combinedDescription = descriptions.join('\n');
   const dialogTitle = validNamesToRequest.length > 1 ? 'Multiple Collectors' : validNamesToRequest[0];
   console.info(`Showing approval dialog for: ${validNamesToRequest.join(', ')}`);
   
   // Use the improved showApprovalDialog which handles custom modal promises
   const approved = await showApprovalDialog(dialogTitle, combinedDescription); 
   
   if (approved) {
       // Add all requested collectors to the approved set
       validNamesToRequest.forEach(name => approvedCollectorsSet.add(name));
       saveApprovedCollectors(approvedCollectorsSet); // Save updated set to localStorage
       console.info(`User approved collectors: ${validNamesToRequest.join(', ')}`);
       return true;
   } else {
       console.info(`User rejected approval for: ${validNamesToRequest.join(', ')}`);
       return false;
   }
}
