"""Command-line interface for content creation tools."""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from managers.oauth_manager import OAuthManager
from managers.upload_manager import UploadManager
from managers.config_manager import ConfigManager
from content_creation.sora_transitions import SoraTransitionGenerator
from content_creation.video_processor import VideoProcessor
from content_creation.scheduler import PostScheduler
from analytics.database import AnalyticsDatabase, ScheduledPost

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
        if oauth_manager.is_authenticated(platform):
            print(f"[SUCCESS] {platform.upper()}: Authenticated")
            
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

def reset_auth(args):
    """Reset authentication and data for a platform."""
    oauth_manager = OAuthManager()
    
    if args.platform == "instagram":
        print("🔄 Resetting Instagram authentication and data...")
        
        # Reset authentication
        oauth_manager.reset_platform_auth("instagram")
        
        # Reset analytics data
        from analytics.database import AnalyticsDatabase
        db = AnalyticsDatabase()
        db.reset_platform_data("instagram")
        
        print("✅ Instagram reset complete! You can now run 'make auth instagram' to re-authenticate.")
        
    elif args.platform == "youtube":
        print("🔄 Resetting YouTube authentication and data...")
        
        # Reset authentication
        oauth_manager.reset_platform_auth("youtube")
        
        # Reset analytics data
        from analytics.database import AnalyticsDatabase
        db = AnalyticsDatabase()
        db.reset_platform_data("youtube")
        
        print("✅ YouTube reset complete! You can now run 'make auth youtube' to re-authenticate.")
        
    elif args.platform == "tiktok":
        print("🔄 Resetting TikTok authentication and data...")
        
        # Reset authentication
        oauth_manager.reset_platform_auth("tiktok")
        
        # Reset analytics data
        from analytics.database import AnalyticsDatabase
        db = AnalyticsDatabase()
        db.reset_platform_data("tiktok")
        
        print("✅ TikTok reset complete! You can now run 'make auth tiktok' to re-authenticate.")
        
    else:
        print(f"Unknown platform: {args.platform}")
        return

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

def config_set_backend(args):
    """Set backend API configuration."""
    config_manager = ConfigManager()
    
    api_url = args.api_url if hasattr(args, 'api_url') and args.api_url else None
    api_key = args.api_key if hasattr(args, 'api_key') and args.api_key else None
    use_backend = args.use_backend if hasattr(args, 'use_backend') else None
    
    config_manager.set_backend_config(
        api_url=api_url,
        api_key=api_key,
        use_backend=use_backend
    )

def generate_transitions(args):
    """Generate Tron lightbike transitions using Sora 2."""
    generator = SoraTransitionGenerator(args.output)
    
    if args.prompt:
        # Generate single custom transition
        transition = generator.generate_transition(args.prompt, "custom")
        print(f"✅ Custom transition generated: {transition.video_id}")
    else:
        # Generate batch of transitions
        transitions = generator.generate_transition_batch(args.type, args.count)
        print(f"✅ Generated {len(transitions)} {args.type} transitions")

def list_transitions(args):
    """List generated transitions."""
    generator = SoraTransitionGenerator(args.output)
    transitions = generator.list_generated_transitions(args.type)
    
    print(f"\n📋 Found {len(transitions)} generated transitions:")
    for t in transitions:
        print(f"  🆔 {t['video_id']} - {t['status']} - {t['transition_type']}")

def check_transition_status(args):
    """Check status of a specific transition."""
    generator = SoraTransitionGenerator()
    status = generator.get_transition_status(args.video_id)
    if status:
        print(f"📊 Status for {args.video_id}: {status['status']}")
    else:
        print(f"❌ Could not retrieve status for {args.video_id}")

def add_outro(args):
    """Add outro image to a video."""
    video_path = Path(args.video)
    outro_path = Path(args.outro) if args.outro else Path("pls_like_follow.png")
    
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        return
    
    if not outro_path.exists():
        print(f"❌ Outro image not found: {outro_path}")
        return
    
    processor = VideoProcessor()
    
    try:
        output_path = Path(args.output) if args.output else None
        result = processor.add_outro_image(
            video_path, 
            outro_path, 
            output_path=output_path,
            outro_duration=args.duration
        )
        print(f"\n✅ Success! Video with outro saved to: {result}")
    except Exception as e:
        print(f"\n❌ Error adding outro: {e}")
        sys.exit(1)

def schedule_add(args):
    """Schedule a video for posting."""
    video_path = Path(args.video)
    
    # Validate video file exists
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    # Parse scheduled time
    try:
        # Support multiple formats
        for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]:
            try:
                scheduled_time = datetime.strptime(args.time, fmt)
                break
            except ValueError:
                continue
        else:
            print(f"❌ Invalid time format: {args.time}")
            print("   Supported formats: YYYY-MM-DD HH:MM, YYYY-MM-DDTHH:MM, YYYY-MM-DD HH:MM:SS")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error parsing time: {e}")
        sys.exit(1)
    
    # Check if time is in the future
    if scheduled_time <= datetime.now():
        print(f"⚠️  Warning: Scheduled time is in the past, post will be uploaded immediately")
    
    # Parse platforms
    platforms = args.platforms.split(',')
    valid_platforms = ['youtube', 'instagram', 'tiktok']
    for platform in platforms:
        if platform.strip() not in valid_platforms:
            print(f"❌ Invalid platform: {platform}")
            print(f"   Valid platforms: {', '.join(valid_platforms)}")
            sys.exit(1)
    
    # Check authentication status
    oauth_manager = OAuthManager()
    unauthenticated = []
    for platform in platforms:
        if not oauth_manager.is_authenticated(platform.strip()):
            unauthenticated.append(platform)
    
    if unauthenticated:
        print(f"⚠️  Warning: Not authenticated for: {', '.join(unauthenticated)}")
        print(f"   Run 'make auth {unauthenticated[0]}' to authenticate")
    
    # Prepare metadata
    metadata = {
        'title': args.title or f"Gaming Clip - {video_path.stem}",
        'caption': args.caption or '',
        'hashtags': args.hashtags or '#gaming'
    }
    
    # Create scheduled post
    db = AnalyticsDatabase()
    post = ScheduledPost(
        video_path=str(video_path.absolute()),
        metadata_json=json.dumps(metadata),
        platforms=args.platforms,
        scheduled_time=scheduled_time,
        status='pending',
        created_at=datetime.now()
    )
    
    post_id = db.add_scheduled_post(post)
    
    print(f"\n✅ Post scheduled successfully!")
    print(f"   Post ID: {post_id}")
    print(f"   Video: {video_path.name}")
    print(f"   Scheduled: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Platforms: {args.platforms}")
    print(f"   Title: {metadata['title']}")

def schedule_list(args):
    """List scheduled posts."""
    db = AnalyticsDatabase()
    
    posts = db.list_scheduled_posts(
        status=args.status,
        platform=args.platform,
        limit=args.limit
    )
    
    if not posts:
        print("No scheduled posts found")
        return
    
    print(f"\n📋 Found {len(posts)} scheduled post(s):\n")
    
    for post in posts:
        video_name = Path(post.video_path).name
        scheduled_time = post.scheduled_time if isinstance(post.scheduled_time, str) else post.scheduled_time.strftime('%Y-%m-%d %H:%M')
        
        status_emoji = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'failed': '❌',
            'cancelled': '🚫'
        }.get(post.status, '❓')
        
        print(f"{status_emoji} ID: {post.id} | {video_name}")
        print(f"   Scheduled: {scheduled_time} | Platforms: {post.platforms}")
        print(f"   Status: {post.status}", end='')
        
        if post.retry_count > 0:
            print(f" (retries: {post.retry_count})", end='')
        print()
        
        if post.error_message:
            print(f"   Error: {post.error_message}")
        
        print()

def schedule_remove(args):
    """Remove/cancel a scheduled post."""
    db = AnalyticsDatabase()
    
    # Check if post exists
    post = db.get_scheduled_post(args.post_id)
    if not post:
        print(f"❌ Post {args.post_id} not found")
        sys.exit(1)
    
    if post.status != 'pending':
        print(f"❌ Cannot cancel post {args.post_id} with status: {post.status}")
        print("   Only pending posts can be cancelled")
        sys.exit(1)
    
    # Cancel the post
    success = db.cancel_scheduled_post(args.post_id)
    
    if success:
        print(f"✅ Post {args.post_id} cancelled successfully")
    else:
        print(f"❌ Failed to cancel post {args.post_id}")
        sys.exit(1)

def schedule_status(args):
    """Show scheduler status."""
    scheduler = PostScheduler()
    status = scheduler.get_status()
    
    if 'error' in status:
        print(f"❌ Error getting scheduler status: {status['error']}")
        sys.exit(1)
    
    print("\n📊 Scheduler Status\n")
    print(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
    print(f"\nPost Statistics:")
    print(f"  Pending: {status['stats']['pending']}")
    print(f"  Processing: {status['stats']['processing']}")
    print(f"  Completed: {status['stats']['completed']}")
    print(f"  Failed: {status['stats']['failed']}")
    
    if status['upcoming']:
        print(f"\n📅 Upcoming Posts (next {len(status['upcoming'])}):\n")
        for post in status['upcoming']:
            video_name = Path(post.video_path).name
            scheduled_time = post.scheduled_time if isinstance(post.scheduled_time, str) else post.scheduled_time.strftime('%Y-%m-%d %H:%M')
            print(f"  • {video_name} - {scheduled_time} ({post.platforms})")
    
    if status['recent']:
        print(f"\n📝 Recent Activity (last {len(status['recent'])}):\n")
        for post in status['recent'][:5]:
            video_name = Path(post.video_path).name
            status_emoji = {'pending': '⏳', 'processing': '🔄', 'completed': '✅', 'failed': '❌', 'cancelled': '🚫'}.get(post.status, '❓')
            print(f"  {status_emoji} {video_name} - {post.status}")

def schedule_run(args):
    """Run the scheduler daemon."""
    print("🚀 Starting Post Scheduler...")
    print(f"   Check interval: {args.interval} seconds")
    print(f"   Mode: {'Single-pass' if args.once else 'Continuous'}")
    print(f"   Press Ctrl+C to stop\n")
    
    scheduler = PostScheduler(
        check_interval=args.interval
    )
    
    try:
        scheduler.run(once=args.once)
    except KeyboardInterrupt:
        print("\n⏹️  Scheduler stopped by user")
    except Exception as e:
        print(f"\n❌ Scheduler error: {e}")
        sys.exit(1)

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
    
    # Reset auth command
    reset_parser = subparsers.add_parser("reset", help="Reset authentication and data for a platform")
    reset_parser.add_argument("platform", choices=["instagram", "youtube", "tiktok"],
                            help="Platform to reset")
    reset_parser.set_defaults(func=reset_auth)
    
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
    
    # Set backend config
    config_backend_parser = config_subparsers.add_parser("set-backend", help="Configure backend API")
    config_backend_parser.add_argument("--api-url", help="Backend API URL")
    config_backend_parser.add_argument("--api-key", help="Your API key")
    config_backend_parser.add_argument("--use-backend", type=bool, help="Enable/disable backend API")
    config_backend_parser.set_defaults(func=config_set_backend)
    
    # Transition generation commands
    transition_parser = subparsers.add_parser("transitions", help="Generate Tron lightbike transitions using Sora 2")
    transition_subparsers = transition_parser.add_subparsers(dest="transition_command", help="Transition commands")
    
    # Generate transitions
    gen_parser = transition_subparsers.add_parser("generate", help="Generate transitions")
    gen_parser.add_argument("-p", "--prompt", help="Custom prompt for transition generation")
    gen_parser.add_argument("-t", "--type", choices=["racing", "transitions", "environmental"], 
                           default="racing", help="Type of transitions to generate")
    gen_parser.add_argument("-c", "--count", type=int, default=1, help="Number of transitions to generate")
    gen_parser.add_argument("-o", "--output", default="generated_transitions", help="Output directory")
    gen_parser.set_defaults(func=generate_transitions)
    
    # List transitions
    list_parser = transition_subparsers.add_parser("list", help="List generated transitions")
    list_parser.add_argument("-t", "--type", help="Filter by transition type")
    list_parser.add_argument("-o", "--output", default="generated_transitions", help="Output directory")
    list_parser.set_defaults(func=list_transitions)
    
    # Check status
    status_parser = transition_subparsers.add_parser("status", help="Check status of a specific transition")
    status_parser.add_argument("video_id", help="Video ID to check")
    status_parser.set_defaults(func=check_transition_status)
    
    # Add outro command
    outro_parser = subparsers.add_parser("add-outro", help="Add outro image to end of video")
    outro_parser.add_argument("video", help="Path to input video file")
    outro_parser.add_argument("-o", "--output", help="Path to output video file (optional)")
    outro_parser.add_argument("--outro", help="Path to outro image (default: pls_like_follow.png)")
    outro_parser.add_argument("-d", "--duration", type=float, default=1.0, 
                             help="Duration of outro in seconds (default: 1.0)")
    outro_parser.set_defaults(func=add_outro)
    
    # Schedule commands
    schedule_parser = subparsers.add_parser("schedule", help="Manage scheduled posts")
    schedule_subparsers = schedule_parser.add_subparsers(dest="schedule_command", help="Schedule commands")
    
    # Schedule add
    schedule_add_parser = schedule_subparsers.add_parser("add", help="Schedule a video for posting")
    schedule_add_parser.add_argument("video", help="Path to video file")
    schedule_add_parser.add_argument("--time", required=True, help="Scheduled time (YYYY-MM-DD HH:MM)")
    schedule_add_parser.add_argument("--platforms", required=True, 
                                    help="Comma-separated platforms (youtube,instagram,tiktok)")
    schedule_add_parser.add_argument("--title", help="Video title")
    schedule_add_parser.add_argument("--caption", help="Video caption")
    schedule_add_parser.add_argument("--hashtags", help="Hashtags")
    schedule_add_parser.set_defaults(func=schedule_add)
    
    # Schedule list
    schedule_list_parser = schedule_subparsers.add_parser("list", help="List scheduled posts")
    schedule_list_parser.add_argument("--status", choices=['pending', 'processing', 'completed', 'failed', 'cancelled'],
                                     help="Filter by status")
    schedule_list_parser.add_argument("--platform", choices=['youtube', 'instagram', 'tiktok'],
                                     help="Filter by platform")
    schedule_list_parser.add_argument("--limit", type=int, default=50, help="Maximum posts to show")
    schedule_list_parser.set_defaults(func=schedule_list)
    
    # Schedule remove
    schedule_remove_parser = schedule_subparsers.add_parser("remove", help="Cancel a scheduled post")
    schedule_remove_parser.add_argument("post_id", type=int, help="Post ID to cancel")
    schedule_remove_parser.set_defaults(func=schedule_remove)
    
    # Schedule status
    schedule_status_parser = schedule_subparsers.add_parser("status", help="Show scheduler status")
    schedule_status_parser.set_defaults(func=schedule_status)
    
    # Schedule run
    schedule_run_parser = schedule_subparsers.add_parser("run", help="Run the scheduler daemon")
    schedule_run_parser.add_argument("--interval", type=int, default=60, 
                                    help="Check interval in seconds (default: 60)")
    schedule_run_parser.add_argument("--once", action="store_true", 
                                    help="Process pending posts once and exit")
    schedule_run_parser.set_defaults(func=schedule_run)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle nested config commands
    if args.command == "config" and not hasattr(args, 'config_command'):
        config_parser.print_help()
        return
    
    # Handle nested transition commands
    if args.command == "transitions" and not hasattr(args, 'transition_command'):
        transition_parser.print_help()
        return
    
    # Handle nested schedule commands
    if args.command == "schedule" and not hasattr(args, 'schedule_command'):
        schedule_parser.print_help()
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
