#!/usr/bin/env python3
"""
Collect Instagram metrics for existing videos in the database.
This script will fetch real Instagram data using the Graph API.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analytics.database import AnalyticsDatabase
from analytics.metrics_collector import InstagramMetricsCollector

# Load environment variables
load_dotenv()

async def collect_instagram_metrics():
    """Collect Instagram metrics for all Instagram videos"""
    print("=" * 60)
    print("COLLECTING INSTAGRAM METRICS")
    print("=" * 60)
    
    # Get Instagram access token from environment
    instagram_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not instagram_token:
        print("❌ ERROR: INSTAGRAM_ACCESS_TOKEN not set in environment")
        print("Please add your Instagram Graph API access token to your .env file:")
        print("  INSTAGRAM_ACCESS_TOKEN=your_token_here")
        print()
        print("To get a token for a Business/Creator account:")
        print("  1. Go to https://developers.facebook.com/tools/explorer/")
        print("  2. Select your Instagram Business account")
        print("  3. Get a User Access Token with these permissions:")
        print("     - instagram_basic")
        print("     - instagram_manage_insights")
        print("     - pages_read_engagement")
        return
    
    # Initialize database and collector
    db = AnalyticsDatabase()
    collector = InstagramMetricsCollector(instagram_token, use_graph_api=True)
    
    # Get all Instagram videos
    instagram_videos = db.list_videos(platform="instagram", limit=1000)
    
    if not instagram_videos:
        print("❌ No Instagram videos found in database")
        print("Run the channel sync script first to import your Instagram videos.")
        return
    
    print(f"\n📹 Found {len(instagram_videos)} Instagram videos")
    print(f"🔄 Collecting metrics...\n")
    
    success_count = 0
    error_count = 0
    total_views = 0
    total_likes = 0
    total_comments = 0
    
    for video in instagram_videos:
        try:
            print(f"  📊 {video.title[:50]}...")
            
            # Collect metrics
            metrics = await collector.collect_metrics(
                video.video_id, 
                video.platform_video_id
            )
            
            if metrics:
                # Save to database
                db.add_metrics(metrics)
                
                # Update counters
                success_count += 1
                total_views += metrics.views
                total_likes += metrics.likes
                total_comments += metrics.comments
                
                print(f"     ✅ {metrics.views:,} views, {metrics.likes:,} likes, {metrics.comments:,} comments")
            else:
                error_count += 1
                print(f"     ❌ Failed to collect metrics")
                
        except Exception as e:
            error_count += 1
            print(f"     ❌ Error: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("COLLECTION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully collected: {success_count} videos")
    print(f"❌ Failed: {error_count} videos")
    print()
    print(f"📈 TOTAL INSTAGRAM STATS:")
    print(f"   👀 Total Views: {total_views:,}")
    print(f"   ❤️  Total Likes: {total_likes:,}")
    print(f"   💬 Total Comments: {total_comments:,}")
    print()
    
    if total_views > 0:
        engagement_rate = (total_likes + total_comments) / total_views * 100
        print(f"   📊 Engagement Rate: {engagement_rate:.2f}%")
    
    print("=" * 60)
    print()
    
    if error_count > 0:
        print("⚠️  Some videos failed to collect metrics.")
        print("This might be due to:")
        print("  - Invalid access token")
        print("  - Access token doesn't have required permissions")
        print("  - Video IDs are incorrect")
        print("  - Need to use Instagram Business/Creator account")
        print()
        print("Make sure you're using a token from:")
        print("  https://developers.facebook.com/tools/explorer/")
        print()

if __name__ == "__main__":
    asyncio.run(collect_instagram_metrics())

