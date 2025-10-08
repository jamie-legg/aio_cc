"""Upload manager for posting videos to social media platforms."""

from pathlib import Path
from typing import Dict, List, Any

from .oauth_manager import OAuthManager
from content_creation.types import FTPUploader, UploadResult
from platform_uploaders import InstagramUploader, YouTubeUploader, TikTokUploader

class UploadManager:
    """Manages video uploads to multiple social media platforms."""
    
    def __init__(self, oauth_manager: OAuthManager):
        self.oauth_manager = oauth_manager
        self.ftp_uploader = FTPUploader()
        
        # Initialize platform uploaders
        self.instagram_uploader = InstagramUploader(self.ftp_uploader)
        self.youtube_uploader = YouTubeUploader()
        self.tiktok_uploader = TikTokUploader()
    
    def upload_to_instagram(self, video_path: Path, metadata: Dict[str, str]) -> UploadResult:
        """Upload video to Instagram Reels using FTP server and video_url parameter."""
        creds = self.oauth_manager.get_credentials("instagram")
        if not creds:
            return UploadResult("instagram", False, error="Not authenticated")
        
        return self.instagram_uploader.upload(video_path, metadata, creds)
    
    
    def upload_to_youtube(self, video_path: Path, metadata: Dict[str, str]) -> UploadResult:
        """Upload video to YouTube Shorts with retry logic."""
        creds = self.oauth_manager.get_credentials("youtube")
        if not creds:
            return UploadResult("youtube", False, error="Not authenticated")
        
        return self.youtube_uploader.upload(video_path, metadata, creds)
    
    
    def upload_to_tiktok(self, video_path: Path, metadata: Dict[str, str]) -> UploadResult:
        """Upload video to TikTok using Content Posting API (Inbox Upload)."""
        creds = self.oauth_manager.get_credentials("tiktok")
        if not creds:
            return UploadResult("tiktok", False, error="Not authenticated")
        
        return self.tiktok_uploader.upload(video_path, metadata, creds)
    
    def _validate_metadata(self, metadata: Dict[str, str], video_path: Path) -> Dict[str, str]:
        """Validate and ensure metadata has required fields with fallbacks."""
        validated = metadata.copy() if metadata else {}
        
        # Ensure we have a title
        if not validated.get('title', '').strip():
            validated['title'] = f"Gaming Clip - {video_path.stem}"
            print(f"⚠️  No title in metadata, using fallback: {validated['title']}")
        
        # Ensure we have caption or hashtags
        if not validated.get('caption', '').strip() and not validated.get('hashtags', '').strip():
            validated['caption'] = "Check out this epic gaming moment! 🎮"
            validated['hashtags'] = "#gaming #shorts"
            print(f"⚠️  No caption/hashtags in metadata, using fallback")
        
        return validated

    def upload_to_all_platforms(self, video_path: Path, metadata: Dict[str, str], 
                              platforms: List[str] = None) -> Dict[str, UploadResult]:
        """Upload video to all specified platforms."""
        if platforms is None:
            platforms = ["instagram", "youtube", "tiktok"]
        
        results = {}
        
        print(f"Uploading {video_path.name} to {len(platforms)} platforms...")
        
        # Validate and fix metadata
        validated_metadata = self._validate_metadata(metadata, video_path)
        
        for platform in platforms:
            print(f"\n--- Uploading to {platform.upper()} ---")
            
            if platform == "instagram":
                results[platform] = self.upload_to_instagram(video_path, validated_metadata)
            elif platform == "youtube":
                results[platform] = self.upload_to_youtube(video_path, validated_metadata)
            elif platform == "tiktok":
                results[platform] = self.upload_to_tiktok(video_path, validated_metadata)
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
                return self.instagram_uploader.get_upload_status(creds)
            elif platform == "youtube":
                return self.youtube_uploader.get_upload_status(creds)
            elif platform == "tiktok":
                return self.tiktok_uploader.get_upload_status(creds)
            else:
                return {"authenticated": False, "error": "Unknown platform"}
            
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
    
    def check_instagram_rate_limit(self) -> Dict[str, Any]:
        """Check Instagram publishing rate limits."""
        creds = self.oauth_manager.get_credentials("instagram")
        if not creds:
            return {"error": "Not authenticated"}
        
        return self.instagram_uploader.check_rate_limit(creds)
