import { showToast, apiRequest, formatDateTime } from '../../../components/common/notifications.js';

// Server Management Functions
const refreshServerList = async () => {
    try {
        await apiRequest('/api/owner/bot/servers/list');
        window.location.reload();
    } catch (error) {
        // Error already handled by apiRequest
    }
};

const updateAccess = async (guildId, status) => {
    try {
        await apiRequest(`/api/owner/bot/servers/${guildId}/access`, {
            method: 'PUT',
            body: JSON.stringify({ status }),
        });
        
        showToast('success', `Server access updated to ${status}`);
        refreshServerList();
    } catch (error) {
        // Error already handled by apiRequest
    }
};

const showServerDetails = async (guildId) => {
    try {
        const data = await apiRequest(`/api/owner/bot/servers/${guildId}/details`);
        const modal = new bootstrap.Modal(document.getElementById('serverDetailsModal'));
        populateServerDetailsModal(data);
        modal.show();
    } catch (error) {
        // Error already handled by apiRequest
    }
};

const populateServerDetailsModal = (serverData) => {
    const modal = document.getElementById('serverDetailsModal');
    modal.querySelector('.server-name').textContent = serverData.name;
    modal.querySelector('.server-id').textContent = serverData.guild_id;
    modal.querySelector('.member-count').textContent = serverData.member_count;
    modal.querySelector('.join-date').textContent = formatDateTime(serverData.joined_at);
    modal.querySelector('.status').textContent = serverData.access_status;
    
    if (serverData.features) {
        const featuresList = modal.querySelector('.features-list');
        featuresList.innerHTML = serverData.features
            .map(feature => `<li class="list-group-item">${feature}</li>`)
            .join('');
    }
}; 