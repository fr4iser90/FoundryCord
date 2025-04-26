// Handles the user approval workflow for state collectors.
import { saveApprovedCollectors } from './bridge_storage.js';

/**
 * Displays an approval dialog to the user using window.confirm as a fallback.
 * @param {string} collectorName - Name of the collector.
 * @param {string} description - Description of what will be collected.
 * @returns {Promise<boolean>} - Whether approval was granted.
 * @private
 */
async function showApprovalDialog(collectorName, description) {
    return new Promise(resolve => {
        // Check if we have a custom modal component (placeholder)
        if (window.UIComponents && window.UIComponents.showConfirmModal) {
            window.UIComponents.showConfirmModal({
                title: 'Allow State Collection',
                message: `The application is requesting permission to collect state information: ${description}`,
                confirmText: 'Approve',
                cancelText: 'Deny',
                onConfirm: () => resolve(true),
                onCancel: () => resolve(false)
            });
            return;
        }
        
        // Fallback to browser confirm
        const approved = window.confirm(
            `The application is requesting permission to collect the following state information:\n\n` +
            `${description}\n\n` +
            `Do you approve?`
        );
        
        resolve(approved);
    });
}

/**
 * Request user approval for a specific collector if needed.
 * Handles pending states and updates the approved collectors set.
 * @param {string} name - Name of the collector.
 * @param {Object} collectorsRegistry - The registry of all collectors.
 * @param {Set<string>} approvedCollectorsSet - The current set of approved collectors.
 * @param {Object} pendingApprovalsMap - A map to track pending approval requests.
 * @returns {Promise<boolean>} - Whether the collector is now approved (or didn't need approval).
 */
export async function requestApproval(name, collectorsRegistry, approvedCollectorsSet, pendingApprovalsMap) {
    if (!collectorsRegistry[name]) {
        console.warn(`Cannot request approval for unknown collector: ${name}`);
        return false;
    }
    
    const collector = collectorsRegistry[name];
    
    // No approval needed
    if (!collector.options.requiresApproval) {
        return true; 
    }
    
    // Already approved
    if (approvedCollectorsSet.has(name)) {
        return true; 
    }
    
    // Check if recently requested (within 30s)
    if (pendingApprovalsMap[name]) {
        if (Date.now() - pendingApprovalsMap[name].requestedAt < 30000) {
            console.debug(`Approval for ${name} already pending.`);
            return false; // Still waiting
        }
    }
    
    // Mark as pending for this request cycle
    pendingApprovalsMap[name] = {
        requestedAt: Date.now(),
        status: 'pending'
    };
    
    // Show dialog
    console.info(`Showing approval dialog for: ${name}`);
    const approved = await showApprovalDialog(name, collector.options.description);
    
    if (approved) {
        approvedCollectorsSet.add(name);
        saveApprovedCollectors(approvedCollectorsSet); // Save to localStorage
        pendingApprovalsMap[name].status = 'approved';
        console.info(`Collector ${name} approved by user.`);
        return true;
    } else {
        pendingApprovalsMap[name].status = 'rejected';
        console.info(`Collector ${name} rejected by user.`);
        return false;
    }
}
