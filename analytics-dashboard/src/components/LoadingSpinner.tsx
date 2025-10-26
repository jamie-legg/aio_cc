import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, Terminal, Database, Globe, Zap, BookOpen, Settings, Upload, BarChart3 } from 'lucide-react';

export type LoadingType = 
  | 'default'
  | 'analytics'
  | 'documentation'
  | 'settings'
  | 'uploads'
  | 'integrations'
  | 'ai-config'
  | 'auth'
  | 'system';

interface LoadingSpinnerProps {
  type?: LoadingType;
  message?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fullScreen?: boolean;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  type = 'default',
  message,
  size = 'md',
  fullScreen = false,
  className = ''
}) => {
  const getIcon = () => {
    switch (type) {
      case 'analytics':
        return <BarChart3 className="text-terminal-green" />;
      case 'documentation':
        return <BookOpen className="text-terminal-blue" />;
      case 'settings':
        return <Settings className="text-terminal-yellow" />;
      case 'uploads':
        return <Upload className="text-terminal-red" />;
      case 'integrations':
        return <Globe className="text-terminal-blue" />;
      case 'ai-config':
        return <Zap className="text-terminal-purple" />;
      case 'auth':
        return <Terminal className="text-terminal-green" />;
      case 'system':
        return <Database className="text-terminal-blue" />;
      default:
        return <Loader2 className="animate-spin text-terminal-green" />;
    }
  };

  const getDefaultMessage = () => {
    switch (type) {
      case 'analytics':
        return 'Loading analytics data...';
      case 'documentation':
        return 'Loading documentation...';
      case 'settings':
        return 'Loading settings...';
      case 'uploads':
        return 'Loading uploads...';
      case 'integrations':
        return 'Loading integrations...';
      case 'ai-config':
        return 'Loading AI configuration...';
      case 'auth':
        return 'Authenticating...';
      case 'system':
        return 'Initializing system...';
      default:
        return 'Loading...';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'w-4 h-4';
      case 'md':
        return 'w-8 h-8';
      case 'lg':
        return 'w-12 h-12';
      case 'xl':
        return 'w-16 h-16';
      default:
        return 'w-8 h-8';
    }
  };

  const getTextSize = () => {
    switch (size) {
      case 'sm':
        return 'text-sm';
      case 'md':
        return 'text-base';
      case 'lg':
        return 'text-lg';
      case 'xl':
        return 'text-xl';
      default:
        return 'text-base';
    }
  };

  const content = (
    <motion.div
      className={`flex flex-col items-center justify-center ${className}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className={`${getSizeClasses()} mb-4`}
        animate={type === 'default' ? { rotate: 360 } : {}}
        transition={type === 'default' ? { duration: 1, repeat: Infinity, ease: "linear" } : {}}
      >
        {getIcon()}
      </motion.div>
      
      <motion.p
        className={`${getTextSize()} text-gray-300 font-mono`}
        initial={{ y: 10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.3 }}
      >
        {message || getDefaultMessage()}
      </motion.p>

      {type === 'system' && (
        <motion.div
          className="w-48 h-1 bg-gray-700 rounded-full overflow-hidden mt-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <motion.div
            className="h-full bg-gradient-to-r from-terminal-green via-terminal-blue to-terminal-red"
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ duration: 2, ease: "easeInOut" }}
          />
        </motion.div>
      )}
    </motion.div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};

// Convenience components for common use cases
export const AnalyticsLoading: React.FC<{ message?: string; fullScreen?: boolean }> = (props) => (
  <LoadingSpinner type="analytics" {...props} />
);

export const DocumentationLoading: React.FC<{ message?: string; fullScreen?: boolean }> = (props) => (
  <LoadingSpinner type="documentation" {...props} />
);

export const SettingsLoading: React.FC<{ message?: string; fullScreen?: boolean }> = (props) => (
  <LoadingSpinner type="settings" {...props} />
);

export const UploadsLoading: React.FC<{ message?: string; fullScreen?: boolean }> = (props) => (
  <LoadingSpinner type="uploads" {...props} />
);

export const IntegrationsLoading: React.FC<{ message?: string; fullScreen?: boolean }> = (props) => (
  <LoadingSpinner type="integrations" {...props} />
);

export const AIConfigLoading: React.FC<{ message?: string; fullScreen?: boolean }> = (props) => (
  <LoadingSpinner type="ai-config" {...props} />
);

export const AuthLoading: React.FC<{ message?: string; fullScreen?: boolean }> = (props) => (
  <LoadingSpinner type="auth" {...props} />
);

export const SystemLoading: React.FC<{ message?: string; fullScreen?: boolean }> = (props) => (
  <LoadingSpinner type="system" {...props} />
);

export default LoadingSpinner;

