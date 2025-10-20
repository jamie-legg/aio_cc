"""Metrics collector for different social media platforms"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from analytics.database import AnalyticsDatabase, VideoMetrics

logger = logging.getLogger(__name__)

class PlatformMetricsCollector:
    """Base class for platform-specific metrics collection"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.db = AnalyticsDatabase()
    
    async def collect_metrics(self, video_id: str, platform_video_id: str) -> Optional[VideoMetrics]:
        """Collect metrics for a specific video"""
        raise NotImplementedError
    
    async def collect_all_metrics(self) -> List[VideoMetrics]:
        """Collect metrics for all videos on this platform"""
        videos = self.db.list_videos(platform=self.platform, status="published")
        metrics = []
        
        for video in videos:
            if video.platform_video_id:
                try:
                    video_metrics = await self.collect_metrics(video.video_id, video.platform_video_id)
                    if video_metrics:
                        metrics.append(video_metrics)
                        # Save to database
                        self.db.add_metrics(video_metrics)
                except Exception as e:
                    logger.error(f"Failed to collect metrics for {video.video_id}: {e}")
        
        return metrics

class YouTubeMetricsCollector(PlatformMetricsCollector):
    """YouTube metrics collector"""
    
    def __init__(self, api_key: str):
        super().__init__("youtube")
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def collect_metrics(self, video_id: str, platform_video_id: str) -> Optional[VideoMetrics]:
        """Collect YouTube metrics using the YouTube Data API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/videos"
                params = {
                    "part": "statistics",
                    "id": platform_video_id,
                    "key": self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("items"):
                            stats = data["items"][0]["statistics"]
                            
                            views = int(stats.get("viewCount", 0))
                            likes = int(stats.get("likeCount", 0))
                            comments = int(stats.get("commentCount", 0))
                            
                            # Calculate engagement rate
                            engagement_rate = 0.0
                            if views > 0:
                                engagement_rate = (likes + comments) / views
                            
                            return VideoMetrics(
                                video_id=video_id,
                                platform=self.platform,
                                views=views,
                                likes=likes,
                                shares=0,  # YouTube doesn't provide share count in basic API
                                comments=comments,
                                engagement_rate=engagement_rate,
                                collected_at=datetime.now()
                            )
                    else:
                        logger.error(f"YouTube API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error collecting YouTube metrics: {e}")
        
        return None

class InstagramMetricsCollector(PlatformMetricsCollector):
    """Instagram metrics collector (requires Instagram Graph API for Business/Creator accounts)"""
    
    def __init__(self, access_token: str, use_graph_api: bool = True):
        super().__init__("instagram")
        self.access_token = access_token
        self.use_graph_api = use_graph_api
        
        if use_graph_api:
            # Instagram Graph API (Business/Creator accounts - provides views)
            self.base_url = "https://graph.facebook.com/v18.0"
        else:
            # Instagram Basic Display API (Personal accounts - no views)
            self.base_url = "https://graph.instagram.com"
    
    async def collect_metrics(self, video_id: str, platform_video_id: str) -> Optional[VideoMetrics]:
        """Collect Instagram metrics using the Instagram Graph API (Business) or Basic Display API"""
        try:
            async with aiohttp.ClientSession() as session:
                if self.use_graph_api:
                    # Instagram Graph API for Business/Creator accounts
                    url = f"{self.base_url}/{platform_video_id}"
                    params = {
                        "fields": "media_type,like_count,comments_count,video_views,reach,engagement,impressions",
                        "access_token": self.access_token
                    }
                else:
                    # Instagram Basic Display API (legacy)
                    url = f"{self.base_url}/{platform_video_id}"
                    params = {
                        "fields": "media_type,media_url,permalink,timestamp,like_count,comments_count",
                        "access_token": self.access_token
                    }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        likes = int(data.get("like_count", 0))
                        comments = int(data.get("comments_count", 0))
                        
                        # Get views (available in Graph API for Business/Creator accounts)
                        if self.use_graph_api:
                            # For videos, use video_views; for images, use reach or impressions
                            media_type = data.get("media_type", "")
                            if media_type in ["VIDEO", "REELS"]:
                                views = int(data.get("video_views", 0))
                            else:
                                # For images/carousel, use reach or impressions as proxy for views
                                views = int(data.get("reach", data.get("impressions", 0)))
                        else:
                            # Basic Display API doesn't provide views
                            views = 0
                        
                        # Calculate engagement rate
                        engagement_rate = 0.0
                        if views > 0:
                            engagement_rate = (likes + comments) / views
                        elif likes > 0 or comments > 0:
                            # If we have engagement but no views, calculate based on reach
                            reach = int(data.get("reach", 0))
                            if reach > 0:
                                engagement_rate = (likes + comments) / reach
                        
                        return VideoMetrics(
                            video_id=video_id,
                            platform=self.platform,
                            views=views,
                            likes=likes,
                            shares=0,  # Instagram API doesn't provide share count
                            comments=comments,
                            engagement_rate=engagement_rate,
                            collected_at=datetime.now()
                        )
                    else:
                        logger.error(f"Instagram API error: {response.status}")
                        error_text = await response.text()
                        logger.error(f"Error details: {error_text}")
                        
        except Exception as e:
            logger.error(f"Error collecting Instagram metrics: {e}")
        
        return None

class TikTokMetricsCollector(PlatformMetricsCollector):
    """TikTok metrics collector (requires TikTok for Business API)"""
    
    def __init__(self, access_token: str):
        super().__init__("tiktok")
        self.access_token = access_token
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
    
    async def collect_metrics(self, video_id: str, platform_video_id: str) -> Optional[VideoMetrics]:
        """Collect TikTok metrics using the TikTok for Business API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/video/info/"
                headers = {
                    "Access-Token": self.access_token,
                    "Content-Type": "application/json"
                }
                data = {
                    "video_ids": [platform_video_id]
                }
                
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("data", {}).get("videos"):
                            video_data = data["data"]["videos"][0]
                            stats = video_data.get("video_metrics", {})
                            
                            views = int(stats.get("video_views", 0))
                            likes = int(stats.get("likes", 0))
                            shares = int(stats.get("shares", 0))
                            comments = int(stats.get("comments", 0))
                            
                            # Calculate engagement rate
                            engagement_rate = 0.0
                            if views > 0:
                                engagement_rate = (likes + shares + comments) / views
                            
                            return VideoMetrics(
                                video_id=video_id,
                                platform=self.platform,
                                views=views,
                                likes=likes,
                                shares=shares,
                                comments=comments,
                                engagement_rate=engagement_rate,
                                collected_at=datetime.now()
                            )
                    else:
                        logger.error(f"TikTok API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error collecting TikTok metrics: {e}")
        
        return None

class MetricsCollectorManager:
    """Manager for all platform metrics collectors"""
    
    def __init__(self):
        self.collectors: Dict[str, PlatformMetricsCollector] = {}
        self.db = AnalyticsDatabase()
    
    def add_collector(self, platform: str, collector: PlatformMetricsCollector):
        """Add a metrics collector for a platform"""
        self.collectors[platform] = collector
    
    async def collect_all_platforms(self) -> Dict[str, List[VideoMetrics]]:
        """Collect metrics from all configured platforms"""
        results = {}
        
        for platform, collector in self.collectors.items():
            try:
                metrics = await collector.collect_all_metrics()
                results[platform] = metrics
                logger.info(f"Collected {len(metrics)} metrics for {platform}")
            except Exception as e:
                logger.error(f"Failed to collect metrics for {platform}: {e}")
                results[platform] = []
        
        return results
    
    async def collect_platform(self, platform: str) -> List[VideoMetrics]:
        """Collect metrics for a specific platform"""
        if platform not in self.collectors:
            raise ValueError(f"No collector configured for platform: {platform}")
        
        collector = self.collectors[platform]
        return await collector.collect_all_metrics()

# Example usage and configuration
def create_metrics_collector_manager(
    youtube_api_key: Optional[str] = None,
    instagram_access_token: Optional[str] = None,
    tiktok_access_token: Optional[str] = None
) -> MetricsCollectorManager:
    """Create a metrics collector manager with configured platforms"""
    manager = MetricsCollectorManager()
    
    if youtube_api_key:
        manager.add_collector("youtube", YouTubeMetricsCollector(youtube_api_key))
    
    if instagram_access_token:
        # Use Graph API by default for Business/Creator accounts with view counts
        manager.add_collector("instagram", InstagramMetricsCollector(instagram_access_token, use_graph_api=True))
    
    if tiktok_access_token:
        manager.add_collector("tiktok", TikTokMetricsCollector(tiktok_access_token))
    
    return manager

async def main():
    """Example usage of the metrics collector"""
    # Configure with your API keys
    manager = create_metrics_collector_manager(
        youtube_api_key="your_youtube_api_key",
        instagram_access_token="your_instagram_token",
        tiktok_access_token="your_tiktok_token"
    )
    
    # Collect metrics from all platforms
    results = await manager.collect_all_platforms()
    
    for platform, metrics in results.items():
        print(f"{platform}: {len(metrics)} metrics collected")

if __name__ == "__main__":
    asyncio.run(main())
