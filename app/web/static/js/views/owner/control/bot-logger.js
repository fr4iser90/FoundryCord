import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

class BotLogger {
    constructor() {
        this.logContainer = document.getElementById('log-container');
        this.refreshButton = document.getElementById('refresh-logs-btn');
        this.autoRefreshSwitch = document.getElementById('auto-refresh-switch');
        this.autoRefreshInterval = null;
        this.refreshIntervalMs = 5000; // Refresh every 5 seconds
        this.isAutoRefreshing = true;
        this.isFetching = false; // Prevent concurrent fetches

        this.init();
    }

    init() {
        if (!this.logContainer || !this.refreshButton || !this.autoRefreshSwitch) {
            console.error('Log viewer elements not found. Logger cannot initialize.');
            return;
        }

        console.log('Initializing bot logger...');

        // Initial fetch
        this.fetchAndDisplayLogs();

        // Setup auto-refresh
        this.setupAutoRefresh();

        // Add event listeners
        this.refreshButton.addEventListener('click', () => this.fetchAndDisplayLogs(true)); // Pass true for manual refresh
        this.autoRefreshSwitch.addEventListener('change', () => this.toggleAutoRefresh());
    }

    async fetchAndDisplayLogs(isManual = false) {
        if (this.isFetching) {
            console.log('Log fetch already in progress. Skipping.');
            return;
        }
        this.isFetching = true;
        if(isManual) {
            showToast('info', 'Refreshing logs...');
        }

        try {
            // apiRequest likely returns the full {status, message, data} object
            const response = await apiRequest('/api/v1/owner/bot/logger/logs');
            console.log('Fetched logs response:', response); // Log the full response

            // Check if the response structure is valid and extract logs from the 'data' field
            if (response && response.status === 'success' && response.data && Array.isArray(response.data.logs)) {
                this.updateLogDisplay(response.data.logs); // Use response.data.logs
            } else {
                // Log the actual received structure for debugging
                console.warn('Received unexpected log data format:', response);
                this.updateLogDisplay(['Received invalid log data from server.']);
                if (isManual) showToast('warning', 'Received invalid log data.');
            }
        } catch (error) {
            console.error('Failed to fetch bot logs:', error);
            if (isManual) showToast('error', `Failed to fetch logs: ${error.message}`);
        } finally {
            this.isFetching = false;
        }
    }

    updateLogDisplay(logs) {
        if (!this.logContainer) return;

        // Check if scroll is near the bottom before updating
        const shouldScroll = this.logContainer.scrollHeight - this.logContainer.scrollTop <= this.logContainer.clientHeight + 50; // Add tolerance

        // Clear previous logs
        this.logContainer.innerHTML = '';

        if (logs.length === 0) {
            this.logContainer.innerHTML = '<div class="text-center text-muted p-3">No logs available.</div>';
            return;
        }

        // Add new log lines
        logs.forEach(line => {
            const logLineElement = document.createElement('div');
            logLineElement.classList.add('log-line');
            logLineElement.textContent = line;

            // Basic log level coloring (can be expanded)
            const lowerLine = line.toLowerCase();
            if (lowerLine.includes('[error]') || lowerLine.includes('[critical]')) {
                logLineElement.classList.add('error');
            } else if (lowerLine.includes('[warn]') || lowerLine.includes('[warning]')) {
                logLineElement.classList.add('warn');
            } else if (lowerLine.includes('[info]')) {
                logLineElement.classList.add('info');
            } else if (lowerLine.includes('[debug]')) {
                logLineElement.classList.add('debug');
            }

            this.logContainer.appendChild(logLineElement);
        });

        // Scroll to bottom if it was near the bottom before update
        if (shouldScroll) {
            this.logContainer.scrollTop = this.logContainer.scrollHeight;
        }
    }

    setupAutoRefresh() {
        if (this.autoRefreshSwitch.checked) {
            this.isAutoRefreshing = true;
            if (!this.autoRefreshInterval) {
                this.autoRefreshInterval = setInterval(() => {
                    if (this.isAutoRefreshing) {
                        this.fetchAndDisplayLogs();
                    }
                }, this.refreshIntervalMs);
                console.log(`Auto-refresh started (every ${this.refreshIntervalMs}ms).`);
            }
        } else {
            this.isAutoRefreshing = false;
            this.clearAutoRefreshInterval();
        }
    }

    toggleAutoRefresh() {
        this.isAutoRefreshing = this.autoRefreshSwitch.checked;
        if (this.isAutoRefreshing) {
            this.setupAutoRefresh(); // Start or ensure interval is running
            // Optionally fetch immediately when toggled on
            this.fetchAndDisplayLogs();
        } else {
            this.clearAutoRefreshInterval();
            console.log('Auto-refresh stopped.');
        }
    }

    clearAutoRefreshInterval() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }
}

// Initialize the logger when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new BotLogger();
});
