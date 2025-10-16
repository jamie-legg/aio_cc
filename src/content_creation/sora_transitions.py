"""Sora 2 Transition Generation Pipeline for Tron Lightbike Sequences"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv
from analytics.video_tracker import track_sora_video_creation

# Load environment variables
load_dotenv()

@dataclass
class TransitionConfig:
    """Configuration for transition generation"""
    style: str = "tron_lightbike"
    duration: int = 5  # seconds
    resolution: str = "1920x1080"
    fps: int = 24
    quality: str = "high"

@dataclass
class GeneratedTransition:
    """Generated transition video metadata"""
    video_id: str
    prompt: str
    status: str
    created_at: str
    file_path: Optional[str] = None
    duration: Optional[float] = None

class TronLightbikePrompts:
    """Collection of Tron lightbike specific prompts for different transition types"""
    
    @staticmethod
    def get_lightbike_race_prompts() -> List[str]:
        """Get prompts for high-speed lightbike racing sequences"""
        return [
            "A sleek neon blue lightbike racing through a dark digital grid at incredible speed, leaving glowing trails, cyberpunk aesthetic, futuristic racing scene",
            "Two lightbikes in a high-speed chase through a neon-lit digital highway, sparks flying, dramatic lighting, Tron-style racing",
            "A lightbike performing a gravity-defying jump over a digital chasm, neon trails arcing through the void, cinematic lighting",
            "Multiple lightbikes racing in formation through a glowing tunnel, neon reflections on the walls, high-speed motion blur",
            "A lightbike skidding around a sharp corner, neon sparks flying, dramatic camera angle, cyberpunk racing scene"
        ]
    
    @staticmethod
    def get_transition_prompts() -> List[str]:
        """Get prompts for smooth transition sequences"""
        return [
            "A lightbike materializing from digital particles, neon blue energy coalescing into solid form, smooth transition effect",
            "A lightbike dissolving into light trails that reform into a different shape, seamless digital transformation",
            "A lightbike accelerating from zero to incredible speed, neon trails building up behind it, smooth motion blur transition",
            "A lightbike morphing through different geometric shapes while maintaining speed, fluid digital transformation",
            "A lightbike splitting into multiple copies that converge back into one, digital replication effect"
        ]
    
    @staticmethod
    def get_environmental_prompts() -> List[str]:
        """Get prompts for environmental/atmospheric sequences"""
        return [
            "A lightbike racing through a neon-lit cityscape at night, reflections on wet streets, cyberpunk atmosphere",
            "A lightbike navigating through a digital forest of glowing trees, neon particles floating in the air",
            "A lightbike racing across a vast digital plain under a starry sky, neon trails stretching to the horizon",
            "A lightbike ascending a spiral digital tower, neon energy spiraling upward, gravity-defying motion",
            "A lightbike racing through a tunnel of pure light, energy walls pulsing with neon colors"
        ]

class SoraTransitionGenerator:
    """Main class for generating Tron lightbike transitions using Sora 2"""
    
    def __init__(self, output_dir: str = "generated_transitions"):
        self.client = OpenAI()
        self.output_dir = output_dir
        self.prompts = TronLightbikePrompts()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create subdirectories for different types
        self.dirs = {
            'racing': os.path.join(output_dir, 'racing'),
            'transitions': os.path.join(output_dir, 'transitions'),
            'environmental': os.path.join(output_dir, 'environmental'),
            'custom': os.path.join(output_dir, 'custom')
        }
        
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def generate_transition(self, 
                          prompt: str, 
                          transition_type: str = "custom",
                          config: Optional[TransitionConfig] = None) -> GeneratedTransition:
        """Generate a single transition video"""
        
        if config is None:
            config = TransitionConfig()
        
        print(f"🎬 Generating {transition_type} transition...")
        print(f"📝 Prompt: {prompt}")
        
        try:
            # Generate video using Sora 2
            video = self.client.videos.create(
                model="sora-2",
                prompt=prompt,
                duration=5,  # 5 seconds as requested
            )
            
            # Create transition object
            transition = GeneratedTransition(
                video_id=video.id,
                prompt=prompt,
                status=video.status,
                created_at=str(video.created_at)
            )
            
            # Track in analytics
            track_sora_video_creation(
                video_id=video.id,
                prompt=prompt,
                duration=config.duration
            )
            
            # Save metadata
            self._save_transition_metadata(transition, transition_type)
            
            print(f"✅ Transition generation started!")
            print(f"🆔 Video ID: {video.id}")
            print(f"📊 Status: {video.status}")
            
            return transition
            
        except Exception as e:
            print(f"❌ Error generating transition: {e}")
            raise
    
    def generate_transition_batch(self, 
                                transition_type: str = "racing",
                                count: int = 3,
                                config: Optional[TransitionConfig] = None) -> List[GeneratedTransition]:
        """Generate multiple transitions of a specific type"""
        
        if transition_type == "racing":
            prompts = self.prompts.get_lightbike_race_prompts()
        elif transition_type == "transitions":
            prompts = self.prompts.get_transition_prompts()
        elif transition_type == "environmental":
            prompts = self.prompts.get_environmental_prompts()
        else:
            raise ValueError(f"Unknown transition type: {transition_type}")
        
        # Limit to available prompts
        count = min(count, len(prompts))
        selected_prompts = prompts[:count]
        
        print(f"🎬 Generating {count} {transition_type} transitions...")
        
        transitions = []
        for i, prompt in enumerate(selected_prompts, 1):
            print(f"\n--- Generating transition {i}/{count} ---")
            try:
                transition = self.generate_transition(prompt, transition_type, config)
                transitions.append(transition)
                
                # Add delay between requests to avoid rate limiting
                if i < count:
                    print("⏳ Waiting 2 seconds before next generation...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Failed to generate transition {i}: {e}")
                continue
        
        print(f"\n✅ Generated {len(transitions)} transitions successfully!")
        return transitions
    
    def _save_transition_metadata(self, transition: GeneratedTransition, transition_type: str):
        """Save transition metadata to file"""
        
        output_file = os.path.join(
            self.dirs[transition_type], 
            f"{transition.video_id}_metadata.json"
        )
        
        metadata = {
            "video_id": transition.video_id,
            "prompt": transition.prompt,
            "status": transition.status,
            "created_at": transition.created_at,
            "transition_type": transition_type,
            "file_path": transition.file_path,
            "duration": transition.duration
        }
        
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def list_generated_transitions(self, transition_type: str = None) -> List[Dict]:
        """List all generated transitions"""
        
        transitions = []
        
        if transition_type:
            dirs_to_check = [self.dirs[transition_type]]
        else:
            dirs_to_check = self.dirs.values()
        
        for dir_path in dirs_to_check:
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.endswith('_metadata.json'):
                        metadata_file = os.path.join(dir_path, file)
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                transitions.append(metadata)
                        except Exception as e:
                            print(f"Error reading {metadata_file}: {e}")
        
        return transitions
    
    def get_transition_status(self, video_id: str) -> Optional[Dict]:
        """Check the status of a specific transition"""
        try:
            video = self.client.videos.retrieve(video_id)
            return {
                "video_id": video.id,
                "status": video.status,
                "created_at": str(video.created_at)
            }
        except Exception as e:
            print(f"Error retrieving video {video_id}: {e}")
            return None

def main():
    """CLI interface for the transition generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Tron lightbike transitions using Sora 2")
    parser.add_argument("-p", "--prompt", help="Custom prompt for transition generation")
    parser.add_argument("-t", "--type", choices=["racing", "transitions", "environmental"], 
                       default="racing", help="Type of transitions to generate")
    parser.add_argument("-c", "--count", type=int, default=1, help="Number of transitions to generate")
    parser.add_argument("-o", "--output", default="generated_transitions", help="Output directory")
    parser.add_argument("--list", action="store_true", help="List generated transitions")
    parser.add_argument("--status", help="Check status of specific video ID")
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return
    
    generator = SoraTransitionGenerator(args.output)
    
    if args.list:
        transitions = generator.list_generated_transitions()
        print(f"\n📋 Found {len(transitions)} generated transitions:")
        for t in transitions:
            print(f"  🆔 {t['video_id']} - {t['status']} - {t['transition_type']}")
        return
    
    if args.status:
        status = generator.get_transition_status(args.status)
        if status:
            print(f"📊 Status for {args.status}: {status['status']}")
        return
    
    if args.prompt:
        # Generate single custom transition
        transition = generator.generate_transition(args.prompt, "custom")
        print(f"✅ Custom transition generated: {transition.video_id}")
    else:
        # Generate batch of transitions
        transitions = generator.generate_transition_batch(args.type, args.count)
        print(f"✅ Generated {len(transitions)} {args.type} transitions")

if __name__ == "__main__":
    main()
