"""Background scheduler daemon for automated video posting."""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analytics.database import AnalyticsDatabase
from src.scheduling.scheduler import check_due_posts
from src.managers.oauth_manager import OAuthManager
from src.managers.upload_manager import UploadManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchedulerDaemon:
    """Background daemon for processing scheduled posts."""
    
    def __init__(self, db_path: str = "analytics.db", check_interval: int = 60):
        """
        Initialize the scheduler daemon.
        
        Args:
            db_path: Path to the analytics database
            check_interval: How often to check for due posts (seconds)
        """
        self.db_path = db_path
        self.db = AnalyticsDatabase(db_path)
        self.check_interval = check_interval
        self.running = False
        
        # Initialize upload managers
        self.oauth_manager = OAuthManager()
        self.upload_manager = UploadManager(self.oauth_manager)
        
        logger.info("Scheduler daemon initialized")
    
    def post_video(self, post_id: int, video_path: str, metadata: Dict[str, Any], 
                   platforms: list[str]) -> bool:
        """
        Execute the upload for a scheduled post.
        
        Args:
            post_id: ID of the scheduled post
            video_path: Path to the video file
            metadata: Metadata dictionary with title, description, hashtags
            platforms: List of platforms to post to
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"Posting video {video_path} to {', '.join(platforms)}")
            
            # Update status to processing
            self.db.update_post_status(post_id, "processing")
            
            # Upload to each platform
            results = {}
            errors = []
            
            # Convert video_path to Path object
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                raise Exception(f"Video file not found: {video_path}")
            
            for platform in platforms:
                platform = platform.strip().lower()
                
                try:
                    if not self.oauth_manager.is_authenticated(platform):
                        raise Exception(f"{platform} not authenticated")
                    
                    # Prepare metadata dictionary for upload
                    upload_metadata = {
                        "title": metadata.get("title", ""),
                        "caption": metadata.get("description", ""),
                        "hashtags": metadata.get("hashtags", "")
                    }
                    
                    if platform == "youtube":
                        result = self.upload_manager.upload_to_youtube(video_path_obj, upload_metadata)
                        results[platform] = result
                        logger.info(f"✅ Uploaded to YouTube: {result.url if result.success else result.error}")
                    
                    elif platform == "instagram":
                        result = self.upload_manager.upload_to_instagram(video_path_obj, upload_metadata)
                        results[platform] = result
                        logger.info(f"✅ Uploaded to Instagram: {result.url if result.success else result.error}")
                    
                    elif platform == "tiktok":
                        result = self.upload_manager.upload_to_tiktok(video_path_obj, upload_metadata)
                        results[platform] = result
                        logger.info(f"✅ Uploaded to TikTok: {result.url if result.success else result.error}")
                    
                    else:
                        logger.warning(f"Unknown platform: {platform}")
                        continue
                    
                    # Track errors
                    if not result.success:
                        errors.append(f"{platform}: {result.error}")
                
                except Exception as e:
                    error_msg = f"Failed to upload to {platform}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Update status based on results
            if errors:
                if len(errors) == len(platforms):
                    # All failed
                    self.db.update_post_status(
                        post_id, "failed", 
                        error_message="; ".join(errors),
                        increment_retry=True
                    )
                    return False
                else:
                    # Partial success
                    self.db.update_post_status(
                        post_id, "completed", 
                        error_message=f"Partial: {'; '.join(errors)}"
                    )
            else:
                # All successful
                self.db.update_post_status(post_id, "completed", processed_at=datetime.now())
            
            logger.info(f"✅ Successfully posted {video_path}")
            return True
        
        except Exception as e:
            error_msg = f"Error posting video: {str(e)}"
            logger.error(error_msg)
            self.db.update_post_status(
                post_id, "failed", 
                error_message=error_msg,
                increment_retry=True
            )
            return False
    
    def process_due_posts(self):
        """Check for and process all due posts."""
        try:
            due_posts = check_due_posts(self.db_path)
            
            if not due_posts:
                logger.debug("No due posts found")
                return
            
            logger.info(f"Found {len(due_posts)} due posts to process")
            
            for post in due_posts:
                # Check retry limit
                if post.retry_count >= 3:
                    logger.warning(f"Post {post.id} has reached max retries, skipping")
                    self.db.update_post_status(post.id, "failed", 
                                                error_message="Max retries exceeded")
                    continue
                
                # Parse metadata
                try:
                    metadata = json.loads(post.metadata_json)
                except json.JSONDecodeError:
                    logger.error(f"Invalid metadata JSON for post {post.id}")
                    self.db.update_post_status(post.id, "failed", 
                                                error_message="Invalid metadata JSON")
                    continue
                
                # Parse platforms
                platforms = [p.strip() for p in post.platforms.split(',')]
                
                # Post the video
                self.post_video(post.id, post.video_path, metadata, platforms)
        
        except Exception as e:
            logger.error(f"Error processing due posts: {e}")
    
    def run(self):
        """Start the daemon main loop."""
        self.running = True
        logger.info(f"Scheduler daemon started (checking every {self.check_interval}s)")
        
        try:
            while self.running:
                self.process_due_posts()
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
    
    def stop(self):
        """Stop the daemon."""
        self.running = False
        logger.info("Scheduler daemon stopped")


def main():
    """Main entry point for the scheduler daemon."""
    print("=" * 60)
    print("SCHEDULER DAEMON - AUTOMATED VIDEO POSTING")
    print("=" * 60)
    print()
    print("This service monitors scheduled posts and uploads them")
    print("automatically when their scheduled time arrives.")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    daemon = SchedulerDaemon(check_interval=60)  # Check every minute
    daemon.run()


if __name__ == "__main__":
    main()

