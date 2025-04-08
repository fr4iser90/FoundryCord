import { showToast, apiRequest, formatDuration } from '/static/js/components/common/notifications.js';

class BotControls {
    constructor() {
        // Initialize instance variables
        this.statusInterval = null;
        this.initialized = false;
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        if (this.initialized) return;
        console.log('Initializing bot controls...');
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Initial status update
        this.updateBotStatus();
        
        // Set up periodic status updates
        this.statusInterval = setInterval(() => this.updateBotStatus(), 30000);
        
        this.initialized = true;
    }

    async startBot() {
        try {
            console.log('Starting bot...');
            await apiRequest('/api/v1/owner/bot/start', { 
                method: 'POST'
            });
            showToast('success', 'Bot started successfully');
            await this.updateBotStatus();
        } catch (error) {
            console.error('Start bot error:', error);
            showToast('error', `Failed to start bot: ${error.message}`);
        }
    }

    async stopBot() {
        try {
            console.log('Stopping bot...');
            await apiRequest('/api/v1/owner/bot/stop', { 
                method: 'POST'
            });
            showToast('success', 'Bot stopped successfully');
            await this.updateBotStatus();
        } catch (error) {
            console.error('Stop bot error:', error);
            showToast('error', `Failed to stop bot: ${error.message}`);
        }
    }

    async restartBot() {
        try {
            console.log('Restarting bot...');
            await apiRequest('/api/v1/owner/bot/restart', { 
                method: 'POST'
            });
            showToast('success', 'Bot restarting...');
            // Wait 5 seconds before checking status to allow for restart
            setTimeout(() => this.updateBotStatus(), 5000);
        } catch (error) {
            console.error('Restart bot error:', error);
            showToast('error', `Failed to restart bot: ${error.message}`);
        }
    }

    async updateBotStatus() {
        try {
            console.log('Fetching bot status...');
            const data = await apiRequest('/api/v1/owner/bot/status');
            console.log('Bot status data:', data);
            this.updateStatusUI(data);
        } catch (error) {
            console.error('Failed to update bot status:', error);
            this.updateStatusUI({ 
                status: 'offline', 
                latency: 0,
                uptime: 0,
                guilds: 0,
                total_members: 0,
                commands_today: 0
            });
        }
    }

    updateStatusUI(statusData) {
        console.log('Updating status UI with:', statusData);
        
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        const latencyText = document.querySelector('.text-muted');
        const statsSection = document.querySelector('.bot-stats');
        
        if (!statusIndicator || !statusText) {
            console.error('Status elements not found');
            return;
        }
        
        // Update status indicator and text
        statusIndicator.className = `status-indicator ${statusData.status}`;
        statusText.textContent = statusData.status.charAt(0).toUpperCase() + statusData.status.slice(1);
        
        // Update latency if available
        if (latencyText && statusData.latency !== undefined) {
            latencyText.textContent = `(${Math.round(statusData.latency)}ms)`;
        }
        
        // Update button states
        document.querySelectorAll('[data-action]').forEach(button => {
            const action = button.dataset.action;
            if (action === 'start') {
                button.disabled = statusData.status === 'online';
            } else {
                button.disabled = statusData.status === 'offline';
            }
        });
        
        // Update stats if available
        if (statsSection && statusData.status === 'online') {
            statsSection.style.display = 'block';
            
            // Update each stat if the element exists
            const stats = {
                'uptime': formatDuration(statusData.uptime || 0),
                'servers': statusData.guilds || 0,
                'members': statusData.total_members || 0,
                'commands': statusData.commands_today || 0
            };
            
            Object.entries(stats).forEach(([key, value]) => {
                const element = document.querySelector(`[data-stat="${key}"]`);
                if (element) {
                    element.textContent = value;
                }
            });
        } else if (statsSection) {
            statsSection.style.display = 'none';
        }
    }

    initializeEventListeners() {
        console.log('Initializing event listeners...');
        
        // Add event listeners for bot control buttons using arrow functions to preserve 'this'
        document.querySelectorAll('[data-action]').forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                const action = event.currentTarget.dataset.action;
                console.log('Handling action:', action);
                
                switch (action) {
                    case 'start':
                        this.startBot();
                        break;
                    case 'stop':
                        this.stopBot();
                        break;
                    case 'restart':
                        this.restartBot();
                        break;
                }
            });
        });
    }
}

// Create and export a single instance
export const botControls = new BotControls(); 