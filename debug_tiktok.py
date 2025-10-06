#!/usr/bin/env python3
"""Debug script for TikTok authentication issues."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set."""
    print("=== Environment Check ===")
    
    required_vars = {
        'NGROK_AUTH_TOKEN': os.getenv('NGROK_AUTH_TOKEN'),
        'TIKTOK_CLIENT_KEY': os.getenv('TIKTOK_CLIENT_KEY'),
        'TIKTOK_CLIENT_SECRET': os.getenv('TIKTOK_CLIENT_SECRET'),
    }
    
    all_set = True
    for var, value in required_vars.items():
        status = "✅ Set" if value else "❌ Not set"
        print(f"{var}: {status}")
        if not value:
            all_set = False
    
    return all_set

def test_ngrok():
    """Test ngrok functionality."""
    print("\n=== Testing Ngrok ===")
    try:
        from src.content_creation.ngrok_manager import NgrokManager
        manager = NgrokManager()
        
        if manager.start_tunnel(18473):
            print("✅ Ngrok tunnel started successfully")
            print(f"Public URL: {manager.public_url}")
            print(f"Callback URL: {manager.get_callback_url()}")
            manager.stop_tunnel()
            return True
        else:
            print("❌ Failed to start ngrok tunnel")
            return False
    except Exception as e:
        print(f"❌ Ngrok error: {e}")
        return False

def test_tiktok_auth():
    """Test TikTok authentication step by step."""
    print("\n=== Testing TikTok Authentication ===")
    
    try:
        from src.content_creation.oauth_manager import OAuthManager
        oauth_manager = OAuthManager()
        
        # Test just the URL generation first
        client_key = os.getenv("TIKTOK_CLIENT_KEY")
        client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
        
        print(f"Client Key: {client_key[:10]}..." if client_key else "Not set")
        print(f"Client Secret: {'Set' if client_secret else 'Not set'}")
        
        # Test callback server creation
        from src.content_creation.callback_server import OAuthCallbackServer
        print("\n--- Testing Callback Server ---")
        # Use reserved ngrok domain for consistent URLs
        ngrok_domain = os.getenv("NGROK_DOMAIN", "uninclinable-ontogenetic-leoma.ngrok-free.dev")
        server = OAuthCallbackServer(use_ngrok=True, ngrok_domain=ngrok_domain)
        
        if server.start_server():
            print("✅ Callback server started")
            callback_url = server.get_callback_url()
            print(f"Callback URL: {callback_url}")
            
            # Generate auth URL with correct parameters
            import secrets
            state = secrets.token_urlsafe(32)
            
            auth_url = (
                f"https://www.tiktok.com/v2/auth/authorize/"
                f"?client_key={client_key}"
                f"&response_type=code"
                f"&scope=user.info.basic,video.publish"
                f"&redirect_uri={callback_url}"
                f"&state={state}"
                f"&disable_auto_auth=1"
            )
            
            print(f"\n--- Generated Auth URL ---")
            print(f"URL: {auth_url}")
            print(f"\nYou can test this URL manually in your browser.")
            print(f"Expected redirect URI: {callback_url}")
            
            server.stop_server()
            return True
        else:
            print("❌ Failed to start callback server")
            return False
            
    except Exception as e:
        print(f"❌ Error during TikTok auth test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function."""
    print("TikTok Authentication Debug Tool")
    print("=" * 40)
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        print("\n❌ Missing required environment variables.")
        print("Please check your .env file and ensure all variables are set.")
        return False
    
    # Test ngrok
    ngrok_ok = test_ngrok()
    if not ngrok_ok:
        print("\n❌ Ngrok is not working properly.")
        return False
    
    # Test TikTok auth
    tiktok_ok = test_tiktok_auth()
    if not tiktok_ok:
        print("\n❌ TikTok authentication setup has issues.")
        return False
    
    print("\n✅ All tests passed! TikTok authentication should work.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
