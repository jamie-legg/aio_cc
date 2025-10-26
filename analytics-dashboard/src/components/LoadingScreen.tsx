import React from 'react';
import { SystemLoading } from './LoadingSpinner';

const LoadingScreen: React.FC = () => {
  return <SystemLoading fullScreen message="INITIALIZING ANALYTICS TERMINAL..." />;
};

export default LoadingScreen;
