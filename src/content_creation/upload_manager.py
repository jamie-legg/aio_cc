"""Upload manager for posting videos to social media platforms."""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from .oauth_manager import OAuthManager, OAuthCredentials

@dataclass
class UploadResult:
    """Result of an upload operation."""
    platform: str
    success: bool
    video_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

class UploadManager:
    """Manages video uploads to multiple social media platforms."""
    
    def __init__(self, oauth_manager: OAuthManager):
        self.oauth_manager = oauth_manager
    
    def upload_to_instagram(self, video_path: Path, metadata: Dict[str, str]) -> UploadResult:
        """Upload video to Instagram Reels."""
        creds = self.oauth_manager.get_credentials("instagram")
        if not creds:
            return UploadResult("instagram", False, error="Not authenticated")
        
        try:
            # Instagram Basic Display API doesn't support video uploads directly
            # This would require Instagram Graph API with business account
            # For now, we'll return a placeholder implementation
            
            # Get user info first
            user_info_url = f"https://graph.instagram.com/me?fields=id,username&access_token={creds.access_token}"
            response = requests.get(user_info_url)
            response.raise_for_status()
            
            user_data = response.json()
            print(f"Instagram user: {user_data.get('username')}")
            
            # Note: Instagram Basic Display API doesn't support video uploads
            # You would need Instagram Graph API with a business account
            return UploadResult(
                "instagram", 
                False, 
                error="Instagram Basic Display API doesn't support video uploads. Business account with Graph API required."
            )
            
        except Exception as e:
            return UploadResult("instagram", False, error=str(e))
    
    def upload_to_youtube(self, video_path: Path, metadata: Dict[str, str]) -> UploadResult:
        """Upload video to YouTube Shorts."""
        creds = self.oauth_manager.get_credentials("youtube")
        if not creds:
            return UploadResult("youtube", False, error="Not authenticated")
        
        try:
            # Create YouTube service
            credentials = Credentials(token=creds.access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': metadata.get('title', 'Gaming Clip'),
                    'description': f"{metadata.get('caption', '')}\n\n{metadata.get('hashtags', '')}",
                    'tags': self._extract_hashtags(metadata.get('hashtags', '')),
                    'categoryId': '20',  # Gaming category
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False,
                }
            }
            
            # Upload video
            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Upload progress: {int(status.progress() * 100)}%")
            
            if 'id' in response:
                video_id = response['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                return UploadResult(
                    "youtube",
                    True,
                    video_id=video_id,
                    url=video_url
                )
            else:
                return UploadResult("youtube", False, error="No video ID in response")
                
        except HttpError as e:
            return UploadResult("youtube", False, error=f"YouTube API error: {e}")
        except Exception as e:
            return UploadResult("youtube", False, error=str(e))
    
    def upload_to_tiktok(self, video_path: Path, metadata: Dict[str, str]) -> UploadResult:
        """Upload video to TikTok."""
        creds = self.oauth_manager.get_credentials("tiktok")
        if not creds:
            return UploadResult("tiktok", False, error="Not authenticated")
        
        try:
            # TikTok for Developers API upload process
            # Step 1: Initialize upload
            init_url = "https://open-api.tiktok.com/share/video/upload/"
            
            headers = {
                "Authorization": f"Bearer {creds.access_token}",
                "Content-Type": "application/json"
            }
            
            init_data = {
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": video_path.stat().st_size,
                    "chunk_size": 10000000,  # 10MB chunks
                    "total_chunk_count": 1
                }
            }
            
            init_response = requests.post(init_url, headers=headers, json=init_data)
            init_response.raise_for_status()
            
            init_result = init_response.json()
            
            if init_result.get("error"):
                return UploadResult("tiktok", False, error=init_result["error"]["message"])
            
            upload_url = init_result["data"]["upload_url"]
            publish_id = init_result["data"]["publish_id"]
            
            # Step 2: Upload video file
            with open(video_path, 'rb') as video_file:
                upload_response = requests.post(upload_url, files={"video": video_file})
                upload_response.raise_for_status()
            
            # Step 3: Publish video
            publish_url = "https://open-api.tiktok.com/share/video/publish/"
            
            publish_data = {
                "post_info": {
                    "title": metadata.get('title', 'Gaming Clip'),
                    "description": f"{metadata.get('caption', '')}\n\n{metadata.get('hashtags', '')}",
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "publish_id": publish_id
                }
            }
            
            publish_response = requests.post(publish_url, headers=headers, json=publish_data)
            publish_response.raise_for_status()
            
            publish_result = publish_response.json()
            
            if publish_result.get("error"):
                return UploadResult("tiktok", False, error=publish_result["error"]["message"])
            
            video_id = publish_result["data"]["id"]
            video_url = f"https://www.tiktok.com/@username/video/{video_id}"
            
            return UploadResult(
                "tiktok",
                True,
                video_id=video_id,
                url=video_url
            )
            
        except Exception as e:
            return UploadResult("tiktok", False, error=str(e))
    
    def upload_to_all_platforms(self, video_path: Path, metadata: Dict[str, str], 
                              platforms: List[str] = None) -> Dict[str, UploadResult]:
        """Upload video to all specified platforms."""
        if platforms is None:
            platforms = ["instagram", "youtube", "tiktok"]
        
        results = {}
        
        print(f"Uploading {video_path.name} to {len(platforms)} platforms...")
        
        for platform in platforms:
            print(f"\n--- Uploading to {platform.upper()} ---")
            
            if platform == "instagram":
                results[platform] = self.upload_to_instagram(video_path, metadata)
            elif platform == "youtube":
                results[platform] = self.upload_to_youtube(video_path, metadata)
            elif platform == "tiktok":
                results[platform] = self.upload_to_tiktok(video_path, metadata)
            else:
                results[platform] = UploadResult(platform, False, error="Unknown platform")
            
            # Print result
            result = results[platform]
            if result.success:
                print(f"✅ {platform.upper()}: Success! Video ID: {result.video_id}")
                if result.url:
                    print(f"   URL: {result.url}")
            else:
                print(f"❌ {platform.upper()}: Failed - {result.error}")
        
        return results
    
    def _extract_hashtags(self, hashtags_str: str) -> List[str]:
        """Extract hashtags from string and return as list."""
        if not hashtags_str:
            return []
        
        # Split by space and filter hashtags
        tags = [tag.strip() for tag in hashtags_str.split() if tag.strip().startswith('#')]
        # Remove # symbol for YouTube tags
        return [tag[1:] for tag in tags if len(tag) > 1]
    
    def get_upload_status(self, platform: str) -> Dict[str, Any]:
        """Get upload status and account info for a platform."""
        creds = self.oauth_manager.get_credentials(platform)
        if not creds:
            return {"authenticated": False, "error": "Not authenticated"}
        
        try:
            if platform == "instagram":
                # Get user info
                user_info_url = f"https://graph.instagram.com/me?fields=id,username,account_type&access_token={creds.access_token}"
                response = requests.get(user_info_url)
                response.raise_for_status()
                return {"authenticated": True, "user_info": response.json()}
            
            elif platform == "youtube":
                # Get channel info
                credentials = Credentials(token=creds.access_token)
                youtube = build('youtube', 'v3', credentials=credentials)
                channels = youtube.channels().list(part='snippet', mine=True).execute()
                return {"authenticated": True, "channels": channels.get('items', [])}
            
            elif platform == "tiktok":
                # Get user info
                user_info_url = "https://open-api.tiktok.com/user/info/"
                headers = {"Authorization": f"Bearer {creds.access_token}"}
                response = requests.get(user_info_url, headers=headers)
                response.raise_for_status()
                return {"authenticated": True, "user_info": response.json()}
            
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
        
        return {"authenticated": False, "error": "Unknown platform"}
