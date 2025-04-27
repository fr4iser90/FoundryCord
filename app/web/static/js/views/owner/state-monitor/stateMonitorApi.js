/**
 * stateMonitorApi.js: Handles API interactions and data fetching for the State Monitor.
 */
import stateBridge from '/static/js/core/state-bridge/bridgeMain.js';

// Import setStatus function from the UI module to replicate original behavior
import { setStatus } from './stateMonitorUi.js'; 
// Import rendering functions needed by API calls based on original structure
import { renderCollectorPanel, renderResults, renderSummaryPanel } from './stateMonitorRenderer.js';

/**
 * Loads available collectors from the backend and browser.
 * Corresponds to the original loadAvailableCollectors method.
 * @param {object} instance - The StateMonitorDashboard instance.
 */
export async function loadAvailableCollectors(instance) {
    try {
        // Call setStatus via the imported function, passing the instance's UI element
        setStatus(instance.ui.statusDisplay, 'Loading collectors...'); 
        
        // Original fetch logic
        const response = await fetch(`/api/v1/owner/state/collectors?scope=${instance.currentScope}`);
        if (!response.ok) {
            let errorBody = await response.text();
            console.error("API Response Error Body:", errorBody);
            throw new Error(`Server responded with ${response.status}: ${response.statusText}. Body: ${errorBody.substring(0, 100)}...`);
        }
        const collectors = await response.json();
        
        // Original browser collector logic
        const browserCollectors = Object.keys(stateBridge.collectors).map(name => {
            const collector = stateBridge.collectors[name];
            return {
                name,
                description: collector.options.description,
                requires_approval: collector.options.requiresApproval,
                scope: collector.options.scope,
                is_approved: stateBridge.approvedCollectors.has(name)
            };
        });
        
        // Update instance state directly (as in original)
        instance.collectors = {
            server: collectors,
            browser: browserCollectors
        };
        
        // Call renderer via imported function, passing instance (as in original)
        renderCollectorPanel(instance);
        // Call setStatus via imported function (as in original)
        setStatus(instance.ui.statusDisplay, 'Ready'); 
    } catch (error) {
        console.error('Error loading collectors:', error);
         // Call setStatus via imported function (as in original)
        setStatus(instance.ui.statusDisplay, `Error: ${error.message}`, 'error');
    }
}

/**
 * Captures a state snapshot from server and browser.
 * Corresponds to the original captureSnapshot method.
 * @param {object} instance - The StateMonitorDashboard instance.
 */
export async function captureSnapshot(instance) {
    try {
         // Call setStatus via imported function
        setStatus(instance.ui.statusDisplay, 'Capturing state snapshot...');
        
        // Original logic to get selected collectors
        const serverCollectors = Array.from(document.querySelectorAll('[data-source="server"]:checked'))
            .map(checkbox => checkbox.dataset.name);
        const browserCollectors = Array.from(document.querySelectorAll('[data-source="browser"]:checked'))
            .map(checkbox => checkbox.dataset.name);
            
        // Original browser state capture - MODIFIED to pass context
        const browserSnapshot = await stateBridge.collectState(browserCollectors, { trigger: 'user_capture' });
        
        // Original server state capture
        const response = await fetch('/api/v1/owner/state/snapshot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-State-Security-Token': stateBridge.securityToken || ''
            },
            body: JSON.stringify({
                collectors: serverCollectors,
                context: { 
                    browser_snapshot: browserSnapshot,
                    source: 'state-monitor-dashboard'
                }
            })
        });
        
        if (!response.ok) {
             // Try get error body (improvement on original)
             let errorBody = ''; try { errorBody = await response.text(); } catch(e){}
             console.error("API Snapshot Error Body:", errorBody);
             throw new Error(`Server responded with ${response.status}. Body: ${errorBody.substring(0, 100)}...`);
        }
        const serverSnapshot = await response.json();
        
        // Update instance state directly (as in original)
        instance.currentSnapshot = {
            timestamp: Date.now(),
            server: serverSnapshot,
            browser: browserSnapshot
        };
        
        // Call renderer via imported function (as in original)
        renderSummaryPanel(instance);
        renderResults(instance);
        // Call setStatus via imported function (as in original)
        setStatus(instance.ui.statusDisplay, 'Snapshot captured successfully');
        
        // Update timestamp (as in original)
        if (instance.ui.snapshotTimestamp) {
            const date = new Date(instance.currentSnapshot.timestamp);
            instance.ui.snapshotTimestamp.textContent = `Last captured: ${date.toLocaleString()}`;
        }
    } catch (error) {
        console.error('Error capturing snapshot:', error);
         // Call setStatus via imported function (as in original)
        setStatus(instance.ui.statusDisplay, `Error: ${error.message}`, 'error');
    }
}

/**
 * Triggers download of the current snapshot.
 * Corresponds to the original downloadSnapshot method.
 * @param {object} instance - The StateMonitorDashboard instance.
 */
export function downloadSnapshot(instance) {
    // Access instance state and UI directly (as in original)
    if (!instance.currentSnapshot) {
        setStatus(instance.ui.statusDisplay, 'No snapshot data to download', 'warning');
        return;
    }
    
    // Original download logic
    const json = JSON.stringify(instance.currentSnapshot, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const timestamp = new Date().toISOString().replace(/[:.]/g, '.'); // Original used . ? Verify
    const filename = `state-snapshot-${timestamp}.json`;
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setStatus(instance.ui.statusDisplay, 'Snapshot downloaded');
}

/**
 * Copies the current snapshot to the clipboard.
 * Corresponds to the original copySnapshot method.
 * @param {object} instance - The StateMonitorDashboard instance.
 */
export async function copySnapshot(instance) {
     // Access instance state and UI directly (as in original)
    if (!instance.currentSnapshot) {
        setStatus(instance.ui.statusDisplay, 'No snapshot data to copy', 'warning');
        return;
    }

    try {
        // Original copy logic
        const jsonString = JSON.stringify(instance.currentSnapshot, null, 2);
        await navigator.clipboard.writeText(jsonString);
        setStatus(instance.ui.statusDisplay, 'Snapshot copied to clipboard', 'success');
    } catch (err) {
        console.error('Failed to copy snapshot:', err);
        setStatus(instance.ui.statusDisplay, 'Failed to copy snapshot to clipboard', 'error');
    }
} 