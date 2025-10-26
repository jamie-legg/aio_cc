# Channel Analytics & Aggregated Views Guide

This guide shows how to discover videos from your authorized channels and get aggregated view counts across all platforms.

## 🚀 Quick Start

### 1. Sync Your Channel Videos

```bash
# Sync videos from all your channels
uv run sync-channels --youtube-channel YOUR_CHANNEL_ID --instagram-user YOUR_USER_ID --tiktok-user YOUR_USER_ID

# Or sync just one platform
uv run sync-channels --youtube-channel YOUR_CHANNEL_ID

# Get just total views (quick check)
uv run sync-channels --total-views-only
```

### 2. Get Aggregated Stats via API

```bash
# Start the analytics server
uv run analytics-server

# Get total views across all platforms
curl http://localhost:8000/channels/total-views

# Get detailed channel statistics
curl http://localhost:8000/channels/stats

# Sync channels via API
curl "http://localhost:8000/channels/sync?youtube_channel_id=YOUR_CHANNEL_ID&max_results=100"
```

## 📊 What You'll Get

### Total Views Across Platforms
```json
{
  "total_views": 1250000,
  "platform_breakdown": {
    "youtube": 800000,
    "instagram": 300000,
    "tiktok": 150000
  },
  "formatted_total": "1,250,000",
  "platforms": 3
}
```

### Detailed Channel Statistics
```json
{
  "total_views_across_platforms": 1250000,
  "platform_breakdown": {
    "youtube": 800000,
    "instagram": 300000,
    "tiktok": 150000
  },
  "channel_stats": [
    {
      "platform": "youtube",
      "total_videos": 45,
      "total_views": 800000,
      "total_likes": 40000,
      "total_shares": 5000,
      "total_comments": 8000,
      "avg_engagement_rate": 0.065,
      "most_popular_video": {
        "platform": "youtube",
        "platform_video_id": "abc123",
        "title": "My Most Popular Video",
        "platform_url": "https://youtube.com/watch?v=abc123"
      }
    }
  ]
}
```

## 🔧 Setup Instructions

### 1. Get Your Channel/User IDs

#### YouTube Channel ID
1. Go to your YouTube channel
2. Look at the URL: `https://youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxx`
3. The part after `/channel/` is your channel ID

#### Instagram User ID
1. Go to [Instagram Basic Display API](https://developers.facebook.com/tools/explorer/)
2. Use your access token to get user info
3. The `id` field is your user ID

#### TikTok User ID
1. Go to [TikTok for Business](https://business.tiktok.com/)
2. In your account settings, find your user ID

### 2. Configure API Keys

Add to your `.env` file:

```bash
# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key

# Instagram Basic Display API
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token

# TikTok for Business API
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token
```

### 3. Get API Keys

#### YouTube Data API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key

#### Instagram Basic Display API
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Instagram Basic Display product
4. Generate a long-lived access token
5. Copy the access token

#### TikTok for Business API
1. Go to [TikTok for Business](https://business.tiktok.com/)
2. Create a developer account
3. Create an app
4. Get your access token

## 📈 Usage Examples

### Python Integration

```python
import asyncio
from analytics.database import AnalyticsDatabase
from analytics.channel_discovery import ChannelDiscovery

async def analyze_my_channels():
    # Initialize
    db = AnalyticsDatabase()
    discovery = ChannelDiscovery(db)
    
    # Setup with API keys
    discovery.setup_collectors(
        youtube_api_key="your_youtube_api_key",
        instagram_access_token="your_instagram_token",
        tiktok_access_token="your_tiktok_token"
    )
    
    # Sync videos from your channels
    results = await discovery.sync_channel_videos(
        youtube_channel_id="UCxxxxxxxxxxxxxxxxxxxxx",
        instagram_user_id="123456789",
        tiktok_user_id="tiktok_user_123"
    )
    
    # Get aggregated stats
    stats = await discovery.get_aggregated_channel_stats()
    total_views, platform_breakdown = discovery.get_total_views_across_platforms()
    
    print(f"Total views across all platforms: {total_views:,}")
    for platform, views in platform_breakdown.items():
        print(f"{platform}: {views:,} views")

# Run the analysis
asyncio.run(analyze_my_channels())
```

### API Integration

```python
import requests

# Get total views
response = requests.get("http://localhost:8000/channels/total-views")
data = response.json()
print(f"Total views: {data['formatted_total']}")

# Get detailed stats
response = requests.get("http://localhost:8000/channels/stats")
stats = response.json()

for channel in stats['channel_stats']:
    print(f"{channel['platform']}: {channel['total_views']:,} views")
```

## 🔄 Automated Workflows

### Daily Sync Script

Create `daily_sync.py`:

```python
#!/usr/bin/env python3
import asyncio
import os
from analytics.database import AnalyticsDatabase
from analytics.channel_discovery import ChannelDiscovery

async def daily_sync():
    db = AnalyticsDatabase()
    discovery = ChannelDiscovery(db)
    
    discovery.setup_collectors(
        youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
        instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN"),
        tiktok_access_token=os.getenv("TIKTOK_ACCESS_TOKEN")
    )
    
    # Sync latest videos
    await discovery.sync_channel_videos(
        youtube_channel_id=os.getenv("YOUTUBE_CHANNEL_ID"),
        instagram_user_id=os.getenv("INSTAGRAM_USER_ID"),
        tiktok_user_id=os.getenv("TIKTOK_USER_ID"),
        max_results=20  # Only latest 20 videos
    )
    
    # Get total views
    total_views, _ = discovery.get_total_views_across_platforms()
    print(f"Daily sync complete. Total views: {total_views:,}")

if __name__ == "__main__":
    asyncio.run(daily_sync())
```

### Cron Job Setup

```bash
# Add to crontab for daily sync at 6 AM
0 6 * * * cd /path/to/project && uv run python daily_sync.py
```

## 📊 Dashboard Integration

### Grafana Dashboard

Use the API endpoints to create dashboards:

```javascript
// Total views over time
const totalViews = await fetch('http://localhost:8000/channels/total-views')
  .then(r => r.json());

// Platform breakdown
const platformData = totalViews.platform_breakdown;
```

### Custom Web Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>Channel Analytics</title>
</head>
<body>
    <h1>My Channel Analytics</h1>
    <div id="total-views"></div>
    <div id="platform-breakdown"></div>
    
    <script>
        async function loadAnalytics() {
            const response = await fetch('http://localhost:8000/channels/total-views');
            const data = await response.json();
            
            document.getElementById('total-views').innerHTML = 
                `<h2>Total Views: ${data.formatted_total}</h2>`;
            
            let breakdown = '<h3>Platform Breakdown:</h3><ul>';
            for (const [platform, views] of Object.entries(data.platform_breakdown)) {
                breakdown += `<li>${platform}: ${views.toLocaleString()} views</li>`;
            }
            breakdown += '</ul>';
            
            document.getElementById('platform-breakdown').innerHTML = breakdown;
        }
        
        loadAnalytics();
    </script>
</body>
</html>
```

## 🚨 Troubleshooting

### Common Issues

1. **No videos found after sync**
   - Check your channel/user IDs are correct
   - Verify API keys have proper permissions
   - Check if videos are public

2. **API rate limiting**
   - The system includes delays between requests
   - Reduce `max_results` if needed
   - Check API quotas

3. **Missing metrics**
   - Run `uv run collect-metrics` to fetch latest metrics
   - Some platforms have limited API access

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Database

```bash
sqlite3 analytics.db
.tables
SELECT platform, COUNT(*) FROM videos GROUP BY platform;
SELECT platform, SUM(views) FROM video_metrics GROUP BY platform;
```

## 🎯 Best Practices

1. **Regular Syncing**: Set up daily syncs to keep data current
2. **API Quotas**: Monitor your API usage to avoid hitting limits
3. **Data Backup**: Regularly backup your analytics database
4. **Error Handling**: Implement retry logic for API failures
5. **Monitoring**: Set up alerts for sync failures

## 📚 API Reference

### Channel Sync Endpoint
```
GET /channels/sync?youtube_channel_id=ID&max_results=50
```

### Total Views Endpoint
```
GET /channels/total-views
```

### Channel Stats Endpoint
```
GET /channels/stats
```

For full API documentation, visit http://localhost:8000/docs when the server is running.
