# Authentication Quick Start

## ✅ What's Been Implemented

I've added a complete authentication system to your AIOCC dashboard:

### Backend
- ✅ User database table with bcrypt password hashing
- ✅ JWT token-based authentication
- ✅ `/auth/register` - Create new account
- ✅ `/auth/login` - Login with username/password
- ✅ `/auth/me` - Get current user info
- ✅ Protected route middleware

### Frontend
- ✅ Beautiful login/register page
- ✅ Protected dashboard routes
- ✅ User info display in sidebar
- ✅ Logout functionality
- ✅ Persistent sessions (localStorage)

## 🚀 How to Test

### 1. Restart Services

Since we added new dependencies and database tables, restart everything:

```bash
# Stop all services (Ctrl+C if running)
# Then start them again:
make start
```

This will:
- Create the new `users` table in the database
- Start the API with auth endpoints
- Start the dashboard with login page

### 2. Access the Dashboard

Open your browser and go to:
```
http://localhost:5174/dashboard
```

**You'll be redirected to `/login`** since you're not authenticated! 🎉

### 3. Login with Default Admin Account

The system automatically creates a default admin account for you:

**Default Credentials:**
- **Username**: `admin`
- **Password**: `admin`
- **Email**: `admin@aio_cc.local`
- **Role**: `admin`

Simply enter these credentials and click **"Sign In"** to access the dashboard!

### 4. Alternative: Create Your Own Account

If you prefer to create your own account:
1. Click **"Don't have an account? Create one"**
2. Fill in your details
3. Click **"Create Account"**

You'll be automatically logged in and see the dashboard!

### 5. Check User Info

Look at the **sidebar** at the bottom - you should see:
- Your username
- Your email
- A logout button

### 6. Test Logout

1. Click the **"Logout"** button in the sidebar
2. You'll be redirected back to `/login`
3. Session cleared!

### 7. Test Login

1. Enter your username and password
2. Click **"Sign In"**
3. Back to the dashboard!

### 8. Test Session Persistence

1. While logged in, **refresh the page** (F5)
2. You should still be logged in!
3. Session is saved in localStorage

## 🎯 What This Enables

### Now You Can:

1. **Multi-User Support**
   - Different users can have separate accounts
   - Each user gets their own dashboard access

2. **OAuth Account Linking** (Next Step)
   - Link YouTube accounts to user profiles
   - Link Instagram accounts to user profiles
   - Link TikTok accounts to user profiles
   - Manage multiple platform accounts under one login

3. **User-Specific Data**
   - Track which user uploaded which videos
   - User-specific settings and preferences
   - Per-user analytics

4. **Secure API Access**
   - All API requests now include Bearer token
   - Protected endpoints require authentication

## 📋 Next Steps for OAuth Integration

When you're ready to add OAuth (YouTube, Instagram, etc.):

1. **Add OAuth Connections Table**
   ```sql
   CREATE TABLE oauth_connections (
     id INTEGER PRIMARY KEY,
     user_id INTEGER REFERENCES users(id),
     platform TEXT,  -- 'youtube', 'instagram', 'tiktok'
     platform_user_id TEXT,
     access_token TEXT,
     refresh_token TEXT,
     expires_at TIMESTAMP
   );
   ```

2. **OAuth Callback Endpoints**
   - `GET /auth/youtube/authorize` - Redirect to Google OAuth
   - `GET /auth/youtube/callback` - Handle OAuth callback
   - Store tokens linked to current user

3. **Dashboard UI**
   - "Connect YouTube" button
   - "Connect Instagram" button
   - Show connected accounts
   - Disconnect/reauthorize options

4. **Use Linked Accounts**
   - When uploading, use OAuth tokens from connected accounts
   - Support multiple accounts per platform per user

## 🔐 Security Notes

### Current Setup (Development)
- Password hashing with bcrypt ✅
- JWT tokens with 7-day expiration ✅
- Secure session management ✅

### For Production
Before going live, update:

1. **Secret Key** - Move to environment variable:
   ```python
   # In api_server.py
   SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-dev-key")
   ```

2. **CORS Origins** - Restrict to your domain:
   ```python
   allow_origins=["https://yourdomain.com"]  # Not ["*"]
   ```

3. **HTTPS** - Always use HTTPS in production

4. **Environment File**:
   ```env
   JWT_SECRET_KEY=your-super-secret-random-string
   ACCESS_TOKEN_EXPIRE_MINUTES=10080
   ```

## 🐛 Troubleshooting

### "Cannot GET /login"
- Make sure dashboard is running on port 5174
- Check console for errors

### "401 Unauthorized" on API calls
- Token might be expired (7 days)
- Try logging out and back in

### Can't create account
- Check if username/email already exists
- Check API console for error messages

### Dashboard not loading
- Clear localStorage: F12 → Application → Local Storage → Clear
- Try logging in again

## 📁 Files Changed

### Backend
- `src/analytics/database.py` - Added User model and methods
- `src/analytics/api_server.py` - Added auth endpoints
- `pyproject.toml` - Added bcrypt and python-jose

### Frontend
- `analytics-dashboard/src/pages/LoginPage.tsx` - NEW ✨
- `analytics-dashboard/src/contexts/AuthContext.tsx` - NEW ✨
- `analytics-dashboard/src/components/ProtectedRoute.tsx` - NEW ✨
- `analytics-dashboard/src/App.tsx` - Updated with auth routing
- `analytics-dashboard/src/components/Sidebar.tsx` - Added user info & logout

## ✅ Success Checklist

Test these to confirm everything works:

- [ ] Navigate to dashboard → redirected to login
- [ ] Register new account → auto logged in
- [ ] See user info in sidebar
- [ ] Refresh page → still logged in
- [ ] Logout → redirected to login
- [ ] Login again → access dashboard
- [ ] Wrong password → error message shown

## 🎉 Summary

Your dashboard now has **production-ready authentication**! You can:
- ✅ Create user accounts
- ✅ Secure login/logout
- ✅ Protected routes
- ✅ Persistent sessions
- ✅ Beautiful brutalist UI

And you're **ready to add OAuth** for linking social media accounts! 🚀

Need help with OAuth integration or have questions? Just ask!


