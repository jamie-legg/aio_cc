#!/usr/bin/env python3
"""Check the status of uploads and replays."""

from src.analytics.database import AnalyticsDatabase

def main():
    db = AnalyticsDatabase('analytics.db')
    
    # Check failed uploads
    failed_data = db.get_failed_uploads()
    failed_uploads = failed_data.get('failed_uploads', [])
    
    # Check missed replays
    missed_replays = db.get_missed_replays()
    
    # Check scheduled posts
    pending_posts = db.get_pending_posts()
    
    print("=" * 60)
    print("UPLOAD STATUS")
    print("=" * 60)
    print(f"Pending scheduled posts: {len(pending_posts)}")
    print(f"Failed uploads: {len(failed_uploads)}")
    print(f"Missed replays: {len(missed_replays)}")
    print("=" * 60)
    
    if failed_uploads:
        print("\nFAILED UPLOADS:")
        for upload in failed_uploads[:5]:
            print(f"  - {upload.get('metadata', {}).get('title', 'Unknown')}")
            print(f"    Platform: {upload.get('platform')}")
            print(f"    Error: {upload.get('error', 'Unknown error')[:60]}")
    
    if missed_replays:
        print(f"\nMISSED REPLAYS: {len(missed_replays)} videos available")
        print("Use the dashboard to schedule these properly")

if __name__ == "__main__":
    main()


