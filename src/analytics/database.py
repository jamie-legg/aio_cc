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

@dataclass
class AIPromptTemplate:
    """AI prompt template record"""
    id: Optional[int] = None
    name: str = ""
    prompt_text: str = ""
    is_active: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class DailySnapshot:
    """Daily aggregated metrics snapshot"""
    id: Optional[int] = None
    snapshot_date: str = ""  # YYYY-MM-DD format
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_videos: int = 0
    youtube_views: int = 0
    instagram_views: int = 0
    tiktok_views: int = 0
    created_at: Optional[datetime] = None

@dataclass
class User:
    """User account record"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    created_at: Optional[datetime] = None
    is_active: bool = True
    role: str = "user"  # user, admin

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
            
            # AI prompt templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_prompt_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    prompt_text TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Daily snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_date TEXT UNIQUE NOT NULL,
                    total_views INTEGER DEFAULT 0,
                    total_likes INTEGER DEFAULT 0,
                    total_comments INTEGER DEFAULT 0,
                    total_shares INTEGER DEFAULT 0,
                    total_videos INTEGER DEFAULT 0,
                    youtube_views INTEGER DEFAULT 0,
                    instagram_views INTEGER DEFAULT 0,
                    tiktok_views INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_date ON daily_snapshots(snapshot_date)")
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    role TEXT DEFAULT 'user'
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_platform ON videos(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_video_id ON video_metrics(video_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_platform ON video_metrics(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_status ON scheduled_posts(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_time ON scheduled_posts(scheduled_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_active ON ai_prompt_templates(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            
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
    
    def get_top_videos_with_metrics(self, limit: int = 10, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get top videos with their latest metrics in a single query"""
        query = """
        SELECT 
            v.id, v.video_id, v.title, v.description, v.platform, 
            v.platform_url, v.created_at,
            COALESCE(m.views, 0) as views,
            COALESCE(m.likes, 0) as likes,
            COALESCE(m.comments, 0) as comments,
            COALESCE(m.shares, 0) as shares
        FROM videos v
        LEFT JOIN (
            SELECT video_id, platform, views, likes, comments, shares
            FROM video_metrics
            WHERE (video_id, platform, collected_at) IN (
                SELECT video_id, platform, MAX(collected_at)
                FROM video_metrics
                GROUP BY video_id, platform
            )
        ) m ON v.video_id = m.video_id AND v.platform = m.platform
        """
        
        params = []
        if platform:
            query += " WHERE v.platform = ?"
            params.append(platform)
        
        query += " ORDER BY COALESCE(m.views, 0) DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    'id': row[0],
                    'video_id': row[1],
                    'title': row[2],
                    'description': row[3],
                    'platform': row[4],
                    'platform_url': row[5],
                    'created_at': row[6],
                    'views': row[7],
                    'likes': row[8],
                    'comments': row[9],
                    'shares': row[10]
                })
            
            return results
    
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
                # Parse datetime strings from SQLite
                scheduled_time = datetime.fromisoformat(row[4]) if row[4] else None
                created_at = datetime.fromisoformat(row[6]) if row[6] else None
                processed_at = datetime.fromisoformat(row[7]) if row[7] else None
                
                posts.append(ScheduledPost(
                    id=row[0], video_path=row[1], metadata_json=row[2], platforms=row[3],
                    scheduled_time=scheduled_time, status=row[5], created_at=created_at,
                    processed_at=processed_at, error_message=row[8], retry_count=row[9]
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
                # Parse datetime strings from SQLite
                scheduled_time = datetime.fromisoformat(row[4]) if row[4] else None
                created_at = datetime.fromisoformat(row[6]) if row[6] else None
                processed_at = datetime.fromisoformat(row[7]) if row[7] else None
                
                posts.append(ScheduledPost(
                    id=row[0], video_path=row[1], metadata_json=row[2], platforms=row[3],
                    scheduled_time=scheduled_time, status=row[5], created_at=created_at,
                    processed_at=processed_at, error_message=row[8], retry_count=row[9]
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
    
    def force_post_now(self, post_id: int) -> bool:
        """Force a scheduled post to post immediately by setting scheduled_time to now"""
        from datetime import datetime
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update scheduled time to now for pending posts
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                UPDATE scheduled_posts 
                SET scheduled_time = ?, status = 'pending'
                WHERE id = ? AND status = 'pending'
            """, (now, post_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_scheduled_post(self, post_id: int) -> Optional[ScheduledPost]:
        """Get a specific scheduled post by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scheduled_posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            
            if row:
                # Parse datetime strings from SQLite
                scheduled_time = datetime.fromisoformat(row[4]) if row[4] else None
                created_at = datetime.fromisoformat(row[6]) if row[6] else None
                processed_at = datetime.fromisoformat(row[7]) if row[7] else None
                
                return ScheduledPost(
                    id=row[0], video_path=row[1], metadata_json=row[2], platforms=row[3],
                    scheduled_time=scheduled_time, status=row[5], created_at=created_at,
                    processed_at=processed_at, error_message=row[8], retry_count=row[9]
                )
            return None
    
    def get_pending_posts(self) -> List[ScheduledPost]:
        """Get all pending scheduled posts"""
        return self.list_scheduled_posts(status="pending", limit=1000)
    
    def get_all_scheduled_posts(self) -> List[ScheduledPost]:
        """Get all scheduled posts regardless of status"""
        return self.list_scheduled_posts(limit=10000)
    
    def get_posts_by_status(self, status: str, limit: int = 100) -> List[ScheduledPost]:
        """Get posts filtered by status"""
        return self.list_scheduled_posts(status=status, limit=limit)
    
    def get_upcoming_schedule(self, hours: int = 24) -> List[ScheduledPost]:
        """Get scheduled posts for next N hours"""
        from datetime import timedelta
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scheduled_posts 
                WHERE scheduled_time >= ? AND scheduled_time <= ?
                AND status IN ('pending', 'processing')
                ORDER BY scheduled_time ASC
            """, (now.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))
            rows = cursor.fetchall()
            
            posts = []
            for row in rows:
                # Parse datetime strings from SQLite
                scheduled_time = datetime.fromisoformat(row[4]) if row[4] else None
                created_at = datetime.fromisoformat(row[6]) if row[6] else None
                processed_at = datetime.fromisoformat(row[7]) if row[7] else None
                
                posts.append(ScheduledPost(
                    id=row[0], video_path=row[1], metadata_json=row[2], platforms=row[3],
                    scheduled_time=scheduled_time, status=row[5], created_at=created_at,
                    processed_at=processed_at, error_message=row[8], retry_count=row[9]
                ))
            
            return posts
    
    def get_completed_posts(self, days: int = 7) -> List[ScheduledPost]:
        """Get completed posts from the last N days"""
        from datetime import timedelta
        now = datetime.now()
        start_time = now - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scheduled_posts 
                WHERE processed_at >= ? AND processed_at <= ?
                AND status = 'completed'
                ORDER BY processed_at DESC
            """, (start_time.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S')))
            rows = cursor.fetchall()
            
            posts = []
            for row in rows:
                # Parse datetime strings from SQLite
                scheduled_time = datetime.fromisoformat(row[4]) if row[4] else None
                created_at = datetime.fromisoformat(row[6]) if row[6] else None
                processed_at = datetime.fromisoformat(row[7]) if row[7] else None
                
                posts.append(ScheduledPost(
                    id=row[0], video_path=row[1], metadata_json=row[2], platforms=row[3],
                    scheduled_time=scheduled_time, status=row[5], created_at=created_at,
                    processed_at=processed_at, error_message=row[8], retry_count=row[9]
                ))
            
            return posts
    
    def has_post_at_time(self, platform: str, scheduled_time: datetime) -> bool:
        """Check if there's already a post scheduled for this platform at this time"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM scheduled_posts 
                WHERE platforms LIKE ? 
                AND scheduled_time = ?
                AND status = 'pending'
            """, (f"%{platform}%", scheduled_time))
            count = cursor.fetchone()[0]
            return count > 0
    
    def reschedule_post(self, post_id: int, new_time: datetime) -> bool:
        """Update the scheduled time for a post"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scheduled_posts 
                SET scheduled_time = ?
                WHERE id = ? AND status = 'pending'
            """, (new_time, post_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_scheduled_post_metadata(self, post_id: int, metadata_json: str, platforms: Optional[str] = None) -> bool:
        """Update metadata for a scheduled post"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if platforms is not None:
                cursor.execute("""
                    UPDATE scheduled_posts 
                    SET metadata_json = ?, platforms = ?
                    WHERE id = ? AND status = 'pending'
                """, (metadata_json, platforms, post_id))
            else:
                cursor.execute("""
                    UPDATE scheduled_posts 
                    SET metadata_json = ?
                    WHERE id = ? AND status = 'pending'
                """, (metadata_json, post_id))
            conn.commit()
            return cursor.rowcount > 0
    
    # AI Prompt Template Methods
    
    def add_prompt_template(self, template: AIPromptTemplate) -> int:
        """Add a new AI prompt template"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ai_prompt_templates (name, prompt_text, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (template.name, template.prompt_text, template.is_active, 
                  template.created_at or datetime.now(), template.updated_at or datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_prompt_template(self, template_id: int) -> Optional[AIPromptTemplate]:
        """Get a specific prompt template by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ai_prompt_templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            
            if row:
                # Parse datetime strings from SQLite
                created_at = datetime.fromisoformat(row[4]) if row[4] else None
                updated_at = datetime.fromisoformat(row[5]) if row[5] else None
                
                return AIPromptTemplate(
                    id=row[0], name=row[1], prompt_text=row[2], is_active=bool(row[3]),
                    created_at=created_at, updated_at=updated_at
                )
            return None
    
    def get_active_prompt_template(self) -> Optional[AIPromptTemplate]:
        """Get the currently active prompt template"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ai_prompt_templates WHERE is_active = 1 LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                # Parse datetime strings from SQLite
                created_at = datetime.fromisoformat(row[4]) if row[4] else None
                updated_at = datetime.fromisoformat(row[5]) if row[5] else None
                
                return AIPromptTemplate(
                    id=row[0], name=row[1], prompt_text=row[2], is_active=bool(row[3]),
                    created_at=created_at, updated_at=updated_at
                )
            return None
    
    def list_prompt_templates(self) -> List[AIPromptTemplate]:
        """List all prompt templates"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ai_prompt_templates ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            templates = []
            for row in rows:
                # Parse datetime strings from SQLite
                created_at = datetime.fromisoformat(row[4]) if row[4] else None
                updated_at = datetime.fromisoformat(row[5]) if row[5] else None
                
                templates.append(AIPromptTemplate(
                    id=row[0], name=row[1], prompt_text=row[2], is_active=bool(row[3]),
                    created_at=created_at, updated_at=updated_at
                ))
            
            return templates
    
    def update_prompt_template(self, template_id: int, name: Optional[str] = None, 
                              prompt_text: Optional[str] = None) -> bool:
        """Update a prompt template"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if prompt_text is not None:
            updates.append("prompt_text = ?")
            params.append(prompt_text)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        params.append(datetime.now())
        params.append(template_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE ai_prompt_templates 
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def activate_prompt_template(self, template_id: int) -> bool:
        """Set a template as active (deactivates all others)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Deactivate all templates
            cursor.execute("UPDATE ai_prompt_templates SET is_active = 0")
            
            # Activate the specified template
            cursor.execute("UPDATE ai_prompt_templates SET is_active = 1 WHERE id = ?", (template_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_prompt_template(self, template_id: int) -> bool:
        """Delete a prompt template"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ai_prompt_templates WHERE id = ?", (template_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # User management methods
    def create_user(self, username: str, email: str, password_hash: str, role: str = "user") -> int:
        """Create a new user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, role, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=row[0], username=row[1], email=row[2], password_hash=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else None,
                    is_active=bool(row[5]), role=row[6]
                )
            return None
    
    def update_user_password(self, user_id: int, password_hash: str) -> bool:
        """Update user password"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (password_hash, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=row[0], username=row[1], email=row[2], password_hash=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else None,
                    is_active=bool(row[5]), role=row[6]
                )
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=row[0], username=row[1], email=row[2], password_hash=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else None,
                    is_active=bool(row[5]), role=row[6]
                )
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user fields"""
        allowed_fields = ['username', 'email', 'password_hash', 'is_active', 'role']
        updates = []
        params = []
        
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(user_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def create_daily_snapshot(self) -> bool:
        """Create a daily snapshot of current metrics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total videos
            cursor.execute("SELECT COUNT(*) FROM videos")
            total_videos = cursor.fetchone()[0]
            
            # Get total metrics across all platforms
            cursor.execute("""
                SELECT 
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares
                FROM video_metrics vm
                JOIN videos v ON vm.video_id = v.video_id
            """)
            metrics_row = cursor.fetchone()
            total_views = metrics_row[0] or 0
            total_likes = metrics_row[1] or 0
            total_comments = metrics_row[2] or 0
            total_shares = metrics_row[3] or 0
            
            # Get platform breakdown
            cursor.execute("""
                SELECT 
                    v.platform,
                    SUM(vm.views) as views
                FROM video_metrics vm
                JOIN videos v ON vm.video_id = v.video_id
                GROUP BY v.platform
            """)
            platform_data = dict(cursor.fetchall())
            
            cursor.execute("""
                INSERT OR REPLACE INTO daily_snapshots 
                (snapshot_date, total_views, total_likes, total_comments, total_shares, 
                 total_videos, youtube_views, instagram_views, tiktok_views)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                today,
                total_views,
                total_likes,
                total_comments,
                total_shares,
                total_videos,
                platform_data.get('youtube', 0),
                platform_data.get('instagram', 0),
                platform_data.get('tiktok', 0)
            ))
            conn.commit()
            return True

    def get_daily_snapshots(self, days: int = 30) -> List[DailySnapshot]:
        """Get daily snapshots for the last N days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_snapshots 
                ORDER BY snapshot_date DESC 
                LIMIT ?
            """, (days,))
            rows = cursor.fetchall()
            
            snapshots = []
            for row in rows:
                snapshots.append(DailySnapshot(
                    id=row[0],
                    snapshot_date=row[1],
                    total_views=row[2],
                    total_likes=row[3],
                    total_comments=row[4],
                    total_shares=row[5],
                    total_videos=row[6],
                    youtube_views=row[7],
                    instagram_views=row[8],
                    tiktok_views=row[9],
                    created_at=datetime.fromisoformat(row[10]) if row[10] else None
                ))
            
            return list(reversed(snapshots))  # Return oldest to newest for charts