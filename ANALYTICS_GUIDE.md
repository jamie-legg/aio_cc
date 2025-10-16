# Video Analytics System

A comprehensive analytics system for tracking video creation, platform uploads, and performance metrics across YouTube, Instagram, and TikTok.

## 🚀 Quick Start

### 1. Start the Analytics Server

```bash
# Start the analytics API server
uv run analytics-server

# Or manually
uv run python start_analytics.py
```

The server will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Track Video Creation

When creating videos with Sora 2, they're automatically tracked:

```bash
# Generate a video (automatically tracked)
uv run content-cli transitions generate -t racing -c 1
```

### 3. Collect Platform Metrics

```bash
# Collect metrics from all platforms
uv run collect-metrics

# Or manually
uv run python collect_metrics.py
```

## 📊 Database Schema

### Videos Table
Tracks all video creation and upload information:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| video_id | TEXT | Unique video identifier |
| title | TEXT | Video title |
| description | TEXT | Video description |
| prompt | TEXT | AI generation prompt |
| platform | TEXT | Platform (sora, youtube, instagram, tiktok) |
| platform_video_id | TEXT | ID on the platform |
| platform_url | TEXT | URL on the platform |
| duration | REAL | Video duration in seconds |
| file_path | TEXT | Local file path |
| created_at | TIMESTAMP | Creation timestamp |
| uploaded_at | TIMESTAMP | Upload timestamp |
| status | TEXT | Status (created, processing, uploaded, published, error) |

### Video Metrics Table
Tracks performance metrics over time:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| video_id | TEXT | Foreign key to videos |
| platform | TEXT | Platform name |
| views | INTEGER | View count |
| likes | INTEGER | Like count |
| shares | INTEGER | Share count |
| comments | INTEGER | Comment count |
| engagement_rate | REAL | Calculated engagement rate |
| collected_at | TIMESTAMP | Metrics collection timestamp |

## 🔌 API Endpoints

### Video Management

#### Create Video
```http
POST /videos
Content-Type: application/json

{
  "video_id": "video_123",
  "title": "My Video",
  "description": "Video description",
  "prompt": "AI generation prompt",
  "platform": "sora",
  "duration": 5.0,
  "file_path": "/path/to/video.mp4"
}
```

#### Get Video
```http
GET /videos/{video_id}
```

#### List Videos
```http
GET /videos?platform=youtube&status=published&limit=10&offset=0
```

#### Update Video
```http
PATCH /videos/{video_id}
Content-Type: application/json

{
  "status": "published",
  "platform_video_id": "yt_123456",
  "platform_url": "https://youtube.com/watch?v=123456"
}
```

### Metrics Management

#### Add Metrics
```http
POST /metrics
Content-Type: application/json

{
  "video_id": "video_123",
  "platform": "youtube",
  "views": 1000,
  "likes": 50,
  "shares": 10,
  "comments": 25,
  "engagement_rate": 0.085
}
```

#### Get Latest Metrics
```http
GET /metrics/{video_id}/latest?platform=youtube
```

#### Get Metrics History
```http
GET /metrics/{video_id}/history?platform=youtube&limit=30
```

### Analytics

#### Get Summary
```http
GET /analytics/summary?platform=youtube&days=30
```

Response:
```json
{
  "total_videos": 25,
  "status_counts": {
    "published": 20,
    "uploaded": 3,
    "error": 2
  },
  "avg_metrics": {
    "avg_views": 1250.5,
    "avg_likes": 62.3,
    "avg_shares": 8.7,
    "avg_comments": 15.2,
    "avg_engagement": 0.068
  },
  "period_days": 30,
  "platform": "youtube"
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your API keys:

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_key

# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key

# Instagram Basic Display API
INSTAGRAM_ACCESS_TOKEN=your_instagram_token

# TikTok for Business API
TIKTOK_ACCESS_TOKEN=your_tiktok_token

# Analytics API (optional, defaults to localhost:8000)
ANALYTICS_API_URL=http://localhost:8000
```

### API Keys Setup

#### YouTube Data API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create credentials (API Key)
4. Add to `.env` as `YOUTUBE_API_KEY`

#### Instagram Basic Display API
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app
3. Add Instagram Basic Display product
4. Generate access token
5. Add to `.env` as `INSTAGRAM_ACCESS_TOKEN`

#### TikTok for Business API
1. Go to [TikTok for Business](https://business.tiktok.com/)
2. Create a developer account
3. Create an app and get access token
4. Add to `.env` as `TIKTOK_ACCESS_TOKEN`

## 📈 Usage Examples

### Python Integration

```python
from analytics.video_tracker import get_video_tracker

# Get tracker instance
tracker = get_video_tracker()

# Track video creation
tracker.track_video_creation(
    video_id="video_123",
    title="My Amazing Video",
    description="Generated with AI",
    prompt="A cool cat on a motorcycle",
    platform="sora",
    duration=5.0
)

# Track platform upload
tracker.track_video_upload(
    video_id="video_123",
    platform="youtube",
    platform_video_id="yt_123456",
    platform_url="https://youtube.com/watch?v=123456"
)

# Track publication
tracker.track_video_published("video_123")

# Get analytics summary
summary = tracker.get_analytics_summary(platform="youtube", days=7)
print(f"Total videos: {summary['total_videos']}")
```

### Metrics Collection

```python
from analytics.metrics_collector import create_metrics_collector_manager
import asyncio

async def collect_metrics():
    manager = create_metrics_collector_manager(
        youtube_api_key="your_key",
        instagram_access_token="your_token",
        tiktok_access_token="your_token"
    )
    
    # Collect from all platforms
    results = await manager.collect_all_platforms()
    
    for platform, metrics in results.items():
        print(f"{platform}: {len(metrics)} metrics collected")

# Run collection
asyncio.run(collect_metrics())
```

## 🔄 Automated Collection

### Cron Job Setup

Add to your crontab for automated metrics collection:

```bash
# Collect metrics every hour
0 * * * * cd /path/to/project && uv run collect-metrics

# Or every 6 hours
0 */6 * * * cd /path/to/project && uv run collect-metrics
```

### Systemd Service (Linux)

Create `/etc/systemd/system/video-analytics.service`:

```ini
[Unit]
Description=Video Analytics API Server
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/.venv/bin/python start_analytics.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable video-analytics
sudo systemctl start video-analytics
```

## 📊 Dashboard Integration

The analytics API provides data that can be easily integrated with dashboards:

### Grafana Integration
Use the `/analytics/summary` endpoint to create dashboards showing:
- Video creation trends
- Platform performance
- Engagement metrics over time

### Custom Dashboard
Build a simple web dashboard using the API:

```javascript
// Fetch analytics data
const response = await fetch('http://localhost:8000/analytics/summary?days=30');
const data = await response.json();

console.log(`Total videos: ${data.total_videos}`);
console.log(`Average views: ${data.avg_metrics.avg_views}`);
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```
   sqlite3.OperationalError: database is locked
   ```
   Solution: Ensure only one process is accessing the database at a time

2. **API Key Errors**
   ```
   HTTP 403: API key not valid
   ```
   Solution: Check your API keys in the `.env` file

3. **Metrics Collection Fails**
   ```
   Failed to collect metrics for youtube: HTTP 403
   ```
   Solution: Verify your API keys have the correct permissions

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Inspection

Inspect the SQLite database directly:

```bash
sqlite3 analytics.db
.tables
.schema videos
SELECT * FROM videos LIMIT 5;
```

## 🔒 Security Considerations

1. **API Keys**: Store securely and never commit to version control
2. **Database**: Consider encrypting sensitive data
3. **Network**: Use HTTPS in production
4. **Access Control**: Implement authentication for production use

## 📚 API Documentation

Once the server is running, visit http://localhost:8000/docs for interactive API documentation with Swagger UI.
