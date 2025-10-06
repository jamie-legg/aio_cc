"""Command-line interface for content creation tools."""

import argparse
import sys
from pathlib import Path
from .oauth_manager import OAuthManager
from .upload_manager import UploadManager

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
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
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
