import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, BarChart3, Heart, MessageCircle, Share2 } from 'lucide-react';

interface PlatformData {
  videos: number;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  engagementRate: number;
  mostPopular: {
    title: string;
    views: number;
    likes: number;
    url: string;
  };
}

interface PlatformStatsProps {
  platform: string;
  icon: React.ReactNode;
  data: PlatformData;
  color: string;
}

const PlatformStats: React.FC<PlatformStatsProps> = ({ platform, icon, data, color }) => {
  const colorClasses = {
    'red-500': 'text-red-500',
    'pink-500': 'text-pink-500',
    'black': 'text-black',
  };

  return (
    <motion.div
      className="brutalist-box p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`${colorClasses[color as keyof typeof colorClasses]}`}>
            {icon}
          </div>
          <h3 className="text-2xl font-bold uppercase tracking-wider">
            {platform}
          </h3>
        </div>
        <div className="text-right">
          <div className="text-3xl font-extrabold text-terminal-green">
            {data.views.toLocaleString()}
          </div>
          <div className="text-sm text-gray-400 uppercase tracking-wider">
            Views
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <BarChart3 size={16} className="text-terminal-blue" />
            <span className="text-sm text-gray-400 uppercase tracking-wider">Videos</span>
          </div>
          <div className="text-xl font-bold text-terminal-green">
            {data.videos}
          </div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <TrendingUp size={16} className="text-terminal-yellow" />
            <span className="text-sm text-gray-400 uppercase tracking-wider">Engagement</span>
          </div>
          <div className="text-xl font-bold text-terminal-green">
            {data.engagementRate.toFixed(1)}%
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Heart size={16} className="text-terminal-red" />
            <span className="text-sm text-gray-400">Likes</span>
          </div>
          <span className="font-mono text-terminal-green">
            {data.likes.toLocaleString()}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageCircle size={16} className="text-terminal-blue" />
            <span className="text-sm text-gray-400">Comments</span>
          </div>
          <span className="font-mono text-terminal-green">
            {data.comments.toLocaleString()}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Share2 size={16} className="text-terminal-yellow" />
            <span className="text-sm text-gray-400">Shares</span>
          </div>
          <span className="font-mono text-terminal-green">
            {data.shares.toLocaleString()}
          </span>
        </div>
      </div>

      {data.mostPopular && (
        <motion.div
          className="mt-6 p-4 bg-terminal-bg border border-terminal-green rounded"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="text-sm text-gray-400 uppercase tracking-wider mb-2">
            Most Popular
          </div>
          <div className="text-sm text-terminal-green font-mono mb-2 truncate">
            {data.mostPopular.title}
          </div>
          <div className="flex justify-between text-xs text-gray-400">
            <span>{data.mostPopular.views.toLocaleString()} views</span>
            <span>{data.mostPopular.likes.toLocaleString()} likes</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default PlatformStats;
