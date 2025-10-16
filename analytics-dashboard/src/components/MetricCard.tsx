import React from 'react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  icon: React.ReactNode;
  value: string;
  label: string;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, value, label, color }) => {
  const colorClasses = {
    'terminal-green': 'text-terminal-green',
    'terminal-blue': 'text-terminal-blue',
    'terminal-red': 'text-terminal-red',
    'terminal-yellow': 'text-terminal-yellow',
  };

  return (
    <motion.div
      className="brutalist-box p-6 text-center group"
      whileHover={{ scale: 1.05 }}
      transition={{ duration: 0.2 }}
    >
      <motion.div
        className={`${colorClasses[color as keyof typeof colorClasses]} mb-4 flex justify-center`}
        whileHover={{ rotate: 360 }}
        transition={{ duration: 0.5 }}
      >
        {icon}
      </motion.div>
      
      <motion.div
        className="metric-value text-4xl font-extrabold mb-2"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5, type: "spring" }}
      >
        {value}
      </motion.div>
      
      <div className="metric-label text-sm text-gray-400 uppercase tracking-wider">
        {label}
      </div>
      
      {/* Animated border effect */}
      <motion.div
        className="absolute inset-0 border-2 border-terminal-green opacity-0 group-hover:opacity-100"
        initial={{ scale: 0.8 }}
        whileHover={{ scale: 1 }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  );
};

export default MetricCard;
