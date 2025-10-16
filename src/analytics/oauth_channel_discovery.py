"""Channel discovery using existing OAuth credentials"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from analytics.database import AnalyticsDatabase, VideoRecord, VideoMetrics
from managers.oauth_manager import OAuthManager

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
    _metrics: Optional[Dict[str, Any]] = None  # Store raw metrics data

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

class OAuthChannelDiscovery:
    """Channel discovery using existing OAuth credentials"""
    
    def __init__(self, db: AnalyticsDatabase):
        self.db = db
        self.oauth_manager = OAuthManager()
    
    async def discover_youtube_channel_videos(self, max_results: int = 50) -> List[ChannelVideo]:
        """Discover videos from authenticated YouTube channel"""
        if not self.oauth_manager.is_authenticated("youtube"):
            logger.warning("YouTube not authenticated")
            return []
        
        try:
            # Get YouTube service using OAuth credentials
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            creds = self.oauth_manager.get_credentials("youtube")
            if not creds:
                return []
            
            # Create YouTube service
            youtube = build('youtube', 'v3', credentials=Credentials(
                token=creds.access_token,
                refresh_token=creds.refresh_token
            ))
            
            # Get channel info
            channel_response = youtube.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            if not channel_response.get('items'):
                logger.warning("No YouTube channel found")
                return []
            
            channel_id = channel_response['items'][0]['id']
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                playlist_response = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
                
                if not video_ids:
                    break
                
                # Get video details
                video_response = youtube.videos().list(
                    part='snippet,contentDetails,statistics',
                    id=','.join(video_ids)
                ).execute()
                
                for video in video_response['items']:
                    snippet = video['snippet']
                    content_details = video['contentDetails']
                    statistics = video['statistics']
                    
                    # Parse duration
                    duration = self._parse_youtube_duration(content_details['duration'])
                    
                    videos.append(ChannelVideo(
                        platform="youtube",
                        platform_video_id=video['id'],
                        title=snippet['title'],
                        description=snippet['description'],
                        published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                        duration=duration,
                        platform_url=f"https://youtube.com/watch?v={video['id']}",
                        thumbnail_url=snippet['thumbnails'].get('high', {}).get('url', '')
                    ))
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            logger.info(f"Discovered {len(videos)} YouTube videos")
            return videos
            
        except Exception as e:
            logger.error(f"Error discovering YouTube videos: {e}")
            return []
    
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
    
    async def discover_instagram_videos(self, max_results: int = 50) -> List[ChannelVideo]:
        """Discover videos from authenticated Instagram account"""
        if not self.oauth_manager.is_authenticated("instagram"):
            logger.warning("Instagram not authenticated")
            return []
        
        try:
            creds = self.oauth_manager.get_credentials("instagram")
            if not creds:
                return []
            
            async with aiohttp.ClientSession() as session:
                # Get user info first
                user_url = f"https://graph.instagram.com/me"
                params = {
                    "fields": "id,username",
                    "access_token": creds.access_token
                }
                
                async with session.get(user_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Instagram user info error: {response.status}")
                        return []
                    
                    user_data = await response.json()
                    user_id = user_data['id']
                
                # Get user's media
                media_url = f"https://graph.instagram.com/{user_id}/media"
                params = {
                    "fields": "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url",
                    "limit": max_results,
                    "access_token": creds.access_token
                }
                
                async with session.get(media_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Instagram media error: {response.status}")
                        return []
                    
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
                    
                    logger.info(f"Discovered {len(videos)} Instagram videos")
                    return videos
                    
        except Exception as e:
            logger.error(f"Error discovering Instagram videos: {e}")
            return []
    
    async def discover_tiktok_videos(self, max_results: int = 50) -> List[ChannelVideo]:
        """Discover videos from authenticated TikTok account"""
        if not self.oauth_manager.is_authenticated("tiktok"):
            logger.warning("TikTok not authenticated")
            return []
        
        try:
            creds = self.oauth_manager.get_credentials("tiktok")
            if not creds:
                return []
            
            async with aiohttp.ClientSession() as session:
                # Get user info first
                user_url = "https://open.tiktokapis.com/v2/user/info/"
                headers = {
                    "Authorization": f"Bearer {creds.access_token}",
                    "Content-Type": "application/json"
                }
                user_params = {
                    "fields": "open_id,union_id,avatar_url,display_name,bio_description"
                }
                
                async with session.get(user_url, headers=headers, params=user_params) as response:
                    if response.status != 200:
                        logger.error(f"TikTok user info error: {response.status}")
                        try:
                            error_data = await response.json()
                            logger.error(f"TikTok user info error details: {error_data}")
                        except:
                            logger.error(f"TikTok user info error text: {await response.text()}")
                        return []
                    
                    user_data = await response.json()
                    logger.info(f"TikTok user data: {user_data}")
                    user_id = user_data['data']['user']['open_id']
                
                # First get video list to get video IDs
                videos_url = "https://open.tiktokapis.com/v2/video/list/"
                headers = {
                    "Authorization": f"Bearer {creds.access_token}",
                    "Content-Type": "application/json"
                }
                
                # Get basic video list first
                params = {
                    "fields": "id,title,create_time"
                }
                
                data = {
                    "max_count": min(max_results, 20)  # TikTok API limit is 20
                }
                
                async with session.post(videos_url, headers=headers, json=data, params=params) as response:
                    if response.status != 200:
                        logger.error(f"TikTok videos error: {response.status}")
                        try:
                            error_data = await response.json()
                            logger.error(f"TikTok videos error details: {error_data}")
                        except:
                            logger.error(f"TikTok videos error text: {await response.text()}")
                        return []
                    
                    list_data = await response.json()
                    logger.info(f"TikTok videos list response: {list_data}")
                    
                    # Extract video IDs for detailed query
                    video_ids = [item["id"] for item in list_data.get("data", {}).get("videos", [])]
                    
                    if not video_ids:
                        logger.info("No TikTok videos found")
                        return []
                    
                    # Now query detailed video information including metrics
                    query_url = "https://open.tiktokapis.com/v2/video/query/"
                    query_params = {
                        "fields": "id,title,create_time,duration,cover_image_url,share_url,video_description,like_count,comment_count,share_count,view_count"
                    }
                    
                    # Process videos in batches of 20 (TikTok API limit)
                    all_videos = []
                    for i in range(0, len(video_ids), 20):
                        batch_ids = video_ids[i:i+20]
                        
                        query_data = {
                            "filters": {
                                "video_ids": batch_ids
                            }
                        }
                        
                        async with session.post(query_url, headers=headers, json=query_data, params=query_params) as query_response:
                            if query_response.status != 200:
                                logger.error(f"TikTok video query error: {query_response.status}")
                                try:
                                    error_data = await query_response.json()
                                    logger.error(f"TikTok video query error details: {error_data}")
                                except:
                                    logger.error(f"TikTok video query error text: {await query_response.text()}")
                                continue
                            
                            query_result = await query_response.json()
                            logger.info(f"TikTok video query response: {query_result}")
                            
                            for item in query_result.get("data", {}).get("videos", []):
                                all_videos.append(ChannelVideo(
                                    platform="tiktok",
                                    platform_video_id=item["id"],
                                    title=item.get("title", "") or "TikTok Video",
                                    description=item.get("video_description", ""),
                                    published_at=datetime.fromtimestamp(item.get("create_time", 0) / 1000),
                                    duration=float(item.get("duration", 0)),
                                    platform_url=item.get("share_url", ""),
                                    thumbnail_url=item.get("cover_image_url", ""),
                                    # Store metrics for later use
                                    _metrics={
                                        "views": item.get("view_count", 0),
                                        "likes": item.get("like_count", 0),
                                        "comments": item.get("comment_count", 0),
                                        "shares": item.get("share_count", 0)
                                    }
                                ))
                    
                    logger.info(f"Discovered {len(all_videos)} TikTok videos with detailed metrics")
                    return all_videos
                    
        except Exception as e:
            logger.error(f"Error discovering TikTok videos: {e}")
            return []
    
    async def sync_all_authenticated_channels(self, max_results: int = 50) -> Dict[str, List[ChannelVideo]]:
        """Sync videos from all authenticated channels"""
        results = {}
        
        # Check which platforms are authenticated
        authenticated_platforms = []
        if self.oauth_manager.is_authenticated("youtube"):
            authenticated_platforms.append("youtube")
        if self.oauth_manager.is_authenticated("instagram"):
            authenticated_platforms.append("instagram")
        if self.oauth_manager.is_authenticated("tiktok"):
            authenticated_platforms.append("tiktok")
        
        if not authenticated_platforms:
            logger.warning("No platforms authenticated")
            return results
        
        logger.info(f"Syncing videos from authenticated platforms: {', '.join(authenticated_platforms)}")
        
        # Discover videos from each platform
        if "youtube" in authenticated_platforms:
            videos = await self.discover_youtube_channel_videos(max_results)
            results["youtube"] = videos
            await self._sync_videos_to_db(videos)
        
        if "instagram" in authenticated_platforms:
            videos = await self.discover_instagram_videos(max_results)
            results["instagram"] = videos
            await self._sync_videos_to_db(videos)
        
        if "tiktok" in authenticated_platforms:
            videos = await self.discover_tiktok_videos(max_results)
            results["tiktok"] = videos
            await self._sync_videos_to_db(videos)
        
        return results
    
    async def _sync_videos_to_db(self, videos: List[ChannelVideo]):
        """Sync discovered videos to the database"""
        for video in videos:
            # Check if video already exists
            existing = self.db.get_video(video.platform_video_id)
            if existing:
                # Update metrics if available
                if video._metrics:
                    await self._update_video_metrics(video.platform_video_id, video._metrics, video.platform)
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
                
                # Add metrics if available (e.g., from TikTok)
                if video._metrics:
                    await self._update_video_metrics(video.platform_video_id, video._metrics, video.platform)
                    
            except Exception as e:
                logger.error(f"Failed to sync video {video.platform_video_id}: {e}")
    
    async def _update_video_metrics(self, video_id: str, metrics: Dict[str, Any], platform: str = "tiktok"):
        """Update video metrics in the database"""
        try:
            # Create VideoMetrics record
            video_metrics = VideoMetrics(
                video_id=video_id,
                platform=platform,
                views=metrics.get("views", 0),
                likes=metrics.get("likes", 0),
                shares=metrics.get("shares", 0),
                comments=metrics.get("comments", 0),
                collected_at=datetime.now()
            )
            
            self.db.add_metrics(video_metrics)
            logger.info(f"Updated metrics for video {video_id}: {metrics}")
            
        except Exception as e:
            logger.error(f"Failed to update metrics for video {video_id}: {e}")
    
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
    """Example usage of OAuth channel discovery"""
    db = AnalyticsDatabase()
    discovery = OAuthChannelDiscovery(db)
    
    # Sync videos from all authenticated channels
    results = await discovery.sync_all_authenticated_channels()
    
    # Get aggregated stats
    stats = await discovery.get_aggregated_channel_stats()
    
    # Get total views
    total_views, platform_views = discovery.get_total_views_across_platforms()
    
    print(f"Total views across all platforms: {total_views:,}")
    for platform, views in platform_views.items():
        print(f"  {platform}: {views:,} views")

if __name__ == "__main__":
    asyncio.run(main())
