# Safe Scheduling Guide

## ✅ Your Current Setup is SAFE

- **AUTO_SCHEDULE: Enabled** - New videos are scheduled, not posted immediately
- **Scheduler Daemon: Stopped** - Scheduled posts won't go out until you start it
- **10 posts currently scheduled** - Review them before starting the daemon

## How to Safely Schedule Videos

### Method 1: Using the Dashboard (Recommended)

1. **Open the dashboard:**
   ```powershell
   python open_dashboard.py
   ```
   Or visit: http://localhost:5173/uploads

2. **Review Scheduled Posts** (top section)
   - See what's already queued
   - Check scheduled times and countdowns
   - Cancel anything you don't want

3. **Schedule Missed Replays** (bottom section)
   - These are videos that weren't processed while the watcher was down
   - Options:
     - **Schedule Next**: Adds to next available slot (1 hour from last post)
     - **Pick Time**: Choose exact date/time
     - **Select Multiple**: Check boxes and use "Schedule Selected"
       - They'll be spaced 1 hour apart automatically
       - You'll get a confirmation dialog before scheduling

### Method 2: When Watcher Detects New Videos

When you drop a new video in your watch folder:
1. Video is processed (watermark, outro, AI metadata)
2. **Automatically scheduled** for next available time slot
3. Appears in dashboard's "Scheduled Uploads" section
4. **Will NOT post until scheduler daemon is running**

## Starting the Scheduler Daemon

### ⚠️ IMPORTANT: Only start this when you're ready for posts to go out!

```powershell
# Option 1: Use the safety script
.\start_scheduler.ps1

# Option 2: Run directly
python -m src.scheduling.scheduler_daemon
```

The daemon:
- Checks every 60 seconds for due posts
- Posts videos when their scheduled time arrives
- Handles retries for failed uploads
- Runs until you press Ctrl+C

### Stopping the Scheduler

Press `Ctrl+C` at any time to stop the scheduler daemon. Posts remain scheduled and won't be posted until you start it again.

## Understanding the Scheduling System

### How Videos Are Spaced

- **1 hour apart** by default (configurable)
- Each platform gets its own slot
- No overlapping posts on the same platform
- Next available slot calculation prevents conflicts

### Example Timeline

```
Now:     2:00 PM
Video 1: 3:00 PM (Instagram, YouTube, TikTok)
Video 2: 4:00 PM (Instagram, YouTube, TikTok)
Video 3: 5:00 PM (Instagram, YouTube, TikTok)
```

### Picking Custom Times

From the dashboard:
1. Find video in "Missed Replays" section
2. Click "Pick Time" button
3. Select date and time
4. Click "Schedule"
5. Video appears in "Scheduled Uploads"

### Force Posting

If you need to post a scheduled video immediately:
1. Go to "Scheduled Uploads" section
2. Find the video
3. Click "Post Now"
4. Confirm the dialog
5. Video posts immediately (bypasses schedule)

## Safety Features

### 1. Confirmation Dialogs
- Batch scheduling asks for confirmation
- Shows how many videos will be scheduled
- Shows spacing (1 hour apart)

### 2. Visual Feedback
- Scheduled time displayed clearly
- Countdown shows "in Xh Ym"
- Status badges show pending/processing/completed/failed

### 3. Cancellation
- Cancel scheduled posts anytime before they're processed
- Click "Cancel" button
- Confirm dialog
- Post removed from schedule

### 4. Failed Upload Handling
- Failed uploads appear in "Failed Uploads" section
- Retry individual uploads
- Retry all failed uploads
- Remove from queue if you don't want to retry

## Configuration

### Adjust Scheduling Behavior

Edit your `.env` file or set environment variables:

```bash
# Enable/disable auto-scheduling
AUTO_SCHEDULE=true              # true = schedule, false = immediate upload

# Spacing between posts on same platform (hours)
SCHEDULE_SPACING_HOURS=1        # Default: 1 hour

# Hours after processing to schedule first post
DEFAULT_POST_TIME_OFFSET=1      # Default: 1 hour
```

Then restart the watcher:
```powershell
# Stop the watcher (Ctrl+C)
# Restart it
python -m src.content_creation.clip_watcher
```

### Change Spacing Example

Want 2 hours between posts instead of 1?

```bash
# In .env
SCHEDULE_SPACING_HOURS=2
```

## Best Practices

### ✅ DO:

- Review scheduled posts before starting the daemon
- Use the dashboard to visualize your schedule
- Cancel posts you're not happy with
- Test with 1-2 videos first
- Check authentication status for all platforms
- Keep the scheduler daemon running (once you're ready)

### ❌ DON'T:

- Start the scheduler daemon without reviewing scheduled posts
- Schedule more posts than platform limits allow (Instagram: ~25/day)
- Schedule posts more than a few days out (in case you need to make changes)
- Close the scheduler daemon terminal if you want posts to go out

## Platform Limits

### Instagram
- **~25 posts per day** recommended
- Space them out (every 1-2 hours)
- Processing takes 5-10 minutes

### YouTube
- No daily limit for uploads
- Videos go live immediately
- Processing takes 1-2 minutes

### TikTok
- No strict daily limit
- Videos go to creator's inbox
- Must be manually published from TikTok app
- Processing takes 1-2 minutes

## Monitoring

### View Scheduled Posts
```powershell
# From Python
python -c "from src.analytics.database import AnalyticsDatabase; db = AnalyticsDatabase('analytics.db'); posts = db.get_pending_posts(); print(f'Scheduled: {len(posts)}'); [print(f'  - {p.metadata_json[:50]}... at {p.scheduled_time}') for p in posts[:5]]"
```

### Check Scheduler Status
Look at the terminal where scheduler daemon is running:
- Shows when checking for posts
- Shows when posting videos
- Shows success/failure for each platform

### Dashboard
The dashboard updates every 30 seconds automatically:
- Countdowns tick down in real-time
- New posts appear automatically
- Status changes reflect immediately

## Troubleshooting

### Videos not posting at scheduled time
1. Check scheduler daemon is running
2. Check terminal for errors
3. Verify video file still exists
4. Check platform authentication

### "Schedule Selected" posts all immediately
This shouldn't happen with AUTO_SCHEDULE=true. If it does:
1. Check your configuration: `AUTO_SCHEDULE=true` in .env
2. Restart the watcher
3. Check the dashboard again

### Want to stop all scheduled posts
1. Stop the scheduler daemon (Ctrl+C)
2. Go to dashboard
3. Cancel posts one by one
4. Or clear from database:
   ```powershell
   python -c "from src.analytics.database import AnalyticsDatabase; db = AnalyticsDatabase('analytics.db'); [db.update_post_status(p.id, 'cancelled') for p in db.get_pending_posts()]"
   ```

### Change scheduled time for a post
Currently, you need to:
1. Cancel the existing scheduled post
2. Re-schedule with new time using "Pick Time"

## Summary

✅ **You're safe!** AUTO_SCHEDULE is enabled  
✅ **Scheduler daemon is stopped** - nothing will post until you start it  
✅ **10 posts are scheduled** - review them first  
✅ **Dashboard gives full control** - cancel, reschedule, or force post  

When you're ready:
1. Open dashboard and review scheduled posts
2. Adjust as needed
3. Run `.\start_scheduler.ps1` when ready for posts to go out
4. Monitor the terminal and dashboard

**Remember:** You can stop the scheduler daemon anytime with Ctrl+C!


