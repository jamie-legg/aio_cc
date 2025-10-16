#!/usr/bin/env python3
"""Simple script to test adding outro to videos."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from content_creation.video_processor import VideoProcessor

def main():
    """Test adding outro to test videos."""
    processor = VideoProcessor()
    
    # Default paths
    test_videos = [
        "test_videos/test_shorts_1.mp4",
        "test_videos/test_shorts_2.mp4",
        "test_videos/test_landscape.mp4"
    ]
    
    outro_image = Path("pls_like_follow.png")
    
    if not outro_image.exists():
        outro_image = Path("assets/pls_like_follow.png")
    
    if not outro_image.exists():
        print("❌ Could not find pls_like_follow.png")
        return
    
    print(f"🖼️  Using outro image: {outro_image.absolute()}\n")
    
    # Test on first video
    video_path = Path(test_videos[0])
    
    if not video_path.exists():
        print(f"❌ Test video not found: {video_path}")
        print("💡 Run: python scripts/content/create_test_videos.py first")
        return
    
    try:
        print(f"Testing on: {video_path}\n")
        result = processor.add_outro_image(
            video_path,
            outro_image,
            outro_duration=1.0
        )
        print(f"\n✅ Success! Video with outro: {result.absolute()}")
        print(f"\n💡 You can now watch the result:")
        print(f"   open {result}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



