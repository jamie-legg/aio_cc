import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';

interface TrendData {
  date: string;
  total_views: number;
  total_likes: number;
  total_comments: number;
}

interface ViewsTrendChartProps {
  data: TrendData[];
  loading?: boolean;
}

const ViewsTrendChart: React.FC<ViewsTrendChartProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-800 rounded"></div>
        </div>
      </div>
    );
  }

  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    Views: item.total_views,
  }));

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp size={20} className="text-blue-400" />
        <h3 className="text-lg font-semibold text-white">Total Views Over Time</h3>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="date" 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1F2937', 
              border: '1px solid #374151',
              borderRadius: '0.5rem'
            }}
            labelStyle={{ color: '#F3F4F6' }}
            formatter={(value: number) => [value.toLocaleString(), 'Views']}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="Views" 
            stroke="#3B82F6" 
            strokeWidth={2}
            dot={{ fill: '#3B82F6', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ViewsTrendChart;




