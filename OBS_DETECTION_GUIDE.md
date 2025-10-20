# OBS Studio Auto-Detection Guide

## Overview

The content watcher now automatically detects OBS Studio and finds your replay buffer output directory! No more manual configuration needed.

## How It Works

When you start the watcher (`uv run python main.py`), it will:

1. **Detect OBS Installation**: Scans your system for OBS Studio configuration
2. **Find Active Profile**: Identifies which OBS profile you're currently using
3. **Locate Replay Buffer**: Reads your OBS config to find where replay files are saved
4. **Auto-Configure**: Automatically sets this as your watch directory

## Features

### ✅ Cross-Platform Support
- **Windows**: `%APPDATA%\obs-studio`
- **macOS**: `~/Library/Application Support/obs-studio`
- **Linux**: `~/.config/obs-studio`

### ✅ OBS Process Detection
- Checks if OBS is currently running
- Shows status in watcher startup logs

### ✅ Replay Buffer Path Detection
- Reads from `basic.ini` in your active profile
- Supports both Simple and Advanced output modes
- Handles environment variables in paths

### ✅ Auto-Configuration
- Automatically updates `config.json` with the correct path
- Only updates if current watch directory doesn't exist or is default

## OBS Configuration Requirements

For auto-detection to work, you need to configure OBS replay buffer:

### Option 1: Simple Output Mode
1. Open OBS Studio
2. Go to **Settings** → **Output**
3. Make sure **Output Mode** is set to **Simple**
4. Set your **Recording Path** (e.g., `C:\Users\YourName\Videos`)
5. Click **OK**

### Option 2: Advanced Output Mode
1. Open OBS Studio
2. Go to **Settings** → **Output**
3. Set **Output Mode** to **Advanced**
4. Go to **Recording** tab
5. Set **Recording Path** (e.g., `C:\Users\YourName\Videos`)
6. Click **OK**

### Enable Replay Buffer
1. In OBS, go to **Settings** → **Output**
2. Enable **Replay Buffer**
3. Set duration (e.g., 30 seconds)
4. Click **OK**
5. Start the replay buffer from OBS main window

## Testing OBS Detection

Run the test script to check if OBS is properly detected:

```bash
uv run python scripts/test_obs_detection.py
```

This will show:
- ✓ OBS Running status
- ✓ OBS Installed status
- ✓ Config directory location
- ✓ Active profile name
- ✓ Replay buffer path

Example output:
```
🎬 OBS Studio Detection
==================================================
OBS Running: ✓ Yes
OBS Installed: ✓ Yes
Config Directory: C:\Users\Jamie\AppData\Roaming\obs-studio
Active Profile: Untitled

✓ Replay Buffer Directory Found:
  C:\Users\Jamie\Videos

==================================================
```

## Viewing OBS Status in the Dashboard

The OBS status is also available via the API:

```bash
curl http://localhost:8000/api/obs/status
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

## Manual Override

If auto-detection doesn't work or you want to use a different directory:

1. Edit `config.json` in your project root
2. Set `watch_dir` to your desired path
3. Restart the watcher

The auto-detection will **not** override a manually configured path that exists.

## Troubleshooting

### OBS Not Detected
- Make sure OBS Studio is installed
- Check if OBS config exists at the expected location
- Run `test_obs_detection.py` to see detailed info

### Replay Buffer Path Not Found
- Open OBS and configure recording path in Settings → Output
- Make sure you have a profile selected in OBS
- Check that the path exists and is accessible

### Path Detected But Not Working
- Verify the path has write permissions
- Check if the directory exists
- Make sure OBS is saving files to this location

### Auto-Configuration Not Applying
- The watcher only auto-configures if:
  - Current watch directory doesn't exist, OR
  - Current watch directory is "." or "clips" (default)
- To force re-detection, delete or rename your `config.json`

## Startup Log Example

When you run the watcher, you'll see OBS detection info:

```
============================================================
CONTENT CREATION CLIP WATCHER - STARTUP
============================================================

[ENABLED PLATFORMS]
  Instagram: [ENABLED] [AUTHENTICATED]
  YouTube: [ENABLED] [AUTHENTICATED]
  TikTok: [ENABLED] [AUTHENTICATED]

[OBS STUDIO DETECTION]
  OBS Running: ✓ Yes
  OBS Installed: ✓ Yes
  Replay Buffer: C:\Users\Jamie\Videos

[DIRECTORY STATUS]
  Watch Directory: [EXISTS]
  Processed Directory: [EXISTS]
  Video files in watch directory: 0

============================================================
👀 Watching for new video files...
```

## Benefits

- **Zero Configuration**: Works out of the box if you have OBS
- **Always In Sync**: Uses whatever path OBS is configured to use
- **Multi-Profile Support**: Automatically detects your active profile
- **Cross-Platform**: Works on Windows, macOS, and Linux

## API Integration

Frontend developers can fetch OBS status:

```typescript
const response = await fetch('http://localhost:8000/api/obs/status');
const obsInfo = await response.json();

if (obsInfo.replay_buffer_path) {
  console.log('Watching:', obsInfo.replay_buffer_path);
}
```

This allows the dashboard to show:
- Real-time OBS status
- Current watch directory
- Connection indicators

## Next Steps

1. **Test it**: Run `uv run python scripts/test_obs_detection.py`
2. **Configure OBS**: Set your replay buffer path in OBS Settings
3. **Start Watcher**: Run `uv run python main.py`
4. **Save Replay**: Hit your OBS replay buffer hotkey
5. **Watch Magic**: The watcher automatically processes and uploads!

No more wondering which directory to watch - the system finds it for you! 🎬

