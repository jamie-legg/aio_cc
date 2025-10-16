#!/usr/bin/env python3
"""Example script demonstrating Tron lightbike transition generation"""

import os
import sys
import time
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from content_creation.sora_transitions import SoraTransitionGenerator, TransitionConfig

def demo_racing_transitions():
    """Demonstrate racing-style lightbike transitions"""
    print("🏁 Generating Racing Transitions Demo")
    print("=" * 50)
    
    generator = SoraTransitionGenerator("demo_transitions")
    
    # Generate 2 racing transitions
    transitions = generator.generate_transition_batch("racing", count=2)
    
    print(f"\n✅ Generated {len(transitions)} racing transitions:")
    for i, transition in enumerate(transitions, 1):
        print(f"  {i}. {transition.video_id} - {transition.status}")
    
    return transitions

def demo_custom_transition():
    """Demonstrate custom transition generation"""
    print("\n🎨 Generating Custom Transition Demo")
    print("=" * 50)
    
    generator = SoraTransitionGenerator("demo_transitions")
    
    custom_prompt = """
    A sleek neon blue lightbike racing through a digital cityscape at night, 
    leaving glowing trails that form geometric patterns in the air. 
    The bike performs a gravity-defying jump over a glowing bridge, 
    with neon particles cascading down like digital rain. 
    Cyberpunk aesthetic, cinematic lighting, high-speed motion blur.
    """
    
    transition = generator.generate_transition(custom_prompt.strip(), "custom")
    
    print(f"✅ Custom transition generated: {transition.video_id}")
    return transition

def demo_environmental_transitions():
    """Demonstrate environmental/atmospheric transitions"""
    print("\n🌃 Generating Environmental Transitions Demo")
    print("=" * 50)
    
    generator = SoraTransitionGenerator("demo_transitions")
    
    # Generate 1 environmental transition
    transitions = generator.generate_transition_batch("environmental", count=1)
    
    print(f"✅ Generated {len(transitions)} environmental transitions:")
    for transition in transitions:
        print(f"  - {transition.video_id} - {transition.status}")
    
    return transitions

def demo_transition_management():
    """Demonstrate transition management features"""
    print("\n📋 Transition Management Demo")
    print("=" * 50)
    
    generator = SoraTransitionGenerator("demo_transitions")
    
    # List all generated transitions
    all_transitions = generator.list_generated_transitions()
    print(f"📊 Total transitions generated: {len(all_transitions)}")
    
    # List by type
    for transition_type in ["racing", "transitions", "environmental", "custom"]:
        type_transitions = generator.list_generated_transitions(transition_type)
        print(f"  {transition_type}: {len(type_transitions)} transitions")
    
    # Check status of a specific transition (if any exist)
    if all_transitions:
        first_transition = all_transitions[0]
        video_id = first_transition["video_id"]
        print(f"\n🔍 Checking status of {video_id}...")
        status = generator.get_transition_status(video_id)
        if status:
            print(f"  Status: {status['status']}")
            print(f"  Created: {status['created_at']}")

def main():
    """Run the complete demo"""
    print("🚀 Tron Lightbike Transition Generation Demo")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file or environment")
        return
    
    try:
        # Run demos
        racing_transitions = demo_racing_transitions()
        custom_transition = demo_custom_transition()
        environmental_transitions = demo_environmental_transitions()
        demo_transition_management()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📁 Check the 'demo_transitions' directory for generated metadata files")
        print("💡 Use 'uv run content-cli transitions list' to see all generated transitions")
        print("🔍 Use 'uv run content-cli transitions status <video_id>' to check specific status")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
