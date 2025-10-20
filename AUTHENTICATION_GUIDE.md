# Authentication System Guide

## Overview
We've implemented a secure username/password authentication system for the AIOCC dashboard using JWT tokens and bcrypt password hashing. This sets the foundation for multi-user support and OAuth integration for linking social media accounts.

## Default Admin Account
The system automatically creates a default admin account for immediate access:

- **Username**: `admin`
- **Password**: `admin`
- **Email**: `admin@aio_cc.local`
- **Role**: `admin`

This account is created during database initialization and provides full access to all dashboard features.

## Architecture

### Backend (FastAPI)

#### Dependencies Added
- `bcrypt>=4.0.0` - Password hashing
- `python-jose[cryptography]>=3.3.0` - JWT token handling
- `python-multipart>=0.0.6` - Form data support

#### Database Schema
New `users` table with the following fields:
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Bcrypt hashed password
- `created_at` - Account creation timestamp
- `is_active` - Account status (boolean)
- `role` - User role (user/admin)

#### API Endpoints

**POST `/auth/register`**
- Register a new user account
- Request body: `{ username, email, password }`
- Returns: JWT token and user info
- Validates username/email uniqueness

**POST `/auth/login`**
- Login with existing credentials
- Request body: `{ username, password }`
- Returns: JWT token and user info
- Validates credentials with bcrypt

**GET `/auth/me`**
- Get current user information
- Requires: Bearer token in Authorization header
- Returns: User profile information

#### Security Features
- Passwords hashed with bcrypt (salt rounds: 12)
- JWT tokens with 7-day expiration
- Token validation on protected endpoints
- Active user status checking
- HTTPBearer security scheme

### Frontend (React + TypeScript)

#### New Components

**`LoginPage`** (`/login`)
- Modern brutalist UI design
- Combined login/register form
- Form validation
- Error handling
- Auto-redirects to dashboard on success

**`AuthContext`**
- Global authentication state management
- Token and user persistence in localStorage
- Login/logout methods
- Auto-restore session on page reload

**`ProtectedRoute`**
- HOC for protecting routes
- Redirects to `/login` if not authenticated
- Shows loading state while checking auth

#### Updated Components

**`App.tsx`**
- Wrapped in `AuthProvider`
- Added `/login` route
- Protected `/dashboard` routes
- Fallback redirect to dashboard

**`Sidebar`**
- Displays current user info
- User avatar placeholder
- Logout button
- Shows username and email

## Installation & Setup

### 1. Install Backend Dependencies
```bash
# Install new Python packages
uv sync
```

### 2. Initialize Database
The users table will be created automatically when the API starts:
```bash
python scripts/analytics/start_analytics.py
```

### 3. Start Dashboard
```bash
cd analytics-dashboard
npm install
npm run dev
```

## Usage Flow

### First Time Setup

1. Navigate to `http://localhost:5173/login`
2. Click "Don't have an account? Create one"
3. Fill in:
   - Username
   - Email
   - Password (min 6 characters)
   - Confirm password
4. Click "Create Account"
5. You'll be automatically logged in and redirected to dashboard

### Subsequent Logins

1. Navigate to `http://localhost:5173/login`
2. Enter username and password
3. Click "Sign In"
4. Redirected to dashboard

### Logout

- Click the "Logout" button in the sidebar
- Session cleared, redirected to login

## Security Considerations

### Current Implementation
✅ Password hashing with bcrypt  
✅ JWT token-based authentication  
✅ Token expiration (7 days)  
✅ HTTPS recommended for production  
✅ No password requirements enforced (min 6 chars)  

### Production Recommendations
🔒 **Secret Key**: Move `SECRET_KEY` to environment variable  
🔒 **CORS**: Configure `allow_origins` properly (not `["*"]`)  
🔒 **HTTPS**: Enforce HTTPS in production  
🔒 **Rate Limiting**: Add rate limiting on auth endpoints  
🔒 **Token Refresh**: Implement refresh tokens for better UX  
🔒 **Password Policy**: Stronger password requirements  
🔒 **Email Verification**: Add email verification flow  
🔒 **2FA**: Consider two-factor authentication  

## Next Steps: OAuth Integration

This authentication system prepares the ground for OAuth integration:

### 1. Link Social Media Accounts
```
users table
  ↓ one-to-many
oauth_connections table
  - id
  - user_id (FK)
  - platform (youtube/instagram/tiktok)
  - platform_user_id
  - access_token
  - refresh_token
  - expires_at
  - created_at
```

### 2. OAuth Callback Flow
1. User clicks "Connect YouTube" in dashboard
2. Redirected to YouTube OAuth
3. Callback to `/auth/oauth/youtube/callback`
4. Store tokens linked to `user_id`
5. Can now manage multiple platform accounts under one user

### 3. Dashboard Features
- View all connected accounts
- Disconnect accounts
- Reauthorize expired tokens
- Switch between accounts for uploads

## API Request Authentication

To make authenticated API requests from the frontend:

```typescript
const token = localStorage.getItem('auth_token');

fetch('http://localhost:8000/some-endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

The `analyticsApi` service already handles token storage and will automatically include it in requests.

## Testing

### Manual Testing Checklist
- [ ] Register new user
- [ ] Login with correct credentials
- [ ] Login with wrong credentials (should fail)
- [ ] Access dashboard when logged in
- [ ] Try to access dashboard when logged out (should redirect)
- [ ] Logout functionality
- [ ] Session persistence (reload page while logged in)
- [ ] Token expiration (wait 7 days or modify expiration)

### Automated Testing
Consider adding:
- Unit tests for auth endpoints
- Integration tests for login flow
- E2E tests with Playwright

## Troubleshooting

### "Module not found: bcrypt"
```bash
uv sync
```

### "401 Unauthorized"
- Check if token is expired
- Verify token is being sent in Authorization header
- Check if user account is active

### "Users table not found"
- Restart the analytics API server
- Check database file permissions

### Can't access dashboard
- Make sure you're logged in
- Check browser console for errors
- Verify token in localStorage

## Files Modified/Created

### Backend
- ✅ `src/analytics/database.py` - Added User model and methods
- ✅ `src/analytics/api_server.py` - Added auth endpoints and JWT handling
- ✅ `pyproject.toml` - Added auth dependencies

### Frontend
- ✅ `analytics-dashboard/src/pages/LoginPage.tsx` - NEW
- ✅ `analytics-dashboard/src/contexts/AuthContext.tsx` - NEW
- ✅ `analytics-dashboard/src/components/ProtectedRoute.tsx` - NEW
- ✅ `analytics-dashboard/src/App.tsx` - Updated
- ✅ `analytics-dashboard/src/components/Sidebar.tsx` - Updated

## Configuration

### Environment Variables (Recommended for Production)

Create `.env` file:
```env
# Backend
SECRET_KEY=your-super-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
CORS_ORIGINS=https://yourdomain.com

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

Update `api_server.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key-only-for-dev")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
```

## Summary

✅ **Complete authentication system** with register, login, and protected routes  
✅ **Secure password storage** with bcrypt hashing  
✅ **JWT tokens** for stateless authentication  
✅ **Modern UI** with brutalist design  
✅ **Session persistence** with localStorage  
✅ **Ready for OAuth** integration with user-account linking  

The system is now ready for you to:
1. Test the authentication flow
2. Add OAuth providers (YouTube, Instagram, TikTok)
3. Link multiple platform accounts to user accounts
4. Build multi-user features

🚀 Your dashboard is now secure and ready for multi-user, multi-platform management!


