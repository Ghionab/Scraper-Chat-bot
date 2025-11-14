# Security Measures Documentation

This document outlines the security measures implemented in the Web Scraping Chatbot application.

## 1. Input Validation

### Email Validation
- **Location**: `backend/routes/auth.py`, `frontend/signup.js`, `frontend/login.js`
- **Implementation**: Regex pattern validation
- **Pattern**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Validates**: Proper email format with username, @ symbol, domain, and TLD

### Password Validation
- **Location**: `backend/routes/auth.py`, `frontend/signup.js`
- **Requirements**:
  - Minimum 8 characters length
  - Enforced on both frontend and backend
- **Security**: Passwords are hashed using bcrypt with 12 salt rounds before storage

### URL Validation
- **Location**: `backend/routes/chat.py`, `frontend/script.js`
- **Validates**:
  - URL must start with `http://` or `https://`
  - Only HTTP and HTTPS protocols allowed (blocks javascript:, file:, ftp:, etc.)
  - Proper URL structure with scheme and netloc
- **Purpose**: Prevents malicious URL injection and protocol-based attacks

## 2. Input Sanitization

### Frontend Sanitization
- **Location**: `frontend/script.js`
- **Function**: `sanitizeInput(text)`
- **Actions**:
  - Removes null bytes (`\x00`)
  - Trims whitespace
  - Applied to all user inputs before sending to API

### Backend Sanitization
- **Location**: `backend/routes/chat.py`
- **Function**: `sanitize_input(text)`
- **Actions**:
  - Removes null bytes
  - Trims whitespace
  - Limits length to 10,000 characters (DoS prevention)
  - Applied to prompts, URLs, and chat IDs

### Database Sanitization
- **Location**: `backend/utils/db.py`
- **Function**: `sanitize_db_input(text)`
- **Actions**:
  - Removes null bytes (prevents SQLite issues)
  - Trims whitespace
  - Applied before all database insertions

## 3. SQL Injection Prevention

### Parameterized Queries
- **Location**: All database operations in `backend/utils/db.py`
- **Implementation**: All SQL queries use parameterized statements with `?` placeholders
- **Example**:
  ```python
  cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
  ```
- **Coverage**: All CRUD operations (create_user, get_user_by_email, add_message, etc.)
- **Security**: Prevents SQL injection by separating SQL code from data

## 4. XSS (Cross-Site Scripting) Prevention

### Frontend Protection
- **Location**: `frontend/script.js`, `frontend/signup.js`, `frontend/login.js`
- **Implementation**: Uses `textContent` instead of `innerHTML` for all user-generated content
- **Protected Elements**:
  - Chat messages (user and AI responses)
  - Error messages
  - User information display
  - Chat previews
  - URLs in messages
- **Note**: `innerHTML` is only used to clear containers (set to empty string), which is safe

### Content Display
```javascript
// Safe - uses textContent
contentDiv.textContent = content;

// Only used for clearing (safe)
messagesContainer.innerHTML = '';
```

## 5. Authentication & Authorization

### JWT Token Security
- **Location**: `backend/routes/auth.py`
- **Implementation**:
  - Tokens expire after 24 hours
  - Tokens include user_id, expiration (exp), and issued-at (iat) claims
  - Signed with SECRET_KEY using HS256 algorithm
  - Verified on all protected routes using `@require_auth` decorator

### Token Validation
- **Location**: `backend/routes/auth.py` (`require_auth` decorator)
- **Checks**:
  - Token presence in Authorization header
  - Proper "Bearer <token>" format
  - Token signature validity
  - Token expiration
- **Error Handling**:
  - Returns 401 for missing, invalid, or expired tokens
  - Clear error messages for debugging

### Frontend Token Handling
- **Location**: `frontend/script.js` (APIClient class)
- **Implementation**:
  - Automatic redirect to login on 401 responses
  - Token cleared from localStorage on expiration
  - All API requests include Authorization header

## 6. Password Security

### Hashing
- **Algorithm**: bcrypt
- **Salt Rounds**: 12
- **Location**: `backend/routes/auth.py`
- **Functions**:
  - `hash_password(password)`: Hashes passwords before storage
  - `verify_password(password, hashed)`: Verifies passwords during login

### Storage
- Passwords are NEVER stored in plain text
- Only bcrypt hashes are stored in the database
- Passwords are NEVER logged or exposed in API responses

## 7. Session Management

### Token Storage
- **Frontend**: localStorage (consider httpOnly cookies for enhanced security in production)
- **Expiration**: 24 hours
- **Logout**: Token removed from localStorage on logout

### Protected Routes
All chat and user-specific endpoints require authentication:
- `/api/chat/message` - Send messages
- `/api/chat/history` - Get chat history
- `/api/chat/<chat_id>` - Get specific chat
- `/api/chat/new` - Create new chat
- `/api/auth/logout` - Logout

## 8. Error Handling

### Backend Error Handling
- **Location**: `backend/routes/chat.py` (`@handle_errors` decorator)
- **Implementation**:
  - Catches all exceptions
  - Returns generic error messages to prevent information leakage
  - Logs detailed errors server-side for debugging
  - Returns appropriate HTTP status codes

### Frontend Error Handling
- **Location**: `frontend/script.js` (APIClient class)
- **Implementation**:
  - Handles network errors
  - Handles authentication errors (401)
  - Displays user-friendly error messages
  - Automatic redirect on session expiration

## 9. Additional Security Measures

### CORS Configuration
- **Location**: `backend/app.py`
- **Implementation**: Flask-CORS enabled
- **Recommendation**: Restrict origins in production

### Environment Variables
- **Location**: `.env` file (not committed to version control)
- **Protected Data**:
  - SECRET_KEY for JWT signing
  - OPENAI_API_KEY for API access
  - Database path
- **Security**: Never exposed in frontend code or version control

### Rate Limiting
- **Status**: Not yet implemented
- **Recommendation**: Implement rate limiting on API endpoints in production
- **Suggested Limits**:
  - Authentication endpoints: 5 requests per minute
  - Chat endpoints: 20 requests per minute
  - Scraping operations: 10 requests per minute

## 10. Security Checklist

- [x] Email format validation (frontend & backend)
- [x] Password strength requirements (minimum 8 characters)
- [x] URL format validation before scraping
- [x] Input sanitization for all user inputs
- [x] SQL injection prevention with parameterized queries
- [x] XSS prevention using textContent
- [x] JWT token validation on protected routes
- [x] Error handling for expired/invalid tokens
- [x] Password hashing with bcrypt
- [x] Secure session management
- [ ] Rate limiting (recommended for production)
- [ ] HTTPS enforcement (required for production)
- [ ] CORS origin restrictions (required for production)

## Testing Security Measures

All validation functions have been tested and verified:
- Email validation: ✓ Blocks invalid formats
- Password validation: ✓ Enforces minimum length
- URL validation: ✓ Blocks non-HTTP(S) protocols
- Input sanitization: ✓ Removes null bytes and trims whitespace
- SQL injection: ✓ All queries use parameterized statements
- XSS prevention: ✓ All user content uses textContent
- Token validation: ✓ Expired/invalid tokens return 401

## Recommendations for Production

1. **Enable HTTPS**: Use SSL/TLS certificates (Let's Encrypt)
2. **Restrict CORS**: Limit allowed origins to your frontend domain
3. **Implement Rate Limiting**: Use Flask-Limiter or similar
4. **Use httpOnly Cookies**: Store JWT in httpOnly cookies instead of localStorage
5. **Add CSRF Protection**: Implement CSRF tokens for state-changing operations
6. **Enable Security Headers**: Add Content-Security-Policy, X-Frame-Options, etc.
7. **Regular Security Audits**: Review and update dependencies regularly
8. **Logging & Monitoring**: Implement comprehensive logging and monitoring
9. **Database Backups**: Regular automated backups with encryption
10. **Secrets Management**: Use proper secrets management (AWS Secrets Manager, etc.)
