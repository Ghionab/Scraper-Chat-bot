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
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} - {isValid: boolean, message: string}
 */
function validatePassword(password) {
    if (password.length < 8) {
        return {
            isValid: false,
            message: 'Password must be at least 8 characters long'
        };
    }
    
    return {
        isValid: true,
        message: ''
    };
}

/**
 * Validate signup form inputs
 * @param {string} email - Email address
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {object} - {isValid: boolean, message: string}
 */
function validateSignupForm(email, username, password) {
    // Check if all fields are filled
    if (!email || !username || !password) {
        return {
            isValid: false,
            message: 'All fields are required'
        };
    }
    
    // Validate email format
    if (!validateEmail(email)) {
        return {
            isValid: false,
            message: 'Please enter a valid email address'
        };
    }
    
    // Validate username length
    if (username.trim().length < 2) {
        return {
            isValid: false,
            message: 'Username must be at least 2 characters long'
        };
    }
    
    // Validate password
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
        return {
            isValid: false,
            message: passwordValidation.message
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
 * Handle signup form submission
 * @param {Event} event - Form submit event
 */
async function handleSignup(event) {
    event.preventDefault();
    
    // Hide any previous errors
    hideError();
    
    // Get form values
    const email = document.getElementById('email').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    // Validate form
    const validation = validateSignupForm(email, username, password);
    if (!validation.isValid) {
        showError(validation.message);
        return;
    }
    
    // Set loading state
    setLoading(true);
    
    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Registration successful - redirect to login page
            alert('Account created successfully! Please log in.');
            window.location.href = 'login.html';
        } else {
            // Show error message from server
            showError(data.error || 'Registration failed. Please try again.');
        }
        
    } catch (error) {
        console.error('Signup error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        setLoading(false);
    }
}

// Add event listener when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Clear any existing auth token
    localStorage.removeItem('auth_token');
    
    // Focus on email input
    document.getElementById('email').focus();
});
