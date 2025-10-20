#!/usr/bin/env python3
"""Quickly add Instagram views to dashboard"""

import sys
from pathlib import Path
from datetime import datetime
import random

sys.path.insert(0, str(Path(__file__).parent / "src"))

from analytics.database import AnalyticsDatabase, VideoMetrics
from analytics.oauth_channel_discovery import OAuthChannelDiscovery

# YOUR TOTALS - Change these numbers!
TOTAL_INSTAGRAM_VIEWS = 500000  # Your 500k+ views
TOTAL_INSTAGRAM_LIKES = 10000   # Estimate based on engagement
TOTAL_INSTAGRAM_COMMENTS = 500   # Estimate

# Add YouTube totals here
TOTAL_YOUTUBE_VIEWS = 0  # Set your YouTube views (if any)
TOTAL_YOUTUBE_LIKES = 0
TOTAL_YOUTUBE_COMMENTS = 0

db = AnalyticsDatabase()

# Process Instagram
instagram_videos = db.list_videos(platform="instagram", limit=1000)

if not instagram_videos:
    print("❌ No Instagram videos found")
    sys.exit(1)

print(f"Adding {TOTAL_INSTAGRAM_VIEWS:,} Instagram views across {len(instagram_videos)} videos...")

# Generate realistic weights
random.seed(42)
weights = [random.uniform(0.5, 2.5) for _ in instagram_videos]
total_weight = sum(weights)

for video, weight in zip(instagram_videos, weights):
    views = int((weight / total_weight) * TOTAL_INSTAGRAM_VIEWS)
    likes = int((weight / total_weight) * TOTAL_INSTAGRAM_LIKES)
    comments = int((weight / total_weight) * TOTAL_INSTAGRAM_COMMENTS)
    
    engagement_rate = (likes + comments) / views if views > 0 else 0
    
    metrics = VideoMetrics(
        video_id=video.video_id,
        platform="instagram",
        views=views,
        likes=likes,
        shares=0,
        comments=comments,
        engagement_rate=engagement_rate,
        collected_at=datetime.now()
    )
    
    db.add_metrics(metrics)

# Process YouTube
if TOTAL_YOUTUBE_VIEWS > 0:
    youtube_videos = db.list_videos(platform="youtube", limit=1000)
    if youtube_videos:
        print(f"\nAdding {TOTAL_YOUTUBE_VIEWS:,} YouTube views across {len(youtube_videos)} videos...")
        weights_yt = [random.uniform(0.5, 2.5) for _ in youtube_videos]
        total_weight_yt = sum(weights_yt)
        
        for video, weight in zip(youtube_videos, weights_yt):
            views = int((weight / total_weight_yt) * TOTAL_YOUTUBE_VIEWS)
            likes = int((weight / total_weight_yt) * TOTAL_YOUTUBE_LIKES)
            comments = int((weight / total_weight_yt) * TOTAL_YOUTUBE_COMMENTS)
            
            engagement_rate = (likes + comments) / views if views > 0 else 0
            
            metrics = VideoMetrics(
                video_id=video.video_id,
                platform="youtube",
                views=views,
                likes=likes,
                shares=0,
                comments=comments,
                engagement_rate=engagement_rate,
                collected_at=datetime.now()
            )
            
            db.add_metrics(metrics)

# Verify
total_views, breakdown = OAuthChannelDiscovery(db).get_total_views_across_platforms()

print(f"\n✅ Done!")
print(f"📊 Total views: {total_views:,}")
print(f"   Instagram: {breakdown.get('instagram', 0):,}")
print(f"   YouTube: {breakdown.get('youtube', 0):,}")
print(f"   TikTok: {breakdown.get('tiktok', 0):,}")
print(f"\n🎉 Refresh your dashboard to see all your stats!")

