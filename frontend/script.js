// API Client Class
class APIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.authToken = null;
    }

    setAuthToken(token) {
        this.authToken = token;
    }

    async post(endpoint, data) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            // Handle authentication errors
            if (response.status === 401) {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_info');
                window.location.href = 'login.html';
                throw new Error('Session expired. Please log in again.');
            }

            const error = await response.json();
            throw new Error(error.error || 'Request failed');
        }

        return await response.json();
    }

    async get(endpoint) {
        const headers = {};

        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            // Handle authentication errors
            if (response.status === 401) {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_info');
                window.location.href = 'login.html';
                throw new Error('Session expired. Please log in again.');
            }

            const error = await response.json();
            throw new Error(error.error || 'Request failed');
        }

        return await response.json();
    }
}

// Chat Manager Class
class ChatManager {
    constructor(apiClient, uiController) {
        this.apiClient = apiClient;
        this.uiController = uiController;
        this.currentChatId = null;
    }

    async sendMessage(url, prompt) {
        // Sanitize inputs
        prompt = sanitizeInput(prompt);
        url = sanitizeInput(url);

        if (!prompt) {
            this.uiController.showError('Please enter a prompt');
            return;
        }

        // Validate URL if provided
        if (url) {
            const urlValidation = validateURL(url);
            if (!urlValidation.isValid) {
                this.uiController.showError(urlValidation.message);
                return;
            }
        }

        try {
            this.showLoading();

            // Display user message immediately
            this.displayMessage(prompt, true, url);

            // Send to API
            const response = await this.apiClient.post('/api/chat/message', {
                chat_id: this.currentChatId,
                url: url || null,
                prompt: prompt
            });

            if (response.success) {
                // Update current chat ID
                this.currentChatId = response.chat_id;

                // Display AI response
                this.displayMessage(response.response, false);

                // Reload chat history to update sidebar
                await this.loadChatHistory();
            } else {
                this.uiController.showError(response.error || 'Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.uiController.showError(error.message || 'Failed to send message');
        } finally {
            this.hideLoading();
        }
    }

    async loadChatHistory() {
        try {
            const response = await this.apiClient.get('/api/chat/history');
            
            if (response.chats) {
                this.uiController.updateChatList(response.chats);
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            // Don't show error to user for background operation
        }
    }

    async loadChat(chatId) {
        try {
            this.showLoading();

            const response = await this.apiClient.get(`/api/chat/${chatId}`);

            if (response.messages) {
                // Clear current messages
                const messagesContainer = document.getElementById('messagesContainer');
                messagesContainer.innerHTML = '';

                // Set current chat ID
                this.currentChatId = chatId;

                // Display all messages
                response.messages.forEach(message => {
                    this.displayMessage(message.content, message.role === 'user');
                });

                this.uiController.scrollToBottom();
            }
        } catch (error) {
            console.error('Error loading chat:', error);
            this.uiController.showError('Failed to load chat');
        } finally {
            this.hideLoading();
        }
    }

    async createNewChat() {
        try {
            // Clear current display
            const messagesContainer = document.getElementById('messagesContainer');
            messagesContainer.innerHTML = '';

            // Reset current chat ID
            this.currentChatId = null;

            // Clear inputs
            document.getElementById('urlInput').value = '';
            document.getElementById('promptTextarea').value = '';

            // Reload chat history
            await this.loadChatHistory();
        } catch (error) {
            console.error('Error creating new chat:', error);
            this.uiController.showError('Failed to create new chat');
        }
    }

    displayMessage(content, isUser, url = null) {
        const messagesContainer = document.getElementById('messagesContainer');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;

        // If user message and URL provided, show URL
        if (isUser && url) {
            const urlSpan = document.createElement('div');
            urlSpan.className = 'message-url';
            urlSpan.textContent = `URL: ${url}`;
            messageDiv.appendChild(urlSpan);
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        messageDiv.appendChild(contentDiv);

        messagesContainer.appendChild(messageDiv);
        this.uiController.scrollToBottom();
    }

    showLoading() {
        const loadingAnimation = document.getElementById('loadingAnimation');
        loadingAnimation.style.display = 'flex';
    }

    hideLoading() {
        const loadingAnimation = document.getElementById('loadingAnimation');
        loadingAnimation.style.display = 'none';
    }
}

// Validation functions

/**
 * Validate URL format
 * @param {string} url - URL to validate
 * @returns {object} - {isValid: boolean, message: string}
 */
function validateURL(url) {
    if (!url) {
        return { isValid: true, message: '' }; // URL is optional
    }

    // Check if URL starts with http:// or https://
    if (!url.match(/^https?:\/\/.+/)) {
        return {
            isValid: false,
            message: 'URL must start with http:// or https://'
        };
    }

    try {
        const urlObj = new URL(url);
        
        // Only allow http and https protocols
        if (urlObj.protocol !== 'http:' && urlObj.protocol !== 'https:') {
            return {
                isValid: false,
                message: 'Only HTTP and HTTPS URLs are allowed'
            };
        }

        return { isValid: true, message: '' };
    } catch (error) {
        return {
            isValid: false,
            message: 'Invalid URL format'
        };
    }
}

/**
 * Sanitize user input to prevent XSS
 * @param {string} text - Text to sanitize
 * @returns {string} - Sanitized text
 */
function sanitizeInput(text) {
    if (!text) return '';
    
    // Remove null bytes and trim
    return text.replace(/\x00/g, '').trim();
}

// UI Controller Class
class UIController {
    constructor() {
        this.sidebarOpen = true;
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        this.sidebarOpen = !this.sidebarOpen;
        
        if (this.sidebarOpen) {
            sidebar.classList.remove('collapsed');
        } else {
            sidebar.classList.add('collapsed');
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    updateChatList(chats) {
        const chatHistory = document.getElementById('chatHistory');
        chatHistory.innerHTML = '';

        if (!chats || chats.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-history';
            emptyMessage.textContent = 'No chat history yet';
            chatHistory.appendChild(emptyMessage);
            return;
        }

        chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            chatItem.dataset.chatId = chat.chat_id;

            const preview = document.createElement('div');
            preview.className = 'chat-preview';
            preview.textContent = chat.preview || 'New Chat';

            const timestamp = document.createElement('div');
            timestamp.className = 'chat-timestamp';
            timestamp.textContent = this.formatTimestamp(chat.timestamp);

            chatItem.appendChild(preview);
            chatItem.appendChild(timestamp);

            chatHistory.appendChild(chatItem);
        });
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    }

    showError(message) {
        // Create error toast
        const errorToast = document.createElement('div');
        errorToast.className = 'error-toast';
        errorToast.textContent = message;

        document.body.appendChild(errorToast);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            errorToast.remove();
        }, 3000);
    }
}

// Initialize application
let apiClient;
let chatManager;
let uiController;

function initializeApp() {
    // Check authentication
    const token = localStorage.getItem('auth_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Initialize classes
    apiClient = new APIClient();
    apiClient.setAuthToken(token);
    
    uiController = new UIController();
    chatManager = new ChatManager(apiClient, uiController);

    // Load user info
    loadUserInfo();

    // Load chat history
    chatManager.loadChatHistory();

    // Set up event listeners
    setupEventListeners();
}

async function loadUserInfo() {
    try {
        const userInfo = localStorage.getItem('user_info');
        if (userInfo) {
            const user = JSON.parse(userInfo);
            document.getElementById('userInfo').textContent = user.username || user.email;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

function setupEventListeners() {
    // Send button
    document.getElementById('sendBtn').addEventListener('click', handleSendMessage);

    // Enter key in textarea
    document.getElementById('promptTextarea').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // New chat button
    document.getElementById('newChatBtn').addEventListener('click', () => {
        chatManager.createNewChat();
    });

    // Toggle sidebar button
    document.getElementById('toggleSidebarBtn').addEventListener('click', () => {
        uiController.toggleSidebar();
    });

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Chat history click handler (event delegation)
    document.getElementById('chatHistory').addEventListener('click', (e) => {
        const chatItem = e.target.closest('.chat-item');
        if (chatItem) {
            const chatId = chatItem.dataset.chatId;
            chatManager.loadChat(chatId);
        }
    });
}

async function handleSendMessage() {
    const url = document.getElementById('urlInput').value.trim();
    const prompt = document.getElementById('promptTextarea').value.trim();

    if (!prompt) {
        uiController.showError('Please enter a prompt');
        return;
    }

    // Send message
    await chatManager.sendMessage(url, prompt);

    // Clear inputs
    document.getElementById('promptTextarea').value = '';
    // Keep URL for follow-up questions unless user clears it
}

function handleLogout() {
    // Clear token and user info
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');

    // Redirect to login
    window.location.href = 'login.html';
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
