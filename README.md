# Content Creation - AI Video Clip Processor

An AI-powered tool that watches for new video files, automatically processes them for social media, and uploads to multiple platforms with engaging captions and metadata.

## Features

- **File Watching**: Monitors directories for new video files (`.mov`, `.mp4`, `.avi`, `.mkv`, `.webm`)
- **AI Caption Generation**: Uses OpenAI's GPT-4o-mini with structured JSON schema to create engaging titles, captions, and hashtags
- **Video Processing**: Automatically converts videos to 9:16 aspect ratio for YouTube Shorts
- **Audio Mixing**: Automatically adds background music and audio tracks to videos
- **Fade Effects**: Applies smooth fade in/out transitions to videos and audio
- **Multi-Platform Upload**: Uploads to Instagram Reels, YouTube Shorts, and TikTok
- **FTP Video Hosting**: Uses MinIO FTP server for reliable video hosting
- **OAuth Authentication**: Secure authentication with all major social media platforms
- **CLI Management**: Command-line tools for authentication, testing, and configuration
- **Modular Architecture**: Clean separation of platform-specific upload logic for easy maintenance and extension

## Installation

This project uses `uv` for dependency management. Make sure you have `uv` installed:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install the project dependencies:

```bash
uv sync
```

### Windows Quick Setup

For Windows users, we provide automated setup scripts:

```cmd
# Run the batch file (Command Prompt)
setup_windows.bat

# Or run the PowerShell script
powershell -ExecutionPolicy Bypass -File setup_windows.ps1
```

These scripts will:
- Check for Python and install `uv` if needed
- Install all project dependencies
- Verify FFmpeg installation
- Create `.env` file from template
- Set up default directories

Install FFmpeg for video processing:

```bash
# macOS (using Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg

# Windows (using winget)
winget install ffmpeg

# Windows (manual installation)
# 1. Download FFmpeg from https://ffmpeg.org/download.html
# 2. Extract to C:\ffmpeg
# 3. Add C:\ffmpeg\bin to your PATH environment variable
```

## Setup

1. Copy the environment template and configure your API keys:
   ```bash
   # macOS/Linux
   cp env.example .env
   
   # Windows (Command Prompt)
   copy env.example .env
   
   # Windows (PowerShell)
   Copy-Item env.example .env
   
   # Edit .env with your API credentials
   ```

2. Set up ngrok for OAuth callbacks:
   - Sign up for a free account at [ngrok](https://dashboard.ngrok.com/signup)
   - Get your auth token from [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
   - Add `NGROK_AUTH_TOKEN=your_token_here` to your `.env` file

3. Set up your social media API credentials:
   - **OpenAI**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Instagram**: Create an app at [Facebook Developers](https://developers.facebook.com/) (redirect URI will be set dynamically)
   - **YouTube**: Create a project and enable YouTube Data API v3 in [Google Cloud Console](https://console.cloud.google.com/)
   - **TikTok**: Apply for access at [TikTok for Developers](https://developers.tiktok.com/) (redirect URI will be set dynamically)

4. Set up FTP server for video hosting (MinIO):
   - **FTP_URL**: Your MinIO server endpoint
   - **FTP_ACCESS_KEY**: Your MinIO access key
   - **FTP_SECRET_KEY**: Your MinIO secret key
   - **FTP_BUCKET**: Bucket name for video storage

5. Authenticate with social media platforms:
   ```bash
   # Authenticate with all platforms
   uv run content-cli auth all
   
   # Or authenticate individually
   uv run content-cli auth instagram
   uv run content-cli auth youtube
   uv run content-cli auth tiktok
   ```

6. Set up audio tracks (optional):
   ```bash
   # Create audio directory
   mkdir audio
   
   # Add default background music
   cp your_music.mp3 audio/default.mp3
   
   # Or add specific tracks for videos
   cp track1.mp3 audio/Replay_2025-10-07_10-31-10.mp3
   ```

7. Configure your watch directory:
   ```bash
   # macOS/Linux
   uv run content-cli config set-watch-dir ~/Movies
   uv run content-cli config set-processed-dir ~/Movies/Processed
   
   # Windows
   uv run content-cli config set-watch-dir C:\Users\%USERNAME%\Videos
   uv run content-cli config set-processed-dir C:\Users\%USERNAME%\Videos\Processed
   ```

## Usage

### Running the Clip Watcher

```bash
# Using uv
uv run python main.py

# Or using the installed script
uv run clip-watcher
```

The tool will:
1. Watch for new video files in your configured directory
2. **Process videos for social media**:
   - Convert to 9:16 aspect ratio for YouTube Shorts
   - Add background music (if available)
   - Apply fade in/out effects
3. **Generate AI captions and metadata**:
   - Create engaging titles with emojis
   - Write Gen Z-style captions
   - Generate relevant hashtags
4. Save metadata as JSON files
5. Move processed videos to the processed directory
6. Upload videos to configured social media platforms

### CLI Management

Check authentication status:
```bash
uv run content-cli check all
```

Test upload functionality:
```bash
uv run content-cli test --video path/to/your/video.mov --platform all
```

Test video processing:
```bash
# Test basic video processing
uv run python test_video_processor.py

# Test audio processing and fade effects
uv run python test_audio_processing.py

# Test AI metadata generation
uv run python test_ai_manager.py
```

### Configuration Management

Show current configuration:
```bash
uv run content-cli config show
```

Set watch directory (where videos are monitored):
```bash
uv run content-cli config set-watch-dir /path/to/your/videos
```

Set processed directory (where completed videos are saved):
```bash
uv run content-cli config set-processed-dir /path/to/processed/videos
```

Set video file extensions to watch for:
```bash
uv run content-cli config set-extensions mov,mp4,avi,mkv
```

Enable/disable upload to specific platforms:
```bash
uv run content-cli config toggle-platform instagram enable
uv run content-cli config toggle-platform tiktok disable
```

Validate configuration:
```bash
uv run content-cli config validate
```

Reset to defaults:
```bash
uv run content-cli config reset
```

### Configuration

The tool now supports flexible configuration through the CLI. You can:

1. **Use CLI commands** (recommended):
   ```bash
   uv run content-cli config set-watch-dir ~/Videos
   uv run content-cli config set-processed-dir ~/Videos/Processed
   uv run content-cli config toggle-platform instagram enable
   ```

2. **Use environment variables** (legacy):
   ```bash
   UPLOAD_TO_INSTAGRAM=true
   UPLOAD_TO_YOUTUBE=true
   UPLOAD_TO_TIKTOK=false
   ```

Configuration is stored in `~/.content_creation/config.json` and takes precedence over environment variables.

## Architecture

The project follows a modular architecture with clear separation of concerns:

### Core Components
- **`UploadManager`**: Main coordinator that orchestrates uploads across platforms
- **`FTPUploader`**: Handles video hosting via MinIO/S3-compatible storage
- **`AIManager`**: Generates engaging metadata using OpenAI
- **`VideoProcessor`**: Handles video processing for social media requirements
- **`OAuthManager`**: Manages authentication for all social media platforms
- **`ConfigManager`**: Handles application configuration and settings
- **`NgrokManager`**: Manages ngrok tunnels for OAuth callbacks

### Platform Uploaders
Each social media platform has its own dedicated uploader module:
- **`InstagramUploader`**: Handles Instagram Reels uploads via Graph API
- **`YouTubeUploader`**: Manages YouTube Shorts uploads with retry logic
- **`TikTokUploader`**: Processes TikTok uploads via Content Posting API

### Folder Organization
- **`content_creation/`**: Core application logic and main entry points
- **`managers/`**: Centralized manager modules for different aspects of the system
- **`platform_uploaders/`**: Platform-specific upload implementations

### Benefits
- **Maintainability**: Platform-specific logic is isolated and easy to modify
- **Extensibility**: Adding new platforms requires only creating a new uploader module
- **Testability**: Each component can be tested independently
- **Reusability**: Uploaders can be used independently of the main manager
- **Organization**: Clear separation between core logic, managers, and platform-specific code

## Project Structure

```
content-creation/
├── src/
│   ├── content_creation/       # Core application logic
│   │   ├── __init__.py
│   │   ├── clip_watcher.py     # Main file watcher and processor
│   │   ├── types.py            # Common types and FTP uploader
│   │   ├── video_processor.py  # Video processing and audio mixing
│   │   ├── callback_server.py  # OAuth callback server
│   │   └── cli.py             # Command-line interface
│   ├── managers/              # Core manager modules
│   │   ├── ai_manager.py       # AI-powered metadata generation
│   │   ├── config_manager.py   # Configuration management
│   │   ├── ngrok_manager.py    # Ngrok tunnel management
│   │   ├── oauth_manager.py    # OAuth authentication for social platforms
│   │   └── upload_manager.py   # Main upload coordinator
│   └── platform_uploaders/    # Platform-specific upload modules
│       ├── __init__.py
│       ├── instagram.py        # Instagram Reels uploader
│       ├── youtube.py          # YouTube Shorts uploader
│       └── tiktok.py           # TikTok uploader
├── audio/                     # Audio tracks directory
│   ├── README.md             # Audio setup instructions
│   ├── default.mp3           # Default background music
│   └── *.mp3                 # Video-specific audio tracks
├── main.py                    # Entry point
├── pyproject.toml            # Project configuration
├── env.example              # Environment variables template
├── test_*.py                # Test scripts
└── README.md
```

## Important Notes

### Instagram Limitations
- Instagram Basic Display API doesn't support video uploads
- For video uploads, you need Instagram Graph API with a business account
- The current implementation shows this limitation

### YouTube Requirements
- Requires a YouTube channel
- Videos are uploaded as public by default
- Uses YouTube Data API v3
- **Video Processing**: Automatically converts to 9:16 aspect ratio for Shorts
- **Duration**: Maximum 3 minutes for Shorts
- **Format**: MP4, MOV, AVI, MKV, WebM

### TikTok Requirements
- Requires TikTok for Developers account approval
- Videos are uploaded to your TikTok inbox for review and posting
- **Supported formats**: MP4, MOV, AVI, 3GP
- **Maximum file size**: 4GB
- **Maximum duration**: 10 minutes
- **Recommended**: H.264 codec, 1080p resolution
- Uses TikTok for Developers API

## Audio Processing

### Audio Track Setup
The system automatically looks for audio tracks in the following order:

1. **Video-specific tracks**: `audio/Replay_2025-10-07_10-31-10.mp3`
2. **Default tracks**: `audio/default.mp3`, `audio/background.mp3`, `audio/music.mp3`
3. **No audio**: Videos are processed without additional audio

### Supported Audio Formats
- MP3, WAV, AAC, M4A, OGG

### Fade Effects
- **Configurable duration**: Default 1 second fade in/out
- **Smart timing**: Fade duration is limited to half the video duration
- **Both video and audio**: Fade effects are applied to both video and audio tracks

## Troubleshooting

### Authentication Issues
- Make sure all API credentials are correctly set in `.env`
- Check that redirect URIs match your app settings
- Ensure you have the necessary permissions for each platform

### Upload Failures
- Check your internet connection
- Verify video file format is supported by each platform
- Ensure you have sufficient storage/quota on each platform

### Video Processing Issues
- **FFmpeg not found**: Install FFmpeg using the instructions above
- **Audio mixing fails**: Check that audio files are in supported formats
- **Aspect ratio issues**: The system automatically handles 9:16 conversion

### FTP Server Issues
- Verify FTP credentials in `.env`
- Check that the FTP server is accessible
- Ensure the bucket exists and has proper permissions

### Windows-Specific Issues
- **Path issues**: Use forward slashes (/) or raw strings (r"C:\path") in Python
- **FFmpeg not found**: Ensure FFmpeg is in your PATH or use full path to ffmpeg.exe
- **Permission errors**: Run Command Prompt as Administrator if needed
- **File watching**: The tool uses pathlib for better Windows compatibility
- **Environment variables**: Use `set` command in Command Prompt or `$env:` in PowerShell
- **Long paths**: Enable long path support in Windows 10/11 if you encounter path length issues

## Security

### Important Security Notes
- **Never commit credentials**: All API keys and secrets should be stored in `.env` file only
- **Use environment variables**: Never hardcode credentials in source code
- **Keep .env private**: Add `.env` to `.gitignore` (already included)
- **Rotate credentials**: Regularly update your API keys and secrets
- **Use least privilege**: Only grant necessary permissions to your API keys

### Required Environment Variables
Make sure to set all required environment variables in your `.env` file:
- `OPENAI_API_KEY`
- `NGROK_AUTH_TOKEN`
- `INSTAGRAM_CLIENT_ID` & `INSTAGRAM_CLIENT_SECRET`
- `YOUTUBE_CLIENT_ID` & `YOUTUBE_CLIENT_SECRET`
- `TIKTOK_CLIENT_KEY` & `TIKTOK_CLIENT_SECRET`
- `FTP_URL`, `FTP_ACCESS_KEY`, `FTP_SECRET_KEY`, `FTP_BUCKET`
