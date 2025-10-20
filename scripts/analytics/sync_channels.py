#!/usr/bin/env python3
"""Sync videos from your authorized channels and get aggregated stats"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analytics.database import AnalyticsDatabase
from analytics.oauth_channel_discovery import OAuthChannelDiscovery

# Load environment variables
load_dotenv()

async def sync_and_analyze(max_results: int = 50):
    """Sync channels and show aggregated statistics"""
    
    print("🔄 Syncing Channel Videos")
    print("=" * 50)
    
    # Initialize database and OAuth discovery
    db = AnalyticsDatabase()
    discovery = OAuthChannelDiscovery(db)
    
    # Check authentication status
    from managers.oauth_manager import OAuthManager
    oauth_manager = OAuthManager()
    
    authenticated_platforms = []
    if oauth_manager.is_authenticated("youtube"):
        authenticated_platforms.append("youtube")
    if oauth_manager.is_authenticated("instagram"):
        authenticated_platforms.append("instagram")
    if oauth_manager.is_authenticated("tiktok"):
        authenticated_platforms.append("tiktok")
    
    if not authenticated_platforms:
        print("❌ No platforms authenticated!")
        print("Please run: uv run content-cli auth all")
        return
    
    print(f"✅ Found authenticated platforms: {', '.join(authenticated_platforms)}")
    
    # Sync videos from authenticated channels
    print("📥 Discovering videos from your authenticated channels...")
    results = await discovery.sync_all_authenticated_channels(max_results)
    
    total_synced = sum(len(videos) for videos in results.values())
    print(f"✅ Synced {total_synced} videos from your channels")
    
    for platform, videos in results.items():
        print(f"  {platform}: {len(videos)} videos")
    
    print("\n📊 Aggregated Channel Statistics")
    print("=" * 50)
    
    # Get aggregated stats
    stats = await discovery.get_aggregated_channel_stats()
    total_views, platform_breakdown = discovery.get_total_views_across_platforms()
    
    if not stats:
        print("❌ No videos found in database")
        print("Try syncing your channels first or create some videos")
        return
    
    # Display total views
    print(f"🎯 TOTAL VIEWS ACROSS ALL PLATFORMS: {total_views:,}")
    print()
    
    # Display platform breakdown
    print("📈 Platform Breakdown:")
    for platform, views in platform_breakdown.items():
        percentage = (views / total_views * 100) if total_views > 0 else 0
        print(f"  {platform.upper()}: {views:,} views ({percentage:.1f}%)")
    
    print()
    
    # Display detailed stats for each platform
    for platform, stat in stats.items():
        print(f"🔍 {platform.upper()} DETAILS:")
        print(f"  Videos: {stat.total_videos}")
        print(f"  Views: {stat.total_views:,}")
        print(f"  Likes: {stat.total_likes:,}")
        print(f"  Shares: {stat.total_shares:,}")
        print(f"  Comments: {stat.total_comments:,}")
        print(f"  Avg Engagement Rate: {stat.avg_engagement_rate:.2%}")
        
        if stat.most_popular_video:
            print(f"  Most Popular: {stat.most_popular_video.title}")
            print(f"    URL: {stat.most_popular_video.platform_url}")
        
        print()
    
    # Display top performing videos across all platforms
    print("🏆 TOP PERFORMING VIDEOS")
    print("=" * 50)
    
    all_videos = db.list_videos(status="published")
    video_metrics = []
    
    for video in all_videos:
        metrics = db.get_latest_metrics(video.video_id, video.platform)
        if metrics and metrics.views > 0:
            video_metrics.append((video, metrics))
    
    # Sort by views
    video_metrics.sort(key=lambda x: x[1].views, reverse=True)
    
    for i, (video, metrics) in enumerate(video_metrics[:10], 1):
        print(f"{i:2d}. {video.title[:50]}...")
        print(f"    {video.platform.upper()}: {metrics.views:,} views, {metrics.likes:,} likes")
        print(f"    URL: {video.platform_url}")
        print()

def main():
    """Main CLI function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync channel videos and get aggregated stats")
    parser.add_argument("--max-results", type=int, default=50, help="Max videos per platform")
    parser.add_argument("--total-views-only", action="store_true", help="Show only total views")
    
    args = parser.parse_args()
    
    if args.total_views_only:
        # Quick total views check
        async def quick_total():
            db = AnalyticsDatabase()
            discovery = OAuthChannelDiscovery(db)
            total_views, platform_breakdown = discovery.get_total_views_across_platforms()
            print(f"Total views: {total_views:,}")
            for platform, views in platform_breakdown.items():
                print(f"{platform}: {views:,}")
        
        asyncio.run(quick_total())
    else:
        # Full sync and analysis
        asyncio.run(sync_and_analyze(max_results=args.max_results))
    
    return 0

if __name__ == "__main__":
    exit(main())
