# Platform Setup Guide

This guide walks you through setting up developer accounts and apps for each social media platform.

## 🎯 **Quick Setup URLs**

Once you set up GitHub Pages, you can use these URLs for all platforms:
- **Website**: `https://yourusername.github.io/content-creation`
- **Terms of Service**: `https://yourusername.github.io/content-creation/terms.html`
- **Privacy Policy**: `https://yourusername.github.io/content-creation/privacy.html`

## 📱 **TikTok for Developers**

### 1. Create Account
- Go to [TikTok for Developers](https://developers.tiktok.com/)
- Sign up with your TikTok account

### 2. Create App
- Click "Create App"
- **App Name**: `Personal Content Manager`
- **Description**: `Personal tool for managing and uploading video content`
- **Category**: `Content Management`
- **Website**: `https://yourusername.github.io/content-creation`
- **Terms of Service**: `https://yourusername.github.io/content-creation/terms.html`
- **Privacy Policy**: `https://yourusername.github.io/content-creation/privacy.html`

### 3. Get Credentials
- Go to your app dashboard
- Copy `Client Key` and `Client Secret`
- Add to your `.env` file:
  ```
  TIKTOK_CLIENT_KEY=your_client_key_here
  TIKTOK_CLIENT_SECRET=your_client_secret_here
  TIKTOK_REDIRECT_URI=https://localhost:8080/callback
  ```

## 📸 **Instagram/Facebook Developers**

### 1. Create Account
- Go to [Facebook Developers](https://developers.facebook.com/)
- Sign up with your Facebook account

### 2. Create App
- Click "Create App"
- **App Type**: `Consumer`
- **App Name**: `Content Uploader`
- **App Contact Email**: Your email
- **App Purpose**: `Personal use`

### 3. Add Instagram Basic Display
- In your app dashboard, go to "Add Products"
- Add "Instagram Basic Display"
- Go to Instagram Basic Display > Basic Display
- Click "Create New App"

### 4. Configure OAuth
- **Valid OAuth Redirect URIs**: `https://localhost:8080/callback`
- **Deauthorize Callback URL**: `https://localhost:8080/callback`
- **Data Deletion Request URL**: `https://yourusername.github.io/content-creation/privacy.html`

### 5. Get Credentials
- Copy `App ID` and `App Secret`
- Add to your `.env` file:
  ```
  INSTAGRAM_CLIENT_ID=your_app_id_here
  INSTAGRAM_CLIENT_SECRET=your_app_secret_here
  INSTAGRAM_REDIRECT_URI=https://localhost:8080/callback
  ```

## 🎥 **YouTube/Google Cloud Console**

### 1. Create Project
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project: `content-creation-tool`

### 2. Enable APIs
- Go to "APIs & Services" > "Library"
- Search for "YouTube Data API v3"
- Click "Enable"

### 3. Create Credentials
- Go to "APIs & Services" > "Credentials"
- Click "Create Credentials" > "OAuth client ID"
- **Application type**: `Desktop application`
- **Name**: `Content Creation Tool`

### 4. Download Credentials
- Download the JSON file
- Save it as `client_secrets.json` in your project root
- Add to your `.env` file:
  ```
  YOUTUBE_CLIENT_SECRETS_FILE=./client_secrets.json
  ```

## 🚀 **Setting Up GitHub Pages (Optional but Recommended)**

### 1. Create GitHub Repository
- Create a new repository: `content-creation`
- Upload the HTML files (index.html, terms.html, privacy.html)

### 2. Enable GitHub Pages
- Go to repository Settings > Pages
- Source: Deploy from a branch
- Branch: main
- Your site will be available at: `https://yourusername.github.io/content-creation`

## 🔧 **Final Setup**

1. Copy the environment template:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` with your credentials from above

3. Test authentication:
   ```bash
   uv run content-cli auth all
   ```

4. Check status:
   ```bash
   uv run content-cli check all
   ```

## ⚠️ **Important Notes**

- **TikTok**: May require approval process - can take a few days
- **Instagram**: Basic Display API has limitations for video uploads
- **YouTube**: Requires a YouTube channel to upload videos
- **All platforms**: Keep your credentials secure and never commit them to version control

## 🆘 **Troubleshooting**

### Common Issues:
1. **Redirect URI mismatch**: Make sure the redirect URI in your app matches exactly
2. **API not enabled**: Ensure you've enabled the required APIs
3. **Invalid credentials**: Double-check your client ID/secret
4. **Scope issues**: Make sure you've requested the right permissions

### Getting Help:
- Check the platform-specific documentation
- Look at the error messages in the CLI output
- Ensure all environment variables are set correctly
