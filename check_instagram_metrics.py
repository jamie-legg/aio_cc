#!/usr/bin/env python3
"""
Simple Instagram metrics checker and updater.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analytics.database import AnalyticsDatabase

def check_instagram_metrics():
    """Check current Instagram metrics"""
    print("=" * 60)
    print("INSTAGRAM METRICS CHECKER")
    print("=" * 60)
    print()
    
    db = AnalyticsDatabase()
    
    # Get Instagram videos
    instagram_videos = db.list_videos(platform="instagram", limit=100)
    
    if not instagram_videos:
        print("[ERROR] No Instagram videos found in database")
        return
    
    print(f"[VIDEOS] Found {len(instagram_videos)} Instagram videos")
    print()
    
    # Calculate current totals
    total_views = 0
    total_likes = 0
    total_comments = 0
    
    print("[METRICS] Current metrics per video:")
    for i, video in enumerate(instagram_videos[:10]):  # Show first 10
        latest_metrics = db.get_latest_metrics(video.video_id, "instagram")
        if latest_metrics:
            views = latest_metrics.views
            likes = latest_metrics.likes
            comments = latest_metrics.comments
            
            total_views += views
            total_likes += likes
            total_comments += comments
            
            print(f"{i+1:2d}. {video.title[:40]:<40} | {views:>8,} views | {likes:>6,} likes | {comments:>4,} comments")
        else:
            print(f"{i+1:2d}. {video.title[:40]:<40} | No metrics")
    
    if len(instagram_videos) > 10:
        print(f"... and {len(instagram_videos) - 10} more videos")
    
    print()
    print("[TOTALS] CURRENT TOTALS:")
    print(f"   Total Views: {total_views:,}")
    print(f"   Total Likes: {total_likes:,}")
    print(f"   Total Comments: {total_comments:,}")
    
    if total_views > 0:
        engagement_rate = (total_likes + total_comments) / total_views * 100
        print(f"   Engagement Rate: {engagement_rate:.2f}%")
    
    print()
    print("[INFO] To update metrics:")
    print("1. Use the refresh button in the dashboard (requires access tokens)")
    print("2. Run: uv run python scripts/analytics/collect_instagram_metrics.py")
    print("3. Set up Instagram access token with: uv run python get_instagram_token.py")

if __name__ == "__main__":
    load_dotenv()
    check_instagram_metrics()








