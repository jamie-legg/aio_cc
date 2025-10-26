import React from 'react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  icon: React.ReactNode;
  value: string;
  label: string;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, value, label }) => {

  return (
    <motion.div
      className="bg-gray-900 border border-gray-700 rounded-xl p-6 text-center hover:border-gray-500 transition-colors duration-300"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-gray-400 mb-4 flex justify-center">
        {icon}
      </div>
      
      <div className="text-4xl font-bold mb-2 text-white">
        {value}
      </div>
      
      <div className="text-sm text-gray-400 uppercase tracking-wider">
        {label}
      </div>
    </motion.div>
  );
};

export default MetricCard;
