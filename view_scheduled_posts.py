#!/usr/bin/env python3
"""View currently scheduled posts."""

import json
from datetime import datetime
from src.analytics.database import AnalyticsDatabase

def main():
    db = AnalyticsDatabase('analytics.db')
    posts = db.get_pending_posts()
    
    print("=" * 80)
    print("CURRENTLY SCHEDULED POSTS")
    print("=" * 80)
    print(f"\nTotal pending posts: {len(posts)}\n")
    
    if not posts:
        print("No posts currently scheduled.")
        print("\nTo schedule videos:")
        print("  1. Open dashboard: python open_dashboard.py")
        print("  2. Go to 'Missed Replays' section")
        print("  3. Select videos and click 'Schedule Selected'")
        return
    
    now = datetime.now()
    
    for i, post in enumerate(posts, 1):
        try:
            metadata = json.loads(post.metadata_json)
        except json.JSONDecodeError:
            metadata = {"title": "Invalid metadata"}
        
        title = metadata.get("title", "No title")
        scheduled_time = post.scheduled_time
        
        # Calculate time until post
        time_diff = scheduled_time - now
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        if time_diff.total_seconds() <= 0:
            countdown = "[READY TO POST NOW]"
        elif hours > 24:
            days = hours // 24
            countdown = f"in {days}d {hours % 24}h"
        else:
            countdown = f"in {hours}h {minutes}m"
        
        print(f"{i}. {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Title: {title[:60]}")
        print(f"   Platforms: {post.platforms}")
        print(f"   Status: {post.status.upper()} {countdown}")
        print(f"   Video: {post.video_path}")
        print()
    
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print()
    print("✓ Review the schedule above")
    print("✓ Open dashboard to make changes: python open_dashboard.py")
    print("✓ Cancel posts you don't want from the dashboard")
    print()
    print("When ready to start posting:")
    print("  .\\start_scheduler.ps1")
    print()
    print("⚠️  Videos will NOT post until you start the scheduler daemon!")
    print()

if __name__ == "__main__":
    main()


