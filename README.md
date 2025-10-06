# Content Creation - AI Video Clip Processor

An AI-powered tool that watches for new video files and automatically generates engaging social media captions and metadata.

## Features

- **File Watching**: Monitors the `~/Movies` directory for new `.mov` files
- **AI Caption Generation**: Uses OpenAI's GPT-4o-mini to create engaging titles, captions, and hashtags
- **Automatic Processing**: Moves processed files to a `Processed` folder with metadata
- **File Stability Detection**: Waits for files to finish writing before processing
- **Multi-Platform Upload**: Automatically uploads videos to Instagram Reels, YouTube Shorts, and TikTok
- **OAuth Authentication**: Secure authentication with all major social media platforms
- **CLI Management**: Command-line tools for authentication and testing

## Installation

This project uses `uv` for dependency management. Make sure you have `uv` installed:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the project dependencies:

```bash
uv sync
```

## Setup

1. Copy the environment template and configure your API keys:
   ```bash
   cp env.example .env
   # Edit .env with your API credentials
   ```

2. Set up your social media API credentials:
   - **OpenAI**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Instagram**: Create an app at [Facebook Developers](https://developers.facebook.com/)
   - **YouTube**: Create a project and enable YouTube Data API v3 in [Google Cloud Console](https://console.cloud.google.com/)
   - **TikTok**: Apply for access at [TikTok for Developers](https://developers.tiktok.com/)

3. Authenticate with social media platforms:
   ```bash
   # Authenticate with all platforms
   uv run content-cli auth all
   
   # Or authenticate individually
   uv run content-cli auth instagram
   uv run content-cli auth youtube
   uv run content-cli auth tiktok
   ```

4. Make sure your video files are saved to `~/Movies` directory

## Usage

### Running the Clip Watcher

```bash
# Using uv
uv run python main.py

# Or using the installed script
uv run clip-watcher
```

The tool will:
1. Watch for new `.mov` files in `~/Movies`
2. Generate AI captions and metadata
3. Save metadata as JSON files
4. Move processed videos to `~/Movies/Processed`
5. Upload videos to configured social media platforms

### CLI Management

Check authentication status:
```bash
uv run content-cli check all
```

Test upload functionality:
```bash
uv run content-cli test --video path/to/your/video.mov --platform all
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

## Project Structure

```
content-creation/
├── src/
│   └── content_creation/
│       ├── __init__.py
│       ├── clip_watcher.py      # Main file watcher and processor
│       ├── oauth_manager.py     # OAuth authentication for social platforms
│       ├── upload_manager.py    # Video upload to social platforms
│       └── cli.py              # Command-line interface
├── main.py                     # Entry point
├── pyproject.toml             # Project configuration
├── env.example               # Environment variables template
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

### TikTok Requirements
- Requires TikTok for Developers account approval
- Videos are uploaded as public by default
- Uses TikTok for Developers API

## Troubleshooting

### Authentication Issues
- Make sure all API credentials are correctly set in `.env`
- Check that redirect URIs match your app settings
- Ensure you have the necessary permissions for each platform

### Upload Failures
- Check your internet connection
- Verify video file format is supported by each platform
- Ensure you have sufficient storage/quota on each platform
