class ThemeSwitcher {
    constructor() {
        this.STORAGE_KEY = 'preferred-theme';
        this.DARK_THEME = 'dark-theme';
        this.LIGHT_THEME = 'light-theme';
        this.DEFAULT_THEME = this.DARK_THEME;

        this.init();
    }

    init() {
        // Get saved theme or use system preference as fallback
        const savedTheme = localStorage.getItem(this.STORAGE_KEY);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const defaultTheme = prefersDark ? this.DARK_THEME : this.LIGHT_THEME;
        const theme = savedTheme || defaultTheme;

        // Apply theme immediately to prevent flash
        this.applyTheme(theme);

        // Setup theme toggle button
        const themeSwitch = document.getElementById('theme-switch');
        if (themeSwitch) {
            themeSwitch.addEventListener('click', () => this.toggleTheme());
            this.updateToggleButton(theme);
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(this.STORAGE_KEY)) {
                this.applyTheme(e.matches ? this.DARK_THEME : this.LIGHT_THEME);
            }
        });
    }

    applyTheme(theme) {
        document.body.classList.remove(this.DARK_THEME, this.LIGHT_THEME);
        document.body.classList.add(theme);
        this.updateToggleButton(theme);
        localStorage.setItem(this.STORAGE_KEY, theme);
    }

    toggleTheme() {
        const currentTheme = document.body.classList.contains(this.DARK_THEME) ? this.DARK_THEME : this.LIGHT_THEME;
        const newTheme = currentTheme === this.DARK_THEME ? this.LIGHT_THEME : this.DARK_THEME;
        this.applyTheme(newTheme);
    }

    updateToggleButton(theme) {
        const themeSwitch = document.getElementById('theme-switch');
        if (!themeSwitch) return;

        const icon = document.getElementById('theme-icon');
        if (!icon) return;

        // Update icon
        icon.className = theme === this.DARK_THEME ? 'bi bi-sun-fill' : 'bi bi-moon-fill';

        // Update tooltip
        themeSwitch.setAttribute('title', `Switch to ${theme === this.DARK_THEME ? 'light' : 'dark'} theme`);
    }
}

// Initialize theme switcher when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.themeSwitcher = new ThemeSwitcher();
}); 