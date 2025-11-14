# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create directory structure: backend/, frontend/, backend/routes/, backend/utils/, backend/models/
  - Create requirements.txt with all Python dependencies (Flask, Flask-CORS, python-dotenv, bcrypt, PyJWT, openai, crawl4ai, sqlite3)
  - Create .env.example file with required environment variables
  - Create .gitignore to exclude .env, database.db, __pycache__, etc.
  - _Requirements: 11.1, 11.2_

- [x] 2. Implement database schema and helper functions





  - Write database initialization script in utils/db.py with tables: users, chats, messages, chat_metadata
  - Implement get_db() and init_db() functions
  - Create user CRUD operations: create_user(), get_user_by_email(), get_user_by_id()
  - Create chat operations: create_chat(), get_user_chats(), get_chat_messages(), add_message(), update_chat_timestamp()
  - Create chat metadata operations: save_chat_metadata(), get_chat_metadata()
  - _Requirements: 1.1, 2.1, 6.2, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 3. Create data models





  - Implement User model in models/user.py with dataclass, to_dict(), and from_db_row() methods
  - Implement Message and Chat models in models/chat.py with dataclass, to_dict(), and get_preview() methods
  - _Requirements: 1.1, 6.3, 8.1, 8.2_

- [x] 4. Build authentication system










  - Create auth blueprint in routes/auth.py
  - Implement password hashing functions: hash_password() and verify_password() using bcrypt
  - Implement JWT token functions: generate_token() and verify_token()
  - Create require_auth decorator for protected routes
  - Implement POST /api/auth/register endpoint with email validation, duplicate check, and password hashing
  - Implement POST /api/auth/login endpoint with credential verification and token generation
  - Implement POST /api/auth/logout endpoint
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5, 11.3_

- [x] 5. Implement web scraping module





  - Create WebScraper class in utils/scraper.py
  - Implement async scrape_url() method using Crawl4AI to extract markdown content
  - Implement scrape_sync() wrapper for synchronous usage in Flask routes
  - Add error handling for invalid URLs and scraping failures
  - Return structured dict with success status, content, title, and error fields
  - _Requirements: 3.3, 3.4, 12.4_

- [x] 6. Implement OpenAI integration








  - Create OpenAIHelper class in utils/openai_helper.py
  - Initialize OpenAI client with API key from environment variable
  - Define system prompt for web scraping assistant behavior
  - Implement generate_response() method that accepts user prompt, website content, and conversation history
  - Build messages array with system prompt, conversation history, and combined website content + user prompt
  - Call OpenAI API with GPT-4 Turbo model and temperature 0.7
  - Return structured dict with success status, response text, and error fields
  - _Requirements: 3.5, 5.3, 11.1, 12.1, 12.2, 12.3, 12.5_

- [x] 7. Build chat API endpoints





  - Create chat blueprint in routes/chat.py
  - Implement POST /api/chat/message endpoint: validate auth, get/create chat session, scrape URL if provided, call OpenAI, save messages, return response
  - Implement GET /api/chat/history endpoint: validate auth, retrieve all user chats with metadata
  - Implement GET /api/chat/<chat_id> endpoint: validate auth and ownership, retrieve complete conversation
  - Implement POST /api/chat/new endpoint: validate auth, create new chat session, return chat_id
  - Add error handling decorator for all endpoints
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2_

- [x] 8. Create Flask application entry point





  - Write create_app() function in backend/app.py
  - Load environment variables with python-dotenv
  - Configure Flask app with SECRET_KEY and DATABASE path
  - Enable CORS with Flask-CORS
  - Register auth and chat blueprints with URL prefixes
  - Initialize database on app startup
  - Create run.py to start the Flask development server
  - _Requirements: 11.1, 11.2_

- [x] 9. Build authentication frontend pages





  - Create signup.html with form inputs for email, username, password, and submit button
  - Create login.html with form inputs for email, password, and submit button
  - Add CSS styling for forms: centered layout, clean inputs, professional appearance
  - Implement handleSignup() JavaScript function to POST to /api/auth/register
  - Implement handleLogin() JavaScript function to POST to /api/auth/login
  - Add form validation functions: validateSignupForm() and validateLoginForm()
  - Store JWT token in localStorage on successful login
  - Redirect to index.html after successful login
  - Display error messages for failed authentication
  - Add links to switch between login and signup pages
  - _Requirements: 1.1, 1.5, 2.1, 2.2, 2.3, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 10. Build main chat interface HTML structure





  - Create index.html with top navbar containing user info and logout button
  - Add collapsible sidebar with chat history list and "New Chat" button
  - Create main chat area with messages container
  - Add input section with URL input field, prompt textarea, and send button
  - Include loading animation element (hidden by default)
  - Link external CSS (style.css) and JavaScript (script.js) files
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 6.1, 6.5, 7.1, 9.1, 10.1, 10.2, 10.3, 10.4_

- [x] 11. Implement chat interface CSS styling





  - Define CSS variables for colors (white, #333, blue accent), spacing, and typography
  - Style navbar: fixed top, flex layout, user info on right
  - Style sidebar: fixed left, collapsible, chat list with hover effects
  - Style chat messages: user messages aligned right with blue background, AI messages aligned left with gray background
  - Add rounded corners and soft shadows to message bubbles
  - Implement responsive layout with media queries for mobile devices
  - Style input section: fixed bottom, flex layout, URL input and prompt textarea side-by-side
  - Add loading animation styles (spinner or dots)
  - Use Inter or Poppins font family
  - _Requirements: 4.1, 4.2, 4.3, 4.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 12. Implement chat JavaScript functionality





  - Create APIClient class with methods: post(), get(), setAuthToken()
  - Create ChatManager class with methods: sendMessage(), loadChatHistory(), loadChat(), createNewChat(), displayMessage(), showLoading(), hideLoading()
  - Create UIController class with methods: toggleSidebar(), scrollToBottom(), updateChatList(), showError()
  - Implement authentication check: verify token exists, redirect to login if not
  - Load user info and display in navbar
  - Load chat history on page load and populate sidebar
  - Implement send message handler: validate inputs, show loading, call API, display response, hide loading
  - Implement new chat button handler: create new chat, clear display, update sidebar
  - Implement chat history click handler: load selected chat, display messages
  - Implement logout button handler: clear token, redirect to login
  - Add auto-scroll to bottom when new messages appear
  - Implement error handling with user-friendly messages
  - _Requirements: 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.3, 6.4, 7.1, 7.2, 7.3, 7.4, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 13. Implement conversation context management





  - Modify POST /api/chat/message to retrieve previous messages from database
  - Format previous messages as conversation history for OpenAI API
  - Pass conversation history to OpenAIHelper.generate_response()
  - Store last scraped URL and content in chat_metadata table
  - Reuse cached content when user sends follow-up without new URL
  - Update chat_metadata when new URL is provided
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 14. Add input validation and security measures





  - Implement email format validation on frontend and backend
  - Implement URL format validation before scraping
  - Sanitize all user inputs before database insertion
  - Add password strength requirements (minimum 8 characters)
  - Implement SQL injection prevention with parameterized queries
  - Add XSS prevention by using textContent for message display
  - Validate JWT tokens on all protected routes
  - Add error handling for expired or invalid tokens
  - _Requirements: 1.2, 2.3, 3.2, 11.3, 11.4, 11.5_

- [ ] 15. Create documentation and setup instructions
  - Write README.md with project overview, features list, and tech stack
  - Add installation instructions: clone repo, install dependencies, set up .env file
  - Document environment variables required in .env
  - Add usage instructions: run backend server, open frontend in browser
  - Document API endpoints with request/response examples
  - Add troubleshooting section for common issues
  - _Requirements: 11.1, 11.2_

- [ ]* 16. Test core functionality
  - Test user registration with valid and invalid inputs
  - Test user login with correct and incorrect credentials
  - Test protected route access with and without authentication
  - Test web scraping with various URLs (valid, invalid, unreachable)
  - Test OpenAI integration with different prompts and content
  - Test chat message flow: send message, receive response, save to database
  - Test conversation context: follow-up questions without new URL
  - Test chat history: create multiple chats, load previous chats
  - Test new chat creation and session management
  - Test logout functionality and session clearing
  - _Requirements: All requirements_
