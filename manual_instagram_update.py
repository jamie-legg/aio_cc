#!/usr/bin/env python3
"""
Manual Instagram metrics update script.
This allows you to manually update Instagram metrics if you have the data.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analytics.database import AnalyticsDatabase
from analytics.metrics_collector import VideoMetrics
from datetime import datetime

def manual_instagram_update():
    """Manually update Instagram metrics"""
    print("=" * 60)
    print("MANUAL INSTAGRAM METRICS UPDATE")
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
    
    # Show current totals
    current_totals = calculate_current_totals(db, instagram_videos)
    print("[TOTALS] CURRENT TOTALS:")
    print(f"   Views: {current_totals['views']:,}")
    print(f"   Likes: {current_totals['likes']:,}")
    print(f"   Comments: {current_totals['comments']:,}")
    print()
    
    print("[OPTIONS] MANUAL UPDATE OPTIONS:")
    print("1. Update specific video metrics")
    print("2. Add bulk metrics update")
    print("3. Set total views (will distribute across videos)")
    print()
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        update_specific_video(db, instagram_videos)
    elif choice == "2":
        bulk_update_metrics(db, instagram_videos)
    elif choice == "3":
        set_total_views(db, instagram_videos)
    else:
        print("[ERROR] Invalid choice")

def calculate_current_totals(db, videos):
    """Calculate current totals from database"""
    total_views = 0
    total_likes = 0
    total_comments = 0
    
    for video in videos:
        latest_metrics = db.get_latest_metrics(video.video_id, "instagram")
        if latest_metrics:
            total_views += latest_metrics.views
            total_likes += latest_metrics.likes
            total_comments += latest_metrics.comments
    
    return {
        'views': total_views,
        'likes': total_likes,
        'comments': total_comments
    }

def update_specific_video(db, videos):
    """Update metrics for a specific video"""
    print("\n📹 Select video to update:")
    for i, video in enumerate(videos[:10]):  # Show first 10
        latest_metrics = db.get_latest_metrics(video.video_id, "instagram")
        current_views = latest_metrics.views if latest_metrics else 0
        print(f"{i+1}. {video.title[:50]}... (Current: {current_views:,} views)")
    
    if len(videos) > 10:
        print(f"... and {len(videos) - 10} more")
    
    try:
        choice = int(input("\nEnter video number: ")) - 1
        if 0 <= choice < len(videos):
            video = videos[choice]
            update_video_metrics(db, video)
        else:
            print("❌ Invalid video number")
    except ValueError:
        print("❌ Invalid input")

def update_video_metrics(db, video):
    """Update metrics for a single video"""
    print(f"\n📊 Updating: {video.title}")
    
    try:
        views = int(input("Enter new view count: "))
        likes = int(input("Enter new like count: "))
        comments = int(input("Enter new comment count: "))
        
        metrics = VideoMetrics(
            video_id=video.video_id,
            platform="instagram",
            views=views,
            likes=likes,
            shares=0,  # Instagram doesn't provide shares
            comments=comments,
            engagement_rate=(likes + comments) / views if views > 0 else 0,
            collected_at=datetime.now()
        )
        
        db.add_metrics(metrics)
        print("✅ Metrics updated successfully!")
        
    except ValueError:
        print("❌ Invalid input - please enter numbers only")

def bulk_update_metrics(db, videos):
    """Bulk update metrics for multiple videos"""
    print("\n📊 BULK UPDATE")
    print("Enter new metrics for each video (press Enter to skip):")
    
    updated_count = 0
    for video in videos[:5]:  # Limit to first 5 for demo
        print(f"\n📹 {video.title[:50]}...")
        
        try:
            views_input = input("Views (Enter to skip): ").strip()
            if not views_input:
                continue
                
            views = int(views_input)
            likes = int(input("Likes: ") or "0")
            comments = int(input("Comments: ") or "0")
            
            metrics = VideoMetrics(
                video_id=video.video_id,
                platform="instagram",
                views=views,
                likes=likes,
                shares=0,
                comments=comments,
                engagement_rate=(likes + comments) / views if views > 0 else 0,
                collected_at=datetime.now()
            )
            
            db.add_metrics(metrics)
            updated_count += 1
            print("✅ Updated!")
            
        except ValueError:
            print("❌ Invalid input, skipping...")
        except KeyboardInterrupt:
            print("\n⏹️  Update cancelled")
            break
    
    print(f"\n✅ Updated {updated_count} videos")

def set_total_views(db, videos):
    """Set total views and distribute across videos"""
    print("\n📊 SET TOTAL VIEWS")
    
    try:
        total_views = int(input("Enter total Instagram views: "))
        
        # Get current distribution
        current_totals = calculate_current_totals(db, videos)
        current_total = current_totals['views']
        
        if current_total > 0:
            # Scale existing metrics
            scale_factor = total_views / current_total
            print(f"Scaling existing metrics by factor: {scale_factor:.2f}")
            
            for video in videos:
                latest_metrics = db.get_latest_metrics(video.video_id, "instagram")
                if latest_metrics:
                    new_views = int(latest_metrics.views * scale_factor)
                    new_likes = int(latest_metrics.likes * scale_factor)
                    new_comments = int(latest_metrics.comments * scale_factor)
                    
                    metrics = VideoMetrics(
                        video_id=video.video_id,
                        platform="instagram",
                        views=new_views,
                        likes=new_likes,
                        shares=0,
                        comments=new_comments,
                        engagement_rate=(new_likes + new_comments) / new_views if new_views > 0 else 0,
                        collected_at=datetime.now()
                    )
                    
                    db.add_metrics(metrics)
        else:
            # Distribute evenly
            views_per_video = total_views // len(videos)
            print(f"Distributing {views_per_video:,} views per video")
            
            for video in videos:
                metrics = VideoMetrics(
                    video_id=video.video_id,
                    platform="instagram",
                    views=views_per_video,
                    likes=views_per_video // 10,  # Assume 10% like rate
                    shares=0,
                    comments=views_per_video // 50,  # Assume 2% comment rate
                    engagement_rate=0.12,  # 12% engagement rate
                    collected_at=datetime.now()
                )
                
                db.add_metrics(metrics)
        
        print("✅ Total views updated!")
        
    except ValueError:
        print("❌ Invalid input")

if __name__ == "__main__":
    load_dotenv()
    manual_instagram_update()
