"""OAuth authentication manager for social media platforms."""

import os
import json
import webbrowser
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from .callback_server import handle_oauth_flow

load_dotenv()

@dataclass
class OAuthCredentials:
    """Container for OAuth credentials."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None
    scope: Optional[str] = None
    user_id: Optional[str] = None
    platform: str = ""

class OAuthManager:
    """Manages OAuth authentication for multiple social media platforms."""
    
    def __init__(self, credentials_dir: Path = Path.home() / ".content_creation"):
        self.credentials_dir = credentials_dir
        self.credentials_dir.mkdir(exist_ok=True)
        self.credentials_file = self.credentials_dir / "credentials.json"
        
        # Load existing credentials
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, OAuthCredentials]:
        """Load stored credentials from file."""
        if not self.credentials_file.exists():
            return {}
        
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
                return {
                    platform: OAuthCredentials(**creds)
                    for platform, creds in data.items()
                }
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return {}
    
    def _save_credentials(self):
        """Save credentials to file."""
        data = {
            platform: {
                "access_token": creds.access_token,
                "refresh_token": creds.refresh_token,
                "expires_at": creds.expires_at,
                "platform": creds.platform
            }
            for platform, creds in self.credentials.items()
        }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def authenticate_instagram(self) -> bool:
        """Authenticate with Instagram Basic Display API."""
        client_id = os.getenv("INSTAGRAM_CLIENT_ID")
        client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET")
        # Will be set dynamically by callback server
        redirect_uri = None
        
        if not client_id or not client_secret:
            print("Instagram credentials not found. Please set INSTAGRAM_CLIENT_ID and INSTAGRAM_CLIENT_SECRET")
            return False
        
        print("Starting Instagram authentication...")
        
        # Start callback server first to get the redirect URI
        from .callback_server import OAuthCallbackServer
        # Use reserved ngrok domain for consistent URLs
        ngrok_domain = os.getenv("NGROK_DOMAIN", "uninclinable-ontogenetic-leoma.ngrok-free.dev")
        temp_server = OAuthCallbackServer(use_ngrok=True, ngrok_domain=ngrok_domain)
        if not temp_server.start_server():
            print("Failed to start callback server")
            return False
        
        redirect_uri = temp_server.get_callback_url()
        print(f"Using redirect URI: {redirect_uri}")
        
        # Step 1: Get authorization code using callback server
        auth_url = (
            f"https://api.instagram.com/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=user_profile,user_media"
            f"&response_type=code"
        )
        
        callback_result = handle_oauth_flow(auth_url, use_ngrok=True, server=temp_server)
        
        # Clean up temp server
        temp_server.stop_server()
        
        if callback_result.get('error'):
            print(f"Instagram authentication failed: {callback_result.get('error_description', callback_result['error'])}")
            return False
        
        auth_code = callback_result.get('code')
        if not auth_code:
            print("No authorization code received")
            return False
        
        # Step 2: Exchange code for access token
        token_url = "https://api.instagram.com/oauth/access_token"
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": auth_code
        }
        
        try:
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            token_info = response.json()
            
            self.credentials["instagram"] = OAuthCredentials(
                access_token=token_info["access_token"],
                platform="instagram"
            )
            
            self._save_credentials()
            print("Instagram authentication successful!")
            return True
            
        except Exception as e:
            print(f"Instagram authentication failed: {e}")
            return False
    
    def authenticate_youtube(self) -> bool:
        """Authenticate with YouTube Data API v3."""
        client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE")
        
        if not client_secrets_file:
            print("YouTube client secrets file not found. Please set YOUTUBE_CLIENT_SECRETS_FILE")
            return False
        
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, SCOPES)
        
        # Check if we have valid credentials
        creds = None
        token_file = self.credentials_dir / "youtube_token.json"
        
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Store credentials in our format
        self.credentials["youtube"] = OAuthCredentials(
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            expires_at=creds.expiry.timestamp() if creds.expiry else None,
            platform="youtube"
        )
        
        self._save_credentials()
        print("YouTube authentication successful!")
        return True
    
    def authenticate_tiktok(self) -> bool:
        """Authenticate with TikTok for Developers API."""
        client_key = os.getenv("TIKTOK_CLIENT_KEY")
        client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
        # Will be set dynamically by callback server
        redirect_uri = None
        
        if not client_key or not client_secret:
            print("TikTok credentials not found. Please set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET")
            return False
        
        print("Starting TikTok authentication...")
        
        # Start callback server first to get the redirect URI
        from .callback_server import OAuthCallbackServer
        # Use reserved ngrok domain for consistent URLs
        ngrok_domain = os.getenv("NGROK_DOMAIN", "uninclinable-ontogenetic-leoma.ngrok-free.dev")
        temp_server = OAuthCallbackServer(use_ngrok=True, ngrok_domain=ngrok_domain)
        if not temp_server.start_server():
            print("Failed to start callback server")
            return False
        
        redirect_uri = temp_server.get_callback_url()
        print(f"Using redirect URI: {redirect_uri}")
        
        # Step 1: Get authorization code using callback server
        import secrets
        state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"https://www.tiktok.com/v2/auth/authorize/"
            f"?client_key={client_key}"
            f"&response_type=code"
            f"&scope=user.info.basic,video.publish,video.upload"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
            f"&disable_auto_auth=1"
        )
        
        callback_result = handle_oauth_flow(auth_url, use_ngrok=True, server=temp_server)
        
        # Clean up temp server
        temp_server.stop_server()
        
        if callback_result.get('error'):
            print(f"TikTok authentication failed: {callback_result.get('error_description', callback_result['error'])}")
            return False
        
        auth_code = callback_result.get('code')
        if not auth_code:
            print("No authorization code received")
            print(f"Callback result: {callback_result}")
            return False
        
        
        # Step 2: Exchange code for access token
        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
        token_data = {
            "client_key": client_key,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        
        try:
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            token_info = response.json()
            
            if token_info.get("error"):
                print(f"TikTok authentication failed: {token_info['error']['message']}")
                return False
            
            self.credentials["tiktok"] = OAuthCredentials(
                access_token=token_info["access_token"],
                refresh_token=token_info.get("refresh_token"),
                expires_at=token_info.get("expires_in"),
                scope=token_info.get("scope"),
                user_id=token_info.get("open_id"),
                platform="tiktok"
            )
            
            self._save_credentials()
            print("TikTok authentication successful!")
            return True
            
        except Exception as e:
            print(f"TikTok authentication failed: {e}")
            return False
    
    def get_credentials(self, platform: str) -> Optional[OAuthCredentials]:
        """Get credentials for a specific platform."""
        return self.credentials.get(platform)
    
    def is_authenticated(self, platform: str) -> bool:
        """Check if we have valid credentials for a platform."""
        creds = self.get_credentials(platform)
        return creds is not None and creds.access_token is not None
    
    def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate with all platforms."""
        results = {}
        
        print("Starting authentication for all platforms...")
        
        # Instagram
        print("\n=== Instagram Authentication ===")
        results["instagram"] = self.authenticate_instagram()
        
        # YouTube
        print("\n=== YouTube Authentication ===")
        results["youtube"] = self.authenticate_youtube()
        
        # TikTok
        print("\n=== TikTok Authentication ===")
        results["tiktok"] = self.authenticate_tiktok()
        
        return results
