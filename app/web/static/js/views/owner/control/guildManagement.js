import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

// Helper function to format date/time or return 'N/A'
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    try {
        // Assuming dateString is in ISO format or similar
        return new Date(dateString).toLocaleString(); 
    } catch (e) {
        console.warn("Could not parse date:", dateString);
        return 'Invalid Date';
    }
}

// Guild Management Functions
// Renamed function
async function refreshGuildList() {
    try {
        showToast('info', 'Refreshing guild list...');
        // Call the new endpoint that returns all manageable guilds
        // The endpoint now returns the list directly due to response_model
        const guilds = await apiRequest('/api/v1/owner/guilds/manageable'); // Updated endpoint
        
        // Check if guilds is actually an array
        if (!Array.isArray(guilds)) {
            console.error('API did not return an array of guilds:', guilds);
            showToast('error', 'Received invalid data structure from API.');
            return; 
        }
        
        // Update the total guild count badge
        const countBadge = document.getElementById('total-guild-count'); // Updated ID
        if (countBadge) {
            countBadge.textContent = guilds.length;
        }

        // Update the single table with all guilds
        updateGuildList('all-guilds-tbody', guilds); // Target the new tbody ID, pass guilds
        
        showToast('success', 'Guild list updated');
    } catch (error) {
        console.error('Guild refresh error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Could not refresh guilds';
        showToast('error', errorMessage);
    }
}

// Updated function name and parameter
function updateGuildList(tbodyId, guilds) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) {
        console.warn(`Table body ${tbodyId} not found`);
        return;
    }

    // Clear existing rows
    tbody.innerHTML = '';

    if (guilds.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No guilds found</td></tr>'; // Updated text
        return;
    }

    guilds.forEach(guild => { // Updated variable
        const row = document.createElement('tr');
        
        // Determine the appropriate date to show based on status
        let lastUpdatedDate = guild.access_reviewed_at || guild.access_requested_at || guild.created_at; // Updated variable
        
        // Updated CSS classes and variables
        row.innerHTML = `
            <td class="d-flex align-items-center">
                <div class="me-2">
                    ${guild.icon_url 
                        ? `<img src="${guild.icon_url}" alt="" class="guild-icon rounded" width="32" height="32" onerror="this.src='/static/img/discord_default.png'">` 
                        : `<div class="guild-icon-placeholder rounded">${guild.name ? guild.name.charAt(0).toUpperCase() : 'G'}</div>` 
                    }
                </div>
                <div>
                    <div class="guild-name fw-bold">${guild.name}</div>
                    <small class="text-muted">${guild.guild_id}</small>
                </div>
            </td>
            <td>${getStatusBadge(guild.access_status)}</td>
            <td>${guild.member_count || 0}</td>
            <td>${formatDateTime(lastUpdatedDate)}</td>
            <td>${getActionButtons(guild)}</td> 
        `;
        tbody.appendChild(row);
    });
}

function getStatusBadge(status) {
    const statusMap = {
        'pending': '<span class="badge bg-warning text-dark"><i class="bi bi-clock"></i> Pending</span>',
        'approved': '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Approved</span>',
        'rejected': '<span class="badge bg-danger"><i class="bi bi-x-circle"></i> Rejected</span>',
        'banned': '<span class="badge bg-danger"><i class="bi bi-ban"></i> Banned</span>', // Use banned
        'suspended': '<span class="badge bg-secondary"><i class="bi bi-pause-circle"></i> Suspended</span>'
    };
    // Ensure status is checked case-insensitively if needed, though backend likely provides lowercase
    return statusMap[status?.toLowerCase()] || '<span class="badge bg-secondary"><i class="bi bi-question-circle"></i> Unknown</span>';
}

// Updated parameter name
function getActionButtons(guild) {
    const status = guild.access_status ? guild.access_status.toLowerCase() : 'unknown';
    let buttons = '';

    // Always show details button
    buttons += `
        <button data-action="details" data-guild-id="${guild.guild_id}" class="btn btn-info btn-sm" title="Details">
            <i class="bi bi-info-circle"></i>
        </button>
    `;

    if (status === 'pending') {
        buttons += `
            <button data-action="approve" data-guild-id="${guild.guild_id}" class="btn btn-success btn-sm" title="Approve">
                <i class="bi bi-check-lg"></i>
            </button>
            <button data-action="reject" data-guild-id="${guild.guild_id}" class="btn btn-danger btn-sm" title="Reject">
                <i class="bi bi-x-lg"></i>
            </button>
        `;
    } else if (status === 'approved') {
        buttons += `
            <button data-action="suspend" data-guild-id="${guild.guild_id}" class="btn btn-warning btn-sm" title="Suspend">
                <i class="bi bi-pause-circle"></i>
            </button>
            <button data-action="ban" data-guild-id="${guild.guild_id}" class="btn btn-danger btn-sm" title="Ban">
                <i class="bi bi-ban"></i>
            </button>
        `;
    } else if (status === 'rejected' || status === 'banned' || status === 'suspended') {
        buttons += `
            <button data-action="approve" data-guild-id="${guild.guild_id}" class="btn btn-success btn-sm" title="Re-Approve">
                <i class="bi bi-check-lg"></i>
            </button>
        `;
         // Allow banning from rejected/suspended state
         if (status !== 'banned') { 
             buttons += `
                 <button data-action="ban" data-guild-id="${guild.guild_id}" class="btn btn-danger btn-sm" title="Ban">
                     <i class="bi bi-ban"></i>
                 </button>
             `;
         }
    }
    // Add other status cases if needed

    return `<div class="btn-group">${buttons}</div>`;
}

async function updateAccess(guildId, status) {
    try {
        showToast('info', `Setting guild ${guildId} status to ${status}...`); // Updated text
        
        await apiRequest(`/api/v1/owner/guilds/${guildId}/access`, { // Updated endpoint
            method: 'POST',
            body: JSON.stringify({ status: status.toLowerCase() })
        });
        
        showToast('success', `Guild status updated to ${status}`); // Updated text
        await refreshGuildList(); // Refresh the owner's table (renamed function)
        
        // Also refresh the global guild selector dropdown
        if (window.guildSelector && typeof window.guildSelector.loadGuilds === 'function') { // Updated method name
            console.log('Refreshing global guild selector...');
            window.guildSelector.loadGuilds(); // Updated method name
        }

    } catch (error) {
        console.error('Update access error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to update guild access'; // Updated text
        showToast('error', errorMessage);
    }
}

// Renamed function
async function showGuildDetails(guildId) {
    try {
        // TODO: Ensure the backend route /api/v1/owner/guilds/{guildId} is implemented and returns details
        const data = await apiRequest(`/api/v1/owner/guilds/${guildId}`); // Updated endpoint 
        
        const modal = document.getElementById('guildDetailsModal'); // Updated ID
        if (!modal) return;
        
        // Update modal content (ensure backend provides these fields)
        modal.querySelector('.guild-name').textContent = data.name || 'N/A'; // Updated class
        modal.querySelector('.guild-id').textContent = data.guild_id || 'N/A'; // Updated class
        modal.querySelector('.member-count').textContent = data.member_count || 0;
        modal.querySelector('.status').innerHTML = getStatusBadge(data.access_status || 'unknown'); // Use badge
        modal.querySelector('.join-date').textContent = formatDateTime(data.created_at); // Example: use created_at
        
        // TODO: Populate ban info, permissions, features if backend provides them
        const banInfoSection = modal.querySelector('.ban-info');
        if (data.access_status === 'banned' && data.ban_info && banInfoSection) {
            banInfoSection.style.display = 'block';
            modal.querySelector('.ban-reason').textContent = data.ban_info.reason || 'N/A';
            modal.querySelector('.banned-by').textContent = data.ban_info.banned_by_user || 'N/A'; // Assuming field name
            modal.querySelector('.banned-at').textContent = formatDateTime(data.ban_info.banned_at);
        } else if (banInfoSection) {
            banInfoSection.style.display = 'none';
        }

        // Placeholder for permissions/features
        // modal.querySelector('.permissions-list').innerHTML = generatePermissionsHtml(data.permissions);
        // modal.querySelector('.features-list').innerHTML = generateFeaturesHtml(data.features);
        
        // Show modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    } catch (error) {
        console.error('Guild details error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Could not load guild details'; // Updated text
        showToast('error', errorMessage);
    }
}

// --- Add Server Logic ---
async function addGuild(event) {
    if (event) event.preventDefault(); // Prevent default form submission if called from form
    const form = document.getElementById('addGuildForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const guildData = Object.fromEntries(formData.entries());

    // Basic client-side validation (optional)
    if (!guildData.name || !guildData.guild_id) {
        showToast('warning', 'Guild Name and Guild ID are required.');
        return;
    }

    try {
        showToast('info', `Adding guild ${guildData.name}...`);
        // TODO: Ensure backend endpoint POST /api/v1/owner/guilds exists to add a guild
        const response = await apiRequest('/api/v1/owner/guilds', { // Changed endpoint 
            method: 'POST',
            body: JSON.stringify(guildData)
        });

        // Assuming successful response means guild was added (adjust based on actual API)
        showToast('success', `Guild ${response.name || guildData.name} added successfully.`);
        form.reset(); // Clear the form

        // Close the modal
        const modalElement = document.getElementById('addGuildModal');
        if (modalElement) {
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
        
        await refreshGuildList(); // Refresh the list to show the new guild
    } catch (error) {
        console.error('Add guild error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to add guild';
        showToast('error', errorMessage);
    }
}
// Expose addGuild globally if it's called via onclick in HTML
window.addGuild = addGuild;
// --- End Add Server Logic ---


document.addEventListener('DOMContentLoaded', () => {
    // Initial guild list load (renamed function)
    refreshGuildList();
    
    // Add click handlers for guild actions
    document.addEventListener('click', async (event) => {
        const button = event.target.closest('button[data-action]');
        if (!button) return;
        
        const action = button.dataset.action;
        const guildId = button.dataset.guildId;
        
        if (!guildId && action !== 'add') { // Allow add action without guildId
             console.warn('Action button clicked without guildId:', button);
             return; 
        }
        
        switch(action) {
            case 'approve':
                await updateAccess(guildId, 'approved');
                break;
            case 'reject':
                await updateAccess(guildId, 'rejected');
                break;
            case 'ban': // Use ban instead of block
                await updateAccess(guildId, 'banned'); 
                break;
            case 'suspend': // Keep suspend action
                await updateAccess(guildId, 'suspended');
                break;
            case 'details':
                await showGuildDetails(guildId); // Renamed function
                break;
            // Add case for 'add' if needed, though handled separately now
        }
    });
    
    // Refresh button handler
    const refreshButton = document.querySelector('.card-header .btn-info'); 
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshGuildList); // Renamed function
    }
    
    // Add Guild Form submission (if not using onclick)
    // const addGuildForm = document.getElementById('addGuildForm');
    // if (addGuildForm) { 
    //     addGuildForm.addEventListener('submit', addGuild);
    // }
}); 