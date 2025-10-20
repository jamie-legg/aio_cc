# Complete Stack Startup Guide

## ✅ Fixed: `make start` Now Controls Everything

The `make start` command has been updated to manage the complete stack:

### Services Started (in order):

1. **Database Initialization** - Creates new tables (ai_prompt_templates, updated scheduled_posts)
2. **Clip Watcher** - Monitors video directory and auto-schedules videos
3. **API Server** - Provides REST API (port 8000)
4. **Scheduler Daemon** - Auto-posts scheduled videos (checks every minute)
5. **Dashboard** - Web UI (port 5173)

## Quick Start

```bash
make start
```

That's it! All services will start automatically.

## What You'll See

```
==================================================
  Content Creation Platform - Starting
==================================================

[INIT] Initializing database...
[INIT] 📊 Initializing analytics database...
[INIT] ✅ Database tables created/verified
[INIT] ✅ Found N existing AI template(s)
[INIT] 🎉 Database initialization complete!

[WATCHER] Starting clip watcher...
[API] Starting analytics API server...
[SCHEDULER] Starting scheduler daemon...
[DASHBOARD] Starting analytics dashboard...

==================================================
  All Services Started!
==================================================

[WATCHER]   Monitoring videos folder
[API]       http://localhost:8000
[SCHEDULER] Auto-posting scheduled videos
[DASHBOARD] http://localhost:5173/dashboard

Press Ctrl+C to stop all services
```

## Services Explained

### 1. Database Initialization (`scripts/init_database.py`)
- Creates all required tables
- Creates default AI template if none exist
- Runs once at startup before other services

### 2. Clip Watcher (`main.py`)
- Monitors watch directory for new videos
- Processes videos (AI metadata, format conversion)
- **Auto-schedules** videos to next available hour
- Emits events to dashboard

### 3. API Server (`scripts/analytics/start_analytics.py`)
- REST API on port 8000
- Endpoints for:
  - Analytics data
  - Schedule management
  - AI template CRUD
  - OBS status
  - Watcher events (SSE)

### 4. Scheduler Daemon (`src/scheduling/scheduler_daemon.py`)
- Runs in background
- Checks every 60 seconds for due posts
- Auto-posts videos to platforms when scheduled time arrives
- Updates status: pending → processing → completed/failed
- Retry logic (max 3 attempts)

### 5. Dashboard (`analytics-dashboard/`)
- Web UI on port 5173
- Pages:
  - `/dashboard` - Analytics
  - `/dashboard/schedule` - Scheduled posts
  - `/dashboard/ai-config` - AI templates
- Real-time updates via SSE
- Watcher activity panel (bottom-right)

## Testing the Complete Flow

1. **Start the stack:**
   ```bash
   make start
   ```

2. **Wait for all services to initialize** (about 5-10 seconds)

3. **Open dashboard:**
   ```
   http://localhost:5173/dashboard
   ```

4. **Configure AI template (optional):**
   - Navigate to AI Config page
   - Create/edit templates
   - Test prompts
   - Set one as active

5. **Drop a video** in your watch directory

6. **Watch the magic:**
   - Watcher detects file
   - AI generates metadata (using active template)
   - Video processed for Shorts format
   - **Auto-scheduled** for next hour
   - Appears in Schedule page with countdown
   - When time arrives, scheduler daemon posts it
   - Appears in Analytics page

## Troubleshooting

### "Failed to load scheduled posts"
**Fixed!** The database initialization now creates the required tables automatically.

If you still see this error:
1. Stop all services (Ctrl+C)
2. Run: `uv run python scripts/init_database.py`
3. Start again: `make start`

### Service won't start
Check individual services:
```bash
# Test watcher
uv run python main.py

# Test API
uv run python scripts/analytics/start_analytics.py

# Test scheduler
uv run python src/scheduling/scheduler_daemon.py

# Test dashboard
cd analytics-dashboard && npm run dev
```

### Database errors
Reset database:
```bash
make db-reset
make start  # Will recreate tables
```

### Scheduler not posting
- Check if posts are scheduled: `/dashboard/schedule`
- Verify scheduler daemon is running (should see `[SCHEDULER]` logs)
- Check scheduled_time is in the past
- Verify platforms are authenticated

## Individual Commands

If you prefer to start services individually:

```bash
# Start everything
make start

# Or start individually:
make start-watcher      # Just the watcher
make start-analytics    # Just the API
make scheduler-run      # Just the scheduler
make start-dashboard    # Just the dashboard
```

## Configuration Files

- `config.json` - Watcher configuration
- `analytics.db` - SQLite database
- `.env` - API keys and secrets
- `credentials.json` - OAuth tokens

## Ports Used

- `8000` - API Server
- `5173` - Dashboard (dev)
- `5174` - Dashboard (prod)

## Stopping Services

Press `Ctrl+C` once - all services will stop gracefully.

The start script handles cleanup automatically.

## Log Files

Logs are displayed in real-time with color coding:
- 🟢 `[WATCHER]` - Green
- 🔵 `[API]` - Blue  
- 🟡 `[SCHEDULER]` - Yellow
- 🟣 `[DASHBOARD]` - Magenta
- 🔷 `[INIT]` - Cyan
- 🔴 `[ERROR]` - Red

## Environment Variables

Optional variables in `.env`:
```bash
# Auto-scheduling (default: true)
AUTO_SCHEDULE=true

# Hours between posts on same platform (default: 1)
SCHEDULE_SPACING_HOURS=1

# Hours after processing to post (default: 1)
DEFAULT_POST_TIME_OFFSET=1
```

## What's New

### Scheduling System
- ✅ Auto-schedule videos to next hour
- ✅ Smart slot detection per platform
- ✅ Countdown timers
- ✅ Force immediate posting
- ✅ Retry logic on failure

### AI Templates
- ✅ Multiple templates support
- ✅ Active template selection
- ✅ Test prompt functionality
- ✅ Default template included

### Dashboard
- ✅ Fixed sidebar navigation
- ✅ Schedule page with countdown
- ✅ AI Config page
- ✅ Real-time updates

### Integration
- ✅ Watcher → Scheduler
- ✅ AI Manager → Templates
- ✅ Complete event system

## Success Checklist

After running `make start`, verify:

- [ ] No error messages during startup
- [ ] All 4 services show in logs (WATCHER, API, SCHEDULER, DASHBOARD)
- [ ] Dashboard opens at http://localhost:5173/dashboard
- [ ] Can navigate between Analytics/Schedule/AI Config pages
- [ ] Watcher panel appears in bottom-right
- [ ] Drop video → see it scheduled in Schedule page
- [ ] Countdown timer updates every second
- [ ] Can force post → video uploads

## Need Help?

Check these files:
- `IMPLEMENTATION_COMPLETE_SCHEDULING.md` - Full feature documentation
- `SCHEDULING_STATUS.md` - Implementation status
- `OBS_DETECTION_GUIDE.md` - OBS integration guide

Run `make help` to see all available commands.

## Summary

The complete stack is now **fully operational** with one command:

```bash
make start
```

All services work together:
- Videos drop → AI processes → Auto-schedules → Daemon posts → Analytics tracks

Everything is automated and integrated! 🚀

