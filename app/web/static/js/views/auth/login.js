// import { showToast, apiRequest, formatDuration } from '/static/js/components/common/notifications.js';

// Login Functions
async function handleLogin() {
    try {
        window.location.href = '/auth/discord-login';
    } catch (error) {
        console.error('Failed to start login:', error);
    }
}
