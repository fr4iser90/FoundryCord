// Bot Control Functions
async function startBot() {
    try {
        const response = await fetch('/api/v1/owner/bot/start', {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Success', 'Bot started successfully');
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to start bot');
        }
    } catch (error) {
        showToast('Error', 'Failed to start bot: ' + error.message);
    }
}

async function stopBot() {
    if (!confirm('Are you sure you want to stop the bot?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/v1/owner/bot/stop', {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Success', 'Bot stopped successfully');
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to stop bot');
        }
    } catch (error) {
        showToast('Error', 'Failed to stop bot: ' + error.message);
    }
}

async function restartBot() {
    if (!confirm('Are you sure you want to restart the bot?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/v1/owner/bot/restart', {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Success', 'Bot restarted successfully');
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to restart bot');
        }
    } catch (error) {
        showToast('Error', 'Failed to restart bot: ' + error.message);
    }
}

// Server Management Functions
async function addServer() {
    const serverId = document.getElementById('serverId').value;
    const serverName = document.getElementById('serverName').value;
    
    try {
        const response = await fetch('/api/v1/owner/servers/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                guild_id: serverId,
                name: serverName || 'Unknown Server'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Success', 'Server added successfully. Please use the invite link to add the bot to the server.');
            const modal = bootstrap.Modal.getInstance(document.getElementById('addServerModal'));
            modal.hide();
            refreshServerList();
        } else {
            showToast('Error', data.detail || 'Failed to add server');
        }
    } catch (error) {
        showToast('Error', 'Failed to add server: ' + error.message);
    }
}

async function updateAccess(guildId, status) {
    try {
        const response = await fetch(`/api/v1/owner/bot/servers/${guildId}/access`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: status
            })
        });
        
        if (response.ok) {
            showToast('Success', `Server access status updated to ${status}`);
            refreshServerList();
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to update access status');
        }
    } catch (error) {
        showToast('Error', 'Failed to update access status: ' + error.message);
    }
}

async function showServerDetails(guildId) {
    try {
        const response = await fetch(`/api/v1/owner/servers/${guildId}/details`);
        const data = await response.json();
        
        if (response.ok) {
            // Populate server details modal
            document.getElementById('serverDetailsContent').innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Server Name:</strong> ${data.name}</p>
                        <p><strong>Server ID:</strong> ${data.guild_id}</p>
                        <p><strong>Owner ID:</strong> ${data.owner_id}</p>
                        <p><strong>Member Count:</strong> ${data.member_count}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Status:</strong> ${data.is_active ? 'Active' : 'Inactive'}</p>
                        <p><strong>Access Status:</strong> ${data.access_status}</p>
                        <p><strong>Requested:</strong> ${new Date(data.access_requested_at).toLocaleString()}</p>
                        <p><strong>Last Review:</strong> ${data.access_reviewed_at ? new Date(data.access_reviewed_at).toLocaleString() : 'Not reviewed'}</p>
                    </div>
                </div>
            `;
            
            // Set form values
            document.getElementById('serverNotes').value = data.access_notes || '';
            document.getElementById('enableCommands').checked = data.enable_commands;
            document.getElementById('enableLogging').checked = data.enable_logging;
            document.getElementById('enableAutomod').checked = data.enable_automod;
            document.getElementById('enableWelcome').checked = data.enable_welcome;
            
            // Store guild ID for save function
            document.getElementById('serverDetailsModal').dataset.guildId = guildId;
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('serverDetailsModal'));
            modal.show();
        } else {
            showToast('Error', data.detail || 'Failed to load server details');
        }
    } catch (error) {
        showToast('Error', 'Failed to load server details: ' + error.message);
    }
}

async function saveServerDetails() {
    const modal = document.getElementById('serverDetailsModal');
    const guildId = modal.dataset.guildId;
    
    try {
        const response = await fetch(`/api/v1/owner/servers/${guildId}/details`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                access_notes: document.getElementById('serverNotes').value,
                enable_commands: document.getElementById('enableCommands').checked,
                enable_logging: document.getElementById('enableLogging').checked,
                enable_automod: document.getElementById('enableAutomod').checked,
                enable_welcome: document.getElementById('enableWelcome').checked
            })
        });
        
        if (response.ok) {
            showToast('Success', 'Server details updated successfully');
            bootstrap.Modal.getInstance(modal).hide();
            location.reload();
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to update server details');
        }
    } catch (error) {
        showToast('Error', 'Failed to update server details: ' + error.message);
    }
}

async function refreshServerList() {
    try {
        const response = await fetch('/api/v1/owner/servers', {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateServerTable(data);
        } else {
            const error = await response.json();
            showToast('Error', error.detail || 'Failed to refresh server list');
        }
    } catch (error) {
        showToast('Error', 'Failed to refresh server list: ' + error.message);
    }
}

// Helper function to update the server table
function updateServerTable(servers) {
    const pendingServers = servers.filter(s => s.access_status === 'PENDING');
    const otherServers = servers.filter(s => s.access_status !== 'PENDING');
    
    // Update pending servers section
    const serverManagementCard = document.querySelector('.card-body');
    let pendingSection = document.querySelector('.pending-approvals');
    
    if (pendingServers.length > 0) {
        const pendingHtml = `
            <div class="pending-approvals alert alert-warning mb-4">
                <h5 class="d-flex align-items-center">
                    <i class="bi bi-clock-history me-2"></i>
                    Pending Approvals (${pendingServers.length})
                </h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Server Name</th>
                                <th>Server ID</th>
                                <th>Members</th>
                                <th>Requested At</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${pendingServers.map(server => `
                                <tr>
                                    <td>${server.name}</td>
                                    <td>${server.guild_id}</td>
                                    <td>${server.member_count || 0}</td>
                                    <td>${server.access_requested_at ? new Date(server.access_requested_at).toLocaleString() : 'Unknown'}</td>
                                    <td>
                                        <div class="btn-group">
                                            <button class="btn btn-sm btn-success" onclick="updateAccess('${server.guild_id}', 'APPROVED')" title="Approve">
                                                <i class="bi bi-check"></i>
                                            </button>
                                            <button class="btn btn-sm btn-danger" onclick="updateAccess('${server.guild_id}', 'DENIED')" title="Deny">
                                                <i class="bi bi-x"></i>
                                            </button>
                                            <button class="btn btn-sm btn-info" onclick="showServerDetails('${server.guild_id}')" title="Details">
                                                <i class="bi bi-info-circle"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        // If pending section doesn't exist, create it
        if (!pendingSection) {
            const mainTable = document.querySelector('.table-responsive');
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = pendingHtml;
            serverManagementCard.insertBefore(tempDiv.firstChild, mainTable);
        } else {
            // Update existing pending section
            pendingSection.outerHTML = pendingHtml;
        }
    } else if (pendingSection) {
        // Remove pending section if no pending servers
        pendingSection.remove();
    }
    
    // Update main servers table
    const mainTableBody = document.querySelector('.table-hover tbody');
    if (mainTableBody) {
        mainTableBody.innerHTML = otherServers.map(server => `
            <tr class="${server.access_status === 'BLOCKED' ? 'table-danger' : server.access_status === 'DENIED' ? 'table-warning' : ''}">
                <td>${server.name}</td>
                <td>${server.guild_id}</td>
                <td>
                    <span class="badge ${getBadgeClass(server.access_status)}">
                        ${server.access_status}
                    </span>
                </td>
                <td>${server.member_count || 0}</td>
                <td>${server.joined_at ? new Date(server.joined_at).toLocaleString() : 'Not joined'}</td>
                <td>
                    <div class="btn-group">
                        ${getActionButtons(server)}
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

// Helper function to get badge class based on status
function getBadgeClass(status) {
    switch (status) {
        case 'APPROVED': return 'bg-success';
        case 'PENDING': return 'bg-warning';
        case 'DENIED': return 'bg-danger';
        case 'BLOCKED': return 'bg-dark';
        default: return 'bg-secondary';
    }
}

// Helper function to get action buttons based on server status
function getActionButtons(server) {
    let buttons = [];
    
    buttons.push(`
        <button class="btn btn-sm btn-info" onclick="showServerDetails('${server.guild_id}')" title="Details">
            <i class="bi bi-info-circle"></i>
        </button>
    `);
    
    if (server.access_status === 'PENDING') {
        buttons.push(`
            <button class="btn btn-sm btn-success" onclick="updateAccess('${server.guild_id}', 'APPROVED')" title="Approve">
                <i class="bi bi-check"></i>
            </button>
            <button class="btn btn-sm btn-danger" onclick="updateAccess('${server.guild_id}', 'DENIED')" title="Deny">
                <i class="bi bi-x"></i>
            </button>
        `);
    } else if (server.access_status !== 'BLOCKED') {
        buttons.push(`
            <button class="btn btn-sm btn-dark" onclick="updateAccess('${server.guild_id}', 'BLOCKED')" title="Block">
                <i class="bi bi-shield-x"></i>
            </button>
        `);
    } else {
        buttons.push(`
            <button class="btn btn-sm btn-secondary" onclick="updateAccess('${server.guild_id}', 'DENIED')" title="Unblock">
                <i class="bi bi-shield-check"></i>
            </button>
        `);
    }
    
    return buttons.join('');
}

async function removeServer(guildId) {
    if (!confirm('Are you sure you want to remove this server?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/v1/owner/servers/${guildId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Success', 'Server removed successfully');
            location.reload();
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to remove server');
        }
    } catch (error) {
        showToast('Error', 'Failed to remove server: ' + error.message);
    }
}

async function joinServer(guildId) {
    try {
        const response = await fetch(`/api/v1/owner/bot/servers/${guildId}/join`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Success', 'Bot joined server successfully');
            location.reload();
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to join server');
        }
    } catch (error) {
        showToast('Error', 'Failed to join server: ' + error.message);
    }
}

async function leaveServer(guildId) {
    if (!confirm('Are you sure you want the bot to leave this server?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/v1/owner/bot/servers/${guildId}/leave`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Success', 'Bot left server successfully');
            location.reload();
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to leave server');
        }
    } catch (error) {
        showToast('Error', 'Failed to leave server: ' + error.message);
    }
}

// Bot Configuration Functions
document.getElementById('botConfigForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const config = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/v1/owner/bot/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            showToast('Success', 'Configuration saved successfully');
        } else {
            const data = await response.json();
            showToast('Error', data.detail || 'Failed to save configuration');
        }
    } catch (error) {
        showToast('Error', 'Failed to save configuration: ' + error.message);
    }
});

// Helper Functions
function showToast(title, message) {
    // You can implement this using your preferred toast library
    // For now, we'll use a simple alert
    alert(`${title}: ${message}`);
}

// Bot Control Panel JavaScript

// Constants
const BOT_CLIENT_ID = '1342018822755848212'; // Your bot's client ID
const DEFAULT_PERMISSIONS = '8'; // Administrator permission (8)

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    updateInviteLink();
    // Add event listeners for permission checkboxes
    document.getElementById('adminPerm').addEventListener('change', updateInviteLink);
    document.getElementById('managePerm').addEventListener('change', updateInviteLink);
});

// Update the invite link based on selected permissions
function updateInviteLink() {
    let permissions = 0;
    if (document.getElementById('adminPerm').checked) {
        permissions |= 8; // Administrator
    }
    if (document.getElementById('managePerm').checked) {
        permissions |= 32; // Manage Server
    }
    
    const inviteLink = `https://discord.com/api/oauth2/authorize?client_id=${BOT_CLIENT_ID}&permissions=${permissions}&scope=bot%20applications.commands`;
    document.getElementById('inviteLink').value = inviteLink;
    document.getElementById('inviteLinkBtn').href = inviteLink;
}

// Copy invite link to clipboard
function copyInviteLink() {
    const inviteLinkInput = document.getElementById('inviteLink');
    inviteLinkInput.select();
    document.execCommand('copy');
    
    // Show feedback
    const button = document.querySelector('[onclick="copyInviteLink()"]');
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="bi bi-check"></i> Copied!';
    setTimeout(() => {
        button.innerHTML = originalText;
    }, 2000);
}

// Auto-refresh every 30 seconds
setInterval(refreshServerList, 30000);

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    refreshServerList();
}); 