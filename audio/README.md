# Audio Tracks for Video Processing

This directory contains audio tracks that will be automatically mixed with your videos during processing.

## How it works:

1. **Matching audio tracks**: Place audio files with the same name as your video files
   - Video: `Replay 2025-10-07 10-31-10.mov`
   - Audio: `Replay 2025-10-07 10-31-10.mp3`

2. **Default audio track**: Place a file named `default.mp3` to use for all videos without specific audio

3. **Supported formats**: MP3, WAV, AAC, M4A, OGG

## Examples:

```
audio/
├── default.mp3              # Used for all videos without specific audio
├── Replay 2025-10-07 10-31-10.mp3  # Specific audio for this video
├── background.mp3           # Alternative default name
└── music.mp3               # Another alternative default name
```

## Audio Processing Features:

- **Automatic mixing**: Original video audio + new audio track
- **Fade effects**: Smooth fade in/out (configurable duration)
- **Quality optimization**: AAC encoding at 128kbps
- **Smart duration**: Audio is trimmed to match video length
