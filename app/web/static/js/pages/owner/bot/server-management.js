import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

// Server Management Functions
const refreshServerList = async () => {
    try {
        showToast('info', 'Refreshing server list...');
        await apiRequest('/api/v1/owner/bot/servers/list');
        location.reload();
    } catch (error) {
        showToast('error', 'Could not refresh servers');
    }
};

const updateAccess = async (guildId, status) => {
    let message = '';
    let banReason = '';
    
    if (status === 'banned') {
        if (!confirm('⚠️ Are you sure you want to BAN this server?')) return;
        banReason = prompt('Enter ban reason:');
        if (!banReason) return;
        message = '🚫 Server banned';
    } else if (status === 'approved') {
        if (!confirm('Approve this server?')) return;
        message = '✅ Server approved';
    } else if (status === 'rejected') {
        if (!confirm('Reject this server?')) return;
        message = '❌ Server rejected';
    } else if (status === 'suspended') {
        if (!confirm('Suspend this server?')) return;
        message = '⏸️ Server suspended';
    }

    try {
        showToast('info', 'Updating server status...');
        await apiRequest(`/api/v1/owner/bot/servers/${guildId}/access`, {
            method: 'PUT',
            body: JSON.stringify({ 
                status,
                notes: banReason || undefined
            })
        });
        
        showToast('success', message);
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        showToast('error', 'Failed to update server');
    }
};

const showServerDetails = async (guildId) => {
    try {
        showToast('info', 'Loading server details...');
        const data = await apiRequest(`/api/v1/owner/bot/servers/${guildId}/details`);
        
        const modal = document.getElementById('serverDetailsModal');
        if (!modal) return;
        
        // Update basic info
        modal.querySelector('.server-name').textContent = data.name;
        modal.querySelector('.server-id').textContent = data.guild_id;
        modal.querySelector('.member-count').textContent = data.member_count || 0;
        modal.querySelector('.status').textContent = data.access_status;
        modal.querySelector('.join-date').textContent = data.joined_at || 'Not joined';
        
        // Show ban info if present
        const banInfo = modal.querySelector('.ban-info');
        if (banInfo) {
            if (data.access_status === 'banned') {
                banInfo.style.display = 'block';
                banInfo.querySelector('.ban-reason').textContent = data.notes || 'No reason provided';
                banInfo.querySelector('.banned-by').textContent = data.reviewed_by || 'Unknown';
                banInfo.querySelector('.banned-at').textContent = data.reviewed_at || 'Unknown';
            } else {
                banInfo.style.display = 'none';
            }
        }
        
        // Update permissions
        const permissionsList = modal.querySelector('.permissions-list');
        if (permissionsList) {
            permissionsList.innerHTML = data.bot_permissions?.length 
                ? data.bot_permissions.map(perm => `<span class="badge bg-secondary me-1">${perm}</span>`).join('')
                : '<span class="text-muted">No permissions data</span>';
        }
        
        // Update features
        const featuresList = modal.querySelector('.features-list');
        if (featuresList) {
            featuresList.innerHTML = data.features?.length
                ? data.features.map(feature => `<li class="list-group-item">${feature}</li>`).join('')
                : '<li class="list-group-item text-muted">No special features</li>';
        }
        
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    } catch (error) {
        showToast('error', 'Could not load server details');
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const refreshBtn = document.querySelector('button[onclick="refreshServerList()"]');
    if (refreshBtn) {
        refreshBtn.onclick = (e) => {
            e.preventDefault();
            refreshServerList();
        };
    }
    
    const addServerForm = document.getElementById('addServerForm');
    if (addServerForm) {
        addServerForm.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(addServerForm);
            try {
                showToast('info', 'Adding server...');
                await apiRequest('/api/v1/owner/bot/servers/add', {
                    method: 'POST',
                    body: JSON.stringify(Object.fromEntries(formData))
                });
                
                showToast('success', '✅ Server added successfully');
                const modal = bootstrap.Modal.getInstance(document.getElementById('addServerModal'));
                modal.hide();
                setTimeout(() => location.reload(), 1000);
            } catch (error) {
                showToast('error', 'Failed to add server');
            }
        };
    }
}); 