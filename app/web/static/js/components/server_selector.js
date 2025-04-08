import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

// Server Selector Component
export class ServerSelector {
    constructor() {
        console.log('Initializing ServerSelector');
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        // Find required elements
        this.button = document.getElementById('server-selector-button');
        this.dropdown = document.getElementById('server-dropdown');
        this.serverList = this.dropdown?.querySelector('.server-list');
        
        if (this.button && this.dropdown && this.serverList) {
            console.log('Found all required elements');
            this.setupEventListeners();
            this.loadServers();
        } else {
            console.error('Missing required elements:', {
                button: !!this.button,
                dropdown: !!this.dropdown,
                serverList: !!this.serverList
            });
        }
    }

    setupEventListeners() {
        // Toggle dropdown on button click
        this.button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Toggle dropdown');
            this.dropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (event) => {
            if (!this.button.contains(event.target) && !this.dropdown.contains(event.target)) {
                this.dropdown.classList.remove('show');
            }
        });
    }

    async loadServers() {
        try {
            console.log('Loading servers...');
            this.serverList.classList.add('loading');
            
            // Get current server first
            const currentServer = await apiRequest('/api/v1/servers/current');
            this.currentGuildId = currentServer.guild_id;
            
            // Update button if we have a current server
            if (currentServer && currentServer.guild_id) {
                const button = document.getElementById('server-selector-button');
                if (button) {
                    const img = button.querySelector('img');
                    const span = button.querySelector('span');
                    if (img) {
                        img.src = currentServer.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png';
                        img.alt = currentServer.name;
                    }
                    if (span) {
                        span.textContent = currentServer.name;
                    }
                }
            }
            
            const servers = await apiRequest('/api/v1/servers');
            console.log('Servers loaded:', servers);
            
            // Filter for approved servers only
            const approvedServers = servers.filter(server => {
                console.log('Checking server:', server);
                return server && server.access_status === 'approved';
            });
            
            this.serverList.classList.remove('loading');
            if (approvedServers.length === 0) {
                this.serverList.classList.add('empty');
                this.serverList.innerHTML = '<div class="server-list-item">No approved servers available</div>';
                return;
            }
            
            this.updateServerList(approvedServers);
        } catch (error) {
            console.error('Error loading servers:', error);
            this.serverList.classList.remove('loading');
            this.serverList.innerHTML = '<div class="server-list-item">Error loading servers</div>';
            showToast('error', 'Failed to load servers');
        }
    }

    updateServerList(servers) {
        console.log('Updating server list with:', servers);
        this.serverList.innerHTML = '';
        
        if (!Array.isArray(servers) || servers.length === 0) {
            this.serverList.classList.add('empty');
            this.serverList.innerHTML = '<div class="server-list-item">No servers available</div>';
            return;
        }

        // Sort servers to put current server first
        const sortedServers = [...servers].sort((a, b) => {
            if (a.guild_id === this.currentGuildId) return -1;
            if (b.guild_id === this.currentGuildId) return 1;
            return 0;
        });

        this.serverList.classList.remove('empty');
        sortedServers.forEach(server => {
            const serverItem = document.createElement('div');
            serverItem.className = 'server-list-item';
            if (server.guild_id === this.currentGuildId) {
                serverItem.classList.add('active');
            }
            serverItem.innerHTML = `
                <img src="${server.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                     alt="${server.name}" 
                     class="server-icon">
                <div class="server-info">
                    <div class="server-name">${server.name}</div>
                    <div class="server-id">${server.guild_id}</div>
                </div>
                ${server.guild_id === this.currentGuildId ? '<div class="active-indicator"><i class="bi bi-check2"></i></div>' : ''}
            `;
            
            serverItem.addEventListener('click', () => this.switchServer(server));
            this.serverList.appendChild(serverItem);
        });
    }

    async switchServer(server) {
        try {
            console.log('Switching to server:', server);
            await apiRequest(`/api/v1/servers/select/${server.guild_id}`, {
                method: 'POST'
            });

            // Update UI immediately
            const button = document.getElementById('server-selector-button');
            if (button) {
                const img = button.querySelector('img');
                const span = button.querySelector('span');
                if (img) {
                    img.src = server.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png';
                    img.alt = server.name;
                }
                if (span) {
                    span.textContent = server.name;
                }
            }
            
            this.currentGuildId = server.guild_id;
            this.dropdown.classList.remove('show');
            
            showToast('success', `Switched to server: ${server.name}`);

            // Reload page to update content
            window.location.reload();
        } catch (error) {
            console.error('Error switching server:', error);
            showToast('error', 'Failed to switch server. Please try again.');
        }
    }
}

// Initialize when DOM is loaded
if (!window.serverSelector) {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, initializing ServerSelector');
        window.serverSelector = new ServerSelector();
    });
} 