"""Event system for content watcher to broadcast processing events."""

import queue
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class WatcherEvent:
    """Represents a watcher event with all relevant data."""
    timestamp: str
    event_type: str  # file_detected, ai_generation, video_analysis, etc.
    filename: str
    file_size: Optional[int] = None
    duration: Optional[float] = None
    stage: Optional[str] = None
    platform: Optional[str] = None
    status: str = "processing"  # processing, success, error
    message: str = ""
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return asdict(self)


class WatcherEventEmitter:
    """Thread-safe event emitter for watcher events."""
    
    def __init__(self, max_history: int = 100):
        """Initialize event emitter with history limit."""
        self.event_queue = queue.Queue()
        self.history: List[WatcherEvent] = []
        self.max_history = max_history
        self.lock = threading.Lock()
        self.current_status = "idle"  # idle, watching, processing
        
    def emit(self, event_type: str, filename: str, **kwargs):
        """
        Emit a new event.
        
        Args:
            event_type: Type of event (file_detected, ai_generation, etc.)
            filename: Name of the file being processed
            **kwargs: Additional event data
        """
        event = WatcherEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            filename=filename,
            **kwargs
        )
        
        # Add to queue for SSE streaming
        self.event_queue.put(event)
        
        # Add to history with lock
        with self.lock:
            self.history.append(event)
            # Keep only last max_history events
            if len(self.history) > self.max_history:
                self.history.pop(0)
        
        logger.debug(f"Event emitted: {event_type} - {filename}")
    
    def get_next_event(self, timeout: float = 1.0) -> Optional[WatcherEvent]:
        """
        Get the next event from the queue.
        
        Args:
            timeout: How long to wait for an event
            
        Returns:
            Next event or None if timeout
        """
        try:
            event = self.event_queue.get(timeout=timeout)
            return event
        except queue.Empty:
            return None
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get all events from history."""
        with self.lock:
            return [event.to_dict() for event in self.history]
    
    def get_status(self) -> str:
        """Get current watcher status."""
        return self.current_status
    
    def set_status(self, status: str):
        """Set current watcher status."""
        self.current_status = status
        logger.info(f"Watcher status changed to: {status}")
    
    def clear_history(self):
        """Clear all history."""
        with self.lock:
            self.history.clear()
        logger.info("Event history cleared")


# Global event emitter instance
_event_emitter = WatcherEventEmitter()


def get_event_emitter() -> WatcherEventEmitter:
    """Get the global event emitter instance."""
    return _event_emitter


# Convenience functions for emitting common events
def emit_file_detected(filename: str, file_size: int):
    """Emit file detected event."""
    _event_emitter.emit(
        "file_detected",
        filename,
        file_size=file_size,
        status="processing",
        message=f"New file detected: {filename}"
    )


def emit_ai_generation(filename: str, title: str):
    """Emit AI generation complete event."""
    _event_emitter.emit(
        "ai_generation",
        filename,
        status="success",
        message="AI metadata generated",
        metadata={"title": title}
    )


def emit_video_analysis(filename: str, duration: float, aspect_ratio: float, needs_processing: bool):
    """Emit video analysis event."""
    _event_emitter.emit(
        "video_analysis",
        filename,
        duration=duration,
        status="success",
        message="Video analyzed",
        metadata={
            "aspect_ratio": aspect_ratio,
            "needs_processing": needs_processing
        }
    )


def emit_audio_match(filename: str, audio_track: Optional[str]):
    """Emit audio track match event."""
    message = f"Audio track: {audio_track}" if audio_track else "Using default audio"
    _event_emitter.emit(
        "audio_match",
        filename,
        status="success",
        message=message,
        metadata={"audio_track": audio_track}
    )


def emit_video_processing(filename: str, processing_type: str):
    """Emit video processing event."""
    _event_emitter.emit(
        "video_processing",
        filename,
        status="processing",
        message=f"Processing video: {processing_type}",
        metadata={"processing_type": processing_type}
    )


def emit_video_processing_complete(filename: str, output_file: str):
    """Emit video processing complete event."""
    _event_emitter.emit(
        "video_processing",
        filename,
        status="success",
        message="Video processing complete",
        metadata={"output_file": output_file}
    )


def emit_upload_start(filename: str, platform: str):
    """Emit upload start event."""
    _event_emitter.emit(
        "upload_start",
        filename,
        platform=platform,
        status="processing",
        message=f"Uploading to {platform}"
    )


def emit_upload_complete(filename: str, platform: str, video_url: Optional[str] = None, video_id: Optional[str] = None):
    """Emit upload complete event."""
    _event_emitter.emit(
        "upload_complete",
        filename,
        platform=platform,
        status="success",
        message=f"Uploaded to {platform}",
        metadata={"video_url": video_url, "video_id": video_id}
    )


def emit_error(filename: str, error_message: str, stage: Optional[str] = None):
    """Emit error event."""
    _event_emitter.emit(
        "error",
        filename,
        stage=stage,
        status="error",
        message=error_message
    )


def emit_video_scheduled(filename: str, scheduled_time, platforms: list):
    """Emit event when video is scheduled for posting."""
    _event_emitter.emit(
        "video_scheduled",
        filename,
        status="success",
        message=f"Scheduled for {scheduled_time.strftime('%I:%M %p')}",
        metadata={
            "scheduled_time": scheduled_time.isoformat(),
            "platforms": platforms
        }
    )

