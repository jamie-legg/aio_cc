"""FastAPI server for video analytics API"""

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from analytics.database import AnalyticsDatabase, VideoRecord, VideoMetrics
from analytics.channel_discovery import ChannelDiscovery, ChannelStats

# Pydantic models for API
class VideoCreateRequest(BaseModel):
    video_id: str
    title: str
    description: str = ""
    prompt: str = ""
    platform: str
    platform_video_id: str = ""
    platform_url: str = ""
    duration: float = 0.0
    file_path: str = ""

class VideoUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    platform_video_id: Optional[str] = None
    platform_url: Optional[str] = None
    status: Optional[str] = None
    uploaded_at: Optional[datetime] = None

class MetricsRequest(BaseModel):
    video_id: str
    platform: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0

class VideoResponse(BaseModel):
    id: int
    video_id: str
    title: str
    description: str
    prompt: str
    platform: str
    platform_video_id: str
    platform_url: str
    duration: float
    file_path: str
    created_at: datetime
    uploaded_at: Optional[datetime]
    status: str

class MetricsResponse(BaseModel):
    id: int
    video_id: str
    platform: str
    views: int
    likes: int
    shares: int
    comments: int
    engagement_rate: float
    collected_at: datetime

class AnalyticsSummaryResponse(BaseModel):
    total_videos: int
    status_counts: Dict[str, int]
    avg_metrics: Dict[str, float]
    period_days: int
    platform: str

class ChannelStatsResponse(BaseModel):
    platform: str
    total_videos: int
    total_views: int
    total_likes: int
    total_shares: int
    total_comments: int
    avg_engagement_rate: float
    most_popular_video: Optional[Dict[str, Any]] = None

class AggregatedStatsResponse(BaseModel):
    total_views_across_platforms: int
    platform_breakdown: Dict[str, int]
    channel_stats: List[ChannelStatsResponse]

# Initialize FastAPI app
app = FastAPI(
    title="Video Analytics API",
    description="API for tracking video creation and platform metrics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and channel discovery
db = AnalyticsDatabase()
channel_discovery = ChannelDiscovery(db)

# Video endpoints
@app.post("/videos", response_model=VideoResponse)
async def create_video(video_data: VideoCreateRequest):
    """Create a new video record"""
    video = VideoRecord(
        video_id=video_data.video_id,
        title=video_data.title,
        description=video_data.description,
        prompt=video_data.prompt,
        platform=video_data.platform,
        platform_video_id=video_data.platform_video_id,
        platform_url=video_data.platform_url,
        duration=video_data.duration,
        file_path=video_data.file_path,
        created_at=datetime.now()
    )
    
    try:
        video_id = db.add_video(video)
        created_video = db.get_video(video_data.video_id)
        if not created_video:
            raise HTTPException(status_code=500, detail="Failed to retrieve created video")
        
        return VideoResponse(
            id=created_video.id,
            video_id=created_video.video_id,
            title=created_video.title,
            description=created_video.description,
            prompt=created_video.prompt,
            platform=created_video.platform,
            platform_video_id=created_video.platform_video_id,
            platform_url=created_video.platform_url,
            duration=created_video.duration,
            file_path=created_video.file_path,
            created_at=created_video.created_at,
            uploaded_at=created_video.uploaded_at,
            status=created_video.status
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str = Path(..., description="Video ID")):
    """Get a video record by ID"""
    video = db.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return VideoResponse(
        id=video.id,
        video_id=video.video_id,
        title=video.title,
        description=video.description,
        prompt=video.prompt,
        platform=video.platform,
        platform_video_id=video.platform_video_id,
        platform_url=video.platform_url,
        duration=video.duration,
        file_path=video.file_path,
        created_at=video.created_at,
        uploaded_at=video.uploaded_at,
        status=video.status
    )

@app.get("/videos", response_model=List[VideoResponse])
async def list_videos(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, description="Number of videos to return"),
    offset: int = Query(0, description="Number of videos to skip")
):
    """List videos with optional filtering"""
    videos = db.list_videos(platform=platform, status=status, limit=limit, offset=offset)
    
    return [
        VideoResponse(
            id=video.id,
            video_id=video.video_id,
            title=video.title,
            description=video.description,
            prompt=video.prompt,
            platform=video.platform,
            platform_video_id=video.platform_video_id,
            platform_url=video.platform_url,
            duration=video.duration,
            file_path=video.file_path,
            created_at=video.created_at,
            uploaded_at=video.uploaded_at,
            status=video.status
        ) for video in videos
    ]

@app.patch("/videos/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: str = Path(..., description="Video ID"),
    updates: VideoUpdateRequest = None
):
    """Update a video record"""
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    # Convert to dict and remove None values
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No valid updates provided")
    
    success = db.update_video(video_id, update_dict)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found or no changes made")
    
    updated_video = db.get_video(video_id)
    if not updated_video:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated video")
    
    return VideoResponse(
        id=updated_video.id,
        video_id=updated_video.video_id,
        title=updated_video.title,
        description=updated_video.description,
        prompt=updated_video.prompt,
        platform=updated_video.platform,
        platform_video_id=updated_video.platform_video_id,
        platform_url=updated_video.platform_url,
        duration=updated_video.duration,
        file_path=updated_video.file_path,
        created_at=updated_video.created_at,
        uploaded_at=updated_video.uploaded_at,
        status=updated_video.status
    )

# Metrics endpoints
@app.post("/metrics", response_model=MetricsResponse)
async def add_metrics(metrics_data: MetricsRequest):
    """Add video metrics"""
    metrics = VideoMetrics(
        video_id=metrics_data.video_id,
        platform=metrics_data.platform,
        views=metrics_data.views,
        likes=metrics_data.likes,
        shares=metrics_data.shares,
        comments=metrics_data.comments,
        engagement_rate=metrics_data.engagement_rate,
        collected_at=datetime.now()
    )
    
    try:
        metrics_id = db.add_metrics(metrics)
        # Return the created metrics
        return MetricsResponse(
            id=metrics_id,
            video_id=metrics.video_id,
            platform=metrics.platform,
            views=metrics.views,
            likes=metrics.likes,
            shares=metrics.shares,
            comments=metrics.comments,
            engagement_rate=metrics.engagement_rate,
            collected_at=metrics.collected_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/metrics/{video_id}/latest", response_model=Optional[MetricsResponse])
async def get_latest_metrics(
    video_id: str = Path(..., description="Video ID"),
    platform: Optional[str] = Query(None, description="Filter by platform")
):
    """Get latest metrics for a video"""
    metrics = db.get_latest_metrics(video_id, platform)
    if not metrics:
        return None
    
    return MetricsResponse(
        id=metrics.id,
        video_id=metrics.video_id,
        platform=metrics.platform,
        views=metrics.views,
        likes=metrics.likes,
        shares=metrics.shares,
        comments=metrics.comments,
        engagement_rate=metrics.engagement_rate,
        collected_at=metrics.collected_at
    )

@app.get("/metrics/{video_id}/history", response_model=List[MetricsResponse])
async def get_metrics_history(
    video_id: str = Path(..., description="Video ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(30, description="Number of records to return")
):
    """Get metrics history for a video"""
    metrics_list = db.get_metrics_history(video_id, platform, limit)
    
    return [
        MetricsResponse(
            id=metrics.id,
            video_id=metrics.video_id,
            platform=metrics.platform,
            views=metrics.views,
            likes=metrics.likes,
            shares=metrics.shares,
            comments=metrics.comments,
            engagement_rate=metrics.engagement_rate,
            collected_at=metrics.collected_at
        ) for metrics in metrics_list
    ]

# Analytics endpoints
@app.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    days: int = Query(30, description="Number of days to analyze")
):
    """Get analytics summary"""
    summary = db.get_analytics_summary(platform, days)
    return AnalyticsSummaryResponse(**summary)

@app.get("/channels/sync", response_model=Dict[str, Any])
async def sync_channel_videos(
    youtube_channel_id: Optional[str] = Query(None, description="YouTube channel ID"),
    instagram_user_id: Optional[str] = Query(None, description="Instagram user ID"),
    tiktok_user_id: Optional[str] = Query(None, description="TikTok user ID"),
    max_results: int = Query(50, description="Maximum videos to sync per platform")
):
    """Sync videos from your authorized channels"""
    try:
        # Setup collectors with environment variables
        import os
        channel_discovery.setup_collectors(
            youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
            instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            tiktok_access_token=os.getenv("TIKTOK_ACCESS_TOKEN")
        )
        
        results = await channel_discovery.sync_channel_videos(
            youtube_channel_id=youtube_channel_id,
            instagram_user_id=instagram_user_id,
            tiktok_user_id=tiktok_user_id,
            max_results=max_results
        )
        
        # Count total videos synced
        total_synced = sum(len(videos) for videos in results.values())
        
        return {
            "message": f"Successfully synced {total_synced} videos",
            "platforms": {platform: len(videos) for platform, videos in results.items()},
            "details": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/channels/stats", response_model=AggregatedStatsResponse)
async def get_aggregated_channel_stats():
    """Get aggregated statistics across all your channels"""
    try:
        # Get channel stats
        stats = await channel_discovery.get_aggregated_channel_stats()
        
        # Get total views across platforms
        total_views, platform_breakdown = channel_discovery.get_total_views_across_platforms()
        
        # Convert to response format
        channel_stats = []
        for platform, stat in stats.items():
            most_popular = None
            if stat.most_popular_video:
                most_popular = {
                    "platform": stat.most_popular_video.platform,
                    "platform_video_id": stat.most_popular_video.platform_video_id,
                    "title": stat.most_popular_video.title,
                    "platform_url": stat.most_popular_video.platform_url
                }
            
            channel_stats.append(ChannelStatsResponse(
                platform=stat.platform,
                total_videos=stat.total_videos,
                total_views=stat.total_views,
                total_likes=stat.total_likes,
                total_shares=stat.total_shares,
                total_comments=stat.total_comments,
                avg_engagement_rate=stat.avg_engagement_rate,
                most_popular_video=most_popular
            ))
        
        return AggregatedStatsResponse(
            total_views_across_platforms=total_views,
            platform_breakdown=platform_breakdown,
            channel_stats=channel_stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/channels/total-views")
async def get_total_views():
    """Get total views across all platforms"""
    try:
        total_views, platform_breakdown = channel_discovery.get_total_views_across_platforms()
        
        return {
            "total_views": total_views,
            "platform_breakdown": platform_breakdown,
            "formatted_total": f"{total_views:,}",
            "platforms": len(platform_breakdown)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
