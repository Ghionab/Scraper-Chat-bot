// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// Form validation functions

/**
 * Validate email format
 * @param {string} email - Email address to validate
 * @returns {boolean} - True if valid, false otherwise
 */
function validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

/**
 * Validate login form inputs
 * @param {string} email - Email address
 * @param {string} password - Password
 * @returns {object} - {isValid: boolean, message: string}
 */
function validateLoginForm(email, password) {
    // Check if all fields are filled
    if (!email || !password) {
        return {
            isValid: false,
            message: 'Email and password are required'
        };
    }
    
    // Validate email format
    if (!validateEmail(email)) {
        return {
            isValid: false,
            message: 'Please enter a valid email address'
        };
    }
    
    return {
        isValid: true,
        message: ''
    };
}

/**
 * Display error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.classList.add('show');
}

/**
 * Hide error message
 */
function hideError() {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = '';
    errorElement.classList.remove('show');
}

/**
 * Set loading state for submit button
 * @param {boolean} isLoading - Whether to show loading state
 */
function setLoading(isLoading) {
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    if (isLoading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
    } else {
        submitBtn.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
}

/**
 * Handle login form submission
 * @param {Event} event - Form submit event
 */
async function handleLogin(event) {
    event.preventDefault();
    
    // Hide any previous errors
    hideError();
    
    // Get form values
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    
    // Validate form
    const validation = validateLoginForm(email, password);
    if (!validation.isValid) {
        showError(validation.message);
        return;
    }
    
    // Set loading state
    setLoading(true);
    
    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.token) {
            // Login successful - store token and user info
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('user_info', JSON.stringify(data.user));
            
            // Redirect to main chat interface
            window.location.href = 'index.html';
        } else {
            // Show error message from server
            showError(data.error || 'Login failed. Please check your credentials.');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        setLoading(false);
    }
}

// Add event listener when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('auth_token');
    if (token) {
        // Redirect to main page if already logged in
        window.location.href = 'index.html';
        return;
    }
    
    // Focus on email input
    document.getElementById('email').focus();
});
