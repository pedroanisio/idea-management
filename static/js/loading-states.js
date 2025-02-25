const LoadingState = {
    addLoadingState: function(button, text = 'Processing...') {
        // Store original text
        button.dataset.originalText = button.innerHTML;
        
        // Disable button
        button.disabled = true;
        button.classList.add('opacity-75', 'cursor-not-allowed');
        
        // Add spinner and loading text
        button.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            ${text}
        `;
    },
    
    removeLoadingState: function(button) {
        // Restore original text
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            delete button.dataset.originalText;
        }
        
        // Re-enable button
        button.disabled = false;
        button.classList.remove('opacity-75', 'cursor-not-allowed');
    },
    
    init: function() {
        // Add loading state to all form submit buttons
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    LoadingState.addLoadingState(submitButton);
                }
            });
        });
        
        // Add loading state to action buttons with data-loading attribute
        document.querySelectorAll('[data-loading]').forEach(button => {
            button.addEventListener('click', function() {
                LoadingState.addLoadingState(button, button.dataset.loading);
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', function() {
    LoadingState.init();
});
