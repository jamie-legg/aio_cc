# Watcher Panel - OBS Directory Display

## Implementation Complete ✅

The watcher panel now displays the watch directory and indicates when it was automatically detected from OBS!

## What Was Added

### 1. OBS Status in Watcher Service
Added new interface and method to fetch OBS status from the API:

```typescript
export interface OBSStatus {
  obs_running: boolean;
  obs_installed: boolean;
  config_dir: string | null;
  active_profile: string | null;
  replay_buffer_path: string | null;
  timestamp: string;
}

async getOBSStatus(): Promise<OBSStatus>
```

### 2. Watch Directory Display Section
Added a new section in the watcher panel between the header and search bar that shows:

- **Watch Directory Path**: Full path to the directory being monitored (with truncation)
- **OBS Auto-Detection Badge**: Green badge with "OBS Auto-Detected" when:
  - OBS is running
  - Replay buffer path was detected
  - Directory is actively being monitored

### 3. Visual Design

**Directory Info Section:**
```
┌─────────────────────────────────────────────┐
│ 📁 Watching  [🎥 OBS Auto-Detected]         │
│    C:\Users\Jamie\Videos                     │
└─────────────────────────────────────────────┘
```

**Features:**
- Semi-transparent dark background (`bg-gray-800/50`)
- Folder icon in blue
- Video icon for OBS badge (green)
- Green badge with border when OBS detected
- Monospace font for path (easier to read)
- Truncation with full path in tooltip on hover
- Only shows when OBS replay buffer is detected

### 4. Configuration File
Created `analytics-dashboard/src/config.ts` for centralized API configuration:

```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

## User Experience

### When OBS is Detected and Running:
```
┌────────────────────────────────────────────┐
│  🔄 Content Watcher     🟢 watching        │
├────────────────────────────────────────────┤
│ 📁 Watching  [🎥 OBS Auto-Detected]        │
│    C:\Users\Jamie\Videos                    │
├────────────────────────────────────────────┤
│  🔍 Search events...            🗑️         │
├────────────────────────────────────────────┤
│  [Activity Log]                            │
│                                            │
│  No activity yet                           │
│  Drop a video file to see activity         │
└────────────────────────────────────────────┘
```

### When OBS is Not Running (but path detected):
```
┌────────────────────────────────────────────┐
│  🔄 Content Watcher     ⚪ idle            │
├────────────────────────────────────────────┤
│ 📁 Watching                                │
│    C:\Users\Jamie\Videos                    │
├────────────────────────────────────────────┤
│  🔍 Search events...            🗑️         │
└────────────────────────────────────────────┘
```

### When No OBS Detected:
- Directory info section doesn't show
- Panel functions normally
- Uses manually configured watch directory

## Benefits

✅ **Transparency**: Users can see exactly what directory is being watched
✅ **Confirmation**: Green badge confirms OBS auto-detection is working
✅ **Debugging**: Makes it easy to verify the watcher is monitoring the right location
✅ **Status**: Combined with watcher status indicator, provides complete system overview

## Files Modified

1. **`analytics-dashboard/src/services/watcherService.ts`**
   - Added `OBSStatus` interface
   - Added `getOBSStatus()` method
   - Updated to use `API_BASE_URL` from config

2. **`analytics-dashboard/src/components/WatcherPanel.tsx`**
   - Added `obsStatus` state
   - Fetch OBS status on mount
   - Display directory info section with badge
   - Import additional icons (Folder, Video, CheckCircle)

3. **`analytics-dashboard/src/config.ts`** (created)
   - Centralized API configuration
   - Environment variable support

## API Integration

The panel fetches OBS status from:
```
GET http://localhost:8000/api/obs/status
```

Response:
```json
{
  "obs_running": true,
  "obs_installed": true,
  "config_dir": "C:\\Users\\Jamie\\AppData\\Roaming\\obs-studio",
  "active_profile": "Untitled",
  "replay_buffer_path": "C:\\Users\\Jamie\\Videos",
  "timestamp": "2025-10-17T12:34:56.789Z"
}
```

## Testing

1. **Start the API server** (with OBS detection):
   ```bash
   uv run python scripts/analytics/start_analytics.py
   ```

2. **Start the dashboard**:
   ```bash
   cd analytics-dashboard
   npm run dev
   ```

3. **Open the watcher panel**:
   - Click the eye icon in bottom-right
   - Panel expands showing watch directory
   - If OBS is running, green badge appears
   - Path is displayed in monospace font

4. **Test OBS detection**:
   - Start OBS → Badge appears
   - Stop OBS → Badge disappears (on next status refresh)
   - Hover over path → See full path in tooltip

## Future Enhancements

Possible improvements:
- [ ] Real-time OBS status updates (poll every 30s)
- [ ] Click path to open directory in file explorer
- [ ] Copy path to clipboard button
- [ ] Show OBS profile name
- [ ] Indicator when replay buffer is active
- [ ] Manual directory override UI

## Success!

The watcher panel now clearly shows:
- ✅ What directory is being watched
- ✅ Whether OBS auto-detection is active
- ✅ Current connection and watcher status
- ✅ Real-time activity feed

Users have complete visibility into the system! 🎯

