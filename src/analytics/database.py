"""Database models and schema for analytics tracking"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class VideoRecord:
    """Video record in the analytics database"""
    id: Optional[int] = None
    video_id: str = ""
    title: str = ""
    description: str = ""
    prompt: str = ""
    platform: str = ""  # youtube, instagram, tiktok, etc.
    platform_video_id: str = ""  # ID on the platform
    platform_url: str = ""
    duration: float = 0.0
    file_path: str = ""
    created_at: Optional[datetime] = None
    uploaded_at: Optional[datetime] = None
    status: str = "created"  # created, processing, uploaded, published, error

@dataclass
class VideoMetrics:
    """Video metrics for analytics"""
    id: Optional[int] = None
    video_id: str = ""
    platform: str = ""
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    collected_at: Optional[datetime] = None

@dataclass
class ScheduledPost:
    """Scheduled post record"""
    id: Optional[int] = None
    video_path: str = ""
    metadata_json: str = ""  # JSON string with title, caption, hashtags
    platforms: str = ""  # Comma-separated list
    scheduled_time: Optional[datetime] = None
    status: str = "pending"  # pending, processing, completed, failed, cancelled
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    error_message: str = ""
    retry_count: int = 0

class AnalyticsDatabase:
    """SQLite database manager for analytics"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Videos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    prompt TEXT,
                    platform TEXT NOT NULL,
                    platform_video_id TEXT,
                    platform_url TEXT,
                    duration REAL DEFAULT 0.0,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_at TIMESTAMP,
                    status TEXT DEFAULT 'created'
                )
            """)
            
            # Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS video_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos (video_id)
                )
            """)
            
            # Scheduled posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_path TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    platforms TEXT NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_platform ON videos(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_video_id ON video_metrics(video_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_platform ON video_metrics(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_status ON scheduled_posts(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_time ON scheduled_posts(scheduled_time)")
            
            conn.commit()
    
    def add_video(self, video: VideoRecord) -> int:
        """Add a new video record to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO videos (
                    video_id, title, description, prompt, platform,
                    platform_video_id, platform_url, duration, file_path,
                    created_at, uploaded_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video.video_id, video.title, video.description, video.prompt,
                video.platform, video.platform_video_id, video.platform_url,
                video.duration, video.file_path, video.created_at, video.uploaded_at, video.status
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_video(self, video_id: str, updates: Dict[str, Any]) -> bool:
        """Update a video record"""
        if not updates:
            return False
        
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key in ['title', 'description', 'prompt', 'platform', 'platform_video_id', 
                      'platform_url', 'duration', 'file_path', 'uploaded_at', 'status']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return False
        
        values.append(video_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE videos 
                SET {', '.join(set_clauses)}
                WHERE video_id = ?
            """, values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_video(self, video_id: str) -> Optional[VideoRecord]:
        """Get a video record by video_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
            row = cursor.fetchone()
            
            if row:
                return VideoRecord(
                    id=row[0], video_id=row[1], title=row[2], description=row[3],
                    prompt=row[4], platform=row[5], platform_video_id=row[6],
                    platform_url=row[7], duration=row[8], file_path=row[9],
                    created_at=row[10], uploaded_at=row[11], status=row[12]
                )
            return None
    
    def list_videos(self, platform: Optional[str] = None, status: Optional[str] = None, 
                   limit: int = 100, offset: int = 0) -> List[VideoRecord]:
        """List videos with optional filtering"""
        query = "SELECT * FROM videos WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            videos = []
            for row in rows:
                videos.append(VideoRecord(
                    id=row[0], video_id=row[1], title=row[2], description=row[3],
                    prompt=row[4], platform=row[5], platform_video_id=row[6],
                    platform_url=row[7], duration=row[8], file_path=row[9],
                    created_at=row[10], uploaded_at=row[11], status=row[12]
                ))
            
            return videos
    
    def add_metrics(self, metrics: VideoMetrics) -> int:
        """Add video metrics to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO video_metrics (
                    video_id, platform, views, likes, shares, comments,
                    engagement_rate, collected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.video_id, metrics.platform, metrics.views, metrics.likes,
                metrics.shares, metrics.comments, metrics.engagement_rate, metrics.collected_at
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_latest_metrics(self, video_id: str, platform: Optional[str] = None) -> Optional[VideoMetrics]:
        """Get the latest metrics for a video"""
        query = "SELECT * FROM video_metrics WHERE video_id = ?"
        params = [video_id]
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        query += " ORDER BY collected_at DESC LIMIT 1"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return VideoMetrics(
                    id=row[0], video_id=row[1], platform=row[2], views=row[3],
                    likes=row[4], shares=row[5], comments=row[6], engagement_rate=row[7],
                    collected_at=row[8]
                )
            return None
    
    def get_metrics_history(self, video_id: str, platform: Optional[str] = None, 
                           limit: int = 30) -> List[VideoMetrics]:
        """Get metrics history for a video"""
        query = "SELECT * FROM video_metrics WHERE video_id = ?"
        params = [video_id]
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        query += " ORDER BY collected_at DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            metrics = []
            for row in rows:
                metrics.append(VideoMetrics(
                    id=row[0], video_id=row[1], platform=row[2], views=row[3],
                    likes=row[4], shares=row[5], comments=row[6], engagement_rate=row[7],
                    collected_at=row[8]
                ))
            
            return metrics
    
    def get_analytics_summary(self, platform: Optional[str] = None, 
                            days: int = 30) -> Dict[str, Any]:
        """Get analytics summary for the specified period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Base query for date filtering
            date_filter = f"AND v.created_at >= datetime('now', '-{days} days')"
            
            # Total videos
            cursor.execute(f"""
                SELECT COUNT(*) FROM videos v 
                WHERE 1=1 {date_filter if not platform else "AND v.platform = ? " + date_filter}
            """, [platform] if platform else [])
            total_videos = cursor.fetchone()[0]
            
            # Videos by status
            cursor.execute(f"""
                SELECT status, COUNT(*) FROM videos v 
                WHERE 1=1 {date_filter if not platform else "AND v.platform = ? " + date_filter}
                GROUP BY status
            """, [platform] if platform else [])
            status_counts = dict(cursor.fetchall())
            
            # Average metrics
            cursor.execute(f"""
                SELECT 
                    AVG(m.views) as avg_views,
                    AVG(m.likes) as avg_likes,
                    AVG(m.shares) as avg_shares,
                    AVG(m.comments) as avg_comments,
                    AVG(m.engagement_rate) as avg_engagement
                FROM video_metrics m
                JOIN videos v ON m.video_id = v.video_id
                WHERE 1=1 {date_filter if not platform else "AND v.platform = ? " + date_filter}
            """, [platform] if platform else [])
            
            avg_row = cursor.fetchone()
            avg_metrics = {
                'avg_views': avg_row[0] or 0,
                'avg_likes': avg_row[1] or 0,
                'avg_shares': avg_row[2] or 0,
                'avg_comments': avg_row[3] or 0,
                'avg_engagement': avg_row[4] or 0
            }
            
            return {
                'total_videos': total_videos,
                'status_counts': status_counts,
                'avg_metrics': avg_metrics,
                'period_days': days,
                'platform': platform or 'all'
            }
    
    def reset_platform_data(self, platform: str) -> bool:
        """Reset all data for a specific platform."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete videos for the platform
                cursor.execute("DELETE FROM videos WHERE platform = ?", (platform,))
                videos_deleted = cursor.rowcount
                
                # Delete metrics for the platform
                cursor.execute("DELETE FROM video_metrics WHERE platform = ?", (platform,))
                metrics_deleted = cursor.rowcount
                
                conn.commit()
                
                print(f"[SUCCESS] Reset {platform.upper()} data: {videos_deleted} videos, {metrics_deleted} metrics")
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to reset {platform.upper()} data: {e}")
            return False
    
    # Scheduled Posts Methods
    
    def add_scheduled_post(self, post: ScheduledPost) -> int:
        """Add a new scheduled post to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scheduled_posts (
                    video_path, metadata_json, platforms, scheduled_time,
                    status, created_at, processed_at, error_message, retry_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.video_path, post.metadata_json, post.platforms, post.scheduled_time,
                post.status, post.created_at, post.processed_at, post.error_message, post.retry_count
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_pending_posts(self, grace_period_minutes: int = 60) -> List[ScheduledPost]:
        """Get posts that are ready to upload (scheduled_time <= now and status = pending)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get posts that are due (including those missed during downtime)
            cursor.execute("""
                SELECT * FROM scheduled_posts 
                WHERE status = 'pending' 
                AND scheduled_time <= datetime('now')
                AND scheduled_time >= datetime('now', '-' || ? || ' minutes')
                ORDER BY scheduled_time ASC
            """, (grace_period_minutes,))
            
            rows = cursor.fetchall()
            posts = []
            for row in rows:
                posts.append(ScheduledPost(
                    id=row[0], video_path=row[1], metadata_json=row[2], platforms=row[3],
                    scheduled_time=row[4], status=row[5], created_at=row[6],
                    processed_at=row[7], error_message=row[8], retry_count=row[9]
                ))
            
            return posts
    
    def update_post_status(self, post_id: int, status: str, error_message: str = "", 
                          processed_at: Optional[datetime] = None, increment_retry: bool = False) -> bool:
        """Update the status of a scheduled post"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if increment_retry:
                cursor.execute("""
                    UPDATE scheduled_posts 
                    SET status = ?, error_message = ?, processed_at = ?, retry_count = retry_count + 1
                    WHERE id = ?
                """, (status, error_message, processed_at, post_id))
            else:
                cursor.execute("""
                    UPDATE scheduled_posts 
                    SET status = ?, error_message = ?, processed_at = ?
                    WHERE id = ?
                """, (status, error_message, processed_at, post_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def list_scheduled_posts(self, status: Optional[str] = None, platform: Optional[str] = None,
                           limit: int = 100, offset: int = 0) -> List[ScheduledPost]:
        """List scheduled posts with optional filtering"""
        query = "SELECT * FROM scheduled_posts WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if platform:
            query += " AND platforms LIKE ?"
            params.append(f"%{platform}%")
        
        query += " ORDER BY scheduled_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            posts = []
            for row in rows:
                posts.append(ScheduledPost(
                    id=row[0], video_path=row[1], metadata_json=row[2], platforms=row[3],
                    scheduled_time=row[4], status=row[5], created_at=row[6],
                    processed_at=row[7], error_message=row[8], retry_count=row[9]
                ))
            
            return posts
    
    def cancel_scheduled_post(self, post_id: int) -> bool:
        """Mark a scheduled post as cancelled"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Only allow cancelling pending posts
            cursor.execute("""
                UPDATE scheduled_posts 
                SET status = 'cancelled', processed_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'pending'
            """, (post_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_scheduled_post(self, post_id: int) -> Optional[ScheduledPost]:
        """Get a specific scheduled post by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scheduled_posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            
            if row:
                return ScheduledPost(
                    id=row[0], video_path=row[1], metadata_json=row[2], platforms=row[3],
                    scheduled_time=row[4], status=row[5], created_at=row[6],
                    processed_at=row[7], error_message=row[8], retry_count=row[9]
                )
            return None