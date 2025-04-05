document.addEventListener('DOMContentLoaded', function() {
    // Format date helper function
    function formatDate(isoString) {
        if (!isoString) return 'Never';
        
        try {
            const date = new Date(isoString);
            if (isNaN(date.getTime())) return 'Invalid Date';
            
            return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
        } catch (e) {
            console.error('Error formatting date:', e);
            return 'Invalid Date';
        }
    }

    // Initialize components
    const searchInput = document.querySelector('.search-box input');
    const guildFilter = document.querySelector('#guild-filter');
    const roleSelect = document.querySelector('#role-select');
    const statusToggle = document.querySelector('#status-toggle');
    
    // User details modal
    function showUserDetails(userId) {
        const userRow = document.querySelector(`tr[data-user-id="${userId}"]`);
        if (!userRow) return;
        
        const userData = {
            id: userId,
            username: userRow.querySelector('.username').textContent,
            created_at: userRow.dataset.createdAt,
            last_active: userRow.dataset.lastActive,
            guilds: JSON.parse(userRow.dataset.guilds || '[]')
        };
        
        const modalContent = `
            <div class="user-details-modal">
                <h3>${userData.username}</h3>
                <div class="user-info-grid">
                    <div class="info-item">
                        <label>Discord ID:</label>
                        <span>${userData.id}</span>
                    </div>
                    <div class="info-item">
                        <label>Created At:</label>
                        <span>${formatDate(userData.created_at)}</span>
                    </div>
                    <div class="info-item">
                        <label>Last Active:</label>
                        <span>${formatDate(userData.last_active)}</span>
                    </div>
                </div>
                <div class="guild-memberships">
                    <h4>Guild Memberships</h4>
                    ${userData.guilds.map(guild => `
                        <div class="guild-item">
                            <div class="guild-header">
                                <span class="guild-name">${guild.name}</span>
                                <span class="guild-role">${guild.role}</span>
                            </div>
                            <div class="guild-dates">
                                <span>Joined: ${formatDate(guild.joined_at)}</span>
                                <span>Last Active: ${formatDate(guild.last_active)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Show modal with content
        showModal('User Details', modalContent);
    }
    
    // Event Listeners
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            filterUsers(e.target.value);
        }, 300));
    }
    
    if (guildFilter) {
        guildFilter.addEventListener('change', function() {
            filterUsers();
        });
    }
    
    if (roleSelect) {
        roleSelect.addEventListener('change', function(e) {
            const userId = e.target.closest('tr').dataset.userId;
            updateUserRole(userId, e.target.value);
        });
    }
    
    if (statusToggle) {
        statusToggle.addEventListener('change', function(e) {
            const userId = e.target.closest('tr').dataset.userId;
            updateUserStatus(userId, e.target.checked);
        });
    }
    
    // Attach click handlers for user details
    document.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.closest('tr').dataset.userId;
            showUserDetails(userId);
        });
    });
    
    // Helper Functions
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    function filterUsers(searchTerm = '') {
        const rows = document.querySelectorAll('table tbody tr');
        const guildId = guildFilter ? guildFilter.value : '';
        
        rows.forEach(row => {
            const username = row.querySelector('.username').textContent.toLowerCase();
            const userGuilds = JSON.parse(row.dataset.guilds || '[]');
            
            const matchesSearch = !searchTerm || username.includes(searchTerm.toLowerCase());
            const matchesGuild = !guildId || userGuilds.some(g => g.id === guildId);
            
            row.style.display = matchesSearch && matchesGuild ? '' : 'none';
        });
    }
    
    async function updateUserRole(userId, newRole) {
        try {
            const response = await fetch(`/api/v1/admin/users/${userId}/role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ role: newRole })
            });
            
            if (!response.ok) throw new Error('Failed to update role');
            
            showToast('Role updated successfully', 'success');
        } catch (error) {
            console.error('Error updating role:', error);
            showToast('Failed to update role', 'error');
        }
    }
    
    async function updateUserStatus(userId, isActive) {
        try {
            const response = await fetch(`/api/v1/admin/users/${userId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ active: isActive })
            });
            
            if (!response.ok) throw new Error('Failed to update status');
            
            showToast('Status updated successfully', 'success');
        } catch (error) {
            console.error('Error updating status:', error);
            showToast('Failed to update status', 'error');
        }
    }
    
    function showToast(message, type = 'info') {
        // Implementation depends on your toast notification system
        console.log(`${type}: ${message}`);
    }
    
    function showModal(title, content) {
        // Implementation depends on your modal system
        console.log('Show modal:', title, content);
    }
});

