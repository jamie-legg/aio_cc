"""Instagram Reels uploader using Instagram Graph API."""

import os
import time
import requests
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

from ..content_creation.oauth_manager import OAuthCredentials
from ..content_creation.types import FTPUploader, UploadResult


@dataclass
class InstagramUploader:
    """Handles Instagram Reels uploads using FTP server and video_url parameter."""
    
    def __init__(self, ftp_uploader: FTPUploader):
        self.ftp_uploader = ftp_uploader
    
    def upload(self, video_path: Path, metadata: Dict[str, str], creds: OAuthCredentials) -> UploadResult:
        """Upload video to Instagram Reels using FTP server and video_url parameter."""
        try:
            # Step 1: Get Instagram Business Account ID directly
            user_url = f"https://graph.instagram.com/v23.0/me?fields=id,name&access_token={creds.access_token}"

            user_response = requests.get(user_url)
            user_response.raise_for_status()
                
            user_data = user_response.json()
            if not user_data.get('id'):
                return UploadResult("instagram", False, error="No Instagram Business Account found.")
            
            instagram_account_id = user_data['id']
            print(f"✅ Found Instagram Business Account: {instagram_account_id}")
            
            # Step 2: Upload video to FTP server
            print("📤 Uploading video to FTP server...")
            video_url = self.ftp_uploader.upload_video(video_path)
            if not video_url:
                return UploadResult("instagram", False, error="Failed to upload video to FTP server")
            
            print(f"✅ Video uploaded to FTP: {video_url}")
            
            # Step 3: Create media container with video_url
            media_url = f"https://graph.instagram.com/v23.0/{instagram_account_id}/media"
            
            # Create caption with fallbacks
            caption = metadata.get('caption', '').strip()
            hashtags = metadata.get('hashtags', '').strip()
            
            if not caption and not hashtags:
                caption_text = "Check out this epic gaming moment! 🎮 #gaming #shorts"
                print(f"⚠️  Empty caption and hashtags in metadata, using fallback: {caption_text}")
            else:
                caption_text = f"{caption}\n\n{hashtags}".strip()
            
            media_data = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption_text,
                "access_token": creds.access_token
            }
            
            print("Creating Instagram Reels container...")
            media_response = requests.post(media_url, data=media_data)
            media_response.raise_for_status()
            
            container_data = media_response.json()
            if 'error' in container_data:
                return UploadResult("instagram", False, error=f"Container creation failed: {container_data['error']['message']}")
            
            container_id = container_data['id']
            print(f"✅ Container created: {container_id}")
            
            # Step 4: Check container status before publishing
            status_url = f"https://graph.instagram.com/v23.0/{container_id}?fields=status_code&access_token={creds.access_token}"
            

            # Wait for container to be ready (max 5 minutes)
            max_attempts = 30
            for attempt in range(max_attempts):
                status_response = requests.get(status_url)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                status = status_data.get('status_code')
                
                if status == 'FINISHED':
                    print("✅ Container processing finished!")
                    break
                elif status == 'ERROR':
                    return UploadResult("instagram", False, error="Container processing failed")
                elif status == 'EXPIRED':
                    return UploadResult("instagram", False, error="Container expired")
                elif status == 'IN_PROGRESS':
                    print("⏳ Container still processing, waiting 10 seconds...")
                    time.sleep(10)  # Wait 10 seconds
                else:
                    return UploadResult("instagram", False, error=f"Unknown container status: {status}")
            else:
                return UploadResult("instagram", False, error="Container processing timeout")
            
            # Step 5: Publish the Reel
            publish_url = f"https://graph.instagram.com/v23.0/{instagram_account_id}/media_publish"
            publish_data = {
                "creation_id": container_id,
                "access_token": creds.access_token
            }
            
            print("Publishing Instagram Reel...")
            publish_response = requests.post(publish_url, data=publish_data)

            publish_response.raise_for_status()
            
            publish_result = publish_response.json()

            if 'error' in publish_result:
                return UploadResult("instagram", False, error=f"Publishing failed: {publish_result['error']['message']}")
            
            media_id = publish_result['id']
            reel_url = f"https://www.instagram.com/reel/{media_id}/"
            
            print(f"✅ Instagram Reel published successfully! Media ID: {media_id}")
            print(f"🔗 Reel URL: {reel_url}")
            
            return UploadResult(
                "instagram",
                True,
                video_id=media_id,
                url=reel_url
            )
            
        except Exception as e:
            return UploadResult("instagram", False, error=str(e))
    
    def get_upload_status(self, creds: OAuthCredentials) -> Dict[str, any]:
        """Get Instagram upload status and account info."""
        try:
            # Get Instagram Business Account info and rate limits
            user_url = f"https://graph.instagram.com/v23.0/me?fields=id,name&access_token={creds.access_token}"
            user_response = requests.get(user_url)
            user_response.raise_for_status()
            
            user_data = user_response.json()
            if not user_data.get('id'):
                return {"authenticated": False, "error": "No Instagram Business Account found"}
            
            instagram_account_id = user_data['id']
            
            # Get rate limit info
            rate_limit_url = f"https://graph.instagram.com/v23.0/{instagram_account_id}/content_publishing_limit?access_token={creds.access_token}"
            rate_limit_response = requests.get(rate_limit_url)
            
            rate_limit_info = {}
            if rate_limit_response.status_code == 200:
                rate_limit_info = rate_limit_response.json()
            
            return {
                "authenticated": True, 
                "instagram_account_id": instagram_account_id,
                "rate_limits": rate_limit_info
            }
            
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
    
    def check_rate_limit(self, creds: OAuthCredentials) -> Dict[str, any]:
        """Check Instagram publishing rate limits."""
        try:
            # Get Instagram Business Account ID
            user_url = f"https://graph.instagram.com/v23.0/me?fields=id,name&access_token={creds.access_token}"
            user_response = requests.get(user_url)
            user_response.raise_for_status()
            
            user_data = user_response.json()
            if not user_data.get('id'):
                return {"error": "No Instagram Business Account found"}
            
            instagram_account_id = user_data['id']
            
            # Get rate limit info
            rate_limit_url = f"https://graph.instagram.com/v23.0/{instagram_account_id}/content_publishing_limit?access_token={creds.access_token}"
            rate_limit_response = requests.get(rate_limit_url)
            rate_limit_response.raise_for_status()
            
            return rate_limit_response.json()
            
        except Exception as e:
            return {"error": str(e)}
