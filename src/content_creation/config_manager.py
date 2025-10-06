"""Configuration manager for content creation settings."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class Config:
    """Configuration settings for the content creation tool."""
    watch_dir: str = str(Path.home() / "Movies")
    processed_dir: str = str(Path.home() / "Movies" / "Processed")
    video_extensions: list = None
    upload_to_instagram: bool = True
    upload_to_youtube: bool = True
    upload_to_tiktok: bool = True
    
    def __post_init__(self):
        if self.video_extensions is None:
            self.video_extensions = [".mov", ".mp4", ".avi", ".mkv", ".wmv"]

class ConfigManager:
    """Manages configuration settings for the content creation tool."""
    
    def __init__(self, config_file: Path = Path.home() / ".content_creation" / "config.json"):
        self.config_file = config_file
        self.config_file.parent.mkdir(exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Config:
        """Load configuration from file or create default."""
        if not self.config_file.exists():
            return Config()
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return Config(**data)
        except Exception as e:
            print(f"Error loading config: {e}")
            return Config()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_config(self) -> Config:
        """Get current configuration."""
        return self.config
    
    def set_watch_dir(self, path: str) -> bool:
        """Set the watch directory for video files."""
        watch_path = Path(path).expanduser().resolve()
        
        if not watch_path.exists():
            print(f"Error: Directory {watch_path} does not exist")
            return False
        
        if not watch_path.is_dir():
            print(f"Error: {watch_path} is not a directory")
            return False
        
        self.config.watch_dir = str(watch_path)
        self._save_config()
        print(f"Watch directory set to: {watch_path}")
        return True
    
    def set_processed_dir(self, path: str) -> bool:
        """Set the processed directory for completed videos."""
        processed_path = Path(path).expanduser().resolve()
        
        # Create directory if it doesn't exist
        try:
            processed_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {processed_path}: {e}")
            return False
        
        self.config.processed_dir = str(processed_path)
        self._save_config()
        print(f"Processed directory set to: {processed_path}")
        return True
    
    def set_video_extensions(self, extensions: list) -> bool:
        """Set the video file extensions to watch for."""
        # Ensure extensions start with dot
        normalized_extensions = []
        for ext in extensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            normalized_extensions.append(ext.lower())
        
        self.config.video_extensions = normalized_extensions
        self._save_config()
        print(f"Video extensions set to: {', '.join(normalized_extensions)}")
        return True
    
    def set_upload_platform(self, platform: str, enabled: bool) -> bool:
        """Enable or disable upload to a specific platform."""
        if platform == "instagram":
            self.config.upload_to_instagram = enabled
        elif platform == "youtube":
            self.config.upload_to_youtube = enabled
        elif platform == "tiktok":
            self.config.upload_to_tiktok = enabled
        else:
            print(f"Unknown platform: {platform}")
            return False
        
        self._save_config()
        status = "enabled" if enabled else "disabled"
        print(f"Upload to {platform.upper()} {status}")
        return True
    
    def get_upload_platforms(self) -> list:
        """Get list of enabled upload platforms."""
        platforms = []
        if self.config.upload_to_instagram:
            platforms.append("instagram")
        if self.config.upload_to_youtube:
            platforms.append("youtube")
        if self.config.upload_to_tiktok:
            platforms.append("tiktok")
        return platforms
    
    def show_config(self):
        """Display current configuration."""
        print("=== Content Creation Configuration ===")
        print(f"Watch Directory: {self.config.watch_dir}")
        print(f"Processed Directory: {self.config.processed_dir}")
        print(f"Video Extensions: {', '.join(self.config.video_extensions)}")
        print(f"Upload Platforms: {', '.join(self.get_upload_platforms())}")
        
        # Check if directories exist
        watch_path = Path(self.config.watch_dir)
        processed_path = Path(self.config.processed_dir)
        
        print(f"\n=== Directory Status ===")
        print(f"Watch Directory: {'✅ Exists' if watch_path.exists() else '❌ Not found'}")
        print(f"Processed Directory: {'✅ Exists' if processed_path.exists() else '❌ Not found'}")
        
        if watch_path.exists():
            # Count video files in watch directory
            video_count = 0
            for ext in self.config.video_extensions:
                video_count += len(list(watch_path.glob(f"*{ext}")))
            print(f"Video files in watch directory: {video_count}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = Config()
        self._save_config()
        print("Configuration reset to defaults")
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        errors = []
        
        # Check watch directory
        watch_path = Path(self.config.watch_dir)
        if not watch_path.exists():
            errors.append(f"Watch directory does not exist: {watch_path}")
        elif not watch_path.is_dir():
            errors.append(f"Watch directory is not a directory: {watch_path}")
        
        # Check processed directory (create if needed)
        processed_path = Path(self.config.processed_dir)
        try:
            processed_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create processed directory: {e}")
        
        # Check video extensions
        if not self.config.video_extensions:
            errors.append("No video extensions configured")
        
        if errors:
            print("Configuration validation failed:")
            for error in errors:
                print(f"  ❌ {error}")
            return False
        
        print("✅ Configuration is valid")
        return True
