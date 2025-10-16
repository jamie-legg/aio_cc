#!/usr/bin/env python3
"""Sora 2 Video Generation Test Script"""

import argparse
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_video(prompt: str, output_dir: str = "generated_videos"):
    """Generate a video using Sora 2"""
    
    # Initialize OpenAI client
    client = OpenAI()
    
    print(f"🎬 Generating video with prompt: '{prompt}'")
    print("⏳ This may take several minutes...")
    
    try:
        # Generate video using Sora 2
        video = client.videos.create(
            model="sora-2",
            prompt=prompt,
        )
        
        print("✅ Video generation started successfully!")
        print(f"📹 Video ID: {video.id}")
        print(f"🔗 Status: {video.status}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save video info to file
        info_file = os.path.join(output_dir, f"{video.id}_info.txt")
        with open(info_file, 'w') as f:
            f.write(f"Video ID: {video.id}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write(f"Status: {video.status}\n")
            f.write(f"Created: {video.created_at}\n")
        
        print(f"💾 Video info saved to: {info_file}")
        print(f"📁 Output directory: {output_dir}")
        
        return video
        
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate videos using Sora 2")
    parser.add_argument("-p", "--prompt", required=True, help="Video generation prompt")
    parser.add_argument("-o", "--output", default="generated_videos", help="Output directory for generated videos")
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file or environment")
        return
    
    generate_video(args.prompt, args.output)

if __name__ == "__main__":
    main()
