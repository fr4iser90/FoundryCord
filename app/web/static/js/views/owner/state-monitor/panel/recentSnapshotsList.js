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
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        // Format timestamp nicely
        let timestampStr = 'Invalid Date';
        try {
            const date = new Date(snapshot.timestamp || snapshot.created_at); // Handle potential property names
            if (!isNaN(date)) {
                 timestampStr = date.toLocaleString(); // User-friendly format
            }
        } catch (e) { 
            console.warn("Error parsing snapshot timestamp:", snapshot.timestamp || snapshot.created_at);
        }

        const snapshotInfo = document.createElement('div');
        snapshotInfo.innerHTML = `
            <small class="d-block">${timestampStr}</small>
            <small class="text-muted">ID: ${snapshot.id || 'N/A'}</small>
        `;

        const loadButton = document.createElement('button');
        loadButton.className = 'btn btn-sm btn-outline-primary';
        loadButton.textContent = 'Load';
        loadButton.dataset.snapshotId = snapshot.id;
        loadButton.title = `Load snapshot ${snapshot.id}`;

        // TODO: Implement controller.loadSnapshot(snapshotId) method
        loadButton.addEventListener('click', (event) => {
            const snapshotId = event.currentTarget.dataset.snapshotId;
            if (snapshotId) {
                console.log(`[RecentSnapshotsList] Requesting load for snapshot: ${snapshotId}`);
                controller.loadSnapshot(snapshotId); // Call the controller method directly
            } else {
                console.error("[RecentSnapshotsList] Snapshot ID missing from button.");
            }
        });

        listItem.appendChild(snapshotInfo);
        listItem.appendChild(loadButton);
        listGroup.appendChild(listItem);
    });

    contentElement.appendChild(listGroup);

    console.log("[RecentSnapshotsList] Initialization complete.");
} 