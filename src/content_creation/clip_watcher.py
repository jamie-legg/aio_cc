#!/usr/bin/env python3
import os
import time
import json
from pathlib import Path
from datetime import datetime
import subprocess
from dotenv import load_dotenv

from managers.oauth_manager import OAuthManager
from managers.upload_manager import UploadManager
from managers.config_manager import ConfigManager
from managers.ai_manager import AIManager
from .video_processor import VideoProcessor
from .obs_detector import OBSDetector
from .watcher_events import (
    get_event_emitter,
    emit_file_detected,
    emit_ai_generation,
    emit_video_analysis,
    emit_audio_match,
    emit_video_processing,
    emit_video_processing_complete,
    emit_upload_start,
    emit_upload_complete,
    emit_error,
    emit_video_scheduled
)

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
    
    # Emit file detected event
    try:
        file_size = path.stat().st_size
        emit_file_detected(path.name, file_size)
    except Exception as e:
        print(f"[WARNING] Could not emit file detected event: {e}")
    
    if not is_video_complete(path):
        print("...waiting for file to finish writing")
        time.sleep(5)

    # Check if FFmpeg is available
    if not video_processor.is_ffmpeg_available():
        print("[WARNING] FFmpeg not available. Videos will not be processed for Shorts.")
        print("   Install FFmpeg to enable video processing: https://ffmpeg.org/download.html")
        process_video_without_ffmpeg(path)
        return

    # Check video requirements for YouTube Shorts
    try:
        requirements = video_processor.check_video_requirements(path)
        print(f"[ANALYSIS] Video analysis:")
        print(f"   Duration: {requirements['duration']:.1f}s (max: {requirements['max_duration']}s)")
        print(f"   Aspect ratio: {requirements['current_ratio']:.2f} (target: {requirements['target_ratio']:.2f})")
        print(f"   Needs processing: {'Yes' if requirements['needs_processing'] else 'No'}")
        
        # Emit video analysis event
        try:
            emit_video_analysis(
                path.name,
                requirements['duration'],
                requirements['current_ratio'],
                requirements['needs_processing']
            )
        except Exception as e:
            print(f"[WARNING] Could not emit video analysis event: {e}")
    except Exception as e:
        print(f"[WARNING] Could not analyze video: {e}")
        requirements = {'needs_processing': True}

    # Generate AI metadata
    ai_meta = generate_ai_caption(path.name)
    print(f"AI generated: {ai_meta.get('title')}")
    
    # Emit AI generation event
    try:
        emit_ai_generation(path.name, ai_meta.get('title', ''))
    except Exception as e:
        print(f"[WARNING] Could not emit AI generation event: {e}")

    # Get current config
    current_config = config_manager.get_config()
    processed_dir = Path(current_config.processed_dir)
    processed_dir.mkdir(exist_ok=True)

    # Check if we need to process for watermark/outro
    assets_dir = Path("assets")
    watermark_path = assets_dir / "syn_watermark.png"
    outro_path = assets_dir / "outro.png"
    has_assets = watermark_path.exists() or outro_path.exists()
    
    # Process video for Shorts if needed OR if we have assets to apply
    processed_video_path = None
    if requirements.get('needs_processing', True) or has_assets:
        try:
            if requirements.get('needs_processing', True):
                print("[PROCESS] Processing video for YouTube Shorts...")
                processing_type = "shorts"
            else:
                print("[PROCESS] Processing video for watermark/outro...")
                processing_type = "watermark/outro"
            
            # Emit video processing event
            try:
                emit_video_processing(path.name, processing_type)
            except Exception as e:
                print(f"[WARNING] Could not emit video processing event: {e}")
            
            # Look for audio track
            audio_track = video_processor.find_audio_track(path)
            if not audio_track:
                audio_track = video_processor.get_default_audio_track()
                if audio_track:
                    print(f"[AUDIO] Using default audio track: {audio_track.name}")
            else:
                print(f"[AUDIO] Found matching audio track: {audio_track.name}")
            
            # Emit audio match event
            try:
                emit_audio_match(path.name, audio_track.name if audio_track else None)
            except Exception as e:
                print(f"[WARNING] Could not emit audio match event: {e}")
            
            # Process with audio, fade effects, watermark, and outro
            processed_video_path = video_processor.process_for_shorts(
                path, 
                processed_dir / f"{path.stem}_shorts{path.suffix}",
                audio_track=audio_track,
                fade_duration=1.0,  # 1 second fade in/out
                watermark_path=watermark_path if watermark_path.exists() else None,
                outro_path=outro_path if outro_path.exists() else None,
                outro_duration=3.0  # 3 second outro for visibility
            )
            print(f"[SUCCESS] Video processed: {processed_video_path.name}")
            
            # Emit video processing complete event
            try:
                emit_video_processing_complete(path.name, processed_video_path.name)
            except Exception as e:
                print(f"[WARNING] Could not emit video processing complete event: {e}")
        except Exception as e:
            print(f"[ERROR] Video processing failed: {e}")
            print("   Continuing with original video...")
            
            # Emit error event
            try:
                emit_error(path.name, f"Video processing failed: {str(e)}", "video_processing")
            except Exception as ex:
                print(f"[WARNING] Could not emit error event: {ex}")
            
            processed_video_path = None

    # Save JSON metadata
    out_json = processed_dir / f"{path.stem}.json"
    with open(out_json, "w") as f:
        json.dump(ai_meta, f, indent=2)

    # Move original video to processed folder
    new_path = processed_dir / path.name
    path.rename(new_path)
    print(f"[SAVE] Saved metadata: {out_json}\n[MOVE] Moved clip: {new_path}")
    
    # Use processed video for uploads if available, otherwise use original
    upload_path = processed_video_path if processed_video_path else new_path
    if processed_video_path:
        print(f"[UPLOAD] Using processed video for uploads: {upload_path.name}")
    
    # Check if auto-scheduling is enabled
    current_config = config_manager.get_config()
    if current_config.auto_schedule:
        # Schedule the video for later posting
        schedule_for_posting(upload_path, ai_meta)
    else:
        # Upload immediately to social media platforms
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
    print(f"[SAVE] Saved metadata: {out_json}\n[MOVE] Moved clip: {new_path}")
    
    # Check if auto-scheduling is enabled
    if current_config.auto_schedule:
        # Schedule the video for later posting
        schedule_for_posting(new_path, ai_meta)
    else:
        # Upload immediately to social media platforms
        upload_to_social_media(new_path, ai_meta)

def schedule_for_posting(video_path, metadata):
    """Schedule video for posting to social media platforms."""
    from scheduling.scheduler import schedule_video
    
    print(f"\n{'='*60}")
    print("[SCHEDULING] Preparing to schedule video for later posting...")
    print(f"{'='*60}")
    
    # Get current config
    current_config = config_manager.get_config()
    
    # Get enabled platforms
    platforms = []
    if current_config.upload_to_youtube:
        platforms.append("youtube")
    if current_config.upload_to_instagram:
        platforms.append("instagram")
    if current_config.upload_to_tiktok:
        platforms.append("tiktok")
    
    if not platforms:
        print("[WARNING] No platforms enabled for upload")
        return
    
    # Check authentication for each platform
    authenticated_platforms = []
    for platform in platforms:
        if oauth_manager.is_authenticated(platform):
            authenticated_platforms.append(platform)
        else:
            print(f"[WARNING] {platform.upper()} not authenticated - skipping")
    
    if not authenticated_platforms:
        print("[ERROR] No authenticated platforms available")
        return
    
    print(f"[SCHEDULING] Platforms: {', '.join([p.upper() for p in authenticated_platforms])}")
    
    # Prepare metadata for scheduling
    scheduling_metadata = {
        "title": metadata.get("title", ""),
        "description": metadata.get("caption", ""),
        "hashtags": metadata.get("hashtags", "")
    }
    
    # Schedule the video
    try:
        scheduled_time = schedule_video(
            video_path=str(video_path),
            metadata=scheduling_metadata,
            platforms=authenticated_platforms
        )
        
        print(f"\n[✓ SCHEDULED] Video added to schedule!")
        print(f"   📅 Time: {scheduled_time.strftime('%I:%M %p on %B %d, %Y')}")
        print(f"   📱 Platforms: {', '.join([p.upper() for p in authenticated_platforms])}")
        print(f"   📊 View schedule: http://localhost:5173/uploads")
        print(f"\n{'='*60}\n")
        
        # Emit scheduling event
        try:
            emit_video_scheduled(video_path.name, scheduled_time, authenticated_platforms)
        except Exception as e:
            print(f"[WARNING] Could not emit scheduling event: {e}")
        
    except Exception as e:
        print(f"[ERROR] Failed to schedule video: {e}")
        emit_error(video_path.name, str(e), "scheduling")

def process_video_for_scheduling(video_path: Path, ai_manager: AIManager = None, 
                                  video_processor: VideoProcessor = None, 
                                  config_manager: ConfigManager = None):
    """
    Process a video (AI metadata, watermark, outro) and prepare it for scheduling.
    Returns: (processed_video_path, metadata)
    """
    # Use global instances if not provided
    if ai_manager is None:
        ai_manager = globals()['ai_manager']
    if video_processor is None:
        video_processor = globals()['video_processor']
    if config_manager is None:
        config_manager = globals()['config_manager']
    
    print(f"\n{'='*60}")
    print(f"Processing: {video_path.name}")
    print('='*60)
    
    # Generate AI metadata
    print("[1/4] Generating AI metadata...")
    game_context = "armagetron advanced | retroycycles"
    ai_meta = ai_manager.generate_metadata(video_path.name, game_context)
    print(f"  [OK] Title: {ai_meta.get('title', 'N/A')}")
    
    # Get config
    current_config = config_manager.get_config()
    processed_dir = Path(current_config.processed_dir)
    processed_dir.mkdir(exist_ok=True)
    
    # Check if we need to process for watermark/outro
    assets_dir = Path("assets")
    watermark_path = assets_dir / "syn_watermark.png"
    outro_path = assets_dir / "outro.png"
    has_assets = watermark_path.exists() or outro_path.exists()
    
    # Check video requirements
    print("[2/4] Analyzing video...")
    try:
        requirements = video_processor.check_video_requirements(video_path)
        print(f"  Duration: {requirements['duration']:.1f}s")
        print(f"  Aspect ratio: {requirements['current_ratio']:.2f}")
        needs_processing = requirements.get('needs_processing', True)
    except Exception as e:
        print(f"  Warning: Could not analyze video: {e}")
        needs_processing = True
    
    # Process video if needed
    processed_video_path = None
    if needs_processing or has_assets:
        print("[3/4] Processing video (watermark/outro/shorts formatting)...")
        try:
            # Look for audio track
            audio_track = video_processor.find_audio_track(video_path)
            if not audio_track:
                audio_track = video_processor.get_default_audio_track()
            
            if audio_track:
                print(f"  [OK] Using audio: {audio_track.name}")
            
            # Process video
            processed_video_path = video_processor.process_for_shorts(
                video_path,
                processed_dir / f"{video_path.stem}_shorts{video_path.suffix}",
                audio_track=audio_track,
                fade_duration=1.0,
                watermark_path=watermark_path if watermark_path.exists() else None,
                outro_path=outro_path if outro_path.exists() else None,
                outro_duration=3.0
            )
            print(f"  [OK] Processed: {processed_video_path.name}")
        except Exception as e:
            print(f"  Warning: Processing failed: {e}")
            print(f"  Will use original video")
            processed_video_path = None
    else:
        print("[3/4] No processing needed")
    
    # Save JSON metadata
    print("[4/4] Saving metadata...")
    out_json = processed_dir / f"{video_path.stem}.json"
    with open(out_json, "w") as f:
        json.dump(ai_meta, f, indent=2)
    print(f"  [OK] Metadata saved: {out_json.name}")
    
    # Move original to processed folder
    new_path = processed_dir / video_path.name
    if not new_path.exists():  # Don't move if already there
        video_path.rename(new_path)
        print(f"  [OK] Moved original to: {new_path}")
    
    # Use processed video if available, otherwise original
    final_video_path = processed_video_path if processed_video_path else new_path
    
    return final_video_path, ai_meta


def upload_to_social_media(video_path, metadata):
    """Upload video to configured social media platforms (legacy - now uses scheduling)."""
    
    # Get current config
    current_config = config_manager.get_config()
    
    # Check which platforms to upload to
    platforms = config_manager.get_upload_platforms()
    
    if not platforms:
        print("No platforms configured for upload")
        return
    
    print(f"\n[UPLOAD] Uploading to {', '.join(platforms)}...")
    
    # Check authentication for each platform
    for platform in platforms:
        if not oauth_manager.is_authenticated(platform):
            print(f"[WARNING] {platform.upper()} not authenticated. Run 'uv run python -c \"from content_creation.oauth_manager import OAuthManager; OAuthManager().authenticate_{platform}()\"' to authenticate.")
            platforms.remove(platform)
    
    if not platforms:
        print("[ERROR] No authenticated platforms available for upload")
        return
    
    # Upload to authenticated platforms
    # Emit upload start events
    for platform in platforms:
        try:
            emit_upload_start(video_path.name, platform)
        except Exception as e:
            print(f"[WARNING] Could not emit upload start event: {e}")
    
    results = upload_manager.upload_to_all_platforms(video_path, metadata, platforms)
    
    # Print summary and emit completion events
    print(f"\n[UPLOAD] Upload Summary:")
    for platform, result in results.items():
        if result.success:
            print(f"  [SUCCESS] {platform.upper()}: {result.url or result.video_id}")
            
            # Emit upload complete event
            try:
                emit_upload_complete(
                    video_path.name,
                    platform,
                    result.url,
                    result.video_id
                )
            except Exception as e:
                print(f"[WARNING] Could not emit upload complete event: {e}")
        else:
            print(f"  [ERROR] {platform.upper()}: {result.error}")
            
            # Emit error event
            try:
                emit_error(video_path.name, f"{platform} upload failed: {result.error}", "upload")
            except Exception as e:
                print(f"[WARNING] Could not emit error event: {e}")

def watch_folder():
    # Get current config
    current_config = config_manager.get_config()
    watch_dir = Path(current_config.watch_dir)
    
    if not watch_dir.exists():
        print(f"Error: Watch directory {watch_dir} does not exist")
        print("Use 'uv run content-cli config set-watch-dir <path>' to set a valid directory")
        return
    
    # Set watcher status to watching
    event_emitter = get_event_emitter()
    event_emitter.set_status("watching")
    
    # Use pathlib for better Windows compatibility
    seen = set(f.name for f in watch_dir.iterdir() if f.is_file())
    extensions_str = ", ".join(current_config.video_extensions)
    print(f"Watching {watch_dir} for new {extensions_str} files...")
    
    while True:
        current = set(f.name for f in watch_dir.iterdir() if f.is_file())
        new_files = []
        for f in current - seen:
            if any(f.lower().endswith(ext) for ext in current_config.video_extensions):
                new_files.append(f)
        
        for f in new_files:
            process_clip(watch_dir / f)
        seen = current
        time.sleep(3)

def print_startup_config():
    """Print configuration and status at startup."""
    print("=" * 60)
    print("AI CONTENT CREATION TOOL - STARTUP CONFIGURATION")
    print("=" * 60)
    
    # Import config manager
    from managers.config_manager import ConfigManager
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    # Print basic configuration
    print(f"\n[CONFIG] Watch Directory: {config.watch_dir}")
    print(f"[CONFIG] Processed Directory: {config.processed_dir}")
    print(f"[CONFIG] Video Extensions: {', '.join(config.video_extensions)}")
    
    # Print FTP server configuration
    print(f"\n[FTP SERVER]")
    ftp_url = os.getenv("FTP_URL", "Not configured")
    ftp_bucket = os.getenv("FTP_BUCKET", "Not configured")
    print(f"  URL: {ftp_url}")
    print(f"  Bucket: {ftp_bucket}")
    
    # Print upload platforms with auth status
    print(f"\n[UPLOAD PLATFORMS]")
    platforms = [
        ("Instagram", config.upload_to_instagram, "instagram"),
        ("YouTube", config.upload_to_youtube, "youtube"),
        ("TikTok", config.upload_to_tiktok, "tiktok")
    ]
    
    for platform_name, enabled, platform_key in platforms:
        auth_status = "[AUTHENTICATED]" if oauth_manager.is_authenticated(platform_key) else "[NOT AUTHENTICATED]"
        enabled_status = "[ENABLED]" if enabled else "[DISABLED]"
        print(f"  {platform_name}: {enabled_status} {auth_status}")
    
    # OBS Detection
    print(f"\n[OBS STUDIO DETECTION]")
    obs_detector = OBSDetector()
    obs_info = obs_detector.get_obs_info()
    print(f"  OBS Running: {'Yes' if obs_info['obs_running'] else 'No'}")
    print(f"  OBS Installed: {'Yes' if obs_info['obs_installed'] else 'No'}")
    if obs_info['replay_buffer_path']:
        print(f"  Replay Buffer: {obs_info['replay_buffer_path']}")
    else:
        print(f"  Replay Buffer: Not configured")
    
    # Print directory status
    print(f"\n[DIRECTORY STATUS]")
    watch_path = Path(config.watch_dir)
    processed_path = Path(config.processed_dir)
    print(f"  Watch Directory: {'[EXISTS]' if watch_path.exists() else '[NOT FOUND]'}")
    print(f"  Processed Directory: {'[EXISTS]' if processed_path.exists() else '[NOT FOUND]'}")
    
    # Count video files
    if watch_path.exists():
        video_count = 0
        for ext in config.video_extensions:
            video_count += len(list(watch_path.glob(f"*{ext}")))
        print(f"  Video files in watch directory: {video_count}")
    
    print("=" * 60)

def main():
    """Main entry point for the clip watcher."""
    
    # Auto-detect OBS replay buffer directory
    obs_detector = OBSDetector()
    replay_buffer_path = obs_detector.get_replay_buffer_path()
    
    # If OBS replay buffer found and watch directory not configured or doesn't exist
    if replay_buffer_path:
        watch_path = Path(config.watch_dir)
        if not watch_path.exists() or str(watch_path) == "." or str(watch_path) == "clips":
            print(f"\n[OBS] Replay buffer detected: {replay_buffer_path}")
            print(f"[OBS] Auto-configuring watch directory...")
            config.watch_dir = str(replay_buffer_path)
            config_manager.save_config(config)
            print(f"[OBS] Watch directory set to OBS replay buffer")
    
    # Print startup configuration
    print_startup_config()
    
    # Check for authentication only for enabled platforms
    print(f"\n[AUTH] Checking authentication for enabled platforms...")
    enabled_platforms = config_manager.get_upload_platforms()
    
    missing_auth = []
    for platform in enabled_platforms:
        if not oauth_manager.is_authenticated(platform):
            missing_auth.append(platform)
            print(f"[WARNING] {platform.upper()} is enabled but not authenticated.")
    
    if missing_auth:
        print(f"\n[WARNING] The following platforms are enabled but not authenticated:")
        for platform in missing_auth:
            print(f"  - {platform.upper()}: Run 'make auth-{platform}' to authenticate")
        print(f"\n[INFO] The watcher will still run, but uploads to these platforms will be skipped.")
        print(f"       Authenticate them later to enable uploads.\n")
    else:
        print(f"[AUTH] All enabled platforms are authenticated\n")
    
    watch_folder()

if __name__ == "__main__":
    main()
