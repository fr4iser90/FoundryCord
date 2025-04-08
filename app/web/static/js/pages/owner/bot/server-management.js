// Server Management Functions
function showToast(type, message) {
    // Basic toast implementation
    console.log(`${type}: ${message}`);
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
}

async function refreshServerList() {
    try {
        showToast('info', 'Refreshing server list...');
        const response = await fetch('/api/v1/owner/servers');
        const servers = await response.json();
        
        // Update UI with server lists
        const pendingServers = servers.filter(s => s.access_status.toLowerCase() === 'pending');
        const approvedServers = servers.filter(s => s.access_status.toLowerCase() === 'approved');
        const blockedServers = servers.filter(s => s.access_status.toLowerCase() === 'blocked' || s.access_status.toLowerCase() === 'rejected');
        
        updateServerList('pending-servers', pendingServers);
        updateServerList('approved-servers', approvedServers);
        updateServerList('blocked-servers', blockedServers);
        
        showToast('success', 'Server list updated');
    } catch (error) {
        console.error('Server refresh error:', error);
        showToast('error', 'Could not refresh servers: ' + error.message);
    }
}

function updateServerList(containerId, servers) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.warn(`Container ${containerId} not found`);
        return;
    }

    if (servers.length === 0) {
        container.innerHTML = '<tr><td colspan="5" class="text-center">No servers found</td></tr>';
        return;
    }

    container.innerHTML = servers.map(server => `
        <tr>
            <td class="d-flex align-items-center">
                <div class="me-2">
                    ${server.icon_url 
                        ? `<img src="${server.icon_url}" alt="" class="server-icon rounded" width="32" height="32">`
                        : `<div class="server-icon-placeholder rounded"></div>`
                    }
                </div>
                <div>
                    <div class="server-name">${server.name}</div>
                    <small class="text-muted">${server.guild_id}</small>
                </div>
            </td>
            <td>${getStatusBadge(server.access_status)}</td>
            <td>${server.member_count || 0}</td>
            <td>${new Date(server.access_requested_at).toLocaleDateString()}</td>
            <td>${getActionButtons(server)}</td>
        </tr>
    `).join('');
}

function getStatusBadge(status) {
    const statusMap = {
        'pending': '<span class="badge bg-warning text-dark"><i class="bi bi-clock"></i> Pending</span>',
        'approved': '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Approved</span>',
        'rejected': '<span class="badge bg-danger"><i class="bi bi-x-circle"></i> Rejected</span>',
        'blocked': '<span class="badge bg-danger"><i class="bi bi-ban"></i> Blocked</span>'
    };
    return statusMap[status.toLowerCase()] || '<span class="badge bg-secondary"><i class="bi bi-question-circle"></i> Unknown</span>';
}

function getActionButtons(server) {
    const status = server.access_status.toLowerCase();
    
    if (status === 'pending') {
        return `
            <div class="btn-group">
                <button onclick="updateAccess('${server.guild_id}', 'approved')" class="btn btn-success btn-sm">
                    <i class="bi bi-check-lg"></i>
                </button>
                <button onclick="updateAccess('${server.guild_id}', 'rejected')" class="btn btn-danger btn-sm">
                    <i class="bi bi-x-lg"></i>
                </button>
                <button onclick="showServerDetails('${server.guild_id}')" class="btn btn-info btn-sm">
                    <i class="bi bi-info-circle"></i>
                </button>
            </div>
        `;
    }
    
    if (status === 'approved') {
        return `
            <div class="btn-group">
                <button onclick="showServerDetails('${server.guild_id}')" class="btn btn-info btn-sm">
                    <i class="bi bi-info-circle"></i>
                </button>
                <button onclick="updateAccess('${server.guild_id}', 'blocked')" class="btn btn-warning btn-sm">
                    <i class="bi bi-pause-circle"></i>
                </button>
            </div>
        `;
    }
    
    return `
        <div class="btn-group">
            <button onclick="showServerDetails('${server.guild_id}')" class="btn btn-info btn-sm">
                <i class="bi bi-info-circle"></i>
            </button>
            <button onclick="updateAccess('${server.guild_id}', 'approved')" class="btn btn-success btn-sm">
                <i class="bi bi-check-lg"></i>
            </button>
        </div>
    `;
}

async function updateAccess(guildId, status) {
    try {
        showToast('info', 'Updating server status...');
        await fetch(`/api/v1/owner/servers/${guildId}/access`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: status.toLowerCase() })
        });
        
        showToast('success', `Server ${status} successfully`);
        await refreshServerList();
    } catch (error) {
        console.error('Update access error:', error);
        showToast('error', 'Failed to update server access');
    }
}

async function showServerDetails(guildId) {
    try {
        const response = await fetch(`/api/v1/owner/servers/${guildId}/details`);
        const data = await response.json();
        
        const modal = document.getElementById('serverDetailsModal');
        if (!modal) return;
        
        // Update modal content
        modal.querySelector('.server-name').textContent = data.name;
        modal.querySelector('.server-id').textContent = data.guild_id;
        modal.querySelector('.member-count').textContent = data.member_count || 0;
        modal.querySelector('.status').textContent = data.access_status;
        
        // Show modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    } catch (error) {
        console.error('Server details error:', error);
        showToast('error', 'Could not load server details');
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initial server list load
    refreshServerList();
    
    // Add refresh button handler
    const refreshButton = document.querySelector('button[onclick="refreshServerList()"]');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshServerList);
    }
    
    // Make functions globally available
    window.refreshServerList = refreshServerList;
    window.updateAccess = updateAccess;
    window.showServerDetails = showServerDetails;
}); 