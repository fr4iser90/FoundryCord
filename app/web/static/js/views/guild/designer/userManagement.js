document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeSearch();
    initializeRoleFilter();
    initializeRoleSelects();
    
    // Setup modals
    const userViewModal = new bootstrap.Modal(document.getElementById('userViewModal'));
    
    // Global state
    let currentFilters = {
        search: '',
        role: ''
    };
    
    function initializeSearch() {
        const searchInput = document.getElementById('user-search');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(function(e) {
                currentFilters.search = e.target.value.toLowerCase();
                filterUsers();
            }, 300));
        }
    }
    
    function initializeRoleFilter() {
        const roleFilter = document.getElementById('role-filter');
        if (roleFilter) {
            roleFilter.addEventListener('change', function(e) {
                currentFilters.role = e.target.value;
                filterUsers();
            });
        }
    }
    
    function initializeRoleSelects() {
        // Guild Role Selects
        document.querySelectorAll('.guild-role-select').forEach(select => {
            select.addEventListener('change', handleGuildRoleChange);
            select.dataset.originalValue = select.value;
        });
        
        // App Role Selects
        document.querySelectorAll('.app-role-select').forEach(select => {
            select.addEventListener('change', handleAppRoleChange);
            select.dataset.originalValue = select.value;
        });
    }
    
    async function handleGuildRoleChange(event) {
        const select = event.target;
        const userId = select.dataset.userId;
        const newRole = select.value;
        const guildId = document.body.dataset.guildId;
        
        try {
            const response = await fetch(`/api/v1/guild/users/${userId}/role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ role: newRole })
            });
            
            if (!response.ok) throw new Error('Failed to update role');
            
            const data = await response.json();
            showNotification(data.message || 'Role updated successfully', 'success');
            select.dataset.originalValue = newRole;
            
        } catch (error) {
            console.error('Error updating role:', error);
            showNotification('Failed to update role', 'error');
            select.value = select.dataset.originalValue;
        }
    }
    
    async function handleAppRoleChange(event) {
        const select = event.target;
        const userId = select.dataset.userId;
        const newRole = select.value;
        const guildId = document.body.dataset.guildId;
        
        try {
            const response = await fetch(`/api/v1/guild/users/${userId}/app-role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ role: newRole })
            });
            
            if (!response.ok) throw new Error('Failed to update app role');
            
            const data = await response.json();
            showNotification(data.message || 'App role updated successfully', 'success');
            select.dataset.originalValue = newRole;
            
        } catch (error) {
            console.error('Error updating app role:', error);
            showNotification('Failed to update app role', 'error');
            select.value = select.dataset.originalValue;
        }
    }
    
    async function viewUser(userId) {
        const guildId = document.body.dataset.guildId;
        
        try {
            const response = await fetch(`/api/v1/guild/users/${userId}`);
            if (!response.ok) throw new Error('Failed to fetch user details');
            
            const user = await response.json();
            const modalContent = document.getElementById('userViewContent');
            
            modalContent.innerHTML = `
                <div class="user-details-view">
                    <div class="user-header">
                        <img src="${user.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                             alt="" class="user-avatar-lg">
                        <div class="user-info-main">
                            <h3>${user.username}</h3>
                            <div class="user-meta">
                                <span class="discord-id">${user.discord_id}</span>
                                <span class="badge bg-primary">${user.guild_role}</span>
                            </div>
                        </div>
                    </div>
                    <div class="user-stats mt-4">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="stat-card">
                                    <h5>Joined Server</h5>
                                    <p>${new Date(user.guild_joined_at).toLocaleDateString()}</p>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="stat-card">
                                    <h5>Last Active</h5>
                                    <p>${user.last_active ? new Date(user.last_active).toLocaleDateString() : 'Never'}</p>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="stat-card">
                                    <h5>Messages</h5>
                                    <p>${user.message_count || 0}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="user-activity mt-4">
                        <h4>Recent Activity</h4>
                        <div class="activity-timeline">
                            ${user.recent_activity ? user.recent_activity.map(activity => `
                                <div class="activity-item">
                                    <div class="activity-time">
                                        ${new Date(activity.timestamp).toLocaleString()}
                                    </div>
                                    <div class="activity-content">
                                        <i class="bi ${getActivityIcon(activity.type)}"></i>
                                        ${activity.description}
                                    </div>
                                </div>
                            `).join('') : '<p class="text-muted">No recent activity</p>'}
                        </div>
                    </div>
                </div>
            `;
            
            userViewModal.show();
            
        } catch (error) {
            console.error('Error fetching user details:', error);
            showNotification('Failed to load user details', 'error');
        }
    }
    
    async function kickUser(userId) {
        if (!confirm('Are you sure you want to kick this user from the server?')) {
            return;
        }
        
        const guildId = document.body.dataset.guildId;
        
        try {
            const response = await fetch(`/api/v1/guild/users/${userId}/kick`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });
            
            if (!response.ok) throw new Error('Failed to kick user');
            
            const data = await response.json();
            showNotification(data.message || 'User kicked successfully', 'success');
            
            // Remove user row from table
            const userRow = document.querySelector(`tr[data-user-id="${userId}"]`);
            if (userRow) {
                userRow.remove();
            }
            
        } catch (error) {
            console.error('Error kicking user:', error);
            showNotification('Failed to kick user', 'error');
        }
    }
    
    function filterUsers() {
        const rows = document.querySelectorAll('.user-row');
        
        rows.forEach(row => {
            const username = row.querySelector('.username').textContent.toLowerCase();
            const discordId = row.querySelector('.discord-id').textContent.toLowerCase();
            const role = row.querySelector('.guild-role-select').value.toLowerCase();
            
            const matchesSearch = !currentFilters.search || 
                username.includes(currentFilters.search) || 
                discordId.includes(currentFilters.search);
                
            const matchesRole = !currentFilters.role || 
                role === currentFilters.role.toLowerCase();
            
            row.style.display = matchesSearch && matchesRole ? '' : 'none';
        });
    }
    
    function getActivityIcon(type) {
        const icons = {
            'message': 'bi-chat-text',
            'voice': 'bi-mic',
            'role_update': 'bi-person-gear',
            'join': 'bi-box-arrow-in-right',
            'leave': 'bi-box-arrow-left',
            'timeout': 'bi-hourglass-split',
            'kick': 'bi-door-closed',
            'ban': 'bi-shield-x'
        };
        
        return icons[type] || 'bi-asterisk';
    }
    
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    }
    
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    function showNotification(message, type = 'info') {
        // Check if we have a notification system
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            const toastContainer = document.getElementById('toast-container') || createToastContainer();
            
            const toast = document.createElement('div');
            toast.className = `toast align-items-center text-white bg-${type} border-0`;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;
            
            toastContainer.appendChild(toast);
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        }
    }
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }
    
    // Expose necessary functions
    window.viewUser = viewUser;
    window.kickUser = kickUser;
}); 