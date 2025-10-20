import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Eye,
  Heart,
  MessageCircle,
  Youtube,
  Instagram,
  Music
} from 'lucide-react';
import MetricCard from './MetricCard';
import PlatformStats from './PlatformStats';
import TopVideos from './TopVideos';
import { analyticsApi } from '../services/analyticsApi';

interface AnalyticsData {
  totalViews: number;
  totalVideos: number;
  totalLikes: number;
  totalComments: number;
  totalShares: number;
  platforms: {
    youtube: PlatformData;
    instagram: PlatformData;
    tiktok: PlatformData;
  };
  topVideos: VideoData[];
}

interface RealApiResponse {
  total_views_across_platforms: number;
  platform_breakdown: Record<string, number>;
  channel_stats: Array<{
    platform: string;
    total_videos: number;
    total_views: number;
    total_likes: number;
    total_shares: number;
    total_comments: number;
    avg_engagement_rate: number;
    most_popular_video: {
      platform: string;
      platform_video_id: string;
      title: string;
      platform_url: string;
      views: number;
      likes: number;
      comments: number;
      shares: number;
    } | null;
  }>;
}

interface PlatformData {
  videos: number;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  engagementRate: number;
  mostPopular: VideoData;
}

interface VideoData {
  id: string;
  title: string;
  platform: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  url: string;
  thumbnail?: string;
}

const AnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      await fetchAnalyticsData();
      await fetchTopVideos();
    };
    loadData();
    
    // Listen for refresh events from header
    const handleRefresh = () => {
      setLoading(true);
      loadData();
    };
    
    window.addEventListener('dashboard-refresh', handleRefresh);
    return () => window.removeEventListener('dashboard-refresh', handleRefresh);
  }, []);

  const fetchTopVideos = async () => {
    try {
      // Use the new efficient endpoint that gets top videos with metrics in a single query
      const response = await fetch('http://localhost:8000/videos/top-with-metrics?limit=10');
      const videosWithMetrics = await response.json();
      
      // Map to the expected format
      const topVideos = videosWithMetrics.map((video: any) => ({
        id: video.video_id,
        title: video.title,
        platform: video.platform,
        views: video.views || 0,
        likes: video.likes || 0,
        comments: video.comments || 0,
        shares: video.shares || 0,
        url: video.platform_url
      }));
      
      setData(prevData => {
        if (!prevData) return null;
        return {
          ...prevData,
          topVideos
        };
      });
    } catch (err) {
      console.error('Error fetching top videos:', err);
    }
  };

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      // Use real API data
      const analyticsData = await analyticsApi.getChannelStats() as RealApiResponse;
      
      // Helper function to get platform data
      const getPlatformData = (platform: string) => {
        return analyticsData.channel_stats.find((p: any) => p.platform === platform) || {
          total_videos: 0,
          total_views: 0,
          total_likes: 0,
          total_shares: 0,
          total_comments: 0,
          avg_engagement_rate: 0,
          most_popular_video: null
        };
      };

      // Map the API data structure to component data structure
      const mappedData: AnalyticsData = {
        totalViews: analyticsData.total_views_across_platforms,
        totalVideos: analyticsData.channel_stats.reduce((sum: number, platform) => sum + platform.total_videos, 0),
        totalLikes: analyticsData.channel_stats.reduce((sum: number, platform) => sum + platform.total_likes, 0),
        totalComments: analyticsData.channel_stats.reduce((sum: number, platform) => sum + platform.total_comments, 0),
        totalShares: analyticsData.channel_stats.reduce((sum: number, platform) => sum + platform.total_shares, 0),
        platforms: {
          youtube: {
            videos: getPlatformData('youtube').total_videos,
            views: getPlatformData('youtube').total_views,
            likes: getPlatformData('youtube').total_likes,
            comments: getPlatformData('youtube').total_comments,
            shares: getPlatformData('youtube').total_shares,
            engagementRate: getPlatformData('youtube').avg_engagement_rate,
            mostPopular: getPlatformData('youtube').most_popular_video ? {
              id: getPlatformData('youtube').most_popular_video!.platform_video_id,
              title: getPlatformData('youtube').most_popular_video!.title,
              platform: 'YouTube',
              views: getPlatformData('youtube').most_popular_video!.views,
              likes: getPlatformData('youtube').most_popular_video!.likes,
              comments: getPlatformData('youtube').most_popular_video!.comments,
              shares: getPlatformData('youtube').most_popular_video!.shares,
              url: getPlatformData('youtube').most_popular_video!.platform_url
            } : {
              id: '',
              title: 'No videos',
              platform: 'YouTube',
              views: 0,
              likes: 0,
              comments: 0,
              shares: 0,
              url: ''
            }
          },
          instagram: {
            videos: getPlatformData('instagram').total_videos,
            views: getPlatformData('instagram').total_views,
            likes: getPlatformData('instagram').total_likes,
            comments: getPlatformData('instagram').total_comments,
            shares: getPlatformData('instagram').total_shares,
            engagementRate: getPlatformData('instagram').avg_engagement_rate,
            mostPopular: getPlatformData('instagram').most_popular_video ? {
              id: getPlatformData('instagram').most_popular_video!.platform_video_id,
              title: getPlatformData('instagram').most_popular_video!.title,
              platform: 'Instagram',
              views: getPlatformData('instagram').most_popular_video!.views,
              likes: getPlatformData('instagram').most_popular_video!.likes,
              comments: getPlatformData('instagram').most_popular_video!.comments,
              shares: getPlatformData('instagram').most_popular_video!.shares,
              url: getPlatformData('instagram').most_popular_video!.platform_url
            } : {
              id: '',
              title: 'No videos',
              platform: 'Instagram',
              views: 0,
              likes: 0,
              comments: 0,
              shares: 0,
              url: ''
            }
          },
          tiktok: {
            videos: getPlatformData('tiktok').total_videos,
            views: getPlatformData('tiktok').total_views,
            likes: getPlatformData('tiktok').total_likes,
            comments: getPlatformData('tiktok').total_comments,
            shares: getPlatformData('tiktok').total_shares,
            engagementRate: getPlatformData('tiktok').avg_engagement_rate,
            mostPopular: getPlatformData('tiktok').most_popular_video ? {
              id: getPlatformData('tiktok').most_popular_video!.platform_video_id,
              title: getPlatformData('tiktok').most_popular_video!.title,
              platform: 'TikTok',
              views: getPlatformData('tiktok').most_popular_video!.views,
              likes: getPlatformData('tiktok').most_popular_video!.likes,
              comments: getPlatformData('tiktok').most_popular_video!.comments,
              shares: getPlatformData('tiktok').most_popular_video!.shares,
              url: getPlatformData('tiktok').most_popular_video!.platform_url
            } : {
              id: '',
              title: 'No videos',
              platform: 'TikTok',
              views: 0,
              likes: 0,
              comments: 0,
              shares: 0,
              url: ''
            }
          }
        },
        topVideos: [] // We'll fetch this separately
      };
      
      setData(mappedData);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="rounded-full h-12 w-12 border-b-2 border-terminal-red mx-auto mb-4"></div>
          <p className="text-terminal-red font-mono">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-terminal-red font-mono text-xl mb-4">{error}</p>
          <button 
            className="brutalist-button"
            onClick={fetchAnalyticsData}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="container mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">
          AIOCC Dashboard
        </h1>
        <p className="text-lg text-gray-400">
          Real-time performance metrics across all platforms
        </p>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <MetricCard
          icon={<Eye size={32} />}
          value={data.totalViews.toLocaleString()}
          label="Total Views"
          color="terminal-red"
        />
        <MetricCard
          icon={<BarChart3 size={32} />}
          value={data.totalVideos.toString()}
          label="Total Videos"
          color="terminal-blue"
        />
        <MetricCard
          icon={<Heart size={32} />}
          value={data.totalLikes.toLocaleString()}
          label="Total Likes"
          color="terminal-red"
        />
        <MetricCard
          icon={<MessageCircle size={32} />}
          value={data.totalComments.toLocaleString()}
          label="Total Comments"
          color="terminal-yellow"
        />
      </div>

      {/* Platform Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        <PlatformStats
          platform="YouTube"
          icon={<Youtube size={24} />}
          data={data.platforms.youtube}
          color="red-500"
        />
        <PlatformStats
          platform="Instagram"
          icon={<Instagram size={24} />}
          data={data.platforms.instagram}
          color="pink-500"
        />
        <PlatformStats
          platform="TikTok"
          icon={<Music size={24} />}
          data={data.platforms.tiktok}
          color="black"
        />
      </div>

      {/* Top Videos */}
      <div>
        <TopVideos videos={data.topVideos} />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
