#!/usr/bin/env python3
"""Test script for OBS Studio detection."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from content_creation.obs_detector import OBSDetector, print_obs_info

if __name__ == "__main__":
    print("\n🎬 Testing OBS Studio Detection\n")
    
    # Create detector and get info
    detector = OBSDetector()
    info = detector.get_obs_info()
    
    # Print detailed info
    print_obs_info()
    
    # Test suggested watch directory
    suggested_dir = detector.suggest_watch_directory()
    if suggested_dir:
        print(f"✓ Suggested Watch Directory: {suggested_dir}")
    else:
        print("✗ No watch directory suggestion available")
    
    print("\n" + "=" * 50)
    
    # Show recommendation
    if info['replay_buffer_path']:
        print("\n✅ OBS Replay Buffer Detected!")
        print(f"   The watcher will automatically use: {info['replay_buffer_path']}")
        print("\n   To test, drop a video file in this directory and run:")
        print("   uv run python main.py")
    elif info['obs_installed']:
        print("\n⚠️  OBS is installed but replay buffer not configured")
        print("\n   To configure replay buffer in OBS:")
        print("   1. Open OBS Studio")
        print("   2. Go to Settings → Output")
        print("   3. Set 'Recording Path' or 'Replay Buffer Path'")
        print("   4. Click OK")
        print("   5. Restart this script")
    else:
        print("\n✗ OBS Studio not detected")
        print("\n   Please manually configure watch directory in config.json")
    
    print("\n")

