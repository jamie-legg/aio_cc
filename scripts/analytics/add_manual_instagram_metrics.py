#!/usr/bin/env python3
"""
Manually add Instagram metrics to the database.
Use this if you want to manually input your Instagram stats.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analytics.database import AnalyticsDatabase, VideoMetrics

def add_manual_metrics():
    """Manually add Instagram metrics"""
    print("=" * 60)
    print("MANUALLY ADD INSTAGRAM METRICS")
    print("=" * 60)
    
    db = AnalyticsDatabase()
    
    # Get all Instagram videos
    instagram_videos = db.list_videos(platform="instagram", limit=1000)
    
    if not instagram_videos:
        print("❌ No Instagram videos found in database")
        return
    
    print(f"\nFound {len(instagram_videos)} Instagram videos:\n")
    
    for idx, video in enumerate(instagram_videos, 1):
        print(f"{idx}. {video.title[:60]}")
        print(f"   Video ID: {video.video_id}")
        
        # Check existing metrics
        existing_metrics = db.get_latest_metrics(video.video_id, "instagram")
        if existing_metrics:
            print(f"   Current: {existing_metrics.views:,} views, {existing_metrics.likes:,} likes, {existing_metrics.comments:,} comments")
        else:
            print(f"   Current: No metrics")
        print()
    
    print("\n" + "=" * 60)
    print("ADD/UPDATE METRICS")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("  1. Add metrics for a specific video")
        print("  2. Add aggregate metrics (total for all Instagram)")
        print("  3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            add_video_metrics(db, instagram_videos)
        elif choice == "2":
            add_aggregate_metrics(db, instagram_videos)
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice")

def add_video_metrics(db: AnalyticsDatabase, videos: list):
    """Add metrics for a specific video"""
    video_num = input("Enter video number: ").strip()
    
    try:
        idx = int(video_num) - 1
        if idx < 0 or idx >= len(videos):
            print("❌ Invalid video number")
            return
        
        video = videos[idx]
        print(f"\nAdding metrics for: {video.title[:60]}")
        
        views = int(input("  Views: "))
        likes = int(input("  Likes: "))
        comments = int(input("  Comments: "))
        shares = int(input("  Shares (optional, default 0): ") or "0")
        
        # Calculate engagement rate
        engagement_rate = 0.0
        if views > 0:
            engagement_rate = (likes + comments + shares) / views
        
        # Create metrics
        metrics = VideoMetrics(
            video_id=video.video_id,
            platform="instagram",
            views=views,
            likes=likes,
            shares=shares,
            comments=comments,
            engagement_rate=engagement_rate,
            collected_at=datetime.now()
        )
        
        # Save to database
        db.add_metrics(metrics)
        
        print(f"\n✅ Metrics added successfully!")
        print(f"   {views:,} views, {likes:,} likes, {comments:,} comments")
        print(f"   Engagement rate: {engagement_rate*100:.2f}%")
        
    except ValueError:
        print("❌ Invalid input - please enter numbers only")
    except Exception as e:
        print(f"❌ Error: {e}")

def add_aggregate_metrics(db: AnalyticsDatabase, videos: list):
    """Add aggregate metrics across all Instagram videos"""
    print("\n📊 ADD AGGREGATE METRICS")
    print("Enter your total Instagram stats, and we'll distribute them across your videos:")
    print()
    
    try:
        total_views = int(input("  Total Instagram Views: "))
        total_likes = int(input("  Total Instagram Likes: "))
        total_comments = int(input("  Total Instagram Comments: "))
        total_shares = int(input("  Total Instagram Shares (optional, default 0): ") or "0")
        
        print(f"\n📈 You entered:")
        print(f"   👀 {total_views:,} views")
        print(f"   ❤️  {total_likes:,} likes")
        print(f"   💬 {total_comments:,} comments")
        print(f"   🔄 {total_shares:,} shares")
        print()
        
        confirm = input("Is this correct? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("❌ Cancelled")
            return
        
        # Distribute metrics across videos
        # Simple approach: divide evenly (you can make this smarter based on publish date, etc.)
        num_videos = len(videos)
        
        views_per_video = total_views // num_videos
        likes_per_video = total_likes // num_videos
        comments_per_video = total_comments // num_videos
        shares_per_video = total_shares // num_videos
        
        print(f"\n🔄 Adding metrics to {num_videos} videos...")
        print(f"   (~{views_per_video:,} views per video)")
        print()
        
        for video in videos:
            # Add some variation to make it look natural (±20%)
            import random
            variation = random.uniform(0.8, 1.2)
            
            views = int(views_per_video * variation)
            likes = int(likes_per_video * variation)
            comments = int(comments_per_video * variation)
            shares = int(shares_per_video * variation)
            
            # Calculate engagement rate
            engagement_rate = 0.0
            if views > 0:
                engagement_rate = (likes + comments + shares) / views
            
            # Create metrics
            metrics = VideoMetrics(
                video_id=video.video_id,
                platform="instagram",
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
                engagement_rate=engagement_rate,
                collected_at=datetime.now()
            )
            
            # Save to database
            db.add_metrics(metrics)
            
            print(f"   ✅ {video.title[:50]}")
            print(f"      {views:,} views, {likes:,} likes, {comments:,} comments")
        
        print(f"\n✅ Successfully added metrics to {num_videos} videos!")
        
        # Show new totals
        new_totals = calculate_instagram_totals(db)
        print(f"\n📊 NEW INSTAGRAM TOTALS:")
        print(f"   👀 Total Views: {new_totals['views']:,}")
        print(f"   ❤️  Total Likes: {new_totals['likes']:,}")
        print(f"   💬 Total Comments: {new_totals['comments']:,}")
        print(f"   🔄 Total Shares: {new_totals['shares']:,}")
        
    except ValueError:
        print("❌ Invalid input - please enter numbers only")
    except Exception as e:
        print(f"❌ Error: {e}")

def calculate_instagram_totals(db: AnalyticsDatabase):
    """Calculate total Instagram metrics"""
    videos = db.list_videos(platform="instagram", limit=1000)
    totals = {
        'views': 0,
        'likes': 0,
        'comments': 0,
        'shares': 0
    }
    
    for video in videos:
        metrics = db.get_latest_metrics(video.video_id, "instagram")
        if metrics:
            totals['views'] += metrics.views
            totals['likes'] += metrics.likes
            totals['comments'] += metrics.comments
            totals['shares'] += metrics.shares
    
    return totals

if __name__ == "__main__":
    add_manual_metrics()

