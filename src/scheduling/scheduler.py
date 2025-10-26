"""Core scheduling logic for automated video posting."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from analytics.database import AnalyticsDatabase, ScheduledPost

logger = logging.getLogger(__name__)


def get_next_slot(platform: str, db: AnalyticsDatabase, base_time: Optional[datetime] = None, 
                  spacing_hours: int = 1) -> datetime:
    """
    Get the next available slot for a platform.
    
    Args:
        platform: Platform name (youtube, instagram, tiktok)
        db: Database instance
        base_time: Starting time (defaults to next slot from now)
        spacing_hours: Hours between posts on same platform
    
    Returns:
        Next available datetime slot
    """
    if base_time is None:
        now = datetime.now()
        next_slot = (now + timedelta(hours=spacing_hours)).replace(minute=0, second=0, microsecond=0)
    else:
        next_slot = base_time.replace(minute=0, second=0, microsecond=0)
    
    # Check if slot is taken, keep incrementing until we find a free slot
    while db.has_post_at_time(platform, next_slot):
        next_slot += timedelta(hours=spacing_hours)
    
    return next_slot


def schedule_video(video_path: str, metadata: Dict[str, Any], platforms: List[str], 
                  db_path: str = "analytics.db", spacing_hours: int = 1) -> datetime:
    """
    Schedule a video for posting.
    
    Args:
        video_path: Path to the video file
        metadata: Dictionary with title, description, hashtags
        platforms: List of platforms to post to
        db_path: Path to the analytics database
        spacing_hours: Hours between posts on same platform
    
    Returns:
        Scheduled datetime for the post
    """
    db = AnalyticsDatabase(db_path)
    
    # Get the earliest available slot across all platforms
    next_slots = [get_next_slot(platform, db, spacing_hours=spacing_hours) for platform in platforms]
    scheduled_time = max(next_slots)  # Use the latest slot to avoid conflicts
    
    # Create scheduled post record
    post = ScheduledPost(
        video_path=video_path,
        metadata_json=json.dumps(metadata),
        platforms=",".join(platforms),
        scheduled_time=scheduled_time,
        status="pending",
        created_at=datetime.now()
    )
    
    post_id = db.add_scheduled_post(post)
    logger.info(f"Scheduled video {video_path} for {scheduled_time} (ID: {post_id})")
    
    return scheduled_time


def check_due_posts(db_path: str = "analytics.db") -> List[ScheduledPost]:
    """
    Find posts that are ready to be published (scheduled_time <= now).
    
    Args:
        db_path: Path to the analytics database
    
    Returns:
        List of due scheduled posts
    """
    db = AnalyticsDatabase(db_path)
    now = datetime.now()
    
    # Get pending posts
    pending_posts = db.get_pending_posts()
    
    # Filter for posts that are due
    due_posts = [
        post for post in pending_posts
        if post.scheduled_time and post.scheduled_time <= now
    ]
    
    return due_posts


def get_time_until_post(scheduled_time: datetime) -> Dict[str, int]:
    """
    Calculate countdown time until a post.
    
    Args:
        scheduled_time: When the post is scheduled
    
    Returns:
        Dictionary with hours, minutes, seconds until post
    """
    now = datetime.now()
    if scheduled_time <= now:
        return {"hours": 0, "minutes": 0, "seconds": 0, "total_seconds": 0}
    
    delta = scheduled_time - now
    total_seconds = int(delta.total_seconds())
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": total_seconds
    }


def space_videos(platforms: List[str], count: int, db_path: str = "analytics.db") -> List[datetime]:
    """
    Distribute multiple videos across hours for given platforms.
    
    Args:
        platforms: List of platforms
        count: Number of videos to space out
        db_path: Path to the analytics database
    
    Returns:
        List of scheduled times
    """
    db = AnalyticsDatabase(db_path)
    scheduled_times = []
    
    current_slot = None
    for i in range(count):
        # Get next available slot
        next_slots = [get_next_slot(platform, db, current_slot) for platform in platforms]
        slot = max(next_slots)
        scheduled_times.append(slot)
        
        # Next video should be at least 1 hour later
        current_slot = slot + timedelta(hours=1)
    
    return scheduled_times


def force_post_now(post_id: int, db_path: str = "analytics.db") -> bool:
    """
    Force a scheduled post to execute immediately.
    
    Args:
        post_id: ID of the scheduled post
        db_path: Path to the analytics database
    
    Returns:
        True if successful
    """
    db = AnalyticsDatabase(db_path)
    
    # Update scheduled time to now
    now = datetime.now()
    success = db.reschedule_post(post_id, now)
    
    if success:
        logger.info(f"Forced post {post_id} to post immediately")
    
    return success


def reschedule_video(post_id: int, new_time: datetime, db_path: str = "analytics.db") -> bool:
    """
    Reschedule a post to a new time.
    
    Args:
        post_id: ID of the scheduled post
        new_time: New scheduled time
        db_path: Path to the analytics database
    
    Returns:
        True if successful
    """
    db = AnalyticsDatabase(db_path)
    
    # Round to nearest hour
    new_time_rounded = new_time.replace(minute=0, second=0, microsecond=0)
    
    success = db.reschedule_post(post_id, new_time_rounded)
    
    if success:
        logger.info(f"Rescheduled post {post_id} to {new_time_rounded}")
    
    return success

