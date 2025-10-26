"""FastAPI server for video analytics API"""

import uvicorn
import json
import asyncio
import bcrypt
from fastapi import FastAPI, HTTPException, Query, Path, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from sse_starlette.sse import EventSourceResponse
from jose import JWTError, jwt

from analytics.database import AnalyticsDatabase, VideoRecord, VideoMetrics, User
from analytics.oauth_channel_discovery import OAuthChannelDiscovery, ChannelStats
from content_creation.watcher_events import get_event_emitter
from content_creation.obs_detector import OBSDetector

# JWT settings
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer()

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

# Auth models
class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

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
channel_discovery = OAuthChannelDiscovery(db)

# Auth helper functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get the current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = db.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user

# Auth endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegisterRequest):
    """Register a new user"""
    # Check if username exists
    if db.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    if db.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Hash password and create user
    password_hash = hash_password(user_data.password)
    user_id = db.create_user(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash
    )
    
    # Get the created user
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Create access token
    access_token = create_access_token({"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    )

@app.post("/auth/login", response_model=TokenResponse)
async def login(login_data: UserLoginRequest):
    """Login and get access token"""
    # Get user by username
    user = db.get_user_by_username(login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token({"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at
    )

# Settings endpoints
@app.post("/api/metrics/collect")
async def collect_metrics(current_user: User = Depends(get_current_user)):
    """Trigger fresh metrics collection from all platforms"""
    try:
        from analytics.metrics_collector import InstagramMetricsCollector, YouTubeMetricsCollector, TikTokMetricsCollector
        import os
        
        # Get access tokens from environment
        instagram_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        youtube_token = os.getenv("YOUTUBE_ACCESS_TOKEN") 
        tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        
        collectors = []
        if instagram_token:
            collectors.append(InstagramMetricsCollector(instagram_token, use_graph_api=True))
        if youtube_token:
            collectors.append(YouTubeMetricsCollector(youtube_token))
        if tiktok_token:
            collectors.append(TikTokMetricsCollector(tiktok_token))
        
        if not collectors:
            return {"message": "No platform tokens configured", "collected": 0}
        
        # Get all videos that need metrics collection
        videos = db.list_videos(limit=1000)
        
        collected_count = 0
        for video in videos:
            if not video.platform_video_id:
                continue
                
            # Find appropriate collector
            collector = None
            for c in collectors:
                if c.platform == video.platform:
                    collector = c
                    break
            
            if collector:
                try:
                    metrics = await collector.collect_metrics(video.video_id, video.platform_video_id)
                    if metrics:
                        db.add_metrics(metrics)
                        collected_count += 1
                except Exception as e:
                    print(f"Error collecting metrics for {video.video_id}: {e}")
                    continue
        
        return {
            "message": f"Successfully collected metrics for {collected_count} videos",
            "collected": collected_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")

@app.get("/api/settings", response_model=Dict[str, Any])
async def get_settings(current_user: User = Depends(get_current_user)):
    """Get current user settings and system configuration"""
    # Load config from ConfigManager
    import sys
    import os
    # Add src directory to path if not already there
    src_path = os.path.join(os.path.dirname(__file__), '..')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    from managers.config_manager import ConfigManager
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    return {
        "upload_platforms": {
            "instagram": config.upload_to_instagram,
            "youtube": config.upload_to_youtube,
            "tiktok": config.upload_to_tiktok
        },
        "directories": {
            "watch_dir": config.watch_dir,
            "processed_dir": config.processed_dir
        },
        "scheduling": {
            "auto_schedule": config.auto_schedule,
            "schedule_spacing_hours": config.schedule_spacing_hours,
            "default_post_time_offset": config.default_post_time_offset
        },
        "user": {
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        }
    }

@app.patch("/api/settings", response_model=Dict[str, Any])
async def update_settings(
    settings_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update user settings"""
    import sys
    import os
    # Add src directory to path if not already there
    src_path = os.path.join(os.path.dirname(__file__), '..')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    from managers.config_manager import ConfigManager
    config_manager = ConfigManager()
    
    # Update upload platforms
    if "upload_platforms" in settings_data:
        for platform, enabled in settings_data["upload_platforms"].items():
            config_manager.set_platform_upload(platform, enabled)
    
    # Update directories
    if "directories" in settings_data:
        if "watch_dir" in settings_data["directories"]:
            config_manager.set_watch_dir(settings_data["directories"]["watch_dir"])
        if "processed_dir" in settings_data["directories"]:
            config_manager.set_processed_dir(settings_data["directories"]["processed_dir"])
    
    # Update scheduling
    if "scheduling" in settings_data:
        config_manager.update_scheduling_config(settings_data["scheduling"])
    
    return {"message": "Settings updated successfully"}

@app.post("/api/settings/change-password")
async def change_password(
    password_data: Dict[str, str],
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    # Verify current password
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    new_hash = hash_password(new_password)
    db.update_user_password(current_user.id, new_hash)
    
    return {"message": "Password changed successfully"}

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

@app.get("/videos/top-with-metrics")
async def get_top_videos_with_metrics(
    limit: int = Query(10, description="Number of top videos to return"),
    platform: Optional[str] = Query(None, description="Filter by platform")
):
    """Get top videos with their latest metrics in a single efficient query"""
    try:
        videos = db.get_top_videos_with_metrics(limit=limit, platform=platform)
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/analytics/trends")
async def get_analytics_trends(
    days: int = Query(30, description="Number of days to analyze")
):
    """Get analytics trends data for the specified number of days."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # For now, return mock data since we don't have historical tracking
    # In a real implementation, you would query historical data from the database
    snapshots = []
    
    # Generate mock daily snapshots
    for i in range(days):
        snapshot_date = start_date + timedelta(days=i)
        
        # Mock data - in reality, you'd query actual historical data
        snapshots.append({
            "date": snapshot_date.isoformat(),
            "total_views": max(0, 1000 + (i * 50) - (i % 7) * 100),  # Mock trending data
            "total_likes": max(0, 50 + (i * 5) - (i % 5) * 10),
            "total_comments": max(0, 20 + (i * 2) - (i % 3) * 5),
            "total_shares": max(0, 5 + (i * 1) - (i % 7) * 2),
            "total_videos": max(0, 1 + (i * 0.1)),
            "platforms": {
                "youtube": max(0, 500 + (i * 25) - (i % 7) * 50),
                "instagram": max(0, 300 + (i * 15) - (i % 5) * 30),
                "tiktok": max(0, 200 + (i * 10) - (i % 3) * 20)
            }
        })
    
    return {
        "snapshots": snapshots,
        "days": days,
        "count": len(snapshots)
    }

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
                # Include metrics if available
                vid = stat.most_popular_video
                metrics = getattr(vid, 'metrics', None)
                views = metrics.get("views", 0) if metrics else 0
                likes = metrics.get("likes", 0) if metrics else 0
                comments = metrics.get("comments", 0) if metrics else 0
                shares = metrics.get("shares", 0) if metrics else 0
                
                most_popular = {
                    "platform": vid.platform,
                    "platform_video_id": vid.platform_video_id,
                    "title": vid.title,
                    "platform_url": vid.platform_url,
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares
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

@app.get("/channels/trends")
async def get_channel_trends(days: int = Query(30, description="Number of days to analyze")):
    """Get channel trends data for the specified number of days."""
    try:
        # Get real historical data from daily snapshots
        db = AnalyticsDatabase()
        snapshots = db.get_daily_snapshots(days=days)
        
        if not snapshots:
            # If no historical data exists, return empty data
            return {
                "snapshots": [],
                "days": days,
                "count": 0
            }
        
        # Convert snapshots to the expected format
        formatted_snapshots = []
        for snapshot in snapshots:
            formatted_snapshots.append({
                "date": snapshot.snapshot_date,
                "total_views": snapshot.total_views,
                "total_likes": snapshot.total_likes,
                "total_comments": snapshot.total_comments,
                "total_shares": snapshot.total_shares,
                "total_videos": snapshot.total_videos,
                "platforms": {
                    "youtube": snapshot.youtube_views,
                    "instagram": snapshot.instagram_views,
                    "tiktok": snapshot.tiktok_views
                }
            })
        
        return {
            "snapshots": formatted_snapshots,
            "days": days,
            "count": len(formatted_snapshots)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Watcher Activity Endpoints
@app.get("/api/watcher/stream")
async def watcher_stream(request: Request):
    """
    Server-Sent Events endpoint for real-time watcher activity.
    Streams events as they occur during video processing.
    """
    event_emitter = get_event_emitter()
    
    async def event_generator():
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                # Get next event from queue (non-blocking with timeout)
                event = event_emitter.get_next_event(timeout=1.0)
                
                if event:
                    # Convert event to dict and send as SSE
                    yield {
                        "event": "message",
                        "data": json.dumps(event.to_dict())
                    }
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"SSE error: {e}")
    
    return EventSourceResponse(event_generator())


@app.get("/api/watcher/history")
async def get_watcher_history():
    """
    Get historical watcher events (last 100).
    Returns array of event objects with timestamps.
    """
    try:
        event_emitter = get_event_emitter()
        history = event_emitter.get_history()
        
        return {
            "events": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/watcher/status")
async def get_watcher_status():
    """
    Get current watcher status.
    Returns: idle, watching, or processing
    """
    try:
        event_emitter = get_event_emitter()
        status = event_emitter.get_status()
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/watcher/clear-history")
async def clear_watcher_history():
    """Clear all watcher event history."""
    try:
        event_emitter = get_event_emitter()
        event_emitter.clear_history()
        
        return {
            "success": True,
            "message": "History cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/obs/status")
async def get_obs_status():
    """Get OBS Studio detection status and replay buffer path."""
    try:
        detector = OBSDetector()
        info = detector.get_obs_info()
        
        return {
            "obs_running": info['obs_running'],
            "obs_installed": info['obs_installed'],
            "config_dir": info['config_dir'],
            "active_profile": info['active_profile'],
            "replay_buffer_path": info['replay_buffer_path'],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Schedule Management Endpoints

class SchedulePostRequest(BaseModel):
    video_path: str
    metadata: Dict[str, Any]
    platforms: List[str]
    scheduled_time: Optional[datetime] = None


@app.get("/api/schedule/upcoming")
async def get_upcoming_schedule(hours: int = Query(24, ge=1, le=168)):
    """Get scheduled posts for the next N hours."""
    try:
        db = AnalyticsDatabase()
        posts = db.get_upcoming_schedule(hours=hours)
        
        return {
            "posts": [
                {
                    "id": post.id,
                    "video_path": post.video_path,
                    "metadata": json.loads(post.metadata_json),
                    "platforms": post.platforms.split(","),
                    "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "processed_at": post.processed_at.isoformat() if post.processed_at else None,
                    "error_message": post.error_message,
                    "retry_count": post.retry_count
                }
                for post in posts
            ],
            "count": len(posts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schedule/post/{post_id}")
async def get_scheduled_post(post_id: int):
    """Get a specific scheduled post by ID."""
    try:
        db = AnalyticsDatabase()
        post = db.get_scheduled_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {
            "id": post.id,
            "video_path": post.video_path,
            "metadata": json.loads(post.metadata_json),
            "platforms": post.platforms.split(","),
            "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
            "status": post.status,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "processed_at": post.processed_at.isoformat() if post.processed_at else None,
            "error_message": post.error_message,
            "retry_count": post.retry_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/schedule/post")
async def create_scheduled_post(request: SchedulePostRequest):
    """Manually add a video to the schedule."""
    try:
        from scheduling.scheduler import schedule_video
        from managers.config_manager import ConfigManager
        
        # Get configuration for spacing
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Schedule the video
        scheduled_time = schedule_video(
            video_path=request.video_path,
            metadata=request.metadata,
            platforms=request.platforms,
            spacing_hours=config.schedule_spacing_hours
        )
        
        return {
            "success": True,
            "scheduled_time": scheduled_time.isoformat(),
            "message": f"Video scheduled for {scheduled_time.strftime('%I:%M %p on %B %d')}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/schedule/post/{post_id}/force")
async def force_post_now(post_id: int):
    """Immediately post a scheduled video."""
    try:
        from scheduling.scheduler import force_post_now as force_post
        
        success = force_post(post_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to force post")
        
        return {
            "success": True,
            "message": "Post will be processed immediately"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/schedule/post/{post_id}")
async def cancel_scheduled_post(post_id: int):
    """Cancel/delete a scheduled post."""
    try:
        db = AnalyticsDatabase()
        success = db.cancel_scheduled_post(post_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel post or post not found")
        
        return {
            "success": True,
            "message": "Post cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/schedule/post/{post_id}")
async def reschedule_post(post_id: int, new_time: datetime):
    """Change the scheduled time for a post."""
    try:
        db = AnalyticsDatabase()
        success = db.reschedule_post(post_id, new_time)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reschedule post")
        
        return {
            "success": True,
            "new_time": new_time.isoformat(),
            "message": f"Post rescheduled to {new_time.strftime('%I:%M %p on %B %d')}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/schedule/post/{post_id}/metadata")
async def update_post_metadata(
    post_id: int,
    title: Optional[str] = None,
    caption: Optional[str] = None,
    hashtags: Optional[str] = None,
    platforms: Optional[List[str]] = None
):
    """Update metadata for a scheduled post."""
    try:
        db = AnalyticsDatabase()
        
        # Get current post
        post = db.get_scheduled_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Parse existing metadata
        metadata = json.loads(post.metadata_json) if post.metadata_json else {}
        
        # Update fields if provided
        if title is not None:
            metadata['title'] = title
        if caption is not None:
            metadata['caption'] = caption
        if hashtags is not None:
            metadata['hashtags'] = hashtags
        
        # Update metadata
        success = db.update_scheduled_post_metadata(
            post_id, 
            json.dumps(metadata),
            ",".join(platforms) if platforms else None
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update metadata")
        
        return {
            "success": True,
            "message": "Metadata updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schedule/completed")
async def get_completed_posts(days: int = Query(7, ge=1, le=30)):
    """Get completed posts from the last N days."""
    try:
        db = AnalyticsDatabase()
        # Get completed posts from the database
        completed_posts = db.get_completed_posts(days=days)
        
        posts = []
        for post in completed_posts:
            posts.append({
                "id": post.id,
                "video_path": post.video_path,
                "metadata": json.loads(post.metadata_json) if post.metadata_json else {},
                "platforms": post.platforms.split(",") if post.platforms else [],
                "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
                "processed_at": post.processed_at.isoformat() if post.processed_at else None,
                "status": post.status,
                "created_at": post.created_at.isoformat()
            })
        
        return {
            "posts": posts,
            "count": len(posts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get completed posts: {str(e)}")


# Discord Webhook Integration Endpoints

class DiscordWebhookCreateRequest(BaseModel):
    name: str
    url: str
    platforms: List[str]

class DiscordWebhookUpdateRequest(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    platforms: Optional[List[str]] = None

class DiscordWebhookTestRequest(BaseModel):
    webhook_url: str

# AI Template Endpoints

class TemplateCreateRequest(BaseModel):
    name: str
    prompt_text: str
    is_active: bool = False


class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    prompt_text: Optional[str] = None


class TestPromptRequest(BaseModel):
    prompt_text: str
    filename: str
    game_context: str = "gaming"


@app.get("/api/ai/templates")
async def get_prompt_templates():
    """List all prompt templates."""
    try:
        db = AnalyticsDatabase()
        templates = db.list_prompt_templates()
        
        return {
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "prompt_text": t.prompt_text,
                    "is_active": t.is_active,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None
                }
                for t in templates
            ],
            "count": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/templates/active")
async def get_active_template():
    """Get the currently active template."""
    try:
        db = AnalyticsDatabase()
        template = db.get_active_prompt_template()
        
        if not template:
            return {"template": None, "message": "No active template"}
        
        return {
            "template": {
                "id": template.id,
                "name": template.name,
                "prompt_text": template.prompt_text,
                "is_active": template.is_active,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/templates")
async def create_template(request: TemplateCreateRequest):
    """Create a new prompt template."""
    try:
        from analytics.database import AIPromptTemplate
        
        db = AnalyticsDatabase()
        template = AIPromptTemplate(
            name=request.name,
            prompt_text=request.prompt_text,
            is_active=request.is_active,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # If setting as active, this will deactivate others
        template_id = db.add_prompt_template(template)
        
        if request.is_active:
            db.activate_prompt_template(template_id)
        
        return {
            "success": True,
            "template_id": template_id,
            "message": "Template created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/ai/templates/{template_id}")
async def update_template(template_id: int, request: TemplateUpdateRequest):
    """Update an existing template."""
    try:
        db = AnalyticsDatabase()
        success = db.update_prompt_template(
            template_id=template_id,
            name=request.name,
            prompt_text=request.prompt_text
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "message": "Template updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/ai/templates/{template_id}")
async def delete_template(template_id: int):
    """Delete a template."""
    try:
        db = AnalyticsDatabase()
        success = db.delete_prompt_template(template_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "message": "Template deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/templates/{template_id}/activate")
async def activate_template(template_id: int):
    """Set a template as active (deactivates all others)."""
    try:
        db = AnalyticsDatabase()
        success = db.activate_prompt_template(template_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "message": "Template activated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/test-prompt")
async def test_prompt(request: TestPromptRequest):
    """Test a prompt with sample filename and return generated metadata."""
    try:
        from managers.ai_manager import AIManager
        
        # Create AI manager
        ai_manager = AIManager()
        
        # Temporarily use the provided prompt by creating a test template
        # In a real implementation, you'd inject the prompt directly into generation
        original_method = ai_manager._generate_metadata_local
        
        def temp_generate(filename: str, game_context: str):
            # Use the test prompt
            prompt = request.prompt_text.replace("{filename}", filename).replace("{game_context}", game_context)
            
            completion = ai_manager.client.chat.completions.create(
                model=ai_manager.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates social media metadata. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            return json.loads(response_text)
        
        ai_manager._generate_metadata_local = temp_generate
        
        # Generate metadata
        metadata = ai_manager.generate_metadata(request.filename, request.game_context)
        
        # Restore original method
        ai_manager._generate_metadata_local = original_method
        
        return {
            "success": True,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Discord Webhook Management Endpoints

@app.get("/api/integrations/discord")
async def list_discord_webhooks(current_user: User = Depends(get_current_user)):
    """List all Discord webhook configurations."""
    try:
        import sys
        import os
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.config_manager import ConfigManager
        config_manager = ConfigManager()
        webhooks = config_manager.list_discord_webhooks()
        
        return {
            "webhooks": webhooks,
            "count": len(webhooks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/integrations/discord")
async def create_discord_webhook(
    request: DiscordWebhookCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new Discord webhook configuration."""
    try:
        import sys
        import os
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        webhook_id = config_manager.add_discord_webhook(
            name=request.name,
            url=request.url,
            platforms=request.platforms
        )
        
        return {
            "success": True,
            "webhook_id": webhook_id,
            "message": "Discord webhook created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/integrations/discord/{webhook_id}")
async def update_discord_webhook(
    webhook_id: str,
    request: DiscordWebhookUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update an existing Discord webhook configuration."""
    try:
        import sys
        import os
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        success = config_manager.update_discord_webhook(
            webhook_id=webhook_id,
            name=request.name,
            url=request.url,
            platforms=request.platforms
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        return {
            "success": True,
            "message": "Discord webhook updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/integrations/discord/{webhook_id}")
async def delete_discord_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a Discord webhook configuration."""
    try:
        import sys
        import os
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        success = config_manager.remove_discord_webhook(webhook_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        return {
            "success": True,
            "message": "Discord webhook deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/integrations/discord/test")
async def test_discord_webhook(
    request: DiscordWebhookTestRequest,
    current_user: User = Depends(get_current_user)
):
    """Test a Discord webhook with a sample message."""
    try:
        import sys
        import os
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.discord_service import DiscordWebhookService
        
        discord_service = DiscordWebhookService()
        success = discord_service.test_webhook(request.webhook_url)
        
        if success:
            return {
                "success": True,
                "message": "Webhook test successful - check your Discord channel!"
            }
        else:
            return {
                "success": False,
                "message": "Webhook test failed - check the URL and permissions"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Failed Uploads Management Endpoints

@app.get("/api/uploads/failed")
async def list_failed_uploads():
    """List all failed uploads available for retry."""
    try:
        import sys
        import os
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.upload_manager import UploadManager
        from managers.oauth_manager import OAuthManager
        
        # Initialize managers
        oauth_manager = OAuthManager()
        upload_manager = UploadManager(oauth_manager)
        
        # Get failed uploads
        failed_uploads = upload_manager.list_failed_uploads()
        
        # Format for API response
        uploads_list = []
        for key, upload in failed_uploads.items():
            uploads_list.append({
                "key": key,
                "video_path": upload.get("video_path", ""),
                "platform": upload.get("platform", ""),
                "metadata": upload.get("metadata", {}),
                "error": upload.get("error", ""),
                "timestamp": upload.get("timestamp", ""),
                "retry_count": upload.get("retry_count", 0)
            })
        
        return {
            "failed_uploads": uploads_list,
            "count": len(uploads_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/uploads/retry/{upload_key}")
async def retry_failed_upload(
    upload_key: str
):
    """Retry a specific failed upload."""
    try:
        import sys
        import os
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.upload_manager import UploadManager
        from managers.oauth_manager import OAuthManager
        
        # Initialize managers
        oauth_manager = OAuthManager()
        upload_manager = UploadManager(oauth_manager)
        
        # Parse upload key (format: video_name_platform)
        parts = upload_key.rsplit('_', 1)
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid upload key format")
        
        video_name, platform = parts
        
        # Retry the upload
        result = upload_manager.retry_failed_upload(video_name, platform)
        
        return {
            "success": result.success,
            "platform": result.platform,
            "video_id": result.video_id,
            "url": result.url,
            "error": result.error,
            "message": f"Successfully retried {platform.upper()} upload" if result.success else f"Retry failed: {result.error}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/uploads/failed/{upload_key}")
async def remove_failed_upload(
    upload_key: str
):
    """Remove a failed upload from the retry queue."""
    try:
        import sys
        import os
        import json
        from pathlib import Path
        
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Load failed uploads
        failed_uploads_file = Path.home() / ".content_creation" / "failed_uploads.json"
        
        if not failed_uploads_file.exists():
            raise HTTPException(status_code=404, detail="No failed uploads found")
        
        with open(failed_uploads_file, 'r') as f:
            failed_uploads = json.load(f)
        
        # Remove the upload
        if upload_key not in failed_uploads:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        del failed_uploads[upload_key]
        
        # Save updated list
        with open(failed_uploads_file, 'w') as f:
            json.dump(failed_uploads, f, indent=2)
        
        return {
            "success": True,
            "message": f"Removed {upload_key} from failed uploads"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/uploads/retry-all")
async def retry_all_failed_uploads(
    platforms: Optional[List[str]] = None
):
    """Retry all failed uploads for specified platforms."""
    try:
        import sys
        import os
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.upload_manager import UploadManager
        from managers.oauth_manager import OAuthManager
        
        # Initialize managers
        oauth_manager = OAuthManager()
        upload_manager = UploadManager(oauth_manager)
        
        # Retry all uploads
        results = upload_manager.retry_all_failed_uploads(platforms=platforms)
        
        # Format results
        successful = sum(1 for result in results.values() if result.success)
        failed = len(results) - successful
        
        return {
            "success": True,
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": {
                key: {
                    "success": result.success,
                    "platform": result.platform,
                    "error": result.error
                }
                for key, result in results.items()
            },
            "message": f"Retry complete: {successful} successful, {failed} failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Missed Replays Management Endpoints

def get_missed_replays():
    """Find videos in watch dir not in processed or scheduled"""
    import sys
    import os
    from pathlib import Path
    
    # Add src directory to path if not already there
    src_path = os.path.join(os.path.dirname(__file__), '..')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    from managers.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    watch_dir = Path(config.watch_dir)
    processed_dir = Path(config.processed_dir)
    
    if not watch_dir.exists():
        return []
    
    # Get all videos in watch directory
    video_exts = config.video_extensions
    watch_videos = [f for f in watch_dir.iterdir() 
                    if f.is_file() and f.suffix.lower() in video_exts]
    
    # Get processed filenames and scheduled video paths
    db = AnalyticsDatabase()
    scheduled_posts = db.get_all_scheduled_posts()
    scheduled_paths = set()
    for post in scheduled_posts:
        # Check both the direct path and the filename
        scheduled_paths.add(post.video_path)
        scheduled_paths.add(Path(post.video_path).name)
    
    processed_names = {f.name for f in processed_dir.iterdir() if f.is_file()}
    
    # Filter unprocessed
    missed = []
    for video in watch_videos:
        # Check if video is not processed and not scheduled
        if video.name not in processed_names and video.name not in scheduled_paths and str(video) not in scheduled_paths:
            missed.append({
                'filename': video.name,
                'file_path': str(video),
                'file_size': video.stat().st_size,
                'modified_time': video.stat().st_mtime
            })
    
    # Sort by modified time (newest first)
    missed.sort(key=lambda x: x['modified_time'], reverse=True)
    
    return missed


@app.get("/api/missed-replays")
async def get_missed_replays_endpoint(current_user: User = Depends(get_current_user)):
    """Get list of unprocessed videos in watch directory."""
    try:
        replays = get_missed_replays()
        return {
            "success": True,
            "count": len(replays),
            "replays": replays
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/schedule-replay")
async def schedule_replay(
    video_path: str,
    scheduled_time: Optional[str] = None,
    platforms: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
):
    """Schedule a single missed replay for posting."""
    try:
        import sys
        import os
        from pathlib import Path
        from datetime import datetime
        
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.config_manager import ConfigManager
        from managers.ai_manager import AIManager
        from content_creation.video_processor import VideoProcessor
        from content_creation.clip_watcher import process_video_for_scheduling
        from scheduling.scheduler import get_next_slot
        
        # Validate video path exists
        video_file = Path(video_path)
        if not video_file.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Initialize managers
        config_manager = ConfigManager()
        ai_manager = AIManager()
        video_processor = VideoProcessor()
        
        # Get platforms from config if not provided
        if not platforms:
            platforms = config_manager.get_upload_platforms()
        
        if not platforms:
            raise HTTPException(status_code=400, detail="No platforms configured")
        
        # Process the video
        processed_path, metadata = process_video_for_scheduling(
            video_file, ai_manager, video_processor, config_manager
        )
        
        # Determine scheduled time
        db = AnalyticsDatabase()
        if scheduled_time:
            # Parse provided time
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid datetime format")
        else:
            # Get next available slot using configured spacing
            config = config_manager.get_config()
            next_slots = [get_next_slot(platform, db, spacing_hours=config.schedule_spacing_hours) for platform in platforms]
            scheduled_dt = max(next_slots)
        
        # Create scheduled post
        from analytics.database import ScheduledPost
        post = ScheduledPost(
            video_path=str(processed_path),
            metadata_json=json.dumps(metadata),
            platforms=",".join(platforms),
            scheduled_time=scheduled_dt,
            status="pending",
            created_at=datetime.now()
        )
        
        post_id = db.add_scheduled_post(post)
        
        return {
            "success": True,
            "post_id": post_id,
            "scheduled_time": scheduled_dt.isoformat(),
            "video_path": str(processed_path),
            "metadata": metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/schedule-replays-batch")
async def schedule_replays_batch(
    video_paths: List[str],
    platforms: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
):
    """Schedule multiple missed replays at once, spaced 1 hour apart."""
    try:
        import sys
        import os
        from pathlib import Path
        from datetime import datetime
        
        # Add src directory to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from managers.config_manager import ConfigManager
        from managers.ai_manager import AIManager
        from content_creation.video_processor import VideoProcessor
        from content_creation.clip_watcher import process_video_for_scheduling
        from scheduling.scheduler import space_videos
        
        # Initialize managers
        config_manager = ConfigManager()
        ai_manager = AIManager()
        video_processor = VideoProcessor()
        
        # Get platforms from config if not provided
        if not platforms:
            platforms = config_manager.get_upload_platforms()
        
        if not platforms:
            raise HTTPException(status_code=400, detail="No platforms configured")
        
        # Get scheduled times for all videos (spaced 1 hour apart)
        db = AnalyticsDatabase()
        scheduled_times = space_videos(platforms, len(video_paths))
        
        results = []
        
        for i, video_path in enumerate(video_paths):
            try:
                video_file = Path(video_path)
                if not video_file.exists():
                    results.append({
                        "video_path": video_path,
                        "success": False,
                        "error": "Video file not found"
                    })
                    continue
                
                # Process the video
                processed_path, metadata = process_video_for_scheduling(
                    video_file, ai_manager, video_processor, config_manager
                )
                
                # Create scheduled post
                from analytics.database import ScheduledPost
                post = ScheduledPost(
                    video_path=str(processed_path),
                    metadata_json=json.dumps(metadata),
                    platforms=",".join(platforms),
                    scheduled_time=scheduled_times[i],
                    status="pending",
                    created_at=datetime.now()
                )
                
                post_id = db.add_scheduled_post(post)
                
                results.append({
                    "video_path": video_path,
                    "success": True,
                    "post_id": post_id,
                    "scheduled_time": scheduled_times[i].isoformat(),
                    "metadata": metadata
                })
            except Exception as e:
                results.append({
                    "video_path": video_path,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "total": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
