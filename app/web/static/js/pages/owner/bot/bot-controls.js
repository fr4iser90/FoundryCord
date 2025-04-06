import { showToast, apiRequest, formatDuration } from '../../../components/common/notifications.js';

// Bot Control Functions
const startBot = async () => {
    try {
        await apiRequest('/api/owner/bot/control/start', { method: 'POST' });
        showToast('success', 'Bot started successfully');
        updateBotStatus();
    } catch (error) {
        // Error already handled by apiRequest
    }
};

const stopBot = async () => {
    try {
        await apiRequest('/api/owner/bot/control/stop', { method: 'POST' });
        showToast('success', 'Bot stopped successfully');
        updateBotStatus();
    } catch (error) {
        // Error already handled by apiRequest
    }
};

const restartBot = async () => {
    try {
        await apiRequest('/api/owner/bot/control/restart', { method: 'POST' });
        showToast('success', 'Bot restarting...');
        setTimeout(updateBotStatus, 5000); // Check status after 5 seconds
    } catch (error) {
        // Error already handled by apiRequest
    }
};

const updateBotStatus = async () => {
    try {
        const data = await apiRequest('/api/owner/bot/status');
        updateStatusUI(data);
    } catch (error) {
        // Error already handled by apiRequest
    }
};

const updateStatusUI = (statusData) => {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');
    const latencyText = document.querySelector('.text-muted');
    const statsSection = document.querySelector('.bot-stats');
    
    // Update status indicator and text
    statusIndicator.className = `status-indicator ${statusData.status === 'online' ? 'online' : 'offline'}`;
    statusText.textContent = statusData.status.charAt(0).toUpperCase() + statusData.status.slice(1);
    
    // Update latency if online
    if (statusData.status === 'online' && latencyText) {
        latencyText.textContent = `Latency: ${statusData.latency}ms`;
    }
    
    // Update stats if available
    if (statsSection && statusData.stats) {
        document.querySelector('.stat-value.uptime').textContent = formatDuration(statusData.stats.uptime);
        document.querySelector('.stat-value.servers').textContent = statusData.stats.active_servers_count;
        document.querySelector('.stat-value.members').textContent = statusData.stats.total_members;
        document.querySelector('.stat-value.commands').textContent = statusData.stats.commands_today;
    }
    
    // Update button states
    document.querySelector('button[onclick="startBot()"]').disabled = statusData.status === 'online';
    document.querySelector('button[onclick="stopBot()"]').disabled = statusData.status === 'offline';
    document.querySelector('button[onclick="restartBot()"]').disabled = statusData.status === 'offline';
};

const toggleWorkflow = async (workflowId) => {
    const checkbox = document.getElementById(`workflow-${workflowId}`);
    const enabled = checkbox.checked;
    
    try {
        await apiRequest(`/api/owner/bot/workflows/${workflowId}/toggle`, {
            method: 'PUT',
            body: JSON.stringify({ enabled }),
        });
        
        showToast('success', `Workflow ${enabled ? 'enabled' : 'disabled'} successfully`);
    } catch (error) {
        checkbox.checked = !enabled; // Revert checkbox state
        // Error already handled by apiRequest
    }
};

// Set up periodic status updates
document.addEventListener('DOMContentLoaded', () => {
    updateBotStatus(); // Initial status update
    setInterval(updateBotStatus, 30000); // Update every 30 seconds
}); 