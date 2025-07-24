const FormValidator = {
    validateForm: function(form) {
        let isValid = true;
        const errorMessages = [];
        
        // Clear previous errors
        this.clearErrors(form);
        
        // Validate required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                this.addError(field, 'This field is required');
                errorMessages.push(`${field.name || 'Field'} is required`);
            }
        });
        
        // Validate text length
        const textFields = form.querySelectorAll('input[type="text"], textarea');
        textFields.forEach(field => {
            const minLength = field.getAttribute('minlength');
            const maxLength = field.getAttribute('maxlength');
            const value = field.value.trim();
            
            if (value) {
                if (minLength && value.length < parseInt(minLength)) {
                    isValid = false;
                    this.addError(field, `Must be at least ${minLength} characters`);
                    errorMessages.push(`${field.name || 'Field'} must be at least ${minLength} characters`);
                }
                
                if (maxLength && value.length > parseInt(maxLength)) {
                    isValid = false;
                    this.addError(field, `Must be no more than ${maxLength} characters`);
                    errorMessages.push(`${field.name || 'Field'} must be no more than ${maxLength} characters`);
                }
            }
        });
        
        // Validate email fields
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value.trim() && !this.isValidEmail(field.value)) {
                isValid = false;
                this.addError(field, 'Please enter a valid email address');
                errorMessages.push('Please enter a valid email address');
            }
        });
        
        // Validate number fields
        const numberFields = form.querySelectorAll('input[type="number"]');
        numberFields.forEach(field => {
            if (field.value.trim()) {
                const min = field.getAttribute('min');
                const max = field.getAttribute('max');
                
                if (min && parseFloat(field.value) < parseFloat(min)) {
                    isValid = false;
                    this.addError(field, `Value must be at least ${min}`);
                    errorMessages.push(`${field.name || 'Field'} must be at least ${min}`);
                }
                
                if (max && parseFloat(field.value) > parseFloat(max)) {
                    isValid = false;
                    this.addError(field, `Value must be at most ${max}`);
                    errorMessages.push(`${field.name || 'Field'} must be at most ${max}`);
                }
            }
        });
        
        // Show error summary if needed
        if (!isValid) {
            this.showErrorSummary(form, errorMessages);
        }
        
        return isValid;
    },
    
    addError: function(field, message) {
        field.classList.add('border-red-500');
        
        const errorElement = document.createElement('p');
        errorElement.className = 'text-red-500 text-xs mt-1 error-message';
        errorElement.textContent = message;
        
        const parent = field.parentElement;
        parent.appendChild(errorElement);
    },
    
    clearErrors: function(form) {
        // Remove error styling
        form.querySelectorAll('.border-red-500').forEach(field => {
            field.classList.remove('border-red-500');
        });
        
        // Remove error messages
        form.querySelectorAll('.error-message').forEach(message => {
            message.remove();
        });
        
        // Remove error summary
        const errorSummary = form.querySelector('.error-summary');
        if (errorSummary) {
            errorSummary.remove();
        }
    },
    
    showErrorSummary: function(form, messages) {
        const summary = document.createElement('div');
        summary.className = 'bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-4 error-summary';
        
        const heading = document.createElement('h3');
        heading.className = 'text-sm font-medium';
        heading.textContent = 'Please fix the following errors:';
        summary.appendChild(heading);
        
        const list = document.createElement('ul');
        list.className = 'list-disc pl-5 mt-2 text-sm';
        
        messages.forEach(message => {
            const item = document.createElement('li');
            item.textContent = message;
            list.appendChild(item);
        });
        
        summary.appendChild(list);
        form.prepend(summary);
    },
    
    isValidEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    init: function() {
        // Add validation to all forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
            
            // Add real-time validation for better UX
            form.querySelectorAll('input, select, textarea').forEach(field => {
                field.addEventListener('blur', () => {
                    if (field.hasAttribute('required') && !field.value.trim()) {
                        this.addError(field, 'This field is required');
                    } else if (field.type === 'email' && field.value.trim() && !this.isValidEmail(field.value)) {
                        this.addError(field, 'Please enter a valid email address');
                    } else {
                        // Check minlength/maxlength
                        const minLength = field.getAttribute('minlength');
                        const maxLength = field.getAttribute('maxlength');
                        const value = field.value.trim();
                        
                        if (value) {
                            if (minLength && value.length < parseInt(minLength)) {
                                this.addError(field, `Must be at least ${minLength} characters`);
                            } else if (maxLength && value.length > parseInt(maxLength)) {
                                this.addError(field, `Must be no more than ${maxLength} characters`);
                            } else {
                                field.classList.remove('border-red-500');
                                const errorMessage = field.parentElement.querySelector('.error-message');
                                if (errorMessage) errorMessage.remove();
                            }
                        } else {
                            field.classList.remove('border-red-500');
                            const errorMessage = field.parentElement.querySelector('.error-message');
                            if (errorMessage) errorMessage.remove();
                        }
                    }
                });
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', function() {
    FormValidator.init();
});
