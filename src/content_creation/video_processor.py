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
            
            # Output settings optimized for Instagram Reels (per Facebook docs)
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'medium',  # Better quality than 'fast'
                '-crf', '20',  # Better quality than 23
                '-maxrate', '4M',  # Max bitrate 4Mbps for Instagram
                '-bufsize', '8M',  # Buffer size
                '-r', '30',  # Force 30fps for Instagram (within 24-60 range)
                '-c:a', 'aac',
                '-b:a', '128k',  # Audio bitrate 128kbs+ (per specs)
                '-ar', '48000',  # Sample rate 48kHz (per specs)
                '-ac', '2',  # Stereo channels (per specs)
                '-profile:a', 'aac_low',  # AAC Low Complexity (per specs)
                '-movflags', '+faststart',
                '-pix_fmt', 'yuv420p',  # Chroma subsampling 4:2:0 (per specs)
                '-g', '60',  # Closed GOP 2-5 seconds (30fps * 2s = 60 frames)
                '-keyint_min', '60',  # Minimum keyframe interval
                '-sc_threshold', '0',  # Disable scene change detection for fixed frame rate
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
        """Get detailed video information including audio details for Instagram compliance."""
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
            
            # Extract video and audio stream info
            video_stream = None
            audio_stream = None
            
            for stream in data['streams']:
                if stream['codec_type'] == 'video' and video_stream is None:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and audio_stream is None:
                    audio_stream = stream
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            # Calculate FPS safely
            fps = 30  # Default
            if 'r_frame_rate' in video_stream:
                fps_str = video_stream['r_frame_rate']
                if '/' in fps_str:
                    try:
                        num, den = fps_str.split('/')
                        fps = float(num) / float(den) if float(den) != 0 else 30
                    except (ValueError, ZeroDivisionError):
                        fps = 30
                else:
                    try:
                        fps = float(fps_str)
                    except ValueError:
                        fps = 30
            
            # Extract audio info if available
            audio_codec = 'unknown'
            audio_bitrate = 0
            sample_rate = 0
            channels = 0
            
            if audio_stream:
                audio_codec = audio_stream.get('codec_name', 'unknown')
                if 'bit_rate' in audio_stream:
                    audio_bitrate = int(audio_stream['bit_rate'])
                if 'sample_rate' in audio_stream:
                    sample_rate = int(audio_stream['sample_rate'])
                if 'channels' in audio_stream:
                    channels = int(audio_stream['channels'])
            
            return {
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'duration': float(video_stream.get('duration', 0)),
                'fps': fps,
                'codec': video_stream.get('codec_name', 'unknown'),
                'bitrate': int(video_stream.get('bit_rate', 0)),
                'file_size': os.path.getsize(video_path),
                'audio_codec': audio_codec,
                'audio_bitrate': audio_bitrate,
                'sample_rate': sample_rate,
                'channels': channels
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
    
    def check_instagram_requirements(self, video_path: Path) -> dict[str, any]:
        """Check if video meets Instagram Reels requirements (per Facebook docs)."""
        try:
            info = self.get_video_info(video_path)
            duration = info['duration']
            width = info['width']
            height = info['height']
            codec = info['codec']
            bitrate = info['bitrate']
            file_size = info['file_size']
            fps = info.get('fps', 30)
            audio_codec = info.get('audio_codec', 'unknown')
            audio_bitrate = info.get('audio_bitrate', 0)
            sample_rate = info.get('sample_rate', 0)
            channels = info.get('channels', 0)
            
            # Instagram Reels requirements (per Facebook docs)
            max_duration = 90  # 90 seconds max
            min_duration = 3   # 3 seconds min
            max_file_size = 100 * 1024 * 1024  # 100MB max (conservative)
            max_bitrate = 5 * 1024 * 1024  # 5Mbps max (conservative)
            
            # Resolution requirements (per Facebook docs)
            min_width = 540   # Minimum 540x960
            min_height = 960
            recommended_width = 1080  # Recommended 1080x1920
            recommended_height = 1920
            
            # Frame rate requirements (per Facebook docs)
            min_fps = 24
            max_fps = 60
            
            # Audio requirements (per Facebook docs)
            min_audio_bitrate = 128 * 1000  # 128kbs+
            required_sample_rate = 48000  # 48kHz
            required_channels = 2  # Stereo
            required_audio_codec = 'aac'  # AAC Low Complexity
            
            issues = []
            
            # Duration checks
            if duration < min_duration:
                issues.append(f"Too short ({duration:.1f}s < {min_duration}s)")
            elif duration > max_duration:
                issues.append(f"Too long ({duration:.1f}s > {max_duration}s)")
            
            # File size checks
            if file_size > max_file_size:
                issues.append(f"File too large ({file_size / (1024*1024):.1f}MB > {max_file_size / (1024*1024)}MB)")
            
            # Video bitrate checks
            if bitrate > max_bitrate:
                issues.append(f"Video bitrate too high ({bitrate / (1024*1024):.1f}Mbps > {max_bitrate / (1024*1024)}Mbps)")
            
            # Resolution checks
            if width < min_width or height < min_height:
                issues.append(f"Resolution too low ({width}x{height} < {min_width}x{min_height})")
            elif width > recommended_width or height > recommended_height:
                issues.append(f"Resolution higher than recommended ({width}x{height} > {recommended_width}x{recommended_height})")
            
            # Frame rate checks
            if fps < min_fps or fps > max_fps:
                issues.append(f"Frame rate out of range ({fps}fps not in {min_fps}-{max_fps}fps)")
            
            # Video codec checks
            if codec not in ['h264', 'h265']:
                issues.append(f"Unsupported video codec ({codec}, need h264/h265)")
            
            # Audio checks
            if audio_codec != required_audio_codec:
                issues.append(f"Wrong audio codec ({audio_codec} != {required_audio_codec})")
            
            if audio_bitrate > 0 and audio_bitrate < min_audio_bitrate:
                issues.append(f"Audio bitrate too low ({audio_bitrate/1000:.0f}kbps < {min_audio_bitrate/1000}kbps)")
            
            if sample_rate > 0 and sample_rate != required_sample_rate:
                issues.append(f"Wrong sample rate ({sample_rate}Hz != {required_sample_rate}Hz)")
            
            if channels > 0 and channels != required_channels:
                issues.append(f"Wrong audio channels ({channels} != {required_channels} stereo)")
            
            return {
                'duration': duration,
                'width': width,
                'height': height,
                'codec': codec,
                'bitrate': bitrate,
                'file_size': file_size,
                'fps': fps,
                'audio_codec': audio_codec,
                'audio_bitrate': audio_bitrate,
                'sample_rate': sample_rate,
                'channels': channels,
                'issues': issues,
                'compliant': len(issues) == 0
            }
            
        except Exception as e:
            print(f"Error checking Instagram requirements: {e}")
            return {'compliant': False, 'issues': [f"Error: {e}"]}
    
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
    
    def add_outro_image(self, input_path: Path, outro_image: Path, 
                       output_path: Optional[Path] = None, 
                       outro_duration: float = 1.0) -> Path:
        """
        Add an image outro to the end of a video.
        
        Args:
            input_path: Path to input video file
            outro_image: Path to outro image (PNG/JPG)
            output_path: Path for output file (optional)
            outro_duration: Duration of outro in seconds (default: 1.0)
            
        Returns:
            Path to processed video file with outro
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        if not outro_image.exists():
            raise FileNotFoundError(f"Outro image not found: {outro_image}")
        
        if not self._is_supported_format(input_path):
            raise ValueError(f"Unsupported video format: {input_path.suffix}")
        
        # Generate output path if not provided
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_with_outro{input_path.suffix}"
        
        print(f"🎬 Adding outro image to video: {input_path.name}")
        print(f"🖼️  Outro image: {outro_image.name}")
        print(f"⏱️  Outro duration: {outro_duration}s")
        
        try:
            # Get video info to match dimensions and properties
            video_info = self.get_video_info(input_path)
            width = video_info['width']
            height = video_info['height']
            fps = video_info['fps']
            
            print(f"📏 Video dimensions: {width}x{height} @ {fps}fps")
            
            # Create temporary video from image
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
                temp_video_path = Path(temp_video.name)
            
            try:
                # Step 1: Convert image to video segment matching the video properties
                print("📸 Converting image to video segment...")
                self._create_video_from_image(outro_image, temp_video_path, width, height, 
                                             fps, outro_duration)
                
                # Step 2: Concatenate original video with outro
                print("🔗 Concatenating video with outro...")
                self._concatenate_videos(input_path, temp_video_path, output_path)
                
                print(f"✅ Video with outro created successfully: {output_path.name}")
                return output_path
                
            finally:
                # Clean up temporary file
                if temp_video_path.exists():
                    temp_video_path.unlink()
            
        except Exception as e:
            print(f"❌ Failed to add outro: {e}")
            raise
    
    def _create_video_from_image(self, image_path: Path, output_path: Path, 
                                 width: int, height: int, fps: float, 
                                 duration: float):
        """Create a video from a static image."""
        try:
            cmd = [
                'ffmpeg',
                '-loop', '1',  # Loop the image
                '-i', str(image_path),
                '-t', str(duration),  # Duration
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '20',
                '-r', str(int(fps)),  # Match video fps
                '-pix_fmt', 'yuv420p',
                '-an',  # No audio for the outro segment
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else "Unknown FFmpeg error"
            raise RuntimeError(f"Failed to create video from image: {error_msg}")
    
    def _concatenate_videos(self, video1: Path, video2: Path, output_path: Path):
        """Concatenate two videos together."""
        try:
            # Create a temporary file list for FFmpeg concat
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"file '{video1.absolute()}'\n")
                f.write(f"file '{video2.absolute()}'\n")
                concat_file = Path(f.name)
            
            try:
                cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(concat_file),
                    '-c', 'copy',  # Copy codecs for fast concatenation
                    '-y',
                    str(output_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
            finally:
                # Clean up concat file
                if concat_file.exists():
                    concat_file.unlink()
                
        except subprocess.CalledProcessError as e:
            # If copy codec fails (codec mismatch), re-encode
            print("⚠️  Codec mismatch, re-encoding...")
            self._concatenate_videos_reencode(video1, video2, output_path)
    
    def _concatenate_videos_reencode(self, video1: Path, video2: Path, output_path: Path):
        """Concatenate two videos with re-encoding (slower but more compatible)."""
        try:
            cmd = [
                'ffmpeg',
                '-i', str(video1),
                '-i', str(video2),
                '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]',
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '20',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else "Unknown FFmpeg error"
            raise RuntimeError(f"Failed to concatenate videos: {error_msg}")