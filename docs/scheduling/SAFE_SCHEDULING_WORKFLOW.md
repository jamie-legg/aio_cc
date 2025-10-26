# Safe Scheduling Workflow - Using Missed Replays

## System Status: CLEARED AND SAFE

- Scheduled posts: 0 (all cancelled)
- Failed uploads: 0 (all cleared)
- Ready to schedule videos properly using the dashboard

## How to Safely Schedule Videos

### Step 1: Start the Services

```powershell
make start
```

This starts:
- Watcher (monitors your video folder for NEW videos)
- API Server (backend for dashboard)
- Scheduler Daemon (posts videos at their scheduled time)
- Dashboard (web interface at http://localhost:5173)

### Step 2: Open the Dashboard

The dashboard will automatically open, or visit: **http://localhost:5173/uploads**

### Step 3: Use the "Missed Replays" Section

The "Missed Replays" section shows videos that are ready to be scheduled but haven't been posted yet.

#### Option A: Schedule Individual Videos

For each video in the Missed Replays section:

1. **Schedule Next** - Schedules for the next available slot (1 hour from now, or 1 hour after the last scheduled video)

2. **Pick Time** - Opens a date/time picker to choose when you want it posted
   - Select any future date and time
   - Click "Schedule"
   - Video appears in "Scheduled Uploads" section above

#### Option B: Schedule Multiple Videos (Recommended)

1. **Check the boxes** next to videos you want to schedule
2. Click **"Select All"** to select all videos at once (if desired)
3. Click **"Schedule Selected"** button
4. You'll see a confirmation: "Schedule X video(s)? They will be spaced 1 hour apart."
5. Click OK to confirm
6. All selected videos are scheduled, spaced 1 hour apart starting from now

### Step 4: Review Scheduled Posts

After scheduling, videos appear in the **"Scheduled Uploads"** section at the top:

- See the scheduled time for each video
- See countdown ("in Xh Ym")
- See which platforms each will post to
- Can **Cancel** any post you don't want
- Can **Post Now** to force immediate posting

### Step 5: Let the Scheduler Run

Once videos are scheduled:
- The scheduler daemon (already running from `make start`) checks every 60 seconds
- When a video's scheduled time arrives, it posts automatically
- You can see posting progress in the terminal where you ran `make start`
- Dashboard updates in real-time

## Important: What Happens With New Videos

When you drop a new video in your watch folder:

1. Watcher detects it
2. Video is processed (watermark, outro, AI metadata)
3. **AUTOMATICALLY SCHEDULED** for next available slot (because AUTO_SCHEDULE=true)
4. Appears in "Scheduled Uploads" section
5. Posts at its scheduled time

If you DON'T want automatic scheduling for new videos:
```bash
# In .env file (create if doesn't exist)
AUTO_SCHEDULE=false
```
Then restart with `make start`

## Safety Features

### 1. Confirmation Dialogs
- "Schedule Selected" asks for confirmation before scheduling multiple videos
- "Post Now" asks for confirmation before immediate posting
- "Cancel" asks for confirmation before removing from schedule

### 2. No Surprise Posting
- With the system cleared, nothing will post until YOU schedule it from "Missed Replays"
- Scheduled times are clearly visible
- Countdowns show exactly when each video will post

### 3. Full Control
- Cancel scheduled posts anytime before they post
- Change scheduled times by canceling and re-scheduling
- Stop the scheduler daemon (Ctrl+C) to prevent any posting

## Recommended Workflow

### Daily Posting Schedule

Example: Schedule 3 videos per day

1. Open dashboard: http://localhost:5173/uploads
2. Go to "Missed Replays" section
3. Select 3 videos
4. Click "Schedule Selected"
5. Videos schedule for: Now+1h, Now+2h, Now+3h
6. Repeat tomorrow for the next 3 videos

### Weekly Planning

Example: Schedule a week of content

1. Open dashboard
2. Select first video
3. Click "Pick Time"
4. Choose Monday 9:00 AM
5. Repeat for other videos:
   - Monday 9 AM, 2 PM, 7 PM
   - Tuesday 9 AM, 2 PM, 7 PM
   - Wednesday 9 AM, 2 PM, 7 PM
   - etc.

### Bulk Scheduling

Example: Schedule all available videos

1. Go to "Missed Replays"
2. Click "Select All" checkbox
3. Click "Schedule Selected"
4. Confirm the dialog
5. All videos scheduled 1 hour apart starting now

## Troubleshooting

### Dashboard shows "No missed replays"

This is actually good! It means:
- All videos have already been scheduled or posted
- No unprocessed videos in your watch folder
- System is clean and ready for new content

### Scheduled posts not appearing

1. Check you clicked "Schedule" or "Schedule Selected"
2. Check for error messages in the dashboard
3. Refresh the page
4. Check terminal output where you ran `make start`

### Videos posting immediately when I start

This means there were old scheduled posts with past-due dates. To prevent this:
1. Stop services (Ctrl+C)
2. Run: `python clear_and_start_fresh.py`
3. Start services: `make start`
4. Use "Missed Replays" to schedule properly

### Want to stop all posting

1. In terminal where `make start` is running, press Ctrl+C
2. All services stop
3. Scheduled posts remain in database
4. They'll resume when you run `make start` again

## Platform Notes

### Instagram
- Limit: ~25 posts per day
- Space videos at least 1 hour apart
- Processing time: 5-10 minutes after scheduled time

### YouTube
- No daily limit
- Videos go live immediately
- Processing time: 1-2 minutes after scheduled time

### TikTok
- No strict daily limit
- Videos go to creator inbox (must publish manually from TikTok app)
- Processing time: 1-2 minutes after scheduled time

## Quick Reference

| Action | Steps |
|--------|-------|
| Schedule 1 video | Missed Replays → Pick Time → Select date/time → Schedule |
| Schedule multiple | Missed Replays → Check boxes → Schedule Selected |
| Schedule all | Missed Replays → Select All → Schedule Selected |
| Cancel scheduled | Scheduled Uploads → Find video → Cancel |
| Force post now | Scheduled Uploads → Find video → Post Now |
| Clear system | `python clear_and_start_fresh.py` |
| Start services | `make start` |
| Stop services | Press Ctrl+C in terminal |

## Summary

**You're now safe!** The system is cleared and ready. When you start with `make start`:

1. No old posts will go out
2. Only videos you manually schedule from "Missed Replays" will post
3. You have full control via the dashboard
4. New videos from watch folder will auto-schedule (can disable this)

**Key Tip:** Always use the "Missed Replays" section to schedule videos with proper timing!




