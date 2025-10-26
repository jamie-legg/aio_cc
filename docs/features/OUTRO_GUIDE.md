# Video Outro Guide

This guide explains how to add the "pls like and follow" outro image to your generated videos.

## Overview

The outro feature automatically appends your `pls_like_follow.png` image to the end of any video for a specified duration (default: 1 second). The image is automatically scaled and positioned to match your video's dimensions and aspect ratio.

## Features

- ✅ Automatic scaling to match video dimensions
- ✅ Maintains video properties (fps, codec, audio)
- ✅ Supports all common video formats (MP4, MOV, AVI, MKV, WebM)
- ✅ Works with both portrait (9:16) and landscape (16:9) videos
- ✅ Batch processing for multiple videos
- ✅ Customizable outro duration

## Quick Start

### Single Video

Add outro to a single video:

```bash
# Using default pls_like_follow.png with 1 second duration
python add_outro_batch.py path/to/video.mp4

# Custom outro image
python add_outro_batch.py path/to/video.mp4 --outro custom_outro.png

# Custom duration (2 seconds)
python add_outro_batch.py path/to/video.mp4 -d 2.0

# Specify output location
python add_outro_batch.py path/to/video.mp4 -o output_directory/
```

### Batch Processing

Process all videos in a directory:

```bash
# Process all videos in a directory
python add_outro_batch.py generated_transitions/racing/

# Process with custom settings
python add_outro_batch.py generated_transitions/racing/ -d 1.5 -o processed_videos/
```

## Script Options

### `add_outro_batch.py`

```bash
python add_outro_batch.py <input> [options]

Arguments:
  input                 Input video file or directory containing videos

Options:
  -o, --output         Output directory (default: same as input)
  --outro             Path to outro image (default: pls_like_follow.png)
  -d, --duration      Outro duration in seconds (default: 1.0)
  --suffix            Suffix to add to output filenames (default: _with_outro)
```

### Examples

```bash
# Process all shorts videos
python add_outro_batch.py test_videos/ 

# Use a different outro and 2-second duration
python add_outro_batch.py generated_transitions/racing/ --outro assets/custom_outro.png -d 2.0

# Save processed videos to a different directory
python add_outro_batch.py generated_transitions/ -o processed_with_outro/
```

## Integration with Video Pipeline

You can integrate the outro into your existing video processing workflow:

```python
from pathlib import Path
from content_creation.video_processor import VideoProcessor

processor = VideoProcessor()

# After generating/processing your video
video_path = Path("generated_transitions/racing/video1.mp4")
outro_image = Path("pls_like_follow.png")

# Add outro
final_video = processor.add_outro_image(
    input_path=video_path,
    outro_image=outro_image,
    outro_duration=1.0
)

print(f"Final video with outro: {final_video}")
```

## Testing

Test videos are included for testing the outro functionality:

```bash
# Generate test videos (if not already created)
python scripts/content/create_test_videos.py

# Test outro on a single video
python test_outro.py

# Batch process all test videos
python add_outro_batch.py test_videos/
```

## Technical Details

### How It Works

1. **Video Analysis**: Reads the input video's dimensions, fps, and codec information
2. **Image Conversion**: Converts the PNG outro image to a video segment with:
   - Matching dimensions and aspect ratio
   - Black letterboxing/pillarboxing if needed
   - Same framerate as the original video
   - Specified duration (default 1 second)
3. **Concatenation**: Joins the original video with the outro segment
   - Attempts fast copy (no re-encoding) first
   - Falls back to re-encoding if codecs don't match

### Supported Formats

**Video Formats:**
- MP4 (recommended)
- MOV
- AVI
- MKV
- WebM

**Image Formats:**
- PNG (recommended)
- JPG
- JPEG

### Performance

- **Fast mode**: When codecs match, concatenation is instant (no re-encoding)
- **Re-encode mode**: When codecs don't match, video is re-encoded (slower but reliable)
- **Typical time**: 5-10 seconds per video for a 5-second source video

## Troubleshooting

### Issue: "FFmpeg not found"

Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Issue: "Outro image not found"

Make sure `pls_like_follow.png` is in one of these locations:
- Current directory: `./pls_like_follow.png`
- Assets directory: `./assets/pls_like_follow.png`

Or specify the full path:
```bash
python add_outro_batch.py video.mp4 --outro /full/path/to/outro.png
```

### Issue: Quality loss

If you notice quality loss, the video is being re-encoded. You can adjust the quality settings in `video_processor.py` by changing the `-crf` value (lower = better quality, larger file):

```python
'-crf', '18',  # Higher quality (was 20)
```

## Tips

1. **Batch Processing**: Process all videos in a directory at once for efficiency
2. **Custom Duration**: Adjust outro duration based on your content (1-3 seconds recommended)
3. **Skip Processed**: The script automatically skips videos with `_with_outro` in the filename
4. **Backup**: Keep original videos before batch processing

## Next Steps

- Add outros to all generated transition videos
- Integrate into your upload pipeline
- Customize the outro image for different content types
- Automate outro addition in your video generation scripts

## Files

- `add_outro_batch.py` - Batch processing script
- `test_outro.py` - Single video test script
- `scripts/content/create_test_videos.py` - Generate test videos
- `src/content_creation/video_processor.py` - Core video processing module



