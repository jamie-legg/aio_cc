import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Terminal, Wifi, WifiOff, RefreshCw, Settings } from 'lucide-react';

const TerminalHeader: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isConnected, setIsConnected] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [refreshStatus, setRefreshStatus] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshStatus('Collecting fresh metrics...');
    
    try {
      // First trigger metrics collection
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/api/metrics/collect', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setRefreshStatus(`Updated ${result.collected} videos`);
        console.log(`Metrics collection: ${result.message}`);
      } else {
        setRefreshStatus('Using cached data');
        console.warn('Metrics collection failed, refreshing cached data');
      }
    } catch (error) {
      setRefreshStatus('Using cached data');
      console.warn('Metrics collection error:', error);
    }
    
    // Emit custom refresh event that components can listen to
    const event = new CustomEvent('dashboard-refresh');
    window.dispatchEvent(event);
    
    // Keep spinning for visual feedback
    setTimeout(() => {
      setIsRefreshing(false);
      setRefreshStatus('');
    }, 2000); // Longer delay to show metrics collection
  };

  const handleSettingsClick = () => {
    navigate('/dashboard/settings');
  };

  return (
    <header className="bg-gray-900 sticky top-0 z-50 border-b border-gray-700 px-6 py-4">
      <div className="flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="text-white">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 3h18v18H3V3zm2 2v14h14V5H5z" fill="currentColor"/>
              <path d="M7 9h10M7 12h10M7 15h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <span className="font-semibold text-lg text-white tracking-tight">
            AIOCC Dashboard
          </span>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Wifi size={16} className="text-green-500" />
            ) : (
              <WifiOff size={16} className="text-red-500" />
            )}
            <span className="text-xs text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          <div className="text-sm text-gray-400">
            {formatTime(currentTime)}
          </div>
          
          <div className="flex gap-2">
            <button 
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors duration-200 disabled:opacity-50"
              title={refreshStatus || "Refresh dashboard data"}
            >
              <RefreshCw 
                size={16} 
                className={`text-gray-400 ${isRefreshing ? 'animate-spin' : ''}`}
              />
            </button>
            
            <button 
              onClick={handleSettingsClick}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors duration-200"
              title="Open settings"
            >
              <Settings size={16} className="text-gray-400" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TerminalHeader;