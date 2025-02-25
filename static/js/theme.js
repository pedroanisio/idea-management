// Theme management for the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme from user preference or system setting
    function initializeTheme() {
        // Check for saved user preference, if any
        const savedTheme = localStorage.getItem('theme');
        
        if (savedTheme) {
            document.documentElement.classList.toggle('dark', savedTheme === 'dark');
        } else {
            // If no saved preference, check system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.classList.toggle('dark', prefersDark);
            localStorage.setItem('theme', prefersDark ? 'dark' : 'light');
        }
    }

    // Toggle theme function
    function toggleTheme() {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }

    // Initialize theme on page load
    initializeTheme();

    // Optional: Add theme toggle button functionality
    const themeToggleButton = document.getElementById('theme-toggle');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            document.documentElement.classList.toggle('dark', e.matches);
        }
    });
});
