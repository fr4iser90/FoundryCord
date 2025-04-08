// Server Selector Component
class ServerSelector {
    constructor() {
        console.log('Initializing ServerSelector');
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
            const response = await fetch('/api/v1/owner/servers', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const servers = await response.json();
            console.log('Servers loaded:', servers);
            const approvedServers = servers.filter(server => 
                server.access_status.toLowerCase() === 'approved'
            );
            this.updateServerList(approvedServers);
        } catch (error) {
            console.error('Error loading servers:', error);
            this.serverList.innerHTML = '<div class="navbar-item">Error loading servers</div>';
        }
    }

    updateServerList(servers) {
        console.log('Updating server list with:', servers);
        this.serverList.innerHTML = '';
        
        if (!Array.isArray(servers) || servers.length === 0) {
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
            serverItem.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchServer(server);
            });
            this.serverList.appendChild(serverItem);
        });
    }

    async switchServer(server) {
        try {
            console.log('Switching to server:', server);
            const response = await fetch(`/api/v1/owner/servers/${server.guild_id}/select`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Update UI
            if (this.button.querySelector('img')) {
                this.button.querySelector('img').src = server.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png';
            }
            if (this.button.querySelector('span')) {
                this.button.querySelector('span').textContent = server.name;
            }
            this.dropdown.classList.remove('show');

            // Reload page to update content
            window.location.reload();
        } catch (error) {
            console.error('Error switching server:', error);
            alert('Failed to switch server');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing ServerSelector');
    new ServerSelector();
}); 