import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

// Server Selector Component
export class ServerSelector {
    constructor() {
        this.button = document.getElementById('guild-selector-button');
        this.dropdown = document.getElementById('guild-selector-dropdown');
        this.serverList = document.getElementById('server-list');
        this.currentGuildId = null;

        // Check if essential elements exist before proceeding
        if (!this.button || !this.dropdown || !this.serverList) {
            console.warn('ServerSelector: Required HTML elements not found. Skipping initialization.');
            // Optionally log which elements are missing
            // console.debug('Missing elements:', { 
            //     button: !this.button, 
            //     dropdown: !this.dropdown, 
            //     serverList: !this.serverList 
            // });
            return; // Stop initialization if elements are missing
        }

        this.init();
    }

    init() {
        // Check again (defensive programming)
        if (!this.button || !this.dropdown || !this.serverList) {
             console.error("ServerSelector init called without required elements.");
             return;
        }
        
        console.log('Initializing ServerSelector');
        this.setupEventListeners();
        this.loadServers();
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
            
            // --- Safely set currentGuildId ---
            this.currentGuildId = null; // Default to null
            if (currentServer && currentServer.guild_id) {
                this.currentGuildId = currentServer.guild_id;
                // Update button only if we have a current server
                const button = document.getElementById('guild-selector-button');
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
            // --- End safe handling ---
            
            // Fetch ALL servers
            const response = await apiRequest('/api/v1/servers');
            console.log('Raw API Response for /api/v1/servers:', response);
            
            // Adjust based on actual response structure - assuming response IS the array for now
            const servers = response || []; 
            console.log('Servers array used for filtering:', servers);

            // Filter for approved servers only
            const approvedServers = servers.filter(server => server?.access_status === 'approved');
            console.log('Approved servers after filtering:', approvedServers);
            
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
            throw error; // Let apiRequest handle the error display
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
            const button = document.getElementById('guild-selector-button');
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

            // --- Revised Redirect Logic ---
            const currentPathname = window.location.pathname;
            const currentSearch = window.location.search; 
            const currentHash = window.location.hash;     

            // Regex to find /guild/ followed by digits, ending with / or end of string
            const guildPathRegex = /^(\/guild\/)\d+(\/|$)/;
            
            if (guildPathRegex.test(currentPathname)) {
                // If current path IS a guild path, replace ID and redirect
                const newPathname = currentPathname.replace(guildPathRegex, `$1${server.guild_id}$2`);
                console.log(`Redirecting: Keeping guild structure, new path: ${newPathname}`);
                // Combine the new path with original search params and hash
                window.location.href = newPathname + currentSearch + currentHash;
            } else {
                // If current path IS NOT a guild path (e.g., /home, /owner/), DO NOT REDIRECT.
                // The selector UI has updated, and the session on the backend is updated.
                // The user stays on the current page.
                console.log(`No redirect: Current path (${currentPathname}) is not a guild-specific path. Guild context updated.`);
            }
            // --- End Revised Redirect Logic ---
            
        } catch (error) {
            throw error; // Let apiRequest handle the error display
        }
    }
}

// Initialize when DOM is loaded
if (!window.guildSelector) {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, initializing GuildSelector');
        window.guildSelector = new ServerSelector();
    });
} 