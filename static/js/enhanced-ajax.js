// Enhanced AJAX functionality for module registration system

// Global configuration
const AJAX_CONFIG = {
    timeout: 10000,
    retryAttempts: 3,
    baseURL: window.location.origin
};

// Utility functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.content;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg max-w-sm`;
    notification.style.cssText = `
        background-color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        font-weight: 500;
        transform: translateX(400px);
        transition: transform 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function showLoader(element) {
    const loader = document.createElement('div');
    loader.className = 'ajax-loader';
    loader.innerHTML = `
        <div class="inline-flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading...
        </div>
    `;
    
    element.disabled = true;
    element.dataset.originalText = element.textContent;
    element.innerHTML = loader.innerHTML;
    
    return loader;
}

function hideLoader(element) {
    element.disabled = false;
    element.textContent = element.dataset.originalText || 'Submit';
    delete element.dataset.originalText;
}

// AJAX wrapper with retry logic
async function makeAjaxRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        timeout: AJAX_CONFIG.timeout
    };
    
    const requestOptions = { ...defaultOptions, ...options };
    
    for (let attempt = 0; attempt < AJAX_CONFIG.retryAttempts; attempt++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), requestOptions.timeout);
            
            const response = await fetch(url, {
                ...requestOptions,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
            
        } catch (error) {
            if (attempt === AJAX_CONFIG.retryAttempts - 1) {
                throw error;
            }
            // Wait before retry
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
        }
    }
}

// Module registration functionality
class ModuleRegistration {
    constructor() {
        this.bindEvents();
    }
    
    bindEvents() {
        // Register for module
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="register-module"]')) {
                e.preventDefault();
                this.registerForModule(e.target);
            }
        });
        
        // Unregister from module
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="unregister-module"]')) {
                e.preventDefault();
                this.unregisterFromModule(e.target);
            }
        });
        
        // Quick register from module list
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="quick-register"]')) {
                e.preventDefault();
                this.quickRegister(e.target);
            }
        });
    }
    
    async registerForModule(button) {
        const moduleId = button.dataset.moduleId;
        if (!moduleId) return;
        
        const loader = showLoader(button);
        
        try {
            const response = await makeAjaxRequest('/api/registrations/', {
                method: 'POST',
                body: JSON.stringify({
                    module: parseInt(moduleId)
                })
            });
            
            showNotification('Successfully registered for module!', 'success');
            this.updateRegistrationUI(button, 'registered');
            
            // Update any counters
            this.updateRegistrationCount(moduleId, 1);
            
        } catch (error) {
            console.error('Registration error:', error);
            showNotification('Failed to register for module. Please try again.', 'error');
        } finally {
            hideLoader(button);
        }
    }
    
    async unregisterFromModule(button) {
        const registrationId = button.dataset.registrationId;
        const moduleId = button.dataset.moduleId;
        
        if (!registrationId) return;
        
        // Confirm action
        if (!confirm('Are you sure you want to unregister from this module?')) {
            return;
        }
        
        const loader = showLoader(button);
        
        try {
            await makeAjaxRequest(`/api/registrations/${registrationId}/`, {
                method: 'DELETE'
            });
            
            showNotification('Successfully unregistered from module!', 'success');
            this.updateRegistrationUI(button, 'unregistered');
            
            // Update any counters
            this.updateRegistrationCount(moduleId, -1);
            
        } catch (error) {
            console.error('Unregistration error:', error);
            showNotification('Failed to unregister from module. Please try again.', 'error');
        } finally {
            hideLoader(button);
        }
    }
    
    async quickRegister(button) {
        const moduleId = button.dataset.moduleId;
        const moduleTitle = button.dataset.moduleTitle;
        
        if (!confirm(`Register for ${moduleTitle}?`)) return;
        
        await this.registerForModule(button);
    }
    
    updateRegistrationUI(button, action) {
        const container = button.closest('.module-card, .registration-card, .module-detail');
        
        if (action === 'registered') {
            // Update button to unregister
            button.textContent = 'Unregister';
            button.className = button.className.replace('bg-indigo-600', 'bg-red-600');
            button.dataset.action = 'unregister-module';
            
            // Add registered badge
            const badge = document.createElement('span');
            badge.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
            badge.textContent = 'Registered';
            container?.querySelector('.status-badges')?.appendChild(badge);
            
        } else if (action === 'unregistered') {
            // Update button to register
            button.textContent = 'Register';
            button.className = button.className.replace('bg-red-600', 'bg-indigo-600');
            button.dataset.action = 'register-module';
            
            // Remove registered badge
            container?.querySelector('.status-badges .bg-green-100')?.remove();
        }
    }
    
    updateRegistrationCount(moduleId, change) {
        const countElements = document.querySelectorAll(`[data-registration-count="${moduleId}"]`);
        countElements.forEach(element => {
            const currentCount = parseInt(element.textContent) || 0;
            const newCount = Math.max(0, currentCount + change);
            element.textContent = newCount;
        });
    }
}

// Live search functionality
class LiveSearch {
    constructor(searchInput, resultsContainer, apiEndpoint) {
        this.searchInput = searchInput;
        this.resultsContainer = resultsContainer;
        this.apiEndpoint = apiEndpoint;
        this.debounceTimer = null;
        this.bindEvents();
    }
    
    bindEvents() {
        this.searchInput.addEventListener('input', (e) => {
            this.debounceSearch(e.target.value);
        });
        
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch(e.target.value);
            }
        });
    }
    
    debounceSearch(query) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }
    
    async performSearch(query) {
        if (query.length < 2) {
            this.clearResults();
            return;
        }
        
        this.showSearchLoader();
        
        try {
            const results = await makeAjaxRequest(`${this.apiEndpoint}?search=${encodeURIComponent(query)}`);
            this.displayResults(results);
        } catch (error) {
            console.error('Search error:', error);
            this.showSearchError();
        }
    }
    
    showSearchLoader() {
        this.resultsContainer.innerHTML = `
            <div class="flex items-center justify-center py-8">
                <svg class="animate-spin h-8 w-8 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="ml-2 text-gray-500">Searching...</span>
            </div>
        `;
    }
    
    displayResults(results) {
        if (results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-gray-400 mb-2">
                        <svg class="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </div>
                    <p class="text-gray-500">No results found</p>
                </div>
            `;
            return;
        }
        
        // This would be customized based on the specific search results format
        this.resultsContainer.innerHTML = results.map(item => this.formatSearchResult(item)).join('');
    }
    
    formatSearchResult(item) {
        // Override this method for specific result formatting
        return `<div class="search-result-item p-4 border-b">${item.name || item.title}</div>`;
    }
    
    clearResults() {
        this.resultsContainer.innerHTML = '';
    }
    
    showSearchError() {
        this.resultsContainer.innerHTML = `
            <div class="text-center py-8">
                <div class="text-red-400 mb-2">
                    <svg class="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                </div>
                <p class="text-red-500">Error loading search results</p>
            </div>
        `;
    }
}

// Enhanced contact form
class ContactForm {
    constructor(formElement) {
        this.form = formElement;
        this.bindEvents();
    }
    
    bindEvents() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });
    }
    
    async submitForm() {
        const formData = new FormData(this.form);
        const submitButton = this.form.querySelector('[type="submit"]');
        
        // Validate form
        if (!this.validateForm(formData)) {
            return;
        }
        
        const loader = showLoader(submitButton);
        
        try {
            const response = await makeAjaxRequest('/api/contact/', {
                method: 'POST',
                body: JSON.stringify(Object.fromEntries(formData))
            });
            
            showNotification('Message sent successfully!', 'success');
            this.form.reset();
            
        } catch (error) {
            console.error('Contact form error:', error);
            showNotification('Failed to send message. Please try again.', 'error');
        } finally {
            hideLoader(submitButton);
        }
    }
    
    validateForm(formData) {
        const requiredFields = ['name', 'email', 'subject', 'message'];
        let isValid = true;
        
        requiredFields.forEach(field => {
            const value = formData.get(field);
            const input = this.form.querySelector(`[name="${field}"]`);
            
            if (!value || value.trim() === '') {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });
        
        // Validate email format
        const email = formData.get('email');
        if (email && !this.isValidEmail(email)) {
            const emailInput = this.form.querySelector('[name="email"]');
            this.showFieldError(emailInput, 'Please enter a valid email address');
            isValid = false;
        }
        
        return isValid;
    }
    
    showFieldError(input, message) {
        this.clearFieldError(input);
        
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error text-red-500 text-sm mt-1';
        errorElement.textContent = message;
        
        input.classList.add('border-red-500');
        input.parentNode.appendChild(errorElement);
    }
    
    clearFieldError(input) {
        input.classList.remove('border-red-500');
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize module registration
    new ModuleRegistration();
    
    // Initialize live search if search input exists
    const searchInput = document.querySelector('#moduleSearch, #searchInput');
    const searchResults = document.querySelector('#searchResults, #moduleResults');
    if (searchInput && searchResults) {
        new LiveSearch(searchInput, searchResults, '/api/modules/');
    }
    
    // Initialize contact form
    const contactForm = document.querySelector('#contactForm');
    if (contactForm) {
        new ContactForm(contactForm);
    }
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Export for use in other scripts
window.UniversitySystem = {
    ModuleRegistration,
    LiveSearch,
    ContactForm,
    makeAjaxRequest,
    showNotification,
    showLoader,
    hideLoader
};
