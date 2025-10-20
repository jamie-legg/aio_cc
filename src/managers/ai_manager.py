"""AI Manager for generating social media metadata using OpenAI."""

import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from .api_client import APIClient
from .config_manager import ConfigManager

load_dotenv()

class AIManager:
    """Manages AI-powered content generation for social media metadata."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the AI manager.
        
        Args:
            config_manager: Optional config manager instance
        """
        self.config_manager = config_manager or ConfigManager()
        config = self.config_manager.get_config()
        
        # Initialize OpenAI client for local fallback
        self.client = OpenAI()
        self.model = "gpt-4o-mini"  # Using gpt-4o-mini
        
        # Initialize backend API client if configured
        self.api_client = None
        if config.use_backend_api and config.api_key:
            try:
                self.api_client = APIClient(config.api_key, config.backend_api_url)
                # Test connection
                if self.api_client.test_connection():
                    print("[API] Connected to backend API")
                else:
                    print("[API] Backend API unreachable, will use local mode")
                    self.api_client = None
            except Exception as e:
                print(f"[API] Failed to initialize backend API client: {e}")
                self.api_client = None
    
    def generate_metadata(self, filename: str, game_context: str = "gaming", template_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate social media metadata for a video file.
        
        Uses backend API if available, falls back to local OpenAI.
        Supports custom prompt templates from database.
        
        Args:
            filename: Name of the video file
            game_context: Context about the game being played
            template_id: Optional specific template ID to use
            
        Returns:
            Dictionary containing title, caption, and hashtags
        """
        # Try backend API first if available
        if self.api_client:
            try:
                print("[AI] Using backend API for AI enrichment...")
                metadata = self.api_client.generate_metadata(filename, game_context)
                
                # Sanitize metadata to remove emojis and problematic characters
                metadata = self._sanitize_metadata(metadata)
                
                print(f"[AI] AI generated metadata for {filename}")
                print(f"   Title: {metadata.get('title', 'N/A')}")
                print(f"   Caption: {metadata.get('caption', 'N/A')[:50]}...")
                print(f"   Hashtags: {metadata.get('hashtags', 'N/A')}")
                
                return metadata
                
            except Exception as e:
                print(f"[AI] Backend API failed, falling back to local OpenAI: {e}")
        
        # Fallback to local OpenAI with template support
        return self._generate_metadata_local(filename, game_context, template_id)
    
    def _generate_metadata_local(self, filename: str, game_context: str = "gaming", template_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate metadata using local OpenAI client with optional template support.
        
        Args:
            filename: Name of the video file
            game_context: Context about the game being played
            
        Returns:
            Dictionary containing title, caption, and hashtags
        """
        try:
            print("[AI] Using local OpenAI for AI enrichment...")
            
            # Load template from database if available
            from analytics.database import AnalyticsDatabase
            
            db = AnalyticsDatabase()
            template = None
            
            if template_id:
                template = db.get_prompt_template(template_id)
            else:
                template = db.get_active_prompt_template()
            
            # Create the prompt based on template or default
            if template:
                print(f"[AI] Using template: {template.name}")
                prompt = template.prompt_text.replace("{filename}", filename).replace("{game_context}", game_context)
            else:
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
            
            # Sanitize metadata to remove emojis and problematic characters
            metadata = self._sanitize_metadata(metadata)
            
            print(f"[AI] AI generated metadata for {filename}")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Caption: {metadata.get('caption', 'N/A')[:50]}...")
            print(f"   Hashtags: {metadata.get('hashtags', 'N/A')}")
            
            return metadata
            
        except json.JSONDecodeError as e:
            print(f"[AI] Failed to parse AI response as JSON: {e}")
            return self._get_fallback_metadata(filename)
        except Exception as e:
            print(f"[AI] AI generation failed: {e}")
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
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Remove emojis and problematic characters from metadata."""
        import re
        
        sanitized = {}
        for key, value in metadata.items():
            if isinstance(value, str):
                # Remove emojis and other problematic Unicode characters
                sanitized[key] = re.sub(r'[^\x00-\x7F]+', '', value).strip()
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_fallback_metadata(self, filename: str) -> Dict[str, Any]:
        """Get fallback metadata when AI generation fails."""
        return {
            "title": f"epic gaming moment - {filename}",
            "caption": "check out this insane play! we totally owned them",
            "hashtags": "#gaming #shorts #epic #clutch"
        }
    
    def generate_metadata_for_game(self, filename: str, game_name: str) -> Dict[str, Any]:
        """Generate metadata with specific game context."""
        return self.generate_metadata(filename, game_name)
    
    def check_quota(self) -> Optional[Dict[str, Any]]:
        """
        Check user's quota status (backend API only).
        
        Returns:
            Quota information dictionary or None if not using backend
        """
        if self.api_client:
            try:
                return self.api_client.check_quota()
            except Exception as e:
                print(f"⚠️  Failed to check quota: {e}")
                return None
        return None