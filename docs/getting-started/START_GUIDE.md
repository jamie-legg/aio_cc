# Quick Start Guide

## Starting All Services

You can now start all three services (clip watcher, analytics API, and dashboard) with a single command:

```bash
make start
```

This will start:
- **Clip Watcher**: Monitors your videos folder for new clips
- **Analytics API**: Running on http://localhost:8000
- **Dashboard**: Running on http://localhost:5173/dashboard

All service output will appear in one terminal with color-coded prefixes:
- `[WATCHER]` - Clip watcher messages (Green)
- `[API]` - Analytics API messages (Blue)
- `[DASHBOARD]` - Dashboard messages (Magenta)

## Accessing the Services

Once started, you can access:

- **Analytics API Documentation**: http://localhost:8000/docs
- **Analytics Dashboard**: http://localhost:5173/dashboard
- **API Health Check**: http://localhost:8000/health

## Stopping Services

Press `Ctrl+C` in the terminal to stop all services at once.

## Alternative: Starting Services Individually

If you prefer to start services separately:

```bash
# Start clip watcher only
uv run python main.py

# Start analytics API only  
make start-analytics

# Start dashboard only
make start-dashboard
```

## Troubleshooting

### Port Already in Use

If you get an error about ports already in use:

```bash
# Kill all Python processes
taskkill /F /IM python.exe

# Kill all Node processes
taskkill /F /IM node.exe

# Then try again
make start
```

### Services Not Starting

1. Make sure all dependencies are installed:
   ```bash
   make install
   cd analytics-dashboard && npm install
   ```

2. Check that FFmpeg is installed (for video processing)

3. Check that the `.env` file exists with proper configuration

## Features

### Video Processing
- Automatic watermark application (bottom-right, 256x256)
- Automatic outro addition (1 second at end)
- Aspect ratio conversion to 9:16 for Shorts
- Audio mixing and fade effects

### Analytics
- Track video performance across platforms
- View metrics and statistics
- Monitor total views and engagement

### Platforms Supported
- YouTube Shorts
- Instagram Reels
- TikTok


