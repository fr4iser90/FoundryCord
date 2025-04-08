import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

// Server Selector Component
class ServerSelector {
    constructor() {
        this.button = document.getElementById('server-selector-button');
        this.dropdown = document.getElementById('server-dropdown');
        this.serverList = this.dropdown?.querySelector('.server-list');
        
        if (this.button && this.dropdown && this.serverList) {
            this.setupEventListeners();
            this.loadServers();
        }
    }

    setupEventListeners() {
        // Toggle dropdown on button click
        this.button.addEventListener('click', () => {
            this.dropdown.classList.toggle('is-active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (event) => {
            if (!this.button.contains(event.target) && !this.dropdown.contains(event.target)) {
                this.dropdown.classList.remove('is-active');
            }
        });
    }

    async loadServers() {
        try {
            const response = await apiRequest('/api/servers/list');
            const servers = response.filter(server => server.status === 'APPROVED');
            this.updateServerList(servers);
        } catch (error) {
            console.error('Error loading servers:', error);
            this.serverList.innerHTML = '<div class="navbar-item">Error loading servers</div>';
        }
    }

    updateServerList(servers) {
        this.serverList.innerHTML = '';
        if (servers.length === 0) {
            this.serverList.innerHTML = '<div class="navbar-item">No approved servers available</div>';
            return;
        }

        servers.forEach(server => {
            const serverItem = document.createElement('a');
            serverItem.className = 'navbar-item server-item';
            serverItem.innerHTML = `
                <img src="${server.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                     alt="${server.name}" 
                     class="server-icon">
                <span>${server.name}</span>
            `;
            serverItem.addEventListener('click', () => this.switchServer(server));
            this.serverList.appendChild(serverItem);
        });
    }

    async switchServer(server) {
        if (server.status !== 'APPROVED') {
            console.error('Cannot switch to non-approved server');
            return;
        }

        try {
            await apiRequest(`/api/servers/switch/${server.id}`, {
                method: 'POST'
            });

            // Update UI
            if (this.button.querySelector('img')) {
                this.button.querySelector('img').src = server.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png';
            }
            if (this.button.querySelector('span')) {
                this.button.querySelector('span').textContent = server.name;
            }
            this.dropdown.classList.remove('is-active');

            // Reload page to update content
            window.location.reload();
        } catch (error) {
            console.error('Error switching server:', error);
            showToast('error', 'Failed to switch server');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ServerSelector();
}); 