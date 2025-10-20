"""OBS Studio detection and replay buffer directory finder."""

import os
import platform
import configparser
from pathlib import Path
from typing import Optional
import psutil
import logging

logger = logging.getLogger(__name__)


class OBSDetector:
    """Detects OBS Studio and finds replay buffer output directory."""
    
    def __init__(self):
        self.system = platform.system()
        self.obs_config_dir = self._find_obs_config_dir()
    
    def is_obs_running(self) -> bool:
        """Check if OBS Studio is currently running."""
        try:
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info['name'].lower()
                if 'obs' in proc_name or 'obs64' in proc_name or 'obs32' in proc_name:
                    logger.info(f"Found OBS process: {proc.info['name']}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking for OBS process: {e}")
            return False
    
    def _find_obs_config_dir(self) -> Optional[Path]:
        """Find OBS Studio configuration directory."""
        if self.system == 'Windows':
            # Windows: %APPDATA%\obs-studio
            appdata = os.getenv('APPDATA')
            if appdata:
                config_dir = Path(appdata) / 'obs-studio'
                if config_dir.exists():
                    logger.info(f"Found OBS config directory: {config_dir}")
                    return config_dir
        
        elif self.system == 'Darwin':  # macOS
            # macOS: ~/Library/Application Support/obs-studio
            home = Path.home()
            config_dir = home / 'Library' / 'Application Support' / 'obs-studio'
            if config_dir.exists():
                logger.info(f"Found OBS config directory: {config_dir}")
                return config_dir
        
        elif self.system == 'Linux':
            # Linux: ~/.config/obs-studio
            home = Path.home()
            config_dir = home / '.config' / 'obs-studio'
            if config_dir.exists():
                logger.info(f"Found OBS config directory: {config_dir}")
                return config_dir
        
        logger.warning("Could not find OBS config directory")
        return None
    
    def get_active_profile(self) -> Optional[str]:
        """Get the currently active OBS profile name."""
        if not self.obs_config_dir:
            return None
        
        # Read global.ini to find active profile
        global_ini = self.obs_config_dir / 'global.ini'
        if not global_ini.exists():
            logger.warning(f"global.ini not found at {global_ini}")
            return None
        
        try:
            config = configparser.ConfigParser()
            # Read with UTF-8-sig to handle BOM (Byte Order Mark)
            with open(global_ini, 'r', encoding='utf-8-sig') as f:
                config.read_file(f)
            
            if 'Basic' in config and 'Profile' in config['Basic']:
                profile = config['Basic']['Profile']
                logger.info(f"Active OBS profile: {profile}")
                return profile
            
            if 'Basic' in config and 'ProfileDir' in config['Basic']:
                profile_dir = config['Basic']['ProfileDir']
                logger.info(f"Active OBS profile directory: {profile_dir}")
                return profile_dir
        
        except Exception as e:
            logger.error(f"Error reading OBS global config: {e}")
        
        return None
    
    def get_replay_buffer_path(self) -> Optional[Path]:
        """
        Get the replay buffer output directory from OBS configuration.
        
        Returns:
            Path to replay buffer directory or None if not found
        """
        if not self.obs_config_dir:
            logger.warning("OBS config directory not found")
            return None
        
        profile = self.get_active_profile()
        if not profile:
            # Try default profile
            profile = 'Untitled'
            logger.info(f"Using default profile: {profile}")
        
        # Path to profile's basic.ini
        profile_config = self.obs_config_dir / 'basic' / 'profiles' / profile / 'basic.ini'
        
        if not profile_config.exists():
            logger.warning(f"Profile config not found at {profile_config}")
            return None
        
        try:
            config = configparser.ConfigParser()
            # Read with UTF-8-sig to handle BOM (Byte Order Mark)
            with open(profile_config, 'r', encoding='utf-8-sig') as f:
                config.read_file(f)
            
            # Try different possible locations for replay buffer path
            replay_path = None
            
            # Check SimpleOutput section (simple output mode)
            if 'SimpleOutput' in config:
                if 'FilePath' in config['SimpleOutput']:
                    replay_path = config['SimpleOutput']['FilePath']
                    logger.info(f"Found replay buffer path in SimpleOutput: {replay_path}")
                elif 'RecRBFilePath' in config['SimpleOutput']:
                    replay_path = config['SimpleOutput']['RecRBFilePath']
                    logger.info(f"Found replay buffer path in SimpleOutput (RecRBFilePath): {replay_path}")
            
            # Check AdvOut section (advanced output mode)
            if not replay_path and 'AdvOut' in config:
                if 'RecRBFilePath' in config['AdvOut']:
                    replay_path = config['AdvOut']['RecRBFilePath']
                    logger.info(f"Found replay buffer path in AdvOut: {replay_path}")
                elif 'RecFilePath' in config['AdvOut']:
                    replay_path = config['AdvOut']['RecFilePath']
                    logger.info(f"Found replay buffer path in AdvOut (RecFilePath): {replay_path}")
            
            # Check Output section
            if not replay_path and 'Output' in config:
                if 'FilePath' in config['Output']:
                    replay_path = config['Output']['FilePath']
                    logger.info(f"Found replay buffer path in Output: {replay_path}")
            
            if replay_path:
                # Expand environment variables and convert to Path
                replay_path = os.path.expandvars(replay_path)
                replay_path = Path(replay_path)
                
                # Create directory if it doesn't exist
                if not replay_path.exists():
                    logger.warning(f"Replay buffer path does not exist: {replay_path}")
                    try:
                        replay_path.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created replay buffer directory: {replay_path}")
                    except Exception as e:
                        logger.error(f"Failed to create directory: {e}")
                        return None
                
                logger.info(f"✓ Found OBS replay buffer directory: {replay_path}")
                return replay_path
            
            else:
                logger.warning("Could not find replay buffer path in OBS config")
                
                # Log all sections and keys for debugging
                logger.debug("Available config sections and keys:")
                for section in config.sections():
                    logger.debug(f"  [{section}]")
                    for key in config[section]:
                        logger.debug(f"    {key} = {config[section][key]}")
        
        except Exception as e:
            logger.error(f"Error reading OBS profile config: {e}")
        
        return None
    
    def get_obs_info(self) -> dict:
        """
        Get comprehensive OBS information.
        
        Returns:
            Dictionary with OBS status and configuration
        """
        info = {
            'obs_running': self.is_obs_running(),
            'obs_installed': self.obs_config_dir is not None,
            'config_dir': str(self.obs_config_dir) if self.obs_config_dir else None,
            'active_profile': self.get_active_profile(),
            'replay_buffer_path': None
        }
        
        replay_path = self.get_replay_buffer_path()
        if replay_path:
            info['replay_buffer_path'] = str(replay_path)
        
        return info
    
    def suggest_watch_directory(self) -> Optional[Path]:
        """
        Suggest the best watch directory based on OBS configuration.
        
        Returns:
            Path to suggested watch directory or None
        """
        # First try to get replay buffer path
        replay_path = self.get_replay_buffer_path()
        if replay_path and replay_path.exists():
            logger.info(f"Suggesting OBS replay buffer directory: {replay_path}")
            return replay_path
        
        # Fallback to common OBS recording paths
        if self.system == 'Windows':
            # Try Videos folder
            videos_dir = Path.home() / 'Videos'
            if videos_dir.exists():
                logger.info(f"Suggesting Videos directory: {videos_dir}")
                return videos_dir
        
        return None


def auto_detect_obs_directory() -> Optional[Path]:
    """
    Convenience function to automatically detect OBS replay buffer directory.
    
    Returns:
        Path to OBS replay buffer directory or None if not found
    """
    detector = OBSDetector()
    return detector.suggest_watch_directory()


def print_obs_info():
    """Print OBS detection information (for CLI usage)."""
    detector = OBSDetector()
    info = detector.get_obs_info()
    
    print("\n🎬 OBS Studio Detection")
    print("=" * 50)
    print(f"OBS Running: {'✓ Yes' if info['obs_running'] else '✗ No'}")
    print(f"OBS Installed: {'✓ Yes' if info['obs_installed'] else '✗ No'}")
    
    if info['config_dir']:
        print(f"Config Directory: {info['config_dir']}")
    
    if info['active_profile']:
        print(f"Active Profile: {info['active_profile']}")
    
    if info['replay_buffer_path']:
        print(f"\n✓ Replay Buffer Directory Found:")
        print(f"  {info['replay_buffer_path']}")
    else:
        print(f"\n✗ Replay Buffer Directory: Not configured or not found")
    
    print("=" * 50 + "\n")
    
    return info


if __name__ == "__main__":
    # Run detection when executed directly
    print_obs_info()

