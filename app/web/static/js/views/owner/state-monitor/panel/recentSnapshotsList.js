/**
 * Renders the list of recent snapshots.
 */

// TODO: Import necessary dependencies (e.g., loadAndDisplaySnapshot from api)

/**
 * Initializes the Recent Snapshots List widget.
 * @param {object} controller - The main StateMonitorController instance.
 * @param {Array} recentSnapshotsData - An array of recent snapshot metadata objects.
 * @param {HTMLElement} contentElement - The container element for the widget's content.
 */
export function initializeRecentSnapshotsList(controller, recentSnapshotsData, contentElement) {
    console.log("[RecentSnapshotsList] Initializing with data:", recentSnapshotsData);
    if (!contentElement) {
        console.error("[RecentSnapshotsList] Content element not provided.");
        return;
    }

    contentElement.innerHTML = ''; // Clear previous content

    if (!recentSnapshotsData || recentSnapshotsData.length === 0) {
        contentElement.innerHTML = '<p class="text-muted px-2 pt-2">No recent snapshots found.</p>';
        return;
    }

    const listGroup = document.createElement('ul');
    listGroup.className = 'list-group list-group-flush'; // Flush removes borders

    recentSnapshotsData.forEach(snapshot => {
        // --- Robustness Check: Ensure snapshot_id exists --- 
        if (!snapshot || !snapshot.snapshot_id) {
            console.warn("[RecentSnapshotsList] Skipping snapshot entry due to missing snapshot_id:", snapshot);
            return; // Skip this iteration
        }
        // --- End Check ---
        
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        // Format timestamp nicely
        let timestampStr = 'Invalid Date';
        try {
            // Use snapshot.capture_timestamp (API response field)
            const date = new Date((snapshot.capture_timestamp || 0) * 1000); // API sends seconds, convert to ms
            if (!isNaN(date)) {
                 timestampStr = date.toLocaleString(); // User-friendly format
            }
        } catch (e) { 
            console.warn("Error parsing snapshot timestamp:", snapshot.capture_timestamp);
        }

        const snapshotInfo = document.createElement('div');
        snapshotInfo.innerHTML = `
            <small class="d-block">${timestampStr}</small>
            <small>ID: ${snapshot.snapshot_id || 'N/A'}</small> 
        `; // Use snapshot_id

        const loadButton = document.createElement('button');
        loadButton.className = 'btn btn-sm btn-outline-primary';
        loadButton.textContent = 'Load';
        // Use snapshot_id for dataset
        loadButton.dataset.snapshotId = snapshot.snapshot_id;
        loadButton.title = `Load snapshot ${snapshot.snapshot_id}`;

        // Create Delete Button
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-sm btn-outline-danger ms-1'; // Added margin start
        deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
        // Use snapshot_id for dataset
        deleteButton.dataset.snapshotId = snapshot.snapshot_id;
        deleteButton.title = `Delete snapshot ${snapshot.snapshot_id}`;

        // Load Button Listener
        loadButton.addEventListener('click', (event) => {
            const snapshotId = event.currentTarget.dataset.snapshotId;
            if (snapshotId) { // Check if dataset has ID
                console.log(`[RecentSnapshotsList] Requesting load for snapshot: ${snapshotId}`);
                controller.loadSnapshot(snapshotId); // Call the controller method
            } else {
                console.error("[RecentSnapshotsList] Snapshot ID missing for load button.");
            }
        });

        // Delete Button Listener
        deleteButton.addEventListener('click', (event) => {
            const snapshotId = event.currentTarget.dataset.snapshotId;
             // Double check we have an ID before proceeding
            if (!snapshotId) {
                 console.error("[RecentSnapshotsList] Snapshot ID missing for delete button.");
                 return; 
            }

            // Confirmation dialog
            if (confirm(`Are you sure you want to delete snapshot ${snapshotId}?`)) {
                console.log(`[RecentSnapshotsList] Requesting delete for snapshot: ${snapshotId}`);
                controller.deleteSnapshot(snapshotId, event.currentTarget.closest('li'));
            }
        });

        // Append elements
        const buttonGroup = document.createElement('div'); // Group buttons for alignment
        buttonGroup.className = 'd-flex align-items-center'; // Use flex for buttons
        buttonGroup.appendChild(loadButton);
        buttonGroup.appendChild(deleteButton); // Add delete button next to load

        listItem.appendChild(snapshotInfo);
        listItem.appendChild(buttonGroup); // Append the button group
        listGroup.appendChild(listItem);
    });

    contentElement.appendChild(listGroup);

    console.log("[RecentSnapshotsList] Initialization complete.");
} 