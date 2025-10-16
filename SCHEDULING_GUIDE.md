# Post Scheduling System Guide

## Overview

The scheduling system allows you to queue video posts and have them automatically uploaded to multiple platforms at specified times. The system is resilient to downtime and will handle missed posts when the scheduler comes back online.

## Features

- **Schedule posts for specific times**: Set exact date/time for each post
- **Multi-platform support**: Upload to YouTube, Instagram, and TikTok
- **Resilient to downtime**: Missed posts are uploaded immediately when scheduler restarts (within grace period)
- **Automatic retries**: Failed uploads are retried automatically (configurable max retries)
- **Status tracking**: View pending, completed, and failed posts
- **Grace period**: Skip posts that are too old (default: 1 hour)

## Quick Start

### 1. Schedule a Video

```bash
# Schedule a video for specific time
make schedule-add \
  VIDEO=test_videos/test_shorts_1.mp4 \
  TIME="2025-10-15 14:30" \
  PLATFORMS=youtube,instagram,tiktok \
  TITLE="Epic Gaming Moment" \
  CAPTION="Check out this amazing clip!" \
  HASHTAGS="#gaming #shorts #epic"
```

### 2. View Scheduled Posts

```bash
# List all scheduled posts
make schedule-list

# List only pending posts
make schedule-list STATUS=pending

# List posts for specific platform
make schedule-list PLATFORM=youtube
```

### 3. Run the Scheduler

```bash
# Run scheduler daemon (continuous mode)
make scheduler-run

# Run scheduler once and exit (useful for cron)
make scheduler-once

# Run with custom check interval (seconds)
make scheduler-run INTERVAL=30
```

### 4. Check Scheduler Status

```bash
make schedule-status
```

### 5. Cancel a Scheduled Post

```bash
# Cancel post with ID 1
make schedule-remove ID=1
```

## CLI Commands

All commands can also be run directly using `uv run content-cli`:

### Schedule Add

```bash
uv run content-cli schedule add VIDEO_PATH \
  --time "2025-10-15 10:00" \
  --platforms youtube,instagram,tiktok \
  --title "Title" \
  --caption "Caption" \
  --hashtags "#tags"
```

**Time Format Options:**
- `YYYY-MM-DD HH:MM` (e.g., "2025-10-15 10:00")
- `YYYY-MM-DDTHH:MM` (e.g., "2025-10-15T10:00")
- `YYYY-MM-DD HH:MM:SS` (e.g., "2025-10-15 10:00:00")

### Schedule List

```bash
uv run content-cli schedule list [OPTIONS]

Options:
  --status [pending|processing|completed|failed|cancelled]
  --platform [youtube|instagram|tiktok]
  --limit INTEGER  (default: 50)
```

### Schedule Remove

```bash
uv run content-cli schedule remove POST_ID
```

### Schedule Status

```bash
uv run content-cli schedule status
```

### Schedule Run

```bash
uv run content-cli schedule run [OPTIONS]

Options:
  --interval INTEGER  Check interval in seconds (default: 60)
  --once             Process pending posts once and exit
```

## Post Status Lifecycle

1. **pending**: Post is scheduled and waiting for its scheduled time
2. **processing**: Post is currently being uploaded
3. **completed**: Post was successfully uploaded (may have partial failures noted in error message)
4. **failed**: Post failed after maximum retries
5. **cancelled**: Post was manually cancelled

## Configuration

### Grace Period

Posts missed during downtime are uploaded if they're within the grace period (default: 60 minutes). Posts older than the grace period are marked as failed.

To adjust the grace period, modify `PostScheduler` initialization:

```python
scheduler = PostScheduler(
    grace_period_minutes=120  # 2 hours
)
```

### Max Retries

Failed uploads are retried automatically (default: 3 attempts). To adjust:

```python
scheduler = PostScheduler(
    max_retries=5
)
```

### Check Interval

How often the scheduler checks for pending posts (default: 60 seconds):

```bash
make scheduler-run INTERVAL=30  # Check every 30 seconds
```

## Running as a Background Service

### Using screen (Simple)

```bash
screen -S scheduler
make scheduler-run
# Press Ctrl+A, then D to detach
# To reattach: screen -r scheduler
```

### Using nohup

```bash
nohup make scheduler-run > scheduler.log 2>&1 &
```

### Using systemd (Linux - Recommended for Production)

Create `/etc/systemd/system/post-scheduler.service`:

```ini
[Unit]
Description=Post Scheduler Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/content_creation
ExecStart=/path/to/uv run content-cli schedule run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable post-scheduler
sudo systemctl start post-scheduler
sudo systemctl status post-scheduler
```

### Using launchd (macOS - Recommended for Production)

Create `~/Library/LaunchAgents/com.contentcreation.scheduler.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.contentcreation.scheduler</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/uv</string>
        <string>run</string>
        <string>content-cli</string>
        <string>schedule</string>
        <string>run</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/jamie/jamie/content_creation</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/jamie/jamie/content_creation/scheduler.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/jamie/jamie/content_creation/scheduler-error.log</string>
</dict>
</plist>
```

Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.contentcreation.scheduler.plist
launchctl start com.contentcreation.scheduler
```

### Using Cron (Alternative)

Run scheduler every minute (will process due posts and exit):

```bash
# Edit crontab
crontab -e

# Add this line:
* * * * * cd /path/to/content_creation && make scheduler-once >> scheduler-cron.log 2>&1
```

## Logging

Scheduler logs are written to `scheduler.log` in the project root. The log includes:

- When posts are scheduled
- When posts are processed
- Upload success/failure details
- Retry attempts
- Errors and warnings

To view logs in real-time:

```bash
tail -f scheduler.log
```

## Database

Scheduled posts are stored in `analytics.db` in the `scheduled_posts` table. You can query directly if needed:

```bash
sqlite3 analytics.db "SELECT * FROM scheduled_posts WHERE status='pending';"
```

## Troubleshooting

### Posts not uploading

1. Check scheduler is running: `make schedule-status`
2. Check authentication: `make check-auth`
3. Review logs: `tail -f scheduler.log`
4. Verify post is pending: `make schedule-list STATUS=pending`

### Post marked as failed

1. Check error message: `make schedule-list`
2. Verify video file still exists
3. Check platform authentication
4. Review scheduler logs for details

### Missed posts not uploading

Posts are only uploaded if missed by less than the grace period (default: 60 minutes). Older posts are automatically marked as failed.

## Examples

### Schedule multiple videos

```bash
# Schedule first video
make schedule-add \
  VIDEO=clip1.mp4 \
  TIME="2025-10-15 10:00" \
  PLATFORMS=youtube,instagram \
  TITLE="Morning Gaming Session"

# Schedule second video
make schedule-add \
  VIDEO=clip2.mp4 \
  TIME="2025-10-15 14:00" \
  PLATFORMS=youtube,tiktok \
  TITLE="Afternoon Gameplay"

# Schedule third video
make schedule-add \
  VIDEO=clip3.mp4 \
  TIME="2025-10-15 18:00" \
  PLATFORMS=youtube,instagram,tiktok \
  TITLE="Evening Highlights"
```

### View schedule for the day

```bash
make schedule-list STATUS=pending
```

### Cancel a post

```bash
# List posts to find ID
make schedule-list

# Cancel specific post
make schedule-remove ID=2
```

### Monitor scheduler

```bash
# In one terminal
make scheduler-run

# In another terminal
watch -n 5 'make schedule-status'
```

## Best Practices

1. **Test first**: Schedule posts a few minutes in the future to test the system
2. **Monitor initially**: Keep an eye on the scheduler logs for the first few posts
3. **Check authentication**: Ensure all platforms are authenticated before scheduling
4. **Use absolute paths**: Always use full paths for video files
5. **Grace period**: Keep the scheduler running or use cron to minimize missed posts
6. **Backup schedule**: Export your scheduled posts periodically
7. **Rate limits**: Be aware of platform rate limits (especially Instagram)

## Platform-Specific Notes

### YouTube
- No native rate limits for uploads
- Videos appear immediately after upload

### Instagram
- Rate limit: ~25 posts per day
- Videos must meet Instagram Reels requirements
- Processing time: 5-10 minutes

### TikTok
- Videos go to creator's inbox
- Must be manually published from TikTok app
- Processing time: 1-2 minutes

## Future Enhancements

Planned features for future releases:

- Web UI for scheduling management
- Calendar view of scheduled posts
- Recurring post schedules
- Optimal time suggestions based on analytics
- Bulk scheduling interface
- Email/SMS notifications for failures
- Platform-specific rate limit awareness



