import { showToast, apiRequest, formatDuration } from '/static/js/components/common/notifications.js';

// Bot Control Functions
const startBot = async () => {
    try {
        await apiRequest('/api/v1/owner/bot/control/start', { method: 'POST' });
        showToast('success', 'Bot started successfully');
        updateBotStatus();
    } catch (error) {
        showToast('error', `Failed to start bot: ${error.message}`);
    }
};

const stopBot = async () => {
    try {
        await apiRequest('/api/v1/owner/bot/control/stop', { method: 'POST' });
        showToast('success', 'Bot stopped successfully');
        updateBotStatus();
    } catch (error) {
        showToast('error', `Failed to stop bot: ${error.message}`);
    }
};

const restartBot = async () => {
    try {
        await apiRequest('/api/v1/owner/bot/control/restart', { method: 'POST' });
        showToast('success', 'Bot restarting...');
        setTimeout(updateBotStatus, 5000); // Check status after 5 seconds
    } catch (error) {
        showToast('error', `Failed to restart bot: ${error.message}`);
    }
};

const updateBotStatus = async () => {
    try {
        const data = await apiRequest('/api/v1/owner/bot/status');
        updateStatusUI(data);
    } catch (error) {
        console.error('Failed to update bot status:', error);
        updateStatusUI({ status: 'offline', latency: 0 });
    }
};

const updateStatusUI = (statusData) => {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');
    const latencyText = document.querySelector('.text-muted');
    const statsSection = document.querySelector('.bot-stats');
    const startButton = document.querySelector('button[onclick="startBot()"]');
    const stopButton = document.querySelector('button[onclick="stopBot()"]');
    const restartButton = document.querySelector('button[onclick="restartBot()"]');
    
    if (!statusIndicator || !statusText) return;
    
    // Update status indicator and text
    statusIndicator.className = `status-indicator ${statusData.status === 'online' ? 'online' : 'offline'}`;
    statusText.textContent = statusData.status.charAt(0).toUpperCase() + statusData.status.slice(1);
    
    // Update latency if online
    if (statusData.status === 'online' && latencyText) {
        latencyText.textContent = `Latency: ${statusData.latency}ms`;
    }
    
    // Update stats if available
    if (statsSection && statusData.stats) {
        const uptimeElement = document.querySelector('.stat-value[data-stat="uptime"]');
        const serversElement = document.querySelector('.stat-value[data-stat="servers"]');
        const membersElement = document.querySelector('.stat-value[data-stat="members"]');
        const commandsElement = document.querySelector('.stat-value[data-stat="commands"]');
        
        if (uptimeElement) uptimeElement.textContent = formatDuration(statusData.stats.uptime);
        if (serversElement) serversElement.textContent = statusData.stats.active_servers_count;
        if (membersElement) membersElement.textContent = statusData.stats.total_members;
        if (commandsElement) commandsElement.textContent = statusData.stats.commands_today;
    }
    
    // Update button states
    if (startButton) startButton.disabled = statusData.status === 'online';
    if (stopButton) stopButton.disabled = statusData.status === 'offline';
    if (restartButton) restartButton.disabled = statusData.status === 'offline';
    
    // Show/hide stats section
    if (statsSection) {
        statsSection.style.display = statusData.status === 'online' ? 'block' : 'none';
    }
};

const toggleWorkflow = async (workflowId) => {
    const checkbox = document.getElementById(`workflow-${workflowId}`);
    if (!checkbox) return;
    
    const enabled = checkbox.checked;
    
    try {
        await apiRequest(`/api/v1/owner/bot/workflows/${workflowId}/toggle`, {
            method: 'PUT',
            body: JSON.stringify({ enabled }),
        });
        
        showToast('success', `Workflow ${enabled ? 'enabled' : 'disabled'} successfully`);
    } catch (error) {
        checkbox.checked = !enabled; // Revert checkbox state
        showToast('error', `Failed to toggle workflow: ${error.message}`);
    }
};

// Initialize bot controls
document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners for bot control buttons
    document.querySelectorAll('[onclick^="startBot"]').forEach(button => {
        button.onclick = (e) => {
            e.preventDefault();
            startBot();
        };
    });

    document.querySelectorAll('[onclick^="stopBot"]').forEach(button => {
        button.onclick = (e) => {
            e.preventDefault();
            stopBot();
        };
    });

    document.querySelectorAll('[onclick^="restartBot"]').forEach(button => {
        button.onclick = (e) => {
            e.preventDefault();
            restartBot();
        };
    });

    // Add event listeners for workflow toggles
    document.querySelectorAll('[id^="workflow-"]').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const workflowId = e.target.id.replace('workflow-', '');
            toggleWorkflow(workflowId);
        });
    });

    // Initial status update
    updateBotStatus();
    // Set up periodic status updates
    setInterval(updateBotStatus, 30000); // Update every 30 seconds
}); 