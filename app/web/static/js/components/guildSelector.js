import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

// Guild Selector Component
export class GuildSelector {
    constructor() {
        this.button = document.getElementById('guild-selector-button');
        this.dropdown = document.getElementById('guild-selector-dropdown');
        this.guildList = document.getElementById('guild-list');
        this.currentGuildId = null;

        // Check if essential elements exist before proceeding
        if (!this.button || !this.dropdown || !this.guildList) {
            console.warn('GuildSelector: Required HTML elements not found. Skipping initialization.');
            // Optionally log which elements are missing
            // console.debug('Missing elements:', { 
            //     button: !this.button, 
            //     dropdown: !this.dropdown, 
            //     guildList: !this.guildList 
            // });
            return; // Stop initialization if elements are missing
        }

        this.init();
    }

    init() {
        // Check again (defensive programming)
        if (!this.button || !this.dropdown || !this.guildList) {
             console.error("GuildSelector init called without required elements.");
             return;
        }
        
        console.log('Initializing GuildSelector');
        this.setupEventListeners();
        this.loadGuilds();
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

    async loadGuilds() {
        try {
            console.log('Loading guilds...');
            this.guildList.classList.add('loading');
            
            // Get current guild first
            const currentGuild = await apiRequest('/api/v1/guilds/current');
            
            // --- Safely set currentGuildId ---
            this.currentGuildId = null; // Default to null
            if (currentGuild && currentGuild.guild_id) {
                this.currentGuildId = currentGuild.guild_id;
                // Update button only if we have a current guild
                const button = document.getElementById('guild-selector-button');
                if (button) {
                    const img = button.querySelector('img');
                    const span = button.querySelector('span');
                    if (img) {
                        img.src = currentGuild.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png';
                        img.alt = currentGuild.name;
                    }
                    if (span) {
                        span.textContent = currentGuild.name;
                    }
                }
            }
            // --- End safe handling ---
            
            // Fetch ALL available guilds
            const response = await apiRequest('/api/v1/guilds/');
            console.log('Raw API Response for /api/v1/guilds/:', response);
            
            // Adjust based on actual response structure - assuming response IS the array 
            const guilds = response || [];
            console.log('Guilds array used for filtering:', guilds);

            // No need to filter for 'approved' here, as the backend /api/v1/guilds endpoint already returns only available (approved) guilds
            const availableGuilds = guilds;
            console.log('Available guilds:', availableGuilds);
            
            this.guildList.classList.remove('loading');
            if (availableGuilds.length === 0) {
                this.guildList.classList.add('empty');
                this.guildList.innerHTML = '<div class="guild-list-item">No available guilds</div>';
                return;
            }
            
            this.updateGuildList(availableGuilds);
        } catch (error) {
            console.error('Error loading guilds:', error);
            this.guildList.classList.remove('loading');
            this.guildList.innerHTML = '<div class="guild-list-item">Error loading guilds</div>';
            throw error; // Let apiRequest handle the error display
        }
    }

    updateGuildList(guilds) {
        console.log('Updating guild list with:', guilds);
        this.guildList.innerHTML = '';
        
        if (!Array.isArray(guilds) || guilds.length === 0) {
            this.guildList.classList.add('empty');
            this.guildList.innerHTML = '<div class="guild-list-item">No guilds available</div>';
            return;
        }

        // Sort guilds to put current guild first
        const sortedGuilds = [...guilds].sort((a, b) => {
            if (a.guild_id === this.currentGuildId) return -1;
            if (b.guild_id === this.currentGuildId) return 1;
            return a.name.localeCompare(b.name);
        });

        this.guildList.classList.remove('empty');
        sortedGuilds.forEach(guild => {
            const guildItem = document.createElement('div');
            guildItem.className = 'guild-list-item';
            if (guild.guild_id === this.currentGuildId) {
                guildItem.classList.add('active');
            }
            guildItem.innerHTML = `
                <img src="${guild.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                     alt="${guild.name}" 
                     class="guild-icon">
                <div class="guild-info">
                    <div class="guild-name">${guild.name}</div>
                    <div class="guild-id">${guild.guild_id}</div>
                </div>
                ${guild.guild_id === this.currentGuildId ? '<div class="active-indicator"><i class="bi bi-check2"></i></div>' : ''}
            `;
            
            guildItem.addEventListener('click', () => this.switchGuild(guild));
            this.guildList.appendChild(guildItem);
        });
    }

    async switchGuild(guild) {
        try {
            console.log('Switching to guild:', guild);
            await apiRequest(`/api/v1/guilds/select/${guild.guild_id}`, {
                method: 'POST'
            });

            // Update UI immediately
            const button = document.getElementById('guild-selector-button');
            if (button) {
                const img = button.querySelector('img');
                const span = button.querySelector('span');
                if (img) {
                    img.src = guild.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png';
                    img.alt = guild.name;
                }
                if (span) {
                    span.textContent = guild.name;
                }
            }
            
            this.currentGuildId = guild.guild_id;
            this.dropdown.classList.remove('show');
            
            showToast('success', `Switched to guild: ${guild.name}`);

            // --- Revised Redirect Logic ---
            const currentPathname = window.location.pathname;
            const currentSearch = window.location.search; 
            const currentHash = window.location.hash;     

            // Regex to find /guild/ followed by digits, ending with / or end of string
            const guildPathRegex = /^(\/guild\/)\d+(\/|$)/;
            
            if (guildPathRegex.test(currentPathname)) {
                // If current path IS a guild path, replace ID and redirect
                const newPathname = currentPathname.replace(guildPathRegex, `$1${guild.guild_id}$2`);
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
        window.guildSelector = new GuildSelector();
    });
} 