#!/usr/bin/env python3
"""Automated metrics syncing every 15-30 minutes"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, time as dt_time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analytics.oauth_channel_discovery import OAuthChannelDiscovery
from src.analytics.database import AnalyticsDatabase
from src.managers.oauth_manager import OAuthManager

async def sync_all_metrics():
    """Sync videos and collect metrics from all platforms"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting metrics sync...")
    
    db = AnalyticsDatabase()
    discovery = OAuthChannelDiscovery(db)
    
    try:
        # Sync new videos from all authenticated channels
        results = await discovery.sync_all_authenticated_channels(max_results=100)
        total_videos = sum(len(videos) for videos in results.values())
        print(f"  [OK] Synced {total_videos} videos")
        
        # Collect metrics for all videos
        from src.analytics.metrics_collector import create_metrics_collector_manager
        
        youtube_key = os.getenv("YOUTUBE_API_KEY")
        instagram_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        
        manager = create_metrics_collector_manager(
            youtube_api_key=youtube_key,
            instagram_access_token=instagram_token,
            tiktok_access_token=tiktok_token
        )
        
        all_videos = db.list_videos(limit=1000)
        collected = 0
        
        for video in all_videos:
            if not video.platform_video_id:
                continue
            
            try:
                metrics = await manager.collect_metrics(video.platform, video.video_id, video.platform_video_id)
                if metrics:
                    db.add_metrics(metrics)
                    collected += 1
            except Exception as e:
                continue
        
        print(f"  [OK] Collected metrics for {collected} videos")
        
        # Get current stats
        stats = db.get_analytics_summary()
        print(f"  [STATS] Total videos: {stats.get('total_videos', 0)}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False

async def check_and_create_daily_snapshot():
    """Create daily snapshot if needed"""
    db = AnalyticsDatabase()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check if snapshot for today exists
    snapshots = db.get_daily_snapshots(days=1)
    if not snapshots or snapshots[-1].snapshot_date != today:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Creating daily snapshot...")
        db.create_daily_snapshot()
        print("  [OK] Snapshot created")

async def run_continuous_sync(interval_minutes: int = 20):
    """Run sync continuously at specified interval"""
    print(f"Starting continuous sync (every {interval_minutes} minutes)")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    while True:
        try:
            # Run sync
            await sync_all_metrics()
            
            # Check if we need daily snapshot (run at midnight)
            now = datetime.now()
            if now.hour == 0 and now.minute < interval_minutes:
                await check_and_create_daily_snapshot()
            
            # Wait for next interval
            print(f"  [WAIT] Next sync in {interval_minutes} minutes")
            await asyncio.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            print("\n\nStopping sync...")
            break
        except Exception as e:
            print(f"  [ERROR] Unexpected error: {e}")
            print(f"  [RETRY] Retrying in {interval_minutes} minutes")
            await asyncio.sleep(interval_minutes * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-sync metrics from all platforms")
    parser.add_argument("--interval", type=int, default=20, help="Minutes between syncs (default: 20)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    
    if args.once:
        asyncio.run(sync_all_metrics())
        asyncio.run(check_and_create_daily_snapshot())
    else:
        asyncio.run(run_continuous_sync(interval_minutes=args.interval))
