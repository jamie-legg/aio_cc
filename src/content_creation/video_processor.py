"""Video processing utilities for social media content."""

import os
import subprocess
from pathlib import Path
from typing import Tuple, Optional
import tempfile

class VideoProcessor:
    """Handles video processing for social media platforms."""
    
    def __init__(self):
        """Initialize the video processor."""
        self.supported_formats = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    
    def process_for_shorts(self, input_path: Path, output_path: Optional[Path] = None, 
                          audio_track: Optional[Path] = None, fade_duration: float = 1.0) -> Path:
        """
        Process video for YouTube Shorts (9:16 aspect ratio) with optional audio and fade effects.
        
        Args:
            input_path: Path to input video file
            output_path: Path for output file (optional, will generate if not provided)
            audio_track: Path to MP3 audio track to mix (optional)
            fade_duration: Duration of fade in/out in seconds (default: 1.0)
            
        Returns:
            Path to processed video file
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        if not self._is_supported_format(input_path):
            raise ValueError(f"Unsupported video format: {input_path.suffix}")
        
        # Validate audio track if provided
        if audio_track and not audio_track.exists():
            raise FileNotFoundError(f"Audio track not found: {audio_track}")
        
        if audio_track and not audio_track.suffix.lower() in ['.mp3', '.wav', '.aac', '.m4a']:
            raise ValueError(f"Unsupported audio format: {audio_track.suffix}")
        
        # Generate output path if not provided
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_shorts{input_path.suffix}"
        
        print(f"🎬 Processing video for Shorts: {input_path.name}")
        print(f"📐 Converting to 9:16 aspect ratio...")
        if audio_track:
            print(f"🎵 Adding audio track: {audio_track.name}")
        if fade_duration > 0:
            print(f"✨ Adding fade in/out: {fade_duration}s")
        
        try:
            # Get video dimensions and duration
            width, height = self._get_video_dimensions(input_path)
            video_info = self.get_video_info(input_path)
            duration = video_info['duration']
            
            print(f"📏 Original dimensions: {width}x{height}")
            print(f"⏱️  Video duration: {duration:.1f}s")
            
            # Calculate target dimensions for 9:16
            target_width, target_height = self._calculate_9_16_dimensions(width, height)
            print(f"🎯 Target dimensions: {target_width}x{target_height}")
            
            # Process video with FFmpeg
            self._convert_to_9_16_with_audio(input_path, output_path, target_width, target_height, 
                                           audio_track, fade_duration, duration)
            
            print(f"✅ Video processed successfully: {output_path.name}")
            return output_path
            
        except Exception as e:
            print(f"❌ Video processing failed: {e}")
            raise
    
    def _is_supported_format(self, file_path: Path) -> bool:
        """Check if video format is supported."""
        return file_path.suffix.lower() in self.supported_formats
    
    def _get_video_dimensions(self, video_path: Path) -> Tuple[int, int]:
        """Get video dimensions using FFprobe."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)
            
            # Find video stream
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    width = int(stream['width'])
                    height = int(stream['height'])
                    return width, height
            
            raise ValueError("No video stream found")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFprobe failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to get video dimensions: {e}")
    
    def _calculate_9_16_dimensions(self, width: int, height: int) -> Tuple[int, int]:
        """Calculate target dimensions for 9:16 aspect ratio."""
        aspect_ratio = 9 / 16
        
        # If video is already 9:16 or close, return original
        current_ratio = width / height
        if abs(current_ratio - aspect_ratio) < 0.1:
            return width, height
        
        # Calculate new dimensions for 9:16 aspect ratio
        if current_ratio > aspect_ratio:
            # Video is too wide (landscape), crop width to make it 9:16
            new_height = height
            new_width = int(height * aspect_ratio)
        else:
            # Video is too tall (portrait), crop height to make it 9:16
            new_width = width
            new_height = int(width / aspect_ratio)
        
        # Ensure dimensions are even (required by most codecs)
        new_width = new_width - (new_width % 2)
        new_height = new_height - (new_height % 2)
        
        # Ensure minimum dimensions
        if new_width < 320:
            new_width = 320
        if new_height < 320:
            new_height = 320
            
        return new_width, new_height
    
    def _convert_to_9_16_with_audio(self, input_path: Path, output_path: Path, target_width: int, 
                                   target_height: int, audio_track: Optional[Path] = None, 
                                   fade_duration: float = 1.0, video_duration: float = 0.0):
        """Convert video to 9:16 with optional audio mixing and fade effects."""
        try:
            # Build video filter
            video_filters = [f'scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height}']
            
            # Add fade effects if requested
            if fade_duration > 0 and video_duration > 0:
                # Ensure fade duration doesn't exceed half the video duration
                actual_fade_duration = min(fade_duration, video_duration / 2)
                video_filters.append(f'fade=t=in:st=0:d={actual_fade_duration},fade=t=out:st={video_duration - actual_fade_duration}:d={actual_fade_duration}')
            
            # Build audio filter
            audio_filters = []
            if audio_track:
                # Mix original audio with new track, with fade effects
                if fade_duration > 0 and video_duration > 0:
                    actual_fade_duration = min(fade_duration, video_duration / 2)
                    audio_filters.append(f'afade=t=in:st=0:d={actual_fade_duration},afade=t=out:st={video_duration - actual_fade_duration}:d={actual_fade_duration}')
            
            # Build FFmpeg command
            cmd = ['ffmpeg']
            
            # Input files
            cmd.extend(['-i', str(input_path)])
            if audio_track:
                cmd.extend(['-i', str(audio_track)])
            
            # Video filters
            cmd.extend(['-vf', ','.join(video_filters)])
            
            # Audio processing
            if audio_track:
                # Mix original audio with new track
                if audio_filters:
                    cmd.extend(['-filter_complex', f'[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2,{",".join(audio_filters)}[a]'])
                    cmd.extend(['-map', '0:v', '-map', '[a]'])
                else:
                    cmd.extend(['-filter_complex', '[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]'])
                    cmd.extend(['-map', '0:v', '-map', '[a]'])
            else:
                # Just apply audio fade to original audio
                if audio_filters:
                    cmd.extend(['-af', ','.join(audio_filters)])
            
            # Output settings
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',  # Overwrite output file
                str(output_path)
            ])
            
            print(f"🔧 Running FFmpeg: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ FFmpeg conversion completed")
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else "Unknown FFmpeg error"
            raise RuntimeError(f"FFmpeg conversion failed: {error_msg}")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg to process videos.")
    
    def _convert_to_9_16(self, input_path: Path, output_path: Path, target_width: int, target_height: int):
        """Convert video to 9:16 using FFmpeg (legacy method for backward compatibility)."""
        return self._convert_to_9_16_with_audio(input_path, output_path, target_width, target_height)
    
    def get_video_info(self, video_path: Path) -> dict:
        """Get detailed video information."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = None
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            return {
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'duration': float(video_stream.get('duration', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'codec': video_stream.get('codec_name', 'unknown'),
                'bitrate': int(video_stream.get('bit_rate', 0)),
                'file_size': os.path.getsize(video_path)
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get video info: {e}")
    
    def is_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available on the system."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_video_requirements(self, video_path: Path) -> dict:
        """Check if video meets YouTube Shorts requirements."""
        info = self.get_video_info(video_path)
        
        # YouTube Shorts requirements
        max_duration = 180  # 3 minutes
        aspect_ratio = info['width'] / info['height']
        target_ratio = 9 / 16
        
        requirements = {
            'duration_ok': info['duration'] <= max_duration,
            'aspect_ratio_ok': abs(aspect_ratio - target_ratio) < 0.1,
            'needs_processing': not (info['duration'] <= max_duration and abs(aspect_ratio - target_ratio) < 0.1),
            'current_ratio': aspect_ratio,
            'target_ratio': target_ratio,
            'duration': info['duration'],
            'max_duration': max_duration
        }
        
        return requirements
    
    def find_audio_track(self, video_path: Path, audio_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Find a matching audio track for a video file.
        
        Args:
            video_path: Path to the video file
            audio_dir: Directory to search for audio files (optional)
            
        Returns:
            Path to matching audio file, or None if not found
        """
        if audio_dir is None:
            # Look in common audio directories
            audio_dirs = [
                video_path.parent / "audio",
                video_path.parent.parent / "audio",
                Path.home() / "Music",
                Path(".") / "audio"
            ]
        else:
            audio_dirs = [audio_dir]
        
        video_stem = video_path.stem
        
        # Common audio file extensions
        audio_extensions = ['.mp3', '.wav', '.aac', '.m4a', '.ogg']
        
        for audio_dir in audio_dirs:
            if not audio_dir.exists():
                continue
                
            for ext in audio_extensions:
                # Try exact match
                audio_file = audio_dir / f"{video_stem}{ext}"
                if audio_file.exists():
                    return audio_file
                
                # Try common variations
                variations = [
                    f"{video_stem}_audio{ext}",
                    f"{video_stem}_music{ext}",
                    f"{video_stem}_track{ext}",
                    f"audio_{video_stem}{ext}",
                    f"music_{video_stem}{ext}"
                ]
                
                for variation in variations:
                    audio_file = audio_dir / variation
                    if audio_file.exists():
                        return audio_file
        
        return None
    
    def get_default_audio_track(self, audio_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Get a default audio track for videos that don't have a specific match.
        
        Args:
            audio_dir: Directory to search for default audio files
            
        Returns:
            Path to default audio file, or None if not found
        """
        if audio_dir is None:
            audio_dir = Path(".") / "audio"
        
        if not audio_dir.exists():
            return None
        
        # Look for default audio files
        default_names = [
            "default.mp3",
            "background.mp3", 
            "music.mp3",
            "track.mp3",
            "audio.mp3"
        ]
        
        for name in default_names:
            audio_file = audio_dir / name
            if audio_file.exists():
                return audio_file
        
        return None
