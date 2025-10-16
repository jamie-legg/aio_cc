#!/usr/bin/env python3
"""Generate test videos for testing the outro image feature."""

import subprocess
import sys
from pathlib import Path

def create_test_video(output_path: Path, width: int = 1080, height: int = 1920, 
                      duration: int = 5, text: str = "Test Video"):
    """
    Create a simple test video using FFmpeg.
    
    Args:
        output_path: Path for output video
        width: Video width (default: 1080 for 9:16)
        height: Video height (default: 1920 for 9:16)
        duration: Duration in seconds
        text: Text to display on the video
    """
    print(f"🎬 Creating test video: {output_path.name}")
    print(f"   Dimensions: {width}x{height}")
    print(f"   Duration: {duration}s")
    
    try:
        # Create a test video with colored background and text
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'color=c=blue:s={width}x{height}:d={duration}:r=30',
            '-f', 'lavfi',
            '-i', f'sine=frequency=440:duration={duration}',  # Add audio tone
            '-vf', f"drawtext=text='{text}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '20',
            '-r', '30',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '48000',
            '-movflags', '+faststart',
            '-y',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Created: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create test video: {e}")
        print(f"   Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ FFmpeg not found. Please install FFmpeg to create test videos.")
        return False

def main():
    """Generate test videos."""
    print("🎥 Test Video Generator\n")
    
    # Create test videos directory
    test_dir = Path("test_videos")
    test_dir.mkdir(exist_ok=True)
    print(f"📁 Creating test videos in: {test_dir.absolute()}\n")
    
    # Test video configurations
    test_videos = [
        {
            'name': 'test_shorts_1.mp4',
            'width': 1080,
            'height': 1920,
            'duration': 5,
            'text': 'Test Shorts Video 1'
        },
        {
            'name': 'test_shorts_2.mp4',
            'width': 1080,
            'height': 1920,
            'duration': 8,
            'text': 'Test Shorts Video 2'
        },
        {
            'name': 'test_landscape.mp4',
            'width': 1920,
            'height': 1080,
            'duration': 5,
            'text': 'Landscape Video'
        }
    ]
    
    created = 0
    for config in test_videos:
        output_path = test_dir / config['name']
        if create_test_video(
            output_path,
            width=config['width'],
            height=config['height'],
            duration=config['duration'],
            text=config['text']
        ):
            created += 1
    
    print(f"\n✅ Created {created}/{len(test_videos)} test videos")
    print(f"📁 Test videos location: {test_dir.absolute()}")
    
    if created > 0:
        print("\n💡 Now you can test adding the outro with:")
        print(f"   python -m content_creation.cli add-outro test_videos/test_shorts_1.mp4")
        print(f"   python -m content_creation.cli add-outro test_videos/test_shorts_1.mp4 --outro pls_like_follow.png")
        print(f"   python -m content_creation.cli add-outro test_videos/test_shorts_1.mp4 -d 2.0  # 2 second outro")

if __name__ == "__main__":
    main()



