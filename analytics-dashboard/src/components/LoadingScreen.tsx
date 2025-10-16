import React from 'react';
import { motion } from 'framer-motion';
import { Terminal, Loader2 } from 'lucide-react';

const LoadingScreen: React.FC = () => {
  return (
    <div className="min-h-screen bg-terminal-bg flex items-center justify-center">
      <motion.div
        className="text-center"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          className="mb-8"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Terminal size={80} className="text-terminal-green mx-auto" />
        </motion.div>
        
        <motion.h1
          className="text-4xl font-extrabold text-terminal-green mb-4 uppercase tracking-wider"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          ANALYTICS TERMINAL
        </motion.h1>
        
        <motion.div
          className="flex items-center justify-center gap-2 mb-8"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <Loader2 size={24} className="text-terminal-green animate-spin" />
          <span className="text-terminal-green font-mono text-lg">
            INITIALIZING SYSTEM...
          </span>
        </motion.div>
        
        <motion.div
          className="w-64 h-2 bg-terminal-card border-2 border-terminal-green rounded-sm overflow-hidden mx-auto"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <motion.div
            className="h-full bg-gradient-to-r from-terminal-green via-terminal-blue to-terminal-red"
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ duration: 2, ease: "easeInOut" }}
          />
        </motion.div>
        
        <motion.div
          className="mt-8 text-sm text-gray-400 font-mono"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.5 }}
        >
          <div className="animate-pulse">
            <div>Loading analytics data...</div>
            <div>Connecting to platforms...</div>
            <div>Initializing 3D renderer...</div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default LoadingScreen;
