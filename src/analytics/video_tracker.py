"""Video tracking integration for analytics"""

import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from analytics.database import VideoRecord

logger = logging.getLogger(__name__)

class VideoTracker:
    """Tracks video creation and updates analytics database"""
    
    def __init__(self, analytics_api_url: str = "http://localhost:8000"):
        self.analytics_api_url = analytics_api_url.rstrip('/')
        self.session = requests.Session()
    
    def track_video_creation(self, 
                           video_id: str,
                           title: str,
                           description: str = "",
                           prompt: str = "",
                           platform: str = "sora",
                           duration: float = 0.0,
                           file_path: str = "") -> bool:
        """Track when a video is created"""
        try:
            data = {
                "video_id": video_id,
                "title": title,
                "description": description,
                "prompt": prompt,
                "platform": platform,
                "duration": duration,
                "file_path": file_path
            }
            
            response = self.session.post(f"{self.analytics_api_url}/videos", json=data)
            response.raise_for_status()
            
            logger.info(f"Tracked video creation: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track video creation {video_id}: {e}")
            return False
    
    def track_video_upload(self, 
                         video_id: str,
                         platform: str,
                         platform_video_id: str,
                         platform_url: str = "") -> bool:
        """Track when a video is uploaded to a platform"""
        try:
            updates = {
                "platform": platform,
                "platform_video_id": platform_video_id,
                "platform_url": platform_url,
                "status": "uploaded",
                "uploaded_at": datetime.now().isoformat()
            }
            
            response = self.session.patch(f"{self.analytics_api_url}/videos/{video_id}", json=updates)
            response.raise_for_status()
            
            logger.info(f"Tracked video upload: {video_id} to {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track video upload {video_id}: {e}")
            return False
    
    def track_video_published(self, video_id: str) -> bool:
        """Track when a video is published"""
        try:
            updates = {
                "status": "published"
            }
            
            response = self.session.patch(f"{self.analytics_api_url}/videos/{video_id}", json=updates)
            response.raise_for_status()
            
            logger.info(f"Tracked video published: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track video published {video_id}: {e}")
            return False
    
    def track_video_error(self, video_id: str, error_message: str = "") -> bool:
        """Track when a video processing fails"""
        try:
            updates = {
                "status": "error"
            }
            
            response = self.session.patch(f"{self.analytics_api_url}/videos/{video_id}", json=updates)
            response.raise_for_status()
            
            logger.info(f"Tracked video error: {video_id} - {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track video error {video_id}: {e}")
            return False
    
    def get_video_status(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a video"""
        try:
            response = self.session.get(f"{self.analytics_api_url}/videos/{video_id}")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get video status {video_id}: {e}")
            return None
    
    def get_analytics_summary(self, platform: Optional[str] = None, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get analytics summary"""
        try:
            params = {"days": days}
            if platform:
                params["platform"] = platform
            
            response = self.session.get(f"{self.analytics_api_url}/analytics/summary", params=params)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return None

# Global tracker instance
_tracker: Optional[VideoTracker] = None

def get_video_tracker(analytics_api_url: str = "http://localhost:8000") -> VideoTracker:
    """Get or create the global video tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = VideoTracker(analytics_api_url)
    return _tracker

def track_sora_video_creation(video_id: str, prompt: str, duration: float = 5.0) -> bool:
    """Convenience function to track Sora video creation"""
    tracker = get_video_tracker()
    return tracker.track_video_creation(
        video_id=video_id,
        title=f"Sora Generated Video - {video_id[:8]}",
        description=f"AI-generated video using Sora 2",
        prompt=prompt,
        platform="sora",
        duration=duration
    )

def track_platform_upload(video_id: str, platform: str, platform_video_id: str, platform_url: str = "") -> bool:
    """Convenience function to track platform uploads"""
    tracker = get_video_tracker()
    return tracker.track_video_upload(
        video_id=video_id,
        platform=platform,
        platform_video_id=platform_video_id,
        platform_url=platform_url
    )
