"""AI Manager for generating social media metadata using OpenAI."""

import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIManager:
    """Manages AI-powered content generation for social media metadata."""
    
    def __init__(self):
        """Initialize the AI manager with OpenAI client."""
        self.client = OpenAI()
        self.model = "gpt-4o-mini"  # Using gpt-4o-mini for better reliability
    
    def generate_metadata(self, filename: str, game_context: str = "gaming") -> Dict[str, Any]:
        """
        Generate social media metadata for a video file.
        
        Args:
            filename: Name of the video file
            game_context: Context about the game being played
            
        Returns:
            Dictionary containing title, caption, and hashtags
        """
        try:
            # Create the prompt based on game context
            prompt = self._create_prompt(filename, game_context)
            
            # Generate metadata using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "video_metadata",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "The title of the video."
                                },
                                "caption": {
                                    "type": "string",
                                    "description": "A descriptive caption for the video."
                                },
                                "hashtags": {
                                    "type": "array",
                                    "description": "A list of hashtags associated with the video.",
                                    "items": {
                                        "type": "string",
                                        "description": "A single hashtag, including the # symbol.",
                                        "pattern": "^#\\w+$"
                                    }
                                }
                            },
                            "required": [
                                "title",
                                "caption",
                                "hashtags"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                temperature=0.8,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            metadata = json.loads(content)
            
            # Convert hashtags array to string for compatibility with existing code
            if isinstance(metadata.get('hashtags'), list):
                metadata['hashtags'] = ' '.join(metadata['hashtags'])
            
            print(f"🤖 AI generated metadata for {filename}")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Caption: {metadata.get('caption', 'N/A')[:50]}...")
            print(f"   Hashtags: {metadata.get('hashtags', 'N/A')}")
            
            return metadata
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse AI response as JSON: {e}")
            return self._get_fallback_metadata(filename)
        except Exception as e:
            print(f"❌ AI generation failed: {e}")
            return self._get_fallback_metadata(filename)
    
    def _create_prompt(self, filename: str, game_context: str) -> str:
        """Create a prompt for AI metadata generation."""
        if "armagetron" in game_context.lower() or "tron" in game_context.lower():
            return f"""You are a social media strategist. It needs to be super hype. It needs to be super gen z,
no capitals, kinda dry, sarcastic, but full of bait and alpha.
Skull emojis and wilting flower emojis are your favorite emojis. add them at the end either 2 or 3 of any
In this video, we beat someone at a game. Embarassed them. Make it clickbait.

The game is armagetron advanced. It's a tron clone lightcycle snake game. Highly fast reactions and predictions. Infinite skill ceiling. Hashtags should be very short and generic 
retrocycles, satisfying, tron, max 4.

include an emoji in the title

Filename: {filename}"""
        else:
            return f"""You are a social media strategist. It needs to be super hype. It needs to be super gen z,
no capitals, kinda dry, sarcastic, but full of bait and alpha.
Skull emojis and wilting flower emojis are your favorite emojis. add them at the end either 2 or 3 of any
In this video, we beat someone at a game. Embarassed them. Make it clickbait.

Create an engaging, short title and caption for a 30-second gaming or reaction clip.
The filename is "{filename}".

Output JSON with keys: title, caption, hashtags."""
    
    def _get_fallback_metadata(self, filename: str) -> Dict[str, Any]:
        """Get fallback metadata when AI generation fails."""
        return {
            "title": f"epic gaming moment - {filename} 🎮",
            "caption": "check out this insane play! we totally owned them 💀🥀",
            "hashtags": "#gaming #shorts #epic #clutch"
        }
    
    def generate_metadata_for_game(self, filename: str, game_name: str) -> Dict[str, Any]:
        """Generate metadata with specific game context."""
        return self.generate_metadata(filename, game_name)