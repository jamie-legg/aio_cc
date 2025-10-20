import React, { useState } from 'react';
import {
  FileVideo,
  Sparkles,
  Video,
  Music,
  Clapperboard,
  Upload,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { WatcherEvent } from '../services/watcherService';

interface ActivityLogItemProps {
  event: WatcherEvent;
}

const ActivityLogItem: React.FC<ActivityLogItemProps> = ({ event }) => {
  const [expanded, setExpanded] = useState(false);

  // Get icon based on event type
  const getIcon = () => {
    switch (event.event_type) {
      case 'file_detected':
        return <FileVideo size={16} />;
      case 'ai_generation':
        return <Sparkles size={16} />;
      case 'video_analysis':
        return <Video size={16} />;
      case 'audio_match':
        return <Music size={16} />;
      case 'video_processing':
        return <Clapperboard size={16} />;
      case 'upload_start':
      case 'upload_complete':
        return <Upload size={16} />;
      case 'error':
        return <XCircle size={16} />;
      default:
        return <CheckCircle size={16} />;
    }
  };

  // Get status color
  const getStatusColor = () => {
    switch (event.status) {
      case 'processing':
        return 'text-blue-400';
      case 'success':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  // Get status badge
  const getStatusBadge = () => {
    const colors = {
      processing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      success: 'bg-green-500/20 text-green-400 border-green-500/30',
      error: 'bg-red-500/20 text-red-400 border-red-500/30',
    };

    return (
      <span className={`px-2 py-0.5 text-xs rounded border ${colors[event.status]}`}>
        {event.status}
      </span>
    );
  };

  // Format file size
  const formatFileSize = (bytes?: number) => {
    if (!bytes) return null;
    const mb = bytes / (1024 * 1024);
    return mb >= 1 ? `${mb.toFixed(1)}MB` : `${(bytes / 1024).toFixed(0)}KB`;
  };

  // Format duration
  const formatDuration = (seconds?: number) => {
    if (!seconds) return null;
    return `${seconds.toFixed(1)}s`;
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    
    return date.toLocaleTimeString();
  };

  // Truncate filename
  const truncateFilename = (filename: string, maxLength: number = 30) => {
    if (filename.length <= maxLength) return filename;
    const ext = filename.split('.').pop();
    const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'));
    const truncated = nameWithoutExt.substring(0, maxLength - ext!.length - 4);
    return `${truncated}...${ext}`;
  };

  return (
    <div className="border-b border-gray-700 last:border-b-0">
      <div
        className="p-3 hover:bg-gray-800/50 cursor-pointer transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className={`mt-0.5 ${getStatusColor()}`}>
            {getIcon()}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Filename and Status */}
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="text-sm text-white font-medium truncate">
                {truncateFilename(event.filename)}
              </span>
              {getStatusBadge()}
            </div>

            {/* Message */}
            <div className="text-xs text-gray-400 mb-1">
              {event.message}
            </div>

            {/* Metrics Row */}
            <div className="flex items-center gap-3 text-xs text-gray-500">
              {event.file_size && (
                <span>{formatFileSize(event.file_size)}</span>
              )}
              {event.duration && (
                <span>{formatDuration(event.duration)}</span>
              )}
              {event.platform && (
                <span className="capitalize">{event.platform}</span>
              )}
              <span>{formatTimestamp(event.timestamp)}</span>
            </div>
          </div>

          {/* Expand Icon */}
          <div className="text-gray-500 mt-0.5">
            {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </div>
        </div>

        {/* Expanded Details */}
        {expanded && event.metadata && (
          <div className="mt-3 pl-7 pr-2">
            <div className="bg-gray-800/50 rounded p-2 text-xs">
              <div className="text-gray-400 font-mono">
                {Object.entries(event.metadata).map(([key, value]) => (
                  <div key={key} className="mb-1 last:mb-0">
                    <span className="text-gray-500">{key}:</span>{' '}
                    <span className="text-white">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ActivityLogItem;

