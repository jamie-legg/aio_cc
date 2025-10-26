#!/usr/bin/env python3
"""
Quick script to help get Instagram access tokens for metrics collection.
This will guide you through getting a token for your Instagram Business/Creator account.
"""

import os
import webbrowser
from urllib.parse import urlencode

def get_instagram_token():
    """Guide user through getting Instagram access token"""
    print("=" * 60)
    print("INSTAGRAM ACCESS TOKEN SETUP")
    print("=" * 60)
    print()
    print("To collect real Instagram metrics, you need an access token.")
    print("This requires a Business or Creator Instagram account.")
    print()
    
    # Get client credentials from environment
    client_id = os.getenv("INSTAGRAM_CLIENT_ID")
    redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI")
    
    if not client_id or not redirect_uri:
        print("❌ ERROR: Instagram OAuth credentials not configured")
        print("Please set INSTAGRAM_CLIENT_ID and INSTAGRAM_REDIRECT_URI in your .env file")
        return
    
    print(f"✅ Using Client ID: {client_id}")
    print(f"✅ Redirect URI: {redirect_uri}")
    print()
    
    # Build authorization URL
    auth_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'instagram_basic,instagram_manage_insights,pages_read_engagement',
        'response_type': 'code'
    }
    
    auth_url = f"https://api.instagram.com/oauth/authorize?{urlencode(auth_params)}"
    
    print("🔗 STEP 1: Authorize the app")
    print("Click the link below to authorize access to your Instagram account:")
    print()
    print(auth_url)
    print()
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("🌐 Opened authorization URL in your browser")
    except:
        print("📋 Please copy and paste the URL above into your browser")
    
    print()
    print("📝 STEP 2: Get the authorization code")
    print("After authorizing, you'll be redirected to a URL like:")
    print(f"  {redirect_uri}?code=AUTHORIZATION_CODE")
    print()
    print("Copy the 'code' parameter from the URL.")
    print()
    
    # Get authorization code from user
    auth_code = input("Enter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    print()
    print("🔄 STEP 3: Exchange code for access token")
    print("Now we'll exchange the authorization code for an access token...")
    
    # Exchange code for token
    import requests
    
    token_url = "https://api.instagram.com/oauth/access_token"
    token_data = {
        'client_id': client_id,
        'client_secret': os.getenv("INSTAGRAM_CLIENT_SECRET"),
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': auth_code
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        if access_token:
            print("✅ Successfully obtained access token!")
            print()
            print("🔧 STEP 4: Add token to environment")
            print("Add this line to your .env file:")
            print(f"INSTAGRAM_ACCESS_TOKEN={access_token}")
            print()
            print("Then restart the API server to use fresh metrics collection.")
            
            # Offer to add to .env automatically
            add_to_env = input("Add to .env file automatically? (y/n): ").strip().lower()
            if add_to_env == 'y':
                try:
                    with open('.env', 'a') as f:
                        f.write(f"\n# Instagram Access Token\nINSTAGRAM_ACCESS_TOKEN={access_token}\n")
                    print("✅ Added to .env file")
                except Exception as e:
                    print(f"❌ Failed to add to .env: {e}")
                    print("Please add it manually:")
                    print(f"INSTAGRAM_ACCESS_TOKEN={access_token}")
        else:
            print("❌ Failed to get access token")
            print("Response:", token_data)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error exchanging code for token: {e}")
        if hasattr(e, 'response') and e.response:
            print("Response:", e.response.text)

if __name__ == "__main__":
    get_instagram_token()








