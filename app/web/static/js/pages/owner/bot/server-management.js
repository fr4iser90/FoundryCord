import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

// Helper function to format date/time or return 'N/A'
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    try {
        // Assuming dateString is in ISO format or similar
        return new Date(dateString).toLocaleString(); 
    } catch (e) {
        console.warn("Could not parse date:", dateString);
        return 'Invalid Date';
    }
}

// Server Management Functions
async function refreshServerList() {
    try {
        showToast('info', 'Refreshing server list...');
        // Call the new endpoint that returns all manageable servers
        // The endpoint now returns the list directly due to response_model
        const servers = await apiRequest('/api/v1/owner/servers/manageable'); 
        
        // Check if servers is actually an array (apiRequest might return the raw response or parsed data)
        // Adjust this check based on how apiRequest actually behaves on success
        if (!Array.isArray(servers)) {
            // If apiRequest returns the full response object on success, uncomment next line:
            // servers = servers.data;
            if (!Array.isArray(servers)) { // Check again after potential adjustment
                console.error('API did not return an array of servers:', servers);
                showToast('error', 'Received invalid data structure from server.');
                return; 
            }
        }
        
        // Update the total server count badge
        const countBadge = document.getElementById('total-server-count');
        if (countBadge) {
            countBadge.textContent = servers.length;
        }

        // Update the single table with all servers
        updateServerList('all-servers-tbody', servers); // Target the new tbody ID
        
        showToast('success', 'Server list updated');
    } catch (error) {
        console.error('Server refresh error:', error);
        // Display the error from the API response if available
        const errorMessage = error.response?.data?.detail || error.message || 'Could not refresh servers';
        showToast('error', errorMessage);
    }
}

// Updated function to populate a single table
function updateServerList(tbodyId, servers) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) {
        console.warn(`Table body ${tbodyId} not found`);
        return;
    }

    // Clear existing rows
    tbody.innerHTML = '';

    if (servers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No servers found</td></tr>';
        return;
    }

    servers.forEach(server => {
        const row = document.createElement('tr');
        
        // Determine the appropriate date to show based on status
        let lastUpdatedDate = server.access_reviewed_at || server.access_requested_at || server.created_at; // Example logic
        
        row.innerHTML = `
            <td class="d-flex align-items-center">
                <div class="me-2">
                    ${server.icon_url 
                        ? `<img src="${server.icon_url}" alt="" class="server-icon rounded" width="32" height="32" onerror="this.src='/static/img/default-server.png'">` // Added onerror fallback
                        : `<div class="server-icon-placeholder rounded">${server.name ? server.name.charAt(0).toUpperCase() : 'S'}</div>` // Show initial if no icon
                    }
                </div>
                <div>
                    <div class="server-name fw-bold">${server.name}</div>
                    <small class="text-muted">${server.guild_id}</small>
                </div>
            </td>
            <td>${getStatusBadge(server.access_status)}</td>
            <td>${server.member_count || 0}</td>
            <td>${formatDateTime(lastUpdatedDate)}</td>
            <td>${getActionButtons(server)}</td>
        `;
        tbody.appendChild(row);
    });
}

function getStatusBadge(status) {
    const statusMap = {
        'pending': '<span class="badge bg-warning text-dark"><i class="bi bi-clock"></i> Pending</span>',
        'approved': '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Approved</span>',
        'rejected': '<span class="badge bg-danger"><i class="bi bi-x-circle"></i> Rejected</span>',
        'blocked': '<span class="badge bg-danger"><i class="bi bi-ban"></i> Blocked</span>',
        'suspended': '<span class="badge bg-secondary"><i class="bi bi-pause-circle"></i> Suspended</span>' // Added suspended
    };
    return statusMap[status.toLowerCase()] || '<span class="badge bg-secondary"><i class="bi bi-question-circle"></i> Unknown</span>';
}

function getActionButtons(server) {
    const status = server.access_status ? server.access_status.toLowerCase() : 'unknown';
    let buttons = '';

    // Always show details button
    buttons += `
        <button data-action="details" data-guild-id="${server.guild_id}" class="btn btn-info btn-sm" title="Details">
            <i class="bi bi-info-circle"></i>
        </button>
    `;

    if (status === 'pending') {
        buttons += `
            <button data-action="approve" data-guild-id="${server.guild_id}" class="btn btn-success btn-sm" title="Approve">
                <i class="bi bi-check-lg"></i>
            </button>
            <button data-action="reject" data-guild-id="${server.guild_id}" class="btn btn-danger btn-sm" title="Reject">
                <i class="bi bi-x-lg"></i>
            </button>
        `;
    } else if (status === 'approved') {
        buttons += `
            <button data-action="suspend" data-guild-id="${server.guild_id}" class="btn btn-warning btn-sm" title="Suspend">
                <i class="bi bi-pause-circle"></i>
            </button>
            <button data-action="block" data-guild-id="${server.guild_id}" class="btn btn-danger btn-sm" title="Block">
                <i class="bi bi-ban"></i>
            </button>
        `;
    } else if (status === 'rejected' || status === 'blocked' || status === 'suspended') {
        buttons += `
            <button data-action="approve" data-guild-id="${server.guild_id}" class="btn btn-success btn-sm" title="Re-Approve">
                <i class="bi bi-check-lg"></i>
            </button>
        `;
         if (status !== 'blocked') { // Can't unblock directly from here maybe? Add if needed.
             buttons += `
                 <button data-action="block" data-guild-id="${server.guild_id}" class="btn btn-danger btn-sm" title="Block">
                     <i class="bi bi-ban"></i>
                 </button>
             `;
         }
    }
    // Add other status cases if needed

    return `<div class="btn-group">${buttons}</div>`;
}

async function updateAccess(guildId, status) {
    try {
        showToast('info', `Setting server ${guildId} status to ${status}...`);
        // Ensure API endpoint exists, assuming /access updates status
        // NOTE: The backend might need adjustment to handle 'suspend'
        await apiRequest(`/api/v1/owner/servers/${guildId}/access`, { 
            method: 'POST',
            body: JSON.stringify({ status: status.toLowerCase() })
        });
        
        showToast('success', `Server status updated to ${status}`);
        await refreshServerList(); // Refresh the list to show changes
    } catch (error) {
        console.error('Update access error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to update server access';
        showToast('error', errorMessage);
    }
}

async function showServerDetails(guildId) {
    try {
        const data = await apiRequest(`/api/v1/owner/servers/${guildId}`); // Use the correct details endpoint
        
        const modal = document.getElementById('serverDetailsModal');
        if (!modal) return;
        
        // Update modal content (ensure backend provides these fields)
        modal.querySelector('.server-name').textContent = data.name || 'N/A';
        modal.querySelector('.server-id').textContent = data.guild_id || 'N/A';
        modal.querySelector('.member-count').textContent = data.member_count || 0;
        modal.querySelector('.status').innerHTML = getStatusBadge(data.access_status || 'unknown'); // Use badge
        modal.querySelector('.join-date').textContent = formatDateTime(data.created_at); // Example: use created_at
        
        // TODO: Populate ban info, permissions, features if backend provides them
        
        // Show modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    } catch (error) {
        console.error('Server details error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Could not load server details';
        showToast('error', errorMessage);
    }
}

// Event listener setup needs to handle new actions
document.addEventListener('DOMContentLoaded', () => {
    // Initial server list load
    refreshServerList();
    
    // Add click handlers for server actions
    document.addEventListener('click', async (event) => {
        const button = event.target.closest('button[data-action]');
        if (!button) return;
        
        const action = button.dataset.action;
        const guildId = button.dataset.guildId;
        
        if (!guildId) return;
        
        switch(action) {
            case 'approve':
                await updateAccess(guildId, 'approved');
                break;
            case 'reject':
                await updateAccess(guildId, 'rejected');
                break;
            case 'block': // Changed from suspend to block if needed
                await updateAccess(guildId, 'blocked'); 
                break;
            case 'suspend': // Added suspend action
                await updateAccess(guildId, 'suspended');
                break;
            case 'details':
                await showServerDetails(guildId);
                break;
        }
    });
    
    // Refresh button handler (remains the same)
    const refreshButton = document.querySelector('.card-header .btn-info'); // More specific selector
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshServerList);
    }
    
    // Add Server Modal logic (Assuming it exists elsewhere or is simple)
    // const addServerForm = document.getElementById('addServerForm');
    // if (addServerForm) { ... }
}); 