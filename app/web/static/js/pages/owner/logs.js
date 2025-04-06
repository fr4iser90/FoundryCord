// Global variables
let autoScroll = true;
let logUpdateInterval;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Set up form submission
    document.getElementById('logFilterForm').addEventListener('submit', function(e) {
        e.preventDefault();
        updateLogs();
    });

    // Initialize auto-update
    startLogUpdates();

    // Set up log entry click handlers
    setupLogEntryHandlers();
});

// Start automatic log updates
function startLogUpdates() {
    // Update logs every 5 seconds
    logUpdateInterval = setInterval(updateLogs, 5000);
}

// Stop automatic log updates
function stopLogUpdates() {
    if (logUpdateInterval) {
        clearInterval(logUpdateInterval);
    }
}

// Toggle auto-scroll functionality
function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const button = document.querySelector('[onclick="toggleAutoScroll()"]');
    button.classList.toggle('active');
}

// Clear the log display
function clearLogs() {
    const logContainer = document.getElementById('logContainer');
    logContainer.innerHTML = '';
}

// Update logs based on current filters
async function updateLogs() {
    try {
        const form = document.getElementById('logFilterForm');
        const formData = new FormData(form);
        const params = new URLSearchParams(formData);

        const response = await fetch(`/api/v1/owner/logs?${params.toString()}`);
        const data = await response.json();

        if (response.ok) {
            updateLogDisplay(data.logs);
        } else {
            showToast('error', data.detail || 'Failed to fetch logs');
        }
    } catch (error) {
        console.error('Error updating logs:', error);
        showToast('error', 'Failed to update logs');
    }
}

// Update the log display with new entries
function updateLogDisplay(logs) {
    const logContainer = document.getElementById('logContainer');
    
    // Add new log entries
    logs.forEach(log => {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${log.level.toLowerCase()}`;
        logEntry.innerHTML = `
            <span class="timestamp">${log.timestamp}</span>
            <span class="level">${log.level}</span>
            <span class="component">[${log.component}]</span>
            <span class="message">${log.message}</span>
        `;
        logContainer.appendChild(logEntry);
    });

    // Auto-scroll if enabled
    if (autoScroll) {
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

// Reset all filters to default values
function resetFilters() {
    const form = document.getElementById('logFilterForm');
    form.reset();
    updateLogs();
}

// Download logs with current filters
async function downloadLogs() {
    try {
        const form = document.getElementById('logFilterForm');
        const formData = new FormData(form);
        const params = new URLSearchParams(formData);

        const response = await fetch(`/api/v1/owner/logs/download?${params.toString()}`);
        
        if (response.ok) {
            // Create and click a temporary download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `bot_logs_${new Date().toISOString()}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const data = await response.json();
            showToast('error', data.detail || 'Failed to download logs');
        }
    } catch (error) {
        console.error('Error downloading logs:', error);
        showToast('error', 'Failed to download logs');
    }
}

// Set up click handlers for log entries
function setupLogEntryHandlers() {
    document.getElementById('logContainer').addEventListener('click', function(e) {
        const logEntry = e.target.closest('.log-entry');
        if (logEntry) {
            showLogDetail(logEntry);
        }
    });
}

// Show detailed log entry in modal
function showLogDetail(logEntry) {
    const modal = new bootstrap.Modal(document.getElementById('logDetailModal'));
    const detailElement = document.getElementById('logDetail');
    
    // Format the log entry content
    const timestamp = logEntry.querySelector('.timestamp').textContent;
    const level = logEntry.querySelector('.level').textContent;
    const component = logEntry.querySelector('.component').textContent;
    const message = logEntry.querySelector('.message').textContent;
    
    const formattedDetail = `Timestamp: ${timestamp}
Level: ${level}
Component: ${component}
Message: ${message}`;
    
    detailElement.textContent = formattedDetail;
    modal.show();
}

// Helper function to show toast notifications
function showToast(type, message) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toast);
    });
} 