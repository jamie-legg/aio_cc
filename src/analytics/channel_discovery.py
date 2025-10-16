"""Channel discovery and video synchronization for analytics"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from analytics.database import AnalyticsDatabase, VideoRecord, VideoMetrics
from analytics.metrics_collector import YouTubeMetricsCollector, InstagramMetricsCollector, TikTokMetricsCollector

logger = logging.getLogger(__name__)

@dataclass
class ChannelVideo:
    """Video discovered from a channel"""
    platform: str
    platform_video_id: str
    title: str
    description: str
    published_at: datetime
    duration: float
    platform_url: str
    thumbnail_url: str = ""

@dataclass
class ChannelStats:
    """Aggregated channel statistics"""
    platform: str
    total_videos: int
    total_views: int
    total_likes: int
    total_shares: int
    total_comments: int
    avg_engagement_rate: float
    most_popular_video: Optional[ChannelVideo] = None

class ChannelDiscovery:
    """Discovers and syncs videos from authorized channels"""
    
    def __init__(self, db: AnalyticsDatabase):
        self.db = db
        self.youtube_collector = None
        self.instagram_collector = None
        self.tiktok_collector = None
    
    def setup_collectors(self, 
                        youtube_api_key: Optional[str] = None,
                        instagram_access_token: Optional[str] = None,
                        tiktok_access_token: Optional[str] = None):
        """Setup platform collectors with API keys"""
        if youtube_api_key:
            self.youtube_collector = YouTubeMetricsCollector(youtube_api_key)
        if instagram_access_token:
            self.instagram_collector = InstagramMetricsCollector(instagram_access_token)
        if tiktok_access_token:
            self.tiktok_collector = TikTokMetricsCollector(tiktok_access_token)
    
    async def discover_youtube_channel_videos(self, channel_id: str, max_results: int = 50) -> List[ChannelVideo]:
        """Discover videos from a YouTube channel"""
        if not self.youtube_collector:
            logger.warning("YouTube collector not configured")
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get channel videos
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "channelId": channel_id,
                    "type": "video",
                    "maxResults": max_results,
                    "order": "date",
                    "key": self.youtube_collector.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = []
                        
                        for item in data.get("items", []):
                            snippet = item["snippet"]
                            video_id = item["id"]["videoId"]
                            
                            # Get video details for duration
                            video_details = await self._get_youtube_video_details(session, video_id)
                            
                            videos.append(ChannelVideo(
                                platform="youtube",
                                platform_video_id=video_id,
                                title=snippet["title"],
                                description=snippet["description"],
                                published_at=datetime.fromisoformat(snippet["publishedAt"].replace('Z', '+00:00')),
                                duration=video_details.get("duration", 0),
                                platform_url=f"https://youtube.com/watch?v={video_id}",
                                thumbnail_url=snippet["thumbnails"].get("high", {}).get("url", "")
                            ))
                        
                        logger.info(f"Discovered {len(videos)} YouTube videos from channel {channel_id}")
                        return videos
                    else:
                        logger.error(f"YouTube API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error discovering YouTube videos: {e}")
        
        return []
    
    async def _get_youtube_video_details(self, session: aiohttp.ClientSession, video_id: str) -> Dict[str, Any]:
        """Get detailed video information including duration"""
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "contentDetails,statistics",
                "id": video_id,
                "key": self.youtube_collector.api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("items"):
                        item = data["items"][0]
                        content_details = item.get("contentDetails", {})
                        statistics = item.get("statistics", {})
                        
                        # Parse duration (ISO 8601 format)
                        duration_str = content_details.get("duration", "PT0S")
                        duration = self._parse_youtube_duration(duration_str)
                        
                        return {
                            "duration": duration,
                            "views": int(statistics.get("viewCount", 0)),
                            "likes": int(statistics.get("likeCount", 0)),
                            "comments": int(statistics.get("commentCount", 0))
                        }
        except Exception as e:
            logger.error(f"Error getting YouTube video details: {e}")
        
        return {"duration": 0, "views": 0, "likes": 0, "comments": 0}
    
    def _parse_youtube_duration(self, duration_str: str) -> float:
        """Parse YouTube duration string (PT1H2M3S) to seconds"""
        import re
        
        # Remove PT prefix
        duration_str = duration_str[2:]
        
        # Parse hours, minutes, seconds
        hours = re.search(r'(\d+)H', duration_str)
        minutes = re.search(r'(\d+)M', duration_str)
        seconds = re.search(r'(\d+)S', duration_str)
        
        total_seconds = 0
        if hours:
            total_seconds += int(hours.group(1)) * 3600
        if minutes:
            total_seconds += int(minutes.group(1)) * 60
        if seconds:
            total_seconds += int(seconds.group(1))
        
        return float(total_seconds)
    
    async def discover_instagram_videos(self, user_id: str, max_results: int = 50) -> List[ChannelVideo]:
        """Discover videos from Instagram account"""
        if not self.instagram_collector:
            logger.warning("Instagram collector not configured")
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.instagram.com/{user_id}/media"
                params = {
                    "fields": "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url",
                    "limit": max_results,
                    "access_token": self.instagram_collector.access_token
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = []
                        
                        for item in data.get("data", []):
                            # Only include video content
                            if item.get("media_type") in ["VIDEO", "CAROUSEL_ALBUM"]:
                                videos.append(ChannelVideo(
                                    platform="instagram",
                                    platform_video_id=item["id"],
                                    title=item.get("caption", "")[:100] or "Instagram Video",
                                    description=item.get("caption", ""),
                                    published_at=datetime.fromisoformat(item["timestamp"].replace('Z', '+00:00')),
                                    duration=0,  # Instagram doesn't provide duration in basic API
                                    platform_url=item.get("permalink", ""),
                                    thumbnail_url=item.get("thumbnail_url", "")
                                ))
                        
                        logger.info(f"Discovered {len(videos)} Instagram videos from user {user_id}")
                        return videos
                    else:
                        logger.error(f"Instagram API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error discovering Instagram videos: {e}")
        
        return []
    
    async def discover_tiktok_videos(self, user_id: str, max_results: int = 50) -> List[ChannelVideo]:
        """Discover videos from TikTok account"""
        if not self.tiktok_collector:
            logger.warning("TikTok collector not configured")
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://business-api.tiktok.com/open_api/v1.3/video/list/"
                headers = {
                    "Access-Token": self.tiktok_collector.access_token,
                    "Content-Type": "application/json"
                }
                data = {
                    "filters": {
                        "user_id": user_id
                    },
                    "max_count": max_results
                }
                
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = []
                        
                        for item in data.get("data", {}).get("videos", []):
                            videos.append(ChannelVideo(
                                platform="tiktok",
                                platform_video_id=item["video_id"],
                                title=item.get("title", "") or "TikTok Video",
                                description=item.get("description", ""),
                                published_at=datetime.fromtimestamp(item.get("create_time", 0)),
                                duration=float(item.get("duration", 0)),
                                platform_url=item.get("share_url", ""),
                                thumbnail_url=item.get("cover_image_url", "")
                            ))
                        
                        logger.info(f"Discovered {len(videos)} TikTok videos from user {user_id}")
                        return videos
                    else:
                        logger.error(f"TikTok API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error discovering TikTok videos: {e}")
        
        return []
    
    async def sync_channel_videos(self, 
                                youtube_channel_id: Optional[str] = None,
                                instagram_user_id: Optional[str] = None,
                                tiktok_user_id: Optional[str] = None,
                                max_results: int = 50) -> Dict[str, List[ChannelVideo]]:
        """Sync videos from all configured channels"""
        results = {}
        
        if youtube_channel_id and self.youtube_collector:
            videos = await self.discover_youtube_channel_videos(youtube_channel_id, max_results)
            results["youtube"] = videos
            await self._sync_videos_to_db(videos)
        
        if instagram_user_id and self.instagram_collector:
            videos = await self.discover_instagram_videos(instagram_user_id, max_results)
            results["instagram"] = videos
            await self._sync_videos_to_db(videos)
        
        if tiktok_user_id and self.tiktok_collector:
            videos = await self.discover_tiktok_videos(tiktok_user_id, max_results)
            results["tiktok"] = videos
            await self._sync_videos_to_db(videos)
        
        return results
    
    async def _sync_videos_to_db(self, videos: List[ChannelVideo]):
        """Sync discovered videos to the database"""
        for video in videos:
            # Check if video already exists
            existing = self.db.get_video(video.platform_video_id)
            if existing:
                continue
            
            # Create video record
            video_record = VideoRecord(
                video_id=video.platform_video_id,
                title=video.title,
                description=video.description,
                platform=video.platform,
                platform_video_id=video.platform_video_id,
                platform_url=video.platform_url,
                duration=video.duration,
                file_path="",  # Not available for discovered videos
                created_at=video.published_at,
                status="published"  # Assume published if discovered
            )
            
            try:
                self.db.add_video(video_record)
                logger.info(f"Synced video: {video.title} ({video.platform})")
            except Exception as e:
                logger.error(f"Failed to sync video {video.platform_video_id}: {e}")
    
    async def get_aggregated_channel_stats(self) -> Dict[str, ChannelStats]:
        """Get aggregated statistics for all channels"""
        stats = {}
        
        # Get all published videos from database
        all_videos = self.db.list_videos(status="published")
        
        # Group by platform
        platform_videos = {}
        for video in all_videos:
            if video.platform not in platform_videos:
                platform_videos[video.platform] = []
            platform_videos[video.platform].append(video)
        
        # Calculate stats for each platform
        for platform, videos in platform_videos.items():
            total_views = 0
            total_likes = 0
            total_shares = 0
            total_comments = 0
            engagement_rates = []
            most_popular_video = None
            max_views = 0
            
            for video in videos:
                # Get latest metrics
                metrics = self.db.get_latest_metrics(video.video_id, platform)
                if metrics:
                    total_views += metrics.views
                    total_likes += metrics.likes
                    total_shares += metrics.shares
                    total_comments += metrics.comments
                    engagement_rates.append(metrics.engagement_rate)
                    
                    # Track most popular video
                    if metrics.views > max_views:
                        max_views = metrics.views
                        most_popular_video = ChannelVideo(
                            platform=platform,
                            platform_video_id=video.platform_video_id,
                            title=video.title,
                            description=video.description,
                            published_at=video.created_at,
                            duration=video.duration,
                            platform_url=video.platform_url
                        )
            
            avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.0
            
            stats[platform] = ChannelStats(
                platform=platform,
                total_videos=len(videos),
                total_views=total_views,
                total_likes=total_likes,
                total_shares=total_shares,
                total_comments=total_comments,
                avg_engagement_rate=avg_engagement,
                most_popular_video=most_popular_video
            )
        
        return stats
    
    def get_total_views_across_platforms(self) -> Tuple[int, Dict[str, int]]:
        """Get total views across all platforms"""
        all_videos = self.db.list_videos(status="published")
        total_views = 0
        platform_views = {}
        
        for video in all_videos:
            metrics = self.db.get_latest_metrics(video.video_id, video.platform)
            if metrics:
                views = metrics.views
                total_views += views
                
                if video.platform not in platform_views:
                    platform_views[video.platform] = 0
                platform_views[video.platform] += views
        
        return total_views, platform_views

async def main():
    """Example usage of channel discovery"""
    db = AnalyticsDatabase()
    discovery = ChannelDiscovery(db)
    
    # Setup with your API keys
    discovery.setup_collectors(
        youtube_api_key="your_youtube_api_key",
        instagram_access_token="your_instagram_token",
        tiktok_access_token="your_tiktok_token"
    )
    
    # Sync videos from your channels
    results = await discovery.sync_channel_videos(
        youtube_channel_id="your_channel_id",
        instagram_user_id="your_instagram_user_id",
        tiktok_user_id="your_tiktok_user_id"
    )
    
    # Get aggregated stats
    stats = await discovery.get_aggregated_channel_stats()
    
    # Get total views
    total_views, platform_views = discovery.get_total_views_across_platforms()
    
    print(f"Total views across all platforms: {total_views:,}")
    for platform, views in platform_views.items():
        print(f"  {platform}: {views:,} views")

if __name__ == "__main__":
    asyncio.run(main())
