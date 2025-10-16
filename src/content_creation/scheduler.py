"""Post scheduler service for automated video uploads."""

import time
import json
import signal
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from analytics.database import AnalyticsDatabase, ScheduledPost
from managers.oauth_manager import OAuthManager
from managers.upload_manager import UploadManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PostScheduler')


class PostScheduler:
    """Scheduler service for automated video uploads at scheduled times."""
    
    def __init__(self, db_path: str = "analytics.db", 
                 check_interval: int = 60,
                 grace_period_minutes: int = 60,
                 max_retries: int = 3):
        """
        Initialize the post scheduler.
        
        Args:
            db_path: Path to analytics database
            check_interval: How often to check for pending posts (seconds)
            grace_period_minutes: How old can a missed post be before we skip it
            max_retries: Maximum retry attempts for failed uploads
        """
        self.db = AnalyticsDatabase(db_path)
        self.check_interval = check_interval
        self.grace_period_minutes = grace_period_minutes
        self.max_retries = max_retries
        self.running = False
        
        # Initialize upload manager
        self.oauth_manager = OAuthManager()
        self.upload_manager = UploadManager(self.oauth_manager)
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"PostScheduler initialized (check_interval={check_interval}s, grace_period={grace_period_minutes}m)")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def run(self, once: bool = False):
        """
        Start the scheduler service.
        
        Args:
            once: If True, process pending posts once and exit (useful for cron)
        """
        self.running = True
        logger.info("Scheduler started")
        
        if once:
            logger.info("Running in single-pass mode")
            self._process_pending_posts()
            logger.info("Single-pass complete, exiting")
            return
        
        # Main loop
        while self.running:
            try:
                self._process_pending_posts()
                
                if self.running:
                    logger.debug(f"Sleeping for {self.check_interval} seconds...")
                    time.sleep(self.check_interval)
                    
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                # Continue running even if there's an error
                time.sleep(self.check_interval)
        
        logger.info("Scheduler stopped")
    
    def _process_pending_posts(self):
        """Check for and process pending posts."""
        try:
            # Get posts that are ready to upload
            pending_posts = self.db.get_pending_posts(self.grace_period_minutes)
            
            if not pending_posts:
                logger.debug("No pending posts found")
                return
            
            logger.info(f"Found {len(pending_posts)} pending post(s)")
            
            for post in pending_posts:
                if not self.running:
                    logger.info("Scheduler stopped, aborting post processing")
                    break
                
                self._process_post(post)
                
        except Exception as e:
            logger.error(f"Error processing pending posts: {e}", exc_info=True)
    
    def _process_post(self, post: ScheduledPost):
        """Process a single scheduled post."""
        try:
            logger.info(f"Processing post {post.id} - {Path(post.video_path).name}")
            
            # Check if video file exists
            video_path = Path(post.video_path)
            if not video_path.exists():
                error_msg = f"Video file not found: {post.video_path}"
                logger.error(f"Post {post.id}: {error_msg}")
                self.db.update_post_status(
                    post.id, 
                    'failed', 
                    error_msg,
                    datetime.now()
                )
                return
            
            # Check if post was missed (scheduled time is in the past)
            scheduled_time = datetime.fromisoformat(post.scheduled_time) if isinstance(post.scheduled_time, str) else post.scheduled_time
            now = datetime.now()
            
            if scheduled_time < now:
                time_diff = now - scheduled_time
                logger.warning(f"Post {post.id} is {time_diff} late (scheduled for {scheduled_time})")
                
                # Check if it's too old
                if time_diff > timedelta(minutes=self.grace_period_minutes):
                    error_msg = f"Post missed by {time_diff}, exceeds grace period of {self.grace_period_minutes} minutes"
                    logger.error(f"Post {post.id}: {error_msg}")
                    self.db.update_post_status(
                        post.id,
                        'failed',
                        error_msg,
                        datetime.now()
                    )
                    return
            
            # Parse metadata
            try:
                metadata = json.loads(post.metadata_json)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid metadata JSON: {e}"
                logger.error(f"Post {post.id}: {error_msg}")
                self.db.update_post_status(
                    post.id,
                    'failed',
                    error_msg,
                    datetime.now()
                )
                return
            
            # Parse platforms
            platforms = [p.strip() for p in post.platforms.split(',')]
            logger.info(f"Post {post.id}: Uploading to platforms: {platforms}")
            
            # Update status to processing
            self.db.update_post_status(post.id, 'processing', '')
            
            # Upload to platforms
            results = self.upload_manager.upload_to_all_platforms(
                video_path,
                metadata,
                platforms
            )
            
            # Check results
            successful_platforms = []
            failed_platforms = []
            errors = []
            
            for platform, result in results.items():
                if result.success:
                    successful_platforms.append(platform)
                    logger.info(f"Post {post.id}: {platform} upload succeeded - {result.video_id}")
                else:
                    failed_platforms.append(platform)
                    errors.append(f"{platform}: {result.error}")
                    logger.error(f"Post {post.id}: {platform} upload failed - {result.error}")
            
            # Determine final status
            if successful_platforms and not failed_platforms:
                # All succeeded
                logger.info(f"Post {post.id}: All uploads completed successfully")
                self.db.update_post_status(
                    post.id,
                    'completed',
                    '',
                    datetime.now()
                )
            elif successful_platforms and failed_platforms:
                # Partial success
                error_msg = f"Partial success. Failed: {', '.join(errors)}"
                logger.warning(f"Post {post.id}: {error_msg}")
                self.db.update_post_status(
                    post.id,
                    'completed',
                    error_msg,
                    datetime.now()
                )
            else:
                # All failed - check if we should retry
                error_msg = f"All uploads failed. Errors: {', '.join(errors)}"
                
                if post.retry_count < self.max_retries:
                    logger.warning(f"Post {post.id}: {error_msg}. Retry {post.retry_count + 1}/{self.max_retries}")
                    self.db.update_post_status(
                        post.id,
                        'pending',  # Reset to pending for retry
                        error_msg,
                        None,
                        increment_retry=True
                    )
                else:
                    logger.error(f"Post {post.id}: {error_msg}. Max retries exceeded.")
                    self.db.update_post_status(
                        post.id,
                        'failed',
                        f"{error_msg}. Max retries ({self.max_retries}) exceeded.",
                        datetime.now()
                    )
                    
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Post {post.id}: {error_msg}", exc_info=True)
            
            # Retry logic for unexpected errors
            if post.retry_count < self.max_retries:
                self.db.update_post_status(
                    post.id,
                    'pending',
                    error_msg,
                    None,
                    increment_retry=True
                )
            else:
                self.db.update_post_status(
                    post.id,
                    'failed',
                    f"{error_msg}. Max retries exceeded.",
                    datetime.now()
                )
    
    def get_status(self) -> Dict:
        """Get scheduler status and statistics."""
        try:
            # Count posts by status
            pending = len(self.db.list_scheduled_posts(status='pending', limit=1000))
            processing = len(self.db.list_scheduled_posts(status='processing', limit=1000))
            completed = len(self.db.list_scheduled_posts(status='completed', limit=1000))
            failed = len(self.db.list_scheduled_posts(status='failed', limit=1000))
            
            # Get upcoming posts
            upcoming = self.db.list_scheduled_posts(status='pending', limit=5)
            
            # Get recent activity
            recent = self.db.list_scheduled_posts(limit=5)
            
            return {
                'running': self.running,
                'stats': {
                    'pending': pending,
                    'processing': processing,
                    'completed': completed,
                    'failed': failed
                },
                'upcoming': upcoming,
                'recent': recent
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}", exc_info=True)
            return {
                'error': str(e)
            }



