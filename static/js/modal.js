const Modal = {
    open: function(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        
        // Focus first input
        setTimeout(() => {
            const firstInput = modal.querySelector('input, select, textarea');
            if (firstInput) firstInput.focus();
        }, 100);
        
        // Close on escape key
        document.addEventListener('keydown', function escHandler(e) {
            if (e.key === 'Escape') {
                Modal.close(modalId);
                document.removeEventListener('keydown', escHandler);
            }
        });
        
        // Close on background click
        modal.addEventListener('click', function bgClickHandler(e) {
            if (e.target === modal) {
                Modal.close(modalId);
                modal.removeEventListener('click', bgClickHandler);
            }
        });
    },
    
    close: function(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    },
    
    create: function(options) {
        const { id, title, content, onSubmit } = options;
        
        // Create modal if it doesn't exist
        let modal = document.getElementById(id);
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = id;
            modal.className = 'hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
            modal.innerHTML = `
                <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-medium text-gray-900">${title}</h3>
                        <button onclick="Modal.close('${id}')" class="text-gray-400 hover:text-gray-500">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-content">
                        ${content}
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Set up form submission if provided
            if (onSubmit) {
                const form = modal.querySelector('form');
                if (form) {
                    form.addEventListener('submit', onSubmit);
                }
            }
        }
        
        return modal;
    },
    
    init: function() {
        // Initialize all modal triggers
        document.querySelectorAll('[data-modal-target]').forEach(trigger => {
            const modalId = trigger.dataset.modalTarget;
            
            trigger.addEventListener('click', function() {
                Modal.open(modalId);
            });
        });
        
        // Initialize all close buttons
        document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
            const modalId = closeBtn.dataset.modalClose;
            
            closeBtn.addEventListener('click', function() {
                Modal.close(modalId);
            });
        });
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    Modal.init();
});
