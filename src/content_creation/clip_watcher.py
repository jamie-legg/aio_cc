#!/usr/bin/env python3
import os
import time
import json
from openai import OpenAI
from pathlib import Path
from datetime import datetime
import subprocess
from dotenv import load_dotenv

from .oauth_manager import OAuthManager
from .upload_manager import UploadManager

# Load environment variables
load_dotenv()

# ---- CONFIG ----
WATCH_DIR = Path.home() / "Movies"
PROCESSED_DIR = WATCH_DIR / "Processed"
PROCESSED_DIR.mkdir(exist_ok=True)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize OAuth and Upload managers
oauth_manager = OAuthManager()
upload_manager = UploadManager(oauth_manager)

def is_video_complete(path):
    """Return True when the file is stable (not growing)."""
    size1 = path.stat().st_size
    time.sleep(2)
    size2 = path.stat().st_size
    return size1 == size2

def generate_ai_caption(filename):
    prompt = f"""
    You are a social media strategist.
    Create an engaging, short title and caption for a 30-second gaming or reaction clip.
    The filename is "{filename}".
    Output JSON with keys: title, caption, hashtags.
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    text = completion.choices[0].message.content
    try:
        return json.loads(text)
    except Exception:
        return {"title": text.strip(), "caption": "", "hashtags": ""}

def process_clip(path):
    print(f"[+] Detected new clip: {path.name}")
    if not is_video_complete(path):
        print("...waiting for file to finish writing")
        time.sleep(5)

    ai_meta = generate_ai_caption(path.name)
    print(f"AI generated: {ai_meta.get('title')}")

    # Save JSON metadata
    out_json = PROCESSED_DIR / f"{path.stem}.json"
    with open(out_json, "w") as f:
        json.dump(ai_meta, f, indent=2)

    # Move video to processed folder
    new_path = PROCESSED_DIR / path.name
    path.rename(new_path)
    print(f"[✓] Saved metadata: {out_json}\n[→] Moved clip: {new_path}")
    
    # Upload to social media platforms
    upload_to_social_media(new_path, ai_meta)

def upload_to_social_media(video_path, metadata):
    """Upload video to configured social media platforms."""
    # Check which platforms to upload to
    platforms = []
    if os.getenv("UPLOAD_TO_INSTAGRAM", "true").lower() == "true":
        platforms.append("instagram")
    if os.getenv("UPLOAD_TO_YOUTUBE", "true").lower() == "true":
        platforms.append("youtube")
    if os.getenv("UPLOAD_TO_TIKTOK", "true").lower() == "true":
        platforms.append("tiktok")
    
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
    seen = set(os.listdir(WATCH_DIR))
    print(f"Watching {WATCH_DIR} for new .mov files...")
    while True:
        current = set(os.listdir(WATCH_DIR))
        new_files = [f for f in current - seen if f.endswith(".mov")]
        for f in new_files:
            process_clip(WATCH_DIR / f)
        seen = current
        time.sleep(3)

def main():
    """Main entry point for the clip watcher."""
    watch_folder()

if __name__ == "__main__":
    main()
