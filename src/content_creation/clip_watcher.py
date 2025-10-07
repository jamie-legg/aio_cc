#!/usr/bin/env python3
import os
import time
import json
from pathlib import Path
from datetime import datetime
import subprocess
from dotenv import load_dotenv

from .oauth_manager import OAuthManager
from .upload_manager import UploadManager
from .config_manager import ConfigManager
from .ai_manager import AIManager
from .video_processor import VideoProcessor

# Load environment variables
load_dotenv()

# Initialize managers
config_manager = ConfigManager()
config = config_manager.get_config()
oauth_manager = OAuthManager()
upload_manager = UploadManager(oauth_manager)
ai_manager = AIManager()
video_processor = VideoProcessor()

def is_video_complete(path):
    """Return True when the file is stable (not growing)."""
    size1 = path.stat().st_size
    time.sleep(2)
    size2 = path.stat().st_size
    return size1 == size2

def generate_ai_caption(filename):
    """Generate AI metadata using the new AI manager."""
    # Detect game context from filename
    game_context = "armagetron advanced | retroycycles"
    return ai_manager.generate_metadata(filename, game_context)

def process_clip(path):
    print(f"[+] Detected new clip: {path.name}")
    if not is_video_complete(path):
        print("...waiting for file to finish writing")
        time.sleep(5)

    # Check if FFmpeg is available
    if not video_processor.is_ffmpeg_available():
        print("⚠️  FFmpeg not available. Videos will not be processed for Shorts.")
        print("   Install FFmpeg to enable video processing: https://ffmpeg.org/download.html")
        process_video_without_ffmpeg(path)
        return

    # Check video requirements for YouTube Shorts
    try:
        requirements = video_processor.check_video_requirements(path)
        print(f"📊 Video analysis:")
        print(f"   Duration: {requirements['duration']:.1f}s (max: {requirements['max_duration']}s)")
        print(f"   Aspect ratio: {requirements['current_ratio']:.2f} (target: {requirements['target_ratio']:.2f})")
        print(f"   Needs processing: {'Yes' if requirements['needs_processing'] else 'No'}")
    except Exception as e:
        print(f"⚠️  Could not analyze video: {e}")
        requirements = {'needs_processing': True}

    # Generate AI metadata
    ai_meta = generate_ai_caption(path.name)
    print(f"AI generated: {ai_meta.get('title')}")

    # Get current config
    current_config = config_manager.get_config()
    processed_dir = Path(current_config.processed_dir)
    processed_dir.mkdir(exist_ok=True)

    # Process video for Shorts if needed
    processed_video_path = None
    if requirements.get('needs_processing', True):
        try:
            print("🎬 Processing video for YouTube Shorts...")
            
            # Look for audio track
            audio_track = video_processor.find_audio_track(path)
            if not audio_track:
                audio_track = video_processor.get_default_audio_track()
                if audio_track:
                    print(f"🎵 Using default audio track: {audio_track.name}")
            else:
                print(f"🎵 Found matching audio track: {audio_track.name}")
            
            # Process with audio and fade effects
            processed_video_path = video_processor.process_for_shorts(
                path, 
                processed_dir / f"{path.stem}_shorts{path.suffix}",
                audio_track=audio_track,
                fade_duration=1.0  # 1 second fade in/out
            )
            print(f"✅ Video processed: {processed_video_path.name}")
        except Exception as e:
            print(f"❌ Video processing failed: {e}")
            print("   Continuing with original video...")
            processed_video_path = None

    # Save JSON metadata
    out_json = processed_dir / f"{path.stem}.json"
    with open(out_json, "w") as f:
        json.dump(ai_meta, f, indent=2)

    # Move original video to processed folder
    new_path = processed_dir / path.name
    path.rename(new_path)
    print(f"[✓] Saved metadata: {out_json}\n[→] Moved clip: {new_path}")
    
    # Use processed video for uploads if available, otherwise use original
    upload_path = processed_video_path if processed_video_path else new_path
    if processed_video_path:
        print(f"📤 Using processed video for uploads: {upload_path.name}")
    
    # Upload to social media platforms
    upload_to_social_media(upload_path, ai_meta)

def process_video_without_ffmpeg(path):
    """Process video without FFmpeg (fallback)."""
    ai_meta = generate_ai_caption(path.name)
    print(f"AI generated: {ai_meta.get('title')}")

    # Get current config
    current_config = config_manager.get_config()
    processed_dir = Path(current_config.processed_dir)
    processed_dir.mkdir(exist_ok=True)

    # Save JSON metadata
    out_json = processed_dir / f"{path.stem}.json"
    with open(out_json, "w") as f:
        json.dump(ai_meta, f, indent=2)

    # Move video to processed folder
    new_path = processed_dir / path.name
    path.rename(new_path)
    print(f"[✓] Saved metadata: {out_json}\n[→] Moved clip: {new_path}")
    
    # Upload to social media platforms
    upload_to_social_media(new_path, ai_meta)

def upload_to_social_media(video_path, metadata):
    """Upload video to configured social media platforms."""
    
    # Get current config
    current_config = config_manager.get_config()
    
    # Check which platforms to upload to
    platforms = config_manager.get_upload_platforms()
    
    if not platforms:
        print("No platforms configured for upload")
        return
    
    print(f"\n[📤] Uploading to {', '.join(platforms)}...")
    
    # Check authentication for each platform
    for platform in platforms:
        if not oauth_manager.is_authenticated(platform):
            print(f"⚠️  {platform.upper()} not authenticated. Run 'uv run python -c \"from content_creation.oauth_manager import OAuthManager; OAuthManager().authenticate_{platform}()\"' to authenticate.")
            platforms.remove(platform)
    
    if not platforms:
        print("❌ No authenticated platforms available for upload")
        return
    
    # Upload to authenticated platforms
    results = upload_manager.upload_to_all_platforms(video_path, metadata, platforms)
    
    # Print summary
    print(f"\n[📊] Upload Summary:")
    for platform, result in results.items():
        if result.success:
            print(f"  ✅ {platform.upper()}: {result.url or result.video_id}")
        else:
            print(f"  ❌ {platform.upper()}: {result.error}")

def watch_folder():
    # Get current config
    current_config = config_manager.get_config()
    watch_dir = Path(current_config.watch_dir)
    
    if not watch_dir.exists():
        print(f"Error: Watch directory {watch_dir} does not exist")
        print("Use 'uv run content-cli config set-watch-dir <path>' to set a valid directory")
        return
    
    seen = set(os.listdir(watch_dir))
    extensions_str = ", ".join(current_config.video_extensions)
    print(f"Watching {watch_dir} for new {extensions_str} files...")
    
    while True:
        current = set(os.listdir(watch_dir))
        new_files = []
        for f in current - seen:
            if any(f.lower().endswith(ext) for ext in current_config.video_extensions):
                new_files.append(f)
        
        for f in new_files:
            process_clip(watch_dir / f)
        seen = current
        time.sleep(3)

def main():
    """Main entry point for the clip watcher."""
    watch_folder()

if __name__ == "__main__":
    main()
