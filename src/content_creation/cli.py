"""Command-line interface for content creation tools."""

import argparse
import sys
from pathlib import Path
from .oauth_manager import OAuthManager
from .upload_manager import UploadManager
from .config_manager import ConfigManager

def setup_auth(args):
    """Set up authentication for social media platforms."""
    oauth_manager = OAuthManager()
    
    if args.platform == "all":
        results = oauth_manager.authenticate_all()
        print("\n=== Authentication Results ===")
        for platform, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
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
            print(f"✅ {args.platform.upper()} authentication successful!")
        else:
            print(f"❌ {args.platform.upper()} authentication failed!")

def check_auth(args):
    """Check authentication status for platforms."""
    oauth_manager = OAuthManager()
    upload_manager = UploadManager(oauth_manager)
    
    platforms = ["instagram", "youtube", "tiktok"] if args.platform == "all" else [args.platform]
    
    print("=== Authentication Status ===")
    for platform in platforms:
        if oauth_manager.is_authenticated(platform):
            print(f"✅ {platform.upper()}: Authenticated")
            
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
            print(f"❌ {platform.upper()}: Not authenticated")

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
            print(f"✅ {platform.upper()}: {result.url or result.video_id}")
        else:
            print(f"❌ {platform.upper()}: {result.error}")

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
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle nested config commands
    if args.command == "config" and not hasattr(args, 'config_command'):
        config_parser.print_help()
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
