#!/usr/bin/env python3
"""Collect metrics from all platforms"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analytics.metrics_collector import create_metrics_collector_manager

# Load environment variables
load_dotenv()

async def main():
    """Collect metrics from all configured platforms"""
    print("📊 Collecting Video Metrics")
    print("=" * 40)
    
    # Get API keys from environment
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    tiktok_access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    
    # Create metrics collector manager
    manager = create_metrics_collector_manager(
        youtube_api_key=youtube_api_key,
        instagram_access_token=instagram_access_token,
        tiktok_access_token=tiktok_access_token
    )
    
    if not manager.collectors:
        print("❌ No platform collectors configured")
        print("Set the following environment variables:")
        print("  - YOUTUBE_API_KEY")
        print("  - INSTAGRAM_ACCESS_TOKEN")
        print("  - TIKTOK_ACCESS_TOKEN")
        return
    
    print(f"🔧 Configured platforms: {', '.join(manager.collectors.keys())}")
    
    # Collect metrics from all platforms
    results = await manager.collect_all_platforms()
    
    print("\n📈 Collection Results:")
    print("-" * 30)
    
    total_metrics = 0
    for platform, metrics in results.items():
        print(f"  {platform}: {len(metrics)} metrics collected")
        total_metrics += len(metrics)
        
        # Show sample metrics
        if metrics:
            latest = metrics[0]  # Most recent
            print(f"    Latest: {latest.views} views, {latest.likes} likes, {latest.comments} comments")
    
    print(f"\n✅ Total metrics collected: {total_metrics}")

if __name__ == "__main__":
    import os
    asyncio.run(main())
