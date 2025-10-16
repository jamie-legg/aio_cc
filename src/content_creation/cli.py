"""Command-line interface for content creation tools."""

import argparse
import sys
from pathlib import Path
from managers.oauth_manager import OAuthManager
from managers.upload_manager import UploadManager
from managers.config_manager import ConfigManager

def setup_auth(args):
    """Set up authentication for social media platforms."""
    oauth_manager = OAuthManager()
    
    if args.platform == "all":
        results = oauth_manager.authenticate_all()
        print("\n=== Authentication Results ===")
        for platform, success in results.items():
            status = "[SUCCESS] Success" if success else "[ERROR] Failed"
            print(f"{platform.upper()}: {status}")
    else:
        if args.platform == "instagram":
            success = oauth_manager.authenticate_instagram()
        elif args.platform == "youtube":
            success = oauth_manager.authenticate_youtube()
        elif args.platform == "tiktok":
            success = oauth_manager.authenticate_tiktok()
        else:
            print(f"Unknown platform: {args.platform}")
            return
        
        if success:
            print(f"[SUCCESS] {args.platform.upper()} authentication successful!")
        else:
            print(f"[ERROR] {args.platform.upper()} authentication failed!")

def check_auth(args):
    """Check authentication status for platforms."""
    oauth_manager = OAuthManager()
    upload_manager = UploadManager(oauth_manager)
    
    platforms = ["instagram", "youtube", "tiktok"] if args.platform == "all" else [args.platform]
    
    print("=== Authentication Status ===")
    for platform in platforms:
        creds = oauth_manager.get_credentials(platform)
        if creds and creds.access_token:
            print(f"[SUCCESS] {platform.upper()}: Authenticated")
            
            # Show token expiration info
            if creds.expires_at:
                import time
                expires_in = creds.expires_at - int(time.time())
                if expires_in > 0:
                    hours = expires_in // 3600
                    minutes = (expires_in % 3600) // 60
                    print(f"   Token expires in: {hours}h {minutes}m")
                else:
                    print(f"   Token expired: {abs(expires_in)}s ago")
            else:
                print(f"   Token expiration: Unknown")
            
            # Get additional info
            status = upload_manager.get_upload_status(platform)
            if status.get("authenticated"):
                if "user_info" in status:
                    user_info = status["user_info"]
                    if "username" in user_info:
                        print(f"   Username: {user_info['username']}")
                    elif "data" in user_info and "display_name" in user_info["data"]:
                        print(f"   Display Name: {user_info['data']['display_name']}")
                elif "channels" in status and status["channels"]:
                    channel = status["channels"][0]
                    print(f"   Channel: {channel['snippet']['title']}")
        else:
            print(f"[ERROR] {platform.upper()}: Not authenticated")

def test_upload(args):
    """Test upload functionality with a sample video."""
    if not args.video:
        print("Please provide a video file path with --video")
        return
    
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Video file not found: {video_path}")
        return
    
    oauth_manager = OAuthManager()
    upload_manager = UploadManager(oauth_manager)
    
    # Sample metadata
    metadata = {
        "title": "Test Upload",
        "caption": "This is a test upload from the content creation tool!",
        "hashtags": "#test #gaming #content"
    }
    
    platforms = ["instagram", "youtube", "tiktok"] if args.platform == "all" else [args.platform]
    
    print(f"Testing upload to {', '.join(platforms)}...")
    results = upload_manager.upload_to_all_platforms(video_path, metadata, platforms)
    
    print("\n=== Upload Results ===")
    for platform, result in results.items():
        if result.success:
            print(f"[SUCCESS] {platform.upper()}: {result.url or result.video_id}")
        else:
            print(f"[ERROR] {platform.upper()}: {result.error}")

def config_show(args):
    """Show current configuration."""
    config_manager = ConfigManager()
    config_manager.show_config()

def config_set_watch_dir(args):
    """Set the watch directory for video files."""
    config_manager = ConfigManager()
    success = config_manager.set_watch_dir(args.path)
    if success:
        config_manager.validate_config()

def config_set_processed_dir(args):
    """Set the processed directory for completed videos."""
    config_manager = ConfigManager()
    success = config_manager.set_processed_dir(args.path)
    if success:
        config_manager.validate_config()

def config_set_extensions(args):
    """Set video file extensions to watch for."""
    config_manager = ConfigManager()
    extensions = args.extensions.split(',')
    success = config_manager.set_video_extensions(extensions)
    if success:
        config_manager.validate_config()

def config_toggle_platform(args):
    """Enable or disable upload to a specific platform."""
    config_manager = ConfigManager()
    enabled = args.action == "enable"
    success = config_manager.set_upload_platform(args.platform, enabled)
    if success:
        config_manager.show_config()

def config_reset(args):
    """Reset configuration to defaults."""
    config_manager = ConfigManager()
    config_manager.reset_to_defaults()

def config_validate(args):
    """Validate current configuration."""
    config_manager = ConfigManager()
    config_manager.validate_config()

def retry_list(args):
    """List all failed uploads available for retry."""
    oauth_manager = OAuthManager()
    upload_manager = UploadManager(oauth_manager)
    
    failed_uploads = upload_manager.list_failed_uploads()
    
    if not failed_uploads:
        print("[INFO] No failed uploads found")
        return
    
    print("=== Failed Uploads ===")
    for key, entry in failed_uploads.items():
        video_name = entry["video_path"].split("\\")[-1]
        platform = entry["platform"]
        error = entry["error"]
        timestamp = entry["timestamp"]
        retry_count = entry["retry_count"]
        
        print(f"\n{platform.upper()}: {video_name}")
        print(f"  Error: {error}")
        print(f"  Failed: {timestamp}")
        print(f"  Retry count: {retry_count}")

def retry_single(args):
    """Retry a specific failed upload."""
    oauth_manager = OAuthManager()
    upload_manager = UploadManager(oauth_manager)
    
    result = upload_manager.retry_failed_upload(args.video_name, args.platform)
    
    if result.success:
        print(f"[SUCCESS] {args.platform.upper()} retry successful!")
        if result.url:
            print(f"URL: {result.url}")
    else:
        print(f"[ERROR] {args.platform.upper()} retry failed: {result.error}")

def retry_all(args):
    """Retry all failed uploads for specified platforms."""
    oauth_manager = OAuthManager()
    upload_manager = UploadManager(oauth_manager)
    
    platforms = args.platforms.split(",") if args.platforms else None
    results = upload_manager.retry_all_failed_uploads(platforms)
    
    print("\n=== Retry Results ===")
    for key, result in results.items():
        status = "[SUCCESS]" if result.success else "[FAILED]"
        print(f"{key}: {status} {result.error if not result.success else 'Success'}")

def retry_clear(args):
    """Clear failed uploads."""
    oauth_manager = OAuthManager()
    upload_manager = UploadManager(oauth_manager)
    
    upload_manager.clear_failed_uploads(args.platform)
    print(f"[CLEAR] Cleared failed uploads for {args.platform.upper() if args.platform else 'ALL'}")

def upload_video(args):
    """Upload video with AI-generated captions to all platforms."""
    from pathlib import Path
    from managers.ai_manager import AIManager
    from managers.config_manager import ConfigManager
    
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"[ERROR] Video file not found: {video_path}")
        return
    
    print(f"[UPLOAD] Processing video: {video_path.name}")
    
    # Initialize managers
    oauth_manager = OAuthManager()
    upload_manager = UploadManager(oauth_manager)
    ai_manager = AIManager()
    config_manager = ConfigManager()
    
    # Check authentication
    print("[AUTH] Checking authentication status...")
    platforms = []
    if oauth_manager.is_authenticated("instagram") and config_manager.get_config().upload_to_instagram:
        platforms.append("instagram")
    if oauth_manager.is_authenticated("youtube") and config_manager.get_config().upload_to_youtube:
        platforms.append("youtube")
    if oauth_manager.is_authenticated("tiktok") and config_manager.get_config().upload_to_tiktok:
        platforms.append("tiktok")
    
    if not platforms:
        print("[ERROR] No authenticated platforms available for upload")
        return
    
    print(f"[AUTH] Uploading to: {', '.join(platforms)}")
    
    # Generate AI metadata
    print("[AI] Generating captions and metadata...")
    try:
        metadata = ai_manager.generate_metadata(video_path)
        print(f"[AI] Generated title: {metadata.get('title', 'N/A')}")
        print(f"[AI] Generated caption: {metadata.get('caption', 'N/A')[:100]}...")
        print(f"[AI] Generated hashtags: {metadata.get('hashtags', 'N/A')}")
    except Exception as e:
        print(f"[WARNING] AI generation failed: {e}")
        print("[AI] Using fallback metadata...")
        metadata = {
            "title": f"Video {video_path.stem}",
            "caption": f"Check out this amazing video! {video_path.stem}",
            "hashtags": "#video #content #shorts"
        }
    
    # Upload to platforms
    print(f"\n[UPLOAD] Starting upload to {len(platforms)} platforms...")
    results = upload_manager.upload_to_all_platforms(video_path, metadata, platforms)
    
    # Print results
    print(f"\n[RESULTS] Upload Summary:")
    for platform, result in results.items():
        if result.success:
            print(f"  [SUCCESS] {platform.upper()}: {result.video_id}")
            if result.url:
                print(f"    URL: {result.url}")
        else:
            print(f"  [ERROR] {platform.upper()}: {result.error}")
    
    # Show retry info if there were failures
    failed_count = sum(1 for r in results.values() if not r.success)
    if failed_count > 0:
        print(f"\n[RETRY] {failed_count} uploads failed. Use 'uv run content-cli retry list' to see failed uploads.")
        print("[RETRY] Use 'uv run content-cli retry all' to retry failed uploads.")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Content Creation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup auth command
    auth_parser = subparsers.add_parser("auth", help="Set up authentication")
    auth_parser.add_argument("platform", choices=["instagram", "youtube", "tiktok", "all"],
                           help="Platform to authenticate with")
    auth_parser.set_defaults(func=setup_auth)
    
    # Check auth command
    check_parser = subparsers.add_parser("check", help="Check authentication status")
    check_parser.add_argument("platform", choices=["instagram", "youtube", "tiktok", "all"],
                            help="Platform to check")
    check_parser.set_defaults(func=check_auth)
    
    # Test upload command
    test_parser = subparsers.add_parser("test", help="Test upload functionality")
    test_parser.add_argument("--video", required=True, help="Path to video file")
    test_parser.add_argument("--platform", choices=["instagram", "youtube", "tiktok", "all"],
                           default="all", help="Platform to test upload to")
    test_parser.set_defaults(func=test_upload)
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload video with AI captions to all platforms")
    upload_parser.add_argument("--video", required=True, help="Path to video file")
    upload_parser.set_defaults(func=upload_video)
    
    # Configuration commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Configuration commands")
    
    # Show config
    config_show_parser = config_subparsers.add_parser("show", help="Show current configuration")
    config_show_parser.set_defaults(func=config_show)
    
    # Set watch directory
    config_watch_parser = config_subparsers.add_parser("set-watch-dir", help="Set watch directory for video files")
    config_watch_parser.add_argument("path", help="Path to watch directory")
    config_watch_parser.set_defaults(func=config_set_watch_dir)
    
    # Set processed directory
    config_processed_parser = config_subparsers.add_parser("set-processed-dir", help="Set processed directory for completed videos")
    config_processed_parser.add_argument("path", help="Path to processed directory")
    config_processed_parser.set_defaults(func=config_set_processed_dir)
    
    # Set video extensions
    config_ext_parser = config_subparsers.add_parser("set-extensions", help="Set video file extensions to watch for")
    config_ext_parser.add_argument("extensions", help="Comma-separated list of extensions (e.g., mov,mp4,avi)")
    config_ext_parser.set_defaults(func=config_set_extensions)
    
    # Toggle platform
    config_platform_parser = config_subparsers.add_parser("toggle-platform", help="Enable or disable upload to a platform")
    config_platform_parser.add_argument("platform", choices=["instagram", "youtube", "tiktok"],
                                       help="Platform to toggle")
    config_platform_parser.add_argument("action", choices=["enable", "disable"],
                                       help="Action to perform")
    config_platform_parser.set_defaults(func=config_toggle_platform)
    
    # Reset config
    config_reset_parser = config_subparsers.add_parser("reset", help="Reset configuration to defaults")
    config_reset_parser.set_defaults(func=config_reset)
    
    # Validate config
    config_validate_parser = config_subparsers.add_parser("validate", help="Validate current configuration")
    config_validate_parser.set_defaults(func=config_validate)
    
    # Retry commands
    retry_parser = subparsers.add_parser("retry", help="Retry failed uploads")
    retry_subparsers = retry_parser.add_subparsers(dest="retry_command", help="Retry commands")
    
    # List failed uploads
    retry_list_parser = retry_subparsers.add_parser("list", help="List all failed uploads")
    retry_list_parser.set_defaults(func=retry_list)
    
    # Retry specific upload
    retry_single_parser = retry_subparsers.add_parser("single", help="Retry specific failed upload")
    retry_single_parser.add_argument("video_name", help="Name of video file")
    retry_single_parser.add_argument("platform", choices=["instagram", "youtube", "tiktok"], 
                                   help="Platform to retry")
    retry_single_parser.set_defaults(func=retry_single)
    
    # Retry all failed uploads
    retry_all_parser = retry_subparsers.add_parser("all", help="Retry all failed uploads")
    retry_all_parser.add_argument("--platforms", help="Comma-separated platforms (default: all)")
    retry_all_parser.set_defaults(func=retry_all)
    
    # Clear failed uploads
    retry_clear_parser = retry_subparsers.add_parser("clear", help="Clear failed uploads")
    retry_clear_parser.add_argument("--platform", choices=["instagram", "youtube", "tiktok"], 
                                  help="Platform to clear (default: all)")
    retry_clear_parser.set_defaults(func=retry_clear)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle nested commands
    if args.command == "config" and not hasattr(args, 'config_command'):
        config_parser.print_help()
        return
    
    if args.command == "retry" and not hasattr(args, 'retry_command'):
        retry_parser.print_help()
        return
    
    # Handle retry command without subcommand - default to list
    if args.command == "retry" and not hasattr(args, 'func'):
        retry_list(args)
        return
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
