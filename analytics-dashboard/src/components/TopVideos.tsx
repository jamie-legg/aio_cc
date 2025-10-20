import React from 'react';
import { ExternalLink, Eye, Heart, MessageCircle } from 'lucide-react';

interface VideoData {
  id: string;
  title: string;
  platform: string;
  views: number;
  likes: number;
  comments: number;
  url: string;
  thumbnail?: string;
}

interface TopVideosProps {
  videos: VideoData[];
}

const TopVideos: React.FC<TopVideosProps> = ({ videos }) => {
  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return '📺';
      case 'instagram':
        return '📷';
      case 'tiktok':
        return '🎵';
      default:
        return '📹';
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return 'text-red-500';
      case 'instagram':
        return 'text-pink-500';
      case 'tiktok':
        return 'text-black';
      default:
        return 'text-terminal-red';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-8">
      <div className="flex items-center gap-3 mb-8">
        <h2 className="text-2xl font-bold text-white">
          Top Performing Videos
        </h2>
        <div className="flex-1 h-px bg-gray-700"></div>
      </div>

      <div className="space-y-3">
        {videos.slice(0, 10).map((video, index) => (
          <div
            key={video.id}
            className="p-4 bg-gray-800 border border-gray-700 rounded-lg hover:border-gray-500 transition-colors duration-300"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className="text-xl font-bold text-gray-400 min-w-[3rem]">
                  #{index + 1}
                </div>
                
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <span className="text-2xl">
                    {getPlatformIcon(video.platform)}
                  </span>
                  
                  <div className="min-w-0 flex-1">
                    <div className={`font-semibold text-sm ${getPlatformColor(video.platform)}`}>
                      {video.platform}
                    </div>
                    <div className="text-white text-sm truncate">
                      {video.title}
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-1">
                  <Eye size={16} className="text-gray-400" />
                  <span className="text-white">
                    {video.views.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex items-center gap-1">
                  <Heart size={16} className="text-gray-400" />
                  <span className="text-white">
                    {video.likes.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex items-center gap-1">
                  <MessageCircle size={16} className="text-gray-400" />
                  <span className="text-white">
                    {video.comments.toLocaleString()}
                  </span>
                </div>

                <a
                  href={video.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs flex items-center gap-1 transition-colors duration-300"
                >
                  <ExternalLink size={12} />
                  View
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>

      {videos.length === 0 && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">📊</div>
          <div className="text-white text-lg">
            No videos found
          </div>
          <div className="text-gray-400 text-sm mt-2">
            Sync your channels to see analytics data
          </div>
        </div>
      )}
    </div>
  );
};

export default TopVideos;
