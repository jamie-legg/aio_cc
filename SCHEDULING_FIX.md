# Auto-Scheduling Fix

## Problem
Videos were being immediately uploaded to all platforms instead of being scheduled for later posting.

## Root Cause
The clip watcher (`src/content_creation/clip_watcher.py`) was always calling the immediate upload function instead of checking the `auto_schedule` configuration setting.

## Solution
Updated the clip watcher to respect the `AUTO_SCHEDULE` configuration setting:

- **When `AUTO_SCHEDULE=true`** (default): Videos are scheduled for later posting
- **When `AUTO_SCHEDULE=false`**: Videos are uploaded immediately

## Configuration

### Environment Variable (Recommended)
Add to your `.env` file:

```bash
# Set to true to schedule videos (default)
AUTO_SCHEDULE=true

# Set to false to immediately upload videos
# AUTO_SCHEDULE=false

# Optional: Configure scheduling behavior
SCHEDULE_SPACING_HOURS=1         # Hours between posts on same platform
DEFAULT_POST_TIME_OFFSET=1        # Hours after processing to schedule posts
```

### Config File
The setting is also saved in `~/.content_creation/config.json`:

```json
{
  "auto_schedule": true,
  "schedule_spacing_hours": 1,
  "default_post_time_offset": 1
}
```

## What You'll See Now

### With Auto-Schedule Enabled (Default)
When a new video is detected, you'll see:

```
============================================================
[SCHEDULING] Preparing to schedule video for later posting...
============================================================
[SCHEDULING] Platforms: INSTAGRAM, YOUTUBE, TIKTOK

[✓ SCHEDULED] Video added to schedule!
   📅 Time: 08:00 PM on October 20, 2025
   📱 Platforms: INSTAGRAM, YOUTUBE, TIKTOK
   📊 View schedule: http://localhost:5173/uploads

============================================================
```

### With Auto-Schedule Disabled
Videos will upload immediately as before, showing upload progress for each platform.

## Viewing Scheduled Videos

1. Open the dashboard: http://localhost:5173/uploads
2. Click the "Scheduled" tab to see upcoming posts
3. You can edit or delete scheduled posts from the dashboard

## How the Scheduler Works

1. **Video Detection**: New video files are detected in your watch directory
2. **Processing**: Videos are processed with AI metadata, watermarks, and outro
3. **Scheduling**: Videos are scheduled for the next available time slot
4. **Auto-Posting**: The scheduler daemon automatically posts videos at their scheduled time
5. **Spacing**: Posts are spaced 1 hour apart by default (configurable)

## Manual Control

If you want to post a scheduled video immediately:
1. Go to the Uploads page: http://localhost:5173/uploads
2. Find the scheduled video
3. Click "Post Now" or edit the scheduled time

## Switching Between Modes

### To Enable Scheduling (Default)
```bash
# In your .env file
AUTO_SCHEDULE=true
```

### To Disable Scheduling (Immediate Upload)
```bash
# In your .env file
AUTO_SCHEDULE=false
```

Then restart the services:
```bash
uv run python scripts/start_all.py
```

## Notes

- The scheduler daemon must be running for scheduled posts to be published
- All scheduled posts are stored in the analytics database (`analytics.db`)
- Failed uploads are tracked and can be retried from the dashboard
- You can view the schedule and upcoming posts in the Uploads page

