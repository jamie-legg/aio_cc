#!/usr/bin/env python3
"""Test script to trigger Discord webhook notification"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from managers.discord_service import DiscordWebhookService
from managers.config_manager import ConfigManager

def test_discord_webhook():
    """Test Discord webhook notification with a sample video"""
    
    # Initialize services
    config_manager = ConfigManager()
    discord_service = DiscordWebhookService()
    
    # Get configured webhooks
    webhooks = config_manager.list_discord_webhooks()
    
    if not webhooks:
        print("[ERROR] No Discord webhooks configured!")
        print("Please add a webhook through the dashboard first.")
        return
    
    print(f"[SUCCESS] Found {len(webhooks)} Discord webhook(s)")
    
    # Test with a sample video
    test_video = Path("test_videos/test_shorts_1.mp4")
    if not test_video.exists():
        print(f"[ERROR] Test video not found: {test_video}")
        return
    
    print(f"[TEST] Testing with video: {test_video.name}")
    
    # Sample metadata
    metadata = {
        "title": "Test Video Upload - Discord Webhook Test",
        "caption": "This is a test notification from the AIOCC system! 🎮",
        "hashtags": "#test #discord #webhook"
    }
    
    # Test each webhook
    for webhook in webhooks:
        webhook_name = webhook.get("name", "Unnamed")
        webhook_url = webhook.get("url")
        platforms = webhook.get("platforms", [])
        
        print(f"\n[WEBHOOK] Testing webhook: {webhook_name}")
        print(f"   Platforms: {', '.join(platforms)}")
        print(f"   URL: {webhook_url[:50]}..." if len(webhook_url) > 50 else f"   URL: {webhook_url}")
        
        # Test with each platform configured for this webhook
        for platform in platforms:
            print(f"\n   [SEND] Sending test notification for {platform.upper()}...")
            
            # Send notification
            success = discord_service.send_upload_notification(
                webhook_url=webhook_url,
                platform=platform,
                title=metadata["title"],
                video_url="https://example.com/test-video"  # Sample URL
            )
            
            if success:
                print(f"   [SUCCESS] Successfully sent {platform.upper()} notification!")
            else:
                print(f"   [ERROR] Failed to send {platform.upper()} notification")
    
    print(f"\n[COMPLETE] Discord webhook test completed!")
    print("Check your Discord channel(s) for the test notifications!")

if __name__ == "__main__":
    test_discord_webhook()