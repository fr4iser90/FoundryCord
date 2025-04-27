// Contains the core logic for collecting state from browser collectors.
import { requestApproval } from './bridgeApproval.js';
import { sanitizeStateData } from './bridgeUtils.js'; // Assuming sanitization happens here

/**
 * Collects state from the specified browser collectors, handling approvals.
 * @param {Object} collectorsRegistry - The registry of all collectors.
 * @param {Set<string>} approvedCollectorsSet - The current set of approved collectors.
 * @param {Object} pendingApprovalsMap - A map to track pending approval requests.
 * @param {Array<string>} [collectorNames=[]] - Specific collector names to run, or all if empty.
 * @param {Object} [context={}] - Optional context data to pass to collectors.
 * @returns {Promise<{timestamp: number, results: Object}>} - The collected state snapshot.
 */
export async function collectBrowserState(collectorsRegistry, approvedCollectorsSet, pendingApprovalsMap, collectorNames = [], context = {}) {
    const results = {};
    const timestamp = Date.now();
    const collectorsToRun = collectorNames.length > 0 
        ? collectorNames 
        : Object.keys(collectorsRegistry);

    const collectorsToRunApproved = []; // Collectors ready to run
    const collectorsNeedingApproval = []; // Collectors needing approval first

    // --- Phase 1: Request Approvals --- 
    console.debug("StateBridge Collect - Phase 1: Checking Approvals for", collectorsToRun);
    for (const name of collectorsToRun) {
        if (!collectorsRegistry[name]) {
            console.warn(`Unknown state collector during approval check: ${name}`);
            continue;
        }
        const collector = collectorsRegistry[name];
        if (collector.options.requiresApproval && !approvedCollectorsSet.has(name)) {
            collectorsNeedingApproval.push(name); // Add to list for batch approval
        } else {
            collectorsToRunApproved.push(name); // Can run immediately
        }
    }
    console.debug("StateBridge Collect - Phase 1: Approval checks complete. Current approved:", Array.from(approvedCollectorsSet));

    // --- Request Batch Approval if needed --- 
    if (collectorsNeedingApproval.length > 0) {
        console.info(`Requesting batch approval for collectors: ${collectorsNeedingApproval.join(', ')}`);
        // Call requestApproval ONCE with the array
        const granted = await requestApproval(collectorsNeedingApproval, collectorsRegistry, approvedCollectorsSet, pendingApprovalsMap);
        if (granted) {
            // If batch approved, add them to the list to run
            collectorsToRunApproved.push(...collectorsNeedingApproval);
            console.info("Batch approval granted.");
        } else {
            // If batch rejected, mark them as errors
            console.warn("Batch approval rejected.");
            collectorsNeedingApproval.forEach(name => {
                results[name] = { error: 'approval_rejected', requiresApproval: true };
            });
        }
    }

    // --- Phase 2: Collect Data ---
    console.debug("StateBridge Collect - Phase 2: Collecting Data...");
    for (const name of collectorsToRunApproved) {
        if (!collectorsRegistry[name]) {
            console.warn(`Unknown state collector during collection: ${name}`);
            results[name] = { error: 'unknown_collector' };
            continue;
        }
        const collector = collectorsRegistry[name];

        // Check if collector is usable
        if (!collector.options.requiresApproval || approvedCollectorsSet.has(name)) {
             console.debug(`Collecting data for approved collector: ${name}`);
            try {
                const collectorFn = collector.function;
                if (typeof collectorFn === 'function') {
                    let result;
                    const potentialPromise = collectorFn(context);
                    if (potentialPromise && typeof potentialPromise.then === 'function') {
                        result = await potentialPromise;
                    } else {
                        result = potentialPromise;
                    }
                    // Use the sanitize function from utils
                    const processedResult = collector.options.sanitize
                        ? sanitizeStateData(result)
                        : result;
                    results[name] = processedResult;
                    console.log(`Successfully collected state with: ${name}`);
                } else {
                    console.error(`Collector function for ${name} is not a function.`);
                    results[name] = { error: 'collector_not_function' };
                }
            } catch (error) {
                console.error(`Error executing state collector ${name}:`, error);
                results[name] = { error: error.message || 'Unknown error', stack: error.stack };
            }
        }
    }
     console.debug("StateBridge Collect - Phase 2: Data collection complete.");

    const snapshot = {
        timestamp,
        results
    };
    return snapshot;
}
