#!/usr/bin/env python3
"""Batch process videos to add outro image."""

import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from content_creation.video_processor import VideoProcessor

def main():
    """Batch add outro to videos."""
    parser = argparse.ArgumentParser(description="Add outro image to multiple videos")
    parser.add_argument("input", help="Input video file or directory containing videos")
    parser.add_argument("-o", "--output", help="Output directory (default: same as input)")
    parser.add_argument("--outro", default="pls_like_follow.png", 
                       help="Path to outro image (default: pls_like_follow.png)")
    parser.add_argument("-d", "--duration", type=float, default=1.0,
                       help="Outro duration in seconds (default: 1.0)")
    parser.add_argument("--suffix", default="_with_outro",
                       help="Suffix to add to output filenames (default: _with_outro)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    outro_image = Path(args.outro)
    
    # Try alternate location for outro
    if not outro_image.exists():
        outro_image = Path("assets") / args.outro
    
    if not outro_image.exists():
        print(f"❌ Outro image not found: {args.outro}")
        return
    
    processor = VideoProcessor()
    
    # Get list of videos to process
    if input_path.is_file():
        videos = [input_path]
    elif input_path.is_dir():
        # Find all video files in directory
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        videos = []
        for ext in video_extensions:
            videos.extend(input_path.glob(f'*{ext}'))
        
        if not videos:
            print(f"❌ No video files found in: {input_path}")
            return
    else:
        print(f"❌ Input path not found: {input_path}")
        return
    
    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = None
    
    print(f"🎬 Processing {len(videos)} video(s)")
    print(f"🖼️  Outro: {outro_image.absolute()}")
    print(f"⏱️  Duration: {args.duration}s\n")
    
    success_count = 0
    failed_count = 0
    
    for i, video_path in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] Processing: {video_path.name}")
        
        try:
            # Skip if already processed
            if args.suffix in video_path.stem:
                print(f"   ⏭️  Skipping (already processed)\n")
                continue
            
            # Determine output path
            if output_dir:
                output_path = output_dir / f"{video_path.stem}{args.suffix}{video_path.suffix}"
            else:
                output_path = video_path.parent / f"{video_path.stem}{args.suffix}{video_path.suffix}"
            
            result = processor.add_outro_image(
                video_path,
                outro_image,
                output_path=output_path,
                outro_duration=args.duration
            )
            
            print(f"   ✅ Saved: {result.name}\n")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {e}\n")
            failed_count += 1
    
    print("\n" + "="*60)
    print(f"✅ Successfully processed: {success_count}/{len(videos)}")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count}/{len(videos)}")
    print("="*60)

if __name__ == "__main__":
    main()



