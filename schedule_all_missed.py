#!/usr/bin/env python3
"""Schedule all missed replays found in watch directory"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from managers.config_manager import ConfigManager
from managers.ai_manager import AIManager
from content_creation.video_processor import VideoProcessor
from content_creation.clip_watcher import process_video_for_scheduling
from scheduling.scheduler import space_videos
from analytics.database import AnalyticsDatabase, ScheduledPost
from datetime import datetime
import json

def get_missed_replays():
    """Find videos in watch dir not in processed or scheduled"""
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
        scheduled_paths.add(post.video_path)
        scheduled_paths.add(Path(post.video_path).name)
    
    processed_names = {f.name for f in processed_dir.iterdir() if f.is_file()}
    
    # Filter unprocessed
    missed = []
    for video in watch_videos:
        if video.name not in processed_names and video.name not in scheduled_paths and str(video) not in scheduled_paths:
            missed.append(video)
    
    # Sort by modified time (oldest first for scheduling)
    missed.sort(key=lambda x: x.stat().st_mtime)
    
    return missed

def main():
    print("\n" + "="*60)
    print("SCHEDULE ALL MISSED REPLAYS")
    print("="*60)
    
    # Find missed replays
    missed_replays = get_missed_replays()
    
    if not missed_replays:
        print("\nNo missed replays found!")
        return
    
    print(f"\nFound {len(missed_replays)} missed replays")
    print("\nVideos to schedule:")
    for i, video in enumerate(missed_replays, 1):
        print(f"  {i}. {video.name}")
    
    print(f"\nScheduling {len(missed_replays)} videos (1 hour apart)...")
    
    # Initialize managers
    config_manager = ConfigManager()
    ai_manager = AIManager()
    video_processor = VideoProcessor()
    
    # Get platforms
    platforms = config_manager.get_upload_platforms()
    if not platforms:
        print("\n[ERROR] No platforms enabled for upload!")
        return
    
    print(f"\nTarget platforms: {', '.join(platforms)}")
    
    # Get scheduled times (spaced 1 hour apart)
    db = AnalyticsDatabase()
    scheduled_times = space_videos(platforms, len(missed_replays))
    
    print(f"\nProcessing and scheduling {len(missed_replays)} videos...")
    print("="*60)
    
    successful = 0
    failed = 0
    
    for i, video_path in enumerate(missed_replays):
        print(f"\n[{i+1}/{len(missed_replays)}] {video_path.name}")
        try:
            # Process the video
            processed_path, metadata = process_video_for_scheduling(
                video_path, ai_manager, video_processor, config_manager
            )
            
            # Create scheduled post
            post = ScheduledPost(
                video_path=str(processed_path),
                metadata_json=json.dumps(metadata),
                platforms=",".join(platforms),
                scheduled_time=scheduled_times[i],
                status="pending",
                created_at=datetime.now()
            )
            
            post_id = db.add_scheduled_post(post)
            
            print(f"[SCHEDULED] Post #{post_id} at {scheduled_times[i].strftime('%I:%M %p on %b %d')}")
            successful += 1
            
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total: {len(missed_replays)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print("\nScheduled posts will be uploaded by the scheduler daemon.")
    print("View them in the dashboard at http://localhost:5173/dashboard/uploads")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

