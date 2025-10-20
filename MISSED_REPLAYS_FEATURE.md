# Missed Replays Feature

## Overview

The Missed Replays feature allows you to detect, process, and schedule videos that were saved while the watcher was not running. This ensures you never lose content even if the system was down when replays were saved.

## Features

### 1. Automatic Detection
- Scans the watch directory for unprocessed videos
- Filters out videos that are already processed or scheduled
- Shows file size and modification time
- Auto-refreshes every 30 seconds

### 2. Individual Scheduling
- **Schedule Next**: Automatically finds the next available time slot
- **Pick Time**: Manually select a specific date and time
- Both options process the video with AI metadata, watermark, and outro

### 3. Batch Scheduling
- Select multiple videos with checkboxes
- "Schedule Selected" button schedules all at once
- Videos are automatically spaced 1 hour apart
- Shows progress and success/failure counts

### 4. Visual Indicators
- Yellow stat card shows missed replay count
- Selected videos highlight in blue
- Disabled states during processing
- Success/error messages for all operations

## How It Works

### Backend (Python)

**Database Method**: `get_all_scheduled_posts()`
- Returns all scheduled posts regardless of status
- Used to check if a video is already scheduled

**API Endpoints**:
1. `GET /api/missed-replays` - Lists unprocessed videos
2. `POST /api/schedule-replay` - Schedules a single video
3. `POST /api/schedule-replays-batch` - Schedules multiple videos

**Processing Logic**:
- Reuses `process_video_for_scheduling()` from clip_watcher
- Generates AI metadata (title, caption, hashtags)
- Processes video (watermark, outro, shorts formatting)
- Moves to processed directory
- Adds to scheduled_posts table

### Frontend (React/TypeScript)

**New Component**: Missed Replays section in UploadsPage
- Located after Failed Uploads section
- Shows list of unprocessed videos
- Checkbox selection for batch operations
- Two scheduling buttons per video
- DateTime picker modal for manual scheduling

**API Service**: `missedReplaysApi.ts`
- `getMissedReplays()` - Fetch list
- `scheduleReplay()` - Schedule one
- `scheduleBatch()` - Schedule multiple

## Usage

### Accessing the Feature

1. Start the services: `make start`
2. Open dashboard: http://localhost:5173/dashboard
3. Navigate to **Uploads** page
4. Scroll down to **Missed Replays** section

### Scheduling Individual Videos

**Option A - Auto Schedule (Recommended)**:
1. Click "Schedule Next" button
2. System finds next available time slot
3. Video is processed and scheduled automatically

**Option B - Manual Time**:
1. Click "Pick Time" button
2. Select desired date and time in modal
3. Click "Schedule" button
4. Video is scheduled for that specific time

### Scheduling Multiple Videos

1. Check the boxes next to videos you want to schedule
2. Or click "Select All" to select all at once
3. Click "Schedule Selected" button in header
4. Confirm the operation
5. Videos are scheduled 1 hour apart starting from next available slot

### Monitoring

- **Stats Card**: Shows total count of missed replays
- **Selection Count**: Shows how many videos are selected
- **Progress Indicator**: Buttons disable during processing
- **Success Messages**: Confirms when scheduling completes
- **Scheduled Posts**: New posts appear in "Scheduled Uploads" section

## Technical Details

### File Detection Logic

Videos are considered "missed" if they:
- Exist in the watch directory
- Have a valid video extension (.mp4, .mkv, .flv, .avi, .mov)
- Are NOT in the processed directory
- Are NOT already scheduled (checked by filename and full path)

### Processing Pipeline

1. **Video Analysis**: Check duration and aspect ratio
2. **AI Generation**: Create metadata using active prompt template
3. **Video Processing**: Apply watermark, outro, fade effects
4. **Metadata Storage**: Save JSON file with AI-generated content
5. **File Management**: Move original to processed directory
6. **Database Entry**: Add to scheduled_posts table

### Time Slot Management

- **Auto Scheduling**: Uses `get_next_slot()` to find next free hour
- **Batch Scheduling**: Uses `space_videos()` to space posts 1 hour apart
- **Manual Scheduling**: Accepts any datetime, rounds to nearest hour
- **Conflict Prevention**: Checks existing posts to avoid double-booking

## Error Handling

- File not found errors show in results
- Processing errors don't stop batch operations
- Network errors show error messages
- Failed videos can be retried individually
- All errors are logged for debugging

## Integration Points

### With Existing Features

- **Watcher**: Missed replays complement automatic detection
- **Scheduler**: Uses same scheduling system
- **AI Manager**: Uses same metadata generation
- **Video Processor**: Uses same processing pipeline
- **Upload Manager**: Scheduled posts use same upload logic

### Database

- Uses `scheduled_posts` table
- Same structure as watcher-created posts
- Visible in all scheduling queries
- Tracked by scheduler daemon

## Future Enhancements

Possible improvements:
- Metadata preview/editing before scheduling
- Bulk time picker (schedule all at custom intervals)
- Filter by date range or file size
- Sort options (name, date, size)
- Thumbnail previews
- Video preview player
- Custom game context per video

## Troubleshooting

**No missed replays showing?**
- Check watch directory path in settings
- Verify videos have valid extensions
- Ensure videos aren't already processed or scheduled

**Scheduling fails?**
- Check platform authentication
- Verify FFmpeg is installed
- Check asset files (watermark, outro) exist
- Review API server logs for errors

**Videos not uploading?**
- Ensure scheduler daemon is running (`make start`)
- Check scheduled posts status in dashboard
- Review failed uploads section for errors
- Verify platform credentials are still valid

## Files Modified

```
Backend:
- src/analytics/database.py (added get_all_scheduled_posts)
- src/content_creation/clip_watcher.py (extracted process_video_for_scheduling)
- src/analytics/api_server.py (added 3 endpoints + helper)

Frontend:
- analytics-dashboard/src/services/missedReplaysApi.ts (new API client)
- analytics-dashboard/src/pages/UploadsPage.tsx (added Missed Replays section)
```

## Summary

The Missed Replays feature provides a robust solution for handling videos that accumulated while the watcher was down. It seamlessly integrates with existing systems and provides both automatic and manual scheduling options, with batch operations for efficiency.


